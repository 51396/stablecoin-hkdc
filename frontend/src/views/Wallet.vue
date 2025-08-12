<template>
  <div class="wallet-page">
    <div class="page-header">
      <h1>🔐 钱包管理</h1>
      <p class="subtitle">连接 MetaMask，管理您的数字资产</p>
    </div>
    
    <!-- 连接状态 -->
    <div v-if="!isConnected" class="connection-card">
      <div class="connection-content">
        <div class="connection-icon">🔗</div>
        <h2>连接钱包</h2>
        <p>请连接 MetaMask 钱包以开始使用</p>
        <el-button type="primary" size="large" @click="connectWallet" :loading="isConnecting">
          <span class="btn-icon">🦊</span>
          连接 MetaMask
        </el-button>
      </div>
    </div>
    
    <!-- 钱包信息 -->
    <div v-if="isConnected" class="wallet-content">
      <!-- 钱包概览卡片 -->
      <div class="overview-card">
        <div class="overview-header">
          <h2>💰 钱包概览</h2>
          <el-button type="primary" @click="refreshAll" :loading="isUpdating" size="small">
            <span class="btn-icon">🔄</span>
            刷新信息
          </el-button>
        </div>
        
        <div class="overview-grid">
          <!-- 钱包地址 -->
          <div class="overview-item address-item">
            <div class="item-icon">📍</div>
            <div class="item-content">
              <h3>钱包地址</h3>
              <p class="address-text">{{ formattedAddress }}</p>
              <el-button type="text" @click="copyAddress" size="small">
                <span class="btn-icon">📋</span>
                复制地址
              </el-button>
            </div>
          </div>
          
          <!-- 网络信息 -->
          <div class="overview-item network-item">
            <div class="item-icon">🌐</div>
            <div class="item-content">
              <h3>当前网络</h3>
              <div class="network-info">
                <el-tag :type="networkTagType" size="large">
                  {{ currentNetwork.name }}
                </el-tag>
                <p class="network-details">
                  <span class="chain-id">链ID: {{ currentNetwork.chainId }}</span>
                  <span class="symbol">符号: {{ currentNetwork.symbol }}</span>
                </p>
              </div>
            </div>
          </div>
          
          <!-- 原生代币余额 -->
          <div class="overview-item balance-item">
            <div class="item-icon">💎</div>
            <div class="item-content">
              <h3>原生代币余额</h3>
              <p class="balance-amount">{{ formattedBalance }}</p>
              <p class="balance-symbol">{{ currentNetwork.symbol }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 网络状态卡片 -->
      <div class="status-card">
        <h3>📊 网络状态</h3>
        <div class="status-grid">
          <div class="status-item">
            <div class="status-label">连接状态</div>
            <el-tag :type="networkStatus === 'connected' ? 'success' : networkStatus === 'updating' ? 'warning' : 'danger'" size="large">
              {{ networkStatus === 'connected' ? '已连接' : networkStatus === 'updating' ? '更新中' : '未连接' }}
            </el-tag>
          </div>
          
          <div class="status-item">
            <div class="status-label">Gas 价格</div>
            <div class="status-value">
              <span class="value-text">{{ formattedGasPrice }}</span>
              <el-button type="text" @click="refreshGasPrice" size="small" :loading="isUpdatingGas">
                <span class="btn-icon">🔄</span>
              </el-button>
            </div>
          </div>
          
          <div class="status-item">
            <div class="status-label">当前区块</div>
            <div class="status-value">
              <span class="value-text">{{ blockNumber || '未知' }}</span>
              <el-button type="text" @click="refreshBlockInfo" size="small" :loading="isUpdatingBlock">
                <span class="btn-icon">🔄</span>
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 区块信息卡片 -->
      <div v-if="blockInfo" class="block-card">
        <h3>📦 最新区块信息</h3>
        <div class="block-grid">
          <div class="block-item">
            <span class="block-label">区块号</span>
            <span class="block-value">{{ blockInfo.number.toLocaleString() }}</span>
          </div>
          <div class="block-item">
            <span class="block-label">时间戳</span>
            <span class="block-value">{{ formatTimestamp(blockInfo.timestamp) }}</span>
          </div>
          <div class="block-item">
            <span class="block-label">Gas 限制</span>
            <span class="block-value">{{ blockInfo.gasLimit.toLocaleString() }}</span>
          </div>
          <div class="block-item">
            <span class="block-label">Gas 使用</span>
            <span class="block-value">{{ blockInfo.gasUsed.toLocaleString() }}</span>
          </div>
          <div class="block-item">
            <span class="block-label">交易数量</span>
            <span class="block-value">{{ blockInfo.transactions }}</span>
          </div>
          <div class="block-item">
            <span class="block-label">矿工地址</span>
            <span class="block-value address">{{ formatAddress(blockInfo.miner) }}</span>
          </div>
        </div>
      </div>
      
      <!-- 代币查询 -->
      <TokenQuery />
      
      <!-- 操作按钮 -->
      <div class="actions-section">
        <el-button type="danger" size="large" @click="disconnectWallet">
          <span class="btn-icon">❌</span>
          断开连接
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { ElButton, ElTag } from 'element-plus'
import { ElMessage } from 'element-plus'
import { mapGetters, mapActions } from 'vuex'
import TokenQuery from '@/components/TokenQuery.vue'

export default {
  name: 'Wallet',
  components: { ElButton, ElTag, TokenQuery },
  computed: {
    ...mapGetters('wallet', [
      'isConnected',
      'isConnecting',
      'formattedAddress',
      'formattedBalance',
      'currentNetwork',
      'formattedGasPrice',
      'blockNumber',
      'blockInfo',
      'networkStatus',
      'isUpdatingGas',
      'isUpdatingBlock',
      'isUpdating',
      'networkTagType'
    ])
  },
  async mounted() {
    console.log('Wallet component mounted')
    try {
      await this.checkConnection()
    } catch (error) {
      console.error('Check connection error:', error)
    }
  },
  methods: {
    ...mapActions('wallet', [
      'connectWallet',
      'disconnectWallet',
      'checkConnection',
      'updateGasPrice',
      'updateBlockInfo',
      'updateAllInfo'
    ]),
    
    async refreshGasPrice() {
      try {
        await this.updateGasPrice()
        ElMessage.success('Gas 价格已更新')
      } catch (error) {
        ElMessage.error('更新 Gas 价格失败')
      }
    },
    
    async refreshBlockInfo() {
      try {
        await this.updateBlockInfo()
        ElMessage.success('区块信息已更新')
      } catch (error) {
        ElMessage.error('更新区块信息失败')
      }
    },
    
    async refreshAll() {
      try {
        await this.updateAllInfo()
        ElMessage.success('所有信息已更新')
      } catch (error) {
        ElMessage.error('更新信息失败')
      }
    },
    
    async copyAddress() {
      try {
        const address = this.$store.getters['wallet/walletAddress']
        await navigator.clipboard.writeText(address)
        ElMessage.success('地址已复制到剪贴板')
      } catch (error) {
        ElMessage.error('复制失败')
      }
    },
    
    formatTimestamp(timestamp) {
      if (!timestamp) return '未知'
      const date = new Date(timestamp * 1000)
      return date.toLocaleString('zh-CN')
    },
    
    formatAddress(address) {
      if (!address) return '未知'
      return `${address.slice(0, 6)}...${address.slice(-4)}`
    }
  }
}
</script>

<style scoped>
.wallet-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  color: white;
}

.page-header h1 {
  font-size: 2.5rem;
  margin: 0 0 10px 0;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.subtitle {
  font-size: 1.1rem;
  margin: 0;
  opacity: 0.9;
}

.connection-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 60px 40px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.connection-content {
  max-width: 400px;
  margin: 0 auto;
}

.connection-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.connection-content h2 {
  color: #303133;
  margin: 0 0 15px 0;
  font-size: 1.8rem;
}

.connection-content p {
  color: #606266;
  margin: 0 0 30px 0;
  font-size: 1.1rem;
}

.wallet-content {
  max-width: 1200px;
  margin: 0 auto;
}

.overview-card, .status-card, .block-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 15px 35px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.overview-header h2 {
  margin: 0;
  color: #303133;
  font-size: 1.5rem;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
}

.overview-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 25px;
  border-radius: 15px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.overview-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.item-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.item-content h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 1.1rem;
  font-weight: 600;
}

.address-text {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9rem;
  background: #f8f9fa;
  padding: 8px 12px;
  border-radius: 8px;
  margin: 10px 0;
  word-break: break-all;
  border: 1px solid #e9ecef;
}

.network-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.network-details {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 0.85rem;
  color: #606266;
}

.chain-id, .symbol {
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 6px;
  font-family: monospace;
}

.balance-amount {
  font-size: 1.8rem;
  font-weight: 700;
  color: #409eff;
  margin: 10px 0 5px 0;
}

.balance-symbol {
  font-size: 1rem;
  color: #606266;
  margin: 0;
  font-weight: 500;
}

.status-card h3, .block-card h3 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 1.3rem;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 20px;
  border-radius: 12px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
}

.status-label {
  font-weight: 600;
  color: #606266;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-value {
  display: flex;
  align-items: center;
  gap: 10px;
}

.value-text {
  font-size: 1.1rem;
  color: #303133;
  font-weight: 500;
  font-family: monospace;
}

.block-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.block-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 15px;
  border-radius: 10px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
}

.block-label {
  font-size: 0.8rem;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.block-value {
  font-size: 1rem;
  color: #303133;
  font-weight: 500;
  font-family: monospace;
}

.block-value.address {
  font-size: 0.85rem;
}

.actions-section {
  text-align: center;
  padding: 30px 0;
}

.btn-icon {
  margin-right: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .wallet-page {
    padding: 15px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .block-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .overview-item {
    flex-direction: column;
    text-align: center;
  }
  
  .item-icon {
    margin: 0 auto 15px auto;
  }
}
</style>
