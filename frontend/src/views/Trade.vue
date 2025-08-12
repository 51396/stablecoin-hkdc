<template>
  <div class="page">
    <el-row :gutter="24">
      <el-col :span="16">
        <el-card class="card">
          <div class="card-title">
            <el-icon><TrendCharts /></el-icon>
            <span>稳定币交易</span>
          </div>
          
          <el-tabs v-model="activeTab" class="trade-tabs">
            <el-tab-pane label="买入" name="buy">
              <el-form :model="buyForm" label-position="top">
                <el-form-item label="交易金额">
                  <el-input-number 
                    v-model="buyForm.amount" 
                    :min="0.01" 
                    :precision="2"
                    :step="0.01"
                    placeholder="请输入交易金额"
                    class="w-100"
                  />
                </el-form-item>
                <el-form-item label="支付方式">
                  <el-select v-model="buyForm.paymentMethod" placeholder="选择支付方式" class="w-100">
                    <el-option label="银行转账" value="bank" />
                    <el-option label="支付宝" value="alipay" />
                    <el-option label="微信支付" value="wechat" />
                  </el-select>
                </el-form-item>
                <el-button type="primary" size="large" class="w-100">确认买入</el-button>
              </el-form>
            </el-tab-pane>
            
            <el-tab-pane label="卖出" name="sell">
              <el-form :model="sellForm" label-position="top">
                <el-form-item label="卖出数量">
                  <el-input-number 
                    v-model="sellForm.amount" 
                    :min="0.01" 
                    :precision="2"
                    :step="0.01"
                    placeholder="请输入卖出数量"
                    class="w-100"
                  />
                </el-form-item>
                <el-form-item label="收款方式">
                  <el-select v-model="sellForm.receiveMethod" placeholder="选择收款方式" class="w-100">
                    <el-option label="银行账户" value="bank" />
                    <el-option label="支付宝" value="alipay" />
                    <el-option label="微信" value="wechat" />
                  </el-select>
                </el-form-item>
                <el-button type="danger" size="large" class="w-100">确认卖出</el-button>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="card">
          <div class="card-title">
            <el-icon><DataLine /></el-icon>
            <span>市场信息</span>
          </div>
          
          <div class="market-info">
            <div class="stat">
              <div class="value">1.00</div>
              <div class="label">稳定币价格 (USD)</div>
            </div>
            <div class="stat">
              <div class="value">24.5%</div>
              <div class="label">24h 交易量</div>
            </div>
            <div class="stat">
              <div class="value">1,234,567</div>
              <div class="label">流通总量</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { TrendCharts, DataLine } from '@element-plus/icons-vue'
export default {
  name: 'Trade',
  components: { TrendCharts, DataLine },
  data() {
    return {
      activeTab: 'buy',
      buyForm: { amount: null, paymentMethod: '' },
      sellForm: { amount: null, receiveMethod: '' }
    }
  }
}
</script>

<style scoped>
.trade-tabs :deep(.el-tabs__header) { margin-bottom: 20px; }
.market-info { display: grid; gap: 12px; }
.w-100 { width: 100%; }
</style>
