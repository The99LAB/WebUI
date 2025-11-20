from fastapi import APIRouter, Depends, HTTPException
from .interface import NetworkInterfaceEthernet, NetworkInterfaceBridge, edit_interface_ethernet, edit_interface_bridge, get_interface_ethernets, get_interface_bridges, apply
from auth_manager.auth import check_auth

router = APIRouter()

@router.get("/ethernets")
async def api_system_networks_get(username: str = Depends(check_auth)):
    try:
        ethernets = get_interface_ethernets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return ethernets

@router.get("/bridges")
async def api_system_bridges_get(username: str = Depends(check_auth)):
    try:
        bridges = get_interface_bridges()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return bridges

@router.put("/ethernets")
async def api_system_ethernets_put(interface: NetworkInterfaceEthernet, username: str = Depends(check_auth)):
    try:
        edit_interface_ethernet(interface)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "success"}

@router.put("/bridges")
async def api_system_bridges_put(interface: NetworkInterfaceBridge, username: str = Depends(check_auth)):
    try:
        edit_interface_bridge(interface)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "success"}

@router.post("/apply")
async def api_system_apply_post(username: str = Depends(check_auth)):
    try:
        apply()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "success"}
