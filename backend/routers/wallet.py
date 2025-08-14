from fastapi import APIRouter, HTTPException, Depends
from .user import get_current_user
from ..models import User
from sqlalchemy.orm import Session
from ..database import SessionLocal, get_db
from ..models import Wallet, User, Transaction

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.get("")
def get_wallet(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="钱包不存在")
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "balance": wallet.balance
    }

@router.post("/deposit")
def deposit(amount: float, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        wallet = Wallet(user_id=current_user.id, balance=0)  # 修复变量名
        db.add(wallet)
    wallet.balance += amount
    tx = Transaction(user_id=current_user.id, type="deposit", amount=amount, status="success")
    db.add(tx)
    db.commit()
    return {"msg": "充值成功", "balance": wallet.balance}

@router.post("/withdraw")
def withdraw(amount: float, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet or wallet.balance < amount:
        raise HTTPException(status_code=400, detail="余额不足")
    wallet.balance -= amount
    tx = Transaction(user_id=current_user.id, type="withdraw", amount=amount, status="success")
    db.add(tx)
    db.commit()
    return {"msg": "提币成功", "balance": wallet.balance}
