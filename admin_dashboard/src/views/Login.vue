<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginForm = reactive({
  username: '',
  password: '',
  turnstileToken: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ],
  turnstileToken: [
    { required: true, message: '请完成人机验证', trigger: 'change' }
  ]
}

const formRef = ref(null)
const turnstileContainer = ref(null)
const loading = ref(false)
const errorMessage = ref('')
let turnstileWidget = null

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      errorMessage.value = ''
      
      try {
        const result = await authStore.login(loginForm)
        if (result.success) {
          router.push({ path: '/dashboard' })
        } else {
          errorMessage.value = result.message || '登录失败，请检查账号密码'
          resetTurnstile()
        }
      } catch (error) {
        console.error('登录错误:', error)
        errorMessage.value = '登录过程中发生错误，请稍后再试'
        resetTurnstile()
      } finally {
        loading.value = false
      }
    }
  })
}

// 加载Turnstile脚本
const loadTurnstileScript = () => {
  if (!document.getElementById('turnstile-script')) {
    try {
      // 创建脚本标签
      const script = document.createElement('script')
      script.id = 'turnstile-script'
      script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js'
      script.async = true
      script.defer = true
      
      // 添加加载成功处理函数
      script.onload = () => {
        console.log('Turnstile脚本加载成功')
        initTurnstile()
      }
      
      // 添加加载失败处理函数
      script.onerror = (error) => {
        console.error('Turnstile脚本加载失败:', error)
        errorMessage.value = 'Turnstile验证组件加载失败，请刷新页面重试'
        
        // 如果是CSP问题，尝试提示用户
        if (error && error.target && error.target.src) {
          console.error(`可能是CSP策略阻止了脚本加载: ${error.target.src}`)
        }
      }
      
      document.head.appendChild(script)
    } catch (error) {
      console.error('加载Turnstile脚本时出错:', error)
      errorMessage.value = '加载验证组件时出错，请刷新页面重试'
    }
  } else {
    // 脚本标签已存在，尝试初始化
    initTurnstile()
  }
}

// 初始化Turnstile验证组件
const initTurnstile = () => {
  if (window.turnstile) {
    try {
      // 确保容器已经渲染
      if (!turnstileContainer.value) {
        console.error('Turnstile容器未找到')
        setTimeout(() => initTurnstile(), 500) // 延迟重试
        return
      }
      
      turnstileWidget = window.turnstile.render(turnstileContainer.value, {
        sitekey: import.meta.env.VITE_TURNSTILE_SITE_KEY || '1x00000000000000000000AA', // 使用环境变量中的site key
        theme: 'light',
        callback: (token) => {
          loginForm.turnstileToken = token
          console.log('Turnstile验证成功')
        },
        'expired-callback': () => {
          loginForm.turnstileToken = ''
          console.log('Turnstile验证已过期')
        },
        'error-callback': (error) => {
          loginForm.turnstileToken = ''
          console.error('Turnstile验证出错:', error)
        }
      })
    } catch (error) {
      console.error('初始化Turnstile组件时出错:', error)
    }
  } else {
    console.error('Turnstile对象未加载')
  }
}

// 重置Turnstile验证
const resetTurnstile = () => {
  if (turnstileWidget && window.turnstile) {
    window.turnstile.reset(turnstileWidget)
    loginForm.turnstileToken = ''
  }
}

onMounted(() => {
  loadTurnstileScript()
})

onBeforeUnmount(() => {
  // 清理Turnstile组件
  if (turnstileWidget && window.turnstile) {
    window.turnstile.reset(turnstileWidget)
  }
})
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1 class="login-title">管理员控制台</h1>
        <p class="login-subtitle">分布式任务调度系统</p>
      </div>
      
      <el-alert
        v-if="errorMessage"
        type="error"
        :title="errorMessage"
        show-icon
        :closable="false"
        style="margin-bottom: 20px;"
      />
      
      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="loginRules"
        label-position="top"
        @keyup.enter="handleLogin"
      >
        <el-form-item label="手机号" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入手机号"
            type="text"
            autocomplete="username"
            prefix-icon="el-icon-user"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            placeholder="请输入密码"
            type="password"
            autocomplete="current-password"
            show-password
            prefix-icon="el-icon-lock"
          />
        </el-form-item>
        
        <el-form-item prop="turnstileToken">
          <div ref="turnstileContainer" class="turnstile-container"></div>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%;"
            :disabled="!loginForm.turnstileToken"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: var(--background-color);
  transition: background-color 0.3s;
}

.login-box {
  width: 350px;
  padding: 30px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: var(--card-background);
  transition: background-color 0.3s, box-shadow 0.3s;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-title {
  text-align: center;
  margin-bottom: 25px;
  font-size: 22px;
  font-weight: bold;
  color: var(--text-color);
  transition: color 0.3s;
}

.login-subtitle {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

.login-form {
  margin-bottom: 15px;
}

.login-form .el-form-item {
  margin-bottom: 20px;
}

.remember-me {
  margin-bottom: 20px;
  color: var(--text-color-secondary);
  transition: color 0.3s;
}

.login-button {
  width: 100%;
}

/* 深色模式调整 */
@media (prefers-color-scheme: dark) {
  .login-box {
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.3);
  }
  
  :deep(.el-input__inner) {
    background-color: #2a2a2a;
    color: var(--text-color);
    border-color: var(--border-color);
  }
  
  :deep(.el-form-item__label) {
    color: var(--text-color);
  }
  
  :deep(.el-checkbox__label) {
    color: var(--text-color-secondary);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .login-box {
    width: 90%;
    max-width: 350px;
    padding: 20px;
  }
}

.turnstile-container {
  display: flex;
  justify-content: center;
  margin: 15px 0;
}
</style> 