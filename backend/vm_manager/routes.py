from .VmException import VmException
from fastapi import APIRouter, Depends, HTTPException
from auth_manager.auth import check_auth
from db.database import get_session
from sqlmodel import select
from .vmbasic import VirtualMachineBasic, VirtualMachineBasicTemplate, OvmfPath, VirtualMachineXmlTemplate, VirtualMachineDeviceDiskFile, VirtualMachineDeviceNetwork, VirtualMachineDeviceDiskBlock, VirtualMachineDeviceDiskIscsi, VirtualMachineDevicePci
from .network import (
    LibvirtNetworkBridge,
    LibvirtNetworkBridgeResponse,
    LibvirtNetworkCustom,
    LibvirtNetworkCustomResponse,
    get_network_bridge,
    get_network_bridge_all,
    update_network_bridge,
    delete_network_bridge,
    create_network_bridge,
    get_network_custom,
    get_network_custom_all,
    update_network_custom,
    delete_network_custom,
    create_network_custom,
)
from .vm_service import VmService
from pydantic import BaseModel, ConfigDict
from typing import Any

router = APIRouter()

class VirtualMachineResponse(BaseModel):
    """Response model for VM with computed status field"""
    model_config = ConfigDict(from_attributes=True)
    id: int | None
    name: str
    status: str | None = None
    autostart: bool
    cpu_model: str
    vcpu: int
    vcpu_current: int
    vcpu_custom_topology: bool
    vcpu_custom_topology_sockets: int | None
    vcpu_custom_topology_dies: int | None
    vcpu_custom_topology_cores: int | None
    vcpu_custom_topology_threads: int | None
    machine_type: str
    bios_type: str
    ovmf_path_id: int | None
    memory_min: int
    memory_max: int
    video_type: str
    xml_template_id: int | None
    devices_pci: list[dict[str, Any]] = []
    devices_disk_file: list[dict[str, Any]] = []
    devices_disk_block: list[dict[str, Any]] = []
    devices_disk_iscsi: list[dict[str, Any]] = []
    devices_network: list[dict[str, Any]] = []

class VirtualMachineDevicePciRequest(BaseModel):
    """Request model for PCI device"""
    id: int | None = None
    vm_id: int | None = None
    pci_address: str

class VirtualMachineDeviceDiskFileRequest(BaseModel):
    """Request model for file-based disk device"""
    id: int | None = None
    vm_id: int | None = None
    device_type: str
    name: str
    disk_bus: str
    disk_source_file: str

class VirtualMachineDeviceDiskBlockRequest(BaseModel):
    """Request model for block-based disk device"""
    id: int | None = None
    vm_id: int | None = None
    device_type: str
    name: str
    disk_bus: str
    disk_source_dev: str

class VirtualMachineDeviceDiskIscsiRequest(BaseModel):
    """Request model for iSCSI disk device"""
    id: int | None = None
    vm_id: int | None = None
    device_type: str
    name: str
    disk_bus: str
    iscsi_host: str
    iscsi_name: str
    iscsi_port: int

class VirtualMachineDeviceNetworkRequest(BaseModel):
    """Request model for network device"""
    id: int | None = None
    vm_id: int | None = None
    name: str
    type: str
    libvirt_name: str
    mac: str | None = None

class VirtualMachineUpdateRequest(BaseModel):
    """Request model for updating a VM"""
    name: str
    autostart: bool
    cpu_model: str
    vcpu: int
    vcpu_current: int
    vcpu_custom_topology: bool
    vcpu_custom_topology_sockets: int | None
    vcpu_custom_topology_dies: int | None
    vcpu_custom_topology_cores: int | None
    vcpu_custom_topology_threads: int | None
    machine_type: str
    bios_type: str
    ovmf_path_id: int | None
    memory_min: int
    memory_max: int
    video_type: str
    xml_template_id: int | None
    devices_pci: list[VirtualMachineDevicePciRequest] = []
    devices_disk_file: list[VirtualMachineDeviceDiskFileRequest] = []
    devices_disk_block: list[VirtualMachineDeviceDiskBlockRequest] = []
    devices_disk_iscsi: list[VirtualMachineDeviceDiskIscsiRequest] = []
    devices_network: list[VirtualMachineDeviceNetworkRequest] = []

def add_vm_status(vm: VirtualMachineBasic) -> VirtualMachineResponse:
    """Add computed status field to VM"""
    vm_service = VmService(vm)
    return VirtualMachineResponse(
        id=vm.id,
        name=vm.name,
        status=vm_service.get_status(),
        autostart=vm.autostart,
        cpu_model=vm.cpu_model,
        vcpu=vm.vcpu,
        vcpu_current=vm.vcpu_current,
        vcpu_custom_topology=vm.vcpu_custom_topology,
        vcpu_custom_topology_sockets=vm.vcpu_custom_topology_sockets,
        vcpu_custom_topology_dies=vm.vcpu_custom_topology_dies,
        vcpu_custom_topology_cores=vm.vcpu_custom_topology_cores,
        vcpu_custom_topology_threads=vm.vcpu_custom_topology_threads,
        machine_type=vm.machine_type,
        bios_type=vm.bios_type,
        ovmf_path_id=vm.ovmf_path_id,
        memory_min=vm.memory_min,
        memory_max=vm.memory_max,
        video_type=vm.video_type,
        xml_template_id=vm.xml_template_id,
        devices_pci=[device.model_dump() for device in vm.devices_pci],
        devices_disk_file=[device.model_dump() for device in vm.devices_disk_file],
        devices_disk_block=[device.model_dump() for device in vm.devices_disk_block],
        devices_disk_iscsi=[device.model_dump() for device in vm.devices_disk_iscsi],
        devices_network=[device.model_dump() for device in vm.devices_network],
    )

"""/api/vm"""

@router.get("/templates/basic", response_model=list[VirtualMachineBasicTemplate])
async def api_vm_templates_get(username: str = Depends(check_auth)):
    with get_session() as session:
        return session.exec(select(VirtualMachineBasicTemplate)).all()
    
@router.get("/templates/basic/{template_id}", response_model=VirtualMachineBasicTemplate)
async def api_vm_template_get(template_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        template = session.exec(select(VirtualMachineBasicTemplate).where(VirtualMachineBasicTemplate.id == template_id)).first()
        if template is None:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    
@router.get("/templates/xml", response_model=list[VirtualMachineXmlTemplate])
async def api_vm_xml_templates_get(username: str = Depends(check_auth)):
    with get_session() as session:
        return session.exec(select(VirtualMachineXmlTemplate)).all()
    
@router.get("/templates/xml/{xml_template_id}", response_model=VirtualMachineXmlTemplate)
async def api_vm_xml_template_get(xml_template_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        xml_template = session.exec(select(VirtualMachineXmlTemplate).where(VirtualMachineXmlTemplate.id == xml_template_id)).first()
        if xml_template is None:
            raise HTTPException(status_code=404, detail="XML Template not found")
        return xml_template

@router.get("/network/bridge", response_model=list[LibvirtNetworkBridgeResponse])
async def api_vm_network_bridges_get(username: str = Depends(check_auth)):
    return get_network_bridge_all()

@router.get("/network/bridge/{bridge_id}", response_model=LibvirtNetworkBridgeResponse)
async def api_vm_network_bridge_get(bridge_id: int, username: str = Depends(check_auth)):
    bridge = get_network_bridge(bridge_id)
    if bridge is None:
        raise HTTPException(status_code=404, detail="Network bridge not found")
    return bridge

@router.put("/network/bridge/{bridge_id}", response_model=LibvirtNetworkBridge)
async def api_vm_network_bridge_update(bridge_id: int, bridge_update: LibvirtNetworkBridge, username: str = Depends(check_auth)):
    bridge = update_network_bridge(bridge_id, bridge_update)
    if bridge is None:
        raise HTTPException(status_code=404, detail="Network bridge not found")
    return bridge


@router.post("/network/bridge", response_model=LibvirtNetworkBridge)
async def api_vm_network_bridge_create(bridge: LibvirtNetworkBridge, username: str = Depends(check_auth)):
    try:
        created = create_network_bridge(bridge)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return created

@router.delete("/network/bridge/{bridge_id}")
async def api_vm_network_bridge_delete(bridge_id: int, username: str = Depends(check_auth)):
    success = delete_network_bridge(bridge_id)
    if not success:
        raise HTTPException(status_code=404, detail="Network bridge not found")
    return

@router.get("/network/custom", response_model=list[LibvirtNetworkCustomResponse])
async def api_vm_network_customs_get(username: str = Depends(check_auth)):
    return get_network_custom_all()

@router.get("/network/custom/{custom_id}", response_model=LibvirtNetworkCustomResponse)
async def api_vm_network_custom_get(custom_id: int, username: str = Depends(check_auth
)):
    custom = get_network_custom(custom_id)
    if custom is None:
        raise HTTPException(status_code=404, detail="Custom network not found")
    return custom

@router.put("/network/custom/{custom_id}", response_model=LibvirtNetworkCustom)
async def api_vm_network_custom_update(custom_id: int, custom_update: LibvirtNetworkCustom, username: str = Depends(check_auth)):
    custom = update_network_custom(custom_id, custom_update)
    if custom is None:
        raise HTTPException(status_code=404, detail="Custom network not found")
    return custom

@router.delete("/network/custom/{custom_id}")
async def api_vm_network_custom_delete(custom_id: int, username: str = Depends(check_auth)):
    success = delete_network_custom(custom_id)
    if not success:
         raise HTTPException(status_code=404, detail="Custom network not found")
    return


@router.post("/network/custom", response_model=LibvirtNetworkCustom)
async def api_vm_network_custom_create(custom: LibvirtNetworkCustom, username: str = Depends(check_auth)):
    try:
        created = create_network_custom(custom)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return created

@router.get("/", response_model=list[VirtualMachineResponse])
async def api_vm_get(username: str = Depends(check_auth)):
    with get_session() as session:
        vms = session.exec(select(VirtualMachineBasic)).all()
        return [add_vm_status(vm) for vm in vms]

@router.get("/{vm_id}", response_model=VirtualMachineResponse)
async def api_vm_get_id(vm_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        return add_vm_status(vm)
    
@router.delete("/{vm_id}")
async def api_vm_delete(vm_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        try:
            vm_service = VmService(vm)
            vm_service.remove()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        session.delete(vm)
        session.commit()

@router.put("/{vm_id}", response_model=VirtualMachineResponse)
async def api_vm_update(vm_id: int, vm_update: VirtualMachineUpdateRequest, username: str = Depends(check_auth)):
    with get_session() as session:
        old_vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if old_vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        
        # Update basic VM properties
        old_vm.name = vm_update.name
        old_vm.autostart = vm_update.autostart
        old_vm.cpu_model = vm_update.cpu_model
        old_vm.vcpu = vm_update.vcpu
        old_vm.vcpu_current = vm_update.vcpu_current
        old_vm.vcpu_custom_topology = vm_update.vcpu_custom_topology
        old_vm.vcpu_custom_topology_sockets = vm_update.vcpu_custom_topology_sockets
        old_vm.vcpu_custom_topology_dies = vm_update.vcpu_custom_topology_dies
        old_vm.vcpu_custom_topology_cores = vm_update.vcpu_custom_topology_cores
        old_vm.vcpu_custom_topology_threads = vm_update.vcpu_custom_topology_threads
        old_vm.memory_min = vm_update.memory_min
        old_vm.memory_max = vm_update.memory_max
        old_vm.video_type = vm_update.video_type
        
        # Update devices - delete old ones and add new ones
        # Delete existing devices
        for device in old_vm.devices_pci:
            session.delete(device)
        for device in old_vm.devices_disk_file:
            session.delete(device)
        for device in old_vm.devices_disk_block:
            session.delete(device)
        for device in old_vm.devices_disk_iscsi:
            session.delete(device)
        for device in old_vm.devices_network:
            session.delete(device)
        
        # Add new devices from request
        for device_data in vm_update.devices_pci:
            device = VirtualMachineDevicePci(
                vm_id=old_vm.id,
                pci_address=device_data.pci_address
            )
            session.add(device)
        
        for device_data in vm_update.devices_disk_file:
            device = VirtualMachineDeviceDiskFile(
                vm_id=old_vm.id,
                device_type=device_data.device_type,
                name=device_data.name,
                disk_bus=device_data.disk_bus,
                disk_source_file=device_data.disk_source_file
            )
            session.add(device)
        
        for device_data in vm_update.devices_disk_block:
            device = VirtualMachineDeviceDiskBlock(
                vm_id=old_vm.id,
                device_type=device_data.device_type,
                name=device_data.name,
                disk_bus=device_data.disk_bus,
                disk_source_dev=device_data.disk_source_dev
            )
            session.add(device)
        
        for device_data in vm_update.devices_disk_iscsi:
            device = VirtualMachineDeviceDiskIscsi(
                vm_id=old_vm.id,
                device_type=device_data.device_type,
                name=device_data.name,
                disk_bus=device_data.disk_bus,
                iscsi_host=device_data.iscsi_host,
                iscsi_name=device_data.iscsi_name,
                iscsi_port=device_data.iscsi_port
            )
            session.add(device)
        
        for device_data in vm_update.devices_network:
            device = VirtualMachineDeviceNetwork(
                vm_id=old_vm.id,
                name=device_data.name,
                type=device_data.type,
                libvirt_name=device_data.libvirt_name,
                mac=device_data.mac
            )
            session.add(device)
        
        session.commit()
        session.refresh(old_vm)
        return add_vm_status(old_vm)

@router.post("/{vm_id}/start")
async def api_vm_start(vm_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        print(f"Starting VM {vm_id}")
        try:
            vm_service = VmService(vm)
            vm_service.start()
        except VmException as e:
            raise HTTPException(status_code=500, detail=str(e))
        return
    
@router.post("/{vm_id}/shutdown")
async def api_vm_shutdown(vm_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        print(f"Shutting down VM {vm_id}")
        vm_service = VmService(vm)
        vm_service.shutdown()
        return
    
@router.post("/{vm_id}/forcestop")
async def api_vm_forcestop(vm_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        print(f"Force stopping VM {vm_id}")
        vm_service = VmService(vm)
        vm_service.forcestop()
        return
    
@router.post("/{vm_id}/reset")
async def api_vm_reset(vm_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        print(f"Resetting VM {vm_id}")
        vm_service = VmService(vm)
        vm_service.reset()
        return
