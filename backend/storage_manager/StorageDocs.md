# Disks:
- List all disks using BlkDiskInfo
- Wipe: using fdisk: delete all partitions and write changes

# RAID:
- Use mdadm to create a RAID array from the disks /dev/mdx
- RAID array creation:
    - Clean the disks using fdisk
    - Create a filesystem on the disks using mkfs
    - Create the RAID array using mdadm
    - Create a filesystem on the RAID array using mkfs
    - Mount the RAID array using fstab

# Filesystem:
- Use mkfs to create a filesystem on the RAID array
- Use fstab to mount the filesystem on boot 
- RAID:
    - The whole array is mounted as a single filesystem
- Individual disk:
    - The individual disks are mounted as separate filesystems