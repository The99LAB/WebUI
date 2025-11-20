from db import get_session
from vm_manager.vmbasic import OvmfPath, VirtualMachineBasicTemplate, VirtualMachineBasicDiskBusTypes, VirtualMachineBasicDiskDeviceTypes, VirtualMachineBasicVDiskTypes, VirtualMachineBasicNetworkTypes, VirtualMachineBasicVideoTypes, VirtualMachineBasic, VirtualMachineDeviceDiskBlock, VirtualMachineDeviceNetwork, VirtualMachineDeviceDiskFile, VirtualMachineDevicePci, VirtualMachineBasicBiosTypes, VirtualMachineXmlTemplate
from sqlmodel import select

"""
Create a simple Linux VM with a CDROM drive and a network interface.
"""


if __name__ == "__main__":
    xml_template = None
    with get_session() as session:
        xml_template = session.exec(select(VirtualMachineXmlTemplate).where(VirtualMachineXmlTemplate.name == "Basic VM")).first()

    ovmf_path = None
    with get_session() as session:
        ovmf_path = session.exec(select(OvmfPath).where(OvmfPath.name == "OVMF")).first()

    disk_device_file_cdrom = VirtualMachineDeviceDiskFile(
        name="Linux CDROM",
        disk_bus=VirtualMachineBasicDiskBusTypes.SATA,
        device_type=VirtualMachineBasicDiskDeviceTypes.CDROM,
        disk_source_file="/mnt/isos/debian-10.13.0-amd64-netinst.iso"
    )

    network_device = VirtualMachineDeviceNetwork(
        libvirt_name="default",
        type=VirtualMachineBasicNetworkTypes.VIRTIO
    )
        
    vm = VirtualMachineBasic(
        name="Linux VM",
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
        memory_max=2*1024*1024*1024,
        video_type=VirtualMachineBasicVideoTypes.QXL,
        devices_disk_file=[disk_device_file_cdrom],
        devices_network=[network_device],
        xml_template=xml_template
    )

    with get_session() as session:
        session.add(vm)
        session.commit()
