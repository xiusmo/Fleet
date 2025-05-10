<template>
  <div class="dashboard">
    <AppHeader />
    
    <div class="container main-content">
      <h1 class="page-title">仪表盘</h1>
      
      <div class="monitor-control card mb-4">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h3>监控状态</h3>
            <p class="text-muted">{{ monitorStatus ? '已开启监控' : '未开启监控' }}</p>
          </div>
          <button 
            class="btn" 
            :class="monitorStatus ? 'btn-danger' : 'btn-primary'"
            @click="toggleMonitor"
            :disabled="isToggling || monitorStatusLoading"
          >
            <span v-if="isToggling || monitorStatusLoading" class="loading-spinner"></span>
            {{ monitorStatus ? '关闭监控' : '开启监控' }}
          </button>
        </div>
      </div>
      
      <div class="activities-section">
        <div class="section-header d-flex justify-content-between align-items-center">
          <h2>最近活动</h2>
        </div>
        
        <!-- 活动骨架屏 -->
        <div v-if="loading" class="activities-container" :class="{'fade-out': fadeOutSkeleton}">
          <div class="activity-list skeleton-list">
            <div v-for="n in 2" :key="`skeleton-${n}`" class="skeleton-wrapper">
              <div class="activity-item card skeleton-card">
                <div class="activity-header">
                  <div class="activity-title-row">
                    <div class="skeleton-text skeleton-title"></div>
                    <div class="skeleton-badge"></div>
                  </div>
                  <div class="activity-time">
                    <div class="skeleton-text skeleton-time"></div>
                  </div>
                  <div class="course-name">
                    <div class="skeleton-text skeleton-course"></div>
                  </div>
                </div>
                <div class="activity-actions">
                  <div class="skeleton-text skeleton-link"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else-if="activeActivities.length === 0" class="empty-state card">
          <p>当前没有待处理的签到活动</p>
          <small class="text-muted">开启监控后，系统将自动检测新的签到活动</small>
        </div>
        
        <div v-else class="activities-container" :class="{'active-container': dataReady}">
          <div class="activity-list" :class="{ 
            'expanded': isActivityListExpanded,
            'few-items': activeActivities.length <= 2,
            'has-data': activeActivities.length > 0 && !loading
          }">
            <div v-for="activity in activeActivities" :key="`activity-${activity.uuid}`" 
              class="real-data-wrapper"
              :class="{'active': dataReady || transitioningData}"
            >
              <div class="activity-item card">
                <div class="activity-header">
                  
                  <div class="activity-title-row">
                    <h3>{{ activity && activity.activity ? (activity.activity.title || '未知活动') : '未知活动' }}</h3>
                    <span class="activity-status" :class="getStatusClass(activity.status)">
                      {{ getStatusText(activity.status) }}
                    </span>
                  </div>

                  <div class="activity-time" v-if="activity && activity.activity">
                    {{ formatTimeOnly(activity.activity.start_time) }} - {{ formatTimeOnly(activity.activity.end_time) }}
                    <span class="activity-date">{{ formatDateOnly(activity.activity.start_time) }}</span>
                  </div>

                  <div v-if="activity && activity.course_name" class="course-name">
                    {{ activity.course_name }} {{ activity && activity.activity ? '  ' + activity.activity.teacher_name : '' }}
                  </div>

                </div>
                
                <div class="activity-details">
                  <div class="activity-row" v-if="activity && activity.activity && activity.activity.sign_type">
                    <span>{{ activity.activity.sign_type }}</span>
                  </div>
                </div>
                
                <div class="activity-actions">
                  <small v-if="activity.status === 'waiting'" class="text-muted confirm-hint">进入详情页面进行手动确认</small>
                  <a href="javascript:void(0)" class="details-link" @click="viewActivityDetail(activity)">
                    详细信息 <span class="details-arrow">→</span>
                  </a>
                </div>
                
              </div>
            </div>
          </div>
          
          <div v-if="activeActivities.length > 2" class="expand-btn-container">
            <div class="blur-overlay"></div>
            <button class="btn btn-outline expand-btn" @click="toggleActivityList">
              {{ isActivityListExpanded ? '收起' : '查看更多' }}
              <span class="expand-icon" :class="{ 'rotated': isActivityListExpanded }">▼</span>
            </button>
          </div>
        </div>
      </div>
      
      <div class="config-section">
        <div class="section-header d-flex justify-content-between align-items-center">
          <h2>签到配置</h2>
          <router-link to="/sign-configs" class="btn btn-outline">管理配置</router-link>
        </div>
        
        <!-- 配置骨架屏 -->
        <div v-if="loadingConfigs" class="config-skeleton" :class="{'fade-out': fadeOutSkeleton}">
          <div class="config-list">
            <div v-for="n in 2" :key="`config-skeleton-${n}`" class="config-card-wrapper">
              <div class="config-card card skeleton-card">
                <div class="config-header d-flex justify-content-between align-items-center">
                  <div class="skeleton-text skeleton-config-title"></div>
                  <div class="skeleton-badge"></div>
                </div>
                <div class="config-details">
                  <div class="config-row">
                    <div class="skeleton-text skeleton-label"></div>
                    <div class="skeleton-text skeleton-value"></div>
                  </div>
                </div>
                <div class="config-actions">
                  <div class="skeleton-btn"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else-if="configs.length === 0" class="empty-state card">
          <p>将默认为手动签到</p>
        </div>
        
        <div v-else class="config-list">
          <div v-for="config in configs" :key="config.uuid" class="config-card-wrapper">
            <div class="config-card card">
              <div class="config-header d-flex justify-content-between align-items-center">
                <h3 class="config-title">{{ config.name }}</h3>
                <span v-if="config.is_default" class="default-badge">默认</span>
              </div>
              <div class="config-details">
                <div v-if="config.class_id" class="config-row">
                  <span class="config-label">班级ID:</span>
                  <span class="config-value">{{ config.class_id }}</span>
                </div>
              </div>
              <div class="config-actions">
                <router-link :to="`/sign-configs?action=edit&id=${config.uuid}`" class="btn btn-outline">
                  编辑配置
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 请假条编辑器入口 -->
      <div class="leave-note-section">
        <div class="section-header d-flex justify-content-between align-items-center">
          <h2>白名单升级中...</h2>
          <!-- <router-link to="/leave-note-editor" class="btn btn-outline">编辑请假条</router-link> -->
        </div>
        <div class="card">
          <div class="leave-note-info">
            <!-- <p>使用这个工具，您可以创建自定义的请假条</p>
            <p>填写表单后，系统将生成一个与官方请假条完全相同的展示页面。</p>
            <p>你的信息将完全存储在本地。站长自用工具 恕不维护</p> -->
            <p>为了此功能提供更稳定和更安全的工具，我们暂时关闭了这个功能。感谢你的支持。</p>
            <p>敬请期待...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AppHeader from '../components/AppHeader.vue'
import { userApi, activityApi, configApi, EventBus } from '../api'

export default {
  name: 'DashboardPage',
  components: {
    AppHeader
  },
  data() {
    return {
      monitorStatus: false,
      isToggling: false,
      loading: false,
      loadingConfigs: true,
      activeActivities: [],
      configs: [],
      isActivityListExpanded: false,
      activitiesLoading: false,
      initialLoading: true,
      transitioningData: false,
      fadeOutSkeleton: false,
      dataReady: false,
      monitorStatusLoading: false
    }
  },
  methods: {
    async fetchData() {
      this.loading = true
      
      try {
        const activitiesResponse = await activityApi.getActiveActivities()
        
        this.activeActivities = activitiesResponse && activitiesResponse.data ? activitiesResponse.data : []
      } catch (error) {
        console.error('获取数据失败', error)
        this.activeActivities = []
      } finally {
        this.loading = false
      }
    },
    
    async fetchConfigs() {
      this.loadingConfigs = true
      try {
        const response = await configApi.getSignConfigs()
        this.configs = response && response.data ? response.data : []
      } catch (error) {
        console.error('获取配置失败', error)
        this.configs = []
      } finally {
        this.loadingConfigs = false
      }
    },
    
    async fetchMonitorStatus() {
      // 方法内部不再设置loading状态，由外部控制
      try {
        const response = await userApi.getMonitorStatus()
        this.monitorStatus = response.data || false
      } catch (error) {
        console.error('获取监控状态失败', error)
        this.monitorStatus = false
      }
    },
    
    async toggleMonitor() {
      this.isToggling = true;
      try {
        await userApi.manageWsConnection(!this.monitorStatus);
        this.monitorStatus = !this.monitorStatus;
      } catch (error) {
        console.error('切换监控状态失败', error);
      } finally {
        // 延迟关闭loading状态，让按钮动画更平滑
        setTimeout(() => {
          this.isToggling = false;
        }, 300);
      }
    },
    
    async triggerSignFlow(detectionUuid) {
      try {
        await activityApi.triggerSignFlow(detectionUuid)
        // 重新获取活动列表
        this.fetchData()
      } catch (error) {
        console.error('触发签到失败', error)
      }
    },
    
    formatDate(dateValue) {
      if (!dateValue) return '未知'
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
    },
    
    toggleActivityList() {
      setTimeout(() => {
        this.isActivityListExpanded = !this.isActivityListExpanded
      }, 350);
    },
    
    formatTimeOnly(dateValue) {
      if (!dateValue) return '';
      const date = new Date(dateValue);
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    formatDateOnly(dateValue) {
      if (!dateValue) return '';
      const date = new Date(dateValue);
      return date.toLocaleDateString('zh-CN', {
        month: '2-digit',
        day: '2-digit'
      });
    },

    viewActivityDetail(activity) {
      // 将活动数据存储到LocalStorage中
      localStorage.setItem('currentActivityData', JSON.stringify(activity));
      // 导航到详情页面
      this.$router.push(`/activities/${activity.uuid}`);
    }
  },
  created() {
    window.addEventListener('resize', this.resizeHandler);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.resizeHandler);
  },
  async mounted() {
    // 并行请求，但确保loading状态正确
    this.loading = true;
    this.loadingConfigs = true;
    this.monitorStatusLoading = true;
    
    try {
      // 先请求监控状态，因为这个不影响界面loading状态
      const monitorPromise = this.fetchMonitorStatus();
      
      // 然后请求活动和配置，但不等待其完成
      const activitiesPromise = activityApi.getActiveActivities();
      const configsPromise = configApi.getSignConfigs();
      
      // 等待监控状态完成
      await monitorPromise;
      this.monitorStatusLoading = false;
      
      // 处理配置数据
      const configsResponse = await configsPromise;
      this.configs = configsResponse && configsResponse.data ? configsResponse.data : [];
      
      // 处理活动数据
      const activitiesResponse = await activitiesPromise;
      this.activeActivities = activitiesResponse && activitiesResponse.data ? activitiesResponse.data : [];
      
      // 平滑过渡: 先设置数据准备好标志
      this.dataReady = true;
      
      // 先淡出骨架屏
      this.fadeOutSkeleton = true;
      
      // 延迟隐藏骨架屏，让淡出动画有时间播放
      setTimeout(() => {
        this.loadingConfigs = false;
        this.loading = false;
        
        // 延迟给真实数据添加active类，产生淡入效果
        setTimeout(() => {
          this.transitioningData = true;
          
          // 给时间让CSS过渡动画完成
          setTimeout(() => {
            this.transitioningData = false;
          }, 800);
        }, 50);
      }, 300);
      
    } catch (error) {
      console.error('获取数据失败', error);
      this.activeActivities = [];
      this.configs = [];
      this.fadeOutSkeleton = true;
      this.monitorStatusLoading = false;
      
      setTimeout(() => {
        this.loading = false;
        this.loadingConfigs = false;
      }, 300);
    }
  }
}
</script>

<style scoped>
.main-content {
  padding-top: var(--spacing-4);
  padding-bottom: var(--spacing-5);
}

.page-title {
  margin-bottom: var(--spacing-4);
  font-size: 1.75rem;
  font-weight: 600;
}

.stats-row {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-4);
  width: 100%;
}

.stat-card {
  flex: 1;
  min-width: 0; /* 防止溢出 */
  padding: var(--spacing-2) var(--spacing-1);
  height: 100%;
  display: flex;
  align-items: center;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
}

.stat-icon {
  font-size: 1.2rem;
  margin-right: var(--spacing-1);
  width: 24px;
  height: 24px;
  min-width: 24px; /* 防止缩小 */
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: rgba(var(--color-primary-rgb), 0.1);
}

.stat-icon.success {
  background-color: rgba(var(--color-success-rgb), 0.1);
  color: var(--color-success);
}

.stat-icon.danger {
  background-color: rgba(var(--color-danger-rgb), 0.1);
  color: var(--color-danger);
}

.stat-icon.warning {
  background-color: rgba(var(--color-warning-rgb), 0.1);
  color: var(--color-warning);
}

.stat-content {
  text-align: left;
  overflow: hidden; /* 防止溢出 */
  white-space: nowrap; /* 确保在一行 */
  text-overflow: ellipsis; /* 过长显示省略号 */
  min-width: 0; /* 允许flexbox压缩 */
}

.stat-value {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.2;
  color: var(--color-primary);
}

.stat-content p {
  font-size: 0.75rem;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.section-header {
  margin-bottom: var(--spacing-3);
}

.activities-section, .config-section {
  margin-bottom: var(--spacing-4);
}

.activities-container {
  position: relative;
  min-height: auto;
  width: 100%;
  max-width: 100%;
  overflow: hidden;
}

.activity-list {
  display: grid;
  gap: var(--spacing-3);
  max-height: 400px;
  overflow-y: hidden;
  transition: max-height 0.8s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease-out;
  grid-template-columns: repeat(1, 1fr);
  position: relative;
  margin: 0 auto;
  max-width: 500px;
  width: 100%;
}

.activity-list.has-data {
  grid-template-columns: repeat(1, 1fr);
}

.activity-list.few-items {
  max-height: none;
  overflow-y: visible;
}

.activity-list.expanded {
  max-height: 10000px;
}

@media (min-width: 768px) {
  .activity-list,
  .activity-list.has-data {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    max-width: none;
  }
  
  .activity-list.few-items {
    gap: var(--spacing-4);
  }
}

@media (min-width: 992px) {
  .activity-list.few-items {
    max-width: 900px;
    margin: 0 auto;
  }
}

.activity-item {
  padding: var(--spacing-2) var(--spacing-3);
  height: 100%;
  display: flex;
  flex-direction: column;
  width: 100%;
  min-width: 0;
  overflow: hidden;
}

.activity-header {
  margin-bottom: var(--spacing-1);
  width: 100%;
  min-width: 0;
  overflow: hidden;
}

.activity-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-1);
  width: 100%;
  min-width: 0;
}

.activity-title-row h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 70%;
  flex-shrink: 1;
}

.activity-status {
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--border-radius);
  font-size: 0.8rem;
  font-weight: 500;
  line-height: 1;
  flex-shrink: 0;
  white-space: nowrap;
}

.activity-time {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-1);
  width: 100%;
  overflow: hidden;
}

.activity-date {
  font-size: 0.85rem;
  opacity: 0.8;
  flex-shrink: 0;
  margin-left: var(--spacing-1);
}

.activity-details {
  margin-bottom: var(--spacing-1);
  font-size: 0.85rem;
}

.activity-row {
  margin-bottom: var(--spacing-1);
  display: flex;
  align-items: center;
}

.activity-id {
  font-size: 0.8rem;
  opacity: 0.7;
}

.id-value {
  font-family: monospace;
}

.label {
  font-weight: 500;
  width: 42px;
  color: var(--color-text-muted);
}

.activity-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: auto;
}

.confirm-hint {
  font-size: 0.8rem;
  color: var(--color-secondary);
  margin-right: auto;
}

.details-link {
  font-size: 0.85rem;
  margin-left: auto;
}

.details-arrow {
  margin-left: var(--spacing-1);
  transition: transform 0.2s ease;
}

.details-link:hover .details-arrow {
  transform: translateX(3px);
}

.manual-sign-btn {
  display: block;
  width: 100%;
  padding: var(--spacing-2);
  margin-top: var(--spacing-2);
}

.default-badge {
  background-color: var(--color-primary);
  color: white;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 10px;
  margin-left: var(--spacing-1);
}

.config-section {
  margin-bottom: var(--spacing-4);
  padding: var(--spacing-2) 0;
}

.config-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-3);
  margin-top: var(--spacing-3);
  width: 100%;
}

.config-card-wrapper {
  height: 100%;
}

.config-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: var(--spacing-3);
  border-radius: var(--border-radius);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.config-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.config-header {
  margin-bottom: var(--spacing-2);
  padding-bottom: var(--spacing-1);
  border-bottom: 1px solid rgba(var(--color-border-rgb), 0.5);
}

.config-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.config-details {
  flex-grow: 1;
  margin-bottom: var(--spacing-2);
}

.config-row {
  display: flex;
  margin-bottom: var(--spacing-1);
  font-size: 0.85rem;
}

.config-label {
  font-weight: 500;
  width: 70px;
  color: var(--color-text-muted);
}

.config-value {
  font-family: monospace;
}

.config-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: auto;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-4);
  color: var(--color-text-muted);
}

.monitor-control {
  padding: var(--spacing-3);
  margin-bottom: var(--spacing-4);
}

/* 真实数据样式 */
.real-data-wrapper {
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.5s ease-out, transform 0.5s ease-out;
  will-change: opacity, transform;
  width: 100%;
  min-width: 0;
}

.real-data-wrapper.active {
  opacity: 1;
  transform: translateY(0);
}

/* 让真实数据一个接一个出现 */
.real-data-wrapper:nth-child(1) {
  transition-delay: 0.1s;
}

.real-data-wrapper:nth-child(2) {
  transition-delay: 0.2s;
}

.real-data-wrapper:nth-child(3) {
  transition-delay: 0.3s;
}

.real-data-wrapper:nth-child(4) {
  transition-delay: 0.4s;
}

/* 展开按钮区域 */
.expand-btn-container {
  text-align: center;
  margin-top: var(--spacing-3);
  padding-top: var(--spacing-2);
  position: relative;
  z-index: 5;
}

.expand-btn-container:before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(to bottom, 
    rgba(var(--color-background-rgb), 0), 
    rgba(var(--color-background-rgb), 0.7) 50%, 
    rgba(var(--color-background-rgb), 0.95));
  pointer-events: none;
  z-index: 1;
}

.expand-btn-container .blur-overlay {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  height: 80px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  pointer-events: none;
  z-index: 2;
  mask-image: linear-gradient(to bottom, 
    rgba(0, 0, 0, 0.1) 0%,
    rgba(0, 0, 0, 0.4) 30%, 
    rgba(0, 0, 0, 0.7) 60%,
    rgba(0, 0, 0, 1) 100%);
  -webkit-mask-image: linear-gradient(to bottom, 
    rgba(0, 0, 0, 0.1) 0%,
    rgba(0, 0, 0, 0.4) 30%, 
    rgba(0, 0, 0, 0.7) 60%,
    rgba(0, 0, 0, 1) 100%);
}

.expand-btn {
  padding: var(--spacing-2) var(--spacing-4);
  position: relative;
  background: rgba(var(--color-background-rgb), 0.4);
  border: 1px solid rgba(var(--color-text-rgb), 0.1);
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  min-width: 160px;
  font-size: 0.9rem;
  opacity: 0.8;
  color: var(--color-text-muted);
}

.expand-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
  opacity: 1;
  background: rgba(var(--color-background-rgb), 0.6);
}

.expand-icon {
  display: inline-block;
  margin-left: var(--spacing-1);
  transition: transform 0.3s ease;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

/* 响应式调整 */
@media (min-width: 768px) {
  .config-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: var(--spacing-3);
  }
}

/* 移动设备统计卡片布局 */
@media (max-width: 767px) {
  .stats-row {
    gap: var(--spacing-1);
  }
  
  .stat-card {
    padding: var(--spacing-1);
  }
  
  .stat-icon {
    font-size: 1rem;
    width: 20px;
    height: 20px;
    min-width: 20px;
    margin-right: var(--spacing-1);
  }
  
  .stat-value {
    font-size: 0.9rem;
  }
  
  .stat-content p {
    font-size: 0.6rem;
  }
  
  .activity-list {
    max-height: 350px;
  }
  
  .activity-list.few-items .real-data-wrapper {
    margin-bottom: var(--spacing-3);
  }
}

/* 超小屏幕调整 */
@media (max-width: 479px) {
  .stat-card {
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: var(--spacing-1) var(--spacing-1);
  }
  
  .stat-icon {
    margin-right: 0;
    margin-bottom: var(--spacing-1);
  }
  
  .stat-content {
    text-align: center;
  }
}

.activity-header, .config-header {
  margin-bottom: var(--spacing-1);
}

.activity-details, .config-details {
  margin-bottom: var(--spacing-1);
  font-size: 0.85rem;
}

.activity-row, .config-row {
  margin-bottom: var(--spacing-1);
  display: flex;
  align-items: center;
}

.config-actions {
  display: flex;
  gap: var(--spacing-2);
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

.details-link {
  color: var(--color-primary);
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
}

.course-name {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  width: 100%;
  min-width: 0;
  flex-shrink: 1;
}

.text-center {
  text-align: center;
}

.mt-2 {
  margin-top: var(--spacing-2);
}

.text-muted {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

/* 骨架屏样式 */
.skeleton-list, .config-skeleton {
  width: 100%;
  transition: opacity 0.5s ease-out;
}

.skeleton-wrapper, .config-card-wrapper {
  margin-bottom: 16px;
  transition: all 0.3s ease-out;
  width: 100%;
  min-width: 0;
}

.skeleton-card {
  background-color: var(--color-card-bg);
  padding: 16px;
  animation: pulse 1.5s infinite ease-in-out;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(var(--color-shadow-rgb), 0.05);
}

.skeleton-text {
  background-color: var(--color-border);
  height: 16px;
  border-radius: 4px;
  margin-bottom: 8px;
}

.skeleton-title {
  width: 60%;
  height: 20px;
}

.skeleton-config-title {
  width: 40%;
  height: 20px;
}

.skeleton-badge {
  width: 60px;
  height: 24px;
  background-color: var(--color-border);
  border-radius: 12px;
}

.skeleton-time {
  width: 30%;
  height: 14px;
}

.skeleton-course {
  width: 45%;
  height: 14px;
}

.skeleton-link {
  width: 25%;
  height: 16px;
  margin-left: auto;
}

.skeleton-label {
  width: 30%;
  height: 14px;
}

.skeleton-value {
  width: 60%;
  height: 14px;
}

.skeleton-btn {
  width: 80px;
  height: 36px;
  background-color: var(--color-border);
  border-radius: 4px;
  margin-top: 12px;
}

@keyframes pulse {
  0% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.6;
  }
}

/* 数据加载过渡效果 */
.activities-container, .config-list {
  position: relative;
  transition: opacity 0.4s ease-out;
}

.fade-out {
  opacity: 0;
  transition: opacity 0.3s ease-out;
}

.active-container {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from { 
    opacity: 0;
  }
  to { 
    opacity: 1; 
  }
}

/* 加载动画 */
.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;
  vertical-align: middle;
  position: relative;
  top: -1px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

/* 请假条工具部分 */
.leave-note-section {
  margin-top: 30px;
  margin-bottom: 30px;
}

.leave-note-info {
  padding: 7px;
}

.leave-note-info p {
  margin-bottom: 10px;
  color: var(--color-text-muted);
  font-size: 14px;
}
</style> 