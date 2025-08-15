from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from .base import Base

class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True, nullable=False)  # 地址
    label = Column(String, nullable=True)  # 地址标签
    is_whitelisted = Column(Boolean, default=False)  # 是否在白名单中
    is_blacklisted = Column(Boolean, default=False)  # 是否在黑名单中
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

# 预定义的地址标签类型
PREDEFINED_LABELS = [
    "交易所",
    "钱包服务商",
    "矿工",
    "DeFi协议",
    "NFT平台",
    "其他"
]