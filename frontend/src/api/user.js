import api from './index'

// 用户相关 API
export const userAPI = {
  // 用户登录
  login(data) {
    // 使用表单数据格式发送登录请求
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);
    return api.post('/user/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
  },
  
  // 用户注册
  register(data) {
    return api.post('/user/register', data)
  },
  
  // 获取当前用户信息
  getCurrentUser() {
    return api.get('/user/me')
  },
  
  // 用户登出
  logout() {
    return api.post('/user/logout')
  }
}

export default userAPI