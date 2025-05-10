<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const announcements = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('发布公告')
const isEdit = ref(false)

// 分页状态
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const announcementForm = reactive({
  uuid: '',
  title: '',
  content: '',
  status: 'draft',
  is_pinned: false,
  publish_date: null,
  cover_image: null
})

const announcementFormRules = {
  title: [
    { required: true, message: '请输入公告标题', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入公告内容', trigger: 'blur' }
  ],
}

const formRef = ref(null)
const dialogLoading = ref(false)

const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'published', label: '已发布' },
  { value: 'scheduled', label: '定时发布' },
  { value: 'archived', label: '已归档' },
  { value: 'advertisement', label: '广告' }
]

const fetchAnnouncements = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.currentPage - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }
    const response = await api.announcements.getAll(params)
    
    if (Array.isArray(response.data)) {
      announcements.value = response.data
      
      const totalCountHeader = response.headers?.['x-total-count']
      if (totalCountHeader && !isNaN(parseInt(totalCountHeader))) {
        pagination.total = parseInt(totalCountHeader)
      } else {
        if (response.data.length < pagination.pageSize) {
          pagination.total = (pagination.currentPage - 1) * pagination.pageSize + response.data.length
        } else {
          pagination.total = (pagination.currentPage * pagination.pageSize) + 1
          console.warn("后端未返回 'X-Total-Count' 响应头，分页总数可能不准确。")
        }
      }
    } else {
      announcements.value = []
      pagination.total = 0
      console.error('API返回的公告数据格式不正确:', response)
    }

  } catch (error) {
    console.error('获取公告列表失败:', error)
    ElMessage.error('获取公告列表失败: ' + (error.message || '未知错误'))
    announcements.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '发布公告'
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  try {
    dialogTitle.value = '编辑公告'
    isEdit.value = true
    
    resetForm()
    Object.keys(announcementForm).forEach(key => {
      if (row.hasOwnProperty(key)) {
        if (key === 'publish_date' && row[key]) {
          announcementForm[key] = new Date(row[key])
        } else {
          announcementForm[key] = row[key]
        }
      }
    })
    
    dialogVisible.value = true
  } catch (error) {
    console.error('准备编辑公告失败:', error)
    ElMessage.error('加载公告详情失败: ' + (error.message || '未知错误'))
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除标题为"${row.title}"的公告吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    await api.announcements.delete(row.uuid)
    ElMessage.success('删除成功')
    if (announcements.value.length === 1 && pagination.currentPage > 1) {
      pagination.currentPage--
    }
    await fetchAnnouncements()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除公告失败:', error)
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      dialogLoading.value = true
      try {
        const dataToSubmit = {
          title: announcementForm.title,
          content: announcementForm.content,
          status: announcementForm.status,
          is_pinned: announcementForm.is_pinned,
          publish_date: announcementForm.publish_date ? new Date(announcementForm.publish_date).toISOString() : null,
          cover_image: announcementForm.cover_image || null
        }

        if (isEdit.value) {
          await api.announcements.update(announcementForm.uuid, dataToSubmit)
          ElMessage.success('更新成功')
        } else {
          await api.announcements.create(dataToSubmit)
          ElMessage.success('发布成功')
        }
        
        dialogVisible.value = false
        await fetchAnnouncements()
      } catch (error) {
        console.error('保存公告失败:', error)
        const errorMsg = error.response?.data?.detail || error.message || '未知错误'
        ElMessage.error(`保存失败: ${errorMsg}`)
      } finally {
        dialogLoading.value = false
      }
    }
  })
}

const resetForm = () => {
  announcementForm.uuid = ''
  announcementForm.title = ''
  announcementForm.content = ''
  announcementForm.status = 'draft'
  announcementForm.is_pinned = false
  announcementForm.publish_date = null
  announcementForm.cover_image = null
  
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '-'
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusTagType = (status) => {
  switch (status) {
    case 'published':
    case 'advertisement':
      return 'success'
    case 'scheduled':
      return 'warning'
    case 'archived':
      return 'info'
    case 'draft':
    default:
      return 'primary'
  }
}

const handleRowClick = (row) => {
  handleEdit(row)
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  fetchAnnouncements()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  fetchAnnouncements()
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<template>
  <div class="announcements-container">
    <div class="page-header">
      <h1 class="page-title">公告管理</h1>
      <el-button type="primary" @click="handleAdd">发布公告</el-button>
    </div>
    
    <el-card shadow="never">
      <template #header>
        <div class="card-header-with-action">
          <span>公告列表</span>
          <el-button type="primary" size="small" @click="fetchAnnouncements" :loading="loading">刷新</el-button>
        </div>
      </template>
      
      <el-table
        :data="announcements"
        style="width: 100%"
        v-loading="loading"
        border
        empty-text="无数据"
        highlight-current-row
        @row-click="handleRowClick"
      >
        <el-table-column prop="title" label="标题" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ statusOptions.find(s => s.value === scope.row.status)?.label || scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publish_date" label="发布时间" min-width="160">
          <template #default="scope">
            {{ formatDate(scope.row.publish_date) }}
          </template>
        </el-table-column>
         <el-table-column prop="is_pinned" label="置顶" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_pinned ? 'success' : 'info'" size="small">
              {{ scope.row.is_pinned ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="160">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
         <el-table-column prop="updated_at" label="更新时间" min-width="160">
          <template #default="scope">
            {{ formatDate(scope.row.updated_at) }}
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
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :disabled="loading"
        />
      </div>
      <div class="no-data" v-else-if="!loading && announcements.length === 0">
        <el-empty description="暂无数据" />
      </div>
      
    </el-card>
    
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="60%" 
      :close-on-click-modal="false"
      destroy-on-close 
      @closed="resetForm" 
    >
      <el-form
        ref="formRef"
        :model="announcementForm"
        :rules="announcementFormRules"
        label-width="100px"
        v-loading="dialogLoading"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="announcementForm.title" placeholder="请输入公告标题" />
        </el-form-item>
        
        <el-form-item label="内容" prop="content">
          <el-input 
            type="textarea" 
            :rows="5" 
            v-model="announcementForm.content" 
            placeholder="请输入公告内容 (支持 Markdown)"
          />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-select v-model="announcementForm.status" placeholder="选择状态">
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="是否置顶" prop="is_pinned">
          <el-switch v-model="announcementForm.is_pinned" />
        </el-form-item>
        
        <el-form-item label="发布时间" prop="publish_date">
          <el-date-picker
            v-model="announcementForm.publish_date"
            type="datetime"
            placeholder="选择发布时间 (留空则立即发布)"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ssZ" 
            clearable
          />
        </el-form-item>
        
        <el-form-item label="封面图片URL" prop="cover_image">
          <el-input v-model="announcementForm.cover_image" placeholder="输入图片URL (可选)" clearable />
        </el-form-item>
        
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="dialogLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.announcements-container {
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
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

.card-header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  
  /* 表格深色模式 */
  :deep(.el-table) {
    background-color: var(--card-background);
    color: var(--text-color);
  }
  
  :deep(.el-table__header-wrapper th.el-table__cell) {
    background-color: #252525 !important;
    color: var(--text-color) !important;
  }
  
  :deep(.el-table__body tr) {
    background-color: var(--card-background);
  }
  
  :deep(.el-table__row td.el-table__cell) {
    color: var(--text-color);
  }
  
  :deep(.el-table__body tr:hover > td.el-table__cell) {
    background-color: #2a2a2a !important;
  }
  
  /* 选中行样式 */
  :deep(.el-table .el-table__row.current-row > td.el-table__cell) {
    background-color: #384048 !important;
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
  
  :deep(.el-dialog) {
    background-color: var(--card-background);
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
  
  :deep(.el-input__inner), :deep(.el-textarea__inner) {
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
  :deep(.el-select-dropdown__item.hover), :deep(.el-select-dropdown__item:hover) {
    background-color: #363636;
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
  
  :deep(.el-button--primary.is-plain) {
    color: #409eff;
    border-color: #409eff;
    background-color: transparent;
  }
  
  :deep(.el-button--danger.is-plain) {
    color: #f56c6c;
    border-color: #f56c6c; 
    background-color: transparent;
  }
  
  :deep(.el-empty__description) {
    color: var(--text-color);
  }
  
  /* 标签颜色适配 */
  :deep(.el-tag) {
     background-color: transparent;
  }
  :deep(.el-tag--success) {
    color: #67c23a;
    border-color: #67c23a;
  }
   :deep(.el-tag--warning) {
    color: #e6a23c;
    border-color: #e6a23c;
  }
   :deep(.el-tag--info) {
    color: #909399;
    border-color: #909399;
  }
  :deep(.el-tag--primary) {
     color: #409eff;
     border-color: #409eff;
  }
}
</style>