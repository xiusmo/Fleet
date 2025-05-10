<template>
  <div class="not-found">
    <div class="container not-found-content">
      <h1>404</h1>
      <h2>页面未找到</h2>
      <p>抱歉，您尝试访问的页面不存在</p>
      <router-link to="/" class="btn btn-primary">返回首页</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.not-found-content h1 {
  font-size: 6rem;
  color: var(--color-primary);
  margin: 0;
}

.not-found-content h2 {
  margin-bottom: var(--spacing-3);
}

.not-found-content p {
  margin-bottom: var(--spacing-4);
  color: var(--color-text-muted);
}
</style> 