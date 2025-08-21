<template>
    <div class="page-container">
      <!-- 1. 页面头部 -->
      <div class="page-header">
        <h1 class="page-title">账户中心</h1>
        <p class="page-subtitle">管理对公机构与对私个人账户及其关联地址</p>
      </div>
  
      <!-- 2. 顶级标签页 -->
      <el-tabs v-model="activeTab" type="border-card" class="main-tabs">
        
        <!-- ========== 标签页一：对公账户管理 ========== -->
        <el-tab-pane name="institutional">
          <template #label>
            <span><i class="el-icon-office-building"></i> 对公账户管理</span>
          </template>
          <div class="tab-content">
            <el-card class="box-card full-height-card">
              <template #header>
                <div class="card-header-wrapper">
                  <div class="card-header-title">机构账户列表</div>
                  <div class="toolbar">
                    <el-input v-model="institutionalFilters.search" placeholder="搜索机构名称" class="search-input" size="small" clearable @keyup.enter="fetchInstitutionalAccounts" />
                    <el-button type="primary" size="small" @click="openInstitutionalAccountDialog()">注册新机构</el-button>
                  </div>
                </div>
              </template>
              <div class="table-container">
                <el-table :data="institutionalAccounts" style="width: 100%" height="100%" row-key="id" v-loading="institutionalAccountsLoading" @expand-change="handleExpandChange">
                  <el-table-column type="expand">
                    <template #default="{ row }">
                      <div class="expanded-content">
                        <div class="expanded-header">
                           <h4><i class="el-icon-wallet"></i> 绑定的地址 ({{ row.addresses.length }})</h4>
                           <el-button type="primary" size="small" @click="openAddressDialog(row)">绑定新地址</el-button>
                        </div>
                        <el-table :data="row.addresses" size="small" stripe>
                          <el-table-column prop="label" label="地址标签"></el-table-column>
                          <el-table-column prop="address" label="区块链地址" min-width="300">
                             <template #default="props">
                                <div class="tx-hash-cell" @click="copyToClipboard(props.row.address)">
                                  <span>{{ props.row.address }}</span>
                                  <el-icon class="copy-icon"><CopyDocument /></el-icon>
                                </div>
                             </template>
                          </el-table-column>
                          <el-table-column prop="balance" label="地址余额" align="right">
                             <template #default="props">{{ formatCurrency(props.row.balance) }}</template>
                          </el-table-column>
                          <el-table-column label="操作" align="center">
                            <template #default="props">
                              <el-button type="danger" size="small" @click="handleUnbindAddress(row, props.row)">解绑</el-button>
                            </template>
                          </el-table-column>
                        </el-table>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column prop="name" label="机构名称"></el-table-column>
                  <el-table-column prop="description" label="描述"></el-table-column>
                  <el-table-column label="地址总数" align="center" width="100">
                      <template #default="{ row }">{{ row.addresses.length }}</template>
                  </el-table-column>
                  <el-table-column label="总余额" align="right">
                      <template #default="{ row }">{{ formatCurrency(row.total_balance) }}</template>
                  </el-table-column>
                  <el-table-column label="操作" align="center" width="150">
                    <template #default="{ row }">
                      <el-button type="primary" size="small" @click="openInstitutionalAccountDialog(row)">编辑</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
  
        <!-- ========== 标签页二：对私账户管理 ========== -->
        <el-tab-pane name="individual">
          <template #label>
            <span><i class="el-icon-user"></i> 对私账户管理</span>
          </template>
          <div class="tab-content">
            <el-row :gutter="24" class="full-height-row">
              <!-- 左侧：用户列表 -->
              <el-col :span="16">
                <el-card class="box-card full-height-card">
                  <template #header>
                    <div class="card-header-wrapper">
                      <div class="card-header-title">个人用户列表</div>
                      <div class="toolbar">
                        <el-input v-model="userFilters.search" placeholder="搜索用户" class="search-input" size="small" clearable @keyup.enter="fetchUsers"></el-input>
                        <el-select v-model="userFilters.status" placeholder="状态" clearable size="small" @change="fetchUsers" style="width: 120px;"><el-option label="正常" value="active"></el-option><el-option label="已冻结" value="frozen"></el-option></el-select>
                      </div>
                    </div>
                  </template>
                  <div class="table-container">
                    <el-table :data="users" v-loading="usersLoading" style="width: 100%" height="100%" @row-click="selectUser" highlight-current-row>
                      <el-table-column prop="uid" label="用户UID"></el-table-column>
                      <el-table-column prop="username" label="用户名"></el-table-column>
                      <el-table-column prop="kyc_level" label="KYC等级" align="center"><template #default="{ row }"><el-tag type="success">Lv{{ row.kyc_level }}</el-tag></template></el-table-column>
                      <el-table-column prop="status" label="状态" align="center"><template #default="{ row }"><el-tag :type="row.status === 'active' ? 'success' : 'danger'" effect="dark">{{ row.status === 'active' ? '正常' : '已冻结' }}</el-tag></template></el-table-column>
                    </el-table>
                  </div>
                  <div class="pagination-container">
                    <el-pagination background layout="total, sizes, prev, pager, next" :total="usersTotal" v-model:current-page="userPagination.currentPage" v-model:page-size="userPagination.pageSize" @size-change="fetchUsers" @current-change="fetchUsers"></el-pagination>
                  </div>
                </el-card>
              </el-col>
              <!-- 右侧：添加/编辑用户表单 -->
              <el-col :span="8">
                <el-card class="box-card full-height-card">
                   <template #header>
                    <div class="card-header-wrapper">
                      <div class="card-header-title">{{ isEditingUser ? '编辑用户信息' : '添加新用户' }}</div>
                      <el-button v-if="isEditingUser" type="text" @click="resetUserForm">取消编辑</el-button>
                    </div>
                  </template>
                  <el-form :model="userForm" :rules="userFormRules" ref="userFormRef" label-position="top">
                    <el-form-item label="用户名 / 邮箱" prop="username"><el-input v-model="userForm.username"></el-input></el-form-item>
                    <el-form-item label="KYC 等级" prop="kyc_level"><el-select v-model="userForm.kyc_level" style="width:100%"><el-option label="Lv1" :value="1"></el-option><el-option label="Lv2" :value="2"></el-option><el-option label="Lv3" :value="3"></el-option></el-select></el-form-item>
                    <el-form-item label="状态" prop="status"><el-radio-group v-model="userForm.status"><el-radio label="active">正常</el-radio><el-radio label="frozen">冻结</el-radio></el-radio-group></el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="saveUser" :loading="userFormLoading">{{ isEditingUser ? '保存更新' : '确认添加' }}</el-button>
                    </el-form-item>
                  </el-form>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>
  
      <!-- 对话框 -->
      <el-dialog :title="isEditingInstitutionalAccount ? '编辑机构账户' : '注册新机构账户'" v-model="institutionalAccountDialogVisible" width="500px" @closed="resetInstitutionalAccountForm">
          <el-form :model="institutionalAccountForm" :rules="institutionalAccountFormRules" ref="institutionalAccountFormRef" label-position="top">
              <el-form-item label="机构名称" prop="name"><el-input v-model="institutionalAccountForm.name"></el-input></el-form-item>
              <el-form-item label="描述" prop="description"><el-input type="textarea" v-model="institutionalAccountForm.description"></el-input></el-form-item>
          </el-form>
          <template #footer><el-button @click="institutionalAccountDialogVisible = false">取消</el-button><el-button type="primary" @click="saveInstitutionalAccount" :loading="institutionalAccountFormLoading">确认</el-button></template>
      </el-dialog>
      <el-dialog title="为账户绑定新地址" v-model="addressDialogVisible" width="500px" @closed="resetAddressForm">
           <el-form :model="addressForm" :rules="addressFormRules" ref="addressFormRef" label-position="top">
              <el-form-item label="区块链地址" prop="address"><el-input v-model="addressForm.address"></el-input></el-form-item>
              <el-form-item label="地址标签 (可选)" prop="label"><el-input v-model="addressForm.label" placeholder="例如: 主收款地址"></el-input></el-form-item>
          </el-form>
          <template #footer><el-button @click="addressDialogVisible = false">取消</el-button><el-button type="primary" @click="saveAddress" :loading="addressFormLoading">确认绑定</el-button></template>
      </el-dialog>
    </div>
  </template>
  
  <script>
  // Options API
  import { Search, CopyDocument, Right } from '@element-plus/icons-vue';
  // Mock API (模拟后端)
import {retailAccountAPI} from '@/api/retail_account';
import {institutionalAccountAPI} from '@/api/institutional_account'
  export default {
    name: 'AccountManagement',
    components: { Search, CopyDocument, Right },
    data() {
      return {
        activeTab: 'institutional',
        
        // --- 对公 Tab ---
        institutionalAccounts: [],
        institutionalAccountsLoading: false,
        institutionalAccountDialogVisible: false,
        isEditingInstitutionalAccount: false,
        institutionalAccountForm: { name: '', description: '' },
        institutionalAccountFormLoading: false,
        institutionalAccountFormRules: { name: [{ required: true, message: '请输入机构名称' }] },
        institutionalFilters: { search: '' },
        addressDialogVisible: false,
        addressFormLoading: false,
        addressForm: { address: '', label: '' },
        addressFormRules: { address: [{ required: true, message: '请输入区块链地址' }] },
        currentInstitutionalAccount: null, // 当前正在操作的机构账户
  
        // --- 对私 Tab ---
        users: [],
        usersLoading: false,
        usersTotal: 0,
        userPagination: { currentPage: 1, pageSize: 10 },
        userFilters: { search: '', status: '' },
        isEditingUser: false,
        userFormLoading: false,
        userForm: { username: '', kyc_level: 1, status: 'active' },
        userFormRules: { username: [{ required: true, message: '请输入用户名' }] },
      }
    },
    watch: { /* ... (按需加载逻辑) ... */ },
    mounted() { this.fetchInstitutionalAccounts(); },
    methods: {
      // --- 对公方法 ---
      async fetchInstitutionalAccounts() { 
        const response = await institutionalAccountAPI.getInstitutionalAccounts();
        this.institutionalAccounts = response.data.items;
       },
      openInstitutionalAccountDialog(account = null) {
        if (account) {
          this.isEditingInstitutionalAccount = true;
          this.institutionalAccountForm = { ...account };
        } else {
          this.isEditingInstitutionalAccount = false;
        }
        this.institutionalAccountDialogVisible = true;
      },
      resetInstitutionalAccountForm() { this.$refs.institutionalAccountFormRef.resetFields(); },
      async saveInstitutionalAccount() {
        console.log(1)
        this.$refs.institutionalAccountFormRef.validate(async (valid) => {
          if (!valid) return;
          this.institutionalAccountFormLoading = true;
          try {
            if (this.isEditingInstitutionalAccount) {
              await institutionalAccountAPI.updateInstitutionalAccount(this.institutionalAccountForm.id, this.institutionalAccountForm);
            } else {
              await institutionalAccountAPI.createInstitutionalAccount(this.institutionalAccountForm);
            }
            this.$message.success('操作成功！');
            this.institutionalAccountDialogVisible = false;
            await this.fetchInstitutionalAccounts();
          } catch (error) { this.$message.error('操作失败',error); }
          finally { this.institutionalAccountFormLoading = false; }
        });
      },
      openAddressDialog(account) {
        this.currentInstitutionalAccount = account;
        this.addressDialogVisible = true;
      },
      resetAddressForm() { this.$refs.addressFormRef.resetFields(); },
      async saveAddress() {
        this.$refs.addressFormRef.validate(async (valid) => {
          if (!valid) return;
          this.addressFormLoading = true;
          try {
            const payload = { ...this.addressForm };
            await institutionalAccountAPI.bindAddress(this.currentInstitutionalAccount.id,payload);
            this.$message.success('地址绑定成功！');
            this.addressDialogVisible = false;
            await this.fetchInstitutionalAccounts();
          } catch (error) { this.$message.error('绑定失败'); }
          finally { this.addressFormLoading = false; }
        });
      },
      handleUnbindAddress(account, address) {
        this.$confirm(`确定要从 "${account.name}" 解绑地址 ${address.address} 吗?`, '确认解绑', {
            confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning',
          }).then(async () => {
            await mockAPI.unbindAddress(address.id);
            this.$message.success('解绑成功');
            await this.fetchInstitutionalAccounts();
          }).catch(() => {});
      },
      handleExpandChange() {},
  
      // --- 对私方法 ---
      async fetchUsers() { /* ... */ },
      selectUser(user) {
        this.isEditingUser = true;
        this.userForm = { ...user };
      },
      resetUserForm() {
        this.isEditingUser = false;
        this.$refs.userFormRef.resetFields();
      },
      async saveUser() {
         this.$refs.userFormRef.validate(async (valid) => {
          if (!valid) return;
          this.userFormLoading = true;
          try {
            if (this.isEditingUser) {
              await retailAccountAPI.updateUser(this.userForm.id, this.userForm);
            } else {
              await mockAPI.createUser(this.userForm);
            }
            this.$message.success('操作成功！');
            this.resetUserForm();
            await this.fetchUsers();
          } catch (error) { this.$message.error('操作失败',error); }
          finally { this.userFormLoading = false; }
        });
      },
  
      // --- 辅助方法 ---
      formatCurrency(value) { return value ? `$${value.toLocaleString('en-US')}` : '$0.00'; },
      copyToClipboard(text) { navigator.clipboard.writeText(text).then(() => this.$message.success('已复制')); },
    }

  }
  </script>
  
  
  <style scoped>
  /* 保持我们之前确立的专业、干净的浅色风格 */
  .page-container { padding: 32px; background-color: #f9fafb; min-height: 100vh; }
  .page-header { margin-bottom: 24px; }
  .page-title { font-size: 28px; font-weight: 700; }
  .page-subtitle { font-size: 14px; color: #6b7280; margin-top: 8px; }
  .main-tabs { border-radius: 12px; border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
  .tab-content { padding: 24px; }
  
  /* 卡片和Flex布局 */
  .box-card { background-color: #fff; border-radius: 8px; border: 1px solid #e5e7eb; height: 100%; display: flex; flex-direction: column; }
  .card-header-wrapper { display: flex; justify-content: space-between; align-items: center; }
  .card-header-title { font-size: 18px; font-weight: 600; color: #1f2937; }
  .full-height-card { height: 70vh; /* 定义一个固定高度 */ }
  .full-height-row { height: 70vh; }
  ::v-deep(.el-card__body) { flex-grow: 1; overflow: hidden; display: flex; flex-direction: column;}
  
  /* 表格容器 */
  .table-container { flex-grow: 1; overflow: hidden; position: relative; }
  
  /* 对公账户表格展开内容 */
  .expanded-content {
      padding: 16px;
      background-color: #fafafa;
  }
  .expanded-content h4 {
      margin: 0 0 10px 0;
      font-size: 14px;
      font-weight: 600;
  }
  
  /* 对私账户右侧表单 */
  .pagination-container { margin-top: 24px; display: flex; justify-content: flex-end; }
  .toolbar { display: flex; gap: 12px; }
  .search-input { width: 250px; }
  .tx-hash-cell { display: flex; align-items: center; font-family: 'Roboto Mono', monospace; cursor: pointer; }
  .copy-icon { margin-left: 8px; opacity: 0; }
  .tx-hash-cell:hover .copy-icon { opacity: 1; }
  .expanded-content { padding: 16px; background-color: #fafbfd; }
.expanded-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.expanded-header h4 { margin: 0; font-size: 14px; font-weight: 600; }
  </style>