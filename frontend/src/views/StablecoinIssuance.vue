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
      <el-card class="box-card">
        <template #header>
          <div class="card-header-wrapper">
            <div class="card-header-title">任务中心</div>
            <el-tabs v-model="activeTaskTab" @tab-click="fetchTasks">
              <el-tab-pane label="待处理任务" name="pending"></el-tab-pane>
              <el-tab-pane label="历史记录" name="history"></el-tab-pane>
            </el-tabs>
          </div>
        </template>
        <el-table :data="tasks" v-loading="tasksLoading" style="width: 100%">
          <el-table-column prop="id" label="任务ID" width="120"></el-table-column>
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="row.type === 'mint' ? 'success' : 'warning'">{{ row.type === 'mint' ? '铸造' : '销毁' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="金额 (USD)" align="right">
            <template #default="{ row }">{{ formatCurrency(row.amount) }}</template>
          </el-table-column>
          <el-table-column prop="requester" label="发起人" width="120"></el-table-column>
          <el-table-column prop="status" label="状态" width="220">
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
           <el-table-column label="创建时间" width="180">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="250" fixed="right" align="center">
              <template #default="{ row }">
                  <el-button size="small" @click="viewTaskDetails(row)">详情</el-button>
                  <el-button size="small" type="primary" v-if="canApprove(row)" @click="handleApprove(row.id)" :loading="isActionLoading(row.id)">批准</el-button>
                  <el-button size="small" type="danger" v-if="canApprove(row)" @click="handleReject(row.id)" :loading="isActionLoading(row.id)">拒绝</el-button>
                  <el-button size="small" type="success" v-if="canExecute(row)" @click="handleExecute(row.id)" :loading="isActionLoading(row.id)">执行</el-button>
              </template>
          </el-table-column>
        </el-table>
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
                  <el-form-item :label="wizard.type === 'mint' ? '目标接收地址' : '资金来源地址'" prop="target_address"><el-input v-model="requestForm.target_address"></el-input></el-form-item>
                  <el-form-item label="资金来源证明 (文件URL)" prop="fund_proof_url"><el-input v-model="requestForm.fund_proof_url" placeholder="请粘贴银行转账截图、SWIFT电文等证明文件的URL"></el-input></el-form-item>
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
  
  // --- Mock API: 模拟后端逻辑 ---
  const mockAPI = {
    // 模拟数据库
    db: {
      tasks: [
        { id: 'MINT-001', type: 'mint', amount: 1000000, requester: 'Alice', status: 'PENDING_APPROVAL', approvals_count: 1, required_approvals: 3, created_at: new Date(Date.now() - 3600000) },
        { id: 'BURN-001', type: 'burn', amount: 50000, requester: 'Bob', status: 'APPROVED', approvals_count: 2, required_approvals: 2, created_at: new Date(Date.now() - 7200000) },
        { id: 'MINT-002', type: 'mint', amount: 200000, requester: 'Charlie', status: 'COMPLETED', tx_hash: '0xabc...', created_at: new Date(Date.now() - 86400000) }
      ],
      kpi: { totalSupply: 100250000, totalReserve: 100350000, collateralRatio: 100.10 }
    },
    
    // 模拟API调用
    getKpi: () => new Promise(res => setTimeout(() => res({ data: mockAPI.db.kpi }), 200)),
    getTasks: (status) => new Promise(res => {
      setTimeout(() => {
        const tasks = status === 'pending'
          ? mockAPI.db.tasks.filter(t => !['COMPLETED', 'REJECTED', 'FAILED'].includes(t.status))
          : mockAPI.db.tasks.filter(t => ['COMPLETED', 'REJECTED', 'FAILED'].includes(t.status));
        res({ data: tasks });
      }, 500)
    }),
    createRequest: (data) => new Promise(res => {
      setTimeout(() => {
        const newId = `${data.type.toUpperCase()}-00${mockAPI.db.tasks.length + 1}`;
        const newTask = { ...data, id: newId, requester: 'CurrentUser', status: 'PENDING_APPROVAL', approvals_count: 0, required_approvals: 3, created_at: new Date() };
        mockAPI.db.tasks.unshift(newTask);
        res({ data: newTask });
      }, 800)
    }),
    approve: (id) => new Promise(res => {
      setTimeout(() => {
        const task = mockAPI.db.tasks.find(t => t.id === id);
        if (task) {
          task.approvals_count++;
          if (task.approvals_count >= task.required_approvals) {
            task.status = 'APPROVED';
          }
        }
        res({ data: task });
      }, 500)
    }),
    execute: (id) => new Promise(res => {
      setTimeout(() => {
        const task = mockAPI.db.tasks.find(t => t.id === id);
        if (task) {
          task.status = 'PROCESSING';
          // 模拟链上交易
          setTimeout(() => {
              task.status = 'COMPLETED';
              task.tx_hash = `0x${[...Array(40)].map(() => Math.floor(Math.random() * 16).toString(16)).join('')}`;
          }, 3000);
        }
        res({ data: task });
      }, 500)
    }),
  };
  
  
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
          target_address: '0x...',
          fund_proof_url: 'https://...',
          notes: ''
        },
        formRules: {
          amount: [{ required: true, message: '请输入金额' }],
          target_address: [{ required: true, message: '请输入地址' }],
        }
      }
    },
    computed: {
      pendingTasks() {
        // 简单计算，真实应用中应从API获取
        return this.tasks.filter(t => t.status === 'PENDING_APPROVAL' || t.status === 'APPROVED');
      }
    },
    mounted() {
      this.fetchInitialData();
    },
    methods: {
      // --- 数据获取 ---
      async fetchInitialData() {
          this.tasksLoading = true;
          try {
              const [kpiRes, tasksRes] = await Promise.all([
                  mockAPI.getKpi(),
                  mockAPI.getTasks('pending')
              ]);
              this.kpi = kpiRes.data;
              this.tasks = tasksRes.data;
          } catch (error) { this.$message.error('加载初始数据失败'); }
          finally { this.tasksLoading = false; }
      },
      async fetchTasks() {
          this.tasksLoading = true;
          try {
              const response = await mockAPI.getTasks(this.activeTaskTab);
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
              await mockAPI.createRequest(payload);
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
              await mockAPI.approve(taskId);
              this.$message.success('批准成功！');
              await this.fetchTasks();
          } catch (error) { this.$message.error('操作失败'); }
          finally { this.setActionLoading(taskId, false); }
      },
      handleReject() { this.$message.info('拒绝功能待实现'); },
      async handleExecute(taskId) {
          this.setActionLoading(taskId, true);
          try {
              await mockAPI.execute(taskId);
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
      }
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
  </style>