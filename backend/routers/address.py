from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_db
from ..models import Address, User
from ..services.address_service import (
    create_address, get_address_by_address, get_address_by_id, get_all_addresses,
    update_address, delete_address, get_whitelisted_addresses, get_blacklisted_addresses,
    is_address_whitelisted, is_address_blacklisted, get_addresses_by_label
)
from ..core.security import get_current_user

class AddressCreate(BaseModel):
    address: str
    label: Optional[str] = None
    is_whitelisted: bool = False
    is_blacklisted: bool = False

class AddressUpdate(BaseModel):
    label: Optional[str] = None
    is_whitelisted: Optional[bool] = None
    is_blacklisted: Optional[bool] = None

router = APIRouter(prefix="/addresses", tags=["地址管理"])

@router.post("/", summary="创建地址记录")
def create_address_endpoint(
    address_data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    address = address_data.address
    label = address_data.label
    is_whitelisted = address_data.is_whitelisted
    is_blacklisted = address_data.is_blacklisted
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 检查地址是否已存在
    existing_address = get_address_by_address(db, address)
    if existing_address:
        raise HTTPException(status_code=400, detail="地址已存在")
    
    try:
        return create_address(db, address, label, is_whitelisted, is_blacklisted)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/whitelist", summary="获取白名单地址")
def get_whitelisted_addresses_endpoint(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    return get_whitelisted_addresses(db, skip, limit)

@router.get("/blacklist", summary="获取黑名单地址")
def get_blacklisted_addresses_endpoint(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    return get_blacklisted_addresses(db, skip, limit)
@router.get("/{address_id}", summary="根据ID获取地址记录")
def get_address_by_id_endpoint(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    db_address = get_address_by_id(db, address_id)
    if not db_address:
        raise HTTPException(status_code=404, detail="地址不存在")
    
    return db_address

@router.get("/", summary="获取所有地址记录")
def get_all_addresses_endpoint(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    return get_all_addresses(db, skip, limit)

@router.put("/{address_id}", summary="更新地址记录")
def update_address_endpoint(
    address_id: int,
    address_data: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    label = address_data.label
    is_whitelisted = address_data.is_whitelisted
    is_blacklisted = address_data.is_blacklisted
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    db_address = get_address_by_id(db, address_id)
    if not db_address:
        raise HTTPException(status_code=404, detail="地址不存在")
    
    try:
        return update_address(db, address_id, label, is_whitelisted, is_blacklisted)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{address_id}", summary="删除地址记录")
def delete_address_endpoint(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    db_address = get_address_by_id(db, address_id)
    if not db_address:
        raise HTTPException(status_code=404, detail="地址不存在")
    
    return delete_address(db, address_id)



@router.get("/check/{address}", summary="检查地址状态")
def check_address_status_endpoint(
    address: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    is_whitelisted = is_address_whitelisted(db, address)
    is_blacklisted = is_address_blacklisted(db, address)
    
    return {
        "address": address,
        "is_whitelisted": is_whitelisted,
        "is_blacklisted": is_blacklisted
    }

@router.get("/label/{label}", summary="根据标签获取地址")
def get_addresses_by_label_endpoint(
    label: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    return get_addresses_by_label(db, label, skip, limit)