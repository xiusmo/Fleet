<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-box card">
        <div class="login-header">
          <h2>学习痛签到助手</h2>
          <p class="text-muted">使用学习痛账号登录</p>
        </div>
        
        <div class="alert alert-danger" v-if="error">
          {{ error }}
        </div>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="username" class="form-label">学习痛账号</label>
            <input
              type="text"
              id="username"
              class="input"
              v-model="form.username"
              placeholder="请输入手机号"
              required
              :disabled="loading"
            />
          </div>
          
          <div class="form-group">
            <label for="password" class="form-label">学习痛密码</label>
            <input
              type="password"
              id="password"
              class="input"
              v-model="form.password"
              placeholder="请输入密码"
              required
              :disabled="loading"
            />
          </div>
          
          
          <div class="form-actions">
            <button type="submit" class="btn btn-primary w-100" :disabled="loading || !form.turnstileToken">
              <span v-if="loading">登录中...</span>
              <span v-else>登录</span>
            </button>
          </div>
        </form>
        
        <div class="login-footer">
          <p class="text-muted text-center">登录即表示您同意我们的 <router-link to="/terms" class="terms-link">服务条款</router-link> 或 <span class="terms-link" @click="showTelegramRedirect">加入群聊</span></p>
        </div>

        <div class="form-group turnstile-container" ref="turnstileContainer"></div>

      </div>
      
      <div class="login-features">

        
        <router-link to="/qr-scanner" class="feature-item qr-scanner-feature">
          <div class="feature-icon">📷</div>
          <h3>二维码扫描器</h3>
          <p>无需登录，帮助已登录的用户完成二维码签到</p>
          <div class="try-now-btn">立即尝试 →</div>
        </router-link>

        <div class="feature-item">
          <div class="feature-icon">ℹ️</div>
          <h3>支持的类型</h3>
          <p>普通签到、拍照签到、数字码签到、手势签到、位置签到。二维码需要同学代扫。目前支持通过人机验证。</p>
        </div>

        <div class="feature-item">
          <div class="feature-icon">㊙️</div>
          <h3>特性</h3>
          <p>根据班级进行个性化配置。</p>
          <p>你还在找不靠谱的网站？恭喜，找到了。更新不及时，没有错误报告，满屏广告，服务不稳定，一键找罪受</p>
        </div>
        
        <div class="feature-item">
          <div class="feature-icon">🤷🏻</div>
          <h3>不支持无二维码签到</h3>
          <p>除非打赏 $1,000,000 让我把学习通买下来</p>
        </div>
        
      </div>
    </div>
    
    <LinkRedirectModal
      v-model:visible="showRedirectModal"
      :url="redirectUrl"
      title="加入Telegram群组"
      description="您即将跳转到Telegram群组，这里您可以获取最新的公告和帮助。"
      :countdown-duration="3"
      @redirect="handleRedirect"
    />
  </div>
</template>

<script>
import { userApi, saveTokens } from '../api'
import LinkRedirectModal from '../components/LinkRedirectModal.vue'

export default {
  name: 'LoginPage',
  components: {
    LinkRedirectModal
  },
  data() {
    return {
      form: {
        username: '',
        password: '',
        turnstileToken: ''
      },
      loading: false,
      error: '',
      themeColorMeta: null,
      showRedirectModal: false,
      redirectUrl: 'https://t.me/+tnB79Tw4q6A1ZDg1',
      turnstileWidget: null
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''
      
      try {
        console.log('开始登录请求:', this.form.username)
        const response = await userApi.login(this.form.username, this.form.password, this.form.turnstileToken)
        console.log('登录响应:', response.data)
        
        // 验证响应中是否包含必要的token信息
        if (!response.data || !response.data.access_token) {
          throw new Error('登录响应缺少必要的token信息')
        }
        
        // 使用工具函数保存token信息
        saveTokens(response.data)
        console.log('Token信息已保存')
        
        // 获取用户信息
        await this.getUserInfo()
        
        // 打印当前token信息，用于调试
        console.log('登录完成，当前token:', localStorage.getItem('token'))
        
        // 标记用户已登录，用于显示公告
        localStorage.setItem('just_logged_in', 'true')
        
        // 重定向到首页
        this.$router.push('/')
      } catch (error) {
        console.error('登录失败', error)
        this.error = error.response?.data?.detail || error.message || '登录失败，请检查账号和密码'
        
        // 刷新Turnstile验证
        this.resetTurnstile()
      } finally {
        this.loading = false
      }
    },
    
    async getUserInfo() {
      try {
        const response = await userApi.getCurrentUser()
        // 保存用户信息到本地存储
        localStorage.setItem('user', JSON.stringify(response.data))
      } catch (error) {
        console.error('获取用户信息失败', error)
      }
    },

    // 加载Turnstile脚本
    loadTurnstileScript() {
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
            this.initTurnstile()
          }
          
          // 添加加载失败处理函数
          script.onerror = (error) => {
            console.error('Turnstile脚本加载失败:', error)
            this.error = 'Turnstile验证组件加载失败，请刷新页面重试'
            
            // 如果是CSP问题，尝试提示用户
            if (error && error.target && error.target.src) {
              console.error(`可能是CSP策略阻止了脚本加载: ${error.target.src}`)
            }
          }
          
          document.head.appendChild(script)
        } catch (error) {
          console.error('加载Turnstile脚本时出错:', error)
          this.error = '加载验证组件时出错，请刷新页面重试'
        }
      } else {
        // 脚本标签已存在，尝试初始化
        this.initTurnstile()
      }
    },
    
    // 初始化Turnstile验证组件
    initTurnstile() {
      if (window.turnstile) {
        try {
          // 确保容器已经渲染
          if (!this.$refs.turnstileContainer) {
            console.error('Turnstile容器未找到')
            setTimeout(() => this.initTurnstile(), 500) // 延迟重试
            return
          }
          
          this.turnstileWidget = window.turnstile.render(this.$refs.turnstileContainer, {
            sitekey: import.meta.env.VITE_TURNSTILE_SITE_KEY || '1x00000000000000000000AA', // 使用环境变量中的site key
            theme: 'light',
            callback: (token) => {
              this.form.turnstileToken = token
              console.log('Turnstile验证成功')
            },
            'expired-callback': () => {
              this.form.turnstileToken = ''
              console.log('Turnstile验证已过期')
            },
            'error-callback': (error) => {
              this.form.turnstileToken = ''
              console.error('Turnstile验证出错:', error)
            }
          })
        } catch (error) {
          console.error('初始化Turnstile组件时出错:', error)
        }
      } else {
        console.error('Turnstile对象未加载')
      }
    },
    
    // 重置Turnstile验证
    resetTurnstile() {
      if (this.turnstileWidget && window.turnstile) {
        window.turnstile.reset(this.turnstileWidget)
        this.form.turnstileToken = ''
      }
    },

    // 设置状态栏主题色
    setThemeColor() {
      // 判断是否为深色模式
      const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches || 
                         document.body.classList.contains('dark-mode');
      
      // 设置主题色：深色模式为深蓝色，浅色模式为主色调
      const themeColor = isDarkMode ? '#1a237e' : '#4361ee';
      
      // 创建或更新meta标签
      if (!this.themeColorMeta) {
        this.themeColorMeta = document.createElement('meta');
        this.themeColorMeta.name = 'theme-color';
        document.head.appendChild(this.themeColorMeta);
      }
      
      this.themeColorMeta.content = themeColor;
    },

    showTelegramRedirect() {
      this.showRedirectModal = true;
    },
    
    handleRedirect(url) {
      console.log('正在跳转到:', url);
      // 这里可以添加跳转前的其他逻辑，比如发送分析事件等
    },
  },
  mounted() {
    // 组件挂载时设置主题色
    this.setThemeColor();
    
    // 监听系统颜色模式变化
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', this.setThemeColor);
    
    // 加载Turnstile脚本
    this.loadTurnstileScript();
  },
  beforeUnmount() {
    // 移除监听器
    window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', this.setThemeColor);
    
    // 组件卸载时移除meta标签
    if (this.themeColorMeta) {
      document.head.removeChild(this.themeColorMeta);
    }
    
    // 清理Turnstile组件
    if (this.turnstileWidget && window.turnstile) {
      window.turnstile.reset(this.turnstileWidget);
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-3);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
}

.login-container {
  width: 100%;
  max-width: 1000px;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

@media (min-width: 768px) {
  .login-container {
    flex-direction: row;
    align-items: center;
  }
}

.login-box {
  flex: 1;
  max-width: 400px;
  margin: 0 auto;
  background-color: var(--color-card-bg);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: var(--spacing-4);
}

@media (max-width: 767px) {
  .login-box {
    max-width: none;
    width: 90%;
    margin: 0 auto;
  }
  
  .login-page {
    padding: var(--spacing-2);
  }
  
  .login-container {
    padding: 0;
  }
}

.login-header {
  text-align: center;
  margin-bottom: var(--spacing-4);
}

.login-header h2 {
  color: var(--color-primary);
  margin-bottom: var(--spacing-2);
}

.login-form {
  margin-bottom: var(--spacing-3);
}

.form-actions {
  margin-top: var(--spacing-4);
}

.login-footer {
  margin-top: var(--spacing-4);
  font-size: var(--font-size-sm);
}

.login-features {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
}

.feature-item {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: var(--border-radius);
  padding: var(--spacing-3);
  backdrop-filter: blur(10px);
  color: white;
  transition: transform 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: var(--spacing-2);
}

.feature-item h3 {
  margin-bottom: var(--spacing-1);
}

.feature-item p {
  opacity: 0.9;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .login-page {
    background: linear-gradient(135deg, #1a237e 0%, #0d1b2a 100%);
  }
  
  .login-box {
    border: 1px solid var(--color-border);
  }
  
  .feature-item {
    background-color: rgba(0, 0, 0, 0.2);
  }
}

.dark-mode .login-page {
  background: linear-gradient(135deg, #1a237e 0%, #0d1b2a 100%);
}

.dark-mode .login-box {
  border: 1px solid var(--color-border);
}

.dark-mode .feature-item {
  background-color: rgba(0, 0, 0, 0.2);
}

.terms-link {
  color: var(--color-primary);
  text-decoration: none;
  transition: color 0.2s ease;
}

.terms-link:hover {
  text-decoration: underline;
  color: var(--color-primary-dark);
}

.qr-scanner-feature {
  background-color: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  text-decoration: none;
  color: white;
  position: relative;
  overflow: hidden;
}

.qr-scanner-feature::after {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 50px 50px 0;
  border-color: transparent rgba(255, 255, 255, 0.2) transparent transparent;
  z-index: 1;
}

.qr-scanner-feature:hover {
  background-color: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-5px);
}

.qr-scanner-feature .try-now-btn {
  display: inline-block;
  margin-top: var(--spacing-2);
  padding: var(--spacing-1) var(--spacing-2);
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: var(--border-radius);
  font-weight: bold;
  transition: background-color 0.3s ease;
}

.qr-scanner-feature:hover .try-now-btn {
  background-color: rgba(255, 255, 255, 0.5);
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .qr-scanner-feature {
    background-color: rgba(66, 66, 180, 0.2);
    border-color: rgba(66, 66, 180, 0.4);
  }
  
  .qr-scanner-feature:hover {
    background-color: rgba(66, 66, 180, 0.3);
    border-color: rgba(66, 66, 180, 0.6);
  }
  
  .qr-scanner-feature::after {
    border-color: transparent rgba(66, 66, 180, 0.4) transparent transparent;
  }
}

.dark-mode .qr-scanner-feature {
  background-color: rgba(66, 66, 180, 0.2);
  border-color: rgba(66, 66, 180, 0.4);
}

.dark-mode .qr-scanner-feature:hover {
  background-color: rgba(66, 66, 180, 0.3);
  border-color: rgba(66, 66, 180, 0.6);
}

.dark-mode .qr-scanner-feature::after {
  border-color: transparent rgba(66, 66, 180, 0.4) transparent transparent;
}

/* Turnstile样式 */
.turnstile-container {
  margin-top: var(--spacing-3);
  display: flex;
  justify-content: center;
}
</style> 