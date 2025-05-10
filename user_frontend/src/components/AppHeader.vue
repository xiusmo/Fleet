<template>
  <div class="header-wrapper">
    <header class="app-header" :class="{'menu-expanded': showMobileMenu}">
      <div class="container">
        <div class="header-content">
          <div class="logo">
            <router-link to="/">
              <h1 class="full-title">学习痛签到助手</h1>
              <h1 class="short-title">签到助手</h1>
            </router-link>
          </div>
          <nav class="main-nav" v-if="isLoggedIn">
            <ul>
              <li><router-link to="/">仪表盘</router-link></li>
              <li><router-link to="/sign-configs">签到配置</router-link></li>
              <li><router-link to="/qr-scanner">扫码签到</router-link></li>
              <li v-if="hasAnnouncements"><a href="#" @click.prevent="showAnnouncements">公告 <span class="badge" v-if="hasAnnouncements">新</span></a></li>
            </ul>
          </nav>
          <div class="user-controls">
            <div class="announcement-icon" v-if="hasAnnouncements && isLoggedIn">
              <a href="#" @click.prevent="showAnnouncements" class="announcement-link" title="查看公告">
                <span class="icon">📢</span>
                <span class="badge"></span>
              </a>
            </div>
            <div class="user-menu" v-if="isLoggedIn">
              <div class="user-menu-toggle" @click="toggleUserMenu($event)">
                <span class="username">你好 {{ username }}</span>
                <span class="arrow">▼</span>
              </div>
              <div class="user-menu-dropdown" v-if="isUserMenuOpen">
                <ul>
                  <li><router-link to="/profile">个人设置</router-link></li>
                  <li v-if="hasAnnouncements"><a href="#" @click.prevent="showAnnouncements">查看公告</a></li>
                  <li><a href="#" @click.prevent="logout">退出登录</a></li>
                </ul>
              </div>
            </div>
            <button class="mobile-menu-btn" 
              @click="toggleMobileMenu" 
              v-if="isLoggedIn"
              :class="{'active': showMobileMenu}"
            >
              <span></span>
              <span></span>
              <span></span>
            </button>
          </div>
        </div>
      </div>
    </header>
    
    <!-- 移动设备导航菜单 - 平级放置 -->
    <div class="mobile-menu-container" v-if="isLoggedIn">
      <div class="mobile-menu" :class="{'show': showMobileMenu}">
        <nav>
          <ul>
            <li><router-link to="/" @click="showMobileMenu = false">仪表盘</router-link></li>
            <li><router-link to="/sign-configs" @click="showMobileMenu = false">签到配置</router-link></li>
            <li><router-link to="/qr-scanner" @click="showMobileMenu = false">扫码签到</router-link></li>
            <li v-if="hasAnnouncements"><a href="#" @click.prevent="showAnnouncementsAndCloseMenu">公告 <span class="mobile-badge" v-if="hasAnnouncements">新</span></a></li>
            <li><router-link to="/profile" @click="showMobileMenu = false">个人设置</router-link></li>
            <li><a href="#" @click.prevent="logout">退出登录</a></li>
          </ul>
        </nav>
      </div>
    </div>
  </div>
</template>

<script>
import { authApi } from '../api'
import { inject } from 'vue'

export default {
  name: 'AppHeader',
  data() {
    return {
      isUserMenuOpen: false,
      showMobileMenu: false,
      windowWidth: window.innerWidth
    }
  },
  setup() {
    // 注入公告状态
    const announcements = inject('announcements', {
      show: () => {},
      hasAnnouncements: { value: false }
    })

    return {
      announcements
    }
  },
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token')
    },
    username() {
      const userData = JSON.parse(localStorage.getItem('user') || '{}')
      return userData.person_name || '用户名占位'
    },
    isMobileView() {
      return this.windowWidth <= 768
    },
    hasAnnouncements() {
      return this.announcements.hasAnnouncements.value
    }
  },
  methods: {
    showAnnouncements() {
      this.announcements.show()
      this.isUserMenuOpen = false // 关闭用户菜单
    },
    showAnnouncementsAndCloseMenu() {
      this.announcements.show()
      this.showMobileMenu = false // 关闭移动菜单
    },
    toggleUserMenu(event) {
      if (event) {
        event.stopPropagation();
      }
      
      if (!this.isMobileView) {
        this.isUserMenuOpen = !this.isUserMenuOpen
      }
    },
    toggleMobileMenu() {
      this.showMobileMenu = !this.showMobileMenu
    },
    async logout() {
      try {
        // 调用登出API
        await authApi.logout().catch(error => {
          console.error('登出API调用失败', error)
        })
        
        // 清除所有本地存储的令牌和用户信息
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        
        // 重定向到登录页
        this.$router.push('/login')
      } catch (error) {
        console.error('登出失败', error)
        // 即使API调用失败，也清除本地存储并跳转
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        this.$router.push('/login')
      }
    },
    closeUserMenu(e) {
      if (this.isUserMenuOpen && !e.target.closest('.user-menu')) {
        this.isUserMenuOpen = false
      }
    },
    handleResize() {
      this.windowWidth = window.innerWidth
    }
  },
  mounted() {
    document.addEventListener('click', this.closeUserMenu)
    
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.closeUserMenu)
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style scoped>
.header-wrapper {
  position: sticky;
  top: 0;
  z-index: 100;
}

.app-header {
  background-color: rgba(var(--color-background-rgb), 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px var(--color-shadow);
  padding: var(--spacing-2) 0;
  /* transition: background-color 0.3s ease, backdrop-filter 0.3s ease, box-shadow 0.3s ease; */
  z-index: 100;
}

.mobile-menu-container {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  z-index: 99;
}

/* 移动导航菜单 */
.mobile-menu {
  display: none; /* 在移动视图外隐藏 */
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.mobile-menu.show {
  max-height: 300px;
  opacity: 1;
  background-color: rgba(var(--color-background-rgb), 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 10px -2px var(--color-shadow);
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.app-header .container {
  position: relative; /* 确保容器有相对定位，为移动菜单提供定位上下文 */
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo h1 {
  font-size: 1.5rem;
  margin: 0;
  color: var(--color-primary);
}

.full-title {
  display: block;
}

.short-title {
  display: none;
}

.logo a {
  text-decoration: none;
}

.main-nav ul {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.main-nav li {
  margin-left: var(--spacing-3);
}

.main-nav a {
  color: var(--color-text);
  text-decoration: none;
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--border-radius);
  transition: all 0.2s ease;
}

.main-nav a:hover,
.main-nav a.router-link-active {
  color: var(--color-primary);
  background-color: var(--color-sidebar-bg);
}

.user-controls {
  display: flex;
  align-items: center;
  position: relative;
  z-index: 110;
}

.user-menu {
  position: relative;
}

.user-menu-toggle {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--border-radius);
  user-select: none;
}

.user-menu-toggle:hover {
  background-color: var(--color-sidebar-bg);
}

.arrow {
  font-size: 0.7rem;
  margin-left: var(--spacing-1);
  transition: transform 0.2s ease;
}

.user-menu-open .arrow {
  transform: rotate(180deg);
}

.user-menu-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: var(--color-card-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  border: 1px solid var(--color-border);
  width: 160px;
  margin-top: var(--spacing-1);
  z-index: 1000;
}

.user-menu-dropdown ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.user-menu-dropdown li {
  border-bottom: 1px solid var(--color-border);
}

.user-menu-dropdown li:last-child {
  border-bottom: none;
}

.user-menu-dropdown a {
  display: block;
  padding: var(--spacing-2);
  color: var(--color-text);
  text-decoration: none;
  transition: all 0.2s ease;
}

.user-menu-dropdown a:hover {
  background-color: var(--color-sidebar-bg);
  color: var(--color-primary);
}

/* 移动菜单按钮 */
.mobile-menu-btn {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 24px;
  height: 18px;
  background: none;
  border: none;
  cursor: pointer;
  margin-left: var(--spacing-2);
  padding: var(--spacing-1);
  border-radius: var(--border-radius);
  transition: background-color 0.2s ease;
  z-index: 120;
}

.mobile-menu-btn:hover {
  background-color: rgba(var(--color-text-rgb), 0.05);
}

.mobile-menu-btn span {
  display: block;
  height: 2px;
  width: 100%;
  background-color: var(--color-text);
  border-radius: 2px;
  transition: all 0.3s ease;
  transform-origin: center;
}

/* 移动菜单按钮激活状态 */
.mobile-menu-btn.active span:nth-child(1) {
  transform: translateY(8px) rotate(45deg);
}

.mobile-menu-btn.active span:nth-child(2) {
  opacity: 0;
}

.mobile-menu-btn.active span:nth-child(3) {
  transform: translateY(-8px) rotate(-45deg);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .main-nav {
    display: none;
  }
  
  .mobile-menu-btn {
    display: flex;
  }
  
  .mobile-menu {
    display: block;
  }
  
  .logo {
    display: none;
  }

  .header-content {
    justify-content: flex-end;
  }
  
  .user-controls {
    width: 100%;
    justify-content: flex-end;
  }
  
  .user-menu-toggle {
    cursor: default;
    padding: var(--spacing-1) 0;
  }
  
  .user-menu-toggle:hover {
    background-color: transparent;
  }
  
  .arrow {
    display: none;
  }
  
  .username {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

/* 确保点击事件可以穿透app-loading层 */
#app.ready .user-controls {
  pointer-events: auto;
}

.mobile-menu ul {
  list-style: none;
  padding: var(--spacing-2) 0;
  margin: 0;
}

.mobile-menu li {
  border-bottom: 1px solid rgba(var(--color-text-rgb), 0.05);
}

.mobile-menu li:last-child {
  border-bottom: none;
}

.mobile-menu a {
  display: block;
  padding: var(--spacing-2) var(--spacing-3);
  color: var(--color-text);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
}

.mobile-menu a:hover,
.mobile-menu a.router-link-active {
  color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.05);
}

.badge {
  display: inline-block;
  background-color: var(--color-danger);
  color: white;
  font-size: 0.7rem;
  padding: 0.1rem 0.3rem;
  border-radius: 10px;
  margin-left: 0.3rem;
  animation: pulse 1s infinite;
}

.mobile-badge {
  display: inline-block;
  background-color: var(--color-danger);
  color: white;
  font-size: 0.7rem;
  padding: 0.1rem 0.3rem;
  border-radius: 10px;
  margin-left: 0.3rem;
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

/* 隐藏喇叭图标在大屏幕设备 */
.announcement-icon {
  display: none;
}

/* 在移动设备上显示喇叭图标 */
@media (max-width: 768px) {
  .announcement-icon {
    display: block;
    margin-right: 1rem;
    position: relative;
  }
}

.announcement-link {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text);
  text-decoration: none;
  position: relative;
  font-size: 1.2rem;
}

.announcement-link .badge {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-danger);
  padding: 0;
}

.announcement-link:hover {
  color: var(--color-primary);
}
</style> 