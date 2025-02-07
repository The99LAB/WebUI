from sqlmodel import create_engine, SQLModel, Session

sqlite_file_name = "/mnt/data/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def get_session():
    return Session(engine)

def create_db_and_tables():
    from network_manager.interface import NetworkInterface, read_interfaces, apply_interfaces
    from vm_manager.vmbasic import OvmfPath, VirtualMachineBasicTemplate, VirtualMachineBasic, VirtualMachineDeviceDiskFile, VirtualMachineDeviceDiskBlock, VirtualMachineDeviceNetwork, VirtualMachineDevicePci, init_ovmfpaths, init_templates
    SQLModel.metadata.create_all(engine)
    read_interfaces()
    apply_interfaces()
    init_ovmfpaths()

