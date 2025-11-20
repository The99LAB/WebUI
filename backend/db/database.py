from sqlmodel import create_engine, SQLModel, Session

sqlite_file_name = "/mnt/data/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def get_session():
    return Session(engine)

def create_db_and_tables():
    from network_manager.interface import read, apply
    from vm_manager.vmbasic import init_ovmfpaths
    SQLModel.metadata.create_all(engine)
    init_ovmfpaths()
    read()
    apply()
