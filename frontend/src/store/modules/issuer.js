const state = {
  contractAddress: '',
  isIssuer: false,
  decimals: 6,
  ownerAddress: ''
}

const mutations = {
  SET_CONTRACT_ADDRESS(state, addr) { state.contractAddress = addr },
  SET_IS_ISSUER(state, v) { state.isIssuer = v },
  SET_DECIMALS(state, d) { state.decimals = d },
  SET_OWNER_ADDRESS(state, a) { state.ownerAddress = a }
}

const actions = {
  async initIssuer({ commit, rootGetters }, contractAddress) {
    commit('SET_CONTRACT_ADDRESS', contractAddress)
    try {
      const { isOwner, fetchOwnerAddress } = await import('@/utils/contract')
      const currentAddress = rootGetters['wallet/walletAddress']
      const ok = await isOwner(contractAddress, currentAddress)
      const owner = await fetchOwnerAddress(contractAddress)
      commit('SET_OWNER_ADDRESS', owner)
      commit('SET_IS_ISSUER', ok)
      return ok
    } catch (e) {
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
  async setWhitelist({ state }, enabled) {
    const { setWhitelistOnChain } = await import('@/utils/contract')
    return setWhitelistOnChain(state.contractAddress, enabled)
  },
  async addToWhitelist({ state }, account) {
    const { addToWhitelistOnChain } = await import('@/utils/contract')
    return addToWhitelistOnChain(state.contractAddress, account)
  },
  async removeFromWhitelist({ state }, account) {
    const { removeFromWhitelistOnChain } = await import('@/utils/contract')
    return removeFromWhitelistOnChain(state.contractAddress, account)
  }
}

const getters = {
  isIssuer: s => s.isIssuer,
  contractAddress: s => s.contractAddress,
  ownerAddress: s => s.ownerAddress,
  decimals: s => s.decimals
}

export default { namespaced: true, state, mutations, actions, getters }