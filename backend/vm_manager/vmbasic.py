from .VmException import VmException
from sqlmodel import Field, SQLModel, select, Relationship
from typing import Optional
from db import get_session
from .ovmf import OvmfPath
from host_manager import libvirt_connection


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
    devices_disk_iscsi: list["VirtualMachineDeviceDiskIscsi"] = Relationship(back_populates="vm")
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

class VirtualMachineDeviceDiskIscsi(SQLModel, table=True):
    __tablename__ = "virtualmachinedevicediskiscsi"
    id: int | None = Field(primary_key=True)
    name: str = Field(nullable=False)
    disk_bus: str = Field(nullable=False) # VirtualMachineBasicDiskBusTypes
    device_type: str = Field(nullable=False) # VirtualMachineBasicDiskDeviceTypes
    iscsi_name: str = Field(nullable=False) # iqn.2013-07.com.example:iscsi-nopool/2
    iscsi_host: str = Field(nullable=False) # example.com
    iscsi_port: int = Field(nullable=False, default=3260) # 3260
    vm_id: int | None = Field(foreign_key="virtualmachine.id")
    vm: VirtualMachineBasic | None = Relationship(back_populates="devices_disk_iscsi")

class VirtualMachineDeviceNetwork(SQLModel, table=True):
    __tablename__ = "virtualmachinedevicenetwork"
    id: int | None = Field(primary_key=True)
    name: str = Field(nullable=False)
    libvirt_name: str = Field(nullable=True)
    type: str = Field(nullable=False) # VirtualMachineBasicNetworkTypes
    mac: str = Field(nullable=True)
    vm_id: int | None = Field(foreign_key="virtualmachine.id")
    vm: VirtualMachineBasic | None = Relationship(back_populates="devices_network")

def init_ovmfpaths():
    with get_session() as session:
        for ovmf_path in session.exec(select(OvmfPath)).all():
            if ovmf_path.name == "OVMF" or ovmf_path.name == "OVMF_SECBOOT":
                session.delete(ovmf_path)
                session.commit()
        session.add(OvmfPath(name="OVMF", path="/usr/share/OVMF/OVMF_CODE_4M.fd", description="OVMF firmware"))
        session.add(OvmfPath(name="OVMF_SECBOOT", path="/usr/share/OVMF/OVMF_CODE_4M.secboot.fd", description="OVMF firmware with secure boot"))
        session.commit()

def init_templates():
    with get_session() as session:
        session.commit()
