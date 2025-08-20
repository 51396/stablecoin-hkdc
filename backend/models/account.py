from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum ,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base # 确保从您的项目中正确导入 Base
from enum import Enum

class UserStatusEnum(str, Enum):
    active = "active"
    frozen = "frozen"

class RetailAccountDB(Base):
    __tablename__ = "retail_accounts"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    kyc_level = Column(Integer, default=1, nullable=False)
    status = Column(SQLAlchemyEnum(UserStatusEnum), default=UserStatusEnum.active, nullable=False)
    
    addresses = relationship("RetailAddressDB", back_populates="account", cascade="all, delete-orphan")

class RetailAddressDB(Base):
    __tablename__ = "retail_addresses"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("retail_accounts.id"), nullable=False)
    address = Column(String, unique=True, index=True, nullable=False)
    
    account = relationship("RetailAccountDB", back_populates="addresses")