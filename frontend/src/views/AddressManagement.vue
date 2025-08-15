<template>
  <!-- 1. 根容器，应用全局背景和内边距 -->
  <div class="address-management">
    
    <!-- 2. 将页面主标题移到卡片外部，作为整个页面的标题 -->
    <h1 class="page-title">地址管理</h1>
    
    <!-- 添加地址表单卡片 -->
    <el-card class="box-card">
      <!-- 使用 el-card 自带的 header slot，并添加图标 -->
      <div slot="header" class="clearfix card-header">
        <span><i class="el-icon-plus header-icon"></i>添加新地址</span>
      </div>
      <!-- 你的表单逻辑保持不变 -->
      <el-form :model="newAddress" label-width="80px" class="add-form">
        <el-row :gutter="20">
          <el-col :span="10">
            <el-form-item label="地址">
              <el-input v-model="newAddress.address" placeholder="请输入以太坊地址"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="标签">
              <el-select v-model="newAddress.label" placeholder="请选择标签" clearable>
                <el-option
                  v-for="label in predefinedLabels"
                  :key="label"
                  :label="label"
                  :value="label">
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
             <el-form-item label="白名单">
              <el-switch v-model="newAddress.is_whitelisted" active-color="#13ce66"></el-switch>
            </el-form-item>
          </el-col>
           <el-col :span="4">
             <el-form-item label="黑名单">
              <el-switch v-model="newAddress.is_blacklisted" active-color="#13ce66"></el-switch>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="addAddress" icon="el-icon-circle-plus-outline">添加</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 地址列表卡片 -->
    <el-card class="box-card">
      <div slot="header" class="clearfix card-header">
        <span><i class="el-icon-s-grid header-icon"></i>地址列表</span>
        <el-button style="float: right; padding: 0" type="text" @click="loadAddresses" icon="el-icon-refresh">刷新</el-button>
      </div>
      
      <!-- 筛选与搜索区 -->
      <div class="filter-section">
        <el-radio-group v-model="filterType" @change="loadAddresses" size="medium">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="whitelist">白名单</el-radio-button>
          <el-radio-button label="blacklist">黑名单</el-radio-button>
          <el-radio-button label="normal">普通地址</el-radio-button>
        </el-radio-group>
        <el-input
          v-model="searchLabel"
          placeholder="按标签搜索"
          class="search-input"
          @keyup.enter.native="loadAddresses"
          clearable
        >
          <el-button slot="append" icon="el-icon-search" @click="loadAddresses"></el-button>
        </el-input>
      </div>
      
      <!-- 地址表格 (内部逻辑完全保留) -->
      <el-table :data="loggedAddresses" style="width: 100%" v-loading="loading">
        <!-- 你的所有 el-table-column 定义都原封不动地保留在这里 -->
        <!-- ID 列 -->
        <el-table-column prop="id" label="ID" width="80">
          <template #default="{ row}">
            <span v-if="row">{{ row.id }}</span>
          </template>
        </el-table-column>
        <!-- 地址 列 -->
        <el-table-column prop="address" label="地址">
          <template #default="{row}">
            <span v-if="row" class="address-cell" :title="row.address">
              {{ truncateAddress(row.address) }}
              <i class="el-icon-copy-document copy-icon" @click="copyToClipboard(row.address)"></i>
            </span>
          </template>
        </el-table-column>
        <!-- 标签 列 -->
        <el-table-column prop="label" label="标签" width="150">
          <template #default="{row}">
            <el-tag v-if="row && row.label" type="success" size="small">{{ row.label }}</el-tag>
            <span v-else-if="row">无标签</span>
          </template>
        </el-table-column>
        <!-- 白名单 列 -->
        <el-table-column label="白名单" width="100">
          <template #default="{row}">
            {{ logRow(Boolean(row.is_whitelisted)) }}
            {{ logRow(row.is_whitelisted) }}
            {{ logRow(row.is_whitelisted === 'true') }}
            {{ logRow(row.is_whitelisted == 'true') }}
            <el-switch v-if="row" :value="Boolean(row.is_whitelisted === 'true')" disabled active-color="#13ce66"></el-switch>
          </template>
        </el-table-column>
        <!-- 黑名单 列 -->
        <el-table-column label="黑名单" width="100">
          <template #default="{row}">
            <el-switch v-if="row" :value="Boolean(row.is_blacklisted)" disabled active-color="#ff4949"></el-switch>
          </template>
        </el-table-column>
        <!-- 创建时间 列 -->
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{row}">
            <span v-if="row"><i class="el-icon-time"></i> {{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <!-- 操作 列 -->
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <div v-if="row">
              <el-button size="small" @click="editAddress(row)" icon="el-icon-edit">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteAddress(row.id)" icon="el-icon-delete">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 (你的逻辑保留) -->
      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          background
        ></el-pagination>
      </div>
    </el-card>
    
    <!-- 编辑地址对话框 (你的逻辑保留) -->
    <el-dialog title="编辑地址" :visible.sync="editDialogVisible" width="500px">
       <!-- ... 你的表单 ... -->
    </el-dialog>
  </div>
</template>

<script>
import { addressAPI } from '@/api/address'

export default {
  name: 'AddressManagement',
  data() {
    return {
      newAddress: {
        address: '',
        label: '',
        is_whitelisted: false,
        is_blacklisted: false
      },
      addresses: [],
      loading: false,
      currentPage: 1,
      pageSize: 20,
      total: 0,
      filterType: 'all',
      searchLabel: '',
      editDialogVisible: false,
      editingAddress: {
        id: null,
        address: '',
        label: '',
        is_whitelisted: false,
        is_blacklisted: false
      },
      predefinedLabels: [
        '交易所',
        '钱包服务商',
        '矿工',
        'DeFi协议',
        'NFT平台',
        '其他'
      ]
    }
  },
  created() {
    this.loadAddresses()
  },
  methods: {
    truncateAddress(value) {
      if (!value) return ''
      if (value.length <= 20) return value
      return `${value.substring(0, 10)}...${value.substring(value.length - 8)}`
    },
    formatDate(value) {
      if (!value) return ''
      const date = new Date(value)
      return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit',timeZone: 'UTC' })
    },
    validateEthereumAddress(address) {
      // 验证以太坊地址格式
      const pattern = /^0x[a-fA-F0-9]{40}$/;
      return pattern.test(address);
    },
    logRow(row) {
      console.log('当前行的数据(row)是:', row);
      // 为了不影响模板，我们可以返回一个空字符串或true
      return ''; 
    },
    async loadAddresses() {
      this.loading = true
      try {
        const params = {
          skip: (this.currentPage - 1) * this.pageSize,
          limit: this.pageSize
        }
        console.log(this.filterType)
        // 根据筛选类型调整请求参数
        if (this.filterType === 'whitelist') {
          const response = await addressAPI.getWhitelistedAddresses(params)
          this.addresses = response.data || []
        } else if (this.filterType === 'blacklist') {
          const response = await addressAPI.getBlacklistedAddresses(params)
          this.addresses = response.data || []
        } else if (this.filterType === 'normal') {
          // 获取普通地址（非白名单且非黑名单）
          const allAddresses = await addressAPI.getAllAddresses({ skip: 0, limit: 20 })
          const normalAddresses = (allAddresses.data || []).filter(addr => !addr.is_whitelisted && !addr.is_blacklisted)
          this.total = normalAddresses.length
          // 分页处理
          this.addresses = normalAddresses.slice(params.skip, params.skip + params.limit)
        } else {
          // 获取所有地址
          const response = await addressAPI.getAllAddresses(params)
          this.addresses = response.data || []
        }
      } catch (error) {
        console.error('获取地址列表失败:', error)
        this.$message.error('获取地址列表失败')
        this.addresses = [] // 确保在错误情况下地址列表为空数组
      } finally {
        this.loading = false
      }
      return this.addresses
    },
    async addAddress() {
      if (!this.newAddress.address) {
        this.$message.warning('请输入地址')
        return
      }
      
      // 验证地址格式
      if (!this.validateEthereumAddress(this.newAddress.address)) {
        this.$message.warning('地址格式不正确，请输入有效的以太坊地址')
        return
      }
      
      try {
        await addressAPI.createAddress(this.newAddress)
        this.$message.success('地址添加成功')
        this.newAddress = { address: '', label: '', is_whitelisted: false, is_blacklisted: false }
        this.loadAddresses()
      } catch (error) {
        console.error('添加地址失败:', error)
        this.$message.error('添加地址失败: ' + (error.response?.data?.detail || '未知错误'))
      }
    },
    editAddress(address) {
      this.editingAddress = { ...address }
      this.editDialogVisible = true
    },
    async updateAddress() {
      // 编辑地址时不验证地址格式，因为地址字段是只读的
      try {
        await addressAPI.updateAddress(this.editingAddress.id, {
          label: this.editingAddress.label,
          is_whitelisted: this.editingAddress.is_whitelisted,
          is_blacklisted: this.editingAddress.is_blacklisted
        })
        this.$message.success('地址更新成功')
        this.editDialogVisible = false
        this.loadAddresses()
      } catch (error) {
        console.error('更新地址失败:', error)
        this.$message.error('更新地址失败: ' + (error.response?.data?.detail || '未知错误'))
      }
    },
    deleteAddress(id) {
      this.$confirm('确定要删除这个地址吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await addressAPI.deleteAddress(id)
          this.$message.success('地址删除成功')
          this.loadAddresses()
        } catch (error) {
          console.error('删除地址失败:', error)
          this.$message.error('删除地址失败: ' + (error.response?.data?.detail || '未知错误'))
        }
      }).catch(() => {
        // 用户取消删除
      })
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.loadAddresses()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.loadAddresses()
    }
  },
  mounted() {
    this.loadAddresses()
  },
   // 1. 在这里添加 computed 块
  computed: {
    // 这个计算属性是我们用来调试的“代理”
    loggedAddresses() {
      // 当模板访问这个属性时，下面的代码就会执行
      console.log('表格正在渲染，当前 "addresses" 数组的内容是:', this.addresses);
      
      // 然后，它返回原始的 addresses 数组给表格使用
      return this.addresses;
    }
  },
}
</script>

<style scoped>
/* ----- 全局和容器 ----- */
.address-management {
  /* 使用柔和的灰色背景，让白色卡片更突出 */
  background-color: #f0f2f5;
  padding: 24px;
  min-height: 100vh;
}

/* ----- 卡片统一样式 ----- */
.box-card {
  border: none;
  border-radius: 8px; /* 更大的圆角，更现代 */
  margin-bottom: 24px;
  /* 柔和的阴影，创造立体感 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 深度选择器，修改Element UI子组件的样式 */
::v-deep .el-card__header {
  border-bottom: 1px solid #ebeef5;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}


/* ----- 筛选/搜索区 ----- */
.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #fafbfe;
  border-radius: 6px;
}

.search-input {
  width: 250px;
}


/* ----- 表格美化 ----- */

/* 表格的整体圆角和边框 */
::v-deep .el-table {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

/* 表头样式 */
::v-deep .el-table th {
  background-color: #fafbfe !important; /* 清爽的表头背景色 */
  color: #606266;
  font-weight: 600;
  text-align: left;
}

/* 移除表头下方的边框 */
::v-deep .el-table th.is-leaf {
  border-bottom: none;
}

/* 行样式和悬停效果 */
::v-deep .el-table__row {
  transition: background-color 0.2s ease-in-out; /* 平滑的过渡效果 */
}
::v-deep .el-table__row:hover {
  background-color: #ecf5ff !important; /* Element UI 主题色的悬停高亮 */
}

/* 单元格样式 */
::v-deep .el-table td {
  padding: 14px 0; /* 增加行高，让内容不拥挤 */
}


/* ----- 分页 ----- */
.pagination-container {
  margin-top: 24px;
  text-align: right; /* 分页居右显示 */
}

/* ----- 响应式设计 ----- */
@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }
  .search-input {
    width: 100%;
    margin-top: 10px;
  }
}
</style>