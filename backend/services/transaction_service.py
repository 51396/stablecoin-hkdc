from sqlalchemy.orm import Session
from ..models import Transaction
from fastapi import HTTPException
from datetime import datetime, timedelta
import asyncio
import aiohttp
from ..config import settings
from .blockchain_service import get_transaction_receipt, get_contract_transactions
from ..config import settings
from ..utils.web3_utils import get_web3
from ..services.blockchain_service import w3  # 导入web3实例

# HKDC合约ABI定义
HKDC_ABI = [
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "initialOwner",
				"type": "address"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "OwnableInvalidOwner",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "OwnableUnauthorizedAccount",
		"type": "error"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "AddedToWhitelist",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "owner_",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "spender",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "value",
				"type": "uint256"
			}
		],
		"name": "Approval",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "added",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "removed",
				"type": "uint256"
			}
		],
		"name": "BatchWhitelistUpdated",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "previousOwner",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "OwnershipTransferred",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "RemovedFromWhitelist",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "value",
				"type": "uint256"
			}
		],
		"name": "Transfer",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "bool",
				"name": "enabled",
				"type": "bool"
			}
		],
		"name": "WhitelistEnabled",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "addToWhitelist",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner_",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "spender",
				"type": "address"
			}
		],
		"name": "allowance",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "spender",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "approve",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "balanceOf",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address[]",
				"name": "toAdd",
				"type": "address[]"
			},
			{
				"internalType": "address[]",
				"name": "toRemove",
				"type": "address[]"
			}
		],
		"name": "batchUpdateWhitelist",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "burn",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "decimals",
		"outputs": [
			{
				"internalType": "uint8",
				"name": "",
				"type": "uint8"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "isWhitelisted",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "mint",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "name",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "removeFromWhitelist",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "renounceOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bool",
				"name": "enabled",
				"type": "bool"
			}
		],
		"name": "setWhitelistEnabled",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "symbol",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "totalSupply",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "transfer",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "transferFrom",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "whitelistEnabled",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]


def get_transaction_history(db: Session, user_id: int = None, limit: int = 100):
    """获取交易历史记录"""
    query = db.query(Transaction)
    if user_id:
        query = query.filter(Transaction.user_id == user_id)
    return query.order_by(Transaction.timestamp.desc()).limit(limit).all()


def get_transaction_by_id(db: Session, tx_id: int):
    """根据ID获取交易详情"""
    return db.query(Transaction).filter(Transaction.id == tx_id).first()


def monitor_transactions(db: Session, minutes: int = 5):
    """监控最近的交易"""
    # 计算时间范围
    time_threshold = datetime.utcnow() - timedelta(minutes=minutes)
    
    # 查询最近的交易
    recent_transactions = db.query(Transaction).filter(
        Transaction.timestamp >= time_threshold
    ).order_by(Transaction.timestamp.desc()).all()
    
    return recent_transactions


def get_transaction_status(db: Session, tx_id: int):
    """获取交易状态"""
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="交易不存在")
    return tx.status


def update_transaction_status(db: Session, tx_id: int, status: str):
    """更新交易状态"""
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="交易不存在")
    
    tx.status = status
    db.commit()
    return tx


async def check_transaction_status(tx_hash: str):
    """检查链上交易状态"""
    try:
        # 从区块链获取交易收据
        receipt = get_transaction_receipt(tx_hash)
        if receipt:
            # 根据receipt.status判断交易状态
            if receipt['status'] == 1:
                return 'success'
            else:
                return 'failed'
        else:
            return 'unknown'
    except Exception as e:
        print(f"检查交易状态失败: {e}")
        return 'unknown'


async def monitor_onchain_transactions(db: Session):
    """监控链上交易并更新状态"""
    # 获取所有待处理的交易
    pending_transactions = db.query(Transaction).filter(Transaction.status == "pending").all()
    
    # 并发检查所有待处理交易的状态
    tasks = [check_transaction_status(tx.tx_hash) for tx in pending_transactions if hasattr(tx, 'tx_hash')]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 更新数据库中的交易状态
    for tx, status in zip(pending_transactions, results):
        if isinstance(status, str) and status != 'unknown':
            tx.status = status
            # 如果交易成功，更新相关数据
            if status == 'success':
                # 这里可以添加具体的业务逻辑，如更新用户余额等
                pass
    
    db.commit()


def get_transaction_type_and_amount(tx_input, contract_abi):
    """根据交易输入数据解析交易类型和金额"""
    try:
        # 如果没有输入数据，则为普通转账
        if not tx_input or tx_input == '0x':
            return 'transfer', 0
        




        # 创建合约实例以解析输入数据
        w3 = get_web3()
        contract = w3.eth.contract(abi=contract_abi)
        
        # 解析函数调用
        decoded_input = contract.decode_function_input(tx_input)
        function_obj, params = decoded_input
        
        # 根据函数名确定交易类型
        function_name = function_obj.fn_name

        if function_name == 'mint':
            return 'mint', params.get('amount', 0)
        elif function_name == 'burn':
            return 'burn', params.get('amount', 0)
        else:
            # 其他函数调用视为转账
            return 'transfer', params.get('amount', 0)
    except Exception as e:
        print(f"解析交易输入数据失败: {e}")
        # 默认返回转账类型
        return 'transfer', 0


def sync_contract_transactions(db: Session, from_block=0, to_block='latest'):
    """同步合约交易到数据库"""
    try:
        # 获取合约地址
        contract_address = settings.CONTRACT_ADDRESS
        # 零地址，用于判断是否为铸造事件
        ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
        # ERC-20 / ERC-721 标准的 Transfer 事件的签名哈希 (topic)
        # keccak256('Transfer(address,address,uint256)')
        TRANSFER_EVENT_TOPIC = w3.keccak(text="Transfer(address,address,uint256)").hex()
        # 从区块链获取合约交易
        transactions = get_contract_transactions(contract_address, from_block, to_block)
        # 同步到数据库
        count = 0
        for tx in transactions:
            # 检查交易是否已存在
            existing_tx = db.query(Transaction).filter(Transaction.tx_hash == tx.hash.hex()).first()
            
            if not existing_tx:
                # 计算手续费
                gas_used = tx.get('gasUsed',0)
                gas_price = tx.get('gasPrice', 0)
                fee = float(gas_used * gas_price) / 1e18 if gas_used and gas_price else 0.0
                tx_hash = tx.hash.hex()
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                status = receipt['status']
                for log in receipt['logs']:
                    if len(log['topics']) > 1 and log['topics'][0].hex() == TRANSFER_EVENT_TOPIC:
                        print(log['topics'])
                        print(tx)
                        # topics 是32字节的十六进制，地址是后20字节
                        from_address = w3.to_checksum_address(log['topics'][1].hex()[-40:])
                        # 5. 如果是，这就是一个 mint 事件，开始解码
                        to_address = w3.to_checksum_address(log['topics'][2].hex()[-40:])
                        try:
                            value_or_token_id = w3.codec.decode(['uint256'], log['data'])[0]
                        except Exception:
                            # 如果解码失败，可能是不标准的事件，跳过
                            value_or_token_id = 'decoding_error'
                        # 4. 检查 from 地址是否为零地址
                        if from_address == ZERO_ADDRESS:
                            
                            # log['data'] 存储了非索引参数 (value 或 tokenId)
                            # 需要将其解码为整数
                            tx_from = ""
                            tx_to = to_address
                            tx_type = 'mint'
                            amount = value_or_token_id / 1e6
                            print(to_address,value_or_token_id)
                        elif to_address == ZERO_ADDRESS:
                            # 6. 如果是，这就是一个 burn 事件，开始解码
                            tx_from = from_address
                            tx_to = ""
                            tx_type = 'burn'
                            amount = value_or_token_id / 1e6
                            print(from_address,value_or_token_id)
                        else:
                            tx_from = from_address
                            tx_to = to_address
                            # 7. 其他情况，视为转账
                            tx_type = 'transfer'
                            amount = value_or_token_id / 1e6
                # 解析交易类型和金额
                # tx_type, amount = get_transaction_type_and_amount(tx.get('input', '0x'), HKDC_ABI)
                
                # 获取交易时间戳
                block = w3.eth.get_block(tx['blockNumber'])
                timestamp = datetime.fromtimestamp(block['timestamp'])
                
                # 创建新的交易记录
                new_tx = Transaction(
                    user_id=0,  # 合约交易暂时设置user_id为0，表示系统级交易
                    type=tx_type,  # 交易类型
                    amount=amount,
                    block_number=tx['blockNumber'],
                    timestamp=timestamp,  # 使用区块链上的时间戳
                    tx_hash=tx.hash.hex(),
                    status=status,
                    from_address=tx_from,
                    to_address=tx_to,
                    gas_used=gas_used,
                    gas_price=str(gas_price),
                    fee=fee
                )
                db.add(new_tx)
                count += 1
        
        db.commit()
        return count
    except Exception as e:
        print(f"同步合约交易失败: {e}")
        db.rollback()
        return 0