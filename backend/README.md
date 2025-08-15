# 稳定币管理后端

本后端基于 FastAPI + SQLAlchemy + SQLite 实现，结构参考专业项目。

## 目录结构

- backend/
  - core/         # 核心功能（如安全、配置）
  - models/       # ORM模型目录
    - __init__.py # 模型导入
    - base.py     # 基础模型
    - user.py     # 用户模型
    - wallet.py   # 钱包模型
    - transaction.py # 交易模型
    - address.py  # 地址模型
    - whitelist.py # 白名单模型
    - total_supply.py # 总供应量模型
    - reserve.py  # 储备金模型
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

1. 安装依赖：`pip install -r backend/requirements.txt`
2. 启动服务：`uvicorn backend.main:app --reload`

## 环境变量配置

项目使用.env文件配置数据库连接和JWT密钥等环境变量：

- `DB_URL`：数据库连接URL
- `JWT_SECRET`：JWT密钥
- `DEBUG`：调试模式开关

请确保在运行项目前正确配置这些环境变量。

## 区块链服务

项目现在支持通过RPC连接获取区块链数据，包括：

- 获取指定合约地址的所有交易
- 获取交易详情和收据
- 获取区块交易
- 获取最新区块号

这些功能通过`backend/services/blockchain_service.py`文件提供。

## 数据同步

项目会自动定期同步区块链上的合约交易到本地数据库，无需手动操作。同步间隔为30秒。

## 权限说明

- 普通用户只能查看自己的交易记录
- 管理员用户可以查看所有交易记录，包括合约交易

## 交易详情

交易详情现在包含更多区块链交易信息：

- 发起方地址
- 接收方地址
- Gas 使用量
- Gas 价格
- 手续费

管理员用户在交易列表中可以直接看到发起方和接收方地址。
