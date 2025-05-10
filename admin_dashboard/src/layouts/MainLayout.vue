<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import {
  Monitor, User, Cpu, Document, Bell, Setting,
  ArrowDown, Fold, Expand
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const isCollapse = ref(false)

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const handleCommand = (command) => {
  if (command === 'logout') {
    handleLogout()
  } else if (command === 'profile') {
    // 可以在这里处理个人信息页面导航
    ElMessage.info('个人信息功能暂未实现')
  }
}

const currentRoute = computed(() => router.currentRoute.value)
const activeMenu = computed(() => {
  const { path } = currentRoute.value
  if (path.startsWith('/dashboard')) return 'dashboard'
  return path.split('/')[1] // 取路径的第一部分作为激活菜单
})
</script>

<template>
  <div class="app-container">
    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ 'is-collapsed': isCollapse }">
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        :collapse="isCollapse"
        :background-color="'var(--sidebar-background)'"
        :text-color="'var(--sidebar-text)'"
        active-text-color="#409EFF"
        router
      >
        <div class="logo-container">
          <h1 class="logo-title" v-if="!isCollapse">管理控制台</h1>
          <h1 class="logo-title-small" v-else>控</h1>
        </div>
        
        <el-menu-item index="dashboard" route="/dashboard">
          <el-icon><Monitor /></el-icon>
          <template #title>控制面板</template>
        </el-menu-item>
        
        <el-menu-item index="users" route="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        
        <el-menu-item index="workers" route="/workers">
          <el-icon><Cpu /></el-icon>
          <template #title>工作节点</template>
        </el-menu-item>
        
        <el-menu-item index="logs" route="/logs">
          <el-icon><Document /></el-icon>
          <template #title>系统日志</template>
        </el-menu-item>
        
        <el-menu-item index="announcements" route="/announcements">
          <el-icon><Bell /></el-icon>
          <template #title>公告管理</template>
        </el-menu-item>
        
        <el-menu-item index="system" route="/system">
          <el-icon><Setting /></el-icon>
          <template #title>系统状态</template>
        </el-menu-item>
      </el-menu>
    </div>
    
    <!-- 主内容区 -->
    <div class="main-container" :class="{ 'is-collapsed': isCollapse }">
      <!-- 顶部导航栏 -->
      <div class="header">
        <div class="left-area">
          <el-button
            @click="isCollapse = !isCollapse"
          >
            <el-icon>
              <component :is="isCollapse ? Expand : Fold"></component>
            </el-icon>
          </el-button>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute.meta && currentRoute.meta.title">
              {{ currentRoute.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="right-area">
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="el-dropdown-link">
              {{ authStore.user ? authStore.user.person_name || '管理员' : '管理员' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <!-- 内容区域 -->
      <div class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  width: 100%;
}

.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 1001;
  transition: width 0.3s, background-color 0.3s;
  background-color: var(--sidebar-background);
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar.is-collapsed {
  width: 64px;
}

.main-container {
  flex: 1;
  width: calc(100% - var(--sidebar-width));
  margin-left: var(--sidebar-width);
  transition: all 0.3s;
  position: relative;
  display: flex;
  flex-direction: column;
}

.main-container.is-collapsed {
  width: calc(100% - 64px);
  margin-left: 64px;
}

.header {
  padding: 0 20px;
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--header-background);
  box-shadow: 0 1px 4px var(--shadow-color);
  width: 100%;
  z-index: 1000;
}

.content {
  flex: 1;
  overflow-y: auto;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  background-color: var(--background-color);
  transition: background-color 0.3s;
}

.logo-container {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--sidebar-text);
  padding: 10px 0;
}

.logo-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--sidebar-text);
}

.logo-title-small {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--sidebar-text);
}

.el-menu-vertical:not(.el-menu--collapse) {
  width: var(--sidebar-width);
}

.left-area {
  display: flex;
  align-items: center;
}

.left-area .el-button {
  margin-right: 15px;
}

.right-area {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  font-size: 14px;
  color: var(--text-color);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式布局调整 */
@media (max-width: 768px) {
  .main-container {
    width: calc(100% - 64px);
    margin-left: 64px;
  }
  
  .main-container.is-collapsed {
    width: 100%;
    margin-left: 0;
  }
  
  .sidebar {
    width: 64px;
  }
  
  .sidebar.is-collapsed {
    width: 0;
    transform: translateX(-100%);
  }
}

/* 深色模式下的菜单样式调整 */
@media (prefers-color-scheme: dark) {
  :deep(.el-menu) {
    background-color: var(--sidebar-background);
    border-right-color: var(--border-color);
  }
  
  :deep(.el-menu-item), :deep(.el-sub-menu__title) {
    color: var(--sidebar-text);
  }
  
  :deep(.el-menu-item.is-active) {
    color: var(--primary-color);
    background-color: #1f2d3d;
  }
  
  :deep(.el-menu-item:hover), :deep(.el-sub-menu__title:hover) {
    background-color: #263445;
  }
  
  :deep(.el-breadcrumb__inner) {
    color: var(--text-color-secondary);
  }
  
  :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
    color: var(--text-color);
  }
  
  :deep(.el-breadcrumb__inner a, .el-breadcrumb__inner.is-link) {
    color: var(--primary-color);
  }
  
  :deep(.el-dropdown-link) {
    color: var(--text-color);
  }
  
  :deep(.el-dropdown-menu) {
    background-color: var(--card-background);
    border-color: var(--border-color);
  }
  
  :deep(.el-dropdown-menu__item) {
    color: var(--text-color);
  }
  
  :deep(.el-dropdown-menu__item:hover) {
    background-color: #2a2a2a;
  }
  
  :deep(.el-button) {
    border-color: var(--border-color);
  }
}
</style>