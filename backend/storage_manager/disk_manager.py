import subprocess
from blkinfo import BlkDiskInfo
from .storage_manager_exception import StorageManagerException
from .convertsize import convertSizeUnit

def get():
    disk_list = []
    blk_info = BlkDiskInfo().get_disks()
    for disk in blk_info:
        # skip all devices that are not disks and zram devices
        if disk['type'] == 'disk' and not disk['name'].startswith('zram'):
            size = convertSizeUnit(size=int(disk['size']), from_unit="B", mode="str", round_state=True, round_to=None)
            disk_list.append({
                'name': disk['name'],
                'model': disk['model'],
                'size': size,
                'path': f'/dev/{disk["name"]}',
                'serial': disk['serial'],
            })
    return disk_list

def wipe(disk):
    try:
        subprocess.check_output(['wipefs', '-a', disk])
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to wipe disk {disk}") from e