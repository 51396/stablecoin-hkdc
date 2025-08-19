import api from './index'

// 托管机构管理相关 API
export const custodiansAPI = {
  // 获取托管机构数据
  getCustodiansAPIData() {
    return api.get('/custodians/')
  },
  saveCustodian(data){
    return api.post("/custodians/",data)
  }
}

export default custodiansAPI