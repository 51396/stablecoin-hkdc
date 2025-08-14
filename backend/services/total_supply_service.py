from ..models import TotalSupplyHistory
from ..database import get_db
from ..utils.web3_utils import get_web3
from ..config import settings
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_contract_total_supply():
    """获取合约的总供应量和小数位数"""
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
        
        # 调用totalSupply函数
        total_supply = contract.functions.totalSupply().call()
        
        # 调用decimals函数获取合约的小数位数
        decimals = contract.functions.decimals().call()
        
        # 按照合约的小数位数转换为标准单位
        total_supply_standard = total_supply / (10 ** decimals)
        
        return total_supply_standard, decimals
    except Exception as e:
        logger.error(f"获取合约总供应量失败: {str(e)}")
        raise

def save_total_supply_to_db(total_supply: float, decimals: int, db: Session):
    """将总供应量数据保存到数据库"""
    try:
        history_entry = TotalSupplyHistory(
            total_supply=total_supply,
            decimals=decimals,
            timestamp=datetime.utcnow()
        )
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)
        logger.info(f"总供应量数据已保存到数据库: {total_supply}")
        return history_entry
    except Exception as e:
        db.rollback()
        logger.error(f"保存总供应量数据到数据库失败: {str(e)}")
        raise

def get_latest_total_supply_from_db(db: Session):
    """从数据库获取最新的总供应量数据"""
    try:
        latest_entry = db.query(TotalSupplyHistory).order_by(TotalSupplyHistory.timestamp.desc()).first()
        return latest_entry
    except Exception as e:
        logger.error(f"从数据库获取总供应量数据失败: {str(e)}")
        raise

def update_total_supply_periodically():
    """定期更新总供应量数据"""
    try:
        # 获取总供应量
        total_supply, decimals = get_contract_total_supply()
        
        # 获取数据库会话
        db = next(get_db())
        
        # 保存到数据库
        save_total_supply_to_db(total_supply, decimals, db)
        
        logger.info(f"总供应量已更新: {total_supply}")
    except Exception as e:
        logger.error(f"定期更新总供应量时出错: {str(e)}")