import api from './index'

// 钱包相关 API
export const walletAPI = {
  // 获取用户钱包信息
  getUserWallet(userId) {
    return api.get(`/wallet/${userId}`)
  },
  
  // 充值
  deposit({ user_id, amount }) {
    return api.post('/wallet/deposit', null, { params: { user_id, amount } })
  },
  
  // 提币
  withdraw({ user_id, amount }) {
    return api.post('/wallet/withdraw', null, { params: { user_id, amount } })
  },
  
  // 获取交易记录
  getTransactions(userId) {
    return api.get(`/trade/records/${userId}`)
  },
  
  // 获取钱包资产列表
  getWalletAssets(userId) {
    return api.get(`/wallet/${userId}/assets`)
  }
}

// 交易相关 API
export const tradeAPI = {
  // 买入
  buy(data) {
    return api.post('/trade/buy', data)
  },
  
  // 卖出
  sell(data) {
    return api.post('/trade/sell', data)
  },
  
  // 获取交易历史
  getTradeHistory(userId) {
    return api.get(`/trade/records/${userId}`)
  }
}

// 白名单相关 API
export const whitelistAPI = {
  // 获取白名单
  getWhitelist() {
    return api.get('/whitelist')
  },
  
  // 添加到白名单
  addToWhitelist(userId) {
    return api.post('/whitelist/add', null, { params: { user_id: userId } })
  },
  
  // 从白名单移除
  removeFromWhitelist(userId) {
    return api.post('/whitelist/remove', null, { params: { user_id: userId } })
  }
}
