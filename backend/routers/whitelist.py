from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services import whitelist_service
from ..database import get_db
from ..models import User
from ..core.security import get_current_user

router = APIRouter(prefix="/address", tags=["地址管理"])

# 白名单管理
@router.get("/whitelist", summary="获取白名单")
def get_whitelist(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    return whitelist_service.get_whitelist(db)

@router.post("/whitelist/add/{user_id}", summary="添加到白名单")
def add_to_whitelist(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    result = whitelist_service.add_to_whitelist(db, user_id)
    return {"message": "已添加到白名单", "whitelist_id": result.id}

@router.delete("/whitelist/remove/{user_id}", summary="从白名单移除")
def remove_from_whitelist(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    whitelist_service.remove_from_whitelist(db, user_id)
    return {"message": "已从白名单移除"}

# 黑名单管理
@router.post("/blacklist/add/{user_id}", summary="添加到黑名单")
def add_to_blacklist(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    whitelist_service.add_to_blacklist(db, user_id)
    return {"message": "已添加到黑名单"}

@router.delete("/blacklist/remove/{user_id}", summary="从黑名单移除")
def remove_from_blacklist(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    whitelist_service.remove_from_blacklist(db, user_id)
    return {"message": "已从黑名单移除"}

@router.get("/blacklist/check/{user_id}", summary="检查是否在黑名单中")
def check_blacklist(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    is_blacklisted = whitelist_service.is_blacklisted(db, user_id)
    return {"user_id": user_id, "is_blacklisted": is_blacklisted}

@router.get("/whitelist/status", summary="获取白名单状态")
def get_whitelist_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    is_enabled = whitelist_service.is_whitelist_enabled(db)
    return {"enabled": is_enabled}

@router.post("/whitelist/status", summary="设置白名单状态")
def set_whitelist_status(enabled: bool, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    whitelist_service.set_whitelist_status(db, enabled)
    return {"message": "白名单状态已更新", "enabled": enabled}
