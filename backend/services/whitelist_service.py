from sqlalchemy.orm import Session
from ..models import Whitelist, User
from fastapi import HTTPException

def get_whitelist(db: Session):
    items = db.query(Whitelist).all()
    return items

def add_to_whitelist(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.is_whitelisted:
        raise HTTPException(status_code=400, detail="已在白名单")
    user.is_whitelisted = True
    wl = Whitelist(user_id=user_id)
    db.add(wl)
    db.commit()
    return wl

def remove_from_whitelist(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_whitelisted:
        raise HTTPException(status_code=404, detail="不在白名单")
    user.is_whitelisted = False
    db.query(Whitelist).filter(Whitelist.user_id == user_id).delete()
    db.commit()
    return True

def add_to_blacklist(db: Session, user_id: int):
    """将用户添加到黑名单"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.is_blacklisted:
        raise HTTPException(status_code=400, detail="已在黑名单")
    user.is_blacklisted = True
    # 这里可以添加更多的黑名单逻辑
    db.commit()
    return True

def remove_from_blacklist(db: Session, user_id: int):
    """将用户从黑名单移除"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_blacklisted:
        raise HTTPException(status_code=404, detail="不在黑名单")
    user.is_blacklisted = False
    db.commit()
    return True

def is_blacklisted(db: Session, user_id: int):
    """检查用户是否在黑名单中"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user.is_blacklisted

def is_whitelist_enabled(db: Session):
    """检查白名单是否启用"""
    # 这里可以添加检查白名单是否启用的逻辑
    # 目前我们假设白名单总是启用的
    return True

def set_whitelist_status(db: Session, enabled: bool):
    """设置白名单状态"""
    # 这里可以添加设置白名单状态的逻辑
    # 目前我们只是简单地返回
    pass
