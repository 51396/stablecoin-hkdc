from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..core.security import get_current_user
from ..config import settings
from ..utils.web3_utils import get_web3

router = APIRouter(prefix="/issuer", tags=["发行方"])

@router.get("/total_supply", summary="获取合约总供应量")
def get_total_supply():
    """获取智能合约的总供应量"""
    try:
        w3 = get_web3()
        contract_address = settings.CONTRACT_ADDRESS
        
        # 合约ABI，包含totalSupply和decimals函数
        abi = [
            {
                "constant": True,
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"name": "", "type": "uint256"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # 创建合约实例
        contract = w3.eth.contract(address=contract_address, abi=abi)
        print(contract)
        # 调用totalSupply函数
        total_supply = contract.functions.totalSupply().call()
        
        # 调用decimals函数获取合约的小数位数
        decimals = contract.functions.decimals().call()
        
        # 按照合约的小数位数转换为标准单位
        total_supply_standard = total_supply / (10 ** decimals)
        
        return {"total_supply": str(total_supply_standard), "decimals": decimals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取总供应量失败: {str(e)}")