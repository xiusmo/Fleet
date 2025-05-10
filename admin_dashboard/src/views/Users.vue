<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const users = ref([])
const loading = ref(false)
const loadingDetail = ref(false)
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 用户详情
const detailDialogVisible = ref(false)
const selectedUser = ref(null)
const userDetail = ref(null)

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.currentPage - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }
    const response = await api.users.getAll(params)
    
    if (Array.isArray(response.data)) {
      users.value = response.data
      
      // 简单的分页总数处理，可能需要根据后端返回头优化
      if (response.data.length < pagination.pageSize && pagination.currentPage === 1) {
        pagination.total = response.data.length
      } else if (response.data.length === pagination.pageSize) {
        pagination.total = response.headers?.['x-total-count'] 
          ? parseInt(response.headers['x-total-count']) 
          : (pagination.currentPage * pagination.pageSize) + pagination.pageSize
      } else {
        pagination.total = ((pagination.currentPage - 1) * pagination.pageSize) + response.data.length
      }
      
    } else {
      users.value = []
      pagination.total = 0
      console.error('API返回的用户数据格式不正确:', response)
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败: ' + (error.message || '未知错误'))
    users.value = []
  } finally {
    loading.value = false
  }
}

// 获取用户详情
const fetchUserDetail = async (userId) => {
  loadingDetail.value = true
  try {
    const response = await api.users.getOne(userId)
    userDetail.value = response.data
  } catch (error) {
    console.error(`获取用户ID=${userId}的详情失败:`, error)
    ElMessage.error('获取用户详情失败: ' + (error.message || '未知错误'))
    userDetail.value = null
  } finally {
    loadingDetail.value = false
  }
}

// 删除用户
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.person_name || row.id}" 吗？`, 
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    await api.users.delete(row.id)
    ElMessage.success('删除成功')
    await fetchUsers() // 重新加载用户列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

// 格式化时间
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
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

// 处理分页变化
const handleCurrentChange = (page) => {
  pagination.currentPage = page
  fetchUsers()
}

// 处理每页条数变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1 // 重置为第一页
  fetchUsers()
}

// 点击行显示详情
const handleRowClick = (row) => {
  selectedUser.value = row
  userDetail.value = null // 清空之前的详情
  detailDialogVisible.value = true
  
  // 获取完整的用户详情
  fetchUserDetail(row.id)
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="users-container">
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
      <!-- 可以添加 "添加用户" 按钮 -->
    </div>
    
    <el-card shadow="never">
      <template #header>
        <div class="card-header-with-action">
          <span>用户列表</span>
          <el-button type="primary" size="small" @click="fetchUsers" :loading="loading">刷新</el-button>
        </div>
      </template>
      
      <el-table
        :data="users"
        style="width: 100%"
        v-loading="loading"
        border
        empty-text="无数据"
        highlight-current-row
        @row-click="handleRowClick"
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="person_name" label="姓名" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            {{ scope.row.person_name || '未设置' }}
          </template>
        </el-table-column>
        <el-table-column prop="school_name" label="学校" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            {{ scope.row.school_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="tel" label="电话" min-width="120" show-overflow-tooltip>
          <template #default="scope">
            {{ scope.row.tel || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
              {{ scope.row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180">
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
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :disabled="loading"
        />
      </div>
      <div class="no-data" v-else-if="!loading && users.length === 0">
        <el-empty description="暂无数据" />
      </div>
    </el-card>
    
    <!-- 用户详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="用户详情"
      width="70%"
      :close-on-click-modal="false"
      @closed="userDetail = null"
    >
      <div v-loading="loadingDetail" class="user-detail-container">
        <div v-if="userDetail" class="user-detail-content">
          <el-tabs type="border-card">
            <el-tab-pane label="基本信息">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="ID">{{ userDetail.id }}</el-descriptions-item>
                <el-descriptions-item label="姓名">{{ userDetail.person_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="用户名">{{ userDetail.username || '-' }}</el-descriptions-item>
                <el-descriptions-item label="电话">{{ userDetail.tel || '-' }}</el-descriptions-item>
                <el-descriptions-item label="学校">{{ userDetail.school_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="工作人员">{{ userDetail.worker_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="状态">
                  <el-tag :type="userDetail.is_active ? 'success' : 'info'">
                    {{ userDetail.is_active ? '激活' : '禁用' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="管理员">
                  <el-tag :type="userDetail.is_admin ? 'warning' : 'info'">
                    {{ userDetail.is_admin ? '是' : '否' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="监控状态">
                  <el-tag :type="userDetail.monitor_status ? 'success' : 'info'">
                    {{ userDetail.monitor_status ? '开启' : '关闭' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="创建时间">{{ formatDate(userDetail.created_at) }}</el-descriptions-item>
                <el-descriptions-item label="更新时间">{{ formatDate(userDetail.updated_at) }}</el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>
            
            <el-tab-pane label="IM 信息">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="IM 用户名">{{ userDetail.im_username || '-' }}</el-descriptions-item>
                <el-descriptions-item label="IM 密码">{{ userDetail.im_password || '-' }}</el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>
            
            <el-tab-pane label="系统信息">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="FID">{{ userDetail.fid || '-' }}</el-descriptions-item>
                <el-descriptions-item label="CX_UID">{{ userDetail.cx_uid || '-' }}</el-descriptions-item>
                <el-descriptions-item label="CX_D">
                  <div class="long-text">{{ userDetail.cx_d || '-' }}</div>
                </el-descriptions-item>
                <el-descriptions-item label="CX_UF">
                  <div class="long-text">{{ userDetail.cx_uf || '-' }}</div>
                </el-descriptions-item>
                <el-descriptions-item label="CX_VC3">
                  <div class="long-text">{{ userDetail.cx_vc3 || '-' }}</div>
                </el-descriptions-item>
                <el-descriptions-item label="密码哈希">{{ userDetail.hashed_password || '-' }}</el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>
          </el-tabs>
        </div>
        <div v-else-if="!loadingDetail" class="user-detail-empty">
          <el-empty description="无法获取用户详情" />
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <!-- 可以添加更多操作按钮，如禁用/启用用户 -->
        </span>
      </template>
    </el-dialog>
    
  </div>
</template>

<style scoped>
.users-container {
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

.user-detail-container {
  max-height: 70vh;
  overflow-y: auto;
}

.user-detail-content {
  padding: 5px 0;
}

.user-detail-empty {
  padding: 40px 0;
  text-align: center;
}

.no-data {
  padding: 40px 0;
  text-align: center;
}

/* 长文本样式 */
.long-text {
  word-break: break-all;
  white-space: normal;
  max-height: 80px;
  overflow-y: auto;
  padding: 5px;
  background-color: var(--color-sidebar-bg, #f5f7fa);
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
}

@media (prefers-color-scheme: dark) {
  /* 对话框深色模式 */
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
    background-color: var(--card-background);
  }
  
  :deep(.el-descriptions--border) {
    border-color: var(--border-color);
  }
  
  :deep(.el-descriptions--border .el-descriptions__cell) {
    border-color: var(--border-color);
  }
  
  /* 标签页深色模式 */
  :deep(.el-tabs__item) {
    color: var(--text-color);
  }
  
  :deep(.el-tabs__item.is-active) {
    color: var(--primary-color);
  }
  
  :deep(.el-tabs__nav-wrap::after) {
    background-color: var(--border-color);
  }
  
  :deep(.el-tabs--border-card) {
    background-color: var(--card-background);
    border-color: var(--border-color);
  }
  
  :deep(.el-tabs--border-card > .el-tabs__header) {
    background-color: #252525;
    border-bottom-color: var(--border-color);
  }
  
  :deep(.el-tabs--border-card > .el-tabs__header .el-tabs__item.is-active) {
    background-color: var(--card-background);
    border-color: var(--border-color);
    border-bottom-color: var(--card-background);
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
  
  :deep(.el-button--danger.is-plain) {
    color: #f56c6c;
    border-color: #f56c6c; 
    background-color: transparent;
  }
  
  :deep(.el-button--primary.is-plain) {
    color: #409eff;
    border-color: #409eff;
    background-color: transparent;
  }
  
  /* 分页控件深色模式 */
  :deep(.el-pagination) {
    background-color: var(--card-background);
    color: var(--text-color);
  }
  
  :deep(.el-pagination .el-pagination__total) {
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
  
  :deep(.el-empty__description) {
    color: var(--text-color);
  }
  
  :deep(.page-title) {
    color: var(--text-color);
  }
  
  :deep(.el-card__header) {
    border-bottom-color: var(--border-color);
  }
  
  :deep(.card-header-with-action span) {
    color: var(--text-color);
  }
  
  /* 暗黑模式下长文本样式 */
  .long-text {
    background-color: #2a2a2a;
  }
}
</style> 