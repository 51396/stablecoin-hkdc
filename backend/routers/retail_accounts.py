from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas.account import RetailAccount, RetailAccountCreate, RetailAccountUpdate, PaginatedRetailAccounts
from ..services.retail_account_service import create_account,get_accounts,get_account_by_id,update_account

router = APIRouter(
    prefix="/retail-accounts",
    tags=["对私账户 (Retail Accounts)"]
)

@router.post("/", response_model=RetailAccount, status_code=201)
def create_retail_account_endpoint(
    account_data: RetailAccountCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_account(db=db, account=account_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=PaginatedRetailAccounts)
def get_retail_accounts_endpoint(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    status: Optional[str] = None
):
    accounts, total = get_accounts(db, skip, limit, search, status)
    return {"items": accounts, "total": total}

@router.get("/{account_id}", response_model=RetailAccount)
def get_retail_account_details_endpoint(
    account_id: int,
    db: Session = Depends(get_db)
):
    db_account = get_account_by_id(db, account_id=account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="个人账户未找到")
    return db_account

@router.put("/{account_id}", response_model=RetailAccount)
def update_retail_account_endpoint(
    account_id: int,
    account_data: RetailAccountUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated_account = update_account(db, account_id=account_id, account_update=account_data)
        if not updated_account:
            raise HTTPException(status_code=404, detail="个人账户未找到")
        return updated_account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))