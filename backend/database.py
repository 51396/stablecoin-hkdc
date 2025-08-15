from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models.base import Base
from .models.user import User

SQLALCHEMY_DATABASE_URL = "sqlite:///./stablecoin.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    # 创建默认管理员用户
    from .routers.user import pwd_context
    db = SessionLocal()
    try:
        # 检查是否已存在管理员用户
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            # 创建默认管理员用户
            hashed_password = pwd_context.hash("admin123")
            admin_user = User(
                username="admin",
                password_hash=hashed_password,
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()
