import api from './index'

// 储备金管理相关 API
export const reserveAPI = {
  // 获取储备金数据
  getReserveData() {
    return api.get('/reserves/')
  },
  // 获取所有资产列表
  getAllAssets() {
    return api.get('/reserves/manage/assets')
  },
  // 调整资产数量
  adjustAssetBalance(transactionData) {
    return api.post('/reserves/manage/transactions', transactionData)
  },
  // 录入新资产
  createNewAsset(assetData) {
    return api.post('/reserves/manage/assets', assetData)
  },
  // 删除资产
  deleteAsset(assetId) {
    return api.delete(`/reserves/manage/assets/${assetId}`)
  },
  // 更新资产
  updateAsset(assetId, assetData) {
    return api.put(`/reserves/manage/assets/${assetId}`, assetData)
  },
  // 获取核心指标
  getCoreMetrics() {
    return api.get('/reserves/metrics')
  },
  createAssetAccount(data){
    return api.post("/reserves/account",data)
  },
  getAssetAccounts(data){
    return api.get("/reserves/accounts",data)
  }
}

export default reserveAPI