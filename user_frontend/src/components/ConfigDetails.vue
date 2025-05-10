<template>
  <div class="config-details mt-3">
    <div class="config-section">
      <h4>基本设置</h4>
      <div class="row">
        <div class="col">
          <div class="config-item">
            <span class="label">班级ID:</span>
            <span>{{ config.class_id || '未设置' }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="config-section">
      <h4>自动签到设置</h4>
      <div class="row">
        <div class="col">
          <div class="config-item">
            <span class="label">触发类型:</span>
            <span>{{ getTriggerTypeText(config.trigger_type) }}</span>
          </div>
        </div>
      </div>
      <div class="row" v-if="config.trigger_type === 'threshold'">
        <div class="col">
          <div class="config-item">
            <span class="label">阈值(人数):</span>
            <span>{{ config.threshold_count || '未设置' }}</span>
          </div>
        </div>
        <div class="col">
          <div class="config-item">
            <span class="label">阈值(百分比):</span>
            <span>{{ config.threshold_percent ? `${config.threshold_percent}%` : '未设置' }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="config-section">
      <h4>通知设置</h4>
      <div class="row">
        <div class="col">
          <div class="config-item">
            <span class="label">签到检测通知:</span>
            <span>{{ config.notify_on_detect ? '开启' : '关闭' }}</span>
          </div>
        </div>
        <div class="col">
          <div class="config-item">
            <span class="label">签到成功通知:</span>
            <span>{{ config.notify_on_sign ? '开启' : '关闭' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfigDetails',
  props: {
    config: {
      type: Object,
      required: true
    },
    getTriggerTypeText: {
      type: Function,
      required: true
    }
  }
}
</script>

<style scoped>
.config-section {
  margin-bottom: var(--spacing-3);
  padding-bottom: var(--spacing-3);
  border-bottom: 1px solid var(--color-border);
}

.config-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.config-section h4 {
  font-size: 1rem;
  margin-bottom: var(--spacing-2);
  color: var(--color-primary);
}

.config-item {
  margin-bottom: var(--spacing-1);
  font-size: var(--font-size-sm);
}

.label {
  font-weight: 500;
  color: var(--color-text-muted);
  margin-right: var(--spacing-1);
}
</style> 