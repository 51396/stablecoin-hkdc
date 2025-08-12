import axios from 'axios'

const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
})

api.interceptors.request.use(config => {
  // 可在此处添加token等
  return config
})

api.interceptors.response.use(
  response => response,
  error => Promise.reject(error)
)

export default api
