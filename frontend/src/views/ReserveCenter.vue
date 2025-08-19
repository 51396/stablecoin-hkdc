<template>
    <div class="page-container">
      <!-- 1. 页面头部 -->
      <div class="page-header">
        <h1 class="page-title">储备金管理中心</h1>
        <p class="page-subtitle">管理托管机构及旗下资产账户</p>
      </div>
  
      <!-- 2. 使用 Element Plus 的标签页进行功能分区 -->
      <el-tabs v-model="activeTab" type="border-card" class="main-tabs">
          
        <!-- ========== 标签页二：资产账户管理 ========== -->
        <el-tab-pane name="accounts">
          <template #label>
            <span><i class="el-icon-coin"></i> 资产账户管理</span>
          </template>
          <div class="tab-content">
            <el-card class="box-card">
              <!-- 卡片头部，整合了标题和工具栏 -->
              <template #header>
                <div class="card-header-wrapper">
                  <div class="card-header-title">所有资产账户</div>
                  <div class="toolbar">
                    <!-- 筛选器 -->
                    <el-select placeholder="按机构筛选" size="small" clearable></el-select>
                    <el-input placeholder="搜索账户" size="small" class="search-input"></el-input>
                    <el-button 
                        type="primary" 
                        size="small" 
                        :icon="Plus" 
                        @click="openAccountDialog()"
                        >
                        添加账户
                    </el-button>
                  </div>
                </div>
              </template>
              <!-- 表格 -->
              <div class="table-container">
                <el-table :data="accounts" v-loading="accountsLoading" style="width: 100%" height="100%">
                    
                    <!-- 1. 账户名称/ID -->
                    <el-table-column prop="name" label="账户名称 / 描述" min-width="200">
                    <template #default="{ row }">
                        <div class="account-name-cell">
                        <span class="account-name">{{ row.name }}</span>
                        <span class="account-id">ID: {{ row.id }}</span>
                        </div>
                    </template>
                    </el-table-column>
                    
                    <!-- 2. 所属托管机构 -->
                    <el-table-column prop="custodian.name" label="所属机构" min-width="150">
                    <template #default="{ row }">
                        <el-tag effect="plain" size="small">{{ row.custodian.name }}</el-tag>
                    </template>
                    </el-table-column>

                    <!-- 3. 资产类别 -->
                    <el-table-column prop="asset_type" label="资产类别" min-width="150"></el-table-column>
                    
                    <!-- 4. 余额/面值 (带在线编辑功能) -->
                    <el-table-column prop="balance" label="余额 / 面值" align="right" min-width="180">
                    <template #default="{ row }">
                        <!-- 使用 Popover 实现点击编辑 -->
                        <el-popover
                        placement="top"
                        :width="350"
                        trigger="click"
                        @show="openBalanceEditor(row)"
                        >
                        <template #reference>
                            <span class="editable-balance">
                            {{ formatCurrency(row.balance, row.currency) }}
                            <el-icon class="edit-icon"><EditPen /></el-icon>
                            </span>
                        </template>
                        </el-popover>
                    </template>
                    </el-table-column>

                    <!-- 5. 等值美元 (自动计算) -->
                    <el-table-column label="等值 (USD)" align="right" min-width="150">
                        <template #default="{ row }">
                            <span class="usd-value">{{ formatCurrency(row.value_usd, 'USD') }}</span>
                        </template>
                    </el-table-column>
                    
                    <!-- 6. 最后更新时间 -->
                    <el-table-column prop="updated_at" label="最后更新" align="right" width="180">
                    <template #default="{ row }">
                        <span class="update-time">{{ formatDate(row.updated_at) }}</span>
                    </template>
                    </el-table-column>
                    
                    <!-- 7. 操作 -->
                    <el-table-column label="操作" width="120" fixed="right" align="center">
                    <template #default="{ row }">
                        <el-button type="primary" text plain size="small" @click="viewHistory(row)" class="details-button">变动历史</el-button>
                    </template>
                    </el-table-column>

                </el-table>
            </div>
              <!-- 分页 -->
              <!-- 4. 分页器绑定 -->
            <div class="pagination-container">
              <el-pagination 
                background 
                layout="total, sizes, prev, pager, next" 
                :total="accountsTotal"
                v-model:current-page="pagination.currentPage"
                v-model:page-size="pagination.pageSize"
                @size-change="fetchAccounts"
                @current-change="fetchAccounts"
              ></el-pagination>
            </div>
            </el-card>
          </div>
        </el-tab-pane>


        <!-- ========== 新增：添加/编辑资产账户对话框 ========== -->
        <el-dialog
        :title="isEditingAccount ? '编辑资产账户' : '录入新资产账户'"
        v-model="accountDialogVisible"
        width="600px"
        :close-on-click-modal="false"
        @closed="resetAccountForm"
        >
        <el-form
            :model="accountForm"
            :rules="accountFormRules"
            ref="accountFormRef"
            label-position="top"
        >
            <!-- 1. 选择归属的托管机构 -->
            <el-form-item label="托管机构" prop="custodian_id">
            <el-select 
                v-model="accountForm.custodian_id" 
                placeholder="请选择资产存放的机构" 
                style="width: 100%;"
                :disabled="isEditingAccount"
            >
                <el-option
                v-for="custodian in custodians"
                :key="custodian.id"
                :label="custodian.name"
                :value="custodian.id">
                </el-option>
            </el-select>
            </el-form-item>

            <!-- 2. 账户名称/描述 -->
            <el-form-item label="账户名称 / 资产描述" prop="name">
            <el-input v-model="accountForm.name" placeholder="例如: 美元活期存款, 3个月期美国国债"></el-input>
            </el-form-item>

            <!-- 3. 资产类别 -->
            <el-form-item label="资产类别" prop="asset_type">
            <el-select v-model="accountForm.asset_type" placeholder="请选择资产类别" style="width: 100%;">
                <el-option label="现金 (Cash)" value="现金"></el-option>
                <el-option label="现金等价物 (Cash Equivalents)" value="现金等价物"></el-option>
                <el-option label="短期政府债券 (Short-term Treasury)" value="短期政府债券"></el-option>
            </el-select>
            </el-form-item>

            <!-- 4. 货币 和 余额/面值 -->
            <el-row :gutter="20">
            <el-col :span="12">
                <el-form-item label="货币" prop="currency">
                <el-select v-model="accountForm.currency" placeholder="货币" style="width: 100%;">
                    <el-option label="USD" value="USD"></el-option>
                    <el-option label="HKD" value="HKD"></el-option>
                    <el-option label="EUR" value="EUR"></el-option>
                </el-select>
                </el-form-item>
            </el-col>
            <el-col :span="12">
                <!-- 
                在编辑模式下，余额不可直接修改。
                余额的调整应通过“调整数量”功能来记录流水。
                -->
                <el-form-item label="初始余额 / 面值" prop="balance">
                <el-input-number 
                    v-model="accountForm.balance" 
                    :min="0" 
                    :precision="2" 
                    controls-position="right" 
                    style="width: 100%;"
                    :disabled="isEditingAccount"
                ></el-input-number>
                </el-form-item>
            </el-col>
            </el-row>
        </el-form>

        <template #footer>
            <el-button @click="accountDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveAccount" :loading="accountFormLoading">
            {{ isEditingAccount ? '保存更新' : '确认录入' }}
            </el-button>
        </template>
        </el-dialog>


        <!-- ========== 标签页一：托管机构管理 ========== -->
        <el-tab-pane name="custodians">
          <template #label>
            <span><i class="el-icon-office-building"></i> 托管机构管理</span>
          </template>
          <div class="tab-content">
            <el-row :gutter="24">
              <!-- 左侧：录入/编辑机构表单 -->
              <el-col :span="8">
                <el-card class="form-card">
                  <template #header>
                    <div class="card-header-title">{{ isEditingCustodian ? '编辑机构信息' : '录入新机构' }}</div>
                  </template>
                  <el-form :model="custodianForm" :rules="custodianFormRules" ref="custodianFormRef" label-position="top">
                    <el-form-item label="机构名称" prop="name"><el-input v-model="custodianForm.name"></el-input></el-form-item>
                    <el-form-item label="机构类型" prop="custodian_type"><el-select v-model="custodianForm.custodian_type" style="width:100%"><el-option label="银行" value="银行"></el-option><el-option label="信托公司" value="信托公司"></el-option></el-select></el-form-item>
                    <el-form-item label="机构账户" prop="account_address"><el-input v-model="custodianForm.account_address"></el-input></el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="saveCustodian" :loading="custodianFormLoading">{{ isEditingCustodian ? '保存更新' : '确认录入' }}</el-button>
                      <el-button @click="resetCustodianForm" v-if="isEditingCustodian">取消编辑</el-button>
                    </el-form-item>
                  </el-form>
                </el-card>
              </el-col>
              <!-- 右侧：机构列表 -->
              <el-col :span="16">
                <el-card class="table-card">
                  <el-table :data="custodians" v-loading="custodiansLoading" height="500px">
                    <el-table-column prop="name" label="机构名称"></el-table-column>
                    <el-table-column prop="custodian_type" label="类型"></el-table-column>
                    <el-table-column prop="account_address" label="账户"></el-table-column>
                    <el-table-column label="操作">
                      <template #default="{ row }">
                        <el-button size="mini" @click="editCustodian(row)">编辑</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>


  
      </el-tabs>
    </div>
  </template>
  
  <script>
  // Options API 风格
  import axios from 'axios';
import {custodiansAPI} from '@/api/custodians';
import {reserveAPI} from '@/api/reserve';
  // import { Plus } from '@element-plus/icons-vue' // 如果使用 icon
  
  export default {
    name: 'ReserveCenter',
    // components: { Plus },
    data() {
      return {
        activeTab: 'accounts',
        
        // --- 托管机构 Tab ---
        custodians: [],
        custodiansLoading: false,
        custodianForm: { name: '', custodian_type: '', account_address: '' },
        custodianFormLoading: false,
        isEditingCustodian: false,
        custodianFormRules: {
          name: [{ required: true, message: '请输入机构名称' }],
          custodian_type: [{ required: true, message: '请选择机构类型' }],
          account_address: [{required: true,message: '请输入在该机构的账户信息'}]
        },
        pagination: {
          currentPage: 1,
          pageSize: 10
        },

         // 新增：详情对话框的状态
        detailsDialogVisible: false,
        detailsLoading: false,
        selectedAccount: null,


        // --- 资产账户 Tab ---
        accounts: [],
        accountsLoading: false,
        accountsTotal: 0,

         // =======================================================
        accountDialogVisible: false,
        accountFormLoading: false,
        isEditingAccount: false, // 用于区分是“添加”还是“编辑”模式

         // 用于添加/编辑的表单数据模型
        accountForm: {
            id: null,
            custodian_id: null,
            name: '',
            asset_type: '',
            currency: 'USD',
            balance: 0,
        },
        
        // 表单验证规则
        accountFormRules: {
            custodian_id: [{ required: true, message: '请选择一个托管机构', trigger: 'change' }],
            name: [{ required: true, message: '请输入账户名称或资产描述', trigger: 'blur' }],
            asset_type: [{ required: true, message: '请选择资产类别', trigger: 'change' }],
            currency: [{ required: true, message: '请选择货币', trigger: 'change' }],
            balance: [
              { required: true, message: '请输入初始余额' },
              { type: 'number', message: '余额必须为数字' }
            ],
        },
      }
    },
    mounted() {
      this.fetchCustodians();
      this.fetchAccounts();   // 同时获取账户列表
    },
    methods: {
      // --- 托管机构方法 ---
      async fetchCustodians() {
        this.custodiansLoading = true;
        try {
          const response = await custodiansAPI.getCustodiansAPIData();
          this.custodians = response.data;
        } catch (error) { console.error(error); } 
        finally { this.custodiansLoading = false; }
      },
      editCustodian(custodian) {
          this.isEditingCustodian = true;
          // 使用 assign 创建副本，避免直接修改列表数据
          this.custodianForm = Object.assign({}, custodian);
      },
      resetCustodianForm() {
          this.isEditingCustodian = false;
          this.$refs.custodianFormRef.resetFields();
      },
      saveCustodian() {
          this.$refs.custodianFormRef.validate(async (valid) => {
              if (!valid) return;
              this.custodianFormLoading = true;
              try {
                  if (this.isEditingCustodian) {
                      // 调用更新API
                      // await axios.put(`/api/v1/custodians/${this.custodianForm.id}`, this.custodianForm);
                  } else {
                      // 调用创建API
                      await custodiansAPI.saveCustodian(this.custodianForm);
                  }
                  this.$message.success('操作成功！');
                  this.resetCustodianForm();
                  await this.fetchCustodians();
              } catch (error) { this.$message.error('操作失败'); }
              finally { this.custodianFormLoading = false; }
          });
      },
  
        // --- 资产账户方法 ---
        async fetchAccounts() {
            this.accountsLoading = true;
            try {
              const params = {
                skip: (this.pagination.currentPage - 1) * this.pagination.pageSize,
                limit: this.pagination.pageSize,
                ...this.filters
              };
              // 假设API会返回类似这样的数据
              const response = await reserveAPI.getAssetAccounts(params);
              this.accounts = response.data.items;
              this.accountsTotal = response.data.total;
            } catch (error) { console.error(error); } 
            finally { this.accountsLoading = false; }
        },
        handleFilterChange() {
          this.pagination.currentPage = 1;
          this.fetchAccounts();
        },

        // 查看详情和历史记录
        async viewHistory(account) {
          this.detailsDialogVisible = true;
          this.detailsLoading = true;
          try {
              const response = await axios.get(`/api/v1/accounts/${account.id}`);
              this.selectedAccount = response.data;
          } catch (error) {
              this.$message.error('获取账户详情失败');
              this.detailsDialogVisible = false;
          } finally {
              this.detailsLoading = false;
          }
        },
        /**
         * 打开对话框
         * @param {object | null} account - 如果传入了 account 对象，则为编辑模式；否则为添加模式
         */
        openAccountDialog(account = null) {
            if (account) {
            // --- 编辑模式 ---
            this.isEditingAccount = true;
            // 使用 assign 创建副本，填充表单
            this.accountForm = Object.assign({}, account);
            } else {
            // --- 添加模式 ---
            this.isEditingAccount = false;
            // resetFields 会重置为初始值，但我们在这里可以手动再清一下
            this.accountForm = {
                id: null,
                custodian_id: null,
                name: '',
                asset_type: '',
                currency: 'USD',
                balance: 0,
            };
            }
            this.accountDialogVisible = true;
        },
        
        /**
         * 在对话框关闭后，重置表单状态
         */
        resetAccountForm() {
            this.$refs.accountFormRef.resetFields();
            this.isEditingAccount = false;
        },

        /**
         * 提交表单（添加或更新）
         */
        saveAccount() {
            this.$refs.accountFormRef.validate(async (valid) => {
            if (!valid) return;
            
            this.accountFormLoading = true;
            try {
                if (this.isEditingAccount) {
                // --- 调用更新 API ---
                // const { id, ...updateData } = this.accountForm;
                // await axios.put(`/api/v1/accounts/${id}`, updateData);
                } else {
                // --- 调用创建 API ---
                  await reserveAPI.createAssetAccount(this.accountForm);
                }
                
                this.$message.success('操作成功！');
                this.accountDialogVisible = false;
                await this.fetchAccounts(); // 刷新列表
                
            } catch (error) {
                this.$message.error('操作失败: ' + (error.response?.data?.detail || error.message));
            } finally {
                this.accountFormLoading = false;
            }
            });
        },
        formatCurrency(value) {
          if (typeof value !== 'number') return '$0.00';
          return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
      },
      formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute:'2-digit' });
    },
    }
  }
  </script>
  
  <style scoped>
  /* ----- 统一的页面和卡片样式 ----- */
  .page-container { padding: 32px; background-color: #f9fafb; min-height: 100vh; }
  .page-header { margin-bottom: 24px; }
  .page-title { font-size: 28px; font-weight: 700; color: #1f2937; }
  .page-subtitle { font-size: 14px; color: #6b7280; margin-top: 8px; }
  
  .main-tabs { border-radius: 12px; border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
  .tab-content { padding: 24px; }
  
  .form-card, .table-card, .box-card { background-color: #fff; border-radius: 8px; border: 1px solid #e5e7eb; }
  .card-header-title { font-size: 18px; font-weight: 600; color: #1f2937; }
  ::v-deep(.el-card__header) { border-bottom: 1px solid #f3f4f6; }
  
  /* ----- 托管机构 Tab ----- */
  /* (可以添加特定样式) */
  
  /* ----- 资产账户 Tab ----- */
  .card-header-wrapper { display: flex; justify-content: space-between; align-items: center; }
  .toolbar { display: flex; gap: 12px; align-items: center; }
  .pagination-container { margin-top: 24px; display: flex; justify-content: flex-end; }

  .account-name-cell {
  line-height: 1.4;
    }
.account-name {
  font-weight: 600;
  color: #303133;
}
.account-id {
  display: block;
  font-size: 12px;
  color: #909399;
  font-family: 'Roboto Mono', monospace;
}

.editable-balance {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  font-weight: 600;
  color: #409EFF;
  font-family: 'Roboto Mono', monospace;
  text-decoration: underline dashed #c0c4cc;
}
.edit-icon {
  margin-left: 8px;
  opacity: 0.6;
}

.usd-value {
    font-weight: 500;
    font-family: 'Roboto Mono', monospace;
}

.update-time {
  font-size: 13px;
  color: #909399;
}

/* Popover内部表单的样式 */
.balance-editor h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
}
/* 正常状态 */
:deep(.details-button.el-button--primary.is-plain) {
  --el-button-text-color: #fcfcfc;   /* 文字颜色 */
  --el-button-border-color: #4598f7; /* 边框颜色 */
  --el-button-bg-color: #21acec;     /* 背景颜色 */
}
  </style>