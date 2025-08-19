from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..models.base import Base
from typing import Optional,List
class CustodianBase(BaseModel):
    name: str
    custodian_type: str
    account_address: str

class CustodianCreate(CustodianBase):
    pass

class Custodian(CustodianBase):
    id: int
    class Config: from_attributes = True

class ReserveAssetAccountBase(BaseModel):
    # ...
    pass

class ReserveAssetAccountBase(BaseModel):
    name: str = Field(..., min_length=2)
    asset_type: str
    currency: str = Field(..., max_length=10)
    balance: float = Field(..., ge=0)
    custodian_id: int

class ReserveAssetAccountCreate(ReserveAssetAccountBase):
    """用于从API接收创建请求的模型"""
    pass

class ReserveAssetAccount(ReserveAssetAccountBase):
    """用于API响应的模型，包含数据库生成的ID"""
    id: int
    custodian: Custodian # 嵌套显示所属机构信息

    class Config:
        from_attributes = True
        
class PaginatedAccounts(BaseModel):
    total: int
    items: list[ReserveAssetAccount]
    
class AssetTransactionSchema(BaseModel):
    """用于显示单条资产变动历史的Schema"""
    id: int
    transaction_type: str
    amount: float
    notes: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

class ReserveAssetAccountDetails(ReserveAssetAccount): # 继承自基础的账户Schema
    """用于账户详情页的Schema，包含完整的变动历史"""
    transactions: List[AssetTransactionSchema] = []