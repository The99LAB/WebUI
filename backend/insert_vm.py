from db import get_session
from vm_manager.vmbasic import OvmfPath, VirtualMachineBasicTemplate, VirtualMachineBasicDiskBusTypes, VirtualMachineBasicDiskDeviceTypes, VirtualMachineBasicVDiskTypes, VirtualMachineBasicNetworkTypes, VirtualMachineBasicVideoTypes, VirtualMachineBasic, VirtualMachineDeviceDiskBlock, VirtualMachineDeviceNetwork, VirtualMachineDeviceDiskFile, VirtualMachineDevicePci, VirtualMachineBasicBiosTypes, VirtualMachineXmlTemplate
from sqlmodel import select

if __name__ == "__main__":
    xml_template = None
    xml_template_2 = None
    with get_session() as session:
        xml_template = session.exec(select(VirtualMachineXmlTemplate).where(VirtualMachineXmlTemplate.name == "Basic VM")).first()
        xml_template_2 = session.exec(select(VirtualMachineXmlTemplate).where(VirtualMachineXmlTemplate.name == "Basic VM USB2")).first()

    ovmf_path = None
    with get_session() as session:
        ovmf_path = session.exec(select(OvmfPath).where(OvmfPath.name == "OVMF")).first()

    disk_device_file = VirtualMachineDeviceDiskFile(
        name="Windows 10 Disk",
        disk_bus=VirtualMachineBasicDiskBusTypes.VIRTIO,
        device_type=VirtualMachineBasicDiskDeviceTypes.DISK,
        disk_source_file="/mnt/sharedfolders/test2/win10.qcow2"
    )

    # qemu-img create -f qcow2 /var/lib/libvirt/images/windows10.qcow2 40G

    disk_device_file_cdrom = VirtualMachineDeviceDiskFile(
        name="Windows 10 CDROM",
        disk_bus=VirtualMachineBasicDiskBusTypes.SATA,
        device_type=VirtualMachineBasicDiskDeviceTypes.CDROM,
        disk_source_file="/mnt/sharedfolders/test/Win10-21H2-EN.iso"
    )

    disk_device_file_cdrom2 = VirtualMachineDeviceDiskFile(
        name="Virtio Drivers",
        disk_bus=VirtualMachineBasicDiskBusTypes.SATA,
        device_type=VirtualMachineBasicDiskDeviceTypes.CDROM,
        disk_source_file="/mnt/sharedfolders/test/virtio-win.iso"
    )

    network_device = VirtualMachineDeviceNetwork(
        libvirt_name="default",
        type=VirtualMachineBasicNetworkTypes.E1000
    )
        

    vm = VirtualMachineBasic(
        name="Windows 10",
        autostart=False,
        cpu_model="host-passthrough",
        vcpu=2,
        vcpu_current=2,
        vcpu_custom_topology=False,
        vcpu_custom_topology_sockets=None,
        vcpu_custom_topology_dies=None,
        vcpu_custom_topology_cores=None,
        vcpu_custom_topology_threads=None,
        machine_type="pc-q35-7.2",
        bios_type=VirtualMachineBasicBiosTypes.OVMF,
        ovmf_path=ovmf_path,
        memory_min=2*1024*1024*1024,
        memory_max=4*1024*1024*1024,
        video_type=VirtualMachineBasicVideoTypes.QXL,
        devices_disk_file=[disk_device_file, disk_device_file_cdrom, disk_device_file_cdrom2],
        devices_network=[network_device],
        xml_template=xml_template
    )

    vm2 = VirtualMachineBasic(
        name="Windows 7",
        autostart=False,
        cpu_model="host-passthrough",
        vcpu=2,
        vcpu_current=2,
        vcpu_custom_topology=False,
        machine_type="pc-q35-7.2",
        bios_type=VirtualMachineBasicBiosTypes.SEABIOS,
        memory_min=1*1024*1024*1024,
        memory_max=1*1024*1024*1024,
        video_type=VirtualMachineBasicVideoTypes.QXL,
        xml_template=xml_template_2
    )

    with get_session() as session:
        session.add(vm)
        session.add(vm2)
        session.commit()
