from sqlalchemy.orm import Session, joinedload
from ..models.account import RetailAccountDB, RetailAddressDB
from ..schemas.account import RetailAccountCreate, RetailAccountUpdate
from typing import List, Optional
import uuid

def get_account_by_id(db: Session, account_id: int):
    return db.query(RetailAccountDB).filter(RetailAccountDB.id == account_id).first()

def get_account_by_username(db: Session, username: str):
    return db.query(RetailAccountDB).filter(RetailAccountDB.username == username).first()

def get_accounts(
    db: Session, skip: int, limit: int, search: str = "", status: str = ""
) -> (List[RetailAccountDB], int):
    query = db.query(RetailAccountDB).options(joinedload(RetailAccountDB.addresses))
    
    if search:
        query = query.filter(
            (RetailAccountDB.username.contains(search)) | 
            (RetailAccountDB.uid.contains(search))
        )
    if status:
        query = query.filter(RetailAccountDB.status == status)
        
    total = query.count()
    accounts = query.order_by(RetailAccountDB.id.desc()).offset(skip).limit(limit).all()
    return accounts, total

def create_account(db: Session, account: RetailAccountCreate) -> RetailAccountDB:
    if get_account_by_username(db, account.username):
        raise ValueError(f"用户名 '{account.username}' 已存在")

    # 生成一个唯一的UID
    uid = f"UID-{uuid.uuid4().hex[:8].upper()}"
    
    db_account = RetailAccountDB(
        **account.model_dump(),
        uid=uid
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def update_account(db: Session, account_id: int, account_update: RetailAccountUpdate) -> Optional[RetailAccountDB]:
    db_account = get_account_by_id(db, account_id)
    if not db_account:
        return None
    
    update_data = account_update.model_dump(exclude_unset=True)

    if "username" in update_data and update_data["username"] != db_account.username:
        if get_account_by_username(db, update_data["username"]):
            raise ValueError(f"用户名 '{update_data['username']}' 已被占用")

    for key, value in update_data.items():
        setattr(db_account, key, value)
        
    db.commit()
    db.refresh(db_account)
    return db_account