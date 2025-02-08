from db import get_session
from vm_manager.vmbasic import OvmfPath, VirtualMachineBasicTemplate, VirtualMachineBasicDiskBusTypes, VirtualMachineBasicDiskDeviceTypes, VirtualMachineBasicVDiskTypes, VirtualMachineBasicNetworkTypes, VirtualMachineBasicVideoTypes, VirtualMachineBasicBiosTypes, VirtualMachineXmlTemplate
from sqlmodel import select

def insert_vm_templates():
    xml_template = VirtualMachineXmlTemplate(
        name="Basic VM",
        description="Basic VM",
        content=
"""<domain type='kvm'>
<name>{%name%}</name>
<memory unit='B'>{%memory_max%}</memory>
<currentMemory unit='B'>{%memory_min%}</currentMemory>
<vcpu placement='static' current='{%vcpu_current%}'>{%vcpu%}</vcpu>
<os>
    <type arch='x86_64' machine='{%machine_type%}'>hvm</type>
    {%loader%}
    <bootmenu enable="yes"/>
</os>
<features>
    <acpi/>
    <apic/>
    <hyperv mode='custom'>
    <relaxed state='on'/>
    <vapic state='on'/>
    <spinlocks state='on' retries='8191'/>
    </hyperv>
    <vmport state='off'/>
</features>
<cpu mode='{%cpu_model%}' check='partial'/>
<clock offset='utc'/>
<on_poweroff>destroy</on_poweroff>
<on_reboot>restart</on_reboot>
<on_crash>destroy</on_crash>
<devices>
    <emulator>{%qemu_path%}</emulator>
    {%devices_disk_file%}
    {%devices_network%}
    <controller type='pci' index='0' model='pcie-root'/>
    <input type='tablet' bus='usb'>
    <address type='usb' bus='0' port='1'/>
    </input>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    {%graphics%}
    {%video%}
</devices>
</domain>""")
    
    xml_template_2 = VirtualMachineXmlTemplate(
        name="Basic VM USB2",
        description="Basic VM with USB2",
        content=
"""<domain type='kvm'>
<name>{%name%}</name>
<memory unit='B'>{%memory_max%}</memory>
<currentMemory unit='B'>{%memory_min%}</currentMemory>
<vcpu placement='static' current='{%vcpu_current%}'>{%vcpu%}</vcpu>
<os>
    <type arch='x86_64' machine='{%machine_type%}'>hvm</type>
    {%loader%}
    <bootmenu enable="yes"/>
</os>
<features>
    <acpi/>
    <apic/>
    <hyperv mode='custom'>
    <relaxed state='on'/>
    <vapic state='on'/>
    <spinlocks state='on' retries='8191'/>
    </hyperv>
    <vmport state='off'/>
</features>
<cpu mode='{%cpu_model%}' check='partial'/>
<clock offset='utc'/>
<on_poweroff>destroy</on_poweroff>
<on_reboot>restart</on_reboot>
<on_crash>destroy</on_crash>
<devices>
    <emulator>{%qemu_path%}</emulator>
    {%devices_disk_file%}
    {%devices_network%}
    <controller type='pci' index='0' model='pcie-root'/>
    <controller type="usb" index="0" model="ich9-ehci1"/>
    <controller type="usb" index="0" model="ich9-uhci1">
      <master startport="0"/>
    </controller>
    <controller type="usb" index="0" model="ich9-uhci2">
      <master startport="2"/>
    </controller>
    <controller type="usb" index="0" model="ich9-uhci3">
      <master startport="4"/>
    </controller>
    <input type='tablet' bus='usb'>
    <address type='usb' bus='0' port='1'/>
    </input>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    {%graphics%}
    {%video%}
</devices>
</domain>""")

    # OVMF_path is the OVMF path in the database with name "OVMF"
    # use get_session() to get a session
    ovmf_path = None
    with get_session() as session:
        # Select ovmfpath from OvmfPath where name is "OVMF"
        ovmf_path = session.exec(select(OvmfPath).where(OvmfPath.name == "OVMF")).first()


    vm_template = VirtualMachineBasicTemplate(
        name="Windows 10", 
        description="Windows 10", 
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
        vdisk_required=True,
        vdisk_type=VirtualMachineBasicVDiskTypes.QCOW2,
        vdisk_bus_type=VirtualMachineBasicDiskBusTypes.SATA,
        vdisk_min_size=40*1024*1024*1024,
        network_interface_required=True,
        network_interface_type=VirtualMachineBasicNetworkTypes.E1000,
        cdrom_required=True,
        cdrom_bus_type=VirtualMachineBasicDiskBusTypes.SATA,
        xml_template=xml_template
    )

    vm_template_2 = VirtualMachineBasicTemplate(
        name="Windows 7",
        description="Windows 7",
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
        vdisk_required=True,
        vdisk_type=VirtualMachineBasicVDiskTypes.QCOW2,
        vdisk_bus_type=VirtualMachineBasicDiskBusTypes.SATA,
        vdisk_min_size=40*1024*1024*1024,
        network_interface_required=True,
        network_interface_type=VirtualMachineBasicNetworkTypes.E1000,
        cdrom_required=True,
        cdrom_bus_type=VirtualMachineBasicDiskBusTypes.SATA,
        xml_template=xml_template_2
    )

    with get_session() as session:
        session.add(xml_template)
        session.add(xml_template_2)
        session.add(vm_template)
        session.add(vm_template_2)
        session.commit()

if __name__ == "__main__":
    insert_vm_templates()
