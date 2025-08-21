from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from ..models.institutional_account import InstitutionalAccountDB, InstitutionalAddressDB
from ..schemas.institutional_account import InstitutionalAccountCreate, InstitutionalAccountUpdate, InstitutionalAddressCreate
from typing import List, Optional

def get_account_by_id(db: Session, account_id: int):
    return db.query(InstitutionalAccountDB).filter(InstitutionalAccountDB.id == account_id).first()

def get_account_by_name(db: Session, name: str):
    return db.query(InstitutionalAccountDB).filter(InstitutionalAccountDB.name == name).first()

def get_address_by_address_str(db: Session, address: str):
    return db.query(InstitutionalAddressDB).filter(InstitutionalAddressDB.address == address).first()

def get_accounts(
    db: Session, skip: int, limit: int, search: str = ""
) -> (List[InstitutionalAccountDB], int):
    query = db.query(InstitutionalAccountDB).options(joinedload(InstitutionalAccountDB.addresses))
    
    if search:
        query = query.filter(InstitutionalAccountDB.name.contains(search))
        
    total = query.count()
    accounts = query.order_by(InstitutionalAccountDB.id.desc()).offset(skip).limit(limit).all()

    # 动态计算总余额
    for acc in accounts:
        acc.total_balance = sum(addr.balance for addr in acc.addresses)
        
    return accounts, total

def create_account(db: Session, account: InstitutionalAccountCreate) -> InstitutionalAccountDB:
    if get_account_by_name(db, account.name):
        raise ValueError(f"机构账户名 '{account.name}' 已存在")
    
    db_account = InstitutionalAccountDB(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def bind_address(db: Session, account_id: int, address: InstitutionalAddressCreate) -> InstitutionalAddressDB:
    if not get_account_by_id(db, account_id):
        raise ValueError("所属机构账户不存在")
    if get_address_by_address_str(db, address.address):
        raise ValueError(f"地址 '{address.address}' 已被其他账户绑定")

    db_address = InstitutionalAddressDB(**address.model_dump(), account_id=account_id)
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address