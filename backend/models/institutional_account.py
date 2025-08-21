from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class InstitutionalAccountDB(Base):
    __tablename__ = "institutional_accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # 机构名称
    description = Column(String, nullable=True) # 描述
    
    addresses = relationship("InstitutionalAddressDB", back_populates="account", cascade="all, delete-orphan")

class InstitutionalAddressDB(Base):
    __tablename__ = "institutional_addresses"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("institutional_accounts.id"), nullable=False)
    address = Column(String, unique=True, index=True, nullable=False) # 区块链地址
    label = Column(String, nullable=True) # 地址标签
    balance = Column(Float, default=0.0) # 地址余额，可能需要定时任务从链上更新
    
    account = relationship("InstitutionalAccountDB", back_populates="addresses")