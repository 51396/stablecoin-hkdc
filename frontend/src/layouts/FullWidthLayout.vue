<template>
    <div>
      <Navbar />
      <!-- 注意：这里的 main 标签没有 class，所以它会是全宽的 -->
      <main class="full-width-main">
        <router-view />
      </main>
    </div>
  </template>
  
  <script>
  import Navbar from '@/components/Navbar.vue';
  export default {
    components: { Navbar }
  }
  </script>
  
  <style>
  .full-width-main {
    /* 只为导航栏预留空间，没有其他限制 */
    padding-top: 64px;
  }
  </style>