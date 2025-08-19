<template>
  <el-config-provider namespace="el">
    <div id="app">
      <Navbar />
      <main class="main-container">
        <router-view />
      </main>
    </div>
  </el-config-provider>
  
</template>

<script>
import Navbar from './components/Navbar.vue'
export default {
  name: 'App',
  components: { Navbar }
}
</script>

<style>
/* 1. 基础样式，确保全高和统一样式 */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}

body {
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
  /* 我们将背景色交给具体页面控制，这里保持一个中性色或移除 */
  background-color: #f7f8fa; 
}


/* App.vue (修改后的样式) */
.main-container {
  /* 
    ======================================================
    关键改动：将 padding-top 分为两部分思考
    ======================================================
    1. 导航栏的高度：64px
    2. 我们希望的额外间距：例如 24px (您可以调整这个值)
    
    总 padding-top = 64px + 24px = 88px
    
    我们将这个值直接设置在这里，作为全局规则。
  */
  padding-top: 64px; 
  
  padding-left: 65px;
  padding-right: 65px;
  padding-bottom: 32px; /* 同时也给底部留出空间 */
  
  width: 100%;
  min-height: 100vh;
  box-sizing: border-box; 
}

@media (max-width: 768px) {
  .main-container {
    padding-top: 72px; /* 64px + 8px */
    padding-left: 16px;
    padding-right: 16px;
    padding-bottom: 16px;
  }
}

/* 3. (可选) 如果你还想保留中心化布局给某些页面使用 */
/* 你可以在这个全局样式中，再定义一个 .centered-content 类 */
.centered-content {
    max-width: 1200px;
    margin: 0 auto;
    padding-left: 24px;
    padding-right: 24px;
}
/* 正常状态 */
:deep(.details-button.el-button--primary.is-plain) {
  --el-button-text-color: #fcfcfc;   /* 文字颜色 */
  --el-button-border-color: #4598f7; /* 边框颜色 */
  --el-button-bg-color: #21acec;     /* 背景颜色 */
}

</style>