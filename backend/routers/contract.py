from fastapi import APIRouter
from ..config import settings

router = APIRouter(prefix="/contract", tags=["合约管理"])

@router.get("/address", summary="获取合约地址")
def get_contract_address():
    """获取智能合约地址"""
    return {"contract_address": settings.CONTRACT_ADDRESS}