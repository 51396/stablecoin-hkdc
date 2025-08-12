<template>
  <div class="page">
    <el-card class="card">
      <div class="card-title">
        <el-icon><UserFilled /></el-icon>
        <span>白名单管理</span>
      </div>

      <div class="toolbar">
        <div style="display:flex; gap: 12px; align-items: center;">
          <el-input v-model="newUser" placeholder="输入用户名或地址" clearable style="width: 260px">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="addToWhitelist">
            <el-icon><Plus /></el-icon>
            添加
          </el-button>
        </div>
        <el-input v-model="keyword" placeholder="搜索" clearable style="width: 220px">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <el-table :data="filteredList" style="width: 100%" class="whitelist-table">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="username" label="用户名/地址" />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button type="text" @click="removeFromWhitelist(scope.$index)">
              <el-icon><Delete /></el-icon>
              移除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { User, UserFilled, Plus, Delete, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
export default {
  name: 'Whitelist',
  components: { User, UserFilled, Plus, Delete, Search },
  data() {
    return {
      newUser: '',
      keyword: '',
      whitelist: [
        { username: 'alice' },
        { username: 'bob' },
        { username: '0x1234...ABCD' }
      ]
    }
  },
  computed: {
    filteredList() {
      if (!this.keyword) return this.whitelist
      const k = this.keyword.toLowerCase()
      return this.whitelist.filter(it => String(it.username).toLowerCase().includes(k))
    }
  },
  methods: {
    addToWhitelist() {
      const value = this.newUser && this.newUser.trim()
      if (!value) return ElMessage.warning('请输入有效的用户名/地址')
      this.whitelist.unshift({ username: value })
      this.newUser = ''
      ElMessage.success('已添加到白名单')
    },
    removeFromWhitelist(index) {
      this.whitelist.splice(index, 1)
      ElMessage.success('已从白名单移除')
    }
  }
}
</script>

<style scoped>
.whitelist-table :deep(.el-table) { background: transparent; }
.whitelist-table :deep(.el-table th) { background: rgba(255,255,255,0.02); }
</style>
