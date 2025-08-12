from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Wallet, Transaction

router = APIRouter(prefix="/trade", tags=["trade"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/buy")
def buy(user_id: int, amount: float, db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet or wallet.balance < amount:
        raise HTTPException(status_code=400, detail="余额不足")
    wallet.balance -= amount
    tx = Transaction(user_id=user_id, type="buy", amount=amount, status="success")
    db.add(tx)
    db.commit()
    return {"msg": "买入成功", "balance": wallet.balance}

@router.post("/sell")
def sell(user_id: int, amount: float, db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    wallet.balance += amount
    tx = Transaction(user_id=user_id, type="sell", amount=amount, status="success")
    db.add(tx)
    db.commit()
    return {"msg": "卖出成功", "balance": wallet.balance}

@router.get("/records/{user_id}")
def get_transactions(user_id: int, db: Session = Depends(get_db)):
    txs = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    return [{"id": tx.id, "type": tx.type, "amount": tx.amount, "status": tx.status, "timestamp": tx.timestamp} for tx in txs]
