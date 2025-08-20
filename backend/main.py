from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db, get_db
from .routers import user, wallet, trade, whitelist, mint, burn, transaction, contract, dashboard, issuer, total_supply, address, reserve, custodian,retail_accounts
from .services.transaction_service import sync_contract_transactions
from .services.total_supply_service import update_total_supply_periodically
import asyncio
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(user.router)
app.include_router(wallet.router)
app.include_router(trade.router)
app.include_router(whitelist.router)
app.include_router(mint.router)
app.include_router(burn.router)
app.include_router(transaction.router)
app.include_router(contract.router)
app.include_router(dashboard.dashboard_router)
app.include_router(issuer.router)
app.include_router(total_supply.router)
app.include_router(address.router)
app.include_router(reserve.router)
app.include_router(custodian.router)
app.include_router(retail_accounts.router)
# 存储后台任务的引用
background_task = None
background_task_total_supply = None

async def sync_transactions_periodically():
    """定期同步合约交易"""
    while True:
        try:
            # 获取数据库会话
            db = next(get_db())
            # 同步合约交易
            count = sync_contract_transactions(db)
            print(f"同步了 {count} 笔合约交易")
            # 每30秒同步一次
            await asyncio.sleep(30000000)
        except Exception as e:
            print(f"同步合约交易时出错: {e}")
            await asyncio.sleep(300000000)

async def update_total_supply_periodically_task():
    """定期更新总供应量"""
    while True:
        try:
            # 更新总供应量
            update_total_supply_periodically()
            print("总供应量已更新")
            # 每60秒更新一次
            await asyncio.sleep(600000000)
        except Exception as e:
            print(f"更新总供应量时出错: {e}")
            await asyncio.sleep(600000000)

def start_background_sync():
    """启动后台同步任务"""
    global background_task, background_task_total_supply
    if background_task is None:
        background_task = asyncio.create_task(sync_transactions_periodically())
    if background_task_total_supply is None:
        background_task_total_supply = asyncio.create_task(update_total_supply_periodically_task())

@app.on_event("startup")
async def startup_event():
    """应用启动时启动后台同步任务"""
    start_background_sync()

@app.get("/")
def read_root():
    return {"msg": "Stable Coin Backend API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)