import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Wallet from '../views/Wallet.vue'
import Trade from '../views/Trade.vue'
import Transactions from '../views/Transactions.vue'
import Whitelist from '../views/Whitelist.vue'
import Dashboard from '../views/Dashboard.vue'

const IssuerConsole = () => import('../views/IssuerConsole.vue')
const AdminConsole = () => import('../views/Admin.vue')
const ContractConfig = () => import('../views/ContractConfig.vue')
const AddressManagement = () => import('../views/AddressManagement.vue')
const ReserveManagement = () => import('../views/ReserveManagement.vue')
const ReserveAdmin = () => import('../views/ReserveAdmin.vue')

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/wallet', component: Wallet },
  { path: '/trade', component: Trade },
  { path: '/transactions', component: Transactions },
  { path: '/whitelist', component: Whitelist },
  { path: '/dashboard', component: Dashboard },
  { path: '/issuer', component: IssuerConsole },
  { path: '/admin', component: AdminConsole },
  { path: '/contract-config', component: ContractConfig },
  { path: '/address-management', component: AddressManagement },
  { path: '/reserve-management', component: ReserveManagement },
  { path: '/reserve-admin', component: ReserveAdmin },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 添加导航守卫
router.beforeEach((to, from, next) => {
  // 获取令牌
  const token = localStorage.getItem('token')
  
  // 定义不需要认证的页面
  const publicPages = ['/login', '/register']
  const authRequired = !publicPages.includes(to.path)
  
  // 如果访问需要认证的页面但没有令牌，重定向到登录页
  if (authRequired && !token) {
    return next('/login')
  }
  
  // 如果已登录且访问登录页，重定向到驾驶舱页
  if (token && to.path === '/login') {
    return next('/dashboard')
  }
  
  next()
})

export default router
