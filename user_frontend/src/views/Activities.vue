<template>
  <div class="activities">
    <AppHeader />
    
    <div class="container main-content">
      <h1 class="page-title">签到活动</h1>
      
      <div class="card mb-4">
        <p class="text-center">页面开发中...</p>
      </div>
    </div>
  </div>
</template>

<script>
import AppHeader from '../components/AppHeader.vue'

export default {
  name: 'ActivitiesPage',
  components: {
    AppHeader
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
</style> 