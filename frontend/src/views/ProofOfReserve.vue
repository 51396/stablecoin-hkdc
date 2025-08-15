<template>
  <div class="por-page">
    <div class="por-header">
      <h1>储备金证明 (Proof of Reserve)</h1>
      <p class="subtitle">我们承诺100%的透明度，所有储备金均由可信第三方每日审计验证。</p>
    </div>

    <!-- 最新报告摘要 -->
    <el-card class="box-card latest-report-card" v-loading="loading">
      <div v-if="latestReport">
        <div class="latest-report-header">
          <h2>最新审计报告摘要</h2>
          <span>报告于: {{ formatDate(latestReport.report_date) }}</span>
        </div>
        <el-row :gutter="30" class="kpi-row">
          <el-col :span="8">
            <div class="kpi-item">
              <p class="kpi-label">总储备金价值 (USD)</p>
              <p class="kpi-value positive">{{ formatCurrency(latestReport.total_reserve_usd) }}</p>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="kpi-item">
              <p class="kpi-label">链上总供应量</p>
              <p class="kpi-value">{{ formatCurrency(latestReport.total_supply) }}</p>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="kpi-item">
              <p class="kpi-label">抵押率</p>
              <p class="kpi-value" :class="latestReport.collateral_ratio >= 100 ? 'positive' : 'negative'">
                {{ latestReport.collateral_ratio.toFixed(2) }}%
              </p>
            </div>
          </el-col>
        </el-row>
        <div class="attestation-info">
          <i class="el-icon-lock"></i>
          <span>由 <strong>{{ latestReport.attestation_firm }}</strong> 提供数据证明</span>
        </div>
      </div>
       <el-empty v-else-if="!loading" description="暂无报告数据"></el-empty>
    </el-card>

    <!-- 历史报告列表 -->
    <el-card class="box-card history-card">
      <template #header>
        <div class="card-header">
          <h3>历史审计报告</h3>
        </div>
      </template>
      <el-table :data="reports" v-loading="loading">
        <el-table-column label="报告日期" prop="report_date" width="200">
          <template #default="{ row }">{{ formatDate(row.report_date) }}</template>
        </el-table-column>
        <el-table-column label="总储备金 (USD)" prop="total_reserve_usd" align="right">
          <template #default="{ row }">{{ formatCurrency(row.total_reserve_usd) }}</template>
        </el-table-column>
        <el-table-column label="总供应量" prop="total_supply" align="right">
           <template #default="{ row }">{{ formatCurrency(row.total_supply) }}</template>
        </el-table-column>
        <el-table-column label="抵押率" prop="collateral_ratio" align="center">
          <template #default="{ row }">
            <el-tag :type="row.collateral_ratio >= 100 ? 'success' : 'danger'">
              {{ row.collateral_ratio.toFixed(2) }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="证明来源" prop="attestation_firm"></el-table-column>
        <el-table-column label="详细报告" align="center">
          <template #default="{ row }">
            <a :href="row.report_url" target="_blank" class="report-link">
              <el-button type="primary" plain size="mini">查看详情</el-button>
            </a>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
// Options API 风格
import axios from 'axios';

export default {
  name: 'ProofOfReserve',
  data() {
    return {
      loading: true,
      reports: []
    }
  },
  computed: {
    latestReport() {
      // 总是返回报告列表中的第一个（最新的）
      return this.reports.length > 0 ? this.reports[0] : null;
    }
  },
  mounted() {
    this.fetchReports();
  },
  methods: {
    async fetchReports() {
      this.loading = true;
      try {
        const response = await axios.get('/api/v1/reserves/proof-of-reserve');
        this.reports = response.data;
      } catch (error) {
        console.error("获取储备金证明报告失败:", error);
        // this.$message.error(...)
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute:'2-digit' });
    },
    formatCurrency(value) {
      if (typeof value !== 'number') return '$0.00';
      return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
    }
  }
}
</script>

<style scoped>
.por-page {
  padding: 30px;
  background-color: #f7f8fa;
  font-family: sans-serif;
}

.por-header {
  text-align: center;
  margin-bottom: 30px;
}

.por-header h1 {
  font-size: 36px;
  color: #303133;
  margin-bottom: 10px;
}

.por-header .subtitle {
  font-size: 18px;
  color: #606266;
}

.box-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.07);
  margin-bottom: 30px;
}

.latest-report-card {
  padding: 20px;
}

.latest-report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.latest-report-header h2 {
  font-size: 20px;
  color: #303133;
}

.latest-report-header span {
  font-size: 14px;
  color: #909399;
}

.kpi-item .kpi-label {
  font-size: 15px;
  color: #606266;
  margin-bottom: 8px;
}

.kpi-item .kpi-value {
  font-size: 28px;
  font-weight: bold;
}

.positive { color: #67c23a; }
.negative { color: #f56c6c; }

.attestation-info {
  margin-top: 25px;
  padding-top: 15px;
  border-top: 1px solid #e4e7ed;
  color: #909399;
  display: flex;
  align-items: center;
  font-size: 14px;
}

.attestation-info i {
  margin-right: 8px;
  font-size: 16px;
}

.history-card .card-header h3 {
  font-size: 18px;
  font-weight: 600;
}

.report-link {
  text-decoration: none;
}
</style>