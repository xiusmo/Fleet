<template>
  <transition name="modal-fade">
    <div class="redirect-modal-overlay" v-if="visible" @click="closeModalOnOverlay"></div>
  </transition>
  
  <transition name="modal-slide">
    <div class="redirect-modal" v-if="visible">
      <div class="redirect-header">
        <h2>{{ title || '即将跳转' }}</h2>
        <button class="close-btn" @click="closeModal">×</button>
      </div>
      
      <div class="redirect-body">
        <div class="redirect-content">
          <div class="redirect-description" v-if="description">
            {{ description }}
          </div>
          
          <div class="redirect-link">
            <span class="link-label">目标地址:</span>
            <a :href="url" class="link-url" target="_blank" @click.prevent>{{ url }}</a>
          </div>
          
          <div class="redirect-countdown">
            <template v-if="countdownTime > 0">
              <span class="countdown-text">{{ countdownTime }}秒后自动跳转</span>
              <div class="countdown-progress">
                <div class="countdown-progress-inner" :style="progressStyle"></div>
              </div>
            </template>
            <span v-else class="countdown-done">准备跳转...</span>
          </div>
        </div>
      </div>
      
      <div class="redirect-actions">
        <button 
          class="btn btn-outline secondary-btn" 
          @click="closeModal"
        >
          取消
        </button>
        <button 
          class="btn btn-primary primary-btn" 
          @click="redirect"
          :disabled="!url"
        >
          立即跳转
        </button>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'LinkRedirectModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    url: {
      type: String,
      required: true
    },
    title: {
      type: String,
      default: '即将跳转到外部链接'
    },
    description: {
      type: String,
      default: '您即将离开当前网站，前往外部网站。请确认您了解相关风险。'
    },
    autoRedirect: {
      type: Boolean,
      default: true
    },
    countdownDuration: {
      type: Number,
      default: 5
    }
  },
  emits: ['close', 'update:visible', 'redirect'],
  data() {
    return {
      countdownTime: 0,
      countdownTimer: null,
      progress: 0,
      progressInterval: null
    }
  },
  computed: {
    progressStyle() {
      return {
        width: `${this.progress}%`
      }
    }
  },
  watch: {
    visible(newValue) {
      if (newValue) {
        document.body.classList.add('modal-open');
        this.startCountdown();
      } else {
        document.body.classList.remove('modal-open');
        this.clearTimers();
      }
    }
  },
  methods: {
    startCountdown() {
      // 清除可能存在的定时器
      this.clearTimers();
      
      // 设置倒计时初始值
      this.countdownTime = this.countdownDuration;
      this.progress = 0;
      
      if (this.autoRedirect) {
        // 倒计时定时器
        this.countdownTimer = setInterval(() => {
          if (this.countdownTime > 0) {
            this.countdownTime--;
          } else {
            this.clearTimers();
            this.redirect();
          }
        }, 1000);
        
        // 进度条更新
        const updateInterval = 30; // 每30ms更新一次
        const increment = (updateInterval / (this.countdownDuration * 1000)) * 100;
        
        this.progressInterval = setInterval(() => {
          this.progress += increment;
          if (this.progress >= 100) {
            this.progress = 100;
            clearInterval(this.progressInterval);
          }
        }, updateInterval);
      }
    },
    
    clearTimers() {
      if (this.countdownTimer) {
        clearInterval(this.countdownTimer);
        this.countdownTimer = null;
      }
      
      if (this.progressInterval) {
        clearInterval(this.progressInterval);
        this.progressInterval = null;
      }
    },
    
    closeModal() {
      this.clearTimers();
      this.$emit('update:visible', false);
      this.$emit('close');
    },
    
    closeModalOnOverlay(event) {
      // 只有点击遮罩层时才关闭模态框
      if (event.target === event.currentTarget) {
        this.closeModal();
      }
    },
    
    redirect() {
      this.clearTimers();
      
      // 使用window.location进行跳转，而不是打开新窗口
      // 这样可以避免浏览器的弹窗拦截
      this.$emit('redirect', this.url);
      
      // 直接在当前页面加载URL
      window.location.href = this.url;
      
      // 关闭模态框
      this.closeModal();
    }
  },
  beforeUnmount() {
    this.clearTimers();
    document.body.classList.remove('modal-open');
  }
}
</script>

<style scoped>
.redirect-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(3px);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.redirect-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: var(--color-card-bg, #ffffff);
  border-radius: var(--border-radius, 8px);
  box-shadow: var(--box-shadow, 0 2px 12px rgba(0, 0, 0, 0.15));
  width: 90%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--color-border, #e0e0e0);
  z-index: 1001;
}

.redirect-header {
  padding: var(--spacing-3, 16px);
  border-bottom: 1px solid var(--color-border, #e0e0e0);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.redirect-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--color-text, #333333);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--color-text-muted, #666666);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: var(--color-text, #333333);
}

.redirect-body {
  padding: var(--spacing-4, 20px);
  overflow-y: auto;
  flex: 1;
}

.redirect-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.redirect-description {
  font-size: 0.95rem;
  color: var(--color-text, #333333);
  line-height: 1.5;
}

.redirect-link {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background-color: var(--color-background-muted, #f5f5f5);
  border-radius: var(--border-radius, 4px);
  border: 1px solid var(--color-border, #e0e0e0);
}

.link-label {
  font-size: 0.85rem;
  color: var(--color-text-muted, #666666);
}

.link-url {
  color: var(--color-primary, #007bff);
  word-break: break-all;
  font-size: 0.9rem;
  text-decoration: none;
}

.link-url:hover {
  text-decoration: underline;
}

.redirect-countdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.countdown-text {
  text-align: center;
  font-weight: 500;
  color: var(--color-text, #333333);
}

.countdown-done {
  text-align: center;
  font-weight: 500;
  color: var(--color-primary, #007bff);
}

.countdown-progress {
  height: 4px;
  background-color: var(--color-border, #e0e0e0);
  border-radius: 2px;
  overflow: hidden;
}

.countdown-progress-inner {
  height: 100%;
  background-color: var(--color-primary, #007bff);
  transition: width 0.05s linear;
}

.redirect-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: var(--spacing-3, 16px);
  border-top: 1px solid var(--color-border, #e0e0e0);
}

.btn {
  padding: 8px 16px;
  border-radius: var(--border-radius, 4px);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--color-primary, #007bff);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark, #0069d9);
}

.btn-outline {
  background-color: transparent;
  color: var(--color-text, #333333);
  border: 1px solid var(--color-border, #e0e0e0);
}

.btn-outline:hover:not(:disabled) {
  background-color: var(--color-background-muted, #f5f5f5);
}

/* 动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-slide-enter-active {
  transition: all 0.3s cubic-bezier(0.19, 1, 0.22, 1);
}

.modal-slide-leave-active {
  transition: all 0.2s cubic-bezier(0.19, 1, 0.22, 1);
}

.modal-slide-enter-from,
.modal-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, -40%);
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .redirect-link {
    background-color: rgba(255, 255, 255, 0.05);
    border-color: var(--color-border, #3a3a3a);
  }
  
  .countdown-progress {
    background-color: rgba(255, 255, 255, 0.1);
  }
}

/* 响应式适配 */
@media (max-width: 480px) {
  .redirect-modal {
    width: 95%;
    max-height: 90vh;
  }
  
  .redirect-header h2 {
    font-size: 1.1rem;
  }
}
</style> 