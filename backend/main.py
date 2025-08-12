from fastapi import FastAPI
from .database import init_db
from .routers import user, wallet, trade, whitelist

app = FastAPI()

init_db()

app.include_router(user.router)
app.include_router(wallet.router)
app.include_router(trade.router)
app.include_router(whitelist.router)

@app.get("/")
def read_root():
    return {"msg": "Stable Coin Backend API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)