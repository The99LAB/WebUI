import subprocess
from blkinfo import BlkDiskInfo # fork of genalt/blkinfo see https://github.com/macOS-KVM/blkinfo/releases/tag/0.2.0
from .storage_manager_exception import StorageManagerException
from .convertsize import convertSizeUnit
import time
import os
from pyfstab import Fstab, Entry


def deletePartition(disk, partition):
    try:
        subprocess.check_output(['parted', disk, 'rm', str(partition)])
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to delete partition {partition} on disk {disk}") from e


def formatPartition(path, fstype):
    try:
        if fstype == 'xfs':
            subprocess.check_output(['mkfs.xfs', '-f', path])
        else:
            subprocess.check_output(['mkfs', '-t', fstype, path])
        # wait for the partition to be formatted
        while find_uuid(path) == None:
            time.sleep(0.1)
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to format partition {path} with fstype {fstype}") from e


def findUsedSpace(path):
    try:
        used_space = subprocess.check_output(['df', '-BM', path])
        output = used_space.decode('utf-8')
        used_space = output.split('\n')[1].split()[2]
        capacity = output.split('\n')[1].split()[1]
        free = output.split('\n')[1].split()[3]
        return [int(used_space[:-1]), int(capacity[:-1]), int(free[:-1])]
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to find used space for partition {path}") from e


def find_uuid(path):
    try:
        uuid_process = subprocess.check_output(['blkid', '-s', 'UUID', '-o', 'value', path])
        uuid = uuid_process.decode('utf-8').strip()
        return uuid if uuid != "" else None
    except subprocess.CalledProcessError as e:
        return None


def find_statupmount(uuid):
    try:
        with open("/etc/fstab", "r") as f:
            fstab = Fstab().read_file(f)
        # find the fstab entry with the same uuid
        for entry in fstab.entries:
            if entry.device_tag_type == "UUID" and entry.device_tag_value == uuid:
                return entry.dir
        return None
    except Exception as e:
        raise StorageManagerException(f"Failed to get startup mount for device {uuid}") from e


def remove_startupmount(uuid=None, path=None):
    if uuid == None and path == None:
        raise StorageManagerException("Either uuid or path must be specified")
    try:
        found = False
        with open("/etc/fstab", "r") as f:
            fstab = Fstab().read_file(f)
        for entry in fstab.entries:
            if uuid != None:
                if entry.device_tag_type == "UUID" and entry.device_tag_value == uuid:
                    fstab.entries.remove(entry)
                    found = True
            
            elif path != None:
                if entry.device_tag_value == path:
                    fstab.entries.remove(entry)
                    found = True
        if found:
            with open("/etc/fstab", "w") as f:
                fstab.write_file(f)
    except Exception as e:
        raise StorageManagerException(f"Failed to remove startup mount for device {uuid}") from e
    

def add_startupmount(uuid=None, path=None, mountpoint=None, fstype='ext4'):
    if uuid == None and path == None:
        raise StorageManagerException("Either uuid or path must be specified")
    if mountpoint == None:
        raise StorageManagerException("Mountpoint must be specified")
    if uuid == None:
        fstab_entry = Entry(
            path,
            mountpoint,
            fstype,
            "defaults",
            0,
            0
        )
    else:
        fstab_entry = Entry(
            "UUID=" + uuid,
            mountpoint,
            fstype,
            "defaults",
            0,
            0
        )

    try:
        with open("/etc/fstab", "r") as f:
            fstab = Fstab().read_file(f)
        fstab.entries.append(fstab_entry)
        with open("/etc/fstab", "w") as f:
            fstab.write_file(f)
    except Exception as e:
        raise StorageManagerException(f"Failed to add startup mount for device {uuid}") from e


def lookupPartition(uuid):
    # get the partition from get()
    partition = None
    for disk in get():
        for partition in disk['partitions']:
            if partition['uuid'] == uuid:
                return partition
    if partition == None:
        raise StorageManagerException(f"Failed to lookup partition with uuid {uuid}")


def mountPartition(uuid, mountpoint):
    # lookup the partition
    partition = lookupPartition(uuid)

    # create the mountpoint if it doesn't exist
    if not os.path.exists(mountpoint):
        os.makedirs(mountpoint)

    # add the mountpoint to /etc/fstab
    if find_statupmount(uuid) == None:
        add_startupmount(uuid=uuid, mountpoint=mountpoint, fstype=partition['fstype'])
    else:
        remove_startupmount(uuid=uuid)
        add_startupmount(uuid=uuid, mountpoint=mountpoint, fstype=partition['fstype'])
    
    # reload systemd and mount the partition
    try:
        subprocess.check_output(['systemctl', 'daemon-reload'])
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to reload systemd") from e
    try:
        subprocess.check_output(['mount', '-a'])
        # wait for the partition to be mounted
        while not os.path.ismount(mountpoint):
            time.sleep(0.1)
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to mount partition {uuid} at {mountpoint}") from e


def unmountPartition(uuid):
    remove_startupmount(uuid=uuid)
    try:
        subprocess.check_output(['umount', f'/dev/disk/by-uuid/{uuid}'])
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to unmount partition {uuid}") from e


def checkPartitioningScheme(diskpath):
    # run parted /dev/sdc print
    # if the output contains "Partition Table: unknown", then return False
    # else return True
    try:
        output = subprocess.check_output(['parted', diskpath, 'print'])
        output = output.decode('utf-8')
        # the 4th line of the output contains the partition table type
        if output.split('\n')[3].split(':')[1].strip() == 'unknown':
            return False
        else:
            return True
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to check partitioning scheme on disk {diskpath}") from e


def createPartition(diskpath, fstype):
    # check if the disk has a partition table
    if not checkPartitioningScheme(diskpath):
        # create a partition table
        try:
            subprocess.check_output(['parted', diskpath, 'mklabel', 'gpt'])
            # wait for the partition table to be created
            while not checkPartitioningScheme(diskpath):
                time.sleep(0.1)
        except subprocess.CalledProcessError as e:
            raise StorageManagerException(f"Failed to create partition table on disk {diskpath}") from e

    # create a partition using parted
    try:
        subprocess.check_output(['parted', diskpath, 'mkpart', 'primary', '0%', '100%'])
        # wait for the partition to be created
        while not os.path.exists(diskpath + '1'):
            time.sleep(0.1)
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to create partition on disk {diskpath}") from e

    # format the partition using formatPartition()
    formatPartition(diskpath + '1', fstype)


def wipeDisk(path):
    try:
        subprocess.check_output(['wipefs', '-a', path])
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to wipe disk {path}") from e


def get():
    disk_list = []
    blk_info = BlkDiskInfo().get_disks(ignore_raid_parents=False)
    for disk in blk_info:
        # skip all devices that are not disks and zram devices
        if disk['type'] == 'disk' and not disk['name'].startswith('zram'):
            size = disk['size']
            diskpath = f"/dev/{disk['name']}"
            disk_has_partitiontable = True
            disk_type = 'individual' # disk type can be raid_member, individual, or system

            if disk['fstype'] == 'linux_raid_member':
                disk_type = 'raid_member'

            partitions = []
            for index, partition in enumerate(disk['children']):
                partition_fstype = partition['fstype']
                partition_name = partition['name']
                partition_mount = partition['mountpoint']
                partition_size = partition['size']
                partition_path = f"/dev/{partition_name}"
                partition_uuid = find_uuid(partition_path)
                partition_used = findUsedSpace(partition_path)[0]
                if partition_fstype == 'linux_raid_member':
                    disk_type = 'raid_member'
                    continue
                elif partition_fstype == '':
                    partition_fstype = 'unformatted'
                
                if partition_mount.startswith('/boot'):
                    disk_type = 'system'

                partitions.append({
                    "number": index+1,
                    "fstype": partition_fstype,
                    "uuid": partition_uuid,
                    "name": partition_name,
                    "mount": partition_mount,
                    "path": partition_path,
                    "parent": diskpath,
                    "used": None if partition_used == 0 else convertSizeUnit(size=partition_used, from_unit="MB", mode="str", round_state=True, round_to=None),
                    "size": convertSizeUnit(size=int(partition_size), from_unit="B", mode="str", round_state=True, round_to=None),
                    })

            disk_list.append({
                'name': disk['name'],
                'model': disk['model'],
                'disktype': disk_type,
                'size': convertSizeUnit(size=int(size), from_unit="B", mode="str", round_state=True, round_to=None),
                'path': diskpath,
                'serial': disk['serial'],
                'partitions': partitions,
                'has_partitiontable':  disk_has_partitiontable,
            })
    return disk_list
