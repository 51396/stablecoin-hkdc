from sqlalchemy.orm import Session
from ..models import Address, PREDEFINED_LABELS
from typing import List, Optional
import re

def validate_ethereum_address(address: str) -> bool:
    """验证以太坊地址格式"""
    # 检查是否为有效的以太坊地址格式
    pattern = r'^0x[a-fA-F0-9]{40}$'
    return bool(re.match(pattern, address))

def create_address(db: Session, address: str, label: Optional[str] = None, is_whitelisted: bool = False, is_blacklisted: bool = False):
    """创建新地址记录"""
    # 验证地址格式
    if not validate_ethereum_address(address):
        raise ValueError("无效的以太坊地址格式")
    
    # 如果提供了标签，验证它是否在预定义标签列表中
    if label and label not in PREDEFINED_LABELS:
        raise ValueError(f"标签必须是预定义标签之一: {', '.join(PREDEFINED_LABELS)}")
    
    db_address = Address(
        address=address,
        label=label,
        is_whitelisted=is_whitelisted,
        is_blacklisted=is_blacklisted
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

def get_address_by_address(db: Session, address: str):
    """根据地址获取地址记录"""
    return db.query(Address).filter(Address.address == address).first()

def get_address_by_id(db: Session, address_id: int):
    """根据ID获取地址记录"""
    return db.query(Address).filter(Address.id == address_id).first()

def get_all_addresses(db: Session, skip: int = 0, limit: int = 100):
    """获取所有地址记录"""
    return db.query(Address).offset(skip).limit(limit).all()

def update_address(db: Session, address_id: int, label: Optional[str] = None, is_whitelisted: Optional[bool] = None, is_blacklisted: Optional[bool] = None):
    """更新地址记录"""
    db_address = get_address_by_id(db, address_id)
    if db_address:
        # 如果提供了标签，验证它是否在预定义标签列表中
        if label is not None and label not in PREDEFINED_LABELS:
            raise ValueError(f"标签必须是预定义标签之一: {', '.join(PREDEFINED_LABELS)}")
        
        if label is not None:
            db_address.label = label
        if is_whitelisted is not None:
            db_address.is_whitelisted = is_whitelisted
        if is_blacklisted is not None:
            db_address.is_blacklisted = is_blacklisted
        db_address.updated_at = db_address.__class__.updated_at.property.columns[0].default.arg
        db.commit()
        db.refresh(db_address)
    return db_address

def delete_address(db: Session, address_id: int):
    """删除地址记录"""
    db_address = get_address_by_id(db, address_id)
    if db_address:
        db.delete(db_address)
        db.commit()
    return db_address

def get_whitelisted_addresses(db: Session, skip: int = 0, limit: int = 100):
    """获取白名单地址"""
    return db.query(Address).filter(Address.is_whitelisted == True).offset(skip).limit(limit).all()

def get_blacklisted_addresses(db: Session, skip: int = 0, limit: int = 100):
    """获取黑名单地址"""
    return db.query(Address).filter(Address.is_blacklisted == True).offset(skip).limit(limit).all()

def is_address_whitelisted(db: Session, address: str):
    """检查地址是否在白名单中"""
    db_address = get_address_by_address(db, address)
    return db_address.is_whitelisted if db_address else False

def is_address_blacklisted(db: Session, address: str):
    """检查地址是否在黑名单中"""
    db_address = get_address_by_address(db, address)
    return db_address.is_blacklisted if db_address else False

def get_addresses_by_label(db: Session, label: str, skip: int = 0, limit: int = 100):
    """根据标签获取地址"""
    return db.query(Address).filter(Address.label == label).offset(skip).limit(limit).all()