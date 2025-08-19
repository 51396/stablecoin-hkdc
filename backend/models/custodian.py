
from sqlalchemy.orm import Session
from ..schemas.custodian import CustodianCreate,ReserveAssetAccountCreate
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, joinedload # <-- 确保导入了 relationship
from .base import Base
from datetime import datetime
from typing import Optional,List
class CustodianDB(Base):
    __tablename__ = "custodians"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    custodian_type = Column(String, nullable=False)
    account_address = Column(String)
    
    accounts = relationship("ReserveAssetAccountDB", back_populates="custodian")

class ReserveAssetAccountDB(Base):
    __tablename__ = "reserve_asset_accounts"
    id = Column(Integer, primary_key=True, index=True)
    custodian_id = Column(Integer, ForeignKey("custodians.id"), nullable=False)
    name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)
    currency = Column(String, default="USD")
    balance = Column(Float, nullable=False)
    
    custodian = relationship("CustodianDB", back_populates="accounts")
def create_custodian(db: Session, custodian: CustodianCreate):
    db_custodian = CustodianDB(**custodian.model_dump())
    db.add(db_custodian)
    db.commit()
    db.refresh(db_custodian)
    return db_custodian

def get_custodians(db: Session, skip: int = 0, limit: int = 100, search: str = ""):
    query = db.query(CustodianDB)
    if search:
        query = query.filter(CustodianDB.name.contains(search))
    return query.offset(skip).limit(limit).all()


def get_custodian_by_id(db: Session, custodian_id: int):
    """辅助函数：根据ID查找托管机构"""
    return db.query(CustodianDB).filter(CustodianDB.id == custodian_id).first()
def get_account_by_name_and_custodian(db: Session, name: str, custodian_id: int):
    """检查在同一机构下是否存在同名账户"""
    return db.query(ReserveAssetAccountDB).filter(
        ReserveAssetAccountDB.name == name,
        ReserveAssetAccountDB.custodian_id == custodian_id
    ).first()

def create_asset_account(db: Session, account: ReserveAssetAccountCreate):
    # 1. 验证托管机构是否存在
    db_custodian = get_custodian_by_id(db, custodian_id=account.custodian_id)
    if not db_custodian:
        raise ValueError(f"ID为 {account.custodian_id} 的托管机构不存在")

    # 2. 验证账户名是否重复
    db_account = get_account_by_name_and_custodian(db, name=account.name, custodian_id=account.custodian_id)
    if db_account:
        raise ValueError(f"在 {db_custodian.name} 下已存在名为 '{account.name}' 的账户")

    # 3. 创建并存入数据库
    db_account_obj = ReserveAssetAccountDB(**account.model_dump())
    db.add(db_account_obj)
    db.commit()
    db.refresh(db_account_obj)
    return db_account_obj

def get_accounts(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    custodian_id: Optional[int] = None, 
    asset_type: Optional[str] = None,
    search: Optional[str] = None
) -> (List[ReserveAssetAccountDB], int):
    """
    获取资产账户列表（支持分页和筛选）
    返回: (账户列表, 总数)
    """
    query = db.query(ReserveAssetAccountDB).options(joinedload(ReserveAssetAccountDB.custodian))

    # 应用筛选条件
    if custodian_id:
        query = query.filter(ReserveAssetAccountDB.custodian_id == custodian_id)
    if asset_type:
        query = query.filter(ReserveAssetAccountDB.asset_type == asset_type)
    if search:
        query = query.filter(ReserveAssetAccountDB.name.contains(search))

    # 首先获取筛选后的总数，用于分页
    total = query.count()

    # 然后应用排序和分页
    accounts = query.order_by(ReserveAssetAccountDB.id.desc()).offset(skip).limit(limit).all()
    
    return accounts, total

def get_account_details(db: Session, account_id: int) -> Optional[ReserveAssetAccountDB]:
    """
    获取单个账户的详细信息，并预加载其所有交易记录
    """
    return db.query(ReserveAssetAccountDB).options(
        joinedload(ReserveAssetAccountDB.custodian),
        joinedload(ReserveAssetAccountDB.transactions) # 预加载交易记录
    ).filter(ReserveAssetAccountDB.id == account_id).first()