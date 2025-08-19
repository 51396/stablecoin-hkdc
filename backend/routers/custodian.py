# routers/custodian.py
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from ..schemas.custodian import Custodian, CustodianCreate
from ..database import get_db
from ..models.custodian import create_custodian,get_custodians
# ... (imports) ...
router = APIRouter(prefix="/custodians", tags=["托管机构管理"])

@router.post("/", response_model=Custodian)
def create_custodian_endpoint(custodian: CustodianCreate, db: Session = Depends(get_db)):
    # ... (逻辑) ...
    return create_custodian(db, custodian)

@router.get("/", response_model=list[Custodian])
def get_custodians_endpoint(skip: int = 0, limit: int = 10, search: str = "", db: Session = Depends(get_db)):
    # ... (逻辑) ...
    return get_custodians(db, skip, limit, search)