from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from ..database import get_db
from sqlalchemy.orm import Session
# ... (imports) ...
from ..schemas.account import RetailAccount
router = APIRouter(prefix="/retail-accounts", tags=["对私账户(Retail)"]) # <-- 路由前缀和标签变更

class PaginatedRetailAccounts(BaseModel):
    items: List[RetailAccount]
    total: int
    
@router.get("/", response_model=PaginatedRetailAccounts) 
def get_users_endpoint(
    skip: int = 0, limit: int = 10, search: str = "", status: str = "",
    db: Session = Depends(get_db)
):
    users, total = crud_user.get_users(db, skip, limit, search, status)
    return {"items": users, "total": total}
