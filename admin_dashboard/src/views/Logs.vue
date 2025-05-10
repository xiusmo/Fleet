<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const logs = ref([])
const loading = ref(false)
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 日志筛选条件
const filters = reactive({
  level: null,
  category: null,
  user_id: null,
  task_id: null,
  worker_id: null,
  search: '',
  start_date: null,
  end_date: null
})

// 日志级别选项
const logLevelOptions = [
  { value: 'debug', label: '调试' },
  { value: 'info', label: '信息' },
  { value: 'warning', label: '警告' },
  { value: 'error', label: '错误' },
  { value: 'critical', label: '严重' }
]

// 日志类别选项
const logCategoryOptions = [
  { value: 'system', label: '系统' },
  { value: 'task', label: '任务' },
  { value: 'worker', label: '工作节点' },
  { value: 'user', label: '用户' },
  { value: 'api', label: 'API' },
  { value: 'security', label: '安全' },
  { value: 'push', label: '推送' },
  { value: 'other', label: '其他' }
]

// 日志详情
const detailDialogVisible = ref(false)
const selectedLog = ref(null)

// 获取日志列表
const fetchLogs = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const params = {
      skip: (pagination.currentPage - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }
    
    // 添加筛选条件
    if (filters.level) params.level = filters.level
    if (filters.category) params.category = filters.category
    if (filters.user_id && !isNaN(parseInt(filters.user_id))) {
      params.user_id = parseInt(filters.user_id)
    }
    if (filters.task_id && !isNaN(parseInt(filters.task_id))) {
      params.task_id = parseInt(filters.task_id)
    }
    if (filters.worker_id && !isNaN(parseInt(filters.worker_id))) {
      params.worker_id = parseInt(filters.worker_id)
    }
    if (filters.search && filters.search.trim()) {
      params.search = filters.search.trim()
    }
    if (filters.start_date) {
      params.start_date = new Date(filters.start_date).toISOString()
    }
    if (filters.end_date) {
      params.end_date = new Date(filters.end_date).toISOString()
    }
    
    const response = await api.logs.getAll(params)
    
    // 处理返回数据
    if (Array.isArray(response.data)) {
      logs.value = response.data
      
      // 如果返回的记录少于 pageSize 并且是第一页，说明可能已读取全部数据
      if (response.data.length < pagination.pageSize && pagination.currentPage === 1) {
        pagination.total = response.data.length
      } 
      // 如果返回的记录等于 pageSize，可能还有更多数据
      else if (response.data.length === pagination.pageSize) {
        // 尝试获取总数，假设后端会返回
        pagination.total = response.headers?.['x-total-count'] 
          ? parseInt(response.headers['x-total-count']) 
          : (pagination.currentPage * pagination.pageSize) + pagination.pageSize // 保守估计
      }
      // 如果返回的记录少于 pageSize 但不是第一页，可能已经到了末尾
      else {
        pagination.total = ((pagination.currentPage - 1) * pagination.pageSize) + response.data.length
      }
    } else {
      logs.value = []
      pagination.total = 0
      console.error('API返回的数据格式不正确:', response)
    }
  } catch (error) {
    console.error('获取日志列表失败:', error)
    ElMessage.error('获取日志列表失败：' + (error.message || '未知错误'))
    logs.value = []
  } finally {
    loading.value = false
  }
}

// 删除单条日志
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除此条日志记录吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    await api.logs.delete(row.id)
    ElMessage.success('删除成功')
    await fetchLogs() // 重新加载日志
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除日志失败:', error)
      ElMessage.error('删除失败：' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

// 清空日志
const handleClearLogs = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要清空${getFilterDescription()}的日志记录吗？此操作不可恢复。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 构建清空日志的筛选条件
    const clearParams = {}
    if (filters.level) clearParams.level = filters.level
    if (filters.category) clearParams.category = filters.category
    
    if (filters.user_id && !isNaN(parseInt(filters.user_id))) {
      clearParams.user_id = parseInt(filters.user_id)
    }
    if (filters.task_id && !isNaN(parseInt(filters.task_id))) {
      clearParams.task_id = parseInt(filters.task_id)
    }
    if (filters.worker_id && !isNaN(parseInt(filters.worker_id))) {
      clearParams.worker_id = parseInt(filters.worker_id)
    }
    
    if (filters.search && filters.search.trim()) {
      clearParams.search = filters.search.trim()
    }
    if (filters.start_date) {
      clearParams.start_date = new Date(filters.start_date).toISOString()
    }
    if (filters.end_date) {
      clearParams.end_date = new Date(filters.end_date).toISOString()
    }
    
    loading.value = true
    await api.logs.clear(clearParams)
    ElMessage.success('日志已清空')
    
    // 重置为第一页并重新加载
    pagination.currentPage = 1
    await fetchLogs()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空日志失败:', error)
      ElMessage.error('清空失败：' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

// 获取筛选条件描述
const getFilterDescription = () => {
  const descriptions = []
  
  if (filters.level) {
    const levelOption = logLevelOptions.find(opt => opt.value === filters.level)
    descriptions.push(`级别为"${levelOption?.label || filters.level}"`)
  }
  
  if (filters.category) {
    const categoryOption = logCategoryOptions.find(opt => opt.value === filters.category)
    descriptions.push(`类别为"${categoryOption?.label || filters.category}"`)
  }
  
  if (filters.user_id) descriptions.push(`用户ID为${filters.user_id}`)
  if (filters.task_id) descriptions.push(`任务ID为${filters.task_id}`)
  if (filters.worker_id) descriptions.push(`工作节点ID为${filters.worker_id}`)
  if (filters.search && filters.search.trim()) descriptions.push(`包含"${filters.search.trim()}"`)
  
  if (filters.start_date) {
    descriptions.push(`开始时间为${formatDate(filters.start_date)}`)
  }
  
  if (filters.end_date) {
    descriptions.push(`结束时间为${formatDate(filters.end_date)}`)
  }
  
  return descriptions.length > 0 ? descriptions.join('、') : '所有'
}

// 处理筛选条件变化
const handleFilterChange = () => {
  pagination.currentPage = 1 // 重置为第一页
  fetchLogs()
}

// 重置筛选条件
const resetFilters = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = null
  })
  filters.search = ''
  pagination.currentPage = 1 // 重置为第一页
  fetchLogs()
}

// 格式化时间
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  
  // 检查日期是否有效
  if (isNaN(date.getTime())) {
    return '-'
  }
  
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

// 处理分页变化
const handleCurrentChange = (page) => {
  pagination.currentPage = page
  fetchLogs()
}

// 处理每页条数变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1 // 重置为第一页
  fetchLogs()
}

// 检查当前筛选条件是否有效
const validateFilters = () => {
  let valid = true
  
  // 检查数字输入是否有效
  if (filters.user_id && isNaN(parseInt(filters.user_id))) {
    ElMessage.warning('用户ID必须是数字')
    valid = false
  }
  
  if (filters.task_id && isNaN(parseInt(filters.task_id))) {
    ElMessage.warning('任务ID必须是数字')
    valid = false
  }
  
  if (filters.worker_id && isNaN(parseInt(filters.worker_id))) {
    ElMessage.warning('工作节点ID必须是数字')
    valid = false
  }
  
  // 检查日期是否有效
  if (filters.start_date && isNaN(new Date(filters.start_date).getTime())) {
    ElMessage.warning('开始日期无效')
    valid = false
  }
  
  if (filters.end_date && isNaN(new Date(filters.end_date).getTime())) {
    ElMessage.warning('结束日期无效')
    valid = false
  }
  
  // 检查日期范围
  if (filters.start_date && filters.end_date) {
    const start = new Date(filters.start_date)
    const end = new Date(filters.end_date)
    if (start > end) {
      ElMessage.warning('开始日期必须早于结束日期')
      valid = false
    }
  }
  
  return valid
}

// 处理搜索提交
const handleSearch = () => {
  if (validateFilters()) {
    handleFilterChange()
  }
}

// 点击行显示详情
const handleRowClick = (row) => {
  selectedLog.value = row
  detailDialogVisible.value = true
}

onMounted(() => {
  fetchLogs()
})
</script>

<template>
  <div class="logs-container">
    <div class="page-header">
      <h1 class="page-title">系统日志</h1>
      <el-button type="danger" @click="handleClearLogs" :loading="loading">清空日志</el-button>
    </div>
    
    <!-- 筛选条件 -->
    <el-card shadow="never" class="filters-card">
      <template #header>
        <div class="card-header-with-action">
          <span>筛选条件</span>
          <el-button type="primary" size="small" @click="resetFilters" :disabled="loading">重置</el-button>
        </div>
      </template>
      
      <div class="filters-form">
        <el-form :inline="true" :model="filters" class="filter-form">
          <el-form-item label="日志级别">
            <el-select v-model="filters.level" placeholder="选择级别" clearable>
              <el-option v-for="item in logLevelOptions" :key="item.value" :value="item.value" :label="item.label" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="日志类别">
            <el-select v-model="filters.category" placeholder="选择类别" clearable>
              <el-option v-for="item in logCategoryOptions" :key="item.value" :value="item.value" :label="item.label" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="用户ID">
            <el-input v-model="filters.user_id" placeholder="输入用户ID" clearable type="number" />
          </el-form-item>
          
          <el-form-item label="工作节点ID">
            <el-input v-model="filters.worker_id" placeholder="输入工作节点ID" clearable type="number" />
          </el-form-item>
          
          <el-form-item label="任务ID">
            <el-input v-model="filters.task_id" placeholder="输入任务ID" clearable type="number" />
          </el-form-item>
          
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="filters.start_date"
              type="datetime"
              placeholder="开始时间"
              clearable
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              :disabled-date="date => filters.end_date && date > new Date(filters.end_date)"
            />
            <span style="margin: 0 5px">至</span>
            <el-date-picker
              v-model="filters.end_date"
              type="datetime"
              placeholder="结束时间"
              clearable
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              :disabled-date="date => filters.start_date && date < new Date(filters.start_date)"
            />
          </el-form-item>
          
          <el-form-item label="关键字">
            <div class="search-input">
              <el-input v-model="filters.search" placeholder="搜索内容" clearable @keyup.enter="handleSearch" />
              <el-button type="primary" @click="handleSearch" :loading="loading">搜索</el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
    
    <el-card shadow="never" class="logs-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header-with-action">
          <span>日志列表</span>
          <el-button type="primary" size="small" @click="fetchLogs" :loading="loading">刷新</el-button>
        </div>
      </template>
      
      <el-table
        :data="logs"
        style="width: 100%"
        v-loading="loading"
        border
        empty-text="无数据"
        :header-cell-style="{ background: 'var(--header-background)', color: 'var(--header-text-color)' }"
        @row-click="handleRowClick"
        highlight-current-row
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="level" label="级别" width="100">
          <template #default="scope">
            <el-tag :type="getLogLevelStyle(scope.row.level)" size="small">
              {{ scope.row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="类别" width="120" />
        <el-table-column prop="message" label="消息" min-width="300" show-overflow-tooltip />
        <el-table-column label="相关ID" width="200">
          <template #default="scope">
            <div v-if="scope.row.user_id || scope.row.worker_id || scope.row.task_id">
              <div v-if="scope.row.user_id">用户ID: {{ scope.row.user_id }}</div>
              <div v-if="scope.row.worker_id">工作节点ID: {{ scope.row.worker_id }}</div>
              <div v-if="scope.row.task_id">任务ID: {{ scope.row.task_id }}</div>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" min-width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button
              size="small"
              type="danger"
              plain
              @click.stop="handleDelete(scope.row)"
              :disabled="loading"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container" v-if="pagination.total > 0">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100, 200]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :disabled="loading"
        />
      </div>
      
      <div class="no-data" v-else-if="!loading && logs.length === 0">
        <el-empty description="暂无数据" />
      </div>
    </el-card>
    
    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="日志详情"
      width="60%"
      :close-on-click-modal="false"
      @closed="selectedLog = null"
    >
      <div v-if="selectedLog" class="log-detail-container">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ selectedLog.id }}</el-descriptions-item>
          <el-descriptions-item label="级别">
            <el-tag :type="getLogLevelStyle(selectedLog.level)" size="small">
              {{ selectedLog.level }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="类别">{{ selectedLog.category }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ formatDate(selectedLog.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="来源">{{ selectedLog.source || '-' }}</el-descriptions-item>
          <el-descriptions-item label="相关用户ID">{{ selectedLog.user_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="相关工作节点ID">{{ selectedLog.worker_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="相关任务ID">{{ selectedLog.task_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="消息" :span="2">{{ selectedLog.message }}</el-descriptions-item>
          <el-descriptions-item label="详细信息 (JSON)" :span="2">
            <pre class="details-json">{{ JSON.stringify(selectedLog.details, null, 2) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
  </div>
</template>

<style scoped>
.logs-container {
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
}

.logs-card, .filters-card {
  width: 100%;
  background-color: var(--card-background);
  transition: background-color 0.3s;
}

.filters-form {
  margin-bottom: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  width: 100%;
}

.filter-form {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.search-input {
  display: flex;
  gap: 10px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  width: 100%;
}

.card-header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.no-data {
  padding: 40px 0;
  text-align: center;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  color: var(--text-color);
}

.log-detail-container {
  max-height: 60vh;
  overflow-y: auto;
}

.details-json {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 深色模式调整 */
@media (prefers-color-scheme: dark) {
  :deep(.el-pagination) {
    color: var(--text-color);
  }
  
  :deep(.el-pagination button) {
    background-color: var(--card-background);
    color: var(--text-color);
  }
  
  :deep(.el-pagination .el-input__inner) {
    background-color: #2a2a2a;
    color: var(--text-color);
    border-color: var(--border-color);
  }
  
  :deep(.el-select-dropdown) {
    background-color: #2a2a2a;
    border-color: var(--border-color);
  }
  
  :deep(.el-select-dropdown__item) {
    color: var(--text-color);
  }
  
  :deep(.el-date-editor), :deep(.el-date-picker) {
    --el-datepicker-text-color: var(--text-color);
    --el-datepicker-off-text-color: #909399;
    --el-datepicker-header-text-color: var(--text-color);
    --el-datepicker-border-color: var(--border-color);
    --el-datepicker-inner-border-color: var(--border-color);
    --el-datepicker-inrange-bg-color: #2a2a2a;
    --el-datepicker-inrange-hover-bg-color: #363636;
    --el-datepicker-active-color: var(--primary-color);
    --el-datepicker-hover-text-color: var(--primary-color);
  }
  
  :deep(.el-date-table td.today) {
    color: var(--primary-color) !important;
  }
  
  :deep(.el-date-picker__header-label) {
    color: var(--text-color);
  }
  
  :deep(.el-picker-panel) {
    background-color: #2a2a2a;
    border-color: var(--border-color);
  }
  
  /* 表格深色模式 */
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
    background-color: #252525 !important;
    color: var(--text-color) !important;
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
  
  /* 选中行样式 */
  :deep(.el-table .el-table__row.current-row > td.el-table__cell) {
    background-color: #384048 !important; /* 使用一个稍微不同的深色背景 */
  }
  
  :deep(.el-table--border .el-table__cell) {
    border-color: var(--border-color);
  }
  
  :deep(.el-card__header) {
    border-bottom-color: var(--border-color);
  }
  
  :deep(.page-title) {
    color: var(--text-color);
  }
  
  :deep(.card-header-with-action span) {
    color: var(--text-color);
  }
  
  :deep(.el-form-item__label) {
    color: var(--text-color);
  }
  
  :deep(.el-input__inner) {
    background-color: #2a2a2a;
    color: var(--text-color);
    border-color: var(--border-color);
  }
  
  :deep(.el-select-dropdown__item.hover), :deep(.el-select-dropdown__item:hover) {
    background-color: #363636;
  }
  
  :deep(.el-tag--danger) {
    color: #f56c6c;
    background-color: rgba(245, 108, 108, 0.1);
    border-color: #f56c6c;
  }
  
  :deep(.el-tag--warning) {
    color: #e6a23c;
    background-color: rgba(230, 162, 60, 0.1);
    border-color: #e6a23c;
  }
  
  :deep(.el-tag--info) {
    color: #909399;
    background-color: rgba(144, 147, 153, 0.1);
    border-color: #909399;
  }
  
  :deep(.el-tag--success) {
    color: #67c23a;
    background-color: rgba(103, 194, 58, 0.1);
    border-color: #67c23a;
  }
  
  :deep(.el-empty__description) {
    color: var(--text-color);
  }
  
  /* 日志详情对话框深色模式 */
  :deep(.el-dialog) {
    background-color: var(--card-background);
  }
  
  :deep(.el-dialog__title) {
    color: var(--text-color);
  }
  
  :deep(.el-dialog__body) {
    color: var(--text-color);
  }
  
  :deep(.el-descriptions__body) {
    background-color: var(--card-background);
  }
  
  :deep(.el-descriptions__label) {
    background-color: #252525;
    color: var(--text-color);
  }
  
  :deep(.el-descriptions__content) {
    color: var(--text-color);
    background-color: var(--card-background); /* 确保内容区背景色 */
  }
  
  /* 确保描述列表边框适配 */
  :deep(.el-descriptions--border) {
    border-color: var(--border-color);
  }
  :deep(.el-descriptions--border .el-descriptions__cell) {
    border-color: var(--border-color);
  }
  
  .details-json {
    background-color: #2a2a2a;
    color: #e0e0e0;
    border: 1px solid var(--border-color); /* 添加边框 */
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .logs-container {
    padding: 10px;
  }
  
  .filters-form {
    flex-direction: column;
  }
  
  .search-input {
    width: 100%;
  }
  
  .el-form-item {
    margin-bottom: 10px;
  }
}
</style> 