import api from './index'

// 地址管理相关 API
export const institutionalAccountAPI = {
  createInstitutionalAccount(data) {
        return api.post(`/institutional-accounts/`, data)
      },
  getInstitutionalAccounts() {
      return api.get(`/institutional-accounts/`)
  },
  bindAddress(account_id,payload){
    return api.post(`/institutional-accounts/${account_id}/addresses`,payload)
  }
}


export default institutionalAccountAPI