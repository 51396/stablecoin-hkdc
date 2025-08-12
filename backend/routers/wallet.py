from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Wallet, User, Transaction

router = APIRouter(prefix="/wallet", tags=["wallet"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{user_id}")
def get_wallet(user_id: int, db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="钱包不存在")
    return {"balance": wallet.balance}

@router.post("/deposit")
def deposit(user_id: int, amount: float, db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=0)
        db.add(wallet)
    wallet.balance += amount
    tx = Transaction(user_id=user_id, type="deposit", amount=amount, status="success")
    db.add(tx)
    db.commit()
    return {"msg": "充值成功", "balance": wallet.balance}

@router.post("/withdraw")
def withdraw(user_id: int, amount: float, db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet or wallet.balance < amount:
        raise HTTPException(status_code=400, detail="余额不足")
    wallet.balance -= amount
    tx = Transaction(user_id=user_id, type="withdraw", amount=amount, status="success")
    db.add(tx)
    db.commit()
    return {"msg": "提币成功", "balance": wallet.balance}
