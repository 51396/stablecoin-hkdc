const state = {
  contractAddress: '',
  isIssuer: false,
  decimals: 6,
  ownerAddress: '',
  whitelistEnabled: false,
  whitelist: [],
  totalSupply: '0',
  mintedAmount: '0',
  burnedAmount: '0'
}

const mutations = {
  SET_CONTRACT_ADDRESS(state, addr) { state.contractAddress = addr },
  SET_IS_ISSUER(state, v) { state.isIssuer = v },
  SET_DECIMALS(state, d) { state.decimals = d },
  SET_OWNER_ADDRESS(state, a) { state.ownerAddress = a },
  SET_WHITELIST_ENABLED(state, enabled) { state.whitelistEnabled = enabled },
  SET_WHITELIST(state, list) { state.whitelist = list },
  SET_TOTAL_SUPPLY(state, supply) { state.totalSupply = supply },
  SET_MINTED_AMOUNT(state, amount) { state.mintedAmount = amount },
  SET_BURNED_AMOUNT(state, amount) { state.burnedAmount = amount }
}

const actions = {
  async initIssuer({ commit, rootGetters }) {
    try {
      // 首先从后端获取合约地址
      const { contractAPI } = await import('@/api/wallet')
      const response = await contractAPI.getContractAddress()
      const contractAddress = response.data.contract_address
      commit('SET_CONTRACT_ADDRESS', contractAddress)
      
      // 检查钱包是否已连接
      if (!rootGetters['wallet/isConnected']) {
        throw new Error('钱包未连接')
      }
      const { isOwner, fetchOwnerAddress } = await import('@/utils/contract')
      // 此代码用于从 rootGetters 中获取当前钱包地址
      // 调用的 rootGetters['wallet/walletAddress'] 方法实现应位于 wallet 模块的 getters 中
      const currentAddress = rootGetters['wallet/walletAddress']
      if (!currentAddress) {
        throw new Error('无法获取钱包地址')
      }

      const ok = await isOwner(contractAddress, currentAddress)
      console.log(ok,currentAddress)
      const owner = await fetchOwnerAddress(contractAddress)
      commit('SET_OWNER_ADDRESS', owner)
      commit('SET_IS_ISSUER', ok)
      
      // 获取初始数据
      if (ok) {
        await this.dispatch('issuer/fetchTotalSupply')
        await this.dispatch('issuer/fetchMintedAmount')
        await this.dispatch('issuer/fetchBurnedAmount')
        await this.dispatch('issuer/checkWhitelistEnabled')
      }
      
      return ok
    } catch (e) {
      console.error('初始化发行方失败:', e)
      commit('SET_IS_ISSUER', false)
      return false
    }
  },
  async mint({ state }, { to, amount }) {
    const { mintHKDC } = await import('@/utils/contract')
    return mintHKDC(state.contractAddress, to, amount, state.decimals)
  },
  async burn({ state }, { from, amount }) {
    const { burnHKDC } = await import('@/utils/contract')
    return burnHKDC(state.contractAddress, from, amount, state.decimals)
  },
  async setWhitelist({ commit }, enabled) {
    try {
      const { whitelistAPI } = await import('@/api/wallet')
      // 这里需要根据后端API的具体实现来调整
      // 假设后端提供了一个API来设置白名单状态
      const response = await whitelistAPI.setWhitelistStatus(enabled)
      commit('SET_WHITELIST_ENABLED', enabled)
      return response
    } catch (e) {
      console.error('设置白名单状态失败:', e)
      throw e
    }
  },
  async addToWhitelist({ commit }, account) {
    try {
      const { whitelistAPI } = await import('@/api/wallet')
      const response = await whitelistAPI.addToWhitelist(account)
      // 更新本地白名单列表
      const currentWhitelist = [...this.state.whitelist]
      if (!currentWhitelist.includes(account)) {
        currentWhitelist.push(account)
        commit('SET_WHITELIST', currentWhitelist)
      }
      return response
    } catch (e) {
      console.error('添加到白名单失败:', e)
      throw e
    }
  },
  async removeFromWhitelist({ commit }, account) {
    try {
      const { whitelistAPI } = await import('@/api/wallet')
      const response = await whitelistAPI.removeFromWhitelist(account)
      // 更新本地白名单列表
      const currentWhitelist = [...this.state.whitelist]
      const index = currentWhitelist.indexOf(account)
      if (index > -1) {
        currentWhitelist.splice(index, 1)
        commit('SET_WHITELIST', currentWhitelist)
      }
      return response
    } catch (e) {
      console.error('从白名单移除失败:', e)
      throw e
    }
  },
  async checkWhitelistEnabled({ commit }) {
    try {
      const { whitelistAPI } = await import('@/api/wallet')
      const response = await whitelistAPI.getWhitelistStatus()
      const enabled = response.data.enabled || false
      commit('SET_WHITELIST_ENABLED', enabled)
      return enabled
    } catch (e) {
      console.error('检查白名单状态失败:', e)
      return false
    }
  },
  async checkWhitelistStatus({ commit }, account) {
    try {
      const { whitelistAPI } = await import('@/api/wallet')
      const response = await whitelistAPI.getWhitelist()
      const whitelist = response.data || []
      const isWhitelisted = whitelist.includes(account)
      return isWhitelisted
    } catch (e) {
      console.error('检查账户白名单状态失败:', e)
      return false
    }
  },
  async fetchTotalSupply({ commit, state }) {
    try {
      const { contractAPI } = await import('@/api/wallet')
      const response = await contractAPI.getTotalSupply()
      const totalSupply = response.data.total_supply
      commit('SET_TOTAL_SUPPLY', totalSupply)
      return totalSupply
    } catch (e) {
      console.error('获取代币总供应量失败:', e)
      return '0'
    }
  },
  async fetchMintedAmount({ commit }) {
    try {
      const { mintAPI } = await import('@/api/wallet')
      const response = await mintAPI.getMintedTotal()
      const amount = response.data.total || '0'
      commit('SET_MINTED_AMOUNT', amount)
      return amount
    } catch (e) {
      console.error('获取已铸造数量失败:', e)
      return '0'
    }
  },
  async fetchBurnedAmount({ commit }) {
    try {
      const { burnAPI } = await import('@/api/wallet')
      const response = await burnAPI.getBurnedTotal()
      const amount = response.data.total || '0'
      commit('SET_BURNED_AMOUNT', amount)
      return amount
    } catch (e) {
      console.error('获取已销毁数量失败:', e)
      return '0'
    }
  }
}

const getters = {
  isIssuer: s => s.isIssuer,
  contractAddress: s => s.contractAddress,
  ownerAddress: s => s.ownerAddress,
  decimals: s => s.decimals,
  whitelist: s => s.whitelist,
  whitelistEnabled: s => s.whitelistEnabled,
  totalSupply: s => s.totalSupply,
  mintedAmount: s => s.mintedAmount,
  burnedAmount: s => s.burnedAmount
}

export default { namespaced: true, state, mutations, actions, getters }
