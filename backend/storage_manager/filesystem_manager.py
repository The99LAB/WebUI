import subprocess
from blkinfo import BlkDiskInfo
from .storage_manager_exception import StorageManagerException
from .convertsize import convertSizeUnit

def get():
    filesystems = []
    blk_info = BlkDiskInfo().get_disks()
    for disk in blk_info:
        if disk['type'] == 'disk' and not disk['name'].startswith('zram'):
            partitions = disk['children']
            for partition in partitions:
                fstype = partition['fstype']
                print(f"Disk: {disk['name']}, Partition: {partition['name']}, Fstype: {fstype}")
                if fstype == "linux_raid_member":
                    raid_array = partition['children'][0]
                    print("Found a raid array!", raid_array['name'])
                    # if the filesytems list already has an element with the same type and name, skip it
                    if not any(fs['type'] == raid_array['type'] and fs['name'] == raid_array['name'] for fs in filesystems):
                        size = convertSizeUnit(size=int(raid_array['size']), from_unit="B", mode="str", round_state=True, round_to=None)
                        filesystems.append({
                            "type": raid_array['type'],
                            "name": raid_array['name'],
                            "path": f"/dev/{raid_array['name']}",
                            "parents": raid_array['parents'],
                            "size": size,
                            "fstype": raid_array['fstype'],
                            "mountpoint": raid_array['mountpoint']
                        })
                else:
                    filesystems.append({
                        "type": "part",
                        "name": partition['name'],
                        "path": f"/dev/{partition['name']}",
                        "parents": partition['parents'],
                        "size": convertSizeUnit(int(partition['size']), "B", mode="str", round_state=True, round_to=None),
                        "fstype": fstype,
                        "mountpoint": partition['mountpoint']
                    })

    return filesystems