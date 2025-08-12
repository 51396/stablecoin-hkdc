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
    logout(state) { state.user = null; state.token = null }
  },
  actions: {},
  modules: {
    wallet,
    issuer
  }
})

export default store
