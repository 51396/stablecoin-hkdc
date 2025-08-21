<template>
    <div class="page-container">
      <!-- 1. 页面头部 -->
      <div class="page-header">
        <h1 class="page-title">稳定币发行控制中心</h1>
        <p class="page-subtitle">安全、透明地管理稳定币的铸造与销毁流程</p>
      </div>
  
      <!-- 2. 顶部KPI概览 -->
      <el-row :gutter="24" class="kpi-row">
        <el-col :span="6"><div class="kpi-card"><p class="kpi-label">总供应量</p><p class="kpi-value">{{ formatCurrency(kpi.totalSupply) }}</p></div></el-col>
        <el-col :span="6"><div class="kpi-card"><p class="kpi-label">总储备价值</p><p class="kpi-value">{{ formatCurrency(kpi.totalReserve) }}</p></div></el-col>
        <el-col :span="6"><div class="kpi-card"><p class="kpi-label">抵押率</p><p class="kpi-value">{{ kpi.collateralRatio.toFixed(2) }}%</p></div></el-col>
        <el-col :span="6"><div class="kpi-card"><p class="kpi-label">待处理任务</p><p class="kpi-value">{{ pendingTasks.length }}</p></div></el-col>
      </el-row>
  
      <!-- 3. 操作入口 -->
      <el-row :gutter="24" class="action-entry-row">
        <el-col :span="12">
          <div class="action-card" @click="openWizard('mint')">
            <el-icon class="action-icon"><CirclePlusFilled /></el-icon>
            <h3>铸造新币 (Mint)</h3>
            <p>在确认储备金入账后，发起新的稳定币铸造流程。</p>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="action-card" @click="openWizard('burn')">
            <el-icon class="action-icon"><RemoveFilled /></el-icon>
            <h3>销毁稳定币 (Burn)</h3>
            <p>在处理完用户赎回后，发起稳定币的销毁流程。</p>
          </div>
        </el-col>
      </el-row>
  
      <!-- 4. 任务中心 -->
      <el-card class="box-card full-height-card"> <!-- 1. 确保卡片有 full-height-card class -->
  
        <!-- 卡片头部 -->
        <template #header>
          <div class="card-header-wrapper">
            <div class="card-header-title">任务中心</div>
            <!-- 内部Tabs，用于切换“待处理”和“历史” -->
            <el-tabs v-model="activeTaskTab" @tab-click="fetchTasks" class="inner-tabs">
              <el-tab-pane label="待处理任务" name="pending"></el-tab-pane>
              <el-tab-pane label="历史记录" name="history"></el-tab-pane>
            </el-tabs>
          </div>
        </template>
        <app-table :data="tasks" v-loading="tasksLoading">
          <!-- ... (您所有的 el-table-column 定义都原封不动地放在这里) ... -->
          <el-table-column prop="id" label="任务ID" min-width="200"></el-table-column>
          <el-table-column label="类型" min-width="200">
            <template #default="{ row }">
              <el-tag :type="row.type === 'mint' ? 'success' : 'warning'">{{ row.type === 'mint' ? '铸造' : '销毁' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column 
              prop="amount" 
              label="金额 (USD)" 
              align="right"  
              min-width="200" 
            >
            <template #default="{ row }">
              <div>{{ formatCurrency(row.amount) }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="requester" label="发起人" min-width="200"></el-table-column>
          <el-table-column prop="status" label="状态" min-width="250">
              <template #default="{ row }">
                  <div class="status-cell">
                    <span>{{ getStatusLabel(row.status) }}</span>
                    <el-progress 
                      v-if="row.status === 'PENDING_APPROVAL'"
                      :percentage="getApprovalPercentage(row)" 
                      :stroke-width="6"
                      style="margin-left: 10px; width: 80px"
                    />
                  </div>
              </template>
          </el-table-column>
            <el-table-column label="创建时间" min-width="250">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" min-width="300" fixed="right" align="center">
              <template #default="{ row }">
                  <el-button size="small" @click="viewTaskDetails(row)">详情</el-button>
                  <el-button size="small" type="primary" v-if="canApprove(row)" @click="handleApprove(row.id)" :loading="isActionLoading(row.id)">批准</el-button>
                  <el-button size="small" type="danger" v-if="canApprove(row)" @click="handleReject(row.id)" :loading="isActionLoading(row.id)">拒绝</el-button>
                  <el-button size="small" type="success" v-if="canExecute(row)" @click="handleExecute(row.id)" :loading="isActionLoading(row.id)">执行</el-button>
              </template>
          </el-table-column>
        </app-table>

    </el-card>
  
      <!-- 铸造/销毁流程的Wizard对话框 -->
      <el-dialog :title="wizard.title" v-model="wizard.visible" width="700px" :close-on-click-modal="false" @closed="resetWizard">
          <el-steps :active="wizard.step" finish-status="success" simple style="margin-bottom: 20px;">
              <el-step title="信息录入"></el-step>
              <el-step title="确认提交"></el-step>
          </el-steps>
          <!-- Step 1: 表单 -->
          <div v-show="wizard.step === 0">
              <el-form :model="requestForm" :rules="formRules" ref="requestFormRef" label-position="top">
                  <el-form-item label="划拨金额 (USD)" prop="amount"><el-input-number v-model="requestForm.amount" :min="1" controls-position="right" style="width:100%"></el-input-number></el-form-item>
                 <!-- 
                  我们将原来的一个表单项，拆分为两个联动的表单项。
                  使用 el-row 来将它们放在同一行。
                -->
                <el-row :gutter="20">
                  
                  <!-- 第一个选择器：选择对公账户 -->
                  <el-col :span="12">
                    <el-form-item 
                      :label="wizard.type === 'mint' ? '目标账户' : '来源账户'" 
                      prop="target_account_id"
                    >
                      <el-select 
                        v-model="requestForm.target_account_id" 
                        placeholder="请选择一个对公账户" 
                        style="width: 100%;"
                        @change="handleAccountChange"
                        clearable
                      >
                        <!-- 选项将由 this.institutionalAccounts 填充 -->
                        <el-option
                          v-for="account in institutionalAccounts"
                          :key="account.id"
                          :label="account.name"
                          :value="account.id">
                        </el-option>
                      </el-select>
                    </el-form-item>
                  </el-col>

                  <!-- 第二个选择器：选择该账户下的地址 -->
                  <el-col :span="12">
                    <el-form-item 
                      :label="wizard.type === 'mint' ? '具体接收地址' : '具体来源地址'" 
                      prop="target_address"
                    >
                      <el-select 
                        v-model="requestForm.target_address" 
                        placeholder="请选择一个地址" 
                        style="width: 100%;"
                        :disabled="!requestForm.target_account_id"
                        clearable
                      >
                        <!-- 选项由计算属性 selectedAccountAddresses 动态提供 -->
                        <el-option
                          v-for="address in selectedAccountAddresses"
                          :key="address.id"
                          :label="address.label || address.address"
                          :value="address.address">
                          <!-- 自定义选项，显示标签和截断的地址 -->
                          <div>
                            <span>{{ address.label || '无标签' }}</span>
                            <span class="address-option-display">{{ address.address }}</span>
                          </div>
                        </el-option>
                      </el-select>
                    </el-form-item>
                  </el-col>

                </el-row>
                  <!-- <el-form-item label="资金来源证明 (文件URL)" prop="fund_proof_url"><el-input v-model="requestForm.fund_proof_url" placeholder="请粘贴银行转账截图、SWIFT电文等证明文件的URL"></el-input></el-form-item> -->
                  <el-form-item label="备注 / 交易ID" prop="notes"><el-input type="textarea" v-model="requestForm.notes"></el-input></el-form-item>
              </el-form>
          </div>
          <!-- Step 2: 确认信息 -->
          <div v-show="wizard.step === 1" class="confirmation-view">
              <el-descriptions :column="1" border>
                  <el-descriptions-item label="操作类型">{{ wizard.type === 'mint' ? '铸造' : '销毁' }}</el-descriptions-item>
                  <el-descriptions-item label="金额">{{ formatCurrency(requestForm.amount) }}</el-descriptions-item>
                  <el-descriptions-item :label="wizard.type === 'mint' ? '目标地址' : '来源地址'">{{ requestForm.target_address }}</el-descriptions-item>
                  <el-descriptions-item label="资金证明"><el-link :href="requestForm.fund_proof_url" target="_blank">{{ requestForm.fund_proof_url }}</el-link></el-descriptions-item>
                  <el-descriptions-item label="备注">{{ requestForm.notes || '无' }}</el-descriptions-item>
              </el-descriptions>
          </div>
          <template #footer>
              <el-button @click="wizard.visible = false">取消</el-button>
              <el-button @click="wizard.step--" v-if="wizard.step > 0">上一步</el-button>
              <el-button type="primary" @click="handleWizardNext" :loading="wizard.loading">{{ wizard.step === 0 ? '下一步' : '提交审批' }}</el-button>
          </template>
      </el-dialog>
    </div>
  </template>
  
  <script>
  // Options API 风格
  import { CirclePlusFilled, RemoveFilled, Refresh } from '@element-plus/icons-vue'; // 引入图标
import institutionalAccountAPI from '../api/institutional_account';
import issueAPI from '@/api/issue';
  
  export default {
    name: 'StablecoinIssuance',
    components: { CirclePlusFilled, RemoveFilled }, // 注册图标
    data() {
      return {
        // 当前登录用户 (模拟)
        currentUser: { name: 'CurrentUser', role: 'approver' }, //可以是 'operator', 'approver'
        // KPI数据
        kpi: { totalSupply: 0, totalReserve: 0, collateralRatio: 0 },
        // 任务列表
        tasks: [],
        tasksLoading: true,
        activeTaskTab: 'pending',
        actionLoading: {}, // 用于控制单个按钮的加载状态
        // Wizard对话框
        wizard: {
          visible: false, type: 'mint', title: '', step: 0, loading: false
        },
        requestForm: {
          amount: 10000,
          target_account_id: null, // 新增：用于存储选中的账户ID
          target_address: '',      // 保持不变，用于存储最终选中的地址
          fund_proof_url: '',
          notes: ''
        },
        formRules: {
          amount: [{ required: true, message: '请输入金额' }],
          target_account_id: [{ required: true, message: '请选择目标账户', trigger: 'change' }],
          target_address: [{ required: true, message: '请选择具体地址', trigger: 'change' }],
        },
        institutionalAccounts: [],
      }
    },
    computed: {
      pendingTasks() {
        // 简单计算，真实应用中应从API获取
        return this.tasks.filter(t => t.status === 'PENDING_APPROVAL' || t.status === 'APPROVED');
      },
       /**
       * 根据当前选中的账户ID，返回该账户下的所有地址
       */
      selectedAccountAddresses() {
        // 如果没有选中账户，返回空数组
        if (!this.requestForm.target_account_id) {
          return [];
        }
        
        // 在完整的账户列表中找到那个被选中的账户
        const selectedAccount = this.institutionalAccounts.find(
          acc => acc.id === this.requestForm.target_account_id
        );
        
        // 返回该账户的 addresses 数组，如果找不到则返回空数组
        return selectedAccount ? selectedAccount.addresses : [];
      }
    },
    mounted() {
      this.fetchInitialData();
      this.fetchInstitutionalAccounts(); // <-- 新增这个调用
    },
    methods: {
      // --- 数据获取 ---
      async fetchInitialData() {
          this.tasksLoading = true;
          try {
              const [kpiRes, tasksRes] = await Promise.all([
                  issueAPI.getKpi(),
                  issueAPI.getTasks('pending')
              ]);
              this.kpi = kpiRes.data;
              this.tasks = tasksRes.data;
          } catch (error) { this.$message.error('加载初始数据失败'); }
          finally { this.tasksLoading = false; }
      },
      async fetchTasks() {
          this.tasksLoading = true;
          try {
              const response = await issueAPI.getTasks(this.activeTaskTab);
              this.tasks = response.data;
          } catch (error) { this.$message.error('加载任务列表失败'); }
          finally { this.tasksLoading = false; }
      },
      
      // --- Wizard 对话框逻辑 ---
      openWizard(type) {
        this.wizard.type = type;
        this.wizard.title = type === 'mint' ? '发起新的铸造流程' : '发起销毁流程';
        this.wizard.visible = true;
      },
      resetWizard() {
        this.wizard.step = 0;
        this.$refs.requestFormRef.resetFields();
      },
      handleWizardNext() {
        if (this.wizard.step === 0) {
          this.$refs.requestFormRef.validate((valid) => {
            if (valid) this.wizard.step++;
          });
        } else {
          this.submitRequest();
        }
      },
      async submitRequest() {
          this.wizard.loading = true;
          try {
              const payload = { ...this.requestForm, type: this.wizard.type };
              await issueAPI.createRequest(payload);
              this.$message.success('请求已成功提交审批！');
              this.wizard.visible = false;
              await this.fetchTasks();
          } catch (error) { this.$message.error('提交失败'); }
          finally { this.wizard.loading = false; }
      },
  
      // --- 任务操作 ---
      isActionLoading(taskId) {
          return this.actionLoading[taskId];
      },
      setActionLoading(taskId, status) {
          this.$set(this.actionLoading, taskId, status);
      },
      canApprove(task) {
          // 假设审批人不能是发起人
          return this.currentUser.role === 'approver' && task.status === 'PENDING_APPROVAL' && task.requester !== this.currentUser.name;
      },
      canExecute(task) {
          return this.currentUser.role === 'operator' && task.status === 'APPROVED';
      },
      async handleApprove(taskId) {
          this.setActionLoading(taskId, true);
          try {
              await issueAPI.approve(taskId);
              this.$message.success('批准成功！');
              await this.fetchTasks();
          } catch (error) { this.$message.error('操作失败'); }
          finally { this.setActionLoading(taskId, false); }
      },
      handleReject() { this.$message.info('拒绝功能待实现'); },
      async handleExecute(taskId) {
          this.setActionLoading(taskId, true);
          try {
              await issueAPI.execute(taskId);
              this.$message.info('执行命令已发送，请在区块链浏览器上跟踪交易');
              await this.fetchTasks(); // 状态会先变为 Processing
          } catch (error) { this.$message.error('执行失败'); }
          finally { this.setActionLoading(taskId, false); }
      },
      viewTaskDetails(task) { this.$message.info(`查看任务 ${task.id} 详情`); },
  
      // --- 辅助函数 ---
      formatCurrency(value) { return value ? `$${value.toLocaleString('en-US')}` : '$0.00'; },
      formatDate(date) { return new Date(date).toLocaleString('zh-CN'); },
      getStatusLabel(status) {
          const map = { PENDING_APPROVAL: '等待批准', APPROVED: '已批准', PROCESSING: '执行中', COMPLETED: '已完成', REJECTED: '已拒绝' };
          return map[status] || '未知';
      },
      getApprovalPercentage(task) {
          if (!task.required_approvals) return 0;
          return (task.approvals_count / task.required_approvals) * 100;
      },
        /**
         * 新增：获取所有对公账户及其地址
         */
        async fetchInstitutionalAccounts() {
          try {
            // 调用我们之前为“账户管理”页面创建的API
            // 假设它返回 [{ id, name, addresses: [{ id, address, label }] }]
            const response = await institutionalAccountAPI.getInstitutionalAccounts();
            this.institutionalAccounts = response.data.items || response.data; // 兼容分页和非分页
          } catch (error) {
            this.$message.error('加载对公账户列表失败');
            console.error(error);
          }
        },

        /**
         * 新增：当账户选择变化时，清空已选中的地址
         */
        handleAccountChange() {
          // 当用户重新选择账户时，自动清空之前选择的地址
          // 这样可以强制用户重新选择一个属于新账户的地址
          this.requestForm.target_address = '';
        },
    }
  }
  </script>
  
  <style scoped>
  /* 保持我们之前确立的专业、干净的浅色风格 */
  .page-container { padding: 32px; background-color: #f9fafb; min-height: 100vh; }
  .page-header { margin-bottom: 24px; }
  .page-title { font-size: 28px; font-weight: 700; color: #1f2937; }
  .page-subtitle { font-size: 14px; color: #6b7280; margin-top: 8px; }
  
  .kpi-row { margin-bottom: 32px; }
  .kpi-card { background-color: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 24px; text-align: center; }
  .kpi-label { margin: 0 0 8px 0; color: #6b7280; font-size: 14px; }
  .kpi-value { margin: 0; font-size: 24px; font-weight: 700; color: #111827; }
  
  .action-entry-row { margin-bottom: 32px; }
  .action-card { padding: 32px; border: 1px solid #e5e7eb; border-radius: 12px; text-align: center; cursor: pointer; transition: all 0.3s ease; background-color: #fff; }
  .action-card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); border-color: #409EFF; }
  .action-icon { font-size: 40px; color: #409EFF; margin-bottom: 16px; }
  .action-card h3 { font-size: 20px; font-weight: 600; margin-bottom: 8px; }
  .action-card p { color: #6b7280; }
  
  .box-card { background-color: #fff; border: 1px solid #e5e7eb; border-radius: 12px; }
  .card-header-wrapper { display: flex; justify-content: space-between; align-items: center; }
  .card-header-title { font-size: 18px; font-weight: 600; }
  .status-cell { display: flex; align-items: center; }
  .confirmation-view { padding: 20px; background-color: #fafafa; border-radius: 4px; }

  .address-option-display {
  float: right;
  color: #8492a6;
  font-size: 13px;
  font-family: 'Roboto Mono', monospace;
}
.full-height-card {
  flex-grow: 1; /* 卡片将填充 .tab-content 的所有可用空间 */
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 防止卡片内部内容溢出 */
}
  </style>