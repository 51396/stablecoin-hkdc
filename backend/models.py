from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default='user')
    is_active = Column(Boolean, default=True)
    is_whitelisted = Column(Boolean, default=False)
    is_blacklisted = Column(Boolean, default=False)

class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    balance = Column(Float, default=0.0)

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

class Whitelist(Base):
    __tablename__ = 'whitelist'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    added_at = Column(DateTime, default=datetime.utcnow)

class TotalSupplyHistory(Base):
    __tablename__ = 'total_supply_history'
    id = Column(Integer, primary_key=True, index=True)
    total_supply = Column(Float, nullable=False)
    decimals = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
