<template>
  <div class="issuer-page">
    <div class="page-header">
      <h1>🏛️ 发行方控制台</h1>
      <p class="subtitle">仅合约 Owner 可见与操作（铸币、销毁、白名单）</p>
    </div>

    <el-card class="card">
      <div class="card-title">合约配置</div>
      <el-form :model="form" label-position="top" class="config-form">
        <el-form-item label="HKDC 合约地址">
          <el-input v-model="form.contractAddress" placeholder="0x..." />
        </el-form-item>
        <el-button type="primary" @click="initIssuer">载入并校验</el-button>
        <el-tag v-if="isIssuer" type="success" class="ml-10">发行方身份</el-tag>
        <el-tag v-else type="danger" class="ml-10">非发行方</el-tag>
        <div class="hint">Owner: <span class="mono">{{ ownerAddress || '-' }}</span></div>
      </el-form>
    </el-card>

    <el-row :gutter="20" v-if="isIssuer">
      <el-col :span="12">
        <el-card class="card">
          <div class="card-title">铸币</div>
          <el-form :model="mintForm" label-position="top">
            <el-form-item label="接收地址">
              <el-input v-model="mintForm.to" placeholder="接收者地址 0x..." />
            </el-form-item>
            <el-form-item label="数量 (HKDC)">
              <el-input-number v-model="mintForm.amount" :min="0" :precision="2" :step="0.01" class="w-100" />
            </el-form-item>
            <el-button type="primary" :loading="loading.mint" @click="doMint">确认铸造</el-button>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="card">
          <div class="card-title">销毁</div>
          <el-form :model="burnForm" label-position="top">
            <el-form-item label="来源地址">
              <el-input v-model="burnForm.from" placeholder="被销毁地址 0x..." />
            </el-form-item>
            <el-form-item label="数量 (HKDC)">
              <el-input-number v-model="burnForm.amount" :min="0" :precision="2" :step="0.01" class="w-100" />
            </el-form-item>
            <el-button type="danger" :loading="loading.burn" @click="doBurn">确认销毁</el-button>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="card">
          <div class="card-title">白名单</div>
          <div class="mb-10">
            <el-switch v-model="whitelistEnabled" active-text="启用白名单" inactive-text="关闭白名单" @change="toggleWhitelist" />
          </div>
          <el-form :model="wlForm" label-position="top">
            <el-form-item label="账户地址">
              <el-input v-model="wlForm.account" placeholder="0x..." />
            </el-form-item>
            <div class="btns">
              <el-button type="success" :loading="loading.add" @click="addToWhitelist">添加</el-button>
              <el-button type="warning" :loading="loading.remove" @click="removeFromWhitelist">移除</el-button>
            </div>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="card">
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
      </el-col>
    </el-row>
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
      form: { contractAddress: '' },
      mintForm: { to: '', amount: null },
      burnForm: { from: '', amount: null },
      wlForm: { account: '' },
      whitelistEnabled: false,
      depositForm: { userId: null, amount: null },
      loading: { mint: false, burn: false, add: false, remove: false, deposit: false }
    }
  },
  computed: {
    ...mapGetters('issuer', ['isIssuer', 'ownerAddress']),
    ...mapGetters('wallet', ['walletAddress'])
  },
  methods: {
    ...mapActions('issuer', ['initIssuer', 'mint', 'burn', 'setWhitelist', 'addToWhitelist', 'removeFromWhitelist']),
    async initIssuer() {
      try {
        const ok = await this.$store.dispatch('issuer/initIssuer', this.form.contractAddress)
        if (ok) ElMessage.success('已验证发行方身份')
        else ElMessage.warning('当前连接地址不是合约Owner')
      } catch (e) {
        ElMessage.error(e.message || '初始化失败')
      }
    },
    async doMint() {
      if (!this.mintForm.to || !this.mintForm.amount) return
      this.loading.mint = true
      try {
        await this.mint({ to: this.mintForm.to, amount: this.mintForm.amount })
        ElMessage.success('铸造成功')
      } catch (e) {
        ElMessage.error(e?.error?.message || e.message || '铸造失败')
      } finally { this.loading.mint = false }
    },
    async doBurn() {
      if (!this.burnForm.from || !this.burnForm.amount) return
      this.loading.burn = true
      try {
        await this.burn({ from: this.burnForm.from, amount: this.burnForm.amount })
        ElMessage.success('销毁成功')
      } catch (e) {
        ElMessage.error(e?.error?.message || e.message || '销毁失败')
      } finally { this.loading.burn = false }
    },
    async toggleWhitelist(val) {
      try {
        await this.setWhitelist(val)
        ElMessage.success(val ? '白名单已启用' : '白名单已关闭')
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
    async doDeposit() {
      if (!this.depositForm.userId || !this.depositForm.amount) return
      this.loading.deposit = true
      try {
        await walletAPI.deposit({ user_id: this.depositForm.userId, amount: this.depositForm.amount })
        ElMessage.success('后端充值成功')
      } catch (e) {
        ElMessage.error('后端充值失败')
      } finally { this.loading.deposit = false }
    }
  }
}
</script>

<style scoped>
.issuer-page { padding: 20px; }
.page-header { margin-bottom: 20px; }
.subtitle { color: #666; }
.card { margin-bottom: 20px; }
.card-title { font-weight: 700; margin-bottom: 12px; }
.config-form { max-width: 600px; }
.mono { font-family: monospace; }
.ml-10 { margin-left: 10px; }
.mb-10 { margin-bottom: 10px; }
.w-100 { width: 100%; }
.btns { display: flex; gap: 10px; }
</style>
