<template>
  <header class="app-header">
    <div class="container">
      <div class="brand">
        <el-icon size="20" class="brand-icon"><Coin /></el-icon>
        <span class="brand-name">StableCoin</span>
      </div>

      <nav class="nav">
        <el-menu
          mode="horizontal"
          :ellipsis="false"
          background-color="#f5f7fa"
          text-color="#303133"
          active-text-color="#409eff"
          :default-active="$route.path"
          router
        >
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <template v-if="isLoggedIn && userRole !== 'admin'">
            <el-menu-item index="/wallet">
              <el-icon><Wallet /></el-icon>
              <span>钱包</span>
            </el-menu-item>
            <el-menu-item index="/trade">
              <el-icon><ShoppingCart /></el-icon>
              <span>交易</span>
            </el-menu-item>
            
          </template>
          <template v-if="isLoggedIn && userRole === 'admin'">
            <el-menu-item index="/issuer">
              <el-icon><Coin /></el-icon>
              <span>稳定币管理</span>
            </el-menu-item>
            <el-menu-item index="/whitelist">
              <el-icon><UserFilled /></el-icon>
              <span>白名单</span>
            </el-menu-item>
            <el-menu-item index="/address-management">
              <el-icon><List /></el-icon>
              <span>地址管理</span>
            </el-menu-item>
            <el-menu-item index="/contract-config">
              <el-icon><Setting /></el-icon>
              <span>合约配置</span>
            </el-menu-item>
            <el-menu-item index="/reserve-management">
              <el-icon><Coin /></el-icon>
              <span>储备金管理</span>
            </el-menu-item>
            <el-menu-item index="/transactions">
              <el-icon><List /></el-icon>
              <span>交易记录</span>
            </el-menu-item>
          </template>
          <el-sub-menu index="auth" v-if="!isLoggedIn">
            <template #title>
              <el-icon><User /></el-icon>
              <span>账户</span>
            </template>
            <el-menu-item index="/login">登录</el-menu-item>
            <el-menu-item index="/register">注册</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="user" v-else>
            <template #title>
              <el-icon><User /></el-icon>
              <span>{{ userName }}</span>
            </template>
            <el-menu-item @click="handleLogout">
              <el-icon><Logout /></el-icon>
              <span>退出登录</span>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </nav>
    </div>
  </header>
</template>

<script>
import { Coin, Wallet, ShoppingCart, List, User, UserFilled, Logout, Setting, House } from '@element-plus/icons-vue'
import { mapGetters } from 'vuex'
import { useRouter } from 'vue-router'
export default {
  name: 'Navbar',
  components: { Coin, Wallet, ShoppingCart, List, User, UserFilled, Logout, Setting, House },
  computed: {
    isLoggedIn() {
      return !!this.$store.state.user
    },
    userName() {
      return this.$store.state.user?.username || '用户'
    },
    userRole() {
      return this.$store.state.user?.role || ''
    }
  },
  methods: {
    handleLogout() {
      this.$store.commit('logout')
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: saturate(180%) blur(10px);
  background: rgba(245, 247, 250, 0.75);
  border-bottom: 1px solid #ebeef5;
}
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand { display: flex; align-items: center; gap: 12px; color: #303133; font-size: 18px; }
.brand-name { font-weight: 700; letter-spacing: 0.4px; }
.brand-icon { color: #409eff; font-size: 24px; }
.nav :deep(.el-menu) { border-bottom: none; }
.nav :deep(.el-menu--horizontal > .el-menu-item) { height: 50px; line-height: 50px; font-size: 16px; }
.nav :deep(.el-sub-menu .el-sub-menu__title) { height: 50px; line-height: 50px; font-size: 16px; }
</style>
