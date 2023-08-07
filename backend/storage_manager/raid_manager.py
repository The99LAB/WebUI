import mdstat
import subprocess
from .storage_manager_exception import StorageManagerException
from .convertsize import convertSizeUnit
from .disk_manager import wipeDisk, add_startupmount, remove_startupmount
from blkinfo import BlkDiskInfo
import os
import time

def get():
    output = mdstat.parse()
    raid_arrays = []
    blk_info = BlkDiskInfo().get_disks()
    for device in output['devices']:
        _blk_info = None
        for disk in blk_info:
            if disk['name'] == device:
                _blk_info = disk
                break
        if _blk_info == None:
            raise StorageManagerException(f"Failed to get information for RAID array {device}")
        _devicepath = f"/dev/{device}"
        _active = output['devices'][device]['active']
        _personality = output['devices'][device]['personality']
        _disks = [disk for disk in output['devices'][device]['disks'].keys()]
        _size = convertSizeUnit(size=output['devices'][device]['status']['blocks'], from_unit="KB", mode="str_space", round_state=True, round_to=1)
        _operation = None
        _operation_progress = None
        _operation_finish = None
        _mountpoint = None
        if _blk_info['mountpoint'] != '':
            _mountpoint = _blk_info['mountpoint']
        if output['devices'][device]['resync'] != None:
            _operation = output['devices'][device]['resync']['operation']
            _operation_progress = output['devices'][device]['resync']['progress']
            _operation_finish = output['devices'][device]['resync']['finish']
        try:
            uuid_process = subprocess.check_output(['blkid', '-s', 'UUID', '-o', 'value', _devicepath])
            _uuid = uuid_process.decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            _uuid = None

        raid_arrays.append({
            'name': device,
            "path": _devicepath,
            'uuid': _uuid,
            'active': _active,
            'personality': _personality,
            'disks': _disks,
            'size': _size,
            'mountpoint': _mountpoint,
            'operation': _operation,
            'operation_progress': _operation_progress,
            'operation_finish': _operation_finish
        })

    return raid_arrays


def formatArray(path, fstype):
    # format the array
    try:
        if fstype == 'xfs':
            subprocess.check_output(['mkfs.xfs', '-f', path])
        else:
            subprocess.check_output(['mkfs', '-t', fstype, path])
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to format RAID array {path}") from e


def delete(path):
    # find UUID
    # remove the mountpoint from /etc/fstab
    remove_startupmount(path=path)
    # unmount the array
    try:
        subprocess.check_output(['umount', path])
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to unmount RAID array {path}") from e
    
    # get the disks which are part of the array
    disks = []
    for array in get():
        if array['path'] == path:
            disks = array['disks']
            break

    # stop the array
    try:
        subprocess.check_output(['mdadm', '--stop', path])
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to stop RAID array {path}") from e
    
    # wipe the disks
    for disk in disks:
        wipeDisk(f"/dev/{disk}")


def create(personality, devices, filesystem):
    for disk in devices:
        wipeDisk(disk)
    name = f"md{len(get())}"
    path = f"/dev/{name}"
    metadata = "1.2"
    if personality == "1":
        metadata = "0.90"
    cmd = ['mdadm', '--create', '/dev/md0', f'--level={personality}', f'--raid-devices={len(devices)}'] + [disk for disk in devices] + [f'--metadata={metadata}']
    
    
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Read the output from the subprocess
    output, error = process.communicate()

    # Check if the output contains a question
    if 'Continue creating array? ' in error:
        # Send 'yes' to confirm
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        process.communicate(input='yes\n')

    # Wait for the process to complete
    process.wait()

    if process.returncode != 0:
        raise StorageManagerException(f"Failed to create RAID array: {error}")

    # Format array
    formatArray(path=path, fstype=filesystem)

    # Find UUID
    mountpoint = f"/mnt/{name}"

    # create the mountpoint if it doesn't exist
    if not os.path.exists(mountpoint):
        os.makedirs(mountpoint)
    # add the mountpoint to /etc/fstab
    add_startupmount(path=path, mountpoint=mountpoint, fstype=filesystem)
    # reload systemd and mount array
    try:
        subprocess.check_output(['systemctl', 'daemon-reload'])
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to reload systemd") from e
    try:
        subprocess.check_output(['mount', '-a'])
        # wait for the array to be mounted
        while not os.path.ismount(mountpoint):
            time.sleep(0.1)
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to mount {path} at {mountpoint}") from e
