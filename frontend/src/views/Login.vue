<template>
  <div class="page">
    <el-row justify="center">
      <el-col :xs="24" :sm="18" :md="12" :lg="8">
        <el-card class="card">
          <div class="card-title">
            <el-icon><User /></el-icon>
            <span>登录</span>
          </div>
          <el-form :model="form" label-position="top">
            <el-form-item label="用户名">
              <el-input v-model="form.username" placeholder="请输入用户名" clearable>
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password>
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <div class="toolbar">
              <el-button type="primary" class="w-100">登录</el-button>
              <router-link to="/register" class="muted">还没有账号？去注册</router-link>
            </div>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
  
</template>
<script>
import { User, Lock } from '@element-plus/icons-vue'
export default {
  name: 'Login',
  components: { User, Lock },
  data() {
    return { form: { username: '', password: '' } }
  }
}
</script>
