from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal, get_db
from ..models import Transaction, User, Wallet
from ..core.security import get_current_user
from typing import List
from datetime import datetime, date

dashboard_router = APIRouter(prefix="/dashboard", tags=["驾驶舱"])

@dashboard_router.get("/data", summary="获取驾驶舱数据")
def get_dashboard_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取驾驶舱数据，包括资产、交易统计等信息"""
    try:
        #获取total_supply
        from ..services.total_supply_service import get_latest_total_supply_from_db
        total_supply = get_latest_total_supply_from_db(db)
        # 获取用户交易记录
        transactions = db.query(Transaction).all()
        
        # 计算今日交易数
        today = date.today()
        today_transactions = [
            tx for tx in transactions 
            if tx.timestamp and tx.timestamp.date() == today
        ]
        
        # 计算待处理交易数
        pending_transactions = [
            tx for tx in transactions 
            if tx.status == "pending"
        ]
        
        # 获取最近5笔交易
        recent_transactions = sorted(
            transactions, 
            key=lambda tx: tx.timestamp or datetime.min, 
            reverse=True
        )[:5]
        
        # 转换交易数据为字典
        recent_transactions_data = [
            {
                "id": tx.id,
                "user_id": tx.user_id,
                "type": tx.type,
                "amount": float(tx.amount),
                "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
                "status": tx.status,
                "tx_hash": tx.tx_hash,
            }
            for tx in recent_transactions
        ]
        
        return {
            "totalAssets": total_supply.total_supply,
            "todayTransactions": len(today_transactions),
            "pendingTransactions": len(pending_transactions),
            "recentTransactions": recent_transactions_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取驾驶舱数据失败: {str(e)}")