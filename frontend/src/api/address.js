import api from './index'

// 地址管理相关 API
export const addressAPI = {
  // 创建地址记录
  createAddress(data) {
    return api.post('/addresses/', data)
  },

  // 根据ID获取地址记录
  getAddressById(id) {
    return api.get(`/addresses/${id}`)
  },

  // 获取所有地址记录
  getAllAddresses(params) {
    return api.get('/addresses/', { params }).then(response => {
      // 确保返回的数据格式正确
      return {
        ...response,
        data: Array.isArray(response.data) ? response.data : []
      }
    })
  },

  // 更新地址记录
  updateAddress(id, data) {
    return api.put(`/addresses/${id}`, data)
  },

  // 删除地址记录
  deleteAddress(id) {
    return api.delete(`/addresses/${id}`)
  },

  // 获取白名单地址
  getWhitelistedAddresses(params) {
    return api.get('/addresses/whitelist', { params }).then(response => {
      // 确保返回的数据格式正确
      return {
        ...response,
        data: Array.isArray(response.data) ? response.data : []
      }
    })
  },

  // 获取黑名单地址
  getBlacklistedAddresses(params) {
    return api.get('/addresses/blacklist', { params }).then(response => {
      // 确保返回的数据格式正确
      return {
        ...response,
        data: Array.isArray(response.data) ? response.data : []
      }
    })
  },

  // 检查地址状态
  checkAddressStatus(address) {
    return api.get(`/addresses/check/${address}`)
  },

  // 根据标签获取地址
  getAddressesByLabel(label, params) {
    return api.get(`/addresses/label/${label}`, { params })
  }
}

export default addressAPI