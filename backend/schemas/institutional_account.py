from pydantic import BaseModel, Field
from typing import List, Optional

# --- Address Schemas ---
class InstitutionalAddressBase(BaseModel):
    address: str
    label: Optional[str] = None

class InstitutionalAddressCreate(InstitutionalAddressBase):
    # 创建时不需要余额，余额从链上同步
    pass

class InstitutionalAddress(InstitutionalAddressBase):
    id: int
    balance: float
    class Config: from_attributes = True

# --- Account Schemas ---
class InstitutionalAccountBase(BaseModel):
    name: str
    description: Optional[str] = None

class InstitutionalAccountCreate(InstitutionalAccountBase):
    pass

class InstitutionalAccountUpdate(InstitutionalAccountBase):
    pass

class InstitutionalAccount(InstitutionalAccountBase):
    id: int
    addresses: List[InstitutionalAddress] = []
    # 动态计算字段
    total_balance: float = 0.0
    
    class Config:
        from_attributes = True

class PaginatedInstitutionalAccounts(BaseModel):
    items: List[InstitutionalAccount]
    total: int