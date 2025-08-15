from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from .base import Base

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(String)  # deposit, withdraw, trade, contract, mint, burn, transfer
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    block_number = Column(Integer, nullable=True)  # 区块号
    status = Column(String, default='pending')
    tx_hash = Column(String, nullable=True)  # 交易哈希
    from_address = Column(String, nullable=True)  # 发起方地址
    to_address = Column(String, nullable=True)  # 接收方地址
    gas_used = Column(Integer, nullable=True)  # gas 使用量
    gas_price = Column(String, nullable=True)  # gas 价格
    fee = Column(Float, nullable=True)  # 手续费