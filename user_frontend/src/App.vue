<template>
  <div class="app-container">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    <AppSnackbar />
    <AnnouncementModal 
      v-model:visible="showAnnouncement" 
      @close="onAnnouncementClose" 
      :preloaded-data="preloadedAnnouncements"
    />
  </div>
</template>

<script>
import AppSnackbar from './components/AppSnackbar.vue'
import AnnouncementModal from './components/AnnouncementModal.vue'
import { ref, onMounted, watch, provide } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from './api'

export default {
  name: 'App',
  components: {
    AppSnackbar,
    AnnouncementModal
  },
  setup() {
    const router = useRouter()
    const showAnnouncement = ref(false)
    const hasAnnouncements = ref(false)
    const preloadedAnnouncements = ref([])
    
    // 提供全局访问公告状态的能力
    provide('announcements', {
      show: () => {
        if (hasAnnouncements.value) {
          showAnnouncement.value = true
        }
      },
      hasAnnouncements
    })
    
    // 预加载公告数据
    const preloadAnnouncements = async () => {
      try {
        console.log('预加载公告数据...')
        const response = await apiService.getActiveAnnouncements()
        if (response.data && Array.isArray(response.data)) {
          // 排序并过滤
          const announcements = response.data.sort((a, b) => {
            // 先按置顶排序
            if (a.is_pinned && !b.is_pinned) return -1
            if (!a.is_pinned && b.is_pinned) return 1
            
            // 再按更新时间排序（时间倒序，最新的在前面）
            return new Date(b.updated_at) - new Date(a.updated_at)
          })
          
          // 过滤"不再显示"的公告，但保留广告
          const readAnnouncementIds = JSON.parse(localStorage.getItem('readAnnouncements') || '[]')
          preloadedAnnouncements.value = announcements.filter(item => {
            // 广告类型的公告始终显示
            if (item.status === 'advertisement') return true
            return !readAnnouncementIds.includes(item.uuid)
          })
          
          // 设置是否有公告的状态
          hasAnnouncements.value = preloadedAnnouncements.value.length > 0
          console.log(`预加载完成，共有 ${preloadedAnnouncements.value.length} 条公告`)
        }
      } catch (error) {
        console.error('预加载公告数据失败:', error)
      }
    }
    
    // 检查是否需要显示公告
    const checkForAnnouncements = async () => {
      const justLoggedIn = localStorage.getItem('just_logged_in') === 'true'
      const isLoggedIn = !!localStorage.getItem('token')
      
      if (justLoggedIn && isLoggedIn) {
        // 清除登录标记
        localStorage.removeItem('just_logged_in')
        
        // 显示公告，此时已经预加载了公告数据
        if (hasAnnouncements.value) {
          showAnnouncement.value = true
        }
      }
    }
    
    // 公告关闭后的回调
    const onAnnouncementClose = (hasItems) => {
      showAnnouncement.value = false
      hasAnnouncements.value = hasItems
    }
    
    // 监听路由变化
    watch(() => router.currentRoute.value.path, (newPath) => {
      // 仅在非登录页面检查公告
      if (newPath !== '/login') {
        checkForAnnouncements()
      }
    })
    
    onMounted(() => {
      // 应用挂载完成后，通知index.html中的加载脚本
      document.documentElement.classList.add('app-mounted')
      
      // 确保页面在挂载后再显示，避免闪烁
      setTimeout(() => {
        const loadingEl = document.getElementById('app-loading')
        if (loadingEl) {
          loadingEl.classList.add('loaded')
        }
      }, 200)
      
      // 计算滚动条宽度，设置为CSS变量
      const scrollDiv = document.createElement('div')
      scrollDiv.style.width = '100px'
      scrollDiv.style.height = '100px'
      scrollDiv.style.overflow = 'scroll'
      scrollDiv.style.position = 'absolute'
      scrollDiv.style.top = '-9999px'
      document.body.appendChild(scrollDiv)
      
      const scrollbarWidth = scrollDiv.offsetWidth - scrollDiv.clientWidth
      document.documentElement.style.setProperty('--scrollbar-width', `${scrollbarWidth}px`)
      
      document.body.removeChild(scrollDiv)
      
      // 应用初始化时预加载公告数据
      preloadAnnouncements()
      
      // 检查是否需要显示公告
      checkForAnnouncements()
    })
    
    return {
      showAnnouncement,
      onAnnouncementClose,
      preloadedAnnouncements
    }
  }
}
</script>

<style>
/* 全局样式在assets/styles/index.css定义 */

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
