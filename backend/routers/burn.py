from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services import burn_service
from ..database import get_db
from ..models import User
from ..core.security import get_current_user

router = APIRouter(prefix="/burn", tags=["销毁/赎回"])

@router.post("/redeem", summary="用户赎回请求")
def redeem(amount: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """允许合规的稳定币持有者发起赎回请求"""
    # 检查用户是否在黑名单中
    if current_user.is_blacklisted:
        raise HTTPException(status_code=403, detail="账户已被冻结")
    
    # 调用服务处理赎回请求
    transaction = burn_service.redeem(db, current_user.id, amount)
    return {"message": "赎回请求已提交", "transaction_id": transaction.id}

@router.post("/admin", summary="管理员销毁")
def admin_burn(user_id: int, amount: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """管理员销毁稳定币并完成法币返还"""
    # 检查当前用户是否为管理员
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 调用服务进行销毁
    transaction = burn_service.admin_burn(db, user_id, amount)
    return {"message": "销毁成功", "transaction_id": transaction.id}

@router.get("/total", summary="获取已销毁总量")
def get_burned_total(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取已销毁的稳定币总量"""
    # 检查当前用户是否为管理员
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 调用服务获取已销毁总量
    total = burn_service.get_burned_total(db)
    return {"total": total}