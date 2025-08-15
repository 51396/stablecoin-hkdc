# schemas/reserve.py

from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..models.base import Base

from enum import Enum
from datetime import datetime
from typing import Optional


# --- 新增模型：资产交易/变动记录 ---
class TransactionTypeEnum(str, Enum):
    DEPOSIT = "存入"
    WITHDRAW = "取出"

class AssetTypeEnum(str, Enum):
    fiat = "法币"
    crypto = "加密货币"
    commodity = "大宗商品"


class ReserveAssetBase(BaseModel):
    name: str
    asset_type: AssetTypeEnum

class ReserveAsset(ReserveAssetBase):
    """用于API响应的单个资产模型"""
    balance: float
    value_usd: float
    percentage: float

class ReserveData(BaseModel):
    """用于API响应的顶级数据模型，与前端完全对应"""
    totalReserve: float
    circulatingSupply: float
    collateralRatio: float
    assetTypes: int
    lastUpdated: datetime
    assets: list[ReserveAsset]

class ReserveAssetCreate(BaseModel):
    """用于创建新资产的Schema"""
    name: str = Field(..., min_length=1, max_length=100)
    asset_type: AssetTypeEnum
    base_balance: float = Field(..., ge=0) # 数量必须大于等于0
    ticker: str = Field(..., min_length=1, max_length=20)

class ReserveAssetInfo(ReserveAssetCreate):
    """用于从数据库读取和返回资产信息（包含ID）的Schema"""
    id: int

    class Config:
        from_attributes = True # Pydantic v2
        # orm_mode = True # Pydantic v1

class AssetTransactionCreate(BaseModel):
    """用于记录一笔资产数量变动的Schema"""
    asset_id: int
    transaction_type: TransactionTypeEnum
    amount: float = Field(..., gt=0) # 变动数量必须大于0
    notes: Optional[str] = None

class ReserveAssetUpdate(BaseModel):
    """用于更新现有资产的Schema，所有字段都是可选的"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    asset_type: Optional[AssetTypeEnum] = None
    ticker: Optional[str] = Field(None, min_length=1, max_length=20)
    # base_balance 的更新通过 adjust_asset_balance 接口处理，这里不包含


class ProofOfReserveReportSchema(BaseModel):
    id: int
    report_date: datetime
    total_reserve_usd: float
    total_supply: float
    collateral_ratio: float
    attestation_firm: str
    report_url: Optional[str]

    class Config:
        from_attributes = True



class MetricHistoryPoint(BaseModel):
    """历史数据图表的单个数据点"""
    timestamp: datetime
    value: float

class VolumeDistributionPoint(BaseModel):
    """交易量分布的单个数据点"""
    source: str # 例如 'Uniswap', 'Coinbase', 'Binance'
    volume: float

class RealTimeTransaction(BaseModel):
    """实时交易Feed的单条记录"""
    hash: str
    from_addr: str
    to_addr: str
    amount: float
    timestamp: datetime

class CoreMetricsData(BaseModel):
    """核心指标仪表盘API的顶级响应模型"""
    marketCap: float
    circulatingSupply: float
    volume24h: float
    activeAddresses24h: int
    lastUpdated: datetime
    marketCapHistory30d: list[MetricHistoryPoint]
    volumeDistribution: list[VolumeDistributionPoint]
    realTimeTransactions: list[RealTimeTransaction]




