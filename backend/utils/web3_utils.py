from web3 import Web3
from ..config import settings

def get_web3():
    """获取Web3实例"""
    if not settings.WEB3_PROVIDER_URI:
        raise ValueError("WEB3_PROVIDER_URI not set in settings")
    
    w3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/7e72938da1754441b9f3e1541c00ef82'))
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Ethereum node")
    
    return w3