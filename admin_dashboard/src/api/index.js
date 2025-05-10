import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    console.log('API响应成功:', response.config.url, response.data)
    return response
  },
  error => {
    // 处理401错误（未授权）
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    console.error('API响应错误:', error.config?.url, error.response?.status, error.message)
    return Promise.reject(error)
  }
)

// API服务
export default {
  // 用户管理
  users: {
    getAll(params = {}) {
      return apiClient.get('/admin/users', { params })
    },
    getOne(id) {
      return apiClient.get(`/admin/users/${id}`)
    },
    delete(id) {
      return apiClient.delete(`/admin/users/${id}`)
    }
  },
  
  // 工作节点管理
  workers: {
    getAll(params = {}) {
      return apiClient.get('/workers', { params })
    },
    getOne(id) {
      return apiClient.get(`/workers/${id}`)
    },
    create(data) {
      return apiClient.post('/workers', data)
    },
    update(id, data) {
      return apiClient.put(`/workers/${id}`, data)
    },
    delete(id) {
      return apiClient.delete(`/workers/${id}`)
    }
  },
  
  // 日志管理
  logs: {
    getAll(params = {}) {
      return apiClient.get('/logs', { params })
    },
    delete(id) {
      return apiClient.delete(`/logs/${id}`)
    },
    clear(filters) {
      return apiClient.delete('/logs', { data: filters })
    }
  },
  
  // 公告管理
  announcements: {
    getAll(params = {}) {
      return apiClient.get('/announcement/', { params })
    },
    getActive() {
      return apiClient.get('/announcement/active-list')
    },
    getByUuid(uuid) {
      return apiClient.get('/announcement/', { params: { uuid } })
    },
    create(data) {
      return apiClient.post('/announcement/', data)
    },
    update(uuid, data) {
      return apiClient.put(`/announcement/${uuid}`, data)
    },
    delete(uuid) {
      return apiClient.delete(`/announcement/${uuid}`)
    }
  },
  
  // 系统管理
  system: {
    getStatus() {
      return apiClient.get('/admin/system/status')
    },
    getProcesses(params = {}) {
      return apiClient.get('/admin/system/processes', { params })
    },
    getDatabaseHealth() {
      return apiClient.get('/admin/database/health')
    }
  },
  
  // 认证
  auth: {
    login(credentials) {
      return apiClient.post('/auth/cx_login', credentials)
    },
    getMe() {
      return apiClient.get('/auth/me')
    }
  }
} 