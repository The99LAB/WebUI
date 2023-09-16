

### Create snapshot
- virsh snapshot-create-as --domain UbuntuDesktop --name snapshot1 --diskspec sdb,file=/mnt/sharedfolders/snapshots/snapshot.qcow2 --disk-only
- Specify the disk to be snapshotted with --diskspec and the snapshot file with file=.

### List snapshots
- virsh snapshot-list --domain UbuntuDesktop

### Revert to snapshot
List the backing chain of the snapshot file:
- qemu-img info snapshot.qcow2 -U --backing-chain
- qemu-img info snapshot.qcow2 -U --backing-chain | grep -Po 'backing file:\s\K(.*)'

Revert to snapshot:
- Shutdown the VM
- Remove the snapshot: 'virsh snapshot-delete --metadata UbuntuDesktop snapshot1'
- Remove the snapshot file: 'rm /mnt/sharedfolders/snapshots/snapshot.qcow2
- Edit the domain XML:
    - change the source file of the disk to the 'backing file' of the snapshot file.
    - Remove the 'backing store' element.
- Start the VM
