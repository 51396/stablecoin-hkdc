# services/proof_of_reserve.py

import random
from datetime import datetime
from sqlalchemy.orm import Session
from models.reserve import ProofOfReserveReportDB

# --- 模拟模块 ---
def get_onchain_total_supply():
    """模拟从区块链浏览器API或节点获取稳定币的总供应量"""
    # 假设总供应量在9800万到1.02亿之间波动
    return 100_000_000 * (0.98 + random.random() * 0.04)

def get_offchain_bank_attestation():
    """
    模拟通过预言机或审计公司API获取链下法币储备的证明。
    在真实世界中，这会是一个对Chainlink PoR或其他可信数据源的安全API调用。
    """
    # 假设银行真实储备在4950万到5050万之间
    return {"asset_name": "美元现金储备", "balance": 50_000_000 * (0.99 + random.random() * 0.02)}

# --- 报告生成核心函数 ---
def generate_and_save_report(db: Session):
    print(f"[{datetime.utcnow()}] 开始生成每日储备金证明报告...")
    
    # 1. 获取所有资产的内部计算价值 (复用仪表盘逻辑)
    # (这里为了简化，我们直接模拟计算过程)
    # 在真实应用中，你会调用与仪表盘相同的内部服务来获取 total_reserve_usd
    calculated_total_reserve = 101_000_000 * (0.99 + random.random() * 0.02) # 模拟一个总价值

    # 2. 链下数据同步与验证 (模拟预言机)
    bank_attestation = get_offchain_bank_attestation()
    print(f"  - 从可信源获取的银行余额证明: ${bank_attestation['balance']:,.2f}")
    # 你可以在这里加入对比验证逻辑，如果内部计算值与外部证明差异过大，则发出警报
    
    # 3. 获取链上总供应量
    onchain_supply = get_onchain_total_supply()
    print(f"  - 从链上获取的总供应量: {onchain_supply:,.2f}")

    # 4. 计算抵押率
    collateral_ratio = (calculated_total_reserve / onchain_supply) * 100 if onchain_supply > 0 else 0
    print(f"  - 计算出的抵押率: {collateral_ratio:.2f}%")
    
    # 5. (模拟) 生成详细报告文件并获取URL
    # 在真实应用中，这里会生成一个PDF或JSON文件，并上传到S3等存储服务
    report_filename = f"PoR_Report_{datetime.utcnow().strftime('%Y-%m-%d')}.json"
    report_url = f"/reports/{report_filename}" # 模拟一个可访问的URL

    # 6. 将报告摘要存入数据库
    report_entry = ProofOfReserveReportDB(
        report_date=datetime.utcnow(),
        total_reserve_usd=calculated_total_reserve,
        total_supply=onchain_supply,
        collateral_ratio=collateral_ratio,
        attestation_firm="Chainlink PoR (模拟)",
        report_url=report_url
    )
    db.add(report_entry)
    db.commit()
    print("  - 报告已成功生成并存入数据库。")
    
    return report_entry