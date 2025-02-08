from .VmException import VmException
from fastapi import APIRouter, Depends, HTTPException
from auth_manager.auth import check_auth
from db.database import get_session
from sqlmodel import select
from .vmbasic import VirtualMachineBasic, VirtualMachineBasicTemplate, OvmfPath, VirtualMachineBasicLibvirtConfig, VirtualMachineXmlTemplate, VirtualMachineDeviceDiskFile, VirtualMachineDeviceNetwork, VirtualMachineDeviceDiskBlock, get_vm_networks

router = APIRouter()

"""/api/vm"""

@router.get("/templates")
async def api_vm_templates_get(username: str = Depends(check_auth)):
    with get_session() as session:
        return session.exec(select(VirtualMachineBasicTemplate)).all()
    
@router.get("/templates/{template_id}")
async def api_vm_template_get(template_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        template = session.exec(select(VirtualMachineBasicTemplate).where(VirtualMachineBasicTemplate.id == template_id)).first()
        if template is None:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    
@router.get("/xml_templates")
async def api_vm_xml_templates_get(username: str = Depends(check_auth)):
    with get_session() as session:
        return session.exec(select(VirtualMachineXmlTemplate)).all()
    
@router.get("/xml_templates/{xml_template_id}")
async def api_vm_xml_template_get(xml_template_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        xml_template = session.exec(select(VirtualMachineXmlTemplate).where(VirtualMachineXmlTemplate.id == xml_template_id)).first()
        if xml_template is None:
            raise HTTPException(status_code=404, detail="XML Template not found")
        return xml_template

@router.get("/networks")
async def api_vm_networks_get(username: str = Depends(check_auth)):
    return get_vm_networks()

@router.get("/")
async def api_vm_get(username: str = Depends(check_auth)):
    with get_session() as session:
        vms = session.exec(select(VirtualMachineBasic)).all()
    
        vms = [VirtualMachineBasicLibvirtConfig(vm).to_dict() for vm in vms]
        return vms

@router.get("/{vm_id}")
async def api_vm_get_id(vm_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        return VirtualMachineBasicLibvirtConfig(vm).to_dict()
    
@router.delete("/{vm_id}")
async def api_vm_delete(vm_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        try:
            VirtualMachineBasicLibvirtConfig(vm).remove()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        session.delete(vm)
        session.commit()

@router.put("/{vm_id}")
async def api_vm_update(vm_id: int, vm: VirtualMachineBasic, username: str = Depends(check_auth)):
    with get_session() as session:
        old_vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if old_vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        old_vm.name = vm.name
        old_vm.autostart = vm.autostart
        old_vm.cpu_model = vm.cpu_model
        old_vm.vcpu = vm.vcpu
        old_vm.vcpu_current = vm.vcpu_current
        old_vm.vcpu_custom_topology = vm.vcpu_custom_topology
        old_vm.vcpu_custom_topology_sockets = vm.vcpu_custom_topology_sockets
        old_vm.vcpu_custom_topology_dies = vm.vcpu_custom_topology_dies
        old_vm.vcpu_custom_topology_cores = vm.vcpu_custom_topology_cores
        old_vm.vcpu_custom_topology_threads = vm.vcpu_custom_topology_threads
        old_vm.memory_min = vm.memory_min
        old_vm.memory_max = vm.memory_max
        old_vm.video_type = vm.video_type
        session.commit()
        return

@router.post("/{vm_id}/start")
async def api_vm_start(vm_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        print(f"Starting VM {vm_id}")
        try:
            VirtualMachineBasicLibvirtConfig(vm).start()
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
        VirtualMachineBasicLibvirtConfig(vm).shutdown()
        return
    
@router.post("/{vm_id}/forcestop")
async def api_vm_forcestop(vm_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        print(f"Force stopping VM {vm_id}")
        VirtualMachineBasicLibvirtConfig(vm).forcestop()
        return
    
@router.post("/{vm_id}/reset")
async def api_vm_reset(vm_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        print(f"Resetting VM {vm_id}")
        VirtualMachineBasicLibvirtConfig(vm).reset()
        return
    
@router.delete("/{vm_id}/devices/network/{device_id}")
async def api_vm_delete_device_network(vm_id: int, device_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        network_device = session.exec(select(VirtualMachineDeviceNetwork).where(VirtualMachineDeviceNetwork.id == device_id)).first()
        if network_device is None:
            raise HTTPException(status_code=404, detail="Network device not found")
        session.delete(network_device)
        session.commit()

@router.post("/{vm_id}/devices/network")
async def api_vm_add_device_network(vm_id: int, device: VirtualMachineDeviceNetwork, username: str = Depends(check_auth)):
    print(f"Adding network device {device}")
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        device.vm = vm
        session.add(device)
        session.commit()
        return device
    return

@router.delete("/{vm_id}/devices/disk-file/{device_id}")
async def api_vm_delete_device_disk_file(vm_id: int, device_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        disk_device_file = session.exec(select(VirtualMachineDeviceDiskFile).where(VirtualMachineDeviceDiskFile.id == device_id)).first()
        if disk_device_file is None:
            raise HTTPException(status_code=404, detail="Disk device not found")
        session.delete(disk_device_file)
        session.commit()

@router.post("/{vm_id}/devices/disk-file")
async def api_vm_add_device_disk_file(vm_id: int, device: VirtualMachineDeviceDiskFile, username: str = Depends(check_auth)):
    print(f"Adding disk device {device}")
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        device.vm = vm
        session.add(device)
        session.commit()
        return device
    return

@router.delete("/{vm_id}/devices/disk-block/{device_id}")
async def api_vm_delete_device_disk_block(vm_id: int, device_id: int, username: str = Depends(check_auth)):
    with get_session() as session:
        disk_device_block = session.exec(select(VirtualMachineDeviceDiskBlock).where(VirtualMachineDeviceDiskBlock.id == device_id)).first()
        if disk_device_block is None:
            raise HTTPException(status_code=404, detail="Disk device not found")
        session.delete(disk_device_block)
        session.commit()

@router.post("/{vm_id}/devices/disk-block")
async def api_vm_add_device_disk_block(vm_id: int, device: VirtualMachineDeviceDiskBlock, username: str = Depends(check_auth)):
    print(f"Adding disk device {device}")
    with get_session() as session:
        vm = session.exec(select(VirtualMachineBasic).where(VirtualMachineBasic.id == vm_id)).first()
        if vm is None:
            raise HTTPException(status_code=404, detail="VM not found")
        device.vm = vm
        session.add(device)
        session.commit()
        return device
    return
