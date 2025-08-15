from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from ..database import SessionLocal, get_db
from ..models import Transaction, User
from ..core.security import get_current_user
from ..services.transaction_service import get_transaction_history, monitor_onchain_transactions

router = APIRouter(prefix="/transactions", tags=["交易管理"])

@router.get("/history", summary="交易历史记录")
def get_transaction_history_endpoint(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # 计算偏移量
    offset = (page - 1) * per_page
    
    # 如果是管理员，返回所有交易记录，包括合约交易
    if current_user.role == "admin":
        transactions_query = db.query(Transaction).order_by(Transaction.timestamp.desc())
        total = transactions_query.count()
        transactions = transactions_query.offset(offset).limit(per_page).all()
    else:
        # 对于普通用户，需要修改get_transaction_history以支持分页
        transactions_query = get_transaction_history(db, current_user.id, return_query=True)
        total = transactions_query.count()
        transactions = transactions_query.offset(offset).limit(per_page).all()
    
    # 将交易记录转换为字典列表，确保包含所有字段
    transaction_list = []
    for index, tx in enumerate(transactions, start=1):
        transaction_dict = {
            "id": index,  # 使用列表ID替代交易ID
            "user_id": tx.user_id,
            "type": tx.type,
            "amount": tx.amount,
            "block_number": tx.block_number,
            "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
            "status": tx.status,
            "tx_hash": tx.tx_hash,
            "from_address": tx.from_address,
            "to_address": tx.to_address,
            "gas_used": tx.gas_used,
            "gas_price": tx.gas_price,
            "fee": tx.fee
        }
        transaction_list.append(transaction_dict)
    
    # 返回分页结果
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": transaction_list
    }

@router.get("/monitor", summary="交易监控")
def get_pending_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    transactions = db.query(Transaction).filter(Transaction.status == "pending").all()
    return transactions

@router.get("/onchain/history", summary="链上交易历史记录")
async def get_onchain_transaction_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    # 从链上同步合约交易到数据库
    from ..services.transaction_service import sync_contract_transactions
    count = sync_contract_transactions(db)
    return {"msg": f"已从链上同步 {count} 条交易记录"}

@router.get("/{tx_id}/status", summary="交易状态查询")
def get_transaction_status(tx_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="交易不存在")
    if transaction.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    return {"status": transaction.status}

@router.get("/status/{tx_hash}", summary="根据交易哈希查询交易状态")
def get_transaction_status_by_hash(tx_hash: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.tx_hash == tx_hash).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="交易不存在")
    if transaction.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    return {"status": transaction.status}

@router.put("/{tx_id}/status", summary="更新交易状态")
def update_transaction_status(tx_id: int, status: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    transaction = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="交易不存在")
    transaction.status = status
    db.commit()
    return {"msg": "状态更新成功"}