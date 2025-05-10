<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import api from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const workers = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('添加工作节点')
const isEdit = ref(false)

const workerForm = reactive({
  id: null,
  name: '',
  description: '',
  endpoint: '',
  subdomain: '',
  capabilities: {}
})

// 用于在表单中显示和编辑的 capabilities 字符串
const capabilitiesStr = ref('{}')

// 监听 workerForm.capabilities 变化，更新字符串表示
const updateCapabilitiesStr = (obj) => {
  try {
    capabilitiesStr.value = JSON.stringify(obj || {}, null, 2)
  } catch (e) {
    capabilitiesStr.value = '{}'
    console.error('解析 capabilities 失败:', e)
  }
}

// 处理 capabilities 字符串变化，更新对象
const handleCapabilitiesChange = (str) => {
  // 移除实时验证，只保存用户输入的字符串
  capabilitiesStr.value = str
}

const workerFormRules = {
  name: [
    { required: true, message: '请输入节点名称', trigger: 'blur' }
  ],
  endpoint: [
    { required: true, message: '请输入节点地址', trigger: 'blur' },
    { pattern: /^(https?:\/\/\S+|\/\S+)/i, message: '请输入有效的URL地址或路径', trigger: 'blur' }
  ],
  subdomain: [
    { required: true, message: '请输入子域名', trigger: 'blur' }
  ]
}

const formRef = ref(null)
const dialogLoading = ref(false)

// 获取所有工作节点
const fetchWorkers = async () => {
  loading.value = true
  try {
    const response = await api.workers.getAll()
    workers.value = response.data
  } catch (error) {
    console.error('获取工作节点失败:', error)
    ElMessage.error('获取工作节点失败')
  } finally {
    loading.value = false
  }
}

// 打开添加工作节点对话框
const handleAdd = () => {
  dialogTitle.value = '添加工作节点'
  isEdit.value = false
  resetForm()
  capabilitiesStr.value = '{}'
  dialogVisible.value = true
}

// 打开编辑工作节点对话框
const handleEdit = (row) => {
  dialogTitle.value = '编辑工作节点'
  isEdit.value = true
  
  // 复制数据到表单
  Object.keys(workerForm).forEach(key => {
    if (key in row) {
      if (key === 'capabilities') {
        workerForm[key] = JSON.parse(JSON.stringify(row[key] || {}))
        updateCapabilitiesStr(workerForm[key])
      } else {
        workerForm[key] = row[key]
      }
    }
  })
  
  dialogVisible.value = true
}

// 删除工作节点
const handleDelete = async (row, event) => {
  // 阻止事件冒泡，避免触发行点击事件
  if (event) {
    event.stopPropagation()
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除工作节点 "${row.name}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.workers.delete(row.id)
    ElMessage.success('删除成功')
    fetchWorkers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除工作节点失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 处理行点击事件
const handleRowClick = (row) => {
  handleEdit(row)
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  // 先验证 capabilities 格式
  try {
    workerForm.capabilities = JSON.parse(capabilitiesStr.value || '{}')
  } catch (e) {
    ElMessage.error('节点能力 JSON 格式无效，请检查语法')
    return
  }
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      dialogLoading.value = true
      try {
        if (isEdit.value) {
          // 更新工作节点
          const id = workerForm.id
          const data = { ...workerForm }
          delete data.id // 删除id字段
          
          await api.workers.update(id, data)
          ElMessage.success('更新成功')
        } else {
          // 添加工作节点
          const data = { ...workerForm }
          delete data.id
          
          await api.workers.create(data)
          ElMessage.success('添加成功')
        }
        
        dialogVisible.value = false
        fetchWorkers()
      } catch (error) {
        console.error('保存工作节点失败:', error)
        ElMessage.error('保存失败')
      } finally {
        dialogLoading.value = false
      }
    }
  })
}

// 重置表单
const resetForm = () => {
  Object.keys(workerForm).forEach(key => {
    workerForm[key] = key === 'id' ? null : key === 'capabilities' ? {} : ''
  })
  capabilitiesStr.value = '{}'
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 格式化节点状态
const formatStatus = (status) => {
  const statusMap = {
    'online': { text: '在线', type: 'success' },
    'offline': { text: '离线', type: 'info' },
    'busy': { text: '忙碌中', type: 'warning' },
    'error': { text: '错误', type: 'danger' }
  }
  
  return statusMap[status] || { text: status, type: 'info' }
}

// 格式化时间
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) {
    return '-'
  }
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchWorkers()
})
</script>

<template>
  <div class="workers-container">
    <div class="page-header">
      <h1 class="page-title">工作节点管理</h1>
      <el-button type="primary" @click="handleAdd">添加工作节点</el-button>
    </div>
    
    <el-card shadow="never" class="workers-card">
      <template #header>
        <div class="card-header-with-action">
          <span>工作节点列表</span>
          <el-button type="primary" size="small" @click="fetchWorkers" :loading="loading">刷新</el-button>
        </div>
      </template>
      
      <el-table
        :data="workers"
        style="width: 100%"
        v-loading="loading"
        border
        highlight-current-row
        @row-click="handleRowClick"
      >
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            {{ scope.row.description || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="endpoint" label="节点地址" min-width="180" show-overflow-tooltip />
        <el-table-column prop="subdomain" label="子域名" min-width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="formatStatus(scope.row.status).type">
              {{ formatStatus(scope.row.status).text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_heartbeat" label="最后心跳" min-width="180">
          <template #default="scope">
            {{ formatDate(scope.row.last_heartbeat) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="70" fixed="right">
          <template #default="scope">
            <el-button
              size="small"
              type="danger"
              plain
              @click="handleDelete(scope.row, $event)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加/编辑工作节点对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="workerForm"
        :rules="workerFormRules"
        label-width="100px"
      >
        <el-form-item label="节点名称" prop="name">
          <el-input v-model="workerForm.name" placeholder="请输入节点名称" />
        </el-form-item>
        
        <el-form-item label="节点描述" prop="description">
          <el-input v-model="workerForm.description" placeholder="请输入节点描述" type="textarea" :rows="2" />
        </el-form-item>
        
        <el-form-item label="节点地址" prop="endpoint">
          <el-input v-model="workerForm.endpoint" placeholder="请输入节点地址，例如：http://worker.example.com" />
        </el-form-item>
        
        <el-form-item label="子域名" prop="subdomain">
          <el-input v-model="workerForm.subdomain" placeholder="请输入子域名" />
        </el-form-item>
        
        <el-form-item label="节点能力" prop="capabilities">
          <el-input
            v-model="capabilitiesStr"
            placeholder="请输入节点能力（JSON格式）"
            type="textarea"
            :rows="4"
            @input="handleCapabilitiesChange"
          />
          <div class="form-item-tip">请输入有效的 JSON 格式，例如：{"gpu": true, "maxTasks": 5}（提交时会自动验证格式）</div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="dialogLoading">
            确认
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.workers-container {
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
}

.workers-card {
  width: 100%;
  background-color: var(--card-background);
  transition: background-color 0.3s;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  width: 100%;
}

.card-header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.dialog-footer {
  text-align: right;
}

.table-tip {
  margin-top: 15px;
}

.form-item-tip {
  font-size: 12px;
  color: var(--color-text-secondary, #909399);
  margin-top: 5px;
  line-height: 1.4;
}

/* 深色模式调整 */
@media (prefers-color-scheme: dark) {
  :deep(.el-dialog) {
    background-color: var(--card-background);
  }
  
  :deep(.el-dialog__header) {
    color: var(--text-color);
  }
  
  :deep(.el-dialog__title) {
    color: var(--text-color);
  }
  
  :deep(.el-dialog__body) {
    color: var(--text-color);
  }
  
  :deep(.el-form-item__label) {
    color: var(--text-color);
  }
  
  :deep(.el-table__body tr:hover > td.el-table__cell) {
    background-color: #2a2a2a !important;
  }
  
  :deep(.el-table .el-table__row.current-row > td.el-table__cell) {
    background-color: #384048 !important;
  }
  
  :deep(.el-tag) {
    border: 1px solid transparent;
  }
  
  :deep(.el-tag--info) {
    background-color: #363636;
    color: #a0a0a0;
  }
  
  :deep(.el-table--border .el-table__cell) {
    border-color: var(--border-color);
  }
  
  :deep(.el-table__header-wrapper th.el-table__cell) {
    background-color: #252525;
    color: var(--text-color);
  }
  
  .form-item-tip {
    color: #909399;
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .workers-container {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .page-header .el-button {
    margin-top: 10px;
  }
}
</style> 