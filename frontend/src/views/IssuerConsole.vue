<template>
  <div class="issuer-page">
    <div class="page-header">
      <h1>🏛️ 稳定币管理</h1>
      <p class="subtitle">仅合约 Owner 可见与操作</p>
    </div>

    <!-- 一级导航栏 -->
    <div class="nav-tabs">
      <el-button 
        :type="activeTab === 'mint' ? 'primary' : 'default'" 
        @click="activeTab = 'mint'"
      >
        铸币
      </el-button>
      <el-button 
        :type="activeTab === 'burn' ? 'primary' : 'default'" 
        @click="activeTab = 'burn'"
      >
        销毁
      </el-button>
      <el-button 
        :type="activeTab === 'whitelist' ? 'primary' : 'default'" 
        @click="activeTab = 'whitelist'"
      >
        白名单
      </el-button>
      <el-button 
        :type="activeTab === 'deposit' ? 'primary' : 'default'" 
        @click="activeTab = 'deposit'"
      >
        法币充值
      </el-button>
    </div>

    <el-card class="card">
      <div class="card-title">货币总览</div>
      <div class="currency-overview">
        <div class="overview-item">
          <div class="overview-label">总供应量</div>
          <div class="overview-value">{{ totalSupply }} HKDC</div>
        </div>
        <div class="overview-item">
          <div class="overview-label">已铸造</div>
          <div class="overview-value">{{ mintedAmount }} HKDC</div>
        </div>
        <div class="overview-item">
          <div class="overview-label">已销毁</div>
          <div class="overview-value">{{ burnedAmount }} HKDC</div>
        </div>
        <div class="overview-item">
          <div class="overview-label">流通量</div>
          <div class="overview-value">{{ circulatingSupply }} HKDC</div>
        </div>
        <el-button type="primary" @click="refreshOverview">刷新数据</el-button>
        <!-- <el-button type="success" @click="switchWalletAddress" class="ml-10">切换钱包地址</el-button> -->
      </div>
    </el-card>

    <!-- 铸币功能 -->
    <el-card class="card" v-if="isIssuer && activeTab === 'mint'">
      <div class="card-title">铸币</div>
      <el-form :model="mintForm" label-position="top">
        <el-form-item label="数量 (HKDC)">
          <el-input-number v-model="mintForm.amount" :min="0" :precision="2" :step="0.01" class="w-100" />
        </el-form-item>
        <el-button type="primary" :loading="loading.mint" @click="doMint">确认铸造</el-button>
      </el-form>
    </el-card>

    <!-- 销毁功能 -->
    <el-card class="card" v-if="isIssuer && activeTab === 'burn'">
      <div class="card-title">销毁</div>
      <el-form :model="burnForm" label-position="top">
        <el-form-item label="数量 (HKDC)">
          <el-input-number v-model="burnForm.amount" :min="0" :precision="2" :step="0.01" class="w-100" />
        </el-form-item>
        <el-button type="danger" :loading="loading.burn" @click="doBurn">确认销毁</el-button>
      </el-form>
    </el-card>

    <!-- 白名单功能 -->
    <el-card class="card" v-if="isIssuer && activeTab === 'whitelist'">
      <div class="card-title">白名单</div>
      <!-- 将白名单开关移到外层 -->
      <div class="mb-10">
        <el-switch v-model="whitelistEnabled" active-text="启用白名单" inactive-text="关闭白名单" @change="toggleWhitelist" />
      </div>
      
      <!-- 只有启用白名单时才展示相关功能 -->
      <div v-if="whitelistEnabled">
        <el-form :model="wlForm" label-position="top">
          <el-form-item label="账户地址">
            <el-input v-model="wlForm.account" placeholder="0x..." />
          </el-form-item>
          <div class="btns">
            <el-button type="success" :loading="loading.add" @click="addToWhitelist">添加</el-button>
            <el-button type="warning" :loading="loading.remove" @click="removeFromWhitelist">移除</el-button>
          </div>
        </el-form>
        
        <!-- 白名单列表展示 -->
        <div class="whitelist-list">
          <div class="card-title mt-20">白名单列表</div>
          <el-table :data="whitelist" style="width: 100%" max-height="300">
            <el-table-column prop="address" label="地址" />
            <el-table-column label="操作">
              <template #default="scope">
                <el-button type="warning" size="small" @click="removeFromWhitelistByAddress(scope.row.address)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>

    <!-- 法币充值功能 -->
    <el-card class="card" v-if="isIssuer && activeTab === 'deposit'">
      <div class="card-title">法币充值（后端）</div>
      <el-form :model="depositForm" label-position="top">
        <el-form-item label="用户ID">
          <el-input-number v-model="depositForm.userId" :min="1" />
        </el-form-item>
        <el-form-item label="金额 (法币)">
          <el-input-number v-model="depositForm.amount" :min="0" :precision="2" :step="0.01" class="w-100" />
        </el-form-item>
        <el-button type="primary" :loading="loading.deposit" @click="doDeposit">后端充值</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ElCard, ElForm, ElFormItem, ElInput, ElInputNumber, ElButton, ElTag, ElSwitch, ElRow, ElCol } from 'element-plus'
import { ElMessage } from 'element-plus'
import { mapGetters, mapActions } from 'vuex'
import { walletAPI } from '@/api/wallet'

export default {
  name: 'IssuerConsole',
  components: { ElCard, ElForm, ElFormItem, ElInput, ElInputNumber, ElButton, ElTag, ElSwitch, ElRow, ElCol },
  data() {
    return {
      activeTab: 'mint', // 默认选中铸币标签
      form: { contractAddress: '' },
      mintForm: { amount: null },
      burnForm: { amount: null },
      wlForm: { account: '' },
      whitelistEnabled: false,
      depositForm: { userId: null, amount: null },
      loading: { mint: false, burn: false, add: false, remove: false, deposit: false }
    }
  },
  computed: {
    ...mapGetters('issuer', ['isIssuer', 'ownerAddress', 'whitelistEnabled', 'whitelist', 'totalSupply', 'mintedAmount', 'burnedAmount']),
    ...mapGetters('wallet', ['walletAddress']),
    circulatingSupply() {
      if (!this.totalSupply || !this.burnedAmount) return '0.00'
      return (parseFloat(this.totalSupply) - parseFloat(this.burnedAmount)).toFixed(2)
    }
  },
  mounted() {
    // 自动调用initIssuer以确保页面正确显示
    this.initIssuer();
  },
  beforeUnmount() {
    // 组件销毁前移除钱包事件监听器
    this.$store.dispatch('wallet/removeEventListeners');
  },
  watch: {
    // 监听钱包地址变化，重新初始化发行方身份
    walletAddress(newAddress, oldAddress) {
      if (newAddress && newAddress !== oldAddress) {
        this.initIssuer();
      }
    }
  },
  methods: {
    ...mapActions('issuer', ['initIssuer', 'mint', 'burn', 'setWhitelist', 'addToWhitelist', 'removeFromWhitelist', 'checkWhitelistEnabled']),
    async initIssuer() {
      try {
        const ok = await this.$store.dispatch('issuer/initIssuer')
        // 检查白名单状态
        if (ok) {
          await this.$store.dispatch('issuer/checkWhitelistEnabled')
          // 获取代币总供应量
          await this.$store.dispatch('issuer/fetchTotalSupply')
          // 更新本地whitelistEnabled状态
          this.whitelistEnabled = this.$store.state.issuer.whitelistEnabled
          // 获取白名单列表
          this.$store.commit('issuer/SET_WHITELIST', this.$store.state.issuer.whitelist)
          ElMessage.success('已验证发行方身份')
        } else {
          // ElMessage.warning('当前连接地址不是合约Owner')
        }
      } catch (e) {
        ElMessage.error(e.message || '初始化失败')
      }
    },
    async switchWalletAddress() {
      try {
        // 调用wallet模块的connectWallet action来切换钱包地址
        // 这会触发MetaMask的选择账户界面
        await this.$store.dispatch('wallet/connectWallet')
        
        // 不再自动调用initIssuer，只允许用户手动触发
        // 重新初始化发行方身份
        // await this.initIssuer()
        
        ElMessage.success('钱包地址已切换，请手动点击"载入并校验"按钮')
      } catch (error) {
        ElMessage.error('切换钱包地址失败: ' + (error.message || '未知错误'))
      }
    },
    async doMint() {
      // 如果接收地址为空，则默认使用owner地址
      const toAddress = this.mintForm.to || this.ownerAddress
      if (!toAddress || !this.mintForm.amount) return
      this.loading.mint = true
      try {
        await this.mint({ to: toAddress, amount: this.mintForm.amount })
        ElMessage.success('铸造成功')
      } catch (e) {
        ElMessage.error(e?.error?.message || e.message || '铸造失败')
      } finally { this.loading.mint = false }
    },
    async doBurn() {
      // 如果来源地址为空，则默认使用owner地址
      const fromAddress = this.burnForm.from || this.ownerAddress
      if (!fromAddress || !this.burnForm.amount) return
      this.loading.burn = true
      try {
        await this.burn({ from: fromAddress, amount: this.burnForm.amount })
        ElMessage.success('销毁成功')
      } catch (e) {
        ElMessage.error(e?.error?.message || e.message || '销毁失败')
      } finally { this.loading.burn = false }
    },
    async toggleWhitelist(val) {
      try {
        await this.setWhitelist(val)
        ElMessage.success(val ? '白名单已启用' : '白名单已关闭')
        // 更新store中的白名单状态
        this.$store.commit('issuer/SET_WHITELIST_ENABLED', val)
        // 更新白名单列表显示
        this.$store.commit('issuer/SET_WHITELIST', this.$store.state.issuer.whitelist)
      } catch (e) {
        ElMessage.error('切换白名单失败')
        this.whitelistEnabled = !val
      }
    },
    async addToWhitelist() {
      if (!this.wlForm.account) return
      this.loading.add = true
      try {
        await this.addToWhitelist(this.wlForm.account)
          ElMessage.success('已添加到白名单')
          // 添加后清空输入框
          this.wlForm.account = ''
          // 更新白名单列表显示
          this.$store.commit('issuer/SET_WHITELIST', this.$store.state.issuer.whitelist)
      } catch (e) {
        ElMessage.error('添加失败')
      } finally { this.loading.add = false }
    },
    async removeFromWhitelist() {
      if (!this.wlForm.account) return
      this.loading.remove = true
      try {
        await this.removeFromWhitelist(this.wlForm.account)
        ElMessage.success('已从白名单移除')
      } catch (e) {
        ElMessage.error('移除失败')
      } finally { this.loading.remove = false }
    },
    async removeFromWhitelistByAddress(address) {
      if (!address) return
      this.loading.remove = true
      try {
        await this.removeFromWhitelist(address)
        ElMessage.success('已从白名单移除')
        // 更新白名单列表显示
        this.$store.commit('issuer/SET_WHITELIST', this.$store.state.issuer.whitelist)
      } catch (e) {
        ElMessage.error('移除失败')
      } finally { this.loading.remove = false }
    },
    async doDeposit() {
      if (!this.depositForm.userId || !this.depositForm.amount) return
      this.loading.deposit = true
      try {
        await walletAPI.deposit({ user_id: this.depositForm.userId, amount: this.depositForm.amount })
        ElMessage.success('后端充值成功')
      } catch (e) {
        ElMessage.error('后端充值失败')
      } finally { this.loading.deposit = false }
    },
    
    async refreshOverview() {
      try {
        // 重新获取发行方信息
        // 先调用后端接口手动刷新总供应量数据
        const { contractAPI } = await import('@/api/wallet')
        await contractAPI.refreshTotalSupply()
        // 再获取最新的总供应量数据
        await this.$store.dispatch('issuer/fetchTotalSupply')
        await this.$store.dispatch('issuer/fetchMintedAmount')
        await this.$store.dispatch('issuer/fetchBurnedAmount')
        ElMessage.success('数据已刷新')
      } catch (error) {
        ElMessage.error('刷新数据失败: ' + (error.message || '未知错误'))
      }
    }
  }
}
</script>

<style scoped>
.issuer-page { padding: 20px; background-color: #f5f5f5; color: #333; }
.page-header { margin-bottom: 20px; }
.page-header h1 { margin: 0; color: #333; }
.subtitle { color: #666; }

/* 导航栏样式 */
.nav-tabs { margin-bottom: 20px; }
.nav-tabs .el-button { 
  margin-right: 10px; 
  border-radius: 4px 4px 0 0;
}
.nav-tabs .el-button:last-child { margin-right: 0; }
.admin-entry { 
  display: inline-block;
  padding: 8px 16px;
  background-color: #409eff;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  transition: background-color 0.3s;
}
.admin-entry:hover {
  background-color: #66b1ff;
}
.card { margin-bottom: 20px; background-color: #ffffff; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.card-title { font-weight: 700; margin-bottom: 12px; color: #333; }
.config-form { max-width: 600px; }
.mono { font-family: monospace; }
.ml-10 { margin-left: 10px; }
.mb-10 { margin-bottom: 10px; }
.mt-20 { margin-top: 20px; }
.w-100 { width: 100%; }
.btns { display: flex; gap: 10px; }
.whitelist-list { margin-top: 20px; }

/* 货币总览样式 */
.currency-overview { max-width: 600px; }
.overview-item { display: flex; justify-content: space-between; margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px; }
.overview-label { font-weight: 600; color: #606266; }
.overview-value { font-weight: 700; color: #303133; }

/* 改善对比度 */
.el-button {
  color: #333;
  border-color: #dcdfe6;
}

.el-tag {
  color: #333;
  border-color: #dcdfe6;
}

.el-input__inner {
  background-color: #fff;
  color: #333;
  border-color: #dcdfe6;
}

.el-form-item__label {
  color: #333;
}
</style>
