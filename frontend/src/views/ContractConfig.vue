<template>
  <div class="contract-config-page">
    <div class="page-header">
      <h1>📋 合约配置</h1>
      <p class="subtitle">查看和管理智能合约配置信息</p>
    </div>

    <!-- 合约信息卡片 -->
    <el-card class="info-card">
      <div class="card-header">
        <h2>🔗 合约信息</h2>
      </div>
      
      <div class="info-grid">
        <!-- 合约地址 -->
        <div class="info-item">
          <div class="info-label">合约地址</div>
          <el-input v-model="contractAddress" placeholder="请输入合约地址" class="address-input"></el-input>
          <div class="info-value address-value">{{ formattedContractAddress }}</div>
          <div class="button-group">
            <el-button type="text" @click="copyContractAddress" size="small">
              <span class="btn-icon">📋</span>
              复制
            </el-button>
            <el-button type="text" @click="saveContractAddress" size="small">
              <span class="btn-icon">💾</span>
              保存
            </el-button>
          </div>
        </div>
        
        <!-- Owner地址 -->
        <div class="info-item">
          <div class="info-label">Owner地址</div>
          <div class="info-value address-value">{{ formattedOwnerAddress }}</div>
          <el-button type="text" @click="copyOwnerAddress" size="small">
            <span class="btn-icon">📋</span>
            复制
          </el-button>
        </div>
        
        <!-- 当前钱包地址 -->
        <div class="info-item">
          <div class="info-label">当前钱包</div>
          <div class="info-value address-value">{{ formattedWalletAddress }}</div>
          <el-button type="text" @click="copyWalletAddress" size="small">
            <span class="btn-icon">📋</span>
            复制
          </el-button>
        </div>
        
        <!-- 连接状态 -->
        <div class="info-item">
          <div class="info-label">连接状态</div>
          <el-tag :type="isConnected ? 'success' : 'danger'" size="large">
            {{ isConnected ? '已连接' : '未连接' }}
          </el-tag>
        </div>
  
      </div>
    </el-card>

    <!-- 操作区域 -->
    <div class="actions-section">
      <el-button type="primary" size="large" @click="refreshInfo" :loading="isRefreshing">
        <span class="btn-icon">🔄</span>
        刷新信息
      </el-button>
      <el-button type="warning" size="large" @click="switchWalletAddress">
        <span class="btn-icon">💳</span>
        切换钱包地址
      </el-button>
      <el-button v-if="isOwner" type="success" size="large" @click="switchToIssuerConsole">
        <span class="btn-icon">⚙️</span>
        稳定币管理
      </el-button>
    </div>
  </div>
</template>

<script>
import { ElCard, ElButton, ElTag, ElMessage, ElInput } from 'element-plus'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'ContractConfig',
  components: { ElCard, ElButton, ElTag, ElInput },
  data() {
    return {
      isRefreshing: false,
      contractAddress: localStorage.getItem('hkdcContractAddress') || process.env.VUE_APP_HKDC_ADDRESS || ''
    }
  },
  computed: {
    ...mapGetters('wallet', [
      'isConnected',
      'walletAddress',
      'formattedAddress'
    ]),
    ...mapGetters('issuer', [
      'ownerAddress',
      'isIssuer',
      'totalSupply',
      'mintedAmount',
      'burnedAmount'
    ]),
    formattedContractAddress() {
      if (!this.contractAddress) return '未设置'
      return `${this.contractAddress.slice(0, 10)}...${this.contractAddress.slice(-8)}`
    },
    formattedOwnerAddress() {
      if (!this.ownerAddress) return '未获取'
      return `${this.ownerAddress.slice(0, 10)}...${this.ownerAddress.slice(-8)}`
    },
    formattedWalletAddress() {
      return this.formattedAddress || '未连接'
    },
    isOwner() {
      if (!this.walletAddress || !this.ownerAddress) return false
      return this.walletAddress.toLowerCase() === this.ownerAddress.toLowerCase()
    }
  },
  async mounted() {
    await this.refreshInfo()
  },
  methods: {
    ...mapActions('wallet', ['checkConnection', 'connectWallet']),
    ...mapActions('issuer', ['initIssuer']),
    
    async refreshInfo() {
      this.isRefreshing = true
      try {
        // 检查钱包连接
        await this.checkConnection()
        
        // 初始化发行方信息
        if (this.contractAddress && this.isConnected) {
          await this.initIssuer(this.contractAddress)
        }
      } catch (error) {
        console.error('刷新信息失败:', error)
        ElMessage.error('刷新信息失败: ' + error.message)
      } finally {
        this.isRefreshing = false
      }
    },
    
    async switchWalletAddress() {
      try {
        // 调用wallet模块的connectWallet action来切换钱包地址
        // 这会触发MetaMask的选择账户界面
        await this.connectWallet()
        
        // 刷新信息
        await this.refreshInfo()
        
        ElMessage.success('钱包地址已切换')
      } catch (error) {
        ElMessage.error('切换钱包地址失败: ' + (error.message || '未知错误'))
      }
    },
    
    saveContractAddress() {
      try {
        // 保存合约地址到localStorage
        localStorage.setItem('hkdcContractAddress', this.contractAddress)
        ElMessage.success('合约地址已保存')
        
        // 刷新信息
        this.refreshInfo()
      } catch (error) {
        ElMessage.error('保存合约地址失败: ' + (error.message || '未知错误'))
      }
    },
    
    copyToClipboard(text, message) {
      navigator.clipboard.writeText(text).then(() => {
        ElMessage.success(message + ' 已复制到剪贴板')
      }).catch(err => {
        ElMessage.error('复制失败: ' + err)
      })
    },
    
    copyContractAddress() {
      if (this.contractAddress) {
        this.copyToClipboard(this.contractAddress, '合约地址')
      }
    },
    
    copyOwnerAddress() {
      if (this.ownerAddress) {
        this.copyToClipboard(this.ownerAddress, 'Owner地址')
      }
    },
    
    copyWalletAddress() {
      if (this.walletAddress) {
        this.copyToClipboard(this.walletAddress, '钱包地址')
      }
    },
    
    switchToIssuerConsole() {
      this.$router.push('/issuer')
    }
  }
}
</script>

<style scoped>
.contract-config-page {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 2.5rem;
  margin: 0 0 15px 0;
  color: #303133;
  font-weight: 700;
}

.subtitle {
  font-size: 1.2rem;
  color: #606266;
  margin: 0;
}

.info-card {
  background: #ffffff;
  border: 1px solid #ebeef5;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  margin-bottom: 30px;
}

.card-header {
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 20px;
  margin-bottom: 25px;
}

.card-header h2 {
  font-size: 1.8rem;
  color: #303133;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  border-radius: 12px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.info-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.info-label {
  font-weight: 600;
  color: #606266;
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 1.1rem;
  color: #303133;
  font-weight: 500;
  word-break: break-all;
}

/* 货币总览样式 */
.overview-item { display: flex; justify-content: space-between; margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px; }
.overview-label { font-weight: 600; color: #606266; }
.overview-value { font-weight: 700; color: #303133; }

.address-input {
  margin-bottom: 15px;
}

.address-value {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.95rem;
  background: #ffffff;
  padding: 10px 15px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  margin-bottom: 15px;
}

.button-group {
  display: flex;
  gap: 10px;
}

.actions-section {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
  flex-wrap: wrap;
}

.btn-icon {
  margin-right: 8px;
}

@media (max-width: 768px) {
  .contract-config-page {
    padding: 20px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-section {
    flex-direction: column;
    align-items: center;
  }
  
  .actions-section .el-button {
    width: 100%;
    max-width: 300px;
  }
}
</style>