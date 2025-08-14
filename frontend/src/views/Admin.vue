<template>
  <div class="admin-page">
    <div class="page-header">
      <h1>⚙️ 管理员控制台</h1>
      <p class="subtitle">系统管理功能</p>
    </div>

    <el-card class="card">
      <div class="card-title">用户管理</div>
      <p>在这里可以管理用户账户、权限等。</p>
      <el-button type="primary">查看用户列表</el-button>
    </el-card>

    <el-card class="card">
      <div class="card-title">系统配置</div>
      <p>在这里可以配置系统参数。</p>
      <el-button type="primary">系统设置</el-button>
    </el-card>
  </div>
</template>

<script>
import { ElCard, ElButton } from 'element-plus'

export default {
  name: 'AdminConsole',
  components: { ElCard, ElButton },
  data() {
    return {}
  },
  methods: {}
}
</script>

<style scoped>
.admin-page { padding: 20px; }
.page-header { margin-bottom: 20px; }
.subtitle { color: #666; }
.card { margin-bottom: 20px; }
.card-title { font-weight: 700; margin-bottom: 12px; }

.page-title {
  color: #303133;
  margin-bottom: 30px;
  text-align: center;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-top: 30px;
}

.feature-card {
  background: #ffffff;
  border: 1px solid #ebeef5;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.feature-content {
  text-align: center;
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 15px;
  color: #409eff;
}

.feature-title {
  font-size: 1.3rem;
  margin-bottom: 10px;
  color: #303133;
}

.feature-desc {
  color: #606266;
  margin-bottom: 20px;
}
</style>