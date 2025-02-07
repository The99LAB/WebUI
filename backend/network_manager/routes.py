from fastapi import APIRouter, Depends, HTTPException
from .interface import NetworkInterface, get_interfaces, edit_interface
from auth_manager.auth import check_auth

router = APIRouter()

@router.get("/")
async def api_system_networks_get(username: str = Depends(check_auth)):
    return get_interfaces()

@router.put("/")
async def api_system_networks_put(interface: NetworkInterface, username: str = Depends(check_auth)):
    return edit_interface(interface)
