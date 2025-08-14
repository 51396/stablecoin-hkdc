<template>
  <el-config-provider namespace="el">
    <div id="app">
      <Navbar />
      <main class="app-main">
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
html, body, #app { height: 100%; }
body { margin: 0; font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', sans-serif; background: #f5f7fa; }
.app-main { padding: 24px; max-width: 1200px; margin: 0 auto; }
</style>
