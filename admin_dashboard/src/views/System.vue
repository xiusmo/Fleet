<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import api from '../api'
import * as echarts from 'echarts'

const systemStatus = ref({})
const processes = ref([])
const dbHealth = ref({})
const dbHistory = ref([])
const loadingSystem = ref(true)
const loadingProcesses = ref(true)
const loadingDbHealth = ref(true)
let dbChart = null

// 轮询间隔（毫秒）
const pollingInterval = 10000
let systemPolling = null
let processesPolling = null
let dbHealthPolling = null

// 计算属性：获取根目录磁盘信息
const rootDiskInfo = computed(() => {
  if (systemStatus.value?.disk && systemStatus.value.disk['/']) {
    return systemStatus.value.disk['/']
  }
  return { total: 0, used: 0, free: 0, percent: 0 }
})

// 计算属性：获取主数据卷信息（通常是 /System/Volumes/Data）
const dataVolumeInfo = computed(() => {
  if (systemStatus.value?.disk && systemStatus.value.disk['/System/Volumes/Data']) {
    return systemStatus.value.disk['/System/Volumes/Data']
  }
  return { total: 0, used: 0, free: 0, percent: 0 }
})

// 计算属性：获取主网络接口（en0）信息
const mainNetworkInterface = computed(() => {
  if (systemStatus.value?.net_io && systemStatus.value.net_io['en0']) {
    return systemStatus.value.net_io['en0']
  }
  return { bytes_sent: 0, bytes_recv: 0, packets_sent: 0, packets_recv: 0 }
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

// 获取进程信息
const fetchProcesses = async () => {
  loadingProcesses.value = true
  try {
    const response = await api.system.getProcesses()
    processes.value = response.data
  } catch (error) {
    console.error('获取进程信息失败:', error)
  } finally {
    loadingProcesses.value = false
  }
}

// 获取数据库健康状态
const fetchDatabaseHealth = async () => {
  loadingDbHealth.value = true
  try {
    const response = await api.system.getDatabaseHealth()
    dbHealth.value = response.data
    
    // 添加到历史记录，保留最近10条数据
    const timestamp = new Date(dbHealth.value.timestamp).toLocaleTimeString()
    const responseTime = dbHealth.value.details.connection_test.response_time_ms
    dbHistory.value.push({
      timestamp,
      responseTime,
      status: dbHealth.value.status
    })
    
    // 只保留最近10个数据点
    if (dbHistory.value.length > 10) {
      dbHistory.value.shift()
    }
    
    // 更新图表
    updateDbChart()
  } catch (error) {
    console.error('获取数据库健康状态失败:', error)
  } finally {
    loadingDbHealth.value = false
  }
}

// 更新数据库响应时间图表
const updateDbChart = () => {
  if (!dbChart) return
  
  const timestamps = dbHistory.value.map(item => item.timestamp)
  const responseTimes = dbHistory.value.map(item => item.responseTime)
  const statuses = dbHistory.value.map(item => item.status)
  
  // 根据状态设置颜色
  const colors = statuses.map(status => {
    return status === 'healthy' ? '#67C23A' : '#F56C6C'
  })
  
  dbChart.setOption({
    xAxis: {
      data: timestamps
    },
    series: [{
      data: responseTimes.map((value, index) => ({
        value,
        itemStyle: {
          color: colors[index]
        }
      }))
    }]
  })
}

// 初始化数据库响应时间图表
const initDbChart = () => {
  const chartDom = document.getElementById('db-response-chart')
  if (!chartDom) return
  
  dbChart = echarts.init(chartDom, null, { renderer: 'canvas' })
  
  // 设置图表选项
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const index = params[0].dataIndex
        const status = dbHistory.value[index]?.status || '-'
        return `时间: ${params[0].axisValue}<br/>响应时间: ${params[0].value.toFixed(2)}ms<br/>状态: ${status}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [],
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '响应时间(ms)',
      min: 0
    },
    series: [{
      name: '响应时间',
      type: 'bar',
      data: [],
      barWidth: '60%',
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  
  dbChart.setOption(option)
}

// 格式化内存大小（字节转换为MB/GB）
const formatMemory = (bytes) => {
  if (bytes === undefined || bytes === null) return '-'
  
  if (bytes < 1024 * 1024) {
    return (bytes / 1024).toFixed(2) + ' KB'
  } else if (bytes < 1024 * 1024 * 1024) {
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  } else {
    return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
  }
}

// 格式化CPU使用率
const formatCpuPercent = (percent) => {
  if (percent === undefined || percent === null) return '-'
  return percent.toFixed(1) + '%'
}

// 格式化时间
const formatUptime = (seconds) => {
  if (seconds === undefined || seconds === null) return '-'
  
  const days = Math.floor(seconds / (24 * 60 * 60))
  const hours = Math.floor((seconds % (24 * 60 * 60)) / (60 * 60))
  const minutes = Math.floor((seconds % (60 * 60)) / 60)
  
  let result = ''
  if (days > 0) result += `${days}天`
  if (hours > 0 || days > 0) result += `${hours}小时`
  result += `${minutes}分钟`
  
  return result
}

// 格式化日期时间
const formatDateTime = (timestamp) => {
  if (!timestamp) return '-'
  try {
    return new Date(timestamp).toLocaleString()
  } catch (error) {
    return timestamp
  }
}

// 开始自动刷新数据
const startPolling = () => {
  // 清除已有的轮询
  stopPolling()
  
  // 立即加载一次数据
  fetchSystemStatus()
  fetchProcesses()
  fetchDatabaseHealth()
  
  // 设置定时刷新
  systemPolling = setInterval(fetchSystemStatus, pollingInterval)
  processesPolling = setInterval(fetchProcesses, pollingInterval)
  dbHealthPolling = setInterval(fetchDatabaseHealth, pollingInterval)
}

// 停止自动刷新
const stopPolling = () => {
  if (systemPolling) clearInterval(systemPolling)
  if (processesPolling) clearInterval(processesPolling)
  if (dbHealthPolling) clearInterval(dbHealthPolling)
}

onMounted(() => {
  startPolling()
  // 窗口大小变化时重新调整图表大小
  window.addEventListener('resize', () => {
    if (dbChart) dbChart.resize()
  })
  
  // 初始化图表
  setTimeout(() => {
    initDbChart()
  }, 100)
})

// 组件卸载时清除轮询
onUnmounted(() => {
  stopPolling()
  // 移除事件监听
  window.removeEventListener('resize', () => {
    if (dbChart) dbChart.resize()
  })
  
  // 销毁图表实例
  if (dbChart) {
    dbChart.dispose()
    dbChart = null
  }
})
</script>

<template>
  <div class="system-container">
    <h1 class="page-title">系统状态</h1>
    
    <!-- 系统资源卡片 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="never" class="mb-20">
          <template #header>
            <div class="card-header-with-action">
              <span>系统资源信息</span>
              <el-button type="primary" size="small" @click="fetchSystemStatus" :loading="loadingSystem">刷新</el-button>
            </div>
          </template>
          
          <el-descriptions :column="4" border v-loading="loadingSystem">
            <el-descriptions-item label="CPU使用率">
              <el-progress 
                :percentage="systemStatus.cpu_percent" 
                :status="systemStatus.cpu_percent > 80 ? 'exception' : ''"
              />
            </el-descriptions-item>
            <el-descriptions-item label="内存使用率">
              <el-progress 
                :percentage="systemStatus.memory?.percent" 
                :status="systemStatus.memory?.percent > 80 ? 'exception' : ''"
              />
            </el-descriptions-item>
            <el-descriptions-item label="数据卷使用率">
              <el-progress 
                :percentage="dataVolumeInfo.percent" 
                :status="dataVolumeInfo.percent > 80 ? 'exception' : ''"
              />
            </el-descriptions-item>
            <el-descriptions-item label="系统负载">
              {{ systemStatus.load_avg ? systemStatus.load_avg.join(' / ') : '-' }}
            </el-descriptions-item>
            
            <el-descriptions-item label="总内存">
              {{ formatMemory(systemStatus.memory?.total) }}
            </el-descriptions-item>
            <el-descriptions-item label="已使用内存">
              {{ formatMemory(systemStatus.memory?.used) }}
            </el-descriptions-item>
            <el-descriptions-item label="总磁盘空间">
              {{ formatMemory(dataVolumeInfo.total) }}
            </el-descriptions-item>
            <el-descriptions-item label="已使用磁盘">
              {{ formatMemory(dataVolumeInfo.used) }}
            </el-descriptions-item>
            
            <el-descriptions-item label="CPU核心数">
              {{ systemStatus.cpu_count || '-' }} 核心 (物理核心: {{ systemStatus.cpu_physical_count || '-' }})
            </el-descriptions-item>
            <el-descriptions-item label="系统运行时间">
              {{ formatUptime(systemStatus.uptime_seconds) }}
            </el-descriptions-item>
            <el-descriptions-item label="启动时间">
              {{ formatDateTime(systemStatus.boot_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="进程数">
              {{ systemStatus.process_count || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 网络信息卡片 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="never" class="mb-20">
          <template #header>
            <div class="card-header-with-action">
              <span>网络接口信息 (主接口: en0)</span>
            </div>
          </template>
          
          <el-descriptions :column="4" border v-loading="loadingSystem">
            <el-descriptions-item label="发送数据">
              {{ formatMemory(mainNetworkInterface.bytes_sent) }}
            </el-descriptions-item>
            <el-descriptions-item label="接收数据">
              {{ formatMemory(mainNetworkInterface.bytes_recv) }}
            </el-descriptions-item>
            <el-descriptions-item label="发送包数">
              {{ mainNetworkInterface.packets_sent }}
            </el-descriptions-item>
            <el-descriptions-item label="接收包数">
              {{ mainNetworkInterface.packets_recv }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 数据库健康状态卡片 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="never" class="mb-20">
          <template #header>
            <div class="card-header-with-action">
              <span>数据库健康状态</span>
              <el-button type="primary" size="small" @click="fetchDatabaseHealth" :loading="loadingDbHealth">刷新</el-button>
            </div>
          </template>
          
          <div v-loading="loadingDbHealth">
            <!-- 数据库健康状态基本信息 -->
            <el-descriptions :column="4" border>
              <el-descriptions-item label="状态">
                <el-tag :type="dbHealth.status === 'healthy' ? 'success' : 'danger'">
                  {{ dbHealth.status === 'healthy' ? '健康' : '异常' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="最后检查时间">
                {{ formatDateTime(dbHealth.timestamp) }}
              </el-descriptions-item>
              <el-descriptions-item label="数据库版本">
                PostgreSQL {{ dbHealth.details?.database_version?.split(' ')[1] || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="数据库大小">
                {{ dbHealth.details?.database_size?.formatted || '-' }}
              </el-descriptions-item>
            </el-descriptions>
            
            <!-- 数据库响应时间图表 -->
            <div class="chart-container">
              <h3 class="chart-title">数据库响应时间监控</h3>
              <div id="db-response-chart" class="chart"></div>
            </div>
            
            <!-- 连接池信息 -->
            <h3 class="section-title">连接池状态</h3>
            <el-descriptions :column="4" border>
              <el-descriptions-item label="已检出连接">
                {{ dbHealth.details?.connection_pool?.checked_out || 0 }}
              </el-descriptions-item>
              <el-descriptions-item label="已检入连接">
                {{ dbHealth.details?.connection_pool?.checkedin || 0 }}
              </el-descriptions-item>
              <el-descriptions-item label="连接池大小">
                {{ dbHealth.connection?.pool_size || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="连接池超时">
                {{ dbHealth.connection?.pool_timeout || '-' }}秒
              </el-descriptions-item>
            </el-descriptions>
            
            <!-- 数据表信息 -->
            <h3 class="section-title">数据表信息</h3>
            <el-table
              :data="Object.entries(dbHealth.table_stats || {}).map(([name, info]) => ({
                name,
                ...info
              }))"
              style="width: 100%"
              border
            >
              <el-table-column prop="name" label="表名" min-width="150" />
              <el-table-column prop="row_count" label="行数" width="120" />
              <el-table-column prop="size_formatted" label="大小" width="120" />
              <el-table-column prop="size_bytes" label="字节数" width="120">
                <template #default="scope">
                  {{ formatMemory(scope.row.size_bytes) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 磁盘详情卡片 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="never" class="mb-20">
          <template #header>
            <div class="card-header-with-action">
              <span>磁盘详情</span>
            </div>
          </template>
          
          <el-table
            :data="Object.entries(systemStatus.disk || {}).map(([mount, info]) => ({
              mount,
              ...info
            }))"
            style="width: 100%"
            v-loading="loadingSystem"
            border
          >
            <el-table-column prop="mount" label="挂载点" min-width="200" />
            <el-table-column prop="total" label="总空间" width="120">
              <template #default="scope">
                {{ formatMemory(scope.row.total) }}
              </template>
            </el-table-column>
            <el-table-column prop="used" label="已使用" width="120">
              <template #default="scope">
                {{ formatMemory(scope.row.used) }}
              </template>
            </el-table-column>
            <el-table-column prop="free" label="空闲" width="120">
              <template #default="scope">
                {{ formatMemory(scope.row.free) }}
              </template>
            </el-table-column>
            <el-table-column prop="percent" label="使用率" width="180">
              <template #default="scope">
                <el-progress 
                  :percentage="scope.row.percent" 
                  :status="scope.row.percent > 80 ? 'exception' : ''"
                  :stroke-width="15"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 进程列表 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header-with-action">
          <span>进程列表</span>
          <el-button type="primary" size="small" @click="fetchProcesses" :loading="loadingProcesses">刷新</el-button>
        </div>
      </template>
      
      <el-table
        :data="processes"
        style="width: 100%"
        v-loading="loadingProcesses"
        border
      >
        <el-table-column prop="pid" label="PID" width="80" />
        <el-table-column prop="name" label="进程名称" min-width="150" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="cpu_percent" label="CPU使用率" width="120">
          <template #default="scope">
            {{ formatCpuPercent(scope.row.cpu_percent) }}
          </template>
        </el-table-column>
        <el-table-column prop="memory_percent" label="内存使用率" width="120">
          <template #default="scope">
            {{ formatCpuPercent(scope.row.memory_percent) }}
          </template>
        </el-table-column>
        <el-table-column prop="memory_rss" label="内存占用" width="120">
          <template #default="scope">
            {{ formatMemory(scope.row.memory_rss) }}
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" min-width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.create_time) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.system-container {
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
}

.mb-20 {
  margin-bottom: 20px;
}

.card-header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.el-descriptions {
  margin-bottom: 10px;
  width: 100%;
  color: var(--text-color);
}

.chart-container {
  margin: 20px 0;
}

.chart-title, .section-title {
  font-size: 16px;
  margin: 20px 0 10px;
  color: var(--text-color);
}

.chart {
  height: 300px;
  width: 100%;
  margin-top: 15px;
}

/* 深色模式调整 */
@media (prefers-color-scheme: dark) {
  :deep(.el-descriptions__cell) {
    background-color: var(--card-background);
  }
  
  :deep(.el-descriptions__label) {
    background-color: #252525;
    color: var(--text-color);
  }
  
  :deep(.el-descriptions__content) {
    color: var(--text-color);
    background-color: var(--card-background);
  }
  
  :deep(.el-progress__text) {
    color: var(--text-color);
  }
  
  :deep(.el-progress-bar__outer) {
    background-color: #2a2a2a;
  }
  
  :deep(.el-card__header) {
    border-bottom-color: var(--border-color);
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
  
  :deep(.el-table__body tr:hover > td.el-table__cell) {
    background-color: #2a2a2a !important;
  }
  
  :deep(.el-table--border .el-table__cell) {
    border-color: var(--border-color);
  }
  
  :deep(.el-table__row td.el-table__cell) {
    color: var(--text-color);
  }
  
  :deep(.el-descriptions) {
    color: var(--text-color);
    --el-descriptions-item-bordered-label-background: #252525;
  }
  
  :deep(.el-descriptions__body) {
    background-color: var(--card-background);
  }
  
  :deep(.el-descriptions__table) {
    background-color: var(--card-background);
  }
  
  :deep(.el-descriptions__title) {
    color: var(--text-color);
  }
  
  :deep(.page-title) {
    color: var(--text-color);
  }
  
  :deep(.card-header-with-action span) {
    color: var(--text-color);
  }
  
  :deep(.el-empty__description) {
    color: var(--text-color);
  }
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .el-descriptions :deep(.el-descriptions__body) {
    width: 100%;
  }
  
  .el-descriptions :deep(.el-descriptions__table) {
    width: 100%;
    table-layout: fixed;
  }
}

@media (max-width: 768px) {
  .system-container {
    padding: 10px;
  }
  
  .el-descriptions :deep(.el-descriptions__label) {
    width: 100px;
    min-width: 100px;
  }
}
</style> 