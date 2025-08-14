from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.total_supply_service import update_total_supply_periodically, get_latest_total_supply_from_db
from ..models import TotalSupplyHistory

router = APIRouter(prefix="/total_supply", tags=["总供应量"])

@router.post("/refresh", summary="手动刷新总供应量")
def refresh_total_supply(db: Session = Depends(get_db)):
    """手动触发总供应量更新"""
    try:
        # 获取并更新总供应量
        update_total_supply_periodically()
        return {"message": "总供应量已成功更新"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新总供应量失败: {str(e)}")

@router.get("/latest", summary="获取最新的总供应量")
def get_latest_total_supply(db: Session = Depends(get_db)):
    """获取数据库中存储的最新总供应量数据"""
    try:
        latest_entry = get_latest_total_supply_from_db(db)
        if latest_entry is None:
            return {"message": "暂无数据"}
        
        return {
            "total_supply": latest_entry.total_supply,
            "decimals": latest_entry.decimals,
            "timestamp": latest_entry.timestamp.isoformat() if latest_entry.timestamp else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取总供应量失败: {str(e)}")

@router.get("/history", summary="获取总供应量历史记录")
def get_total_supply_history(limit: int = 10, db: Session = Depends(get_db)):
    """获取总供应量历史记录"""
    try:
        history_entries = db.query(TotalSupplyHistory).order_by(TotalSupplyHistory.timestamp.desc()).limit(limit).all()
        
        return [
            {
                "total_supply": entry.total_supply,
                "decimals": entry.decimals,
                "timestamp": entry.timestamp.isoformat() if entry.timestamp else None
            }
            for entry in history_entries
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取总供应量历史记录失败: {str(e)}")