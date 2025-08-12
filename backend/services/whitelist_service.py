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
