<template>
  <div class="activity-detail">
    <AppHeader />
    
    <div class="container main-content">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h1 class="page-title">活动详情</h1>
        <router-link to="/" class="btn btn-outline">返回控制台</router-link>
      </div>
      
      <div v-if="loading" class="text-center my-4">
        <p>加载中...</p>
      </div>
      
      <div v-else-if="error" class="alert alert-danger">
        <p>{{ error }}</p>
      </div>
      
      <template v-else>
        <!-- 活动状态卡片 -->
        <div class="status-card card mb-4 card-item card-item-1">
          <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
              <h2 class="activity-title">{{ activity.activity?.title || '未知活动' }}</h2>
            </div>
            <div class="status-badge" :class="getStatusClass(activity.status)">
              {{ getStatusText(activity.status) }}
            </div>
          </div>
          
          <div v-if="activity.message" class="message-info mt-2">
            {{ activity.message }}
          </div>
          
          <div v-if="activity.status === 'waiting'" class="mt-3">
            <button class="btn btn-primary w-100" 
              :class="{'signing-btn': signLoading}"
              @click="triggerSignFlow" 
              :disabled="signLoading">
              <span v-if="signLoading" class="loading-spinner"></span>
              {{ signLoading ? '签到中...' : '签到' }}
            </button>
          </div>
        </div>
        
        <!-- 活动基本信息 -->
        <div class="details-card card mb-4 card-item card-item-2">
          <h3 class="card-title">基本信息</h3>
          
          <div class="detail-section">
            <div class="detail-row">
              <span class="detail-label">活动ID:</span>
              <span class="detail-value">{{ activity.activity_id }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">活动UUID:</span>
              <span class="detail-value">{{ activity.uuid }}</span>
            </div>
            <div class="detail-row" v-if="activity.activity?.course_id">
              <span class="detail-label">课程ID:</span>
              <span class="detail-value">{{ activity.activity.course_id }}</span>
            </div>
            <div class="detail-row" v-if="activity.activity?.class_id">
              <span class="detail-label">班级ID:</span>
              <span class="detail-value">{{ activity.activity.class_id }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">检测时间:</span>
              <span class="detail-value">{{ formatDate(activity.detected_at) }}</span>
            </div>
          </div>
        </div>
        
        <!-- 签到信息 -->
        <div class="details-card card mb-4 card-item card-item-3">
          <h3 class="card-title">签到信息</h3>
          
          <div class="detail-section">
            <div class="detail-row" v-if="activity.activity?.sign_type">
              <span class="detail-label">签到类型:</span>
              <span class="detail-value">{{ activity.activity.sign_type }}</span>
            </div>
            <div class="detail-row" v-if="activity.activity?.start_time">
              <span class="detail-label">开始时间:</span>
              <span class="detail-value">{{ formatDate(activity.activity.start_time) }}</span>
            </div>
            <div class="detail-row" v-if="activity.activity?.end_time">
              <span class="detail-label">结束时间:</span>
              <span class="detail-value">{{ formatDate(activity.activity.end_time) }}</span>
            </div>
          </div>
        </div>
        
        <!-- 参与数据 -->
        <div v-if="hasParticipationData" class="details-card card mb-4 card-item card-item-4">
          <h3 class="card-title">参与数据</h3>
          
          <div class="detail-section">
            <div class="detail-row" v-if="activity.activity?.total_users">
              <span class="detail-label">总人数:</span>
              <span class="detail-value">{{ activity.activity.total_users }}</span>
            </div>
            <div class="detail-row" v-if="activity.activity?.signed_users">
              <span class="detail-label">已签到:</span>
              <span class="detail-value">{{ activity.activity.signed_users }}</span>
            </div>
            <div class="detail-row" v-if="activity.activity?.sign_percent">
              <span class="detail-label">签到率:</span>
              <span class="detail-value">{{ formatPercent(activity.activity.sign_percent) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">数据更新时间:</span>
              <span class="detail-value">{{ formatDate(activity.activity.attend_update_at) }}</span>
            </div>
          </div>
        </div>
        
        <!-- 位置要求 -->
        <div v-if="hasLocationRequirements" class="details-card card mb-4 card-item card-item-5">
          <h3 class="card-title">位置要求</h3>
          
          <div class="detail-section">
            <div class="detail-row">
              <span class="detail-label">需要位置:</span>
              <span class="detail-value">{{ activity.activity.need_location ? '是' : '否' }}</span>
            </div>
            <div class="detail-row" v-if="activity.activity?.location_range">
              <span class="detail-label">位置范围:</span>
              <span class="detail-value">{{ activity.activity.location_range }}米</span>
            </div>
            <div class="detail-row" v-if="activity.activity?.latitude && activity.activity?.longitude">
              <span class="detail-label">经纬度:</span>
              <span class="detail-value">{{ activity.activity.longitude }}, {{ activity.activity.latitude }}</span>
            </div>
            <div class="detail-row" v-if="activity.activity?.address">
              <span class="detail-label">位置地址:</span>
              <span class="detail-value">{{ activity.activity.address }}</span>
            </div>
          </div>
        </div>
        
        <!-- 其他要求 -->
        <div v-if="hasOtherRequirements" class="details-card card mb-4 card-item card-item-6">
          <h3 class="card-title">其他要求</h3>
          
          <div class="detail-section">
            <div class="detail-row" v-if="activity.activity?.need_photo !== undefined">
              <span class="detail-label">需要照片:</span>
              <span class="detail-value">{{ activity.activity.need_photo ? '是' : '否' }}</span>
            </div>
            <div class="detail-row" v-if="activity.activity?.need_code !== undefined">
              <span class="detail-label">需要签到码:</span>
              <span class="detail-value">{{ activity.activity.need_code ? '是' : '否' }}</span>
            </div>
            <div class="detail-row" v-if="activity.activity?.sign_code">
              <span class="detail-label">签到码:</span>
              <span class="detail-value">{{ activity.activity.sign_code }}</span>
            </div>
            <div class="detail-row" v-if="activity.activity?.requires_captcha !== undefined">
              <span class="detail-label">需要验证码:</span>
              <span class="detail-value">{{ activity.activity.requires_captcha ? '是' : '否' }}</span>
            </div>
            <div class="detail-row" v-if="activity.activity?.captcha_type">
              <span class="detail-label">验证码类型:</span>
              <span class="detail-value">{{ activity.activity.captcha_type }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import AppHeader from '../components/AppHeader.vue'
import { activityApi, EventBus } from '../api'

export default {
  name: 'ActivityDetail',
  components: {
    AppHeader
  },
  data() {
    return {
      loading: true,
      error: null,
      activity: {},
      signLoading: false
    }
  },
  computed: {
    hasParticipationData() {
      return this.activity.activity && (
        this.activity.activity.total_users || 
        this.activity.activity.signed_users || 
        this.activity.activity.sign_percent
      )
    },
    hasLocationRequirements() {
      return this.activity.activity && (
        this.activity.activity.need_location !== undefined ||
        this.activity.activity.location_range ||
        this.activity.activity.latitude ||
        this.activity.activity.longitude ||
        this.activity.activity.address
      )
    },
    hasOtherRequirements() {
      return this.activity.activity && (
        this.activity.activity.need_photo !== undefined ||
        this.activity.activity.need_code !== undefined ||
        this.activity.activity.sign_code ||
        this.activity.activity.requires_captcha !== undefined ||
        this.activity.activity.captcha_type
      )
    }
  },
  methods: {
    async fetchActivityDetail() {
      this.loading = true
      this.error = null
      
      try {
        const uuid = this.$route.params.uuid
        
        // 先检查localStorage中是否有缓存的活动数据
        const cachedActivityData = localStorage.getItem('currentActivityData')
        
        if (cachedActivityData) {
          const parsedData = JSON.parse(cachedActivityData)
          
          // 确认UUID匹配
          if (parsedData.uuid === uuid) {
            console.log('使用缓存的活动数据')
            this.activity = parsedData
            // 清除缓存，避免数据过期问题
            localStorage.removeItem('currentActivityData')
            this.loading = false
            return
          }
        }
        
        // 如果没有缓存数据或UUID不匹配，则从网络获取
        console.log('从网络获取活动数据')
        const response = await activityApi.getActivity(uuid)
        this.activity = response.data
      } catch (error) {
        console.error('获取活动详情失败', error)
        this.error = '获取活动详情失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    
    async triggerSignFlow() {
      this.signLoading = true
      this.error = null
      
      try {
        if (!this.activity || !this.activity.uuid) {
          throw new Error('没有找到活动ID');
        }
        
        // 发送签到请求并等待返回
        const response = await activityApi.triggerSignFlow(this.activity.uuid)
        
        // 处理返回的消息
        const responseData = response.data
        
        // 显示成功消息
        EventBus.emit('api-error', {
          type: 'success',
          message: responseData.message || '签到成功',
        })
        
        // 等待短暂时间让用户看到消息
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // 签到请求已完成，现在获取最新数据
        await this.fetchActivityDetail()
        
      } catch (error) {
        console.error('触发签到失败', error)
        this.error = '触发签到失败，请稍后重试'
        
        // 显示错误消息
        EventBus.emit('api-error', {
          type: 'client',
          message: error.response?.data?.message || '签到失败，请稍后重试',
        })
      } finally {
        this.signLoading = false
      }
    },
    
    formatDate(dateValue) {
      if (!dateValue) return '未知'
      
      // 处理数值型时间戳（毫秒级）
      if (typeof dateValue === 'number') {
        const date = new Date(dateValue)
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        })
      }
      
      // 处理ISO字符串
      const date = new Date(dateValue)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    
    formatPercent(value) {
      if (value === undefined || value === null) return '0%'
      // 将小于等于1的小数转换为百分比
      return (value <= 1 ? value * 100 : value).toFixed(1).replace('.0', '') + '%'
    },
    
    getStatusClass(status) {
      switch (status) {
        case 'success': return 'status-success'
        case 'failed': return 'status-danger'
        case 'pending': return 'status-warning'
        case 'processing':
        case 'polling': return 'status-info'
        case 'waiting': return 'status-waiting'
        case 'enc': return 'status-enc'
        default: return ''
      }
    },
    
    getStatusText(status) {
      switch (status) {
        case 'success': return '成功'
        case 'failed': return '失败'
        case 'pending': return '待处理'
        case 'processing': return '处理中'
        case 'polling': return '轮询中'
        case 'waiting': return '待手动确认'
        case 'enc': return '请扫描二维码'
        default: return status
      }
    }
  },
  mounted() {
    this.fetchActivityDetail()
  }
}
</script>

<style scoped>
.main-content {
  padding-top: var(--spacing-4);
  padding-bottom: var(--spacing-5);
}

.page-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
}

.card {
  margin-bottom: var(--spacing-4);
  opacity: 0; /* 初始不可见 */
}

@keyframes slideUp {
  0% {
    opacity: 0;
    transform: translateY(25px);
  }
  50% {
    opacity: 0.8;
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 卡片动画级联效果 */
.card-item {
  animation-name: slideUp;
  animation-duration: 0.6s;
  animation-fill-mode: both;
  animation-timing-function: cubic-bezier(0.34, 1.56, 0.64, 1);
}

.card-item-1 {
  animation-delay: 0.1s;
}

.card-item-2 {
  animation-delay: 0.2s;
}

.card-item-3 {
  animation-delay: 0.3s;
}

.card-item-4 {
  animation-delay: 0.4s;
}

.card-item-5 {
  animation-delay: 0.5s;
}

.card-item-6 {
  animation-delay: 0.6s;
}

.card-title {
  font-size: 1.25rem;
  margin-bottom: var(--spacing-3);
  padding-bottom: var(--spacing-2);
  border-bottom: 1px solid var(--color-border);
}

.activity-title {
  font-size: 1.5rem;
  margin: 0;
  display: flex;
  align-items: center;
}

.activity-id {
  margin: 0;
  font-size: var(--font-size-sm);
}

.detail-section {
  display: grid;
  gap: var(--spacing-3);
}

.detail-row {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-3);
}

.detail-label {
  font-weight: 500;
  color: var(--color-text-muted);
  flex-basis: 120px;
  flex-shrink: 0;
}

.detail-value {
  word-break: break-all;
}

.status-badge {
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--border-radius);
  font-size: var(--font-size-sm);
  font-weight: 500;
  min-width: 100px;
  text-align: center;
}

.status-success {
  background-color: rgba(var(--color-success-rgb), 0.1);
  color: var(--color-success);
}

.status-danger {
  background-color: rgba(var(--color-danger-rgb), 0.1);
  color: var(--color-danger);
}

.status-warning {
  background-color: rgba(var(--color-warning-rgb), 0.1);
  color: var(--color-warning);
}

.status-info {
  background-color: rgba(var(--color-info-rgb), 0.1);
  color: var(--color-info);
}

.status-waiting {
  background-color: rgba(var(--color-secondary-rgb), 0.1);
  color: var(--color-secondary);
}

.status-enc {
  background-color: rgba(var(--color-danger-rgb), 0.1);
  color: var(--color-danger);
}

/* 响应式布局 */
@media (min-width: 768px) {
  .detail-section {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .detail-row {
    margin-right: var(--spacing-3);
  }
}

@media (max-width: 767px) {
  .detail-row {
    flex-direction: column;
    gap: var(--spacing-1);
  }
  
  .detail-label {
    flex-basis: auto;
  }
}

.loading-spinner {
  display: inline-block;
  width: 1em;
  height: 1em;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;
}

/* 签到按钮样式 */
.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  position: relative;
  overflow: hidden;
}

.signing-btn {
  background-color: var(--color-primary-dark) !important;
  box-shadow: 0 0 0 rgba(var(--color-primary-rgb), 0.4);
  transition: all 0.3s ease;
}

.btn-primary:disabled::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: loading-shine 1.5s infinite;
}

@keyframes loading-shine {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style> 