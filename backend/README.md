# 稳定币管理后端

本后端基于 FastAPI + SQLAlchemy + SQLite 实现，结构参考专业项目。

## 目录结构

- backend/
  - core/         # 核心功能（如安全、配置）
  - models.py     # ORM模型
  - schemas.py    # Pydantic数据模型
  - services/     # 业务逻辑层
  - routers/      # 路由层
  - utils/        # 工具类
  - config.py     # 配置
  - database.py   # 数据库连接
  - main.py       # FastAPI入口
  - tests/        # 单元测试

## 开发规范
- 路由、服务、模型、数据分层清晰
- 配置集中管理，支持环境变量
- 日志、异常、认证等基础设施完善
- 单元测试覆盖主要业务逻辑

## 运行

1. 安装依赖：`pip install fastapi uvicorn sqlalchemy pydantic jose`
2. 启动服务：`uvicorn backend.main:app --reload`
