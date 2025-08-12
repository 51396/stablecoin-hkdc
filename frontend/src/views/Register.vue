<template>
  <div class="page">
    <el-row justify="center">
      <el-col :xs="24" :sm="18" :md="12" :lg="8">
        <el-card class="card">
          <div class="card-title">
            <el-icon><UserFilled /></el-icon>
            <span>注册</span>
          </div>
          <el-form :model="form" label-position="top">
            <el-form-item label="用户名">
              <el-input v-model="form.username" placeholder="请输入用户名" clearable>
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="form.email" placeholder="请输入邮箱" clearable>
                <template #prefix>
                  <el-icon><Message /></el-icon>
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
            <el-form-item label="确认密码">
              <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" show-password>
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <div class="toolbar">
              <el-button type="primary" class="w-100">注册</el-button>
              <router-link to="/login" class="muted">已有账号？去登录</router-link>
            </div>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { User, UserFilled, Message, Lock } from '@element-plus/icons-vue'
export default {
  name: 'Register',
  components: { User, UserFilled, Message, Lock },
  data() {
    return { 
      form: { 
        username: '', 
        email: '', 
        password: '', 
        confirmPassword: '' 
      } 
    }
  }
}
</script>
