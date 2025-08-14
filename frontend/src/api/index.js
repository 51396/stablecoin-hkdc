import axios from 'axios'

const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
})

import { getToken } from '@/utils/auth'

api.interceptors.request.use(config => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

import { ElMessage } from 'element-plus'
import store from '@/store'
import router from '@/router'
import { removeToken } from '@/utils/auth'

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // 处理未授权错误
      store.commit('logout')
      removeToken()
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(error.response?.data?.message || '操作失败，请重试')
    }
    return Promise.reject(error)
  }
)

export default api
