<template>
  <!-- 1. 根容器，应用深色背景和全宽布局 -->
  <div class="light-tech-dashboard">
    
    <!-- 2. 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">数据驾驶舱</h1>
        <p class="page-subtitle">稳定币生态系统实时监控</p>
      </div>
    </div>

    <!-- 3. 顶部KPI卡片区 - 使用el-row -->
    <el-row :gutter="32">
      <el-col :xs="32" :sm="12" :lg="6">
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="--icon-bg: #e6f7ff; --icon-color: #1890ff;">
            <i class="el-icon-data-line"></i>
          </div>
          <div class="kpi-text">
            <p class="kpi-label">实时市值 (Market Cap)</p>
            <span class="kpi-value">$ {{ formatLargeNumber(metricsData.marketCap) }}</span>
            <!-- <vue-count-to :start-val="0" :end-val="metricsData.marketCap" :duration="2000" :decimals="2" class="kpi-value" ></vue-count-to> -->
          </div>
        </div>
      </el-col>
      <!-- ... 其他三个KPI卡片也做类似修改 ... -->
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="kpi-card">
           <div class="kpi-icon-wrapper" style="--icon-bg: #f6ffed; --icon-color: #52c41a;">
            <i class="el-icon-coin"></i>
          </div>
          <div class="kpi-text">
            <p class="kpi-label">流通供应量</p>
            <span class="kpi-value">$ {{ formatLargeNumber(metricsData.circulatingSupply) }}</span>
            <!-- <vue-count-to :start-val="0" :end-val="metricsData.circulatingSupply" :duration="2000" :decimals="2" class="kpi-value"></vue-count-to> -->
          </div>
        </div>
      </el-col>
       <el-col :xs="24" :sm="12" :lg="6">
        <div class="kpi-card">
           <div class="kpi-icon-wrapper" style="--icon-bg: #fffbe6; --icon-color: #faad14;">
            <i class="el-icon-sort"></i>
          </div>
          <div class="kpi-text">
            <p class="kpi-label">24小时交易量</p>
            <span class="kpi-value">$ {{ formatLargeNumber(metricsData.volume24h) }}</span>
            <!-- <vue-count-to :start-val="0" :end-val="metricsData.volume24h" :duration="2000" :decimals="2" class="kpi-value" prefix="$"></vue-count-to> -->
          </div>
        </div>
      </el-col>
       <el-col :xs="24" :sm="12" :lg="6">
        <div class="kpi-card">
           <div class="kpi-icon-wrapper" style="--icon-bg: #fff1f0; --icon-color: #f5222d;">
            <i class="el-icon-user"></i>
          </div>
          <div class="kpi-text">
            <p class="kpi-label">24小时活跃地址</p>
            <span class="kpi-value">{{ formatLargeNumber(metricsData.activeAddresses24h) }}</span>
            <!-- <vue-count-to :start-val="0" :end-val="metricsData.activeAddresses24h" :duration="2000" class="kpi-value"></vue-count-to> -->
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 4. 主内容区 - 经典的两栏布局 -->
    <el-row :gutter="24">

<!-- 左侧主栏 (占据2/3空间) -->
<el-col :xs="24" :lg="16">
  <!-- 历史趋势图 - 作为视觉焦点 -->
  <div class="content-card focus-card">
    <div class="card-header">
      <h3><i class="el-icon-data-line"></i> 市值历史趋势 (30天)</h3>
      <el-tag effect="dark" size="small">Real-time</el-tag>
    </div>
    <div ref="historyChartRef" class="chart-container" v-loading="loading"></div>
  </div>
</el-col>

<!-- 右侧副栏 (占据1/3空间) -->
<el-col :xs="24" :lg="8">
  <div class="sidebar-stack">
    <!-- 交易量分布图 -->
    <div class="content-card sidebar-card">
      <div class="card-header">
        <h3><i class="el-icon-pie-chart"></i> 交易量来源</h3>
      </div>
      <div ref="barChartRef" class="chart-container" v-loading="loading"></div>
    </div>
    
    <!-- 最近交易记录 -->
    <div class="content-card sidebar-card">
      <div class="card-header">
        <h3><i class="el-icon-document"></i> 最近交易</h3>
      </div>
      <div class="transaction-feed">
        <el-table :data="metricsData.realTimeTransactions" style="width: 100%" height="250px" class="compact-table">
          
          <!-- 第一列：交易哈希 (带截断和复制功能) -->
          <el-table-column label="交易哈希 (Tx Hash)" min-width="150">
            <template #default="{ row }">
              <div class="tx-hash-cell" :title="row.hash">
                <span>{{ truncateAddress(row.hash) }}</span>
                <i class="el-icon-copy-document copy-icon" @click="copyToClipboard(row.hash)"></i>
              </div>
            </template>
          </el-table-column>

          <!-- 第二列：交易金额 -->
          <el-table-column label="金额 (Amount)" align="right">
            <template #default="{ row }">
              <div class="tx-amount-cell" :class="{ 'large-tx': row.amount > 100000 }">
                {{ formatCurrency(row.amount) }}
              </div>
            </template>
          </el-table-column>

          <!-- 第三列：交易时间 (显示为“多久以前”) -->
          <el-table-column label="时间 (Time)" align="right" width="120">
            <template #default="{ row }">
                <span class="tx-time-cell">{{ formatTimeAgo(row.timestamp) }}</span>
            </template>
          </el-table-column>

        </el-table>
        <el-empty v-if="!metricsData.realTimeTransactions || metricsData.realTimeTransactions.length === 0" description="暂无交易"></el-empty>
      </div>
    </div>
  </div>
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
import { CountTo } from 'vue-count-to'; // <-- 引入新组件
export default {
  name: 'Dashboard',
  components: {
    ElCard,
    ElRow,
    ElCol,
    ElTable,
    ElTableColumn,
    ElTag,
    // AnimatedNumber,
    'vue-count-to': CountTo,
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
      // 为浅色主题配置更协调的颜色
      const colors = ['#5470C6', '#91CC75', '#FAC858', '#EE6666', '#73C0DE'];
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
        series: [{ type: 'bar', data: [] }],
        color: colors
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
    },
        /**
     * 将大数字格式化为带单位的缩写 (K, M, B)
     * @param {number} num - 需要格式化的数字
     * @param {number} digits - 保留的小数位数
     * @returns {string} - 例如: 1.23M
     */
     formatLargeNumber(num, digits = 2) {
      if (typeof num !== 'number' || num === 0) return '0';
      
      const si = [
        { value: 1, symbol: "" },
        { value: 1E3, symbol: "K" }, // 千
        { value: 1E6, symbol: "M" }, // 百万
        { value: 1E9, symbol: "B" }, // 十亿
        { value: 1E12, symbol: "T" }  // 万亿
      ];
      
      // 创建一个正则表达式来移除尾随的.00或.0
      const rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
      
      // 找到合适的单位
      let i;
      for (i = si.length - 1; i > 0; i--) {
        if (num >= si[i].value) {
          break;
        }
      }
      
      // 格式化数字并替换尾随的零
      const formattedNum = (num / si[i].value).toFixed(digits).replace(rx, "$1");
      
      return formattedNum + si[i].symbol;
    }
  }
}
</script>

<style scoped>
/* ----- 1. 根容器和主题 ----- */
.light-tech-dashboard {
  background-color: #f9fafb;
  width: 100%;
  box-sizing: border-box;
}

/* ----- 2. 页面头部 ----- */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
/* ... (header-right 等样式保持不变) ... */

/* ----- 3. 栅格行间距 ----- */
.el-row {
  margin-bottom: 24px;
}
.el-row:last-child {
  margin-bottom: 0;
}


/* ----- 4. KPI 卡片 ----- */
.kpi-card {
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}
.kpi-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
.kpi-icon-wrapper {
  font-size: 28px;
  padding: 16px;
  border-radius: 50%;
  margin-right: 20px;
  background-color: var(--icon-bg);
  color: var(--icon-color);
}
.kpi-text {
  line-height: 1.4;
}
.kpi-label {
  margin: 0 0 8px 0;
  color: #6b7280;
  font-size: 14px;
}
.kpi-value {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  font-family: 'Roboto Mono', monospace;
}

/* ----- 5. 主内容卡片 (替换 box-card) ----- */
.content-card {
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
}
.card-header {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}
.chart-card, .list-card {
  height: 420px; /* 统一高度 */
}
/* 通用内容卡片样式 */
.content-card {
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  padding: 24px;
  margin-bottom: 24px; /* 统一的下外边距 */
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}
.content-card:hover {
  box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.07);
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}
.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
}
.card-header h3 i {
  margin-right: 8px;
  color: #409EFF; /* 主题色 */
  font-size: 18px;
}

/* 主图表卡片样式 */
.focus-card {
  height: 624px; /* 占据更大高度 */
}

/* 右侧边栏布局 */
.sidebar-stack {
  display: flex;
  flex-direction: column;
  gap: 24px; /* 使用 gap 创建间隙 */
}
.sidebar-card {
  flex-grow: 1; /* 让两个卡片平分空间 */
  margin-bottom: 0; /* 因为 gap 已经处理了间距 */
  min-height: 300px;
}


/* 图表容器 */
.chart-container {
  width: 100%;
  flex-grow: 1;
}

/* ----- 5. 紧凑型表格美化 ----- */
.compact-table {
  flex-grow: 1;
}
/* 移除 el-table 默认的 padding 和 border */
::v-deep .el-table .el-card__body {
    padding: 0 !important;
}
::v-deep .compact-table {
    border: none;
}
/* 透明化表头 */
::v-deep .compact-table th {
  background-color: transparent !important;
  padding: 8px 0 !important;
}
::v-deep .compact-table th > .cell {
  font-weight: 500;
  font-size: 12px;
  color: #9ca3af;
  text-transform: none;
}
/* 单元格样式 */
::v-deep .compact-table td {
    padding: 10px 0 !important;
    border-bottom: 1px solid #f3f4f6;
}
::v-deep .compact-table tr:last-child td {
    border-bottom: none;
}
::v-deep .compact-table tr:hover > td {
    background-color: #f9fafb !important;
}
/* 自定义单元格内容 */
.tx-type-cell {
  display: flex;
  align-items: center;
}
.status-dot {
  height: 8px;
  width: 8px;
  border-radius: 50%;
  margin-right: 8px;
  flex-shrink: 0; /* 防止被挤压 */
}
.status-success { background-color: #10b981; }
.status-pending { background-color: #f59e0b; }
.tx-amount-cell {
  font-weight: 600;
  font-family: 'Roboto Mono', monospace;
}


/* 深度修改 el-card 样式 */
::v-deep .el-card__header {
    padding: 18px 24px;
    border-bottom: 1px solid #f3f4f6;
}
::v-deep .el-card__body {
  flex-grow: 1; /* 让内容区占满剩余空间 */
  padding: 24px;
  display: flex;
  flex-direction: column;
}

/* ----- 6. 图表和列表容器 ----- */
.chart-container {
  width: 100%;
  height: 100%;
  flex-grow: 1;
}

/* 表格样式 */
::v-deep .el-table {
    border-top: 1px solid #ebeef5;
}
::v-deep .el-table th > .cell {
  font-weight: 600;
  color: #6b7280;
  font-size: 12px;
  text-transform: uppercase;
}
::v-deep .el-table tr:hover > td {
    background-color: #f9fafb;
}
</style>