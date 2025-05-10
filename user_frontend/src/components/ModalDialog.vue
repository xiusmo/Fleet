<template>
  <div class="modal-wrapper">
    <!-- 背景遮罩层 -->
    <transition name="modal-fade">
      <div class="modal-overlay" v-if="show"></div>
    </transition>
    
    <!-- 模态框内容 -->
    <transition name="modal-slide">
      <div class="modal-container card" v-if="show">
        <div class="modal-header">
          <h3>{{ title }}</h3>
          <button class="close-btn" @click="close">&times;</button>
        </div>
        
        <div class="modal-body">
          <slot></slot>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'ModalDialog',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: ''
    }
  },
  watch: {
    show(val) {
      if (val) {
        document.body.classList.add('modal-open')
      } else {
        document.body.classList.remove('modal-open')
      }
    }
  },
  mounted() {
    if (this.show) {
      document.body.classList.add('modal-open')
    }
  },
  beforeUnmount() {
    document.body.classList.remove('modal-open')
  },
  methods: {
    close() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.modal-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
  pointer-events: none;
  overflow: hidden;
  touch-action: none;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  z-index: 1000;
  pointer-events: auto;
  touch-action: none;
}

.modal-container {
  position: relative;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  border: none;
  transform-origin: center center;
  z-index: 1001;
  margin: var(--spacing-3);
  pointer-events: auto;
  background-color: var(--color-background);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-3);
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  margin: 0;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-muted);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background-color: rgba(var(--color-text-rgb), 0.05);
  color: var(--color-text);
}

.modal-body {
  padding: var(--spacing-3);
}

/* 修复input元素样式继承问题 */
.modal-body :deep(input[type="text"]), 
.modal-body :deep(input[type="email"]), 
.modal-body :deep(input[type="password"]), 
.modal-body :deep(input[type="number"]),
.modal-body :deep(input[type="search"]),
.modal-body :deep(textarea),
.modal-body :deep(select) {
  width: 100% !important;
  box-sizing: border-box !important;
  padding: var(--spacing-2) var(--spacing-3) !important;
  border: 1px solid var(--color-input-border) !important;
  border-radius: var(--border-radius) !important;
  font-size: var(--font-size-base) !important;
  background-color: var(--color-input-bg) !important;
  color: var(--color-text) !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
  margin: 0 !important;
  flex: 1 !important;
  min-width: 0 !important;
}

/* 特别针对 number 类型输入框 */
.modal-body :deep(input[type="number"]) {
  appearance: textfield !important;
  -moz-appearance: textfield !important;
  -webkit-appearance: textfield !important;
}

.modal-body :deep(input[type="number"]::-webkit-outer-spin-button),
.modal-body :deep(input[type="number"]::-webkit-inner-spin-button) {
  -webkit-appearance: none !important;
  margin: 0 !important;
}

/* 修复配置表单中的容器样式 */
.modal-body :deep(.col-half) {
  width: 100% !important;
  padding: 0 !important;
  margin-bottom: var(--spacing-3) !important;
}

.modal-body :deep(.form-group) {
  margin-bottom: var(--spacing-3) !important;
  width: 100% !important;
}

.modal-body :deep(input[type="text"]:focus), 
.modal-body :deep(input[type="email"]:focus), 
.modal-body :deep(input[type="password"]:focus), 
.modal-body :deep(input[type="number"]:focus),
.modal-body :deep(input[type="search"]:focus),
.modal-body :deep(textarea:focus),
.modal-body :deep(select:focus) {
  outline: none !important;
  border-color: var(--color-primary) !important;
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.15) !important;
}

/* 背景遮罩动画 */
.modal-fade-enter-active {
  animation: overlayIn 0.3s ease-out forwards;
}

.modal-fade-leave-active {
  animation: overlayIn 0.2s ease-in reverse forwards;
}

/* 模态框本体动画 */
.modal-slide-enter-active {
  animation: modalIn 0.3s cubic-bezier(0.21, 1.02, 0.73, 1) forwards;
  will-change: transform, opacity;
}

.modal-slide-leave-active {
  animation: modalOut 0.2s ease-in forwards;
  will-change: transform, opacity;
}

@keyframes overlayIn {
  from { 
    opacity: 0; 
  }
  to { 
    opacity: 1; 
  }
}

@keyframes modalIn {
  0% { 
    opacity: 0; 
    transform: translateY(-20px); 
  }
  100% { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

@keyframes modalOut {
  0% { 
    opacity: 1; 
    transform: translateY(0); 
  }
  100% { 
    opacity: 0; 
    transform: translateY(20px); 
  }
}

/* 当模态框打开时，禁用body滚动 */
:global(body.modal-open) {
  overflow: hidden;
  position: fixed;
  width: 100%;
  height: 100%;
}
</style> 