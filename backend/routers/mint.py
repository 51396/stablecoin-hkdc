from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services import mint_service
from ..database import get_db
from ..models import User
from ..core.security import get_current_user

router = APIRouter(prefix="/mint", tags=["铸造"])

@router.post("/single", summary="一键铸造")
def mint_single(amount: float, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """授权管理员一键铸造稳定币"""
    # 检查当前用户是否为管理员
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 调用服务进行铸造（使用batch_mint实现单个铸造）
    transactions = mint_service.batch_mint(db, [user_id], amount)
    return {"message": "铸造成功", "transaction_id": transactions[0].id}

@router.post("/batch", summary="批量铸造")
def mint_batch(user_ids: list, amount: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """批量铸造稳定币给多个用户"""
    # 检查当前用户是否为管理员
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 调用服务进行批量铸造
    transactions = mint_service.batch_mint(db, user_ids, amount)
    return {"message": "批量铸造成功", "transaction_count": len(transactions)}

@router.get("/total", summary="获取已铸造总量")
def get_minted_total(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取已铸造的稳定币总量"""
    # 检查当前用户是否为管理员
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 调用服务获取已铸造总量
    total = mint_service.get_minted_total(db)
    return {"total": total}