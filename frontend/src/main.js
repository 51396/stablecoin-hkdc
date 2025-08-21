import { createApp } from 'vue'
import App from './App.vue'
import { getToken } from '@/utils/auth'
import { userAPI } from '@/api/user'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './assets/styles.css'

import AppTable from './components/AppTable.vue'
const app = createApp(App)

// 应用初始化时检查用户登录状态
async function initApp() {
  const token = getToken()
  if (token) {
    try {
      const { data } = await userAPI.getCurrentUser()
      store.commit('setUser', data)
      store.commit('setToken', token)
      
      // 检查MetaMask连接状态
      await store.dispatch('wallet/checkConnection')
      
      // 如果是发行方，初始化发行方状态
      if (data.role === 'issuer') {
        await store.dispatch('issuer/initIssuer', data.contractAddress)
      }
    } catch (error) {
      console.error('初始化用户信息失败:', error)
      // 令牌无效或过期，清除本地存储
      store.commit('logout')
    }
  } else {
    // 即使没有登录，也检查MetaMask连接状态
    await store.dispatch('wallet/checkConnection')
  }
}

// 执行初始化
initApp()

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.component('app-table',AppTable)

app
  .use(router)
  .use(store)
  .use(ElementPlus)
  .mount('#app')
