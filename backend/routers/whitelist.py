from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Whitelist, User

router = APIRouter(prefix="/whitelist", tags=["whitelist"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_whitelist(db: Session = Depends(get_db)):
    items = db.query(Whitelist).all()
    result = []
    for item in items:
        user = db.query(User).filter(User.id == item.user_id).first()
        result.append({"id": item.id, "username": user.username if user else "未知"})
    return result

@router.post("/add")
def add_to_whitelist(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.is_whitelisted:
        raise HTTPException(status_code=400, detail="已在白名单")
    user.is_whitelisted = True
    wl = Whitelist(user_id=user_id)
    db.add(wl)
    db.commit()
    return {"msg": "添加成功"}

@router.post("/remove")
def remove_from_whitelist(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_whitelisted:
        raise HTTPException(status_code=404, detail="不在白名单")
    user.is_whitelisted = False
    db.query(Whitelist).filter(Whitelist.user_id == user_id).delete()
    db.commit()
    return {"msg": "移除成功"}
