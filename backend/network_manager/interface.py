from sqlmodel import Field, SQLModel, select
from typing import Optional
import subprocess
from db import get_session

class NetworkInterface(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(unique=True)
    ipv4_method: str
    ipv4_address: Optional[str] = None
    ipv4_gateway: Optional[str] = None
    ipv4_prefix: Optional[int] = None

def create_interface(interface: NetworkInterface):
    if not isinstance(interface, NetworkInterface):
        raise ValueError("interface must be of type NetworkInterface")
    with get_session() as session:
        session.add(interface)
        session.commit()
        session.refresh(interface)
        return interface

def get_interface_uuid(name: str):
    output = subprocess.run(["nmcli", "connection", "show"], capture_output=True)
    lines = output.stdout.decode().split("\n")
    for line in lines[1:]:
        if line == "":
            continue
        parts = line.split("  ")
        if parts[3] == name:
            return parts[1]
    return None

def apply_interface(interface: NetworkInterface):
    if not isinstance(interface, NetworkInterface):
        raise ValueError("interface must be of type NetworkInterface")
    uuid = get_interface_uuid(interface.name)
    try:
        if interface.ipv4_method == "manual":
            subprocess.run(["nmcli", "connection", "modify", uuid, "ipv4.addresses", f"{interface.ipv4_address}/{interface.ipv4_prefix}"])
            subprocess.run(["nmcli", "connection", "modify", uuid, "ipv4.gateway", interface.ipv4_gateway])
        else:
            subprocess.run(["nmcli", "connection", "modify", uuid, "ipv4.gateway", ""])
            subprocess.run(["nmcli", "connection", "modify", uuid, "ipv4.addresses", ""])
        subprocess.run(["nmcli", "connection", "modify", uuid, "ipv4.method", interface.ipv4_method])
        subprocess.run(["nmcli", "connection", "up", uuid])
    except subprocess.CalledProcessError as e:
        print(f"Error applying interface: {e}")
    read_interfaces(change=True)

def apply_interfaces():
    with get_session() as session:
        interfaces = session.exec(select(NetworkInterface)).all()
        for interface in interfaces:
            apply_interface(interface)
    
    

def get_interface_by_name(name: str):
    with get_session() as session:
        interface = session.exec(select(NetworkInterface).filter(NetworkInterface.name == name)).first()
        return interface

def read_interfaces(change=False):
    read_interfaces_names = []
    output = subprocess.run(["nmcli", "connection", "show", "--active"], capture_output=True)
    lines = output.stdout.decode().split("\n")
    for line in lines[1:]:
        if line == "":
            continue
        parts = line.split("  ")
        if parts[2] == "ethernet":
            uuid = parts[1]
            name = None
            ipv4_method = None
            ipv4_addresses = None
            ipv4_gateway = None
            ipv4_prefix = None

            detail_output = subprocess.run(["nmcli", "connection", "show", uuid], capture_output=True)
            detail_lines = detail_output.stdout.decode().split("\n")
            detail_dict = {}
            for detail_line in detail_lines:
                if ":" in detail_line:
                    split_line = detail_line.split(":")
                    if len(split_line) == 2:
                        key, value = detail_line.split(":")
                        detail_dict[key] = value.strip()

            name = detail_dict.get("connection.interface-name")
            ipv4_method = detail_dict.get("ipv4.method")
            if ipv4_method == "auto":
                ipv4_addresses = detail_dict.get("IP4.ADDRESS[1]").split("/")[0]
                ipv4_prefix = detail_dict.get("IP4.ADDRESS[1]").split("/")[1]
                ipv4_gateway = detail_dict.get("IP4.GATEWAY")
            elif ipv4_method == "manual":
                ipv4_addresses = detail_dict.get("ipv4.addresses").split("/")[0]
                ipv4_prefix = detail_dict.get("ipv4.addresses").split("/")[1]
                ipv4_gateway = detail_dict.get("ipv4.gateway")

            interface = NetworkInterface(
                name=name,
                ipv4_method=ipv4_method,
                ipv4_address=ipv4_addresses,
                ipv4_gateway=ipv4_gateway,
                ipv4_prefix=ipv4_prefix
            )

            read_interfaces_names.append(name)
            if get_interface_by_name(name) is None:
                create_interface(interface)
            
            if change:
                edit_interface(interface, apply=False)

    with get_session() as session:
        interfaces = session.exec(select(NetworkInterface)).all()
        for interface in interfaces:
            if interface.name not in read_interfaces_names:
                session.delete(interface)
        session.commit()

def get_interfaces():
    with get_session() as session:
        interfaces = session.exec(select(NetworkInterface)).all()
        return interfaces

def edit_interface(interface: NetworkInterface, apply=True):
    if not isinstance(interface, NetworkInterface):
        raise ValueError("interface must be of type NetworkInterface")
    with get_session() as session:
        existing_interface = session.exec(select(NetworkInterface).filter(NetworkInterface.name == interface.name)).first()
        if existing_interface:
            session.delete(existing_interface)
            session.commit()
        session.add(interface)
        session.commit()
        session.refresh(interface)
        if apply:
            apply_interface(interface)
        return interface

