import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/styles/index.css'

const app = createApp(App)
app.use(router)

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error(err, vm, info)
}

// 移除加载动画
const removeLoading = () => {
  const loading = document.querySelector('.app-loading')
  if (loading) {
    loading.style.opacity = '0'
    loading.style.transition = 'opacity 0.3s ease-out'
    setTimeout(() => {
      loading.remove()
    }, 300)
  }
}

app.mount('#app')
removeLoading()
