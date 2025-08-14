from math import log
from web3 import Web3
from ..config import settings
from ..utils.web3_utils import get_web3

# 连接到测试网RPC节点
# 这里使用Sepolia测试网作为示例
w3 = get_web3()

def get_transaction_by_hash(tx_hash):
    """根据交易哈希获取交易详情"""
    try:
        tx = w3.eth.get_transaction(tx_hash)
        return tx
    except Exception as e:
        print(f"获取交易详情失败: {e}")
        return None

def get_transaction_receipt(tx_hash):
    """根据交易哈希获取交易收据"""
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        return receipt
    except Exception as e:
        print(f"获取交易收据失败: {e}")
        return None

def get_block_transactions(block_number):
    """获取指定区块的所有交易"""
    try:
        block = w3.eth.get_block(block_number, full_transactions=True)
        return block.transactions
    except Exception as e:
        print(f"获取区块交易失败: {e}")
        return []

def get_latest_block_number():
    """获取最新区块号"""
    try:
        block_number = w3.eth.block_number
        return block_number
    except Exception as e:
        print(f"获取最新区块号失败: {e}")
        return None

def get_contract_transactions(contract_address, from_block=0, to_block='latest'):
    """获取指定合约地址的所有交易"""
    try:
        # 使用web3.py的eth_getLogs方法获取合约相关的交易
        # 这里我们通过过滤合约地址来获取相关交易
        logs = w3.eth.get_logs({
            'address': contract_address,
            'fromBlock': from_block,
            'toBlock': to_block
        })
        
        # 提取交易哈希
        tx_hashes = list(set([log['transactionHash'].hex() for log in logs]))
        # 获取交易详情
        transactions = []
        for tx_hash in tx_hashes:
            tx = w3.eth.get_transaction(tx_hash)
            transactions.append(tx)
            
        return transactions
    except Exception as e:
        print(f"获取合约交易失败: {e}")
        return []