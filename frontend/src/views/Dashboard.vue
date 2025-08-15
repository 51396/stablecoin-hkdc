<template>
  <div class="dashboard-container">
    
    <!-- 1. 欢迎和问候区 -->
    <el-card class="box-card welcome-card">
      <div class="welcome-content">
        <el-avatar :size="60" icon="el-icon-user-solid" class="welcome-avatar"></el-avatar>
        <div class="welcome-text">
          <h2 class="welcome-title">欢迎回来，{{ userInfo.username || '用户' }}！</h2>
          <p class="welcome-subtitle">
            您的角色：
            <el-tag size="small">{{ userInfo.role === 'admin' ? '管理员' : userInfo.role === 'issuer' ? '发行方' : '普通用户' }}</el-tag>
          </p>
        </div>
      </div>
    </el-card>

    <!-- 2. 核心指标 KPI 卡片区 (复用之前的设计) -->
    <el-row :gutter="24" class="kpi-row">
      <el-col :span="6">
        <div class="kpi-card">
          <p class="kpi-label">市值 (Market Cap)</p>
          <animated-number class="kpi-value" :value="metricsData.marketCap" :fraction-digits="2" format="${value}" />
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card">
          <p class="kpi-label">流通量 (Circulating Supply)</p>
          <animated-number class="kpi-value" :value="metricsData.circulatingSupply" :fraction-digits="2" />
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card">
          <p class="kpi-label">24小时交易量</p>
          <animated-number class="kpi-value" :value="metricsData.volume24h" :fraction-digits="2" format="${value}" />
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card">
          <p class="kpi-label">24小时活跃地址</p>
          <animated-number class="kpi-value" :value="metricsData.activeAddresses24h" />
        </div>
      </el-col>
    </el-row>

    <!-- 3. 主图表区 -->
    <el-row :gutter="24">
      <el-col :span="16">
        <el-card class="box-card chart-card">
          <template #header>
            <div class="card-header">市值历史趋势 (30天)</div>
          </template>
          <div ref="historyChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="box-card chart-card">
          <template #header>
            <div class="card-header">24小时交易量分布</div>
          </template>
          <div ref="barChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 4. 列表区：实时交易 和 最近交易 -->
    <el-row :gutter="24">
      <!-- 左侧：实时大额交易 -->
      <el-col :span="12">
        <el-card class="box-card list-card">
          <template #header>
            <div class="card-header">实时大额交易</div>
          </template>
          <div class="transaction-feed">
            <transition-group name="list" tag="ul">
              <li v-for="tx in metricsData.realTimeTransactions" :key="tx.hash" class="tx-item">
                <span class="tx-time">{{ formatTimeAgo(tx.timestamp) }}</span>
                <span class="tx-info">
                  From <span class="tx-address">{{ truncateAddress(tx.from_addr) }}</span>
                  To <span class="tx-address">{{ truncateAddress(tx.to_addr) }}</span>
                </span>
                <span class="tx-amount">{{ formatCurrency(tx.amount) }}</span>
              </li>
            </transition-group>
             <el-empty v-if="!metricsData.realTimeTransactions || metricsData.realTimeTransactions.length === 0" description="暂无大额交易"></el-empty>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：最近交易记录 -->
      <el-col :span="12">
         <el-card class="box-card list-card">
           <template #header>
            <div class="card-header">最近交易记录</div>
          </template>
          <el-table :data="recentTransactions" stripe style="width: 100%" height="300">
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getTransactionTypeTag(row.type)" size="small">{{ getTransactionTypeLabel(row.type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="金额" prop="amount" align="right">
                 <template #default="{ row }">
                   {{ formatCurrency(row.amount) }}
                 </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
                 <template #default="{ row }">
                   <el-tag :type="row.status === 'confirmed' ? 'success' : 'warning'" size="small">{{ getTransactionStatusLabel(row.status) }}</el-tag>
                 </template>
            </el-table-column>
            <el-table-column label="时间" prop="timestamp" width="160">
                <template #default="{ row }">
                   {{ formatDate(row.timestamp) }}
                 </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

  </div>
</template>


<script>
import { ElCard, ElRow, ElCol, ElTable, ElTableColumn, ElTag } from 'element-plus'
import request from '@/api/index'
import { reserveAPI } from '@/api/reserve'
import * as echarts from 'echarts'
import AnimatedNumber from '../components/AnimatedNumber.vue'

export default {
  name: 'Dashboard',
  components: {
    ElCard,
    ElRow,
    ElCol,
    ElTable,
    ElTableColumn,
    ElTag,
    AnimatedNumber
  },
  data() {
    return {
      loading: true,
      userInfo: {},
      dashboardData: {
        totalAssets: 0,
        todayTransactions: 0,
        pendingTransactions: 0,
        recentTransactions: []
      },
      metricsData: {
        marketCap: 0,
        circulatingSupply: 0,
        volume24h: 0,
        activeAddresses24h: 0,
        lastUpdated: null,
        marketCapHistory30d: [],
        volumeDistribution: [],
        realTimeTransactions: [],
      },
      historyChart: null,
      barChart: null
    }
  },
  async mounted() {
    // 获取仪表盘数据
    this.fetchDashboardData()
    // 获取核心指标数据
    this.fetchMetricsData()
    // 初始化图表
    this.$nextTick(() => {
      this.initCharts()
    })
  },
  beforeUnmount() {
    if (this.historyChart) {
      this.historyChart.dispose()
    }
    if (this.barChart) {
      this.barChart.dispose()
    }
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
    async fetchMetricsData() {
      try {
        const response = await reserveAPI.getCoreMetrics()
        this.metricsData = response.data
        this.updateCharts()
      } catch (error) {
        console.error('获取核心指标失败:', error)
      } finally {
        this.loading = false
      }
    },
    initCharts() {
      this.historyChart = echarts.init(this.$refs.historyChartRef)
      this.barChart = echarts.init(this.$refs.barChartRef)

      this.historyChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', boundaryGap: false },
        yAxis: { type: 'value', scale: true, axisLabel: { formatter: val => `${(val/1_000_000).toFixed(1)}M` } },
        grid: { left: '10%', right: '5%', top: '15%', bottom: '15%' },
        series: [{ type: 'line', smooth: true, showSymbol: false, areaStyle: {} }]
      })

      this.barChart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        xAxis: { type: 'value', boundaryGap: [0, 0.01] },
        yAxis: { type: 'category', data: [] },
        grid: { left: '25%', right: '10%', top: '5%', bottom: '5%' },
        series: [{ type: 'bar', data: [] }]
      })
    },
    updateCharts() {
      if (!this.historyChart || !this.barChart) return
      
      this.historyChart.setOption({
        xAxis: { data: this.metricsData.marketCapHistory30d.map(p => new Date(p.timestamp).toLocaleDateString()) },
        series: [{ data: this.metricsData.marketCapHistory30d.map(p => p.value) }]
      })

      // 对交易量分布数据排序，让图表更好看
      const sortedDistribution = [...this.metricsData.volumeDistribution].sort((a, b) => a.volume - b.volume)
      this.barChart.setOption({
        yAxis: { data: sortedDistribution.map(d => d.source) },
        series: [{ data: sortedDistribution.map(d => d.volume) }]
      })
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
    },
    formatTimeAgo(dateStr) {
      if(!dateStr) return ''
      const seconds = Math.floor((new Date() - new Date(dateStr)) / 1000)
      return seconds < 60 ? `${seconds}秒前` : `${Math.floor(seconds/60)}分钟前`
    },
    formatCurrency(val) {
      if (typeof val !== 'number') return '$0.00'
      return val.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
    },
    truncateAddress(addr) {
      return addr ? `${addr.slice(0, 6)}...${addr.slice(-4)}` : ''
    }
  }
}
</script>

<style scoped>
/* ----- 主题和布局 ----- */
.dashboard-container {
  padding: 24px;
  background-color: #f7f8fa;
  min-height: 100vh;
}

.box-card {
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  background-color: #ffffff;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

/* ----- 欢迎区 ----- */
.welcome-card {
  margin-bottom: 24px;
}
.welcome-content {
  display: flex;
  align-items: center;
}
.welcome-avatar {
  margin-right: 20px;
  background-color: #409EFF; /* 主题色 */
}
.welcome-text {
  line-height: 1.4;
}
.welcome-title {
  font-size: 22px;
  font-weight: 600;
  margin: 0 0 8px 0;
}
.welcome-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* ----- KPI 卡片 ----- */
.kpi-row {
  margin-bottom: 0; /* 因为 box-card 已经有 margin-bottom */
}
.kpi-card {
  background-color: #fff;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}
.kpi-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}
.kpi-label {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 15px;
}
.kpi-value {
  margin: 0;
  font-size: 32px;
  font-weight: bold;
}

/* ----- 图表卡片 ----- */
.chart-card {
  height: 400px;
  display: flex;
  flex-direction: column;
}
::v-deep .el-card__body {
  flex-grow: 1;
  padding: 10px;
}
.chart-container {
  width: 100%;
  height: 100%;
}

/* ----- 列表卡片 ----- */
.list-card {
    height: 380px; /* 统一列表卡片高度 */
    display: flex;
    flex-direction: column;
}
/* 实时交易Feed */
.transaction-feed {
    height: 100%;
    overflow-y: auto;
}
.transaction-feed ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.tx-item {
  display: flex;
  align-items: center;
  padding: 12px 5px;
  border-bottom: 1px solid #f0f2f5;
  font-size: 14px;
}
.tx-time { width: 80px; color: #909399; }
.tx-info { flex-grow: 1; }
.tx-address {
  font-family: monospace;
  background-color: #f4f4f5;
  padding: 2px 4px;
  border-radius: 4px;
}
.tx-amount { font-weight: 600; width: 150px; text-align: right; }

/* 列表动画 */
.list-enter-active, .list-leave-active { transition: all 0.5s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: translateY(-20px); }

/* 最近交易表格 */
::v-deep .el-table th > .cell {
  font-weight: 600;
  color: #555;
  background-color: #fafbfe;
}

</style>