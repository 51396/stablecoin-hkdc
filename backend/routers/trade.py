from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Wallet, Transaction
from .user import get_current_user

router = APIRouter(prefix="/trade", tags=["trade"])

@router.post("/buy")
def buy_coins(amount: float, price: float, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        wallet = Wallet(user_id=current_user.id, balance=0)
        db.add(wallet)
    
    total_cost = amount * price
    if wallet.balance < total_cost:
        raise HTTPException(status_code=400, detail="余额不足")
    
    wallet.balance -= total_cost
    # 这里应该调用智能合约进行铸币，简化处理
    tx = Transaction(user_id=current_user.id, type="buy", amount=amount, price=price, status="pending")
    db.add(tx)
    db.commit()
    return {"msg": "购买请求已提交", "tx_id": tx.id}

@router.post("/sell")
def sell_coins(amount: float, price: float, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet or wallet.balance < amount:
        raise HTTPException(status_code=400, detail="余额不足")
    
    wallet.balance -= amount
    # 这里应该调用智能合约进行销毁，简化处理
    tx = Transaction(user_id=current_user.id, type="sell", amount=amount, price=price, status="pending")
    db.add(tx)
    db.commit()
    return {"msg": "出售请求已提交", "tx_id": tx.id}

@router.get("/history")
def get_trade_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 如果是管理员，返回所有交易记录，包括合约交易
    if current_user.role == "admin":
        transactions = db.query(Transaction).all()
    else:
        # 普通用户只返回自己的交易记录
        transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    return transactions
