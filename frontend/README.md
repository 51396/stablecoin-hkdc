# 稳定币管理前端

本前端基于 Vue 3 + Vue Router + Vuex + Axios 实现，结构参考专业项目。

## 目录结构

- src/
  - api/         # 所有后端API请求封装
  - components/  # 公共组件（如Navbar等）
  - views/       # 页面视图
  - store/       # 状态管理
  - router/      # 路由配置
  - utils/       # 工具函数
  - assets/      # 静态资源
  - App.vue      # 主组件
  - main.js      # 入口文件

## 开发规范
- 统一使用ESLint/Prettier格式化
- 组件命名统一、目录清晰
- API请求全部集中管理
- 状态管理用Vuex
- 认证信息本地存储

## 运行

1. 安装依赖：`npm install`
2. 启动开发：`npm run serve`

## 环境变量配置

项目使用.env文件配置合约地址等环境变量：

- `VUE_APP_CONTRACT_ADDRESS`：稳定币合约地址

请确保在运行项目前正确配置这些环境变量。
