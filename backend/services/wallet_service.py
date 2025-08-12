from sqlalchemy.orm import Session
from ..models import Wallet, Transaction
from fastapi import HTTPException

def get_wallet(db: Session, user_id: int):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="钱包不存在")
    return wallet

def deposit(db: Session, user_id: int, amount: float):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=0)
        db.add(wallet)
    wallet.balance += amount
    tx = Transaction(user_id=user_id, type="deposit", amount=amount, status="success")
    db.add(tx)
    db.commit()
    return wallet

def withdraw(db: Session, user_id: int, amount: float):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet or wallet.balance < amount:
        raise HTTPException(status_code=400, detail="余额不足")
    wallet.balance -= amount
    tx = Transaction(user_id=user_id, type="withdraw", amount=amount, status="success")
    db.add(tx)
    db.commit()
    return wallet
