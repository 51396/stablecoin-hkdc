from sqlalchemy.orm import Session
from ..models import Wallet, Transaction
from fastapi import HTTPException


def redeem(db: Session, user_id: int, amount: float):
    """用户发起赎回请求"""
    # 获取用户钱包
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet or wallet.balance < amount:
        raise HTTPException(status_code=400, detail="余额不足")
    
    # 减少余额
    wallet.balance -= amount
    
    # 创建赎回交易记录（待处理状态）
    tx = Transaction(user_id=user_id, type="redeem", amount=amount, status="pending")
    db.add(tx)
    db.commit()
    
    return tx


def admin_burn(db: Session, user_id: int, amount: float):
    """管理员销毁稳定币并完成法币返还"""
    # 获取用户钱包
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet or wallet.balance < amount:
        raise HTTPException(status_code=400, detail="余额不足")
    
    # 减少余额
    wallet.balance -= amount
    
    # 创建销毁交易记录
    tx = Transaction(user_id=user_id, type="burn", amount=amount, status="success")
    db.add(tx)
    db.commit()
    
    return tx


def get_burned_total(db: Session):
    """获取已销毁的稳定币总量"""
    total = db.query(Transaction).filter(Transaction.type == "burn", Transaction.status == "success").with_entities(Transaction.amount).all()
    return sum([tx.amount for tx in total])