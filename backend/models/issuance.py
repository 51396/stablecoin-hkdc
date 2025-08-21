from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
from enum import Enum
from datetime import datetime

class RequestTypeEnum(str, Enum):
    mint = "mint"
    burn = "burn"

class RequestStatusEnum(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class IssuanceRequestDB(Base):
    __tablename__ = "issuance_requests"

    id = Column(Integer, primary_key=True, index=True)
    # 我们可以用自增ID和一个前缀来生成任务ID，例如 MINT-{id}
    type = Column(SQLAlchemyEnum(RequestTypeEnum), nullable=False)
    amount = Column(Float, nullable=False)
    target_address = Column(String, nullable=False)
    fund_proof_url = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    status = Column(SQLAlchemyEnum(RequestStatusEnum), default=RequestStatusEnum.PENDING_APPROVAL)
    
    # 假设有一个用户系统，这里存用户ID
    requester_id = Column(Integer, nullable=False) # 在真实应用中应该是一个 ForeignKey
    requester_name = Column(String) # 为方便显示，冗余一个名字
    
    tx_hash = Column(String, nullable=True) # 链上交易哈希
    required_approvals = Column(Integer, default=2) # 需要的签名数，可以从配置读取
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    approvals = relationship("ApprovalDB", back_populates="request", cascade="all, delete-orphan")

class ApprovalDB(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("issuance_requests.id"), nullable=False)
    # 假设有一个用户系统
    approver_id = Column(Integer, nullable=False)
    approver_name = Column(String)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    request = relationship("IssuanceRequestDB", back_populates="approvals")