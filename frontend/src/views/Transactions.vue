<template>
  <div class="page">
    <el-card class="card">
      <div class="card-title">
        <el-icon><List /></el-icon>
        <span>交易记录</span>
      </div>
      
      <div class="toolbar">
        <div class="filters">
          <el-select v-model="filters.type" placeholder="交易类型" clearable style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="买入" value="buy" />
            <el-option label="卖出" value="sell" />
            <el-option label="充值" value="deposit" />
            <el-option label="提币" value="withdraw" />
            <el-option label="合约交易" value="contract" />
          <el-option label="铸造" value="mint" />
          <el-option label="销毁" value="burn" />
          <el-option label="转账" value="transfer" />
          </el-select>
          
          <el-select v-model="filters.status" placeholder="交易状态" clearable style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="成功" value="success" />
            <el-option label="处理中" value="pending" />
            <el-option label="失败" value="failed" />
          </el-select>
          
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
          />
        </div>
        
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      
      <el-table :data="filteredTransactions" style="width: 100%" class="transactions-table">
        <el-table-column prop="id" label="交易ID" width="120">
          <template #default="scope">
            <el-tag size="small" type="info">{{ scope.row.id }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="type" label="类型" width="100">
          <template #default="scope">
            <el-tag 
              :type="getTypeTagType(scope.row.type)" 
              size="small"
            >
              {{ getTypeLabel(scope.row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="scope">
            <span class="amount-text">{{ scope.row.amount }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="block_number" label="区块高度" width="120" />
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag 
              :type="getStatusTagType(scope.row.status)" 
              size="small"
            >
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.timestamp) }}
          </template>
        </el-table-column>
        
        <el-table-column label="发起方" width="150" v-if="isShowAddressColumn">
          <template #default="scope">
            <el-link type="primary" @click="copyToClipboard(scope.row.from_address)" v-if="scope.row.from_address">
              {{ formatAddress(scope.row.from_address) }}
            </el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="接收方" width="150" v-if="isShowAddressColumn">
          <template #default="scope">
            <el-link type="primary" @click="copyToClipboard(scope.row.to_address)" v-if="scope.row.to_address">
              {{ formatAddress(scope.row.to_address) }}
            </el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button 
              type="text" 
              size="small" 
              @click="viewDetails(scope.row)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 交易详情对话框 -->
    <el-dialog v-model="showDetailsDialog" title="交易详情" width="600px">
      <div v-if="selectedTransaction" class="transaction-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="交易ID">{{ selectedTransaction.id }}</el-descriptions-item>
          <el-descriptions-item label="交易类型">{{ getTypeLabel(selectedTransaction.type) }}</el-descriptions-item>
          <el-descriptions-item label="金额">{{ selectedTransaction.amount }} {{ selectedTransaction.currency }}</el-descriptions-item>
          <el-descriptions-item label="区块高度">{{ selectedTransaction.block_number }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getStatusLabel(selectedTransaction.status) }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ formatDate(selectedTransaction.timestamp) }}</el-descriptions-item>
          <el-descriptions-item label="手续费">{{ selectedTransaction.fee || '0.00' }} ETH</el-descriptions-item>
          <el-descriptions-item label="发起方" v-if="selectedTransaction.from_address">
            <el-link type="primary" @click="copyToClipboard(selectedTransaction.from_address)">
              {{ formatAddress(selectedTransaction.from_address) }}
            </el-link>
          </el-descriptions-item>
          <el-descriptions-item label="接收方" v-if="selectedTransaction.to_address">
            <el-link type="primary" @click="copyToClipboard(selectedTransaction.to_address)">
              {{ formatAddress(selectedTransaction.to_address) }}
            </el-link>
          </el-descriptions-item>
          <el-descriptions-item label="Gas 使用量" v-if="selectedTransaction.gas_used">{{ selectedTransaction.gas_used }}</el-descriptions-item>
          <el-descriptions-item label="Gas 价格" v-if="selectedTransaction.gas_price">{{ selectedTransaction.gas_price }} Gwei</el-descriptions-item>
          <el-descriptions-item label="交易哈希" v-if="selectedTransaction.tx_hash">
            <el-link type="primary" @click="copyToClipboard(selectedTransaction.tx_hash)">
              {{ formatAddress(selectedTransaction.tx_hash) }}
            </el-link>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { List, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { tradeAPI } from '@/api/wallet'
import { onTransactionStatusChange, removeTransactionStatusListener } from '@/utils/metamask'

export default {
  name: 'Transactions',
  components: { List, Refresh },
  data() {
    return {
      filters: {
        type: '',
        status: '',
        dateRange: []
      },
      currentPage: 1,
      pageSize: 20,
      total: 0,
      showDetailsDialog: false,
      selectedTransaction: null,
      transactions: [],
      refreshInterval: null,
      isShowAddressColumn: false
    }
  },
  computed: {
    filteredTransactions() {
      let filtered = this.transactions
      
      if (this.filters.type) {
        filtered = filtered.filter(tx => tx.type === this.filters.type)
      }
      
      if (this.filters.status) {
        filtered = filtered.filter(tx => tx.status === this.filters.status)
      }
      
      return filtered
    }
  },
  methods: {
    getTypeTagType(type) {
      const types = { 
        buy: 'success', 
        sell: 'danger', 
        deposit: 'primary', 
        withdraw: 'warning', 
        contract: 'info',
        mint: 'success',
        burn: 'danger',
        transfer: 'primary'
      }
      return types[type] || 'info'
    },
    getTypeLabel(type) {
      const labels = { 
        buy: '买入', 
        sell: '卖出', 
        deposit: '充值', 
        withdraw: '提币', 
        contract: '合约交易',
        mint: '铸造',
        burn: '销毁',
        transfer: '转账'
      }
      return labels[type] || type
    },
    getStatusTagType(status) {
      const types = { success: 'success', pending: 'warning', failed: 'danger' }
      return types[status] || 'info'
    },
    getStatusLabel(status) {
      const labels = { success: '成功', pending: '处理中', failed: '失败' }
      return labels[status] || status
    },
    formatDate(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN')
    },
    formatAddress(address) {
      if (!address) return ''
      // 如果地址长度大于10，则截取前后各5位
      if (address.length > 10) {
        return `${address.substring(0, 5)}...${address.substring(address.length - 5)}`
      }
      return address
    },
    copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(() => {
        ElMessage.success('已复制到剪贴板')
      }).catch(() => {
        ElMessage.error('复制失败')
      })
    },
    async refreshData() {
      try {
        // // 先调用后端接口手动刷新交易历史数据（从链上获取）
        // await tradeAPI.refreshTradeHistory()
        // 再获取最新的交易历史数据（从数据库）
        const response = await tradeAPI.getTradeHistory({
          page: this.currentPage,
          per_page: this.pageSize
        })
        
        // 处理分页数据
        if (response.data && response.data.items) {
          this.transactions = response.data.items
          this.total = response.data.total
        } else {
          this.transactions = response.data || []
          this.total = this.transactions.length
        }
        
        ElMessage.success('数据已刷新')
      } catch (error) {
        ElMessage.error('刷新数据失败')
      }
    },
    viewDetails(transaction) {
      this.selectedTransaction = transaction
      this.showDetailsDialog = true
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.refreshData()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.refreshData()
    },
    // 启动定时刷新
    startAutoRefresh() {
      this.refreshInterval = setInterval(() => {
        this.refreshData()
      }, 30000) // 每30秒刷新一次
    },
    // 停止定时刷新
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
        this.refreshInterval = null
      }
    },
    // 处理交易状态变化
    handleTransactionStatusChange(txInfo) {
      // 更新交易状态
      const transaction = this.transactions.find(tx => tx.tx_hash === txInfo.txHash)
      if (transaction) {
        transaction.status = txInfo.status
        ElMessage.success(`交易 ${txInfo.txHash} 状态更新为: ${txInfo.status}`)
      }
    },
    // 检查交易状态（当MetaMask无法获取时从后端获取）
    async checkTransactionStatus(txHash) {
      try {
        const response = await tradeAPI.checkTransactionStatus(txHash)
        const transaction = this.transactions.find(tx => tx.tx_hash === txHash)
        if (transaction && response.data) {
          transaction.status = response.data.status
          ElMessage.success(`交易 ${txHash} 状态更新为: ${response.data.status}`)
        }
      } catch (error) {
        console.error('检查交易状态失败:', error)
      }
    }
  },
  async mounted() {
    // 检查用户是否为管理员
    try {
      const userResponse = await this.$http.get('/user/me')
      this.isShowAddressColumn = userResponse.data.role === 'admin'
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
    
    this.refreshData()
    this.startAutoRefresh()
    // 监听MetaMask交易状态变化
    onTransactionStatusChange(this.handleTransactionStatusChange)
  },
  beforeUnmount() {
    // 组件销毁前停止定时刷新和移除监听器
    this.stopAutoRefresh()
    removeTransactionStatusListener()
  }
}
</script>

<style scoped>
.page-title {
  color: #303133;
  margin-bottom: 20px;
}

.toolbar {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.toolbar-item {
  flex: 1;
  min-width: 200px;
}

.transactions-table :deep(.el-table) {
  background: #ffffff;
  border: 1px solid #ebeef5;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.transactions-table :deep(.el-table__header) {
  background: #f5f7fa;
}

.transactions-table :deep(.el-table__row) {
  background: transparent;
}

.transactions-table :deep(.el-table__cell) {
  color: #303133;
  border-color: #ebeef5;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-completed {
  background: rgba(103, 194, 58, 0.2);
  color: #67c23a;
}

.status-pending {
  background: rgba(230, 162, 60, 0.2);
  color: #e6a23c;
}

.status-failed {
  background: rgba(245, 108, 108, 0.2);
  color: #f56c6c;
}

.amount-positive {
  color: #67c23a;
}

.amount-negative {
  color: #f56c6c;
}
</style>
