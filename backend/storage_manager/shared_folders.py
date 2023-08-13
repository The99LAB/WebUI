import os
from .storage_manager_exception import StorageManagerException
from .disk_manager import findUsedSpace
from .convertsize import convertSizeUnit
from .raid_manager import get as getRaidArrays
from .disk_manager import get as getDisks
import shutil
import subprocess

sharedfolderspath = "/mnt/sharedfolders"
smbsharesconfig = "/etc/samba/smb-shares.conf"

def get_selinux_context(path):
    try:
        output = subprocess.check_output(['stat', '-c', '%C', path])
        return output.decode("utf-8")
    except subprocess.CalledProcessError as e:
        return None
    
def remove_selinux_context(path):
    try:
        subprocess.check_output(['semanage', 'fcontext', '-d', f"{path}(/.*)?"])
    except subprocess.CalledProcessError as e:
        pass

    try:
        subprocess.check_output(['restorecon', '-R', '-v', path])
    except subprocess.CalledProcessError as e:
        pass

def get_smb_users():
    try:
        output = subprocess.check_output(['pdbedit', '-L'])
        output = output.decode("utf-8")
        lines = output.split("\n")
        users = []
        for line in lines:
            if line.strip() == "":
                continue
            users.append(line.split(":")[0])
        return users
    except subprocess.CalledProcessError as e:
        return []

def setSMBPermissions(path):
    # chmod 777 {path}
    # semanage fcontext -a -t samba_share_t "{path}(/.*)?"
    # restorecon -R -v {path}
    os.chmod(path, 0o777)

    # if distro uses selinux, set selinux context
    if not os.path.exists("/usr/sbin/semanage"):
        return

    selinux_context = get_selinux_context(path)
    if selinux_context is not None and 'samba_share_t' in selinux_context:
        return

    try:
        subprocess.check_output(["semanage", "fcontext", "-a", "-t", "samba_share_t", f"{path}(/.*)?"])
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to set samba permissions for {path}") from e
    try:
        subprocess.check_output(["restorecon", "-R", path])
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to set samba permissions for {path}") from e
    
def restartSMB():
    try:
        subprocess.check_output(["systemctl", "restart", "smb"])
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to restart samba")

# create smb share
def createSMBShare(name, path, mode="PRIVATE", users_list=[], users_write_list=[], users_read_list=[]):
    # PUBLIC: All users including guests have full read/write access.
    # SECURE: All users including guests have read access, you select which of your users have write access.
    # PRIVATE: No guest access at all, you select which of your users have read/write, read-only access or no access.
    public = "no"
    writeable = "no"
    write_list = " ".join(users_write_list)
    share_extra = ""
    if mode == "SECURE" or mode == "PUBLIC":
        public = "yes"
    if mode == "PUBLIC":
        writeable = "yes"
    if mode == "PRIVATE":
        valid_users = " ".join(users_list)
        read_list = " ".join(users_read_list)
        share_extra = f"""valid users = {valid_users}
        read list = {read_list}
        write list = {write_list}"""
    elif mode == "SECURE":
        share_extra = f"write list = {write_list}"

    share_base = f"""\n[{name}]
        path = {path}
        browseable = yes
        writeable = {writeable}
        public = {public}
        {share_extra}
        case sensitive = auto
        preserve case = yes
        short preserve case = yes
        comment = {mode}
        """

    with open(smbsharesconfig, "a") as f:
        f.write(share_base)

    if os.path.exists('/usr/sbin/semanage'):
        remove_selinux_context(path)
    setSMBPermissions(path)
    restartSMB()

def removeSMBShare(name):
    with open(smbsharesconfig, "r") as f:
        lines = f.readlines()

    # share starts with [name]
    # share ends with comment = {something} or comment = {something}\n
    # share is everything in between
    share_start = None
    share_end = None
    for i, line in enumerate(lines):
        if line.strip() == f"[{name}]":
            share_start = i
        if share_start is not None and line.strip().startswith("comment = "):
            share_end = i
            break
    if share_start is None or share_end is None:
        raise StorageManagerException(f"Failed to remove samba share {name}")
    
    del lines[share_start:share_end+1]

    with open(smbsharesconfig, "w") as f:
        f.writelines(lines)

def getSMBShares():
    keys = ['name', 'mode', 'path', 'valid users', 'read list', 'write list']
    with open(smbsharesconfig, "r") as f:
        lines = f.readlines()

    shares = []
    share = {}
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        if line.startswith("[") and line.endswith("]"):
            if share != {}:
                shares.append(share)
            share = {}
            share["name"] = line[1:-1]
        else:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key == "comment":
                key = "mode"
            if key in keys:
                share[key] = value
    

    if share != {}:
        shares.append(share)

    # create users list, and set their mode (rw, ro, none)
    users = get_smb_users()
    for share in shares:
        writelist = []
        readlist = []
        try:
            writelist = share["write list"].split(",")
        except KeyError:
            pass
        try:
            readlist = share["read list"].split(",")
        except KeyError:
            pass
        share["users"] = []
        for user in users:
            if share['mode'] == 'PRIVATE':
                if user in writelist:
                    share["users"].append({"name": user, "mode": "rw"})
                elif user in readlist:
                    share["users"].append({"name": user, "mode": "ro"})
                else:
                    share["users"].append({"name": user, "mode": "none"})
            elif share['mode'] == 'SECURE':
                if user in writelist:
                    share["users"].append({"name": user, "mode": "rw"})
                else:
                    share["users"].append({"name": user, "mode": "ro"})
            else:
                share["users"].append({"name": user, "mode": "rw"})
    return shares

def getSmbShare(name):
    shares = getSMBShares()
    for share in shares:
        if share["name"] == name:
            return share
    return None

def getAvailableDevices():
    # This are devices where a shared folder can be created on.
    # It can be a disk wiht type individual
    # Or a RAID array

    # get all disks and filter out the ones with type individual
    available_devices = []
    disks = getDisks()
    disks = [disk for disk in disks if disk["disktype"] == "individual"]
    for disk in disks:
        if len(disk['partitions']) == 1:
            available_devices.append({
                "name": disk["model"],
                "type": "disk",
                'mountpoint': disk['partitions'][0]['mount']
            })

    # get all RAID arrays
    raid_arrays = getRaidArrays()
    for raid_array in raid_arrays:
        available_devices.append({
            "name": raid_array["name"],
            "type": "raid",
            "mountpoint": raid_array["mountpoint"]
        })
    
    return available_devices

def get():
    if not os.path.exists(sharedfolderspath):
        os.makedirs(sharedfolderspath)
    
    folders = []

    for folder in os.listdir(sharedfolderspath):
        folder_active = True
        used = "0GB"
        capacity = "0GB"
        free = "0GB"
        smb_share = getSmbShare(folder)
        if smb_share is None:
            smb_share = {
                "name": None,
                "users": [ {'name': user} for user in get_smb_users()]
            }

        # every folder is a symlink to the actual folder.
        # get the path it points to
        folderpath = os.path.join(sharedfolderspath, folder)

        # symlink_target is the mountpoint of the disk
        symlink_target = os.path.dirname(os.readlink(folderpath))

        # Find which device from 'getAvailableDevices' has the symlink_target as mountpoint
        linked_storage_name = None
        linked_storage_type = None

        for device in getAvailableDevices():
            if device["mountpoint"] == symlink_target:
                linked_storage_name = device["name"]
                if device["type"] == "disk":
                    linked_storage_name = os.path.basename(device["mountpoint"])
                linked_storage_type = device["type"]
                break

        # check if the symlink_target still exists
        if not os.path.exists(symlink_target):
            folder_active = False
        else:
            # get the used space of the disk
            usedspace = findUsedSpace(folderpath)
            used = convertSizeUnit(usedspace[0], from_unit="MB", mode="str_space", round_state=True, round_to=None)
            capacity = convertSizeUnit(usedspace[1], from_unit="MB", mode="str_space", round_state=True, round_to=None)
            free = convertSizeUnit(usedspace[2], from_unit="MB", mode="str_space", round_state=True, round_to=None)

        folders.append({
            "name": folder,
            "active": folder_active,
            "path": folderpath,
            "actualpath": symlink_target,
            "used": used,
            "capacity": capacity,
            "free": free,
            "smb_share": smb_share,
            "linked_storage": {
                "name": linked_storage_name,
                "type": linked_storage_type
            }
        })
    return folders

def create(name, target):
    folderpath = os.path.join(sharedfolderspath, name)
    symlink_target = os.path.join(target, name)

    # check if the folder already exists
    if os.path.exists(folderpath):
        raise StorageManagerException(f"Shared folder {name} already exists")
    
    # create the folder
    os.makedirs(symlink_target)
    
    # create the symlink
    os.symlink(symlink_target, folderpath)

    # set samba permissions
    setSMBPermissions(symlink_target)
    return folderpath

def remove(name):
    _path = os.path.join(sharedfolderspath, name)
    symlink_target = os.readlink(_path)

    # check if the folder exists
    if not os.path.exists(_path):
        raise StorageManagerException(f"Shared folder {name} does not exist")
    
    if os.path.exists('usr/sbin/semanage'):
        # remove the selinux context
        remove_selinux_context(_path)
    
    # remove the folder where the symlink points to and all its contents
    shutil.rmtree(symlink_target)

    # remove the symlink
    os.remove(_path)

    # relive the smb share
    if getSmbShare(name) != None:
        removeSMBShare(name)
