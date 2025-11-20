from db import get_session
from network_manager.interface import NetworkInterfaceEthernet, NetworkInterfaceBridge
from sqlmodel import select, SQLModel
from sqlalchemy import delete

if __name__ == "__main__":
    bridge = NetworkInterfaceBridge(
        interface_name="ens18",
        bridge_name="br0",
        ipv4_method="manual",
        ipv4_address="172.16.254.10",
        ipv4_gateway="172.16.0.1",
        ipv4_prefix=16,
        ipv4_dns=["172.16.0.1"]
    )
    
    interface = NetworkInterfaceEthernet(
        name="ens18",
    )
    
    with get_session() as session:
        # Check if tables exist and if not create them
        SQLModel.metadata.create_all(session.get_bind())
        
        # Clear table networkinterface
        # Use SQLAlchemy delete() to remove all rows from the tables
        session.exec(delete(NetworkInterfaceEthernet))
        session.exec(delete(NetworkInterfaceBridge))
        session.commit()

        session.add(interface)
        session.add(bridge)
        session.commit()

