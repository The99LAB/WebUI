from sqlmodel import Field, SQLModel, select, Column, JSON
from typing import Optional
import subprocess
from db import get_session
import jc

class NetworkInterfaceEthernet(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(unique=True)
    ipv4_method: Optional[str] = None  # 'auto' or 'manual'
    ipv4_address: Optional[str] = None
    ipv4_gateway: Optional[str] = None
    ipv4_prefix: Optional[int] = None
    ipv4_dns: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))

class NetworkInterfaceBridge(SQLModel, table=True):
    id: int = Field(primary_key=True)
    interface_name: str = Field(foreign_key="networkinterfaceethernet.name")
    bridge_name: str = Field()
    mac_address: Optional[str] = None  # Persistent MAC address for the bridge
    ipv4_method: Optional[str] = None  # 'auto' or 'manual'
    ipv4_address: Optional[str] = None
    ipv4_gateway: Optional[str] = None
    ipv4_prefix: Optional[int] = None
    ipv4_dns: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))


def create_interface_bridge(bridge: NetworkInterfaceBridge):
    if not isinstance(bridge, NetworkInterfaceBridge):
        raise ValueError("bridge must be of type NetworkInterfaceBridge")
    with get_session() as session:
        session.add(bridge)
        session.commit()
        session.refresh(bridge)
        return bridge


def get_bridge_by_interface(interface_name: str):
    with get_session() as session:
        bridge = session.exec(select(NetworkInterfaceBridge).filter(NetworkInterfaceBridge.interface_name == interface_name)).first()
        return bridge


def edit_interface_bridge(bridge: NetworkInterfaceBridge):
    if not isinstance(bridge, NetworkInterfaceBridge):
        raise ValueError("bridge must be of type NetworkInterfaceBridge")
    with get_session() as session:
        existing = session.exec(select(NetworkInterfaceBridge).filter(NetworkInterfaceBridge.interface_name == bridge.interface_name)).first()
        if existing:
            session.delete(existing)
            session.commit()
        session.add(bridge)
        session.commit()
        session.refresh(bridge)
        return bridge


def get_interface_bridge_uuid(name: str):
    """Return the nmcli connection UUID for a connection with the given name (bridge name / connection name).
    Falls back to returning None if not found.
    """
    output = subprocess.check_output(["nmcli", "connection", "show"], text=True)
    result = jc.parse('nmcli', output)
    for entry in result:
        # connection 'name' field corresponds to con-name
        if entry.get('name') == name:
            return entry.get('uuid')
    return None


def get_interface_bridges():
    """
    Retrieve all Bridge interfaces from the database.
    For bridges with 'auto' IPv4 method, fetch current IP settings from nmcli.
    """
    with get_session() as session:
        bridges = session.exec(select(NetworkInterfaceBridge)).all()
        for bridge in bridges:
            if bridge.ipv4_method == "auto":
                bridge_uuid = get_interface_bridge_uuid(bridge.bridge_name)
                if bridge_uuid:
                    detail_output = subprocess.check_output(["nmcli", "connection", "show", bridge_uuid], text=True)
                    detail_result = jc.parse('nmcli', detail_output)[0]
                    ip_addr_str = detail_result.get("ip4_address_1", "")
                    if ip_addr_str and "/" in ip_addr_str:
                        bridge.ipv4_address = ip_addr_str.split("/")[0]
                        bridge.ipv4_prefix = int(ip_addr_str.split("/")[1])
                    bridge.ipv4_gateway = detail_result.get("ip4_gateway")
    return bridges


def apply_interface_bridge(bridge: NetworkInterfaceBridge):
    """Apply IP settings to a bridge connection and ensure the slave interface is down while the bridge is up."""
    if not isinstance(bridge, NetworkInterfaceBridge):
        raise ValueError("bridge must be of type NetworkInterfaceBridge")
    print(f"Applying bridge settings for {bridge.bridge_name} (slave: {bridge.interface_name})")
    bridge_uuid = get_interface_bridge_uuid(bridge.bridge_name)
    if bridge_uuid is None:
        # Create the bridge connection if it doesn't exist
        subprocess.run(["nmcli", "con", "add", "ifname", bridge.bridge_name, "type", "bridge", "con-name", bridge.bridge_name], check=False)
        subprocess.run(["nmcli", "con", "add", "type", "bridge-slave", "ifname", bridge.interface_name, "master", bridge.bridge_name], check=False)
        bridge_uuid = get_interface_bridge_uuid(bridge.bridge_name)
    interface_uuid = get_interface_ethernet_uuid(bridge.interface_name)
    print(f"Bridge UUID: {bridge_uuid}, Interface UUID: {interface_uuid}")
    try:
        if bridge.ipv4_method == "manual":
            subprocess.run(["nmcli", "connection", "modify", bridge_uuid, "ipv4.addresses", f"{bridge.ipv4_address}/{bridge.ipv4_prefix}"], check=False)
            subprocess.run(["nmcli", "connection", "modify", bridge_uuid, "ipv4.gateway", bridge.ipv4_gateway or ""], check=False)
        else:
            # clear manual settings on bridge if any
            subprocess.run(["nmcli", "connection", "modify", bridge_uuid, "ipv4.gateway", ""], check=False)
            subprocess.run(["nmcli", "connection", "modify", bridge_uuid, "ipv4.addresses", ""], check=False)
        subprocess.run(["nmcli", "connection", "modify", bridge_uuid, "ipv4.dns", ",".join(bridge.ipv4_dns) if bridge.ipv4_dns else ""], check=False)
        subprocess.run(["nmcli", "connection", "modify", bridge_uuid, "ipv4.method", bridge.ipv4_method or ""], check=False)
        
        if bridge.mac_address:
            subprocess.run(["nmcli", "connection", "modify", bridge_uuid, "ethernet.cloned-mac-address", bridge.mac_address], check=False)
        
        # Bring down the physical/slave interface and bring up the bridge
        if interface_uuid:
            subprocess.run(["nmcli", "connection", "down", interface_uuid], check=False)
        subprocess.run(["nmcli", "connection", "up", bridge_uuid], check=False)
    except subprocess.CalledProcessError as e:
        print(f"Error applying bridge: {e}")


def create_interface_ethernet(interface: NetworkInterfaceEthernet):
    if not isinstance(interface, NetworkInterfaceEthernet):
        raise ValueError("interface must be of type NetworkInterface")
    with get_session() as session:
        session.add(interface)
        session.commit()
        session.refresh(interface)
        return interface


def get_interface_ethernet_uuid(name: str):
    output = subprocess.check_output(["nmcli", "connection", "show"], text=True)
    result = jc.parse('nmcli', output)
    for entry in result:
        if entry['name'] == name:
            return entry['uuid']
    return None


def edit_interface_ethernet(interface: NetworkInterfaceEthernet):
    """
    Edit a network interface in the database.
    """
    if not isinstance(interface, NetworkInterfaceEthernet):
        raise ValueError("interface must be of type NetworkInterface")
    with get_session() as session:
        existing_interface = session.exec(select(NetworkInterfaceEthernet).filter(NetworkInterfaceEthernet.name == interface.name)).first()
        if existing_interface:
            session.delete(existing_interface)
            session.commit()
        session.add(interface)
        session.commit()
        session.refresh(interface)
        return interface


def get_interface_ethernets():    
    """
    Retrieve all Ethernet interfaces from the database.
    For interfaces with 'auto' IPv4 method, fetch current IP settings from nmcli.
    """
    with get_session() as session:
        interfaces = session.exec(select(NetworkInterfaceEthernet)).all()
        for interface in interfaces:
            if interface.ipv4_method == "auto":
                uuid = get_interface_ethernet_uuid(interface.name)
                if uuid:
                    detail_output = subprocess.check_output(["nmcli", "connection", "show", uuid], text=True)
                    detail_result = jc.parse('nmcli', detail_output)[0]
                    ip_addr_str = detail_result.get("ip4_address_1", "")
                    if ip_addr_str and "/" in ip_addr_str:
                        interface.ipv4_address = ip_addr_str.split("/")[0]
                        interface.ipv4_prefix = int(ip_addr_str.split("/")[1])
                    interface.ipv4_gateway = detail_result.get("ip4_gateway")
    return interfaces


def apply_interface_ethernet(interface: NetworkInterfaceEthernet):
    if not isinstance(interface, NetworkInterfaceEthernet):
        raise ValueError("interface must be of type NetworkInterface")
    
    # Check if this interface has a bridge associated
    bridge = get_bridge_by_interface(interface.name)
    if bridge is not None:
        print(f"Interface {interface.name} is part of bridge {bridge.bridge_name}, skipping apply.")
        return

    uuid = get_interface_ethernet_uuid(interface.name)
    print(f"Applying settings to interface {interface.name} with UUID {uuid}")
    if uuid is None:
        print(f"No nmcli connection found for interface {interface.name}, creating one.")
        # Create a new connection for this interface
        subprocess.run(["nmcli", "con", "add", "type", "ethernet", "ifname", interface.name, "con-name", interface.name], check=False)
        uuid = get_interface_ethernet_uuid(interface.name)
        if uuid is None:
            print(f"Failed to create nmcli connection for interface {interface.name}, skipping apply.")
            return
    try:
        if interface.ipv4_method == "manual":
            print(f"Applying manual settings to interface {interface.name}")
            print(f"Setting address: {interface.ipv4_address}/{interface.ipv4_prefix}, gateway: {interface.ipv4_gateway}")
            subprocess.run(["nmcli", "connection", "modify", uuid, "ipv4.addresses", f"{interface.ipv4_address}/{interface.ipv4_prefix}"])
            subprocess.run(["nmcli", "connection", "modify", uuid, "ipv4.gateway", interface.ipv4_gateway])
            subprocess.run(["nmcli", "connection", "modify", uuid, "ipv4.method", "manual"])
            subprocess.run(["nmcli", "connection", "modify", uuid, "ipv4.dns", ",".join(interface.ipv4_dns) if interface.ipv4_dns else ""], check=False)
        elif interface.ipv4_method == "auto":
            subprocess.run(["nmcli", "connection", "modify", uuid, "ipv4.gateway", ""])
            subprocess.run(["nmcli", "connection", "modify", uuid, "ipv4.addresses", ""])
            subprocess.run(["nmcli", "connection", "modify", uuid, "ipv4.method", "auto"])
            subprocess.run(["nmcli", "connection", "modify", uuid, "ipv4.dns", ",".join(interface.ipv4_dns) if interface.ipv4_dns else ""], check=False)
        else:
            print(f"Interface {interface.name} has no ipv4_method set. The interface will be disabled.")
            subprocess.run(["nmcli", "connection", "down", uuid])        
    except subprocess.CalledProcessError as e:
        print(f"Error applying interface: {e}")


def update_interface_bridges_mac_addresses():
    """Fetch and update MAC addresses for bridges that don't have one stored yet."""
    with get_session() as session:
        bridges = session.exec(select(NetworkInterfaceBridge)).all()
        for bridge in bridges:
            print(f"Checking MAC address for bridge {bridge.bridge_name}")
            if not bridge.mac_address:
                # Fetch and store the generated MAC address for the bridge
                detail_output = subprocess.check_output(["nmcli", "device", "show", bridge.bridge_name], text=True)
                detail_result = jc.parse('nmcli', detail_output)[0]
                mac_address = detail_result.get("hwaddr")
                if mac_address:
                    print(f"Storing MAC address {mac_address} for bridge {bridge.bridge_name}")
                    bridge.mac_address = mac_address
        # Commit all changes at once within the same session
        session.commit()


def apply():
    """
    - Reset all interfaces to default (deleting all existing nmcli connections except loopback)
    - Apply ethernet interfaces from the database
    - Apply bridge interfaces from the database
    """
    # First remove all interface settings
    reset()

    with get_session() as session:
        interfaces = session.exec(select(NetworkInterfaceEthernet)).all()
        for interface in interfaces:
            apply_interface_ethernet(interface)
    # Also apply bridge records (if any)
    with get_session() as session:
        bridges = session.exec(select(NetworkInterfaceBridge)).all()
        for bridge in bridges:
            apply_interface_bridge(bridge)
    
    update_interface_bridges_mac_addresses()


def read():
    """
    Synchronize the database with the current network interfaces from nmcli.
    - Adds interfaces to the database that aren't in there yet
    - Removes interfaces from the database that don't exist anymore
    """
    # Get all physical network interfaces from "/sys/class/net"
    physical_interfaces = []
    import os
    for iface in os.listdir("/sys/class/net"):
        if os.path.islink(f"/sys/class/net/{iface}/device"):
            physical_interfaces.append(iface)
    
    print(f"Physical interfaces found: {physical_interfaces}")

    with get_session() as session:
        # Get all interfaces currently in the database
        db_interfaces = session.exec(select(NetworkInterfaceEthernet)).all()
        db_interface_names = [iface.name for iface in db_interfaces]

        # Add missing interfaces to the database
        for iface_name in physical_interfaces:
            if iface_name not in db_interface_names:
                print(f"Adding missing interface to DB: {iface_name}")
                new_iface = NetworkInterfaceEthernet(name=iface_name, ipv4_method=None)
                session.add(new_iface)
        
        # Remove interfaces from the database that no longer exist
        for db_iface in db_interfaces:
            if db_iface.name not in physical_interfaces:
                print(f"Removing non-existing interface from DB: {db_iface.name}")
                session.delete(db_iface)
        
        session.commit()


def reset():
    """
    Reset all network interfaces to their default settings by deleting all interfaces except loopback.
    """
    print("Resetting all network interfaces to default settings...")
    
    try:        
        output = subprocess.check_output(["nmcli", "connection", "show"], text=True)
        result = jc.parse('nmcli', output)
        for entry in result:
            conn_name = entry.get('name')
            conn_uuid = entry.get('uuid')
            conn_type = entry.get('type')
            if conn_type != "loopback":
                print(f"Deleting {conn_type} connection: {conn_name} ({conn_uuid})")
                try:
                    subprocess.run(["nmcli", "connection", "delete", conn_uuid], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error deleting {conn_name}: {e}")
        
        print("Reset complete.")

    except Exception as e:
        print(f"An error occurred while resetting interfaces: {e}") 
