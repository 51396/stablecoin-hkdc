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
          background-color="#0b1220"
          text-color="#c9d4f1"
          active-text-color="#e6a23c"
          :default-active="$route.path"
          router
        >
          <el-menu-item index="/wallet">
            <el-icon><Wallet /></el-icon>
            <span>钱包</span>
          </el-menu-item>
          <el-menu-item index="/trade">
            <el-icon><ShoppingCart /></el-icon>
            <span>交易</span>
          </el-menu-item>
          <el-menu-item index="/transactions">
            <el-icon><List /></el-icon>
            <span>交易记录</span>
          </el-menu-item>
          <el-menu-item index="/whitelist">
            <el-icon><UserFilled /></el-icon>
            <span>白名单</span>
          </el-menu-item>
          <el-sub-menu index="auth">
            <template #title>
              <el-icon><User /></el-icon>
              <span>账户</span>
            </template>
            <el-menu-item index="/login">登录</el-menu-item>
            <el-menu-item index="/register">注册</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </nav>
    </div>
  </header>
</template>

<script>
import { Coin, Wallet, ShoppingCart, List, User, UserFilled } from '@element-plus/icons-vue'
export default {
  name: 'Navbar',
  components: { Coin, Wallet, ShoppingCart, List, User, UserFilled }
}
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: saturate(180%) blur(10px);
  background: rgba(11, 18, 32, 0.75);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand { display: flex; align-items: center; gap: 10px; color: #e8eefc; }
.brand-name { font-weight: 700; letter-spacing: 0.4px; }
.brand-icon { color: #e6a23c; }
.nav :deep(.el-menu) { border-bottom: none; }
</style>
