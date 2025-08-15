<template>
  <div class="home-container">
    <div class="main-content">
      <div class="welcome-section">
        <h1>欢迎使用 StableCoin 平台</h1>
        <p class="tagline">安全、稳定、高效的数字货币发行与交易平台</p>
        <div class="features">
          <div class="feature-card">
            <el-icon class="feature-icon"><Shield /></el-icon>
            <h3>安全保障</h3>
            <p>多重加密技术保障您的资产安全</p>
          </div>
          <div class="feature-card">
            <el-icon class="feature-icon"><RefreshRight /></el-icon>
            <h3>即时交易</h3>
            <p>快速匹配订单，实时完成交易</p>
          </div>
          <div class="feature-card">
            <el-icon class="feature-icon"><PieChart /></el-icon>
            <h3>资产管理</h3>
            <p>全面的资产视图和管理工具</p>
          </div>
          <div class="feature-card">
            <el-icon class="feature-icon"><Money /></el-icon>
            <h3>储备金管理</h3>
            <p>查看和管理稳定币的储备金资产</p>
            <el-button type="primary" @click="$router.push('/reserve-management')">访问储备金</el-button>
          </div>
          <div class="feature-card">
            <el-icon class="feature-icon"><Document /></el-icon>
            <h3>储备金证明</h3>
            <p>查看稳定币的储备金审计报告和证明</p>
            <el-button type="primary" @click="$router.push('/proof-of-reserve')">查看证明</el-button>
          </div>
        </div>
      </div>
    </div>
    <!-- <div class="login-sidebar">
      <el-card class="login-card">
        <div class="card-title">
          <el-icon><User /></el-icon>
          <span>账户登录</span>
        </div>
        <el-form :model="form" :rules="rules" ref="loginForm" label-position="top">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" clearable>
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password>
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <div class="toolbar">
            <el-button type="primary" class="w-100" @click="handleLogin">登录</el-button>
            <router-link to="/register" class="muted">还没有账号？去注册</router-link>
          </div>
        </el-form>
      </el-card>
    </div> -->
  </div>
</template>

<script>
import { User, Lock, Shield, RefreshRight, PieChart, Document, Money } from '@element-plus/icons-vue'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { userAPI } from '@/api/user'
import { ElMessage } from 'element-plus'

export default {
  name: 'Home',
  components: { User, Lock, Shield, RefreshRight, PieChart, Document, Money },
  setup() {
    const router = useRouter()
    const store = useStore()
    const form = ref({
      username: '',
      password: ''
    })
    const rules = ref({
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }]
    })

    const handleLogin = async () => {
      try {
        // 调用登录API
        const res = await userAPI.login(form.value)
        console.log('Login response:', res)
        const { access_token } = res.data
        
        // 保存token到store和localStorage
        store.commit('setToken', access_token)
        localStorage.setItem('token', access_token)
        
        // 获取用户信息
        const userRes = await userAPI.getCurrentUser()
        console.log('User info response:', userRes)
        const userData = userRes.data
        
        // 检查userData是否存在以及必要字段是否存在
        if (!userData) {
          throw new Error('用户信息获取失败')
        }
        
        if (userData.user_id === undefined || userData.username === undefined || userData.role === undefined) {
          console.error('User data missing required fields:', userData)
          throw new Error('用户信息不完整')
        }
        
        // 从响应数据中提取用户信息并存储
        const user = {
          id: userData.user_id,
          username: userData.username,
          role: userData.role
        }
        store.commit('setUser', user)
        
        // 登录成功后统一跳转到驾驶舱页面
        router.push('/dashboard')
        
        ElMessage.success('登录成功')
      } catch (err) {
        console.error('Login error:', err)
        ElMessage.error(err.response?.data?.detail || err.message || '登录失败')
      }
    }

    return { form, rules, handleLogin }
  }
}
</script>

<style scoped>
.home-container {
  display: flex;
  min-height: calc(100vh - 64px);
  padding: 20px;
}

.main-content {
  flex: 1;
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.welcome-section h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #303133;
}

.tagline {
  font-size: 1.2rem;
  color: #606266;
  margin-bottom: 3rem;
}

.features {
  display: flex;
  gap: 20px;
  margin-top: 2rem;
}

.feature-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
  flex: 1;
  transition: transform 0.3s ease;
  border: 1px solid #ebeef5;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  color: #409eff;
  margin-bottom: 10px;
  font-size: 24px;
}

.login-sidebar {
  width: 350px;
  padding: 40px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  width: 100%;
  background: #ffffff;
  border-color: #ebeef5;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-title {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  color: #303133;
  font-size: 1.2rem;
  gap: 8px;
}

.toolbar {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.muted {
  color: #86909c;
  text-align: center;
  font-size: 0.9rem;
  text-decoration: none;
}

@media (max-width: 768px) {
  .home-container {
    flex-direction: column;
  }
  .login-sidebar {
    width: 100%;
    padding: 20px;
  }
}
</style>