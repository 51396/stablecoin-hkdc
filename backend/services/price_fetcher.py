import random

def get_real_time_prices(tickers: list[str]) -> dict:
    """模拟从外部API获取实时价格"""
    prices = {
        'USD': 1.0,
        'USTB': 0.99,
        'BTCUSDT': 70000.0 * (1 + (random.random() - 0.5) * 0.05),
        'ETHUSDT': 3500.0 * (1 + (random.random() - 0.5) * 0.06),
        'XAUUSD': 2300.0 * (1 + (random.random() - 0.5) * 0.03),
    }
    return {ticker: prices.get(ticker, 0) for ticker in tickers}