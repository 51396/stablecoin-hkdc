from sqlalchemy.orm import Session
from ..models import Wallet, Transaction
from fastapi import HTTPException


def batch_mint(db: Session, user_ids: list, amount: float):
    """批量铸造稳定币给多个用户"""
    transactions = []
    
    for user_id in user_ids:
        # 获取或创建用户钱包
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            wallet = Wallet(user_id=user_id, balance=0)
            db.add(wallet)
        
        # 增加余额
        wallet.balance += amount
        
        # 创建交易记录
        tx = Transaction(user_id=user_id, type="mint", amount=amount, status="success")
        db.add(tx)
        transactions.append(tx)
    
    # 提交所有更改
    db.commit()
    return transactions


def get_minted_total(db: Session):
    """获取已铸造的稳定币总量"""
    total = db.query(Transaction).filter(Transaction.type == "mint", Transaction.status == "success").with_entities(Transaction.amount).all()
    return sum([tx.amount for tx in total])