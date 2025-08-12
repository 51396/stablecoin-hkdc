from sqlalchemy.orm import Session
from ..models import Wallet, Transaction
from fastapi import HTTPException

def buy(db: Session, user_id: int, amount: float):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet or wallet.balance < amount:
        raise HTTPException(status_code=400, detail="余额不足")
    wallet.balance -= amount
    tx = Transaction(user_id=user_id, type="buy", amount=amount, status="success")
    db.add(tx)
    db.commit()
    return wallet

def sell(db: Session, user_id: int, amount: float):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    wallet.balance += amount
    tx = Transaction(user_id=user_id, type="sell", amount=amount, status="success")
    db.add(tx)
    db.commit()
    return wallet

def get_transactions(db: Session, user_id: int):
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()
