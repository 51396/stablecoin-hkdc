import random
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
# 模拟外部API或服务
from ..services.price_fetcher import get_real_time_prices
from ..services.balance_fetcher import get_real_time_balances

# 数据库和模型依赖
from ..database import get_db
from ..models.custodian import ReserveAssetAccountDB
from ..schemas.reserve import ReserveData, ReserveAsset,ReserveAssetCreate,AssetTransactionCreate,ReserveAssetInfo,ReserveAssetUpdate
from ..schemas.custodian import PaginatedAccounts,ReserveAssetAccountDetails,ReserveAssetAccount,ReserveAssetAccountCreate
# 1. 创建一个新的路由组
router = APIRouter(
    prefix="/reserves",
    tags=["储备金管理"]
)

@router.get("/", 
            response_model=ReserveData, # 使用Pydantic模型定义响应结构
            summary="获取完整的储备金实时数据")
def get_reserve_data_endpoint(db: Session = Depends(get_db)):
    """
    这个端点是前端仪表盘的数据来源。
    它会整合数据库中的资产配置和外部服务的实时数据，
    计算后返回一个完整的数据对象。
    """
    try:

        # 1. 从数据库获取所有配置好的储备资产
        db_assets = db.query(ReserveAssetAccountDB).all()
        if not db_assets:
            # 如果数据库中没有任何资产配置，返回一个空的默认结构
            return ReserveData(
                totalReserve=0, circulatingSupply=0,collateralRatio=0,assetTypes=0, 
                lastUpdated=datetime.utcnow(), assets=[]
            )
        print(db_assets)
        # 3. 计算每个资产的价值和总价值
        processed_assets = []
        total_reserve_usd = 0

        for asset in db_assets:

            processed_assets.append({
                "id": asset.id,
                "name": asset.name,
                "asset_type": asset.asset_type,
                "balance": asset.balance,
                "value_usd": asset.balance
            })
            total_reserve_usd = total_reserve_usd + asset.balance
        
        # 4. 计算每个资产的占比
        final_assets = []
        if total_reserve_usd > 0:
            for asset_data in processed_assets:
                percentage = (asset_data["value_usd"] / total_reserve_usd) * 100
                # 使用 ReserveAsset 模型来验证和创建对象
                final_assets.append(ReserveAsset(
                    name=asset_data["name"],
                    asset_type=asset_data["asset_type"],
                    balance=asset_data["balance"],
                    value_usd=asset_data["value_usd"],
                    percentage=percentage
                ))

        # 5. 组装最终的响应数据
        #    流通量(circulatingSupply)应该从另一个独立的系统中获取
        circulating_supply = total_reserve_usd * 0.98 # 这里我们先模拟一下
        
        response_data = ReserveData(
            totalReserve=total_reserve_usd,
            circulatingSupply=circulating_supply,
            collateralRatio=total_reserve_usd / circulating_supply * 100,
            assetTypes=len(set(asset.asset_type for asset in db_assets)),
            lastUpdated=datetime.utcnow(),
            assets=final_assets
        )
        
        return response_data

    except Exception as e:
        # 捕获任何潜在的错误，并返回一个服务器错误
        # 在生产环境中，应该记录这个错误
        print(f"Error fetching reserve data: {e}")
        raise HTTPException(status_code=500, detail="获取储备金数据时发生内部错误")


# --- 新增管理接口 ---
from ..models.reserve import get_asset_by_name_or_ticker,create_reserve_asset,get_all_assets,adjust_asset_balance,update_reserve_asset    

@router.post("/manage/assets", 
             response_model=ReserveAssetInfo, 
             summary="录入一种新的储备资产")
def create_new_asset_endpoint(
    asset_data: ReserveAssetCreate,
    db: Session = Depends(get_db)
):
    """
    向系统中添加一种新的储备资产配置。
    """
    # 检查资产名称或ticker是否已存在
    existing_asset = get_asset_by_name_or_ticker(db, name=asset_data.name, ticker=asset_data.ticker)
    if existing_asset:
        raise HTTPException(status_code=400, detail="资产名称或Ticker已存在")
    
    return create_reserve_asset(db=db, asset=asset_data)

@router.get("/manage/assets", 
            response_model=List[ReserveAssetInfo], 
            summary="获取所有已录入的资产列表")
def get_all_assets_endpoint(db: Session = Depends(get_db)):
    """
    获取数据库中配置的所有储备资产列表，用于管理页面。
    """
    return get_all_assets(db=db)

@router.post("/manage/transactions", 
             response_model=ReserveAssetInfo, 
             summary="调整指定资产的数量")
def adjust_asset_balance_endpoint(
    transaction_data: AssetTransactionCreate,
    db: Session = Depends(get_db)
):
    """
    对某个资产进行“存入”或“取出”操作，以调整其基础余额。
    """
    try:
        updated_asset = adjust_asset_balance(db=db, transaction=transaction_data)
        if not updated_asset:
            raise HTTPException(status_code=404, detail="资产未找到")
        return updated_asset
    except ValueError as e:
        # 捕获 "余额不足" 的错误
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/manage/assets/{asset_id}",
            response_model=ReserveAssetInfo,
            summary="修改指定ID的资产信息")
def update_asset_endpoint(
    asset_id: int,
    asset_data: ReserveAssetUpdate,
    db: Session = Depends(get_db)
):
    """
    更新现有储备资产的基础信息，如名称、类型、Ticker。
    """
    # 检查更新后的名称或Ticker是否与其他记录冲突
    if asset_data.name or asset_data.ticker:
        existing_asset = get_asset_by_name_or_ticker(db, name=asset_data.name, ticker=asset_data.ticker)
        if existing_asset and existing_asset.id != asset_id:
            raise HTTPException(status_code=400, detail="修改后的名称或Ticker与其他资产冲突")

    updated_asset = update_reserve_asset(db=db, asset_id=asset_id, asset_update=asset_data)
    
    if not updated_asset:
        raise HTTPException(status_code=404, detail="资产未找到")
        
    return updated_asset


from ..models.reserve import ProofOfReserveReportDB
from ..schemas.reserve import ProofOfReserveReportSchema
from sqlalchemy import desc

@router.get("/proof-of-reserve",
            response_model=List[ProofOfReserveReportSchema],
            summary="获取历史储备金证明报告")
def get_proof_of_reserve_reports_endpoint(db: Session = Depends(get_db)):
    """
    为公开的透明度页面提供数据。
    返回按日期降序排列的所有已生成的审计报告摘要。
    """
    reports = db.query(ProofOfReserveReportDB).order_by(desc(ProofOfReserveReportDB.report_date)).all()
    return reports

from ..schemas.reserve import CoreMetricsData # 导入新 Schema
from ..services import core_metrics # 导入新服务模块

@router.get("/metrics",
            response_model=CoreMetricsData,
            summary="获取核心指标仪表盘的全部数据")
def get_core_metrics_endpoint():
    """
    为核心指标仪表盘提供一站式实时和历史数据。
    """
    current = core_metrics.get_current_metrics()
    
    return CoreMetricsData(
        marketCap=current['marketCap'],
        circulatingSupply=current['circulatingSupply'],
        volume24h=current['volume24h'],
        activeAddresses24h=current['activeAddresses24h'],
        lastUpdated=datetime.utcnow(),
        marketCapHistory30d=core_metrics.get_market_cap_history(),
        volumeDistribution=core_metrics.get_volume_distribution(),
        realTimeTransactions=core_metrics.get_real_time_transactions()
    )
    
from ..models.custodian import create_asset_account,get_accounts
    
@router.post("/account", 
             response_model=ReserveAssetAccount,
             summary="创建一个新的资产账户")
def create_account_endpoint(
    account_data: ReserveAssetAccountCreate,
    db: Session = Depends(get_db)
):
    """
    在指定的托管机构下，创建一个新的资产账户记录。
    """
    try:
        return create_asset_account(db=db, account=account_data)
    except ValueError as e:
        # 捕获我们在CRUD层抛出的验证错误 (机构不存在、名称重复等)
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/accounts", 
            response_model=PaginatedAccounts, # 使用新的分页响应模型
            summary="获取资产账户列表 (分页/筛选)")
def get_accounts_endpoint(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    custodian_id: Optional[int] = None,
    asset_type: Optional[str] = None,
    search: Optional[str] = None
):
    """
    获取资产账户列表，支持通过托管机构、资产类型和名称进行筛选。
    """
    
    accounts, total = get_accounts(
        db=db, 
        skip=skip, 
        limit=limit, 
        custodian_id=custodian_id, 
        asset_type=asset_type, 
        search=search
    )
    return {"total": total, "items": accounts}


@router.get("/account/{account_id}",
            response_model=ReserveAssetAccountDetails,
            summary="获取单个资产账户的详情")
def get_account_details_endpoint(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    获取指定ID的资产账户的详细信息，包括其所有的余额变动历史。
    """
    db_account = get_account_details(db=db, account_id=account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="资产账户未找到")
    return db_account