from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    is_active: bool
    is_whitelisted: bool

    class Config:
        orm_mode = True

class WalletOut(BaseModel):
    id: int
    user_id: int
    balance: float
    class Config:
        orm_mode = True

class TransactionOut(BaseModel):
    id: int
    user_id: int
    type: str
    amount: float
    timestamp: datetime
    status: str
    class Config:
        orm_mode = True
