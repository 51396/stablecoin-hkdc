<template>
    <div>
      <Navbar />
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </template>
  
  <script>
  import Navbar from '@/components/Navbar.vue'; // 确保路径正确
  export default {
    components: { Navbar }
  }
  </script>
  
  <style>
  /* 这里是你 App.vue 中原来的 .app-main 样式 */
  .app-main {
    padding-top: 88px; /* 64px 导航栏 + 24px 间距 */
    max-width: 1200px;
    margin: 0 auto;
    padding-left: 24px;
    padding-right: 24px;
    padding-bottom: 24px;
  }
  </style>