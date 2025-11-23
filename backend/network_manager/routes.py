from fastapi import APIRouter, Depends, HTTPException
from .interface import NetworkInterfaceEthernet, NetworkInterfaceBridge, edit_interface_ethernet, edit_interface_bridge, get_interface_ethernets, get_interface_bridges, apply
from auth_manager.auth import check_auth

router = APIRouter()

@router.get("/ethernets", response_model=list[NetworkInterfaceEthernet])
async def api_system_networks_get(username: str = Depends(check_auth)):
    try:
        ethernets = get_interface_ethernets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return ethernets

@router.get("/ethernets/{ethernet_id}", response_model=NetworkInterfaceEthernet)
async def api_system_ethernet_get(ethernet_id: str, username: str = Depends(check_auth)):
    try:
        ethernet = next((eth for eth in get_interface_ethernets() if eth.id == ethernet_id), None)
        if ethernet is None:
            raise HTTPException(status_code=404, detail="Ethernet interface not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return ethernet

@router.get("/bridges", response_model=list[NetworkInterfaceBridge])
async def api_system_bridges_get(username: str = Depends(check_auth)):
    try:
        bridges = get_interface_bridges()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return bridges

@router.get("/bridges/{bridge_id}", response_model=NetworkInterfaceBridge)
async def api_system_bridge_get(bridge_id: str, username: str = Depends(check_auth)):
    try:
        bridge = next((br for br in get_interface_bridges() if br.id == bridge_id), None)
        if bridge is None:
            raise HTTPException(status_code=404, detail="Bridge interface not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return bridge

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
