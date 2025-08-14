import { 
  connectMetaMask, 
  getCurrentAccount, 
  getNetworkInfo,
  getAccountBalance,
  getGasPrice,
  getBlockNumber,
  getBlockInfo,
  getTokenBalance,
  getTokenInfo,
  switchNetwork,
  onAccountsChanged,
  onChainChanged,
  removeListeners
} from '@/utils/metamask'
import { walletAPI } from '@/api/wallet'

const state = {
  connected: false,
  connecting: false,
  address: '',
  balance: 0,
  network: {
    chainId: '0x0',
    name: 'Unknown',
    symbol: 'Unknown',
    explorer: '',
    decimals: 18
  },
  error: null,
  isUpdating: false, // 防止重复更新
  
  // 新增状态
  gasPrice: null,
  blockNumber: null,
  blockInfo: null,
  tokens: [], // 代币列表
  isUpdatingGas: false,
  isUpdatingBlock: false
}

const mutations = {
  SET_CONNECTED(state, connected) {
    state.connected = connected
  },
  SET_CONNECTING(state, connecting) {
    state.connecting = connecting
  },
  SET_ADDRESS(state, address) {
    state.address = address
  },
  SET_BALANCE(state, balance) {
    state.balance = balance
  },
  SET_NETWORK(state, network) {
    state.network = network
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  SET_UPDATING(state, isUpdating) {
    state.isUpdating = isUpdating
  },
  SET_GAS_PRICE(state, gasPrice) {
    state.gasPrice = gasPrice
  },
  SET_BLOCK_NUMBER(state, blockNumber) {
    state.blockNumber = blockNumber
  },
  SET_BLOCK_INFO(state, blockInfo) {
    state.blockInfo = blockInfo
  },
  SET_TOKENS(state, tokens) {
    state.tokens = tokens
  },
  SET_UPDATING_GAS(state, isUpdating) {
    state.isUpdatingGas = isUpdating
  },
  SET_UPDATING_BLOCK(state, isUpdating) {
    state.isUpdatingBlock = isUpdating
  },
  CLEAR_WALLET(state) {
    state.connected = false
    state.address = ''
    state.balance = 0
    state.network = { chainId: '0x0', name: 'Unknown', symbol: 'Unknown', explorer: '', decimals: 18 }
    state.error = null
    state.isUpdating = false
    state.gasPrice = null
    state.blockNumber = null
    state.blockInfo = null
    state.tokens = []
    state.isUpdatingGas = false
    state.isUpdatingBlock = false
  }
}

const actions = {
  async connectWallet({ commit, dispatch }) {
    commit('SET_CONNECTING', true)
    commit('SET_ERROR', null)
    
    try {
      const address = await connectMetaMask()
      commit('SET_ADDRESS', address)
      commit('SET_CONNECTED', true)
      
      // 获取钱包信息
      await dispatch('updateWalletInfo')
      
      // 设置事件监听器
      dispatch('setupEventListeners')
      
      return address
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_CONNECTING', false)
    }
  },
  
  async disconnectWallet({ commit, dispatch }) {
    commit('CLEAR_WALLET')
    dispatch('removeEventListeners')
    
    // 清理Provider实例
    const { clearProvider } = await import('@/utils/provider')
    clearProvider()
  },
  
  async checkConnection({ commit, dispatch }) {
    try {
      const account = await getCurrentAccount()
      if (account) {
        commit('SET_ADDRESS', account)
        commit('SET_CONNECTED', true)
        await dispatch('updateWalletInfo')
        dispatch('setupEventListeners')
        return true
      }
      return false
    } catch (error) {
      console.error('检查钱包连接失败:', error)
      return false
    }
  },
  
  async updateWalletInfo({ commit, state }) {
    if (!state.connected || state.isUpdating) return
    
    commit('SET_UPDATING', true)
    try {
      // 获取网络信息
      const network = await getNetworkInfo()
      if (network) {
        commit('SET_NETWORK', network)
      }
      
      // 获取余额
      try {
        const balance = await getAccountBalance(state.address);
        if (balance !== null) {
          commit('SET_BALANCE', balance);
        }
      } catch (error) {
        console.error('获取余额失败:', error);
        commit('SET_ERROR', error.message);
      }
    } catch (error) {
      console.error('更新钱包信息失败:', error)
      commit('SET_ERROR', error.message)
    } finally {
      commit('SET_UPDATING', false)
    }
  },
  
  // 获取 Gas 价格
  async updateGasPrice({ commit, state }) {
    if (!state.connected || state.isUpdatingGas) return
    
    commit('SET_UPDATING_GAS', true)
    try {
      const gasPrice = await getGasPrice()
      if (gasPrice !== null) {
        commit('SET_GAS_PRICE', gasPrice)
      }
    } catch (error) {
      console.error('获取 Gas 价格失败:', error)
    } finally {
      commit('SET_UPDATING_GAS', false)
    }
  },
  
  // 获取区块信息
  async updateBlockInfo({ commit, state }) {
    if (!state.connected || state.isUpdatingBlock) return
    
    commit('SET_UPDATING_BLOCK', true)
    try {
      // 获取当前区块号
      const blockNumber = await getBlockNumber()
      if (blockNumber !== null) {
        commit('SET_BLOCK_NUMBER', blockNumber)
      }
      
      // 获取最新区块信息
      const blockInfo = await getBlockInfo('latest')
      if (blockInfo) {
        commit('SET_BLOCK_INFO', blockInfo)
      }
    } catch (error) {
      console.error('获取区块信息失败:', error)
    } finally {
      commit('SET_UPDATING_BLOCK', false)
    }
  },
  
  // 获取代币余额
  async getTokenBalance({ state }, tokenAddress) {
    if (!state.connected) return null
    
    try {
      const balance = await getTokenBalance(tokenAddress, state.address)
      return balance
    } catch (error) {
      console.error('获取代币余额失败:', error)
      return null
    }
  },
  
  // 获取代币信息
  async getTokenInfo({ state }, tokenAddress) {
    if (!state.connected) return null
    
    try {
      const tokenInfo = await getTokenInfo(tokenAddress)
      return tokenInfo
    } catch (error) {
      console.error('获取代币信息失败:', error)
      return null
    }
  },
  
  // 批量更新所有信息
  async updateAllInfo({ dispatch }) {
    try {
      await Promise.all([
        dispatch('updateWalletInfo'),
        dispatch('updateGasPrice'),
        dispatch('updateBlockInfo')
      ])
    } catch (error) {
      console.error('批量更新信息失败:', error)
    }
  },
  
  async switchNetwork({ commit, dispatch }, chainId) {
    try {
      await switchNetwork(chainId)
      // 延迟更新，避免网络切换过程中的冲突
      setTimeout(() => {
        dispatch('updateAllInfo')
      }, 1000)
      return true
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    }
  },
  
  setupEventListeners({ commit, dispatch }) {
    // 监听账户变化
    onAccountsChanged((accounts) => {
      if (accounts.length === 0) {
        dispatch('disconnectWallet')
      } else {
        commit('SET_ADDRESS', accounts[0])
        // 延迟更新，避免频繁调用
        setTimeout(() => {
          dispatch('updateAllInfo')
        }, 500)
      }
    })
    
    // 监听网络变化
    onChainChanged(() => {
      // 延迟更新，避免频繁调用
      setTimeout(() => {
        dispatch('updateAllInfo')
      }, 500)
    })
  },
  
  removeEventListeners() {
    removeListeners()
  }
}

const getters = {
  isConnected: state => state.connected,
  isConnecting: state => state.connecting,
  walletAddress: state => state.address,
  walletBalance: state => state.balance,
  currentNetwork: state => state.network,
  walletError: state => state.error,
  isUpdating: state => state.isUpdating,
  
  // 新增 getters
  gasPrice: state => state.gasPrice,
  blockNumber: state => state.blockNumber,
  blockInfo: state => state.blockInfo,
  tokens: state => state.tokens,
  isUpdatingGas: state => state.isUpdatingGas,
  isUpdatingBlock: state => state.isUpdatingBlock,
  
  // 格式化地址显示
  formattedAddress: state => {
    if (!state.address) return ''
    return `${state.address.slice(0, 6)}...${state.address.slice(-4)}`
  },
  
  // 格式化余额显示
  formattedBalance: state => {
    if (state.balance === null || state.balance === undefined) return '0.0000'
    return state.balance.toFixed(4)
  },
  
  // 格式化 Gas 价格
  formattedGasPrice: state => {
    if (state.gasPrice === null || state.gasPrice === undefined) return '0'
    return `${state.gasPrice.toFixed(2)} Gwei`
  },
  
  // 网络标签类型
  networkTagType: state => {
    const mainnets = ['0x1', '0x89', '0x38', '0xa86a']
    return mainnets.includes(state.network.chainId) ? 'success' : 'warning'
  },
  
  // 网络状态
  networkStatus: state => {
    if (!state.connected) return 'disconnected'
    if (state.isUpdating) return 'updating'
    return 'connected'
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
