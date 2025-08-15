<template>
  <div class="reserve-management-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">储备金实时仪表盘</h1>
      <div class="last-updated">
        <span v-if="!loading">最后更新于: {{ formatDate(reserveData.lastUpdated) }}</span>
        <span v-else>正在同步数据...</span>
      </div>
    </div>
    <el-card class="card">
      <div class="card-title">储备金管理</div>
      <p>在这里可以管理储备金资产。</p>
      <el-button type="primary" @click="$router.push('/reserve-admin')">储备金管理</el-button>
    </el-card>
    <!-- 顶部关键指标 (KPI) 卡片 -->
    <el-row :gutter="24" class="kpi-row">
      <el-col :span="6">
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background: #e6f7ff;">
            <i class="el-icon-bank-card" style="color: #1890ff;"></i>
          </div>
          <div class="kpi-text">
            <p class="kpi-label">总储备价值 (USD)</p>
            <!-- 使用数字滚动动画组件 -->
            <animated-number class="kpi-value" :value="reserveData.totalReserve" :duration="10" />
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background: #f6ffed;">
            <i class="el-icon-files" style="color: #52c41a;"></i>
          </div>
          <div class="kpi-text">
            <p class="kpi-label">资产种类</p>
            <animated-number class="kpi-value" :value="reserveData.assetTypes" />
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background: #fffbe6;">
            <i class="el-icon-finished" style="color: #faad14;"></i>
          </div>
          <div class="kpi-text">
            <p class="kpi-label">流通中稳定币</p>
            <animated-number class="kpi-value" :value="reserveData.circulatingSupply" :duration="10" />
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background: #fff1f0;">
            <i class="el-icon-pie-chart" style="color: #f5222d;"></i>
          </div>
          <div class="kpi-text">
            <p class="kpi-label">抵押率</p>
            <animated-number class="kpi-value" :value="reserveData.collateralRatio" :duration="8" format="{value}%" />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 主内容区：资产分布图表 和 资产详情列表 -->
    <el-row :gutter="24">
      <!-- 左侧：资产分布甜甜圈图 -->
      <el-col :span="8">
        <el-card class="box-card chart-card">
          <template #header>
            <div class="card-header">
              <span>资产分布</span>
            </div>
          </template>
          <!-- ECharts 图表容器 -->
          <div ref="pieChart" class="pie-chart-container" v-loading="loading"></div>
        </el-card>
      </el-col>

      <!-- 右侧：多资产监控详情列表 -->
      <el-col :span="16">
        <el-card class="box-card asset-list-card">
           <template #header>
            <div class="card-header">
              <span>资产详情列表</span>
               <el-button type="text" @click="fetchReserveData" icon="el-icon-refresh">手动刷新</el-button>
            </div>
          </template>
          <el-table :data="reserveData.assets" style="width: 100%" v-loading="loading" height="400">
            <el-table-column prop="name" label="资产名称" width="180">
                <template #default="{ row }">
                    <div class="asset-name-cell">
                        <span class="asset-icon" :style="{ backgroundColor: getAssetColor(row.name) }"></span>
                        <span>{{ row.name }}</span>
                    </div>
                </template>
            </el-table-column>
            <el-table-column prop="value_usd" label="价值 (USD)" align="right" sortable>
              <template #default="{ row }">
                {{ formatCurrency(row.value_usd) }}
              </template>
            </el-table-column>
            <el-table-column prop="balance" label="持有数量" align="right" sortable>
              <template #default="{ row }">
                {{ formatNumber(row.balance) }}
              </template>
            </el-table-column>
            <el-table-column prop="percentage" label="占比" width="120" sortable>
              <template #default="{ row }">
                <el-progress :percentage="parseFloat(row.percentage.toFixed(2))" :color="getAssetColor(row.name)" :stroke-width="10"></el-progress>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
// 1. 引入 ECharts
// 确保你已经安装了 echarts: npm install echarts
import * as echarts from 'echarts';
import {reserveAPI} from '@/api/reserve';
// 2. 引入一个简单的数字动画组件（可选，但效果很棒）
// 你需要创建一个 AnimatedNumber.vue 文件，代码在下面提供
import AnimatedNumber from '../components/AnimatedNumber.vue'; 


export default {
  name: 'ReserveManagement',
  components: {
    AnimatedNumber // 注册数字动画组件
  },
  data() {
    return {
      loading: true,
      reserveData: {
        totalReserve: 0,
        assetTypes: 0,
        circulatingSupply: 0,
        collateralRatio: 0,
        lastUpdated: null,
        assets: [],
      },
      timerId: null,
      pieChartInstance: null, // 用于存放ECharts实例
      // 预定义的颜色映射表，让图表和列表颜色保持一致
      assetColorMap: {
        '美元现金储备': '#5470C6',
        '美国国债': '#91CC75',
        '比特币 (BTC)': '#FAC858',
        '以太坊 (ETH)': '#EE6666',
        '黄金': '#73C0DE',
      }
    }
  },
  computed: {
  },
  mounted() {
    this.initPieChart(); // 初始化图表
    this.fetchReserveData();
    // this.timerId = setInterval(this.fetchReserveData, 5000); // 5秒刷新一次
  },
  beforeUnmount() {
    clearInterval(this.timerId);
    if (this.pieChartInstance) {
      this.pieChartInstance.dispose(); // 销毁图表实例，防止内存泄漏
    }
  },
  methods: {
    async fetchReserveData() {
      // 第一次加载时显示loading，后续刷新则静默进行
      if (!this.reserveData.lastUpdated) {
          this.loading = true;
      }
      try {
        const response = await reserveAPI.getReserveData();
        this.reserveData = response.data;
        this.updatePieChart(); // 获取到新数据后，更新图表
      } catch (error) {
        console.error('获取储备金数据失败:', error);
      } finally {
        this.loading = false;
      }
    },
    // 初始化 ECharts 饼图
    initPieChart() {
      const chartDom = this.$refs.pieChart;
      this.pieChartInstance = echarts.init(chartDom);
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: <br/>{c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          top: 'center',
          textStyle: {
              color: '#666'
          }
        },
        series: [
          {
            name: '资产分布',
            type: 'pie',
            radius: ['50%', '70%'], // 创建甜甜圈图
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '20',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: [] // 初始数据为空
          }
        ]
      };
      this.pieChartInstance.setOption(option);
    },
    // 更新 ECharts 饼图数据
    updatePieChart() {
      if (!this.pieChartInstance) return;
      this.pieChartInstance.setOption({
        series: [
          {
            data: this.reserveData.assets.map(asset => ({
              value: asset.value_usd,
              name: asset.name
            }))
          }
        ],
        // 动态设置颜色
        color: this.reserveData.assets.map(asset => this.getAssetColor(asset.name))
      });
    },
    getAssetColor(assetName) {
        return this.assetColorMap[assetName] || '#999'; // 如果没匹配到，返回一个默认灰色
    },
    // 各种格式化辅助函数
    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleString('zh-CN', { hour12: false });
    },
    formatNumber(value) {
      if (typeof value !== 'number') return '0.00';
      return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },
    formatCurrency(value) {
      if (typeof value !== 'number') return '$0.00';
      return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
    }
  }
}
</script>

<style scoped>
/* ----- 主题色和变量 ----- */
:root {
  --primary-color: #409EFF;
  --success-color: #67C23A;
  --warning-color: #E6A23C;
  --danger-color: #F56C6C;
  --text-primary: #303133;
  --text-regular: #606266;
  --text-secondary: #909399;
  --bg-color: #f7f8fa;
  --card-bg-color: #ffffff;
  --border-color: #e4e7ed;
}

/* ----- 页面和卡片基础样式 ----- */
.reserve-management-page {
  padding: 24px;
  background-color: var(--bg-color);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
}

.last-updated {
  font-size: 14px;
  color: var(--text-secondary);
}

.box-card {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background-color: var(--card-bg-color);
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

/* ----- 顶部KPI卡片 ----- */
.kpi-row {
  margin-bottom: 24px;
}
.kpi-card {
  display: flex;
  align-items: center;
  background-color: var(--card-bg-color);
  padding: 24px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}
.kpi-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}

.kpi-icon-wrapper {
  font-size: 32px;
  padding: 18px;
  border-radius: 50%;
  margin-right: 20px;
}
.kpi-text {
  line-height: 1.4;
}
.kpi-label {
  margin: 0 0 8px 0;
  color: var(--text-regular);
  font-size: 14px;
}
.kpi-value {
  margin: 0;
  font-size: 26px;
  font-weight: bold;
  color: var(--text-primary);
}

/* ----- 图表和表格区域 ----- */
.chart-card, .asset-list-card {
  min-height: 460px; /* 保证卡片高度一致 */
}

.pie-chart-container {
  width: 100%;
  height: 400px; /* ECharts容器必须有明确的高度 */
}

.asset-name-cell {
    display: flex;
    align-items: center;
}
.asset-icon {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
}

/* ----- Element Plus 深度样式修改 ----- */
::v-deep .el-table th > .cell {
  font-weight: 600;
  color: var(--text-regular);
}

::v-deep .el-table .el-progress-bar__outer {
  background-color: #ebeef5;
}
</style>