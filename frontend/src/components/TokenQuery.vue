<template>
  <div class="token-query-card">
    <div class="card-header">
      <h3>🪙 代币查询</h3>
      <p class="card-subtitle">查询 ERC-20 代币余额和信息</p>
    </div>
    
    <!-- 代币地址输入 -->
    <div class="input-section">
      <el-input
        v-model="tokenAddress"
        placeholder="输入代币合约地址 (0x...)"
        class="token-input"
        clearable
        size="large"
      >
        <template #prepend>
          <span class="input-icon">📍</span>
          代币地址
        </template>
      </el-input>
      
      <el-button 
        type="primary" 
        @click="queryToken" 
        :loading="isQuerying"
        :disabled="!tokenAddress || !isConnected"
        size="large"
        class="query-btn"
      >
        <span class="btn-icon">🔍</span>
        查询代币
      </el-button>
    </div>
    
    <!-- 代币信息显示 -->
    <div v-if="tokenInfo" class="token-info-section">
      <div class="section-header">
        <h4>📋 代币信息</h4>
        <el-tag type="success" size="large">已找到</el-tag>
      </div>
      
      <div class="info-grid">
        <div class="info-item">
          <div class="info-icon">🏷️</div>
          <div class="info-content">
            <span class="info-label">名称</span>
            <span class="info-value">{{ tokenInfo.name }}</span>
          </div>
        </div>
        
        <div class="info-item">
          <div class="info-icon">💎</div>
          <div class="info-content">
            <span class="info-label">符号</span>
            <span class="info-value">{{ tokenInfo.symbol }}</span>
          </div>
        </div>
        
        <div class="info-item">
          <div class="info-icon">🔢</div>
          <div class="info-content">
            <span class="info-label">精度</span>
            <span class="info-value">{{ tokenInfo.decimals }}</span>
          </div>
        </div>
        
        <div class="info-item">
          <div class="info-icon">🔗</div>
          <div class="info-content">
            <span class="info-label">合约地址</span>
            <span class="info-value address">{{ formatAddress(tokenInfo.address) }}</span>
          </div>
        </div>
      </div>
      
      <!-- 余额信息 -->
      <div v-if="tokenBalance !== null" class="balance-section">
        <div class="section-header">
          <h4>💰 余额信息</h4>
          <el-button type="primary" @click="refreshTokenBalance" size="small" :loading="isQuerying">
            <span class="btn-icon">🔄</span>
            刷新余额
          </el-button>
        </div>
        
        <div class="balance-display">
          <div class="balance-main">
            <span class="balance-label">您的余额:</span>
            <span class="balance-value">{{ formatTokenBalance(tokenBalance, tokenInfo.decimals) }}</span>
            <span class="balance-symbol">{{ tokenInfo.symbol }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 错误信息 -->
    <div v-if="error" class="error-message">
      <el-alert 
        :title="error" 
        type="error" 
        show-icon 
        :closable="false"
        class="error-alert"
      />
    </div>
    
    <!-- 常用代币列表 -->
    <div class="common-tokens-section">
      <div class="section-header">
        <h4>⭐ 常用代币</h4>
        <p class="section-subtitle">点击快速查询常用代币</p>
      </div>
      
      <div class="token-list">
        <div 
          v-for="token in commonTokens" 
          :key="`${token.chainId}-${token.address}`"
          class="token-item"
          :class="{ 'current-network': token.chainId === currentNetwork.chainId }"
          @click="selectCommonToken(token)"
        >
          <div class="token-header">
            <div class="token-symbol">{{ token.symbol }}</div>
            <div class="token-network-tag" v-if="token.chainId === currentNetwork.chainId">
              <el-tag type="success" size="small">当前网络</el-tag>
            </div>
          </div>
          <div class="token-name">{{ token.name }}</div>
          <div class="token-address">{{ formatAddress(token.address) }}</div>
          <div class="token-chain">{{ getNetworkName(token.chainId) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ElInput, ElButton, ElAlert, ElTag } from 'element-plus'
import { ElMessage } from 'element-plus'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'TokenQuery',
  components: { ElInput, ElButton, ElAlert, ElTag },
  data() {
    return {
      tokenAddress: '',
      tokenInfo: null,
      tokenBalance: null,
      isQuerying: false,
      error: '',
      
      // 常用代币列表（多网络支持）
      commonTokens: [
        // Ethereum 主网
        {
          name: 'Tether USD',
          symbol: 'USDT',
          address: '0xdAC17F958D2ee523a2206206994597C13D831ec7',
          chainId: '0x1'
        },
        {
          name: 'USD Coin',
          symbol: 'USDC',
          address: '0xA0b86a33E6441b8c4C8C8C8C8C8C8C8C8C8C8C8',
          chainId: '0x1'
        },
        {
          name: 'Dai',
          symbol: 'DAI',
          address: '0x6B175474E89094C44Da98b954EedeAC495271d0F',
          chainId: '0x1'
        },
        {
          name: 'Wrapped Ether',
          symbol: 'WETH',
          address: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
          chainId: '0x1'
        },
        
        // Polygon 主网
        {
          name: 'Tether USD (Polygon)',
          symbol: 'USDT',
          address: '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
          chainId: '0x89'
        },
        {
          name: 'USD Coin (Polygon)',
          symbol: 'USDC',
          address: '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
          chainId: '0x89'
        },
        {
          name: 'Wrapped MATIC',
          symbol: 'WMATIC',
          address: '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
          chainId: '0x89'
        },
        
        // BSC 主网
        {
          name: 'Tether USD (BSC)',
          symbol: 'USDT',
          address: '0x55d398326f99059fF775485246999027B3197955',
          chainId: '0x38'
        },
        {
          name: 'USD Coin (BSC)',
          symbol: 'USDC',
          address: '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
          chainId: '0x38'
        },
        {
          name: 'Wrapped BNB',
          symbol: 'WBNB',
          address: '0xbb4CdB9CBd36B01bD1cBaEF2aD8c3c2Dd6Dc4C4F',
          chainId: '0x38'
        },
        
        // Avalanche 主网
        {
          name: 'Tether USD (Avalanche)',
          symbol: 'USDT',
          address: '0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7',
          chainId: '0xa86a'
        },
        {
          name: 'USD Coin (Avalanche)',
          symbol: 'USDC',
          address: '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
          chainId: '0xa86a'
        },
        {
          name: 'Wrapped AVAX',
          symbol: 'WAVAX',
          address: '0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7',
          chainId: '0xa86a'
        }
      ]
    }
  },
  computed: {
    ...mapGetters('wallet', [
      'isConnected',
      'currentNetwork'
    ])
  },
  watch: {
    currentNetwork() {
      // 网络切换时清空代币信息
      this.clearTokenInfo()
    }
  },
  methods: {
    ...mapActions('wallet', [
      'getTokenInfo',
      'getTokenBalance'
    ]),
    
    async queryToken() {
      if (!this.tokenAddress || !this.isConnected) return
      
      this.isQuerying = true
      this.error = ''
      this.clearTokenInfo()
      
      try {
        // 查询代币信息
        const info = await this.getTokenInfo(this.tokenAddress)
        if (info) {
          this.tokenInfo = info
          
          // 查询代币余额
          const balance = await this.getTokenBalance(this.tokenAddress)
          this.tokenBalance = balance
          
          ElMessage.success('代币信息查询成功')
        } else {
          this.error = '无法获取代币信息，请检查合约地址是否正确'
        }
      } catch (error) {
        this.error = `查询失败: ${error.message}`
        ElMessage.error('代币查询失败')
      } finally {
        this.isQuerying = false
      }
    },
    
    async refreshTokenBalance() {
      if (!this.tokenAddress || !this.isConnected) return
      
      try {
        const balance = await this.getTokenBalance(this.tokenAddress)
        this.tokenBalance = balance
        ElMessage.success('余额已更新')
      } catch (error) {
        ElMessage.error('更新余额失败')
      }
    },
    
    selectCommonToken(token) {
      // 检查是否在当前网络
      if (token.chainId !== this.currentNetwork.chainId) {
        ElMessage.warning(`该代币在 ${this.currentNetwork.name} 上不可用`)
        return
      }
      
      this.tokenAddress = token.address
      this.queryToken()
    },
    
    clearTokenInfo() {
      this.tokenInfo = null
      this.tokenBalance = null
      this.error = ''
    },
    
    formatAddress(address) {
      if (!address) return ''
      return `${address.slice(0, 6)}...${address.slice(-4)}`
    },
    
    formatTokenBalance(balance, decimals) {
      if (balance === null || balance === undefined) return '0'
      const fractionDigits = Math.min(Number(decimals) || 6, 8)
      const num = typeof balance === 'string' ? Number(balance) : balance
      if (!Number.isFinite(num)) return '0'
      return num.toFixed(fractionDigits)
    },
    
    getNetworkName(chainId) {
      const networkMap = {
        '0x1': 'Ethereum',
        '0x5': 'Goerli',
        '0xaa36a7': 'Sepolia',
        '0x89': 'Polygon',
        '0x13881': 'Mumbai',
        '0x38': 'BSC',
        '0x61': 'BSC Testnet',
        '0xa86a': 'Avalanche',
        '0xa869': 'Fuji',
        '0xa4b1': 'Arbitrum',
        '0x66eed': 'Arbitrum Goerli',
        '0xa': 'Optimism',
        '0x1a4': 'Optimism Goerli',
        '0xfa': 'Fantom',
        '0xfa2': 'Fantom Testnet'
      }
      return networkMap[chainId] || 'Unknown'
    }
  }
}
</script>

<style scoped>
.token-query-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 15px 35px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.card-header h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 1.5rem;
  font-weight: 600;
}

.card-subtitle {
  margin: 0;
  color: #606266;
  font-size: 1rem;
}

.input-section {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  align-items: center;
}

.token-input {
  flex: 1;
}

.input-icon {
  margin-right: 8px;
}

.query-btn {
  white-space: nowrap;
}

.token-info-section {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h4 {
  margin: 0;
  color: #303133;
  font-size: 1.2rem;
  font-weight: 600;
}

.section-subtitle {
  margin: 0;
  color: #606266;
  font-size: 0.9rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.info-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

.info-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-label {
  font-size: 0.8rem;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.info-value {
  font-size: 1rem;
  color: #303133;
  font-weight: 500;
}

.info-value.address {
  font-family: monospace;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.85rem;
}

.balance-section {
  padding: 25px;
  border-radius: 15px;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: 1px solid #90caf9;
}

.balance-display {
  text-align: center;
}

.balance-main {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.balance-label {
  font-size: 1rem;
  color: #1976d2;
  font-weight: 500;
}

.balance-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1565c0;
}

.balance-symbol {
  font-size: 1.2rem;
  color: #1976d2;
  font-weight: 600;
}

.error-message {
  margin: 25px 0;
}

.error-alert {
  border-radius: 12px;
}

.common-tokens-section {
  margin-top: 40px;
}

.token-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.token-item {
  padding: 20px;
  border: 2px solid #e9ecef;
  border-radius: 15px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.token-item:hover {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(64, 158, 255, 0.2);
}

.token-item.current-network {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e1f3d8 100%);
}

.token-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.token-symbol {
  font-size: 1.3rem;
  font-weight: 700;
  color: #303133;
}

.token-network-tag {
  flex-shrink: 0;
}

.token-name {
  font-size: 1rem;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}

.token-address {
  font-size: 0.85rem;
  color: #909399;
  font-family: monospace;
  margin-bottom: 8px;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 6px;
}

.token-chain {
  font-size: 0.8rem;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.btn-icon {
  margin-right: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .token-query-card {
    padding: 20px;
  }
  
  .input-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .query-btn {
    width: 100%;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .token-list {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>
