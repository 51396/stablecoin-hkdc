from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from ..models.issuance import RequestTypeEnum, RequestStatusEnum

class KpiData(BaseModel):
    totalSupply: float
    totalReserve: float
    collateralRatio: float

class IssuanceRequestBase(BaseModel):
    amount: float = Field(..., gt=0)
    target_address: str
    fund_proof_url: Optional[str] = None
    notes: Optional[str] = None
    type: RequestTypeEnum

class IssuanceRequestCreate(IssuanceRequestBase):
    pass

class IssuanceRequest(IssuanceRequestBase):
    id: int
    requester_name: str
    status: RequestStatusEnum
    approvals_count: int = 0
    required_approvals: int
    created_at: datetime
    tx_hash: Optional[str] = None
    # 为前端表格提供一个易于显示的ID
    task_id: str 

    class Config:
        from_attributes = True