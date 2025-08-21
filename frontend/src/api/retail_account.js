import api from './index'

// 地址管理相关 API
export const retailAccountAPI = {
    getAddressesByLabel(label, params) {
        return api.get(`/addresses/label/${label}`, { params })
      }
}


export default retailAccountAPI