import axios from 'axios'

// 创建获取 access token 的函数
export const getAccessToken = () => {
  return localStorage.getItem('token')
}

// 清除所有token信息
export const clearTokens = () => {
  localStorage.removeItem('token')
}

// 保存token信息
export const saveTokens = (data) => {
  const { access_token } = data
  localStorage.setItem('token', access_token)
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  async config => {
    console.log(`发送请求: ${config.method.toUpperCase()} ${config.url}`, config)
    
    const token = getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    } else {
      console.log('未找到token')
    }
    return config
  },
  error => {
    console.error('请求拦截器出错:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log(`响应成功: ${response.config.method.toUpperCase()} ${response.config.url}`, response.status)
    return response
  },
  async error => {
    const statusCode = error.response?.status;
    const url = error.config?.url;
    console.log('响应错误:', statusCode, url)
    
    // 构造错误消息
    const errorMsg = error.response?.data?.detail || error.message;
    const errorInfo = {
      status: statusCode,
      url: url,
      message: errorMsg
    };
    
    // 通过EventBus发送错误信息
    EventBus.emit('api-error', errorInfo);
    
    if (error.response && error.response.status === 401) {
      console.log('收到401错误，需要重新登录')
      clearTokens()
      window.location.href = '/login'
      return Promise.reject(error)
    }
    
    if (error.response) {
      switch (error.response.status) {
        case 403:
          // 权限不足
          console.error('权限不足')
          break
        case 404:
          // 资源不存在
          console.error('请求的资源不存在')
          break
        case 500:
          // 服务器错误
          console.error('服务器错误')
          break
        default:
          console.error('请求失败:', error.response.data)
      }
    }
    return Promise.reject(error)
  }
)

export const apiService = {
  // 用户认证相关
  login: (username, password) => api.post('/auth/cx_login', { username, password }),
  logout: () => api.post('/auth/logout'),
  
  // 用户信息相关
  getCurrentUser: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/users/me', data),
  updatePassword: (data) => api.put('/users/me', data),
  getMonitorStatus: () => api.get('/monitor/status'),
  manageWsConnection: (status) => api.get(`/monitor/${status}`),
  
  // 公告相关
  getActiveAnnouncements: () => api.get('/announcement/active-list'),
  
  // 签到配置相关
  getSignConfigs: () => api.get('/sign-configs/'),
  createSignConfig: (data) => api.post('/sign-configs/', data),
  updateSignConfig: (configId, data) => api.put(`/sign-configs/${configId}`, data),
  deleteSignConfig: (configId) => api.delete(`/sign-configs/${configId}`),
  setDefaultSignConfig: (configId) => api.put(`/sign-configs/${configId}`, { is_default: true }),
  
  // 签到活动相关
  getActiveActivities: (params) => api.get('/activity/active-activities', { params }),
  getActivity: (activityId) => api.get(`/activity/${activityId}`),
  getUserActivity: (uuid) => api.get(`/activity/${uuid}`),
  triggerSignFlow: (detectionUuid) => api.post(`/activity/${detectionUuid}`),
  
  // 签到记录相关
  // getSignRecords: (params) => api.get('/sign-records', { params }),
  // getSignStats: () => api.get('/sign-stats'),
  signIn: (detectionUuid) => api.post(`/activity/${detectionUuid}`),
  signOut: (detectionUuid) => api.post(`/activity/${detectionUuid}`),
  
  // 二维码相关
  submitQrCodeSign: (data) => api.post('/activity/qr-code', data)
}

// 添加缺失的API服务导出

// 认证相关API
export const authApi = {
  login: apiService.login,
  logout: apiService.logout
}

// 用户相关API
export const userApi = {
  login: (username, password, turnstileToken) => api.post('/auth/cx_login', { username, password, turnstileToken }),
  logout: apiService.logout,
  getCurrentUser: apiService.getCurrentUser,
  updateProfile: apiService.updateProfile,
  updatePassword: apiService.updatePassword,
  getMonitorStatus: apiService.getMonitorStatus,
  manageWsConnection: apiService.manageWsConnection
}

// 配置相关API
export const configApi = {
  getSignConfigs: () => api.get('/sign-configs/'),
  getSignConfig: (uuid) => api.get(`/sign-configs/${uuid}`),
  createSignConfig: (data) => api.post('/sign-configs/', data),
  updateSignConfig: (configId, data) => api.put(`/sign-configs/${configId}`, data),
  deleteSignConfig: (configId) => api.delete(`/sign-configs/${configId}`),
  setDefaultSignConfig: (configId) => api.put(`/sign-configs/${configId}`, { is_default: true })
}

// 活动相关API
export const activityApi = {
  getActiveActivities: (params) => api.get('/activity/active-activities', { params }),
  getActivity: (uuid) => api.get(`/activity/${uuid}`),
  getUserActivities: (params) => api.get('/activity/', { params }),
  getActivityStats: (days) => api.get('/activity/summary', { params: { days } }),
  triggerSignFlow: (detectionUuid) => api.post(`/activity/${detectionUuid}`),
  signIn: (detectionUuid) => api.post(`/activity/${detectionUuid}`)
}

// 二维码相关API
export const qrCodeApi = {
  parseQrCodeUrl: (url) => {
    try {
      // 尝试解析URL
      const urlObj = new URL(url);
      const params = new URLSearchParams(urlObj.search);
      
      let activity_id = params.get('id'); 
      if (!activity_id) {
        activity_id = params.get('activeId');
      }
      const enc = params.get('enc');
      
      return {
        valid: !!(activity_id && enc),
        data: {
          activity_id,
          enc
        }
      };
    } catch (error) {
      console.error('解析二维码URL失败:', error);
      return {
        valid: false,
        data: null
      };
    }
  },
  submitQrCodeSign: (data) => apiService.submitQrCodeSign(data)
}

// 事件总线
export const EventBus = {
  _events: {},
  on(event, callback) {
    if (!this._events[event]) this._events[event] = [];
    this._events[event].push(callback);
  },
  off(event, callback) {
    if (!this._events[event]) return;
    if (!callback) {
      delete this._events[event];
      return;
    }
    this._events[event] = this._events[event].filter(cb => cb !== callback);
  },
  emit(event, ...args) {
    if (!this._events[event]) return;
    this._events[event].forEach(callback => callback(...args));
  }
} 