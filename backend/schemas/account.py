from pydantic import BaseModel, Field
from typing import List, Optional
from ..models.account import UserStatusEnum

# --- Address Schemas ---
class RetailAddressBase(BaseModel):
    address: str

class RetailAddress(RetailAddressBase):
    id: int
    class Config: from_attributes = True

# --- Account Schemas ---
class RetailAccountBase(BaseModel):
    username: str
    kyc_level: int = Field(1, ge=1, le=3)
    status: UserStatusEnum

class RetailAccountCreate(RetailAccountBase):
    pass

class RetailAccountUpdate(BaseModel):
    # 更新时所有字段都是可选的
    username: Optional[str] = None
    kyc_level: Optional[int] = Field(None, ge=1, le=3)
    status: Optional[UserStatusEnum] = None

class RetailAccount(RetailAccountBase):
    id: int
    uid: str
    addresses: List[RetailAddress] = []
    
    class Config:
        from_attributes = True

class PaginatedRetailAccounts(BaseModel):
    items: List[RetailAccount]
    total: int