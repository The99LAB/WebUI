from db import get_session
from network_manager.interface import NetworkInterfaceEthernet, NetworkInterfaceBridge, apply
from sqlmodel import select, SQLModel
from sqlalchemy import delete

if __name__ == "__main__":
    apply()
