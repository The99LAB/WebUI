from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class VirtualMachineTemplate(SQLModel, table=True):
    __tablename__ = "virtualmachinetemplate"
    id: int | None = Field(primary_key=True)
    name: str = Field(unique=True)
    description: str = Field(nullable=True)
    xml: str = Field(nullable=False)

class VirtualMachineBasic(SQLModel, table=True):
    __tablename__ = "virtualmachine"
    id: int | None = Field(primary_key=True)
    name: str = Field(unique=True)
    libvirt_uuid: str = Field(nullable=True)
    autostart: bool = Field(default=False)
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
    memory_min: int = Field(nullable=False)
    memory_max: int = Field(nullable=False)
    graphics_type: str = Field(nullable=False)
    devices_pci: list["VirtualMachineDevicePci"] = Relationship(back_populates="vm")
    devices_disk: list["VirtualMachineDeviceDisk"] = Relationship(back_populates="vm")
    devices_network: list["VirtualMachineDeviceNetwork"] = Relationship(back_populates="vm")
    template_id: int | None = Field(default=None, foreign_key="virtualmachinetemplate.id")
    template: VirtualMachineTemplate | None = Relationship()

class OvmfPath(SQLModel, table=True):
    __tablename__ = "ovmfpath"
    id: int | None = Field(primary_key=True)
    name: str = Field(nullable=False, unique=True)
    path: str = Field(nullable=False)
    description: str = Field(nullable=True)

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

class VirtualMachineDeviceDisk(SQLModel, table=True):
    __tablename__ = "virtualmachinedevicedisk"
    id: int | None = Field(primary_key=True)
    name: str = Field(nullable=False)
    disk_type: str = Field(nullable=False) # file, block
    disk_bus: str = Field(nullable=False) # virtio, sata, scsi, usb
    device_type: str = Field(nullable=False) # disk, cdrom
    disk_source_file: str | None = Field(nullable=True) # /path/to/file
    disk_source_block: str | None = Field(nullable=True) # /dev/sda
    vm_id: int | None = Field(foreign_key="virtualmachine.id")
    vm: VirtualMachineBasic | None = Relationship(back_populates="devices_disk")

class VirtualMachineDeviceNetwork(SQLModel, table=True):
    __tablename__ = "virtualmachinedevicenetwork"
    id: int | None = Field(primary_key=True)
    libvirt_uuid: str = Field(nullable=True)
    type: str = Field(nullable=False) # virtio, e1000, rtl8139
    mac: str = Field(nullable=True)
    vm_id: int | None = Field(foreign_key="virtualmachine.id")
    vm: VirtualMachineBasic | None = Relationship(back_populates="devices_network")

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_vm():
    with Session(engine) as session:
        template = VirtualMachineTemplate(name="template1", description="A sample template", xml="<xml></xml>")
        ovmfpath = OvmfPath(name="ovmfpath1", path="/path/to/ovmf", description="A sample OVMF path")
        vm = VirtualMachineBasic(name="vm1", vcpu=2, vcpu_current=2, vcpu_custom_topology=False, machine_type="q35", bios_type="ovmf", memory_min=1024, memory_max=4096, graphics_type="virtio",template=template)
        pci_device = VirtualMachineDevicePci(name="device1", domain="0000", bus="00", slot="00", function="00", rom_use=False, vm=vm)
        disk_device = VirtualMachineDeviceDisk(name="disk1", disk_type="file", disk_bus="virtio", device_type="disk", disk_source_file="/path/to/disk.img", vm=vm)
        network_device = VirtualMachineDeviceNetwork(type="virtio", vm=vm)

        session.add(template)
        session.add(ovmfpath)
        session.add(vm)
        session.add(pci_device)
        session.add(disk_device)
        session.add(network_device)
        session.commit()

        session.refresh(template)
        session.refresh(ovmfpath)
        session.refresh(vm)
        session.refresh(pci_device)
        session.refresh(disk_device)
        session.refresh(network_device)

        print("Created template:", template)
        print("Created vm:", vm)
        print("Created pci device:", pci_device)
        print("Created disk device:", disk_device)
        print("Created network device:", network_device)

def lookup_vm():
    with Session(engine) as session:
        vm = session.exec(select(VirtualMachineBasic)).first()
        print("VM:", vm)
        print("VM template:", vm.template)
        print("VM PCI devices:", vm.devices_pci)
        print("VM disk devices:", vm.devices_disk)
        print("VM network devices:", vm.devices_network)

def main():
    create_db_and_tables()
    create_vm()
    lookup_vm()

if __name__ == "__main__":
    main()