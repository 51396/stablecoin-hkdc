<template>
  <div class="reserve-admin-page">
    <h1 class="page-title">储备金管理中心</h1>

    <el-row :gutter="24">
      <!-- 左侧：资产录入表单 -->
      <el-col :span="8">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span><i class="el-icon-plus header-icon"></i>录入新资产</span>
            </div>
          </template>
          <el-form :model="newAssetForm" :rules="formRules" ref="newAssetFormRef" label-position="top">
            <el-form-item label="资产名称" prop="name">
              <el-input v-model="newAssetForm.name" placeholder="例如: 黄金, 美国十年期国债"></el-input>
            </el-form-item>
            <el-form-item label="资产类型" prop="asset_type">
              <el-select v-model="newAssetForm.asset_type" placeholder="请选择类型" style="width: 100%;">
                <el-option label="法币" value="法币"></el-option>
                <el-option label="加密货币" value="加密货币"></el-option>
                <el-option label="大宗商品" value="大宗商品"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="API Ticker" prop="ticker">
              <el-input v-model="newAssetForm.ticker" placeholder="例如: XAUUSD, BTCUSDT"></el-input>
            </el-form-item>
             <el-form-item label="初始数量" prop="base_balance">
              <el-input-number v-model="newAssetForm.base_balance" :min="0" controls-position="right" style="width: 100%;"></el-input-number>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleCreateAsset" :loading="formLoading">确认录入</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：已录入资产列表 -->
      <el-col :span="16">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span><i class="el-icon-s-grid header-icon"></i>资产管理列表</span>
              <el-button type="text" @click="fetchAllAssets" icon="el-icon-refresh"></el-button>
            </div>
          </template>
          <el-table :data="assetList" v-loading="tableLoading" height="500px">
            <el-table-column prop="name" label="资产名称"></el-table-column>
            <el-table-column prop="asset_type" label="类型"></el-table-column>
            <el-table-column prop="base_balance" label="当前数量" align="right">
                 <template #default="{ row }">
                    {{ formatNumber(row.base_balance) }}
                 </template>
            </el-table-column>
            <el-table-column label="操作" width="150" align="center">
              <template #default="{ row }">
                <el-button size="mini" @click="openEditDialog(row)" icon="el-icon-edit">修改</el-button>
                <el-button size="mini" type="primary" @click="openTransactionDialog(row)">调整数量</el-button>
                <!-- <el-button size="mini" type="danger" @click="handleDeleteAsset(row)">删除</el-button> -->
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 数量调整对话框 -->
    <el-dialog title="调整资产数量" v-model="dialogVisible" width="500px">
        <p>正在为 <strong>{{ currentAsset.name }}</strong> 调整数量</p>
        <el-form :model="transactionForm" :rules="transactionRules" ref="transactionFormRef" label-position="top">
            <el-form-item label="操作类型" prop="transaction_type">
                <el-radio-group v-model="transactionForm.transaction_type">
                    <el-radio label="存入">存入 (增加数量)</el-radio>
                    <el-radio label="取出">取出 (减少数量)</el-radio>
                </el-radio-group>
            </el-form-item>
            <el-form-item label="变动数量" prop="amount">
                <el-input-number v-model="transactionForm.amount" :min="0.01" controls-position="right" style="width: 100%;"></el-input-number>
            </el-form-item>
            <el-form-item label="备注/原因" prop="notes">
                <el-input type="textarea" v-model="transactionForm.notes" placeholder="例如：新购入, 市场卖出"></el-input>
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleAdjustBalance" :loading="dialogLoading">确认调整</el-button>
        </template>
    </el-dialog>
      <el-dialog title="修改资产信息" v-model="editDialogVisible" width="500px">
    <el-form :model="editAssetForm" :rules="editFormRules" ref="editAssetFormRef" label-position="top">
      <el-form-item label="资产名称" prop="name">
        <el-input v-model="editAssetForm.name"></el-input>
      </el-form-item>
      <el-form-item label="资产类型" prop="asset_type">
        <el-select v-model="editAssetForm.asset_type" placeholder="请选择类型" style="width: 100%;">
          <el-option label="法币" value="法币"></el-option>
          <el-option label="加密货币" value="加密货币"></el-option>
          <el-option label="大宗商品" value="大宗商品"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="API Ticker" prop="ticker">
        <el-input v-model="editAssetForm.ticker"></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="editDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleUpdateAsset" :loading="editDialogLoading">确认修改</el-button>
    </template>
  </el-dialog>
  </div>
</template>

<script>
// 假设你有一个封装好的API模块
import {reserveAPI} from '@/api/reserve';
// 模拟的API模块


export default {
  name: 'ReserveAdmin',
  data() {
    return {
      // 状态控制
      loading: false,
      formLoading: false,
      tableLoading: false,
      dialogLoading: false,
      dialogVisible: false,
      editDialogVisible: false, // <-- 新增：修改信息对话框可见性
      editDialogLoading: false, // <-- 新增：修改信息对话框加载状态
      // 数据
      assetList: [],
      newAssetForm: {
        name: '',
        asset_type: '',
        base_balance: 0,
        ticker: ''
      },
      editAssetForm: {
        id: null,
        name: '',
        asset_type: '',
        ticker: ''
      },
      editFormRules: {
        name: [{ required: true, message: '请输入资产名称', trigger: 'blur' }],
        asset_type: [{ required: true, message: '请选择资产类型', trigger: 'change' }],
        ticker: [{ required: true, message: '请输入API Ticker', trigger: 'blur' }],
      },
      transactionForm: {
        asset_id: null,
        transaction_type: '存入',
        amount: 1,
        notes: ''
      },
      currentAsset: {}, // 用于在对话框中显示当前操作的资产信息

      // 表单验证规则
      formRules: {
        name: [{ required: true, message: '请输入资产名称', trigger: 'blur' }],
        asset_type: [{ required: true, message: '请选择资产类型', trigger: 'change' }],
        ticker: [{ required: true, message: '请输入API Ticker', trigger: 'blur' }],
        base_balance: [{ required: true, message: '请输入初始数量', trigger: 'blur' }],
      },
      transactionRules: {
        transaction_type: [{ required: true, message: '请选择操作类型' }],
        amount: [{ required: true, message: '请输入变动数量' }],
      }
    }
  },
  mounted() {
    this.fetchAllAssets();
  },
  methods: {
    // 获取所有资产列表
    async fetchAllAssets() {
      this.tableLoading = true;
      try {
        const response = await reserveAPI.getAllAssets();
        console.log(response.data);

        this.assetList = response.data;
      } catch (error) {
        this.$message.error('获取资产列表失败: ' + (error.response?.data?.detail || error.message));
      } finally {
        this.tableLoading = false;
      }
    },
    // 创建新资产
    handleCreateAsset() {
      this.$refs.newAssetFormRef.validate(async (valid) => {
        if (!valid) return;
        this.formLoading = true;
        try {
          await reserveAPI.createNewAsset(this.newAssetForm);
          this.$message.success('新资产录入成功！');
          this.$refs.newAssetFormRef.resetFields(); // 清空表单
          await this.fetchAllAssets(); // 刷新列表
        } catch (error) {
          this.$message.error('录入失败: ' + (error.response?.data?.detail || error.message));
        } finally {
          this.formLoading = false;
        }
      });
    },
    // 打开数量调整对话框
    openTransactionDialog(asset) {
        this.currentAsset = asset;
        this.transactionForm.asset_id = asset.id;
        this.transactionForm.transaction_type = '存入';
        this.transactionForm.amount = 1;
        this.transactionForm.notes = '';
        this.dialogVisible = true;
        // 3. 使用 this.$nextTick 来确保DOM更新后再执行后续操作
        this.$nextTick(() => {
          // 在这个回调函数内部，可以100%保证对话框和表单已经渲染完毕
          // 因此 this.$refs.transactionFormRef 肯定存在
          if (this.$refs.transactionFormRef) {
              this.$refs.transactionFormRef.clearValidate();
          }
        });
    },
    // 提交数量调整
    handleAdjustBalance() {
        this.$refs.transactionFormRef.validate(async (valid) => {
            if (!valid) return;
            this.dialogLoading = true;
            try {
                await reserveAPI.adjustAssetBalance(this.transactionForm);
                this.$message.success('数量调整成功！');
                this.dialogVisible = false;
                await this.fetchAllAssets(); // 刷新列表
            } catch (error) {
                this.$message.error('调整失败: ' + (error.response?.data?.detail || error.message));
            } finally {
                this.dialogLoading = false;
            }
        });
    },
     // 打开修改对话框
    openEditDialog(asset) {
      // 使用 Object.assign({}, asset) 创建一个副本
      // 防止在对话框中修改时，直接影响到表格中的原始数据
      this.editAssetForm = Object.assign({}, {
          id: asset.id,
          name: asset.name,
          asset_type: asset.asset_type,
          ticker: asset.ticker
      });
      this.editDialogVisible = true;
      this.$nextTick(() => {
        if (this.$refs.editAssetFormRef) {
          this.$refs.editAssetFormRef.clearValidate();
        }
      });
    },
    
    // 提交修改
    handleUpdateAsset() {
      this.$refs.editAssetFormRef.validate(async (valid) => {
        if (!valid) return;
        this.editDialogLoading = true;
        try {
          // 准备提交给后端的数据，只包含需要更新的字段
          const updateData = {
            name: this.editAssetForm.name,
            asset_type: this.editAssetForm.asset_type,
            ticker: this.editAssetForm.ticker,
          };
          
          await reserveAPI.updateAsset(this.editAssetForm.id, updateData);
          
          this.$message.success('资产信息修改成功！');
          this.editDialogVisible = false;
          await this.fetchAllAssets(); // 刷新列表
        } catch (error) {
          this.$message.error('修改失败: ' + (error.response?.data?.detail || error.message));
        } finally {
          this.editDialogLoading = false;
        }
      });
    },
    // 辅助方法
    formatNumber(value) {
      if (typeof value !== 'number') return '0.00';
      return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },
  }
}
</script>

<style scoped>
/* 保持和之前一致的现代化风格 */
.reserve-admin-page {
  padding: 24px;
  background-color: #f7f8fa;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.box-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.03);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.header-icon {
  margin-right: 8px;
  color: #409EFF;
}

::v-deep .el-form-item__label {
  font-weight: 500;
}
</style>