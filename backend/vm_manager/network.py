from sqlmodel import Field, SQLModel, select
from pydantic import BaseModel, ConfigDict
from db import get_session
import libvirt
from host_manager import libvirt_connection


class LibvirtNetworkBridge(SQLModel, table=True):
    __tablename__ = "libvirtnetworkbridge"
    id: int | None = Field(primary_key=True)
    name: str = Field(nullable=False, unique=True)
    bridge_name: str = Field(nullable=False, unique=True)
    description: str = Field(nullable=True)
    autostart: bool = Field(default=False)


class LibvirtNetworkBridgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    bridge_name: str
    description: str | None
    autostart: bool
    active: bool


class LibvirtNetworkBridgeApplyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    checked: int
    removed: int
    defined: int
    started: int
    errors: list[str]

class LibvirtNetworkCustom(SQLModel, table=True):
    __tablename__ = "libvirtnetworkcustom"
    id: int | None = Field(primary_key=True)
    name: str = Field(nullable=False, unique=True)
    xml_content: str = Field(nullable=False)
    description: str = Field(nullable=True)
    autostart: bool = Field(default=False)


class LibvirtNetworkCustomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    xml_content: str
    description: str | None
    autostart: bool
    active: bool


def get_network_bridge(id: int) -> LibvirtNetworkBridgeResponse | None:
    with get_session() as session:
        statement = select(LibvirtNetworkBridge).where(LibvirtNetworkBridge.id == id)
        result = session.exec(statement).first()
        if result:
            # Check if active in libvirt using shared connection
            try:
                conn = libvirt_connection.connection
                network = conn.networkLookupByName(result.name)
                active = network.isActive() == 1
            except libvirt.libvirtError:
                active = False
            return LibvirtNetworkBridgeResponse(
                id=result.id,
                name=result.name,
                bridge_name=result.bridge_name,
                description=result.description,
                autostart=result.autostart,
                active=active
            )
    return None


def get_network_bridge_all() -> list[LibvirtNetworkBridgeResponse]:
    bridges: list[LibvirtNetworkBridgeResponse] = []
    # use get_network_bridge to get all bridges
    with get_session() as session:
        statement = select(LibvirtNetworkBridge)
        results = session.exec(statement).all()
        for result in results:
            bridge = get_network_bridge(result.id)
            if bridge:
                bridges.append(bridge)
    return bridges


def update_network_bridge(bridge_id: int, bridge_update: LibvirtNetworkBridge) -> LibvirtNetworkBridge | None:
    """Update existing LibvirtNetworkBridge by id using values from bridge_update."""
    with get_session() as session:
        statement = select(LibvirtNetworkBridge).where(LibvirtNetworkBridge.id == bridge_id)
        result = session.exec(statement).first()
        if result:
            result.name = bridge_update.name
            result.bridge_name = bridge_update.bridge_name
            result.description = bridge_update.description
            result.autostart = bridge_update.autostart
            session.add(result)
            session.commit()
            session.refresh(result)
            return result
    return None


def create_network_bridge(bridge: LibvirtNetworkBridge) -> LibvirtNetworkBridge:
    """Create a new LibvirtNetworkBridge and return the created record."""
    with get_session() as session:
        new_bridge = LibvirtNetworkBridge(
            name=bridge.name,
            bridge_name=bridge.bridge_name,
            description=bridge.description,
            autostart=bridge.autostart,
        )
        session.add(new_bridge)
        session.commit()
        session.refresh(new_bridge)
        return new_bridge


def delete_network_bridge(id: int) -> bool:
    with get_session() as session:
        statement = select(LibvirtNetworkBridge).where(LibvirtNetworkBridge.id == id)
        result = session.exec(statement).first()
        if result:
            session.delete(result)
            session.commit()
            return True
    return False


def get_network_custom(id: int) -> LibvirtNetworkCustomResponse | None:
    with get_session() as session:
        statement = select(LibvirtNetworkCustom).where(LibvirtNetworkCustom.id == id)
        result = session.exec(statement).first()
        if result:
            # Check if active in libvirt using shared connection
            try:
                conn = libvirt_connection.connection
                network = conn.networkLookupByName(result.name)
                active = network.isActive() == 1
            except libvirt.libvirtError:
                active = False
            return LibvirtNetworkCustomResponse(
                id=result.id,
                name=result.name,
                xml_content=result.xml_content,
                description=result.description,
                autostart=result.autostart,
                active=active
            )
    return None


def get_network_custom_all() -> list[LibvirtNetworkCustomResponse]:
    customs: list[LibvirtNetworkCustomResponse] = []
    # use get_network_custom to get all customs
    with get_session() as session:
        statement = select(LibvirtNetworkCustom)
        results = session.exec(statement).all()
        for result in results:
            custom = get_network_custom(result.id)
            if custom:
                customs.append(custom)
    return customs


def update_network_custom(custom_id: int, custom_update: LibvirtNetworkCustom) -> LibvirtNetworkCustom | None:
    """Update existing LibvirtNetworkCustom by id using values from custom_update."""
    with get_session() as session:
        statement = select(LibvirtNetworkCustom).where(LibvirtNetworkCustom.id == custom_id)
        result = session.exec(statement).first()
        if result:
            result.name = custom_update.name
            result.xml_content = custom_update.xml_content
            result.description = custom_update.description
            result.autostart = custom_update.autostart
            session.add(result)
            session.commit()
            session.refresh(result)
            return result
    return None


def create_network_custom(custom: LibvirtNetworkCustom) -> LibvirtNetworkCustom:
    """Create a new LibvirtNetworkCustom and return the created record."""
    with get_session() as session:
        new_custom = LibvirtNetworkCustom(
            name=custom.name,
            xml_content=custom.xml_content,
            description=custom.description,
            autostart=custom.autostart,
        )
        session.add(new_custom)
        session.commit()
        session.refresh(new_custom)
        return new_custom


def delete_network_custom(id: int) -> bool:
    with get_session() as session:
        statement = select(LibvirtNetworkCustom).where(LibvirtNetworkCustom.id == id)
        result = session.exec(statement).first()
        if result:
            session.delete(result)
            session.commit()
            return True
    return False


def apply_network_bridges() -> LibvirtNetworkBridgeApplyResponse:
    """Apply network bridge settings from the database to libvirt.

    For every bridge entry in the database:
    - If a libvirt network with the same name exists, destroy and undefine it.
    - Define a new network XML for the bridge and register it with libvirt.
    - If the DB entry has `autostart=True`, set autostart and start the network.

    Returns a summary dict with counts and any errors encountered.
    """
    summary = {
        "checked": 0,
        "removed": 0,
        "defined": 0,
        "started": 0,
        "errors": [],
    }

    try:
        conn = libvirt_connection.connection
    except Exception as e:
        summary["errors"].append(f"failed-to-get-libvirt-connection:{e}")
        return summary

    with get_session() as session:
            stmt = select(LibvirtNetworkBridge)
            bridges = session.exec(stmt).all()
            for b in bridges:
                summary["checked"] += 1
                # Remove existing definition if present
                try:
                    try:
                        existing = conn.networkLookupByName(b.name)
                    except libvirt.libvirtError:
                        existing = None

                    if existing is not None:
                        try:
                            if existing.isActive() == 1:
                                existing.destroy()
                        except libvirt.libvirtError as e:
                            # record but continue
                            summary["errors"].append(f"destroy:{b.name}:{e}")
                        try:
                            existing.undefine()
                            summary["removed"] += 1
                        except libvirt.libvirtError as e:
                            summary["errors"].append(f"undefine:{b.name}:{e}")

                    # Build network XML for a bridged network
                    xml = (
                        f"<network>"
                        f"<name>{b.name}</name>"
                        f"<forward mode='bridge'/>"
                        f"<bridge name='{b.bridge_name}'/>"
                        f"</network>"
                    )

                    try:
                        net = conn.networkDefineXML(xml)
                        if net is None:
                            summary["errors"].append(f"define-failed:{b.name}")
                        else:
                            summary["defined"] += 1
                            # Set autostart and start if requested
                            if b.autostart:
                                try:
                                    net.setAutostart(1)
                                except libvirt.libvirtError as e:
                                    summary["errors"].append(f"set-autostart:{b.name}:{e}")
                                try:
                                    if net.isActive() != 1:
                                        net.create()
                                    summary["started"] += 1
                                except libvirt.libvirtError as e:
                                    summary["errors"].append(f"start:{b.name}:{e}")
                    except libvirt.libvirtError as e:
                        summary["errors"].append(f"defineXML:{b.name}:{e}")

                except Exception as e:
                    # Catch-all per-bridge to avoid aborting the whole operation
                    summary["errors"].append(f"unexpected:{b.name}:{e}")
                    continue
    return LibvirtNetworkBridgeApplyResponse(
        checked=summary["checked"],
        removed=summary["removed"],
        defined=summary["defined"],
        started=summary["started"],
        errors=summary["errors"],
    )
