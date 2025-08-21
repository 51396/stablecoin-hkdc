from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas.institutional_account import (
    InstitutionalAccount, InstitutionalAccountCreate, InstitutionalAccountUpdate, 
    InstitutionalAddress, InstitutionalAddressCreate, PaginatedInstitutionalAccounts
)
from ..services.institutional_account_service import create_account,get_accounts,bind_address

router = APIRouter(
    prefix="/institutional-accounts",
    tags=["对公账户 (Institutional Accounts)"]
)

@router.post("/", response_model=InstitutionalAccount, status_code=201)
def create_institutional_account_endpoint(
    account_data: InstitutionalAccountCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_account(db=db, account=account_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=PaginatedInstitutionalAccounts)
def get_institutional_accounts_endpoint(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None
):
    accounts, total = get_accounts(db, skip, limit, search)
    return {"items": accounts, "total": total}

@router.post("/{account_id}/addresses", response_model=InstitutionalAddress, status_code=201)
def bind_address_to_account_endpoint(
    account_id: int,
    address_data: InstitutionalAddressCreate,
    db: Session = Depends(get_db)
):
    try:
        return bind_address(db, account_id=account_id, address=address_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))