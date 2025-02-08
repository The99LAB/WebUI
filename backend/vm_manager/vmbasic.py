from .VmException import VmException
from sqlmodel import Field, SQLModel, select, Relationship
from typing import Optional
from db import get_session
from host_manager import libvirt_connection
import libvirt
import time
import os

class OvmfPath(SQLModel, table=True):
    __tablename__ = "ovmfpath"
    id: int | None = Field(primary_key=True)
    name: str = Field(nullable=False, unique=True)
    path: str = Field(nullable=False)
    description: str = Field(nullable=True)

class VirtualMachineXmlTemplate(SQLModel, table=True):
    __tablename__ = "virtualmachinexmltemplate"
    id: int | None = Field(primary_key=True)
    name: str = Field(nullable=False, unique=True)
    content: str = Field(nullable=False)
    description: str = Field(nullable=True)

class VirtualMachineBasicTemplate(SQLModel, table=True):
    __tablename__ = "virtualmachinebasictemplate"
    id: int | None = Field(primary_key=True)
    name: str = Field(unique=True)
    description: str = Field(nullable=True)
    cpu_model: str = Field(nullable=False)
    vcpu: int = Field(nullable=False)
    vcpu_current: int = Field(nullable=False)
    vcpu_custom_topology: bool = Field(default=False)
    vcpu_custom_topology_sockets: int = Field(nullable=True)
    vcpu_custom_topology_dies: int = Field(nullable=True)
    vcpu_custom_topology_cores: int = Field(nullable=True)
    vcpu_custom_topology_threads: int = Field(nullable=True)
    machine_type: str = Field(nullable=False)
    bios_type: str = Field(nullable=False)
    ovmf_path_id: int | None = Field(nullable=True, foreign_key="ovmfpath.id")
    ovmf_path: OvmfPath | None = Relationship()
    memory_min: int = Field(nullable=False)
    memory_max: int = Field(nullable=False)
    video_type: str = Field(nullable=False) # VirtualMachineBasicVideoTypes
    vdisk_required: bool = Field(nullable=False)
    vdisk_type: str = Field(nullable=True) # VirtualMachineBasicVDiskTypes
    vdisk_bus_type: str = Field(nullable=True) # VirtualMachineBasicDiskBusTypes
    vdisk_min_size: int = Field(nullable=True) # in bytes
    network_interface_required: bool = Field(nullable=False)
    network_interface_type: str = Field(nullable=True) # VirtualMachineBasicNetworkTypes
    cdrom_required: bool = Field(nullable=False)
    cdrom_bus_type: str = Field(nullable=True) # VirtualMachineBasicDiskBusTypes
    xml_template_id: int | None = Field(nullable=True, foreign_key="virtualmachinexmltemplate.id")
    xml_template: VirtualMachineXmlTemplate | None = Relationship()

class VirtualMachineBasicBiosTypes:
    OVMF = "ovmf"
    SEABIOS = "seabios"

class VirtualMachineBasicDiskBusTypes:
    VIRTIO = "virtio"
    SATA = "sata"
    SCSI = "scsi"
    USB = "usb"

class VirtualMachineBasicDiskDeviceTypes:
    DISK = "disk"
    CDROM = "cdrom"

class VirtualMachineBasicVDiskTypes:
    QCOW2 = "qcow2"
    RAW = "raw"

class VirtualMachineBasicNetworkTypes:
    VIRTIO = "virtio"
    E1000 = "e1000"
    RTL8139 = "rtl8139"

class VirtualMachineBasicVideoTypes:
    VIRTIO = "virtio"
    QXL = "qxl"
    VGA = "vga"

class VirtualMachineBasic(SQLModel, table=True):
    __tablename__ = "virtualmachine"
    id: int | None = Field(primary_key=True)
    name: str = Field(unique=True)
    status: str = Field(nullable=True)
    autostart: bool = Field(default=False)
    cpu_model: str = Field(nullable=False)
    vcpu: int = Field(nullable=False)
    vcpu_current: int = Field(nullable=False)
    vcpu_custom_topology: bool = Field(default=False)
    vcpu_custom_topology_sockets: int = Field(nullable=True)
    vcpu_custom_topology_dies: int = Field(nullable=True)
    vcpu_custom_topology_cores: int = Field(nullable=True)
    vcpu_custom_topology_threads: int = Field(nullable=True)
    machine_type: str = Field(nullable=False)
    bios_type: str = Field(nullable=False)
    ovmf_path_id: int | None = Field(nullable=True, foreign_key="ovmfpath.id")
    ovmf_path: OvmfPath | None = Relationship()
    memory_min: int = Field(nullable=False)
    memory_max: int = Field(nullable=False)
    video_type: str = Field(nullable=False) # VirtualMachineBasicVideoTypes
    devices_pci: list["VirtualMachineDevicePci"] = Relationship(back_populates="vm")
    devices_disk_file: list["VirtualMachineDeviceDiskFile"] = Relationship(back_populates="vm")
    devices_disk_block: list["VirtualMachineDeviceDiskBlock"] = Relationship(back_populates="vm")
    devices_network: list["VirtualMachineDeviceNetwork"] = Relationship(back_populates="vm")
    xml_template_id: int | None = Field(nullable=False, foreign_key="virtualmachinexmltemplate.id")
    xml_template: VirtualMachineXmlTemplate | None = Relationship()

class VirtualMachineDevicePci(SQLModel, table=True):
    __tablename__ = "virtualmachinedevicepci"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    domain: str = Field(nullable=False)
    bus: str = Field(nullable=False)
    slot: str = Field(nullable=False)
    function: str = Field(nullable=False)
    rom_use: bool = Field(nullable=False)
    rom_file: str = Field(nullable=True)
    last_pci_id: str = Field(nullable=True)
    vm_id: int | None = Field(default=None, foreign_key="virtualmachine.id")
    vm: VirtualMachineBasic | None = Relationship(back_populates="devices_pci")

class VirtualMachineDeviceDiskFile(SQLModel, table=True):
    __tablename__ = "virtualmachinedevicediskfile"
    id: int | None = Field(primary_key=True)
    name: str = Field(nullable=False)
    disk_bus: str = Field(nullable=False) # VirtualMachineBasicDiskBusTypes
    device_type: str = Field(nullable=False) # VirtualMachineBasicDiskDeviceTypes
    disk_source_file: str = Field(nullable=False) # /path/to/file
    vm_id: int | None = Field(foreign_key="virtualmachine.id")
    vm: VirtualMachineBasic | None = Relationship(back_populates="devices_disk_file")

class VirtualMachineDeviceDiskBlock(SQLModel, table=True):
    __tablename__ = "virtualmachinedevicediskblock"
    id: int | None = Field(primary_key=True)
    name: str = Field(nullable=False)
    disk_bus: str = Field(nullable=False) # VirtualMachineBasicDiskBusTypes
    device_type: str = Field(nullable=False) # VirtualMachineBasicDiskDeviceTypes
    disk_source_block: str = Field(nullable=False) # /dev/sda
    vm_id: int | None = Field(foreign_key="virtualmachine.id")
    vm: VirtualMachineBasic | None = Relationship(back_populates="devices_disk_block")

class VirtualMachineDeviceNetwork(SQLModel, table=True):
    __tablename__ = "virtualmachinedevicenetwork"
    id: int | None = Field(primary_key=True)
    libvirt_name: str = Field(nullable=True)
    type: str = Field(nullable=False) # VirtualMachineBasicNetworkTypes
    mac: str = Field(nullable=True)
    vm_id: int | None = Field(foreign_key="virtualmachine.id")
    vm: VirtualMachineBasic | None = Relationship(back_populates="devices_network")

    
class VirtualMachineBasicLibvirtConfig:
    def __init__(self, vm: VirtualMachineBasic):
        self.vm = vm
        self.conn = libvirt_connection.connection

    def to_dict(self):
        vm_dict = self.vm.model_dump()
        vm_dict["status"] = self.get_status()
        vm_dict["devices_pci"] = [device.model_dump() for device in self.vm.devices_pci]
        vm_dict["devices_disk_file"] = [device.model_dump() for device in self.vm.devices_disk_file]
        vm_dict["devices_disk_block"] = [device.model_dump() for device in self.vm.devices_disk_block]
        vm_dict["devices_network"] = [device.model_dump() for device in self.vm.devices_network]
        return vm_dict

    def gen_graphics(self):
        return f"""<graphics type='spice' port='-1' autoport='yes'><listen type='address' address='127.0.0.1'/> </graphics>"""
    
    def gen_video(self):
        return f"""<video><model type='{self.vm.video_type}'/> </video>"""
    
    def gen_loader(self):
        if self.vm.bios_type == VirtualMachineBasicBiosTypes.OVMF:
            nvram_path = "/mnt/data/s99-vmb-vars/"
            if not os.path.exists(nvram_path):
                os.makedirs(nvram_path)
            nvram_path += f"{self.vm.id}.fd"
            return f"""<loader readonly='yes' type='pflash'>{self.vm.ovmf_path.path}</loader>
            <nvram>{nvram_path}</nvram>"""
        else:
            return ""
        
    def gen_devices_disk_file(self):
        devices_disk_file = ""
        for index, device in enumerate(self.vm.devices_disk_file):
            targetdev = "sd"
            targetdev += chr(ord("a") + index)
            drivertype = "raw"
            if device.disk_source_file.endswith(".qcow2"):
                drivertype = "qcow2"
            devices_disk_file += f"""<disk type='file' device='{device.device_type}'>
            <driver name='qemu' type='{drivertype}'/>
            <source file='{device.disk_source_file}'/>
            <target dev='{targetdev}' bus='{device.disk_bus}'/>
            </disk>"""
        print(devices_disk_file)
        return devices_disk_file
    
    def gen_devices_network(self):
        devices_network = ""
        for index, device in enumerate(self.vm.devices_network):
            if device.mac:
                devices_network += f"""<interface type='network'>
                <mac address='{device.mac}'/>
                <source network='{device.libvirt_name}'/>
                <model type='{device.type}'/>
                </interface>"""
            else:
                devices_network += f"""<interface type='network'>
                <source network='{device.libvirt_name}'/>
                <model type='{device.type}'/>
                </interface>"""
        return devices_network

    def gen_xml(self):
        xml = None
        xml = self.vm.xml_template.content.split("\n")
        xml = "".join(xml)
        xml = xml.replace("{%name%}", f"s99b-{self.vm.id}")
        xml = xml.replace("{%cpu_model%}", self.vm.cpu_model)
        xml = xml.replace("{%vcpu%}", str(self.vm.vcpu))
        xml = xml.replace("{%vcpu_current%}", str(self.vm.vcpu_current))
        xml = xml.replace("{%memory_min%}", str(self.vm.memory_min))
        xml = xml.replace("{%memory_max%}", str(self.vm.memory_max))
        xml = xml.replace("{%machine_type%}", self.vm.machine_type)
        xml = xml.replace("{%loader%}", self.gen_loader())
        xml = xml.replace("{%qemu_path%}", "/usr/bin/qemu-system-x86_64")
        xml = xml.replace("{%devices_disk_file%}", self.gen_devices_disk_file())
        xml = xml.replace("{%devices_network%}", self.gen_devices_network())
        xml = xml.replace("{%graphics%}", self.gen_graphics())
        xml = xml.replace("{%video%}", self.gen_video())
        # print(xml)
        return xml

    def get_libvirt_domain(self):
        return self.conn.lookupByName(f"s99b-{self.vm.id}")
    
    def start(self):
        xml = self.gen_xml()
        try:
            self.conn.defineXML(xml)
            libvirt_domain = self.get_libvirt_domain()
            libvirt_domain.create()
        except libvirt.libvirtError as e:
            self.remove()
            raise VmException(e)

    def shutdown(self):
        libvirt_domain = self.get_libvirt_domain()
        if libvirt_domain.isActive():
            print("Shutting down VM")
            libvirt_domain.shutdown() # send shutdown signal
            # wait up to 30 seconds for the VM to shutdown
            # if the VM is still running after 30 seconds, force stop it
            for i in range(30):
                if libvirt_domain.isActive():
                    time.sleep(1)
                else:
                    print("VM has been shutdown")
                    break
        self.remove()

    def forcestop(self):
        self.remove()

    def reset(self):
        libvirt_domain = self.get_libvirt_domain()
        libvirt_domain.reset()

    def get_status(self):
        try:
            libvirt_domain = self.get_libvirt_domain()
            vm_state = None
            state, result = libvirt_domain.state()
            if state == libvirt.VIR_DOMAIN_RUNNING:
                vm_state = "Running"
            elif state == libvirt.VIR_DOMAIN_PAUSED:
                vm_state = "Paused"
            elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
                vm_state = "Shutdown"
            elif state == libvirt.VIR_DOMAIN_SHUTOFF:
                vm_state = "Shutoff"
            elif state == libvirt.VIR_DOMAIN_CRASHED:
                vm_state = "Crashed"
            elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:
                vm_state = "Pmsuspended"
            else:
                vm_state = "Unknown"
            return vm_state
        except libvirt.libvirtError as e:
            return "Shutoff"

    def remove(self):
        try:
            libvirt_domain = self.get_libvirt_domain()
            if libvirt_domain.isActive():
                libvirt_domain.destroy()
            libvirt_domain.undefineFlags(4)
        except libvirt.libvirtError as e:
            pass

def get_vm_networks():
    networks = libvirt_connection.connection.listAllNetworks()
    networks_list = []
    for network in networks:
        network_active = network.isActive()
        if network_active == 1:
            network_active = True
        else:
            network_active = False
        _network = {
            "uuid": network.UUIDString(),
            "name": network.name(),
            "active": network_active,            
        }
        networks_list.append(_network)
    return networks_list

def init_ovmfpaths():
    with get_session() as session:
        for ovmf_path in session.exec(select(OvmfPath)).all():
            if ovmf_path.name == "OVMF" or ovmf_path.name == "OVMF_SECBOOT":
                session.delete(ovmf_path)
        session.add(OvmfPath(name="OVMF", path="/usr/share/OVMF/OVMF_CODE_4M.fd", description="OVMF firmware"))
        session.add(OvmfPath(name="OVMF_SECBOOT", path="/usr/share/OVMF/OVMF_CODE_4M.secboot.fd", description="OVMF firmware with secure boot"))
        session.commit()

def init_templates():
    with get_session() as session:
        session.commit()
