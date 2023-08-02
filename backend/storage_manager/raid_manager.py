import mdstat
import subprocess
from .storage_manager_exception import StorageManagerException
from .convertsize import convertSizeUnit
# Example data:
# {
#     'personalities': ['raid0'], 
#     'unused_devices': [], 
#     'devices': 
#     {
#         'md0': 
#         {
#             'active': True, 
#             'read_only': False, 
#             'personality': 'raid0', 
#             'disks': 
#             {
#                 'sda1': 
#                 {
#                     'number': 0, 
#                     'write_mostly': False, 
#                     'faulty': False, 
#                     'spare': False, 
#                     'replacement': False
#                 }, 
#                 'sdb1': 
#                 {
#                     'number': 1, 
#                     'write_mostly': False, 
#                     'faulty': False, 
#                     'spare': False, 
#                     'replacement': False
#                 }
#             }, 
#             'status': 
#             {
#                 'blocks': 976506880, 
#                 'super': '1.2', 
#                 'chunks': '512k'
#             }, 
#             'bitmap': None, 
#             'resync': None
#         }
#     }
# }

def get():
    output = mdstat.parse()
    raid_arrays = []

    for device in output['devices']:
        _devicepath = f"/dev/{device}"
        _active = output['devices'][device]['active']
        _personality = output['devices'][device]['personality']
        _disks = [disk[:3] + disk[4:] for disk in output['devices'][device]['disks'].keys()]
        _size = convertSizeUnit(size=output['devices'][device]['status']['blocks'], from_unit="KB", mode="str", round_state=True, round_to=None)

        try:
            uuid_process = subprocess.check_output(['blkid', '-s', 'UUID', '-o', 'value', _devicepath])
            _uuid = uuid_process.decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            raise StorageManagerException(f"Failed to get UUID for device {_devicepath}") from e

        raid_arrays.append({
            'name': device,
            "path": _devicepath,
            'uuid': _uuid,
            'active': _active,
            'personality': _personality,
            'disks': _disks,
            'size': _size
        })

    return raid_arrays


def create(personality, disks):
    name = f"md{len(get())}"
    disks = [f"/dev/{disk}" for disk in disks]
    try:
        subprocess.check_output(['mdadm', '--create', f"/dev/{name}", '--level', personality, '--raid-devices', str(len(disks))] + disks)
    except subprocess.CalledProcessError as e:
        raise StorageManagerException(f"Failed to create RAID array {name}") from e
