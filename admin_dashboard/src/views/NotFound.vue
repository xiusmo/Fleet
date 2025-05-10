<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="not-found">
    <div class="content">
      <h1 class="error-code">404</h1>
      <h2 class="error-message">页面不存在</h2>
      <p class="error-description">抱歉，您访问的页面不存在或已被删除</p>
      <div class="actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button type="info" @click="goBack">返回上页</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
  padding: 40px;
  color: var(--text-color);
  transition: color 0.3s;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  margin-bottom: 20px;
  color: var(--primary-color);
}

.error-message {
  font-size: 24px;
  margin-bottom: 20px;
  color: var(--text-color);
}

.error-description {
  font-size: 16px;
  margin-bottom: 30px;
  max-width: 500px;
  color: var(--text-color-secondary);
}

.back-button {
  margin-top: 20px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .error-code {
    font-size: 80px;
  }
  
  .error-message {
    font-size: 20px;
  }
  
  .error-description {
    font-size: 14px;
  }
}
</style>