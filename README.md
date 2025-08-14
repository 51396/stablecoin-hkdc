# StableCoin HKDC

这是一个基于区块链的稳定币项目，使用Python/FastAPI作为后端，Vue.js作为前端。

## 功能特性

### 核心功能
- 用户注册和登录
- 钱包管理
- 稳定币交易
- 交易历史记录

### 合规功能
- **白名单管理**: 管理员可以设置用户白名单
- **铸币和销毁**: 授权的发行人可以铸币和销毁稳定币
- **地址管理**: 
  - 白名单/黑名单: 具备设置地址白名单（仅允许特定地址交易）和黑名单（冻结涉嫌非法活动的地址）的功能，这是合规的关键
  - 地址标签: 可以为不同类型的地址（如交易所、做市商、用户钱包）打上标签，便于管理和分析

### 合约管理
- 合约配置管理
- 总供应量监控

## 技术栈

### 后端
- Python 3.8+
- FastAPI
- SQLAlchemy
- SQLite
- Web3.py (与区块链交互)

### 前端
- Vue.js 3
- Element Plus
- Axios

## 安装和运行

### 后端

1. 安装依赖:
   ```
   cd backend
   pip install -r requirements.txt
   ```

2. 运行应用:
   ```
   python main.py
   ```

### 前端

1. 安装依赖:
   ```
   cd frontend
   npm install
   ```

2. 运行开发服务器:
   ```
   npm run serve
   ```

## API文档

后端API文档可通过访问 `http://localhost:8000/docs` 查看。

## 数据库

项目使用SQLite数据库，数据库文件为 `backend/stablecoin.db`。

## 许可证

[MIT License](LICENSE)