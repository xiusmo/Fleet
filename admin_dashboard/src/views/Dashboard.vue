<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'
import { Cpu, Monitor, Folder, Connection } from '@element-plus/icons-vue'

const systemStatus = ref({})
const workers = ref([])
const logs = ref([])
const loadingSystem = ref(true)
const loadingWorkers = ref(true)
const loadingLogs = ref(true)

// 计算属性：获取主数据卷信息（通常是 /System/Volumes/Data）
const dataVolumeInfo = computed(() => {
  if (systemStatus.value?.disk && systemStatus.value.disk['/System/Volumes/Data']) {
    return systemStatus.value.disk['/System/Volumes/Data']
  }
  return { total: 0, used: 0, free: 0, percent: 0 }
})

// 获取系统状态信息
const fetchSystemStatus = async () => {
  loadingSystem.value = true
  try {
    const response = await api.system.getStatus()
    systemStatus.value = response.data
  } catch (error) {
    console.error('获取系统状态失败:', error)
  } finally {
    loadingSystem.value = false
  }
}

// 获取工作节点列表
const fetchWorkers = async () => {
  loadingWorkers.value = true
  try {
    const response = await api.workers.getAll()
    workers.value = response.data
  } catch (error) {
    console.error('获取工作节点失败:', error)
  } finally {
    loadingWorkers.value = false
  }
}

// 获取最新日志
const fetchLogs = async () => {
  loadingLogs.value = true
  try {
    const response = await api.logs.getAll({ limit: 10 })
    logs.value = response.data
  } catch (error) {
    console.error('获取日志失败:', error)
  } finally {
    loadingLogs.value = false
  }
}

// 计算工作节点状态统计
const workerStats = computed(() => {
  const stats = {
    total: workers.value.length,
    online: 0,
    offline: 0,
    busy: 0,
    error: 0
  }
  
  workers.value.forEach(worker => {
    if (worker.status in stats) {
      stats[worker.status]++
    }
  })
  
  return stats
})

// 格式化时间
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取日志级别对应的样式
const getLogLevelStyle = (level) => {
  const styles = {
    debug: 'info',
    info: 'info',
    warning: 'warning',
    error: 'danger',
    critical: 'danger'
  }
  return styles[level] || 'info'
}

onMounted(() => {
  fetchSystemStatus()
  fetchWorkers()
  fetchLogs()
})
</script>

<template>
  <div class="dashboard-container">
    <h1 class="page-title">控制面板</h1>
    
    <!-- 系统状态卡片 -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="status-card">
          <template #header>
            <div class="card-header">
              <span>CPU 使用率</span>
              <el-icon><Cpu /></el-icon>
            </div>
          </template>
          <div class="card-value" v-if="!loadingSystem">
            {{ systemStatus.cpu_percent !== undefined ? systemStatus.cpu_percent.toFixed(1) + '%' : '加载中...' }}
          </div>
          <el-skeleton v-else :rows="1" animated />
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="status-card">
          <template #header>
            <div class="card-header">
              <span>内存使用率</span>
              <el-icon><Monitor /></el-icon>
            </div>
          </template>
          <div class="card-value" v-if="!loadingSystem">
            {{ systemStatus.memory?.percent !== undefined ? systemStatus.memory.percent.toFixed(1) + '%' : '加载中...' }}
          </div>
          <el-skeleton v-else :rows="1" animated />
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="status-card">
          <template #header>
            <div class="card-header">
              <span>磁盘使用率</span>
              <el-icon><Folder /></el-icon>
            </div>
          </template>
          <div class="card-value" v-if="!loadingSystem">
            {{ dataVolumeInfo.percent !== undefined ? dataVolumeInfo.percent.toFixed(1) + '%' : '加载中...' }}
          </div>
          <el-skeleton v-else :rows="1" animated />
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="status-card">
          <template #header>
            <div class="card-header">
              <span>工作节点</span>
              <el-icon><Connection /></el-icon>
            </div>
          </template>
          <div class="card-value" v-if="!loadingWorkers">
            {{ workerStats.online }}/{{ workerStats.total }} 在线
          </div>
          <el-skeleton v-else :rows="1" animated />
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 工作节点状态 -->
    <el-card class="box-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header-with-action">
          <span>工作节点状态</span>
          <el-button type="primary" size="small" @click="fetchWorkers">刷新</el-button>
        </div>
      </template>
      <el-table
        :data="workers"
        style="width: 100%"
        v-loading="loadingWorkers"
        border
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="endpoint" label="节点地址" min-width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag
              :type="scope.row.status === 'online' ? 'success' : 
                    scope.row.status === 'offline' ? 'info' : 
                    scope.row.status === 'busy' ? 'warning' : 'danger'"
            >
              {{ scope.row.status === 'online' ? '在线' : 
                 scope.row.status === 'offline' ? '离线' : 
                 scope.row.status === 'busy' ? '忙碌中' : '错误' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_heartbeat" label="最后心跳" min-width="160">
          <template #default="scope">
            {{ formatDate(scope.row.last_heartbeat) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 最新日志 -->
    <el-card class="box-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header-with-action">
          <span>最新系统日志</span>
          <el-button type="primary" size="small" @click="fetchLogs">刷新</el-button>
        </div>
      </template>
      <el-table
        :data="logs"
        style="width: 100%"
        v-loading="loadingLogs"
        border
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="level" label="级别" width="100">
          <template #default="scope">
            <el-tag :type="getLogLevelStyle(scope.row.level)" size="small">
              {{ scope.row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="类别" width="100" />
        <el-table-column prop="message" label="消息" min-width="250" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" min-width="160">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.dashboard-container {
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
}

.status-card {
  height: 160px;
  margin-bottom: 20px;
  width: 100%;
  background-color: var(--card-background);
  transition: background-color 0.3s;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.card-header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  text-align: center;
  margin-top: 20px;
  color: var(--text-color);
  transition: color 0.3s;
}

.el-icon {
  font-size: 20px;
  color: var(--primary-color);
}

/* 深色模式调整 */
@media (prefers-color-scheme: dark) {
  .el-tag {
    --el-tag-bg-color: transparent;
    border-color: var(--border-color);
  }
  
  :deep(.el-tag--success) {
    --el-tag-bg-color: rgba(103, 194, 58, 0.1);
    --el-tag-border-color: #67c23a;
    --el-tag-text-color: #67c23a;
    background-color: rgba(103, 194, 58, 0.1);
    color: #67c23a;
  }
  
  :deep(.el-tag--warning) {
    --el-tag-bg-color: rgba(230, 162, 60, 0.1);
    --el-tag-border-color: #e6a23c;
    --el-tag-text-color: #e6a23c;
    background-color: rgba(230, 162, 60, 0.1);
    color: #e6a23c;
  }
  
  :deep(.el-tag--danger) {
    --el-tag-bg-color: rgba(245, 108, 108, 0.1);
    --el-tag-border-color: #f56c6c;
    --el-tag-text-color: #f56c6c;
    background-color: rgba(245, 108, 108, 0.1);
    color: #f56c6c;
  }
  
  :deep(.el-tag--info) {
    --el-tag-bg-color: rgba(144, 147, 153, 0.1);
    --el-tag-border-color: #909399;
    --el-tag-text-color: #909399;
    background-color: rgba(144, 147, 153, 0.1);
    color: #909399;
  }
  
  :deep(.el-card__header) {
    border-bottom-color: var(--border-color);
  }
  
  .status-card {
    box-shadow: 0 1px 4px var(--shadow-color);
  }
  
  :deep(.el-skeleton__item) {
    background-color: #2a2a2a;
  }
  
  :deep(.el-table) {
    background-color: var(--card-background);
    color: var(--text-color);
  }
  
  :deep(.el-table__header) {
    background-color: var(--card-background);
  }
  
  :deep(.el-table__header-wrapper) {
    background-color: var(--card-background);
  }
  
  :deep(.el-table__header-wrapper th.el-table__cell) {
    background-color: #252525;
    color: var(--text-color);
  }
  
  :deep(.el-table__body-wrapper) {
    background-color: var(--card-background);
  }
  
  :deep(.el-table__body tr) {
    background-color: var(--card-background);
    color: var(--text-color);
  }
  
  :deep(.el-table__row td.el-table__cell) {
    color: var(--text-color);
  }
  
  :deep(.el-table__body tr:hover > td.el-table__cell) {
    background-color: #2a2a2a !important;
  }
  
  :deep(.el-table--border .el-table__cell) {
    border-color: var(--border-color);
  }
  
  :deep(.el-skeleton__item.is-first) {
    background-color: #2a2a2a;
  }
  
  .page-title {
    color: var(--text-color);
  }
  
  .card-header-with-action span {
    color: var(--text-color);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 10px;
  }
  
  .el-col {
    margin-bottom: 10px;
  }
  
  .card-value {
    font-size: 24px;
  }
  
  .status-card {
    height: 140px;
  }
}
</style> 