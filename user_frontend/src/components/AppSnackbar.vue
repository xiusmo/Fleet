<template>
  <transition name="snackbar">
    <div v-if="visible" class="snackbar" :class="errorTypeClass">
      <div class="snackbar-content">
        <div class="snackbar-icon">{{ errorIcon }}</div>
        <div class="snackbar-message">{{ errorMessage }}</div>
        <button v-if="errorAction" class="snackbar-action" @click="handleAction">
          {{ errorAction.label }}
        </button>
        <button class="snackbar-close" @click="hideError">×</button>
      </div>
      <div class="snackbar-progress">
        <div class="snackbar-progress-inner" :style="progressStyle"></div>
      </div>
    </div>
  </transition>
</template>

<script>
import { EventBus } from '../api'

export default {
  name: 'AppSnackbar',
  data() {
    return {
      visible: false,
      errorType: '',
      errorMessage: '',
      errorAction: null,
      timeout: null,
      progressInterval: null,
      progress: 0,
      duration: 5000
    }
  },
  computed: {
    errorIcon() {
      switch (this.errorType) {
        case 'network': return '📶'
        case 'server': return '🛠️'
        case 'client': return '⚠️'
        case 'request': return '❗'
        case 'auth': return '🔒'
        case 'notfound': return '🔍'
        case 'forbidden': return '🚫'
        case 'ratelimit': return '⏱️'
        case 'success': return '✅'
        case 'info': return 'ℹ️'
        default: return 'ℹ️'
      }
    },
    errorTypeClass() {
      return `error-type-${this.errorType}`
    },
    progressStyle() {
      return {
        width: `${this.progress}%`
      }
    }
  },
  methods: {
    showError(errorData) {
      // 清除之前的超时和进度
      this.clearTimers()
      
      // 设置错误信息
      this.errorType = errorData.type || 'default'
      this.errorMessage = errorData.message || '发生未知错误'
      this.errorAction = errorData.action || null
      this.visible = true
      this.progress = 0
      
      // 根据错误类型设置持续时间
      // 如果有操作按钮，延长显示时间
      if (this.errorAction) {
        this.duration = 8000; // 8秒
      } else if (this.errorType === 'success') {
        this.duration = 3000; // 成功消息3秒
      } else {
        this.duration = 5000; // 默认5秒
      }
      
      // 启动进度条动画
      this.startProgressBar()
      
      // 设置自动关闭
      this.timeout = setTimeout(() => {
        this.hideError()
      }, this.duration)
    },
    
    // 简便方法，用于显示消息
    show(message, type = 'info') {
      this.showError({
        type: type,
        message: message
      });
    },
    
    hideError() {
      this.visible = false
      this.clearTimers()
    },
    
    clearTimers() {
      if (this.timeout) {
        clearTimeout(this.timeout)
        this.timeout = null
      }
      
      if (this.progressInterval) {
        clearInterval(this.progressInterval)
        this.progressInterval = null
      }
    },
    
    startProgressBar() {
      // 重置进度
      this.progress = 0
      
      const updateInterval = 30 // 每隔30ms更新一次
      const increment = (updateInterval / this.duration) * 100
      
      this.progressInterval = setInterval(() => {
        this.progress += increment
        
        // 确保进度不超过100%
        if (this.progress >= 100) {
          this.progress = 100
          clearInterval(this.progressInterval)
          this.progressInterval = null
        }
      }, updateInterval)
    },
    
    handleAction() {
      if (this.errorAction && typeof this.errorAction.callback === 'function') {
        this.errorAction.callback()
        this.hideError()
      }
    }
  },
  mounted() {
    // 监听API错误事件
    EventBus.on('api-error', (errorInfo) => {
      // 转换为 showError 方法需要的格式
      this.showError({
        type: 'client',  // 默认为客户端错误类型
        message: `${errorInfo.status} ${errorInfo.url} - ${errorInfo.message}`
      });
    });
  },
  beforeUnmount() {
    // 清除事件监听和超时
    EventBus.off('api-error');
    this.clearTimers();
  }
}
</script>

<style scoped>
.snackbar {
  position: fixed;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 460px;
  background-color: #323232;
  color: white;
  border-radius: 4px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  z-index: 1000;
  overflow: hidden;
}

.snackbar-content {
  display: flex;
  align-items: center;
  padding: 14px 16px;
}

.snackbar-icon {
  margin-right: 12px;
  font-size: 1.25rem;
}

.snackbar-message {
  flex: 1;
  font-size: 0.925rem;
  font-weight: 500;
}

.snackbar-action {
  background: transparent;
  border: none;
  color: #8bc34a;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.875rem;
  padding: 6px 12px;
  margin-left: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.5px;
}

.snackbar-action:hover {
  background-color: rgba(139, 195, 74, 0.1);
}

.snackbar-close {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.25rem;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 8px;
  padding: 0;
}

.snackbar-close:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.snackbar-progress {
  height: 4px;
  width: 100%;
  background-color: rgba(0, 0, 0, 0.2);
}

.snackbar-progress-inner {
  height: 100%;
  width: 0;
  background-color: #4caf50;
  transition: width 0.05s linear;
}

.error-type-network .snackbar-progress-inner {
  background-color: #ff9800; /* 橙色 */
}

.error-type-server .snackbar-progress-inner {
  background-color: #f44336; /* 红色 */
}

.error-type-client .snackbar-progress-inner {
  background-color: #03a9f4; /* 蓝色 */
}

.error-type-request .snackbar-progress-inner {
  background-color: #9c27b0; /* 紫色 */
}

.error-type-auth .snackbar-progress-inner {
  background-color: #ffc107; /* 黄色 */
}

.error-type-notfound .snackbar-progress-inner {
  background-color: #607d8b; /* 蓝灰色 */
}

.error-type-forbidden .snackbar-progress-inner {
  background-color: #e91e63; /* 粉红色 */
}

.error-type-ratelimit .snackbar-progress-inner {
  background-color: #ff5722; /* 深橙色 */
}

.error-type-success .snackbar-progress-inner {
  background-color: #4caf50; /* 绿色 */
}

.error-type-info .snackbar-progress-inner {
  background-color: #2196f3; /* 蓝色 */
}

.error-type-default .snackbar-progress-inner {
  background-color: #4caf50; /* 绿色 */
}

/* 动画 */
.snackbar-enter-active {
  transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
}

.snackbar-leave-active {
  transition: all 0.3s cubic-bezier(0.86, 0, 0.07, 1);
}

.snackbar-enter-from {
  opacity: 0;
  transform: translate(-50%, 80px);
}

.snackbar-leave-to {
  opacity: 0;
  transform: translate(-50%, 80px);
}

@media (max-width: 480px) {
  .snackbar {
    width: calc(100% - 32px);
    bottom: 8px;
    max-width: none;
  }
}
</style> 