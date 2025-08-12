import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Wallet from '../views/Wallet.vue'
import Trade from '../views/Trade.vue'
import Transactions from '../views/Transactions.vue'
import Whitelist from '../views/Whitelist.vue'

const IssuerConsole = () => import('../views/IssuerConsole.vue')

const routes = [
  { path: '/', redirect: '/wallet' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/wallet', component: Wallet },
  { path: '/trade', component: Trade },
  { path: '/transactions', component: Transactions },
  { path: '/whitelist', component: Whitelist },
  { path: '/issuer', component: IssuerConsole },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
