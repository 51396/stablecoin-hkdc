from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from ..models.issuance import IssuanceRequestDB, ApprovalDB, RequestStatusEnum
from ..schemas.issuance import IssuanceRequestCreate

def get_request_by_id(db: Session, request_id: int):
    return db.query(IssuanceRequestDB).options(joinedload(IssuanceRequestDB.approvals)).filter(IssuanceRequestDB.id == request_id).first()

def get_requests(db: Session, status: str):
    pending_statuses = [
        RequestStatusEnum.PENDING_APPROVAL, 
        RequestStatusEnum.APPROVED,
        RequestStatusEnum.PROCESSING
    ]
    history_statuses = [
        RequestStatusEnum.COMPLETED,
        RequestStatusEnum.REJECTED,
        RequestStatusEnum.FAILED
    ]
    
    query = db.query(IssuanceRequestDB).options(joinedload(IssuanceRequestDB.approvals))

    if status == 'pending':
        query = query.filter(IssuanceRequestDB.status.in_(pending_statuses))
    else: # history
        query = query.filter(IssuanceRequestDB.status.in_(history_statuses))
        
    requests = query.order_by(IssuanceRequestDB.created_at.desc()).all()
    # 动态计算
    for req in requests:
        req.approvals_count = len(req.approvals)
        req.task_id = f"{req.type.name.upper()}-{req.id:03d}"
    return requests

def create_issuance_request(db: Session, request: IssuanceRequestCreate, user_id: int, username: str):
    db_request = IssuanceRequestDB(
        **request.model_dump(),
        requester_id=user_id,
        requester_name=username
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    # 动态计算
    db_request.approvals_count = 0
    db_request.task_id = f"{db_request.type.name.upper()}-{db_request.id:03d}"
    return db_request

def add_approval(db: Session, request_id: int, approver_id: int, approver_name: str):
    db_request = get_request_by_id(db, request_id)
    if not db_request:
        raise ValueError("请求不存在")
    if db_request.status != RequestStatusEnum.PENDING_APPROVAL:
        raise ValueError("请求当前状态无法批准")
    
    # 检查是否重复批准
    existing_approval = db.query(ApprovalDB).filter(ApprovalDB.request_id == request_id, ApprovalDB.approver_id == approver_id).first()
    if existing_approval:
        raise ValueError("您已经批准过此请求")

    db_approval = ApprovalDB(request_id=request_id, approver_id=approver_id, approver_name=approver_name)
    db.add(db_approval)
    
    # 检查是否达到批准数量
    if len(db_request.approvals) + 1 >= db_request.required_approvals:
        db_request.status = RequestStatusEnum.APPROVED
        
    db.commit()
    db.refresh(db_request)
    return db_request

def execute_request(db: Session, request_id: int):
    db_request = get_request_by_id(db, request_id)
    if not db_request:
        raise ValueError("请求不存在")
    if db_request.status != RequestStatusEnum.APPROVED:
        raise ValueError("请求未被完全批准，无法执行")

    db_request.status = RequestStatusEnum.PROCESSING
    db.commit()
    db.refresh(db_request)
    
    # --- 在这里触发与智能合约的交互 ---
    # (这是一个耗时操作，通常会交给后台任务队列如 Celery)
    # ... contract_interaction_service.mint(db_request.target_address, db_request.amount) ...
    
    # 模拟成功
    import time, hashlib
    time.sleep(3) # 模拟链上确认
    db_request.status = RequestStatusEnum.COMPLETED
    db_request.tx_hash = f"0x{hashlib.sha256(str(time.time()).encode()).hexdigest()[:40]}"
    db.commit()
    db.refresh(db_request)

    return db_request