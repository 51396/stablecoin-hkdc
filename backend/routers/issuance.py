from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..schemas.issuance import KpiData, IssuanceRequest, IssuanceRequestCreate
from ..services.issuance_service import get_requests,create_issuance_request,add_approval,execute_request

# 假设有一个获取当前用户的依赖
from ..core.security import get_current_user

router = APIRouter(
    prefix="/issuance",
    tags=["发行控制 (Issuance)"]
)

@router.get("/kpi", response_model=KpiData)
def get_kpi_endpoint():
    # 在真实应用中，这些值会从链上分析服务或数据库中计算得出
    return {
        "totalSupply": 100250000, 
        "totalReserve": 100350000, 
        "collateralRatio": 100.10
    }

@router.get("/tasks", response_model=List[IssuanceRequest])
def get_tasks_endpoint(status: str = "pending", db: Session = Depends(get_db)):
    return get_requests(db, status=status)

@router.post("/requests", response_model=IssuanceRequest, status_code=201)
def create_request_endpoint(
    request_data: IssuanceRequestCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # 获取当前登录用户
):
    # 假设 current_user 对象有 id 和 name 属性
    return create_issuance_request(db, request=request_data, user_id=current_user.id, username=current_user.username)

@router.post("/requests/{request_id}/approve", response_model=IssuanceRequest)
def approve_request_endpoint(
    request_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        return add_approval(db, request_id=request_id, approver_id=current_user.id, approver_name=current_user.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/requests/{request_id}/execute", response_model=IssuanceRequest)
def execute_request_endpoint(
    request_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 在真实应用中，需要检查执行权限
    try:
        # 注意：这里的执行是同步的，对于耗时操作应改为后台任务
        return execute_request(db, request_id=request_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))