<template>
  <div class="dashboard">
    <el-card class="welcome-card">
      <div class="welcome-content">
        <h2>欢迎回来，{{ userInfo.username }}！</h2>
        <p>您的角色：{{ userInfo.role === 'admin' ? '管理员' : userInfo.role === 'issuer' ? '发行方' : '普通用户' }}</p>
      </div>
    </el-card>
    
    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <h3>总资产</h3>
            <p class="stat-value">{{ dashboardData.totalAssets || '0.00' }} HKDC</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <h3>今日交易</h3>
            <p class="stat-value">{{ dashboardData.todayTransactions || 0 }} 笔</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <h3>待处理交易</h3>
            <p class="stat-value">{{ dashboardData.pendingTransactions || 0 }} 笔</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="recent-transactions">
      <template #header>
        <div class="card-header">
          <span>最近交易</span>
        </div>
      </template>
      <el-table :data="dashboardData.recentTransactions" style="width: 100%">
        <el-table-column prop="id" label="交易ID" width="80" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="scope">
            <el-tag :type="getTransactionTypeTag(scope.row.type)">
              {{ getTransactionTypeLabel(scope.row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="scope">
            <span :class="scope.row.amount > 0 ? 'positive' : 'negative'">
              {{ scope.row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getTransactionStatusTag(scope.row.status)">
              {{ getTransactionStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.timestamp) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ElCard, ElRow, ElCol, ElTable, ElTableColumn, ElTag } from 'element-plus'
import request from '@/api/index'

export default {
  name: 'Dashboard',
  components: {
    ElCard,
    ElRow,
    ElCol,
    ElTable,
    ElTableColumn,
    ElTag
  },
  data() {
    return {
      userInfo: {},
      dashboardData: {
        totalAssets: 0,
        todayTransactions: 0,
        pendingTransactions: 0,
        recentTransactions: []
      }
    }
  },
  async mounted() {
    // 获取仪表盘数据
    this.fetchDashboardData()
  },
  methods: {
    async fetchDashboardData() {
      try {
        // 获取驾驶舱数据
        const response = await request.get('/dashboard/data')
        this.dashboardData = response.data
      } catch (error) {
        console.error('获取仪表盘数据失败:', error)
      }
    },
    getTransactionTypeTag(type) {
      const types = { 
        buy: 'success', 
        sell: 'danger', 
        deposit: 'primary', 
        withdraw: 'warning', 
        contract: 'info',
        mint: 'primary',
        burn: 'warning'
      }
      return types[type] || 'info'
    },
    getTransactionTypeLabel(type) {
      const labels = { 
        buy: '买入', 
        sell: '卖出', 
        deposit: '充值', 
        withdraw: '提币', 
        contract: '合约交易',
        mint: '铸造',
        burn: '销毁'
      }
      return labels[type] || type
    },
    getTransactionStatusTag(status) {
      const types = { 
        success: 'success', 
        pending: 'warning', 
        failed: 'danger',
        completed: 'success'
      }
      return types[status] || 'info'
    },
    getTransactionStatusLabel(status) {
      const labels = { 
        success: '成功', 
        pending: '处理中', 
        failed: '失败',
        completed: '已完成'
      }
      return labels[status] || status
    },
    formatDate(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 10px;
}

.welcome-content h2 {
  margin-bottom: 10px;
  color: #303133;
}

.welcome-content p {
  color: #606266;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content h3 {
  margin-bottom: 10px;
  color: #606266;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.recent-transactions {
  margin-top: 20px;
}

.card-header {
  font-weight: bold;
  color: #303133;
}

.positive {
  color: #67c23a;
}

.negative {
  color: #f56c6c;
}
</style>