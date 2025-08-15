from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship # <-- 确保导入了 relationship
from .base import Base
from datetime import datetime
from ..schemas.reserve import TransactionTypeEnum,AssetTypeEnum

class ReserveAssetDB(Base):
    __tablename__ = "reserve_assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    asset_type = Column(SQLAlchemyEnum(AssetTypeEnum), nullable=False)
    # 存储基础数量或配置，真实数量可能来自其他系统
    base_balance = Column(Float, default=0.0) 
    # 用于获取实时价格的API符号，例如 'BTCUSDT' 或 'XAUUSD'
    ticker = Column(String, unique=True)
  # 新增关系，一个资产可以有多条变动记录
    transactions = relationship("AssetTransactionDB", back_populates="asset")
class AssetTransactionDB(Base):
    __tablename__ = "asset_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("reserve_assets.id"), nullable=False)
    transaction_type = Column(SQLAlchemyEnum(TransactionTypeEnum), nullable=False)
    amount = Column(Float, nullable=False)
    notes = Column(String, nullable=True) # 变动原因/备注
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    asset = relationship("ReserveAssetDB", back_populates="transactions")

class ProofOfReserveReportDB(Base):
    __tablename__ = "proof_of_reserve_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(DateTime, nullable=False, index=True)
    total_reserve_usd = Column(Float, nullable=False)
    total_supply = Column(Float, nullable=False) # 链上总供应量
    collateral_ratio = Column(Float, nullable=False)
    
    # 证明来源，例如 "Chainlink PoR" 或审计公司名称
    attestation_firm = Column(String, default="Internal Audit") 
    
    # 指向详细报告文件(PDF/JSON)的链接，这里我们存个模拟路径
    report_url = Column(String, nullable=True) 
    
    created_at = Column(DateTime, default=datetime.utcnow)

class DailyMetricDB(Base):
    __tablename__ = "daily_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)
    market_cap = Column(Float)
    circulating_supply = Column(Float)
    daily_volume = Column(Float)
    active_addresses = Column(Integer)

from sqlalchemy.orm import Session
from ..schemas.reserve import ReserveAssetCreate, AssetTransactionCreate,ReserveAssetUpdate

def get_asset_by_name_or_ticker(db: Session, name: str, ticker: str):
    return db.query(ReserveAssetDB).filter(
        (ReserveAssetDB.name == name) | (ReserveAssetDB.ticker == ticker)
    ).first()

def create_reserve_asset(db: Session, asset: ReserveAssetCreate):
    db_asset = ReserveAssetDB(**asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

def get_all_assets(db: Session):
    return db.query(ReserveAssetDB).all()

def adjust_asset_balance(db: Session, transaction: AssetTransactionCreate):
    db_asset = db.query(ReserveAssetDB).filter(ReserveAssetDB.id == transaction.asset_id).first()
    if not db_asset:
        return None
    
    if transaction.transaction_type == "存入":
        db_asset.base_balance += transaction.amount
    elif transaction.transaction_type == "取出":
        if db_asset.base_balance < transaction.amount:
            raise ValueError("余额不足，无法取出")
        db_asset.base_balance -= transaction.amount

    db_transaction = AssetTransactionDB(**transaction.model_dump())
    db.add(db_transaction)
    
    db.commit()
    db.refresh(db_asset)
    return db_asset

def get_asset_by_id(db: Session, asset_id: int):
    return db.query(ReserveAssetDB).filter(ReserveAssetDB.id == asset_id).first()

def update_reserve_asset(db: Session, asset_id: int, asset_update: ReserveAssetUpdate):
    db_asset = get_asset_by_id(db, asset_id=asset_id)
    if not db_asset:
        return None

    # model_dump(exclude_unset=True) 是一个关键技巧
    # 它只获取那些在请求中被明确设置了值的字段
    update_data = asset_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_asset, key, value)
        
    db.commit()
    db.refresh(db_asset)
    return db_asset