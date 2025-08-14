import { createStore } from 'vuex'
import wallet from './modules/wallet'
import issuer from './modules/issuer'

const store = createStore({
  state: {
    user: null,
    token: null,
  },
  mutations: {
    setUser(state, user) { state.user = user },
    setToken(state, token) { state.token = token },
    logout(state) { 
      state.user = null; 
      state.token = null;
      // 清理Provider实例
      import('@/utils/provider').then(({ clearProvider }) => {
        clearProvider();
      });
      // 移除钱包事件监听器
      this.dispatch('wallet/removeEventListeners');
    }
  },
  actions: {},
  modules: {
    wallet,
    issuer
  }
})

export default store
