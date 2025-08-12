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
        
        <el-table-column prop="currency" label="币种" width="80" />
        
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
          <el-descriptions-item label="状态">{{ getStatusLabel(selectedTransaction.status) }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ formatDate(selectedTransaction.timestamp) }}</el-descriptions-item>
          <el-descriptions-item label="手续费">{{ selectedTransaction.fee || '0.00' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { List, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
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
      transactions: [
        { id: 'TX001', type: 'buy', amount: '1000.00', currency: 'USDT', status: 'success', timestamp: '2024-01-15 10:30:00', fee: '2.50' },
        { id: 'TX002', type: 'sell', amount: '500.00', currency: 'USDT', status: 'pending', timestamp: '2024-01-15 09:15:00', fee: '1.25' },
        { id: 'TX003', type: 'deposit', amount: '2000.00', currency: 'CNY', status: 'success', timestamp: '2024-01-14 16:45:00', fee: '0.00' },
        { id: 'TX004', type: 'withdraw', amount: '800.00', currency: 'CNY', status: 'success', timestamp: '2024-01-14 14:20:00', fee: '5.00' }
      ]
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
      const types = { buy: 'success', sell: 'danger', deposit: 'primary', withdraw: 'warning' }
      return types[type] || 'info'
    },
    getTypeLabel(type) {
      const labels = { buy: '买入', sell: '卖出', deposit: '充值', withdraw: '提币' }
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
    refreshData() {
      ElMessage.success('数据已刷新')
    },
    viewDetails(transaction) {
      this.selectedTransaction = transaction
      this.showDetailsDialog = true
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
    },
    handleCurrentChange(val) {
      this.currentPage = val
    }
  }
}
</script>

<style scoped>
.filters { display: flex; gap: 12px; align-items: center; }
.transactions-table :deep(.el-table) { background: transparent; }
.transactions-table :deep(.el-table th) { background: rgba(255,255,255,0.02); }
.amount-text { font-weight: 600; color: #e8eefc; }
.pagination-wrapper { margin-top: 20px; text-align: center; }
.transaction-details { padding: 20px 0; }
</style>
