<template>
  <!-- 1. header 标签现在有了一个 class，并使用 el-header 来获得标准高度 -->
  <el-header class="app-header">
    <div class="header-container">
      
      <!-- Logo 和品牌名称 -->
      <div class="brand-container">
        <router-link to="/" class="brand-link">
          <img src="/logo.svg" alt="StableCoin Logo" class="brand-logo" />
          <span class="brand-name">StableCoin</span>
        </router-link>
      </div>

      <!-- 导航菜单 -->
      <nav class="navigation-menu">
        <!-- 
          el-menu 现在有了新的class，并移除了内联样式，
          所有样式都通过 <style> 块控制
        -->
        <el-menu
          mode="horizontal"
          :ellipsis="false"
          :default-active="$route.path"
          router
          class="main-menu"
        >
          <!-- 菜单项保持不变，新的CSS会自动美化它们 -->
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          
          <!-- 用户菜单 -->
          <template v-if="isLoggedIn && userRole !== 'admin'">
             <!-- ... 您的菜单项 ... -->
          </template>
          
          <template v-if="isLoggedIn && userRole === 'admin'">
        <el-menu-item index="/issuer">
          <el-icon><Coin /></el-icon>
          <span>稳定币管理</span>
        </el-menu-item>
        <el-menu-item index="/address-management">
          <el-icon><List /></el-icon>
          <span>地址管理</span>
        </el-menu-item>
        <!-- <el-menu-item index="/contract-config">
          <el-icon><Setting /></el-icon>
          <span>合约配置</span>
        </el-menu-item> -->
        <el-menu-item index="/reserve-management">
          <el-icon><Coin /></el-icon>
          <span>储备金管理</span>
        </el-menu-item>
        <el-menu-item index="/transactions">
          <el-icon><List /></el-icon>
          <span>交易记录</span>
        </el-menu-item>
      </template>
          
          <!-- 用户认证下拉菜单 -->
          <div class="user-menu-wrapper">
            <el-sub-menu index="auth" v-if="!isLoggedIn">
              <template #title>
                <el-avatar :size="32" icon="el-icon-user-solid"></el-avatar>
                <span class="user-name-guest">未登录</span>
              </template>
              <el-menu-item index="/login">
                <el-icon><Key /></el-icon>登录
              </el-menu-item>
              <el-menu-item index="/register">
                <el-icon><MagicStick /></el-icon>注册
              </el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="user" v-else>
              <template #title>
                <el-avatar :size="32" :src="userAvatarUrl" icon="el-icon-user-solid"></el-avatar>
                <span class="user-name">{{ userName }}</span>
              </template>
              <el-menu-item @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                <span>退出登录</span>
              </el-menu-item>
            </el-sub-menu>
          </div>

        </el-menu>
      </nav>

      <!-- 移动端汉堡菜单按钮 (待实现) -->
      <div class="mobile-menu-button">
        <el-icon><Menu /></el-icon>
      </div>

    </div>
  </el-header>
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
      console.log(123)
      this.$store.commit('logout')
      console.log(456)
      this.$router.push('/login')
    }
  }
}
</script>
<style scoped>
/* ----- 1. 头部容器 ----- */
.app-header {
  /* 固定在顶部 */
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  
  /* 外观 */
  background-color: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  
  /* 内部布局 */
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 64px; /* 标准导航栏高度 */
}

.header-container {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* ----- 2. 品牌Logo区域 ----- */
.brand-container {
  display: flex;
  align-items: center;
}
.brand-link {
  display: flex;
  align-items: center;
  text-decoration: none;
}
.brand-logo {
  height: 32px;
  width: 32px;
  margin-right: 12px;
}
.brand-name {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

/* ----- 3. 导航菜单 ----- */
.navigation-menu {
  flex-grow: 1; /* 占据剩余空间 */
  display: flex;
  justify-content: flex-end; /* 菜单项靠右 */
}
/* 深度修改 el-menu 样式 */
.main-menu {
  /* 移除 el-menu 默认的边框和背景 */
  border-bottom: none !important;
  background-color: transparent !important;
  height: 64px; /* 与 header 高度一致 */
}

::v-deep(.el-menu-item),
::v-deep(.el-sub-menu__title) {
  height: 64px;
  line-height: 64px;
  font-size: 15px;
  font-weight: 500;
  color: #606266 !important;
  border-bottom: 2px solid transparent !important; /* 隐藏默认下划线 */
  transition: all 0.2s ease-in-out;
}
/* 激活状态和悬停效果 */
::v-deep(.el-menu-item:hover),
::v-deep(.el-sub-menu__title:hover) {
  background-color: #f5f7fa !important;
  color: #409EFF !important;
}

::v-deep(.el-menu-item.is-active) {
  color: #409EFF !important;
  border-bottom-color: #409EFF !important; /* 使用底部边框作为激活指示器 */
}
/* 移除 el-menu 最后一项的右边距 (如果有) */
::v-deep(.el-menu--horizontal>.el-menu-item:not(.is-disabled):last-child) {
    margin-right: 0;
}
::v-deep(.el-menu--horizontal>.el-sub-menu:last-child .el-sub-menu__title) {
    margin-right: 0;
}


/* ----- 4. 用户菜单 ----- */
.user-menu-wrapper {
  margin-left: 20px; /* 与其他菜单项拉开距离 */
}
.user-name {
  margin-left: 10px;
}
.user-name-guest {
  margin-left: 10px;
  color: #909399;
}

/* ----- 5. 移动端响应式 (基本) ----- */
.mobile-menu-button {
  display: none; /* 默认隐藏 */
  font-size: 24px;
  cursor: pointer;
}

@media (max-width: 992px) { /* 在中等屏幕及以下尺寸 */
  .navigation-menu {
    display: none; /* 隐藏主导航 */
  }
  .mobile-menu-button {
    display: block; /* 显示汉堡按钮 */
  }
}
</style>