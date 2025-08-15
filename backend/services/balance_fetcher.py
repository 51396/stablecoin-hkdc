# services/balance_fetcher.py
import random

def get_real_time_balances(asset_ids: list[int]) -> dict:
    """模拟从托管账户或钱包获取实时余额"""
    # 假设 asset_id 1=美元, 2=国债, 3=BTC, ...
    base_balances = {
        1: 0,
        2: 30_000_000,
        3: 200,
        4: 2000,
        5: 500,
    }
    return {
        asset_id: base_balances.get(asset_id, 0) * (1 + (random.random() - 0.5) * 0.02)
        for asset_id in asset_ids
    }