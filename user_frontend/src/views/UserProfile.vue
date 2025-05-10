<template>
  <div class="user-profile">
    <AppHeader />
    
    <div class="container main-content">
      <h1 class="page-title">个人设置</h1>
      
      <div class="card setting-card">
        <div class="setting-item">
          <div class="setting-label">
            <div class="setting-icon">🌓</div>
            <div class="setting-text">深色模式</div>
          </div>
          <div class="toggle-switch" @click="toggleTheme">
            <div class="switch-track" :class="{ 'active': isDarkMode }">
              <div class="switch-thumb"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AppHeader from '../components/AppHeader.vue'

export default {
  name: 'UserProfile',
  components: {
    AppHeader
  },
  data() {
    return {
      isDarkMode: false
    }
  },
  methods: {
    toggleTheme() {
      this.isDarkMode = !this.isDarkMode
      document.body.classList.toggle('dark-mode', this.isDarkMode)
      localStorage.setItem('darkMode', this.isDarkMode ? 'true' : 'false')
      console.log('主题切换为:', this.isDarkMode ? '深色模式' : '浅色模式')
    }
  },
  mounted() {
    const storedDarkMode = localStorage.getItem('darkMode')
    if (storedDarkMode !== null) {
      this.isDarkMode = storedDarkMode === 'true'
    } else {
      this.isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches
      localStorage.setItem('darkMode', this.isDarkMode ? 'true' : 'false')
    }
    document.body.classList.toggle('dark-mode', this.isDarkMode)
    console.log('初始主题:', this.isDarkMode ? '深色模式' : '浅色模式')
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

.setting-card {
  padding: 0;
  overflow: hidden;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-3) var(--spacing-4);
  border-bottom: 1px solid var(--color-border);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  display: flex;
  align-items: center;
}

.setting-icon {
  font-size: 1.25rem;
  margin-right: var(--spacing-2);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.setting-text {
  font-weight: 500;
}

.toggle-switch {
  cursor: pointer;
}

.switch-track {
  position: relative;
  width: 50px;
  height: 28px;
  background-color: var(--color-border);
  border-radius: 34px;
  transition: background-color 0.3s ease;
  border: none;
  outline: none;
}

.switch-track.active {
  background-color: var(--color-primary);
}

.switch-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 22px;
  height: 22px;
  background-color: white;
  border-radius: 50%;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  border: none;
}

.switch-track.active .switch-thumb {
  transform: translateX(22px);
}
</style> 