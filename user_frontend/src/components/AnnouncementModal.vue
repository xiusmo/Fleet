<template>
  <div class="announcement-wrapper">
    <!-- 背景遮罩层 -->
    <transition name="modal-fade">
      <div class="announcement-overlay" v-if="visible"></div>
    </transition>
    
    <!-- 模态框内容 -->
    <transition name="modal-slide">
      <div class="announcement-modal" v-if="visible" :class="{'announcement-ad': currentAnnouncement?.status === 'advertisement'}">
        <div class="announcement-header">
          <h2>
            {{ currentAnnouncement?.title || '公告' }}
            <span v-if="currentAnnouncement?.is_pinned" class="pinned-badge">置顶</span>
          </h2>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        
        <div class="announcement-body">
          <!-- 公告内容 -->
          <div class="announcement-content" v-if="currentAnnouncement">
            <!-- 封面图片 -->
            <img 
              v-if="currentAnnouncement.cover_image" 
              :src="currentAnnouncement.cover_image" 
              class="announcement-cover"
              alt="公告封面"
            />
            
            <!-- 摘要 -->
            <div class="announcement-summary" v-if="currentAnnouncement.summary">
              {{ currentAnnouncement.summary }}
            </div>
            
            <!-- 内容 -->
            <div class="announcement-detail" v-html="formattedContent"></div>
          </div>
          
          <!-- 加载中 -->
          <div class="announcement-loading" v-else-if="loading">
            <div class="spinner"></div>
            <p>加载中...</p>
          </div>
          
          <!-- 无公告 -->
          <div class="announcement-empty" v-else>
            <p>暂无公告</p>
          </div>
        </div>
        
        <div class="announcement-footer" v-if="announcements.length > 1">
          <div class="announcement-pagination">
            <span>{{ currentIndex + 1 }}/{{ announcements.length }}</span>
            <div class="pagination-controls">
              <button 
                class="pagination-btn" 
                :disabled="currentIndex === 0"
                @click="prevAnnouncement"
              >
                ←
              </button>
              <button 
                class="pagination-btn" 
                :disabled="currentIndex === announcements.length - 1"
                @click="nextAnnouncement"
              >
                →
              </button>
            </div>
          </div>
        </div>
        
        <div class="announcement-actions">
          <button 
            class="btn btn-outline secondary-btn" 
            @click="doNotShowAgain" 
            v-if="currentAnnouncement && currentAnnouncement.status !== 'advertisement'"
            :disabled="countdownTime > 0"
          >
            <span v-if="countdownTime > 0">不再显示此公告 {{ countdownTime }}秒</span>
            <span v-else>不再显示此公告</span>
          </button>
          <button 
            class="btn btn-primary primary-btn" 
            @click="closeModal"
            :disabled="primaryBtnDisabled"
          >
            {{ currentAnnouncement?.status === 'advertisement' ? '关闭' : '暂时关闭' }}
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { apiService } from '../api'
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import MarkdownIt from 'markdown-it' // 导入 markdown-it

export default {
  name: 'AnnouncementModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    preloadedData: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'update:visible'],
  setup(props, { emit }) {
    const announcements = ref([])
    const currentIndex = ref(0)
    const loading = ref(false)
    const countdownTime = ref(15) // 不再显示按钮的倒计时时间，15秒
    const primaryBtnDisabled = ref(true) // 主按钮禁用状态
    let countdownTimer = null // 倒计时定时器
    let primaryBtnTimer = null // 主按钮禁用定时器
    
    // 初始化 markdown-it
    const md = new MarkdownIt()
    
    // 获取当前公告
    const currentAnnouncement = computed(() => {
      if (announcements.value.length > 0 && currentIndex.value < announcements.value.length) {
        return announcements.value[currentIndex.value]
      }
      return null
    })
    
    // 格式化内容，支持 Markdown 和 HTML
    const formattedContent = computed(() => {
      if (currentAnnouncement.value?.content) {
        // 简单检查是否包含 HTML 标签
        if (/<[a-z][\s\S]*>/i.test(currentAnnouncement.value.content)) {
          // 如果看起来像 HTML，直接返回
          return currentAnnouncement.value.content
        } else {
          // 否则，使用 markdown-it 进行渲染
          return md.render(currentAnnouncement.value.content)
        }
      }
      return ''
    })
    
    // 获取公告列表
    const fetchAnnouncements = async () => {
      // 如果有预加载数据，直接使用
      if (props.preloadedData && props.preloadedData.length > 0) {
        console.log('使用预加载的公告数据:', props.preloadedData.length)
        announcements.value = [...props.preloadedData]
        return
      }
      
      loading.value = true
      try {
        console.log('从API获取公告数据...')
        const response = await apiService.getActiveAnnouncements()
        if (response.data && Array.isArray(response.data)) {
          // 按照置顶、时间倒序排序
          announcements.value = response.data.sort((a, b) => {
            // 先按置顶排序
            if (a.is_pinned && !b.is_pinned) return -1
            if (!a.is_pinned && b.is_pinned) return 1
            
            // 再按更新时间排序（时间倒序，最新的在前面）
            return new Date(b.updated_at) - new Date(a.updated_at)
          })
          
          // 过滤掉已经在本地存储中被标记为"不再显示"的公告
          filterReadAnnouncements()
        }
      } catch (error) {
        console.error('获取公告列表失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 过滤已读公告
    const filterReadAnnouncements = () => {
      const readAnnouncementIds = JSON.parse(localStorage.getItem('readAnnouncements') || '[]')
      announcements.value = announcements.value.filter(item => {
        // 广告类型的公告始终显示
        if (item.status === 'advertisement') return true
        return !readAnnouncementIds.includes(item.uuid)
      })
    }
    
    // 关闭模态框
    const closeModal = () => {
      // 停止倒计时
      if (countdownTimer) {
        clearInterval(countdownTimer)
        countdownTimer = null
      }
      
      // 清除主按钮定时器
      if (primaryBtnTimer) {
        clearTimeout(primaryBtnTimer)
        primaryBtnTimer = null
      }
      
      emit('update:visible', false)
      emit('close', announcements.value.length > 0)
    }
    
    // 上一条公告
    const prevAnnouncement = () => {
      if (currentIndex.value > 0) {
        currentIndex.value--
      }
    }
    
    // 下一条公告
    const nextAnnouncement = () => {
      if (currentIndex.value < announcements.value.length - 1) {
        currentIndex.value++
      }
    }
    
    // 标记不再显示
    const doNotShowAgain = () => {
      if (currentAnnouncement.value) {
        const readAnnouncementIds = JSON.parse(localStorage.getItem('readAnnouncements') || '[]')
        if (!readAnnouncementIds.includes(currentAnnouncement.value.uuid)) {
          readAnnouncementIds.push(currentAnnouncement.value.uuid)
          localStorage.setItem('readAnnouncements', JSON.stringify(readAnnouncementIds))
        }
        
        // 从当前列表中移除
        announcements.value = announcements.value.filter(item => item.uuid !== currentAnnouncement.value.uuid)
        
        // 调整当前索引
        if (currentIndex.value >= announcements.value.length) {
          currentIndex.value = Math.max(0, announcements.value.length - 1)
        }
        
        // 如果没有更多公告，关闭模态框
        if (announcements.value.length === 0) {
          closeModal()
        }
      }
    }
    
    // 开始倒计时
    const startCountdown = () => {
      // 重置倒计时
      countdownTime.value = 15
      
      // 清除可能存在的旧定时器
      if (countdownTimer) {
        clearInterval(countdownTimer)
      }
      
      // 创建新的定时器
      countdownTimer = setInterval(() => {
        if (countdownTime.value > 0) {
          countdownTime.value--
        } else {
          // 倒计时结束，清除定时器
          clearInterval(countdownTimer)
          countdownTimer = null
        }
      }, 1000)
      
      // 设置主按钮禁用状态，1秒后启用
      primaryBtnDisabled.value = true
      if (primaryBtnTimer) {
        clearTimeout(primaryBtnTimer)
      }
      primaryBtnTimer = setTimeout(() => {
        primaryBtnDisabled.value = false
        primaryBtnTimer = null
      }, 1000)
    }
    
    // 监听当前公告索引变化
    watch(currentIndex, () => {
      // 当前公告发生变化时，重新开始倒计时
      startCountdown()
    })
    
    // 监听visible属性变化
    watch(() => props.visible, (newVisible) => {
      if (newVisible) {
        // 当模态框打开时，阻止背景滚动
        document.body.classList.add('modal-open');
        
        // 当模态框打开时，判断是否需要获取公告
        const hasPreloadedData = props.preloadedData && props.preloadedData.length > 0;
        
        if (hasPreloadedData && announcements.value.length === 0) {
          // 如果有预加载数据但本地没有数据，使用预加载数据
          console.log('使用预加载数据显示公告')
          announcements.value = [...props.preloadedData];
          // 如果有公告，开始倒计时
          if (announcements.value.length > 0) {
            startCountdown();
          } else {
            closeModal();
          }
        } else if (!hasPreloadedData) {
          // 如果没有预加载数据，从API获取
          console.log('无预加载数据，从API获取')
          fetchAnnouncements().then(() => {
            // 如果没有公告，则自动关闭
            if (announcements.value.length === 0) {
              closeModal();
            } else {
              // 有公告，开始倒计时
              startCountdown();
            }
          });
        } else {
          // 已有本地数据，直接开始倒计时
          console.log('已有本地数据，直接显示')
          if (announcements.value.length > 0) {
            startCountdown();
          } else {
            closeModal();
          }
        }
      } else {
        // 模态框关闭时清除定时器
        if (countdownTimer) {
          clearInterval(countdownTimer);
          countdownTimer = null;
        }
        
        if (primaryBtnTimer) {
          clearTimeout(primaryBtnTimer);
          primaryBtnTimer = null;
        }
        
        // 移除body上的类，恢复背景滚动
        document.body.classList.remove('modal-open');
      }
    });
    
    // 监听预加载数据变化
    watch(() => props.preloadedData, (newData) => {
      if (newData && newData.length > 0 && announcements.value.length === 0) {
        console.log('预加载数据已更新，重新初始化公告')
        announcements.value = [...newData]
      }
    }, { deep: true })
    
    // 组件挂载时获取公告
    onMounted(() => {
      // 优先使用预加载数据
      if (props.preloadedData && props.preloadedData.length > 0) {
        console.log('组件挂载：使用预加载的公告数据')
        announcements.value = [...props.preloadedData]
        
        // 如果模态框可见且有公告，开始倒计时
        if (props.visible) {
          if (announcements.value.length > 0) {
            startCountdown()
          } else {
            closeModal()
          }
        }
      } else {
        // 无预加载数据，从API获取
        console.log('组件挂载：从API获取公告数据')
        fetchAnnouncements().then(() => {
          // 如果没有公告且模态框显示中，则自动关闭
          if (props.visible && announcements.value.length === 0) {
            closeModal()
          } else if (props.visible && announcements.value.length > 0) {
            // 有公告且模态框显示中，开始倒计时
            startCountdown()
          }
        })
      }
    })
    
    // 组件卸载时清除定时器
    onUnmounted(() => {
      if (countdownTimer) {
        clearInterval(countdownTimer)
        countdownTimer = null
      }
      
      if (primaryBtnTimer) {
        clearTimeout(primaryBtnTimer)
        primaryBtnTimer = null
      }
    })
    
    return {
      announcements,
      currentIndex,
      currentAnnouncement,
      formattedContent,
      loading,
      closeModal,
      prevAnnouncement,
      nextAnnouncement,
      doNotShowAgain,
      countdownTime,
      primaryBtnDisabled
    }
  }
}
</script>

<style scoped>
.announcement-wrapper {
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
  overflow: hidden; /* 防止模态框内容滚动影响背景 */
  touch-action: none; /* 防止移动设备上的滑动穿透 */
}

.announcement-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(3px);
  z-index: 1000;
  pointer-events: auto;
  touch-action: none; /* 防止移动设备上的滑动穿透 */
}

.announcement-modal {
  position: relative;
  background-color: var(--color-card-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  width: 90%;
  max-width: 750px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--color-border);
  z-index: 1001;
  pointer-events: auto;
}

.announcement-ad {
  border: 2px solid var(--color-primary);
}

.announcement-header {
  padding: var(--spacing-3);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.announcement-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 8px;
}

.pinned-badge {
  display: inline-block;
  font-size: 0.75rem;
  padding: 2px 6px;
  background-color: var(--color-primary);
  color: white;
  border-radius: 4px;
  font-weight: normal;
  line-height: 1.2;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: var(--color-text);
}

.announcement-body {
  flex: 1;
  padding: var(--spacing-4);
  overflow-y: auto;
}

.announcement-cover {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: var(--border-radius);
  margin-bottom: var(--spacing-3);
}

.announcement-summary {
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: var(--spacing-3);
  color: var(--color-text);
  padding-bottom: var(--spacing-2);
  border-bottom: 1px solid var(--color-border);
}

.announcement-detail {
  font-size: 1rem;
  line-height: 1.6;
  color: var(--color-text);
}

/* 为 Markdown 渲染的元素添加样式 */
.announcement-detail > *:first-child {
  margin-top: 0;
}

.announcement-detail > *:last-child {
  margin-bottom: 0;
}

.announcement-detail h1,
.announcement-detail h2,
.announcement-detail h3,
.announcement-detail h4,
.announcement-detail h5,
.announcement-detail h6 {
  margin-top: var(--spacing-4);
  margin-bottom: var(--spacing-2);
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-heading);
}

.announcement-detail h1 { font-size: 1.8em; }
.announcement-detail h2 { font-size: 1.5em; }
.announcement-detail h3 { font-size: 1.3em; }
.announcement-detail h4 { font-size: 1.1em; }

.announcement-detail p {
  margin-bottom: var(--spacing-3);
}

.announcement-detail ul,
.announcement-detail ol {
  margin-bottom: var(--spacing-3);
  padding-left: var(--spacing-4);
}

.announcement-detail li {
  margin-bottom: var(--spacing-1);
}

.announcement-detail blockquote {
  margin: var(--spacing-3) 0;
  padding: var(--spacing-2) var(--spacing-3);
  border-left: 4px solid var(--color-primary);
  background-color: var(--color-sidebar-bg);
  color: var(--color-text-muted);
  font-style: italic;
}

.announcement-detail blockquote p {
  margin-bottom: 0;
}

.announcement-detail code {
  font-family: var(--font-family-mono);
  background-color: var(--color-background);
  padding: 0.2em 0.4em;
  border-radius: var(--border-radius-sm);
  font-size: 0.9em;
}

.announcement-detail pre {
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  padding: var(--spacing-3);
  margin: var(--spacing-3) 0;
  overflow-x: auto; /* 允许代码块水平滚动 */
}

.announcement-detail pre code {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
  font-size: 0.9em; 
  line-height: 1.4;
}

.announcement-detail a {
  color: var(--color-primary);
  text-decoration: none;
}

.announcement-detail a:hover {
  text-decoration: underline;
}

.announcement-detail img {
  max-width: 100%;
  height: auto;
  border-radius: var(--border-radius);
  margin: var(--spacing-2) 0;
}

.announcement-detail hr {
  border: 0;
  border-top: 1px solid var(--color-border);
  margin: var(--spacing-4) 0;
}

.announcement-footer {
  padding: var(--spacing-2) var(--spacing-3);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.announcement-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.pagination-controls {
  display: flex;
  gap: var(--spacing-2);
}

.pagination-btn {
  background-color: var(--color-sidebar-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  padding: var(--spacing-1) var(--spacing-2);
  cursor: pointer;
  font-size: 1rem;
  color: var(--color-text);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn:hover:not(:disabled) {
  background-color: var(--color-background);
}

.announcement-actions {
  padding: var(--spacing-3);
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-2);
  border-top: 1px solid var(--color-border);
}

.primary-btn, .secondary-btn {
  font-size: 0.9rem;
  font-weight: 500;
}

.primary-btn {
  min-width: 80px;
}

.secondary-btn {
  min-width: 120px;
}

.secondary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: var(--color-sidebar-bg);
  color: var(--color-text-muted);
}

.secondary-btn:disabled:hover {
  background-color: var(--color-sidebar-bg);
  transform: none;
  box-shadow: none;
}

.announcement-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-sidebar-bg);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-2);
}

.announcement-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: var(--color-text-muted);
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 媒体查询 */
@media (max-width: 768px) {
  .announcement-modal {
    width: 95%;
    max-height: 90vh;
  }
  
  .announcement-actions {
    flex-direction: column;
  }
  
  .primary-btn, .secondary-btn {
    width: 100%;
  }
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: rgba(var(--color-primary-rgb), 0.6);
  transform: none;
  box-shadow: none;
}

/* 当模态框打开时，禁用body滚动 */
:global(body.modal-open) {
  overflow: hidden;
  position: fixed;
  width: 100%;
  height: 100%;
}
</style> 