import random
import time
from datetime import datetime, timedelta
from faker import Faker # 需要安装: pip install Faker
import hashlib # 用于生成哈希值
import os # 用于生成随机字节
fake = Faker("en_US")
# --- 1. 手动实现的伪造数据生成器 ---

def _generate_fake_eth_address() -> str:
    """手动生成一个格式正确的伪造以太坊地址"""
    random_bytes = os.urandom(20) # 以太坊地址是20字节
    hex_address = random_bytes.hex()
    return '0x' + hex_address

def _generate_fake_hash() -> str:
    """手动生成一个伪造的交易哈希"""
    random_data = str(random.random()).encode('utf-8')
    return hashlib.sha256(random_data).hexdigest()

def get_current_metrics():
    
    
    """模拟从实时数据源获取当前核心指标"""
    base_supply = 100_000_000
    return {
        "marketCap": base_supply * (1 + (random.random() - 0.5) * 0.01),
        "circulatingSupply": base_supply * (0.98 + random.random() * 0.02),
        "volume24h": 5_000_000 * (0.8 + random.random() * 0.4),
        "activeAddresses24h": random.randint(5000, 15000)
    }

def get_market_cap_history():
    """模拟从数据库或数据服务获取过去30天的市值历史"""
    history = []
    base_market_cap = 100_000_000
    now = datetime.utcnow()
    for i in range(30):
        # 从29天前开始
        timestamp = now - timedelta(days=29 - i)
        # 模拟一个带趋势和波动的历史值
        value = base_market_cap * (1 - 0.05 * ((29-i)/29) + (random.random() - 0.5) * 0.02)
        history.append({"timestamp": timestamp, "value": value})
    return history

def get_volume_distribution():
    """模拟获取不同来源的交易量分布"""
    sources = ['Uniswap V3', 'Coinbase', 'Binance', 'OKX', 'Other DEXs']
    distribution = []
    total_volume = 1.0 # 归一化
    for source in sources[:-1]:
        part = random.uniform(0.1, total_volume * 0.6)
        distribution.append({"source": source, "volume": part})
        total_volume -= part
    distribution.append({"source": sources[-1], "volume": total_volume})
    
    # 将归一化的值乘以总交易量
    current_volume = get_current_metrics()['volume24h']
    return [{"source": d["source"], "volume": d["volume"] * current_volume} for d in distribution]

def get_real_time_transactions():
    """模拟获取最新的大额交易"""
    transactions = []
    print(fake)

    for _ in range(5): # 返回最新的5笔
        transactions.append({
            "hash": _generate_fake_hash()[:16] + "...",
            "from_addr": _generate_fake_eth_address(),
            "to_addr": _generate_fake_eth_address(),
            "amount": random.choice([10000, 50000, 100000, 250000]) * (1 + random.random()),
            "timestamp": datetime.utcnow() - timedelta(seconds=random.randint(1, 60))
        })
    return transactions