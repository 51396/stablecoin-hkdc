import request from './index';

// 钱包相关 API
export const walletAPI = {
  // 获取用户钱包信息
  getUserWallet() {
    return request.get('/wallet/')
  },
  
  // 充值
  deposit(amount) {
    return request.post('/wallet/deposit', { amount })
  },
  
  // 提币
  withdraw(amount) {
    return request.post('/wallet/withdraw', { amount })
  },
  
  // 获取交易记录
  getTransactions() {
    return request.get('/trade/records')
  },
  
  // 获取钱包资产列表
  getWalletAssets() {
    return request.get('/wallet/assets')
  },
  
  // 获取驾驶舱数据
  getDashboardData() {
    return request.get('/dashboard/data')
  }
}

// 交易相关 API
export const tradeAPI = {
  // 买入
  buy(data) {
    return request.post('/trade/buy', data)
  },
  
  // 卖出
  sell(data) {
    return request.post('/trade/sell', data)
  },
  
  // 获取交易历史（从数据库）
  getTradeHistory() {
    return request.get('/transactions/history')
  },
  
  // 检查交易状态
  checkTransactionStatus(txHash) {
    return request.get(`/transactions/status/${txHash}`)
  },
  
  // 手动刷新交易历史（从链上获取）
  refreshTradeHistory() {
    return request.get('/transactions/onchain/history')
  }
}

// 白名单相关 API
export const whitelistAPI = {
  // 获取白名单
  getWhitelist() {
    return request.get('/address/whitelist')
  },
  
  // 添加到白名单
  addToWhitelist(userId) {
    return request.post('/address/whitelist/add/' + userId)
  },
  
  // 从白名单移除
  removeFromWhitelist(userId) {
    return request.delete('/address/whitelist/remove/' + userId)
  },
  
  // 获取白名单状态
  getWhitelistStatus() {
    return request.get('/address/whitelist/status')
  },
  
  // 设置白名单状态
  setWhitelistStatus(enabled) {
    return request.post('/address/whitelist/status', { enabled })
  }
}

// 铸造相关 API
export const mintAPI = {
  mintSingle(amount, userId) {
    return request.post('/mint/single', { amount, user_id: userId })
  },
  mintBatch(userIds, amount) {
    return request.post('/mint/batch', { user_ids: userIds, amount })
  },
  getMintedTotal() {
    return request.get('/mint/total')
  }
}

// 销毁相关 API
export const burnAPI = {
  redeem(amount) {
    return request.post('/burn/redeem', { amount })
  },
  adminBurn(userId, amount) {
    return request.post('/burn/admin', { user_id: userId, amount })
  },
  getBurnedTotal() {
    return request.get('/burn/total')
  }
}

// 合约相关 API
export const contractAPI = {
  // 获取合约地址
  getContractAddress() {
    return request.get('/contract/address')
  },
  
  // 获取总供应量
  getTotalSupply() {
    return request.get('/total_supply/latest')
  },
  
  // 手动刷新总供应量
  refreshTotalSupply() {
    return request.post('/total_supply/refresh')
  }
}
