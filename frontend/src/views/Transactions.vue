<template>
  <!-- 1. 根容器，应用统一的页面样式 -->
  <div class="page-container">
    
    <!-- 2. 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">交易记录</h1>
      <p class="page-subtitle">查看所有链上及协议内交易</p>
    </div>

    <!-- 3. 主内容卡片 -->
    <el-card class="box-card">
      <!-- 卡片头部，整合了标题和工具栏 -->
      <template #header>
        <div class="card-header-wrapper">
          <div class="card-header-title">
            <el-icon><List /></el-icon>
            <span>所有交易</span>
          </div>
          <div class="toolbar">
            <!-- 筛选器 -->
            <el-select v-model="filters.type" placeholder="交易类型" clearable size="small" style="width: 120px">
              <!-- ... options ... -->
            </el-select>
            <el-select v-model="filters.status" placeholder="交易状态" clearable size="small" style="width: 120px">
              <!-- ... options ... -->
            </el-select>
            <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="-"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              size="small"
              style="width: 240px"
            />
            <!-- 刷新按钮 -->
            <el-button type="primary" plain @click="refreshData" size="small" :icon="Refresh" class="details-button">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 表格 -->
      <el-table :data="filteredTransactions" style="width: 100%" class="transactions-table" v-loading="loading">
        <!-- 为了更好的响应式，使用 min-width 替代固定的 width -->
        <el-table-column prop="tx_hash" label="交易哈希" min-width="180">
          <template #default="{ row }">
            <div class="tx-hash-cell" @click="copyToClipboard(row.tx_hash || row.id)">
              <el-tooltip :content="row.tx_hash || row.id" placement="top">
                <span>{{ formatAddress(row.tx_hash) }}</span>
              </el-tooltip>
              <el-icon class="copy-icon"><CopyDocument /></el-icon>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="type" label="类型" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)" effect="light" size="small">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="amount" label="金额" align="right" min-width="150">
          <template #default="{ row }">
            <span class="amount-text" :class="getAmountClass(row.amount, row.type)">
              {{ getAmountPrefix(row.amount, row.type) }} {{ formatCurrency(Math.abs(row.amount)) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" align="center" min-width="120">
          <template #default="{ row }">
            <div class="status-cell">
              <span class="status-dot" :class="getStatusClass(row.status)"></span>
              <span>{{ getStatusLabel(row.status) }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="地址流向 (From / To)" min-width="300" v-if="isShowAddressColumn">
          <template #default="{ row }">
             <div class="address-flow">
               <el-tooltip :content="row.from_address" placement="top">
                 <span class="address-tag">{{ formatAddress(row.from_address) }}</span>
               </el-tooltip>
               <el-icon class="arrow-icon"><Right /></el-icon>
               <el-tooltip :content="row.to_address" placement="top">
                 <span class="address-tag">{{ formatAddress(row.to_address) }}</span>
               </el-tooltip>
             </div>
           </template>
        </el-table-column>
        
        <el-table-column prop="timestamp" label="时间" align="right" min-width="180">
          <template #default="{ row }">
            {{ formatDate(row.timestamp) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="{ row }">
            <!-- 
              将 type="text" 改为 type="primary" 并添加 plain 属性。
              这会创建一个带蓝色边框和淡蓝色背景的按钮，文字是深蓝色。
            -->
            <el-button 
              type="primary" 
              plain 
              size="small" 
              @click="viewDetails(row)"
               class="details-button"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background
        />
      </div>
    </el-card>
    
    <!-- 交易详情对话框 -->
    <el-dialog v-model="showDetailsDialog" title="交易详情" class="details-dialog"  :teleported="true" >
      <div v-if="selectedTransaction" class="transaction-details" >
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
    formatAddress(address) {
      if (!address) return ''
      // 如果地址长度大于10，则截取前后各5位
      // if (address.length > 10) {
      //   return `${address.substring(0, 5)}...${address.substring(address.length - 5)}`
      // }
      return '0x' + address
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
    },
     /**
     * 根据金额正负和交易类型，返回对应的CSS class
     * @param {number} amount - 金额
     * @param {string} type - 交易类型
     * @returns {string} - 'amount-positive' 或 'amount-negative'
     */
     getAmountClass(amount, type) {
      // 默认规则：正数是 positive，负数是 negative
      if (amount > 0) return 'amount-positive';
      if (amount < 0) return 'amount-negative';

      // 您可以根据交易类型定义更复杂的规则
      // 例如，'提币' (withdraw) 或 '卖出' (sell) 即使是正数，也可能想显示为 negative (红色)
      // const negativeTypes = ['withdraw', 'sell', 'burn'];
      // if (negativeTypes.includes(type)) {
      //   return 'amount-negative';
      // }
      // const positiveTypes = ['deposit', 'buy', 'mint'];
      // if (positiveTypes.includes(type)) {
      //   return 'amount-positive';
      // }
      
      return ''; // 默认无特殊样式
    },

    /**
     * 根据金额正负和交易类型，返回金额前缀 '+' 或 '-'
     * @param {number} amount - 金额
     * @param {string} type - 交易类型
     * @returns {string} - '+' 或 '-'
     */
    getAmountPrefix(amount, type) {
      // 简单的正负判断
      if (amount > 0) return '+';
      if (amount < 0) return '-';
      
      // 同样，您也可以根据类型定义更复杂的规则
      // const negativeTypes = ['withdraw', 'sell', 'burn'];
      // if (negativeTypes.includes(type)) {
      //   return '-';
      // }
      // const positiveTypes = ['deposit', 'buy', 'mint'];
      // if (positiveTypes.includes(type)) {
      //   return '+';
      // }

      return ''; // 0 或未知类型不显示前缀
    },
        /**
     * 将数字格式化为美元货币字符串
     * @param {number} value - 需要格式化的数字
     * @returns {string} - 例如: $1,234.56
     */
     formatCurrency(value) {
      if (typeof value !== 'number') {
        return '$0.00';
      }
      return value.toLocaleString('en-US', {
        style: 'currency',
        currency: 'USD'
      });
    },

    
    /**
     * 将ISO格式的日期字符串格式化为本地可读格式
     * @param {string} dateString - 日期字符串
     * @returns {string} - 例如: 2025/8/15 14:30:00
     */
    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleString('zh-CN', { hour12: false });
    },

    /**
     * 根据交易类型返回对应的Element Plus标签类型
     * @param {string} type - 交易类型
     * @returns {string} - 'success', 'warning', 'info', 'danger'
     */
    getTypeTagType(type) {
      switch (type) {
        case 'buy':
        case 'deposit':
        case 'mint':
          return 'success';
        case 'sell':
        case 'withdraw':
        case 'burn':
          return 'warning';
        default:
          return 'info';
      }
    },
    
    /**
     * 根据交易状态返回对应的CSS class
     * @param {string} status - 状态
     * @returns {string}
     */
    getStatusClass(status) {
        switch (status) {
            case 'success':
            case 'confirmed':
                return 'status-success';
            case 'pending':
                return 'status-pending';
            case 'failed':
                return 'status-failed';
            default:
                return '';
        }
    },
    
    // (如果需要) 复制到剪贴板功能
    async copyToClipboard(text) {
      try {
        await navigator.clipboard.writeText(text);
        this.$message.success('已复制到剪贴板！');
      } catch (err) {
        console.error('复制失败:', err);
        this.$message.error('复制失败');
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
/* ----- 1. 根布局和页面头部 ----- */
.transaction-history-page {
  /* 解决未占满屏幕的问题，并提供呼吸空间 */
  padding: 32px;
  background-color: #f9fafb;
  min-height: 100vh;
  width: 100%;
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 24px;
}
.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
}
.page-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin-top: 8px;
}

/* ----- 2. 卡片通用样式 ----- */
.box-card {
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03), 0 1px 2px rgba(0, 0, 0, 0.06);
}

/* ----- 3. 工具栏/筛选器 ----- */
.toolbar-card {
  padding: 24px;
}
.toolbar {
  display: flex;
  gap: 16px; /* 元素间隙 */
  align-items: center;
  flex-wrap: wrap; /* 自动换行 */
}
.toolbar-item {
  flex-grow: 1; /* 自动填充空间 */
  min-width: 180px; /* 最小宽度 */
}
.date-picker {
  flex-grow: 2; /* 让日期选择器更宽一些 */
}

/* ----- 4. 表格美化 ----- */
.transactions-table {
  border-radius: 8px;
  overflow: hidden; /* 配合圆角 */
}

/* 深度修改 Element Plus 表格样式 */
:deep(.el-table th.el-table__cell) {
  background-color: #f9fafb;
  color: #6b7280;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 12px;
}
:deep(.el-table tr) {
  transition: background-color 0.2s;
}
:deep(.el-table tr:hover > td.el-table__cell) {
  background-color: #f3f4f6;
}

/* ----- 5. 自定义单元格内容 ----- */
.tx-hash-cell {
  display: flex;
  align-items: center;
  font-family: 'Roboto Mono', monospace;
  color: #248bf1;
  cursor: pointer;
  font-weight: 500;
}
.copy-icon {
  margin-left: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}
.tx-hash-cell:hover .copy-icon {
  opacity: 1;
}

.amount-positive { color: #10b981; font-weight: 600; }
.amount-negative { color: #ef4444; font-weight: 600; }

.status-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}
.status-dot {
  height: 8px;
  width: 8px;
  border-radius: 50%;
  margin-right: 8px;
}
.status-confirmed { background-color: #10b981; }
.status-pending { background-color: #f59e0b; }
.status-failed { background-color: #ef4444; }

.address-flow {
  display: flex;
  align-items: center;
  gap: 8px;
}
.address-tag {
  font-family: 'Roboto Mono', monospace;
  background-color: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.arrow-icon {
  color: #9ca3af;
}


/* ----- 6. 分页 ----- */
.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end; /* 标准居右 */
}
/* 正常状态 */
:deep(.details-button.el-button--primary.is-plain) {
  --el-button-text-color: #fcfcfc;   /* 文字颜色 */
  --el-button-border-color: #4598f7; /* 边框颜色 */
  --el-button-bg-color: #21acec;     /* 背景颜色 */
}

/* 鼠标悬停或聚焦状态 */
:deep(.details-button.el-button--primary.is-plain:hover),
:deep(.details-button.el-button--primary.is-plain:focus) {
  --el-button-hover-text-color: #ffffff; /* 悬停时文字变为白色 */
  --el-button-hover-border-color: #67c23a;
  --el-button-hover-bg-color: #67c23a;   /* 悬停时背景变为深绿色 */
}

/* 美化 el-descriptions 组件 */
:deep(.transaction-details .el-descriptions__label) {
  font-weight: 500;
  color: #909399;
  background: #fafafa;
}
:deep(.transaction-details .el-descriptions__content) {
  color: #303133;
}
:deep(.transaction-details .el-link) {
  font-family: 'Roboto Mono', monospace; /* 对地址和哈希使用等宽字体 */
  font-size: 14px;
}
</style>