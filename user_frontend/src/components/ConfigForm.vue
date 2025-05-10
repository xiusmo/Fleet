<template>
  <div class="config-form">
    <div class="form-tabs mb-4">
      <button 
        type="button" 
        class="tab-btn" 
        :class="{'active': activeTab === 'basic'}" 
        @click="activeTab = 'basic'"
      >
        基本
      </button>
      <button 
        type="button" 
        class="tab-btn" 
        :class="{'active': activeTab === 'location'}" 
        @click="activeTab = 'location'"
      >
        位置照片
      </button>
      <button 
        type="button" 
        class="tab-btn" 
        :class="{'active': activeTab === 'trigger'}" 
        @click="activeTab = 'trigger'"
      >
        策略
      </button>
      <button 
        type="button" 
        class="tab-btn" 
        :class="{'active': activeTab === 'advanced'}" 
        @click="activeTab = 'advanced'"
      >
        高级
      </button>
    </div>
    
    <!-- 基本信息 -->
    <div v-show="activeTab === 'basic'">
      <div class="form-group">
        <label for="config_name">配置名称</label>
        <input type="text" id="config_name" v-model="localForm.name" class="input" required />
      </div>

      <div class="form-group">
        <div class="d-flex justify-content-between align-items-center">
            <div for="is_default" class="setting-label">设为默认配置</div>
          <div class="toggle-switch">
            <input type="checkbox" id="is_default" v-model="localForm.is_default" />
            <label for="is_default"></label>
          </div>
        </div>
      </div>
      
      <div class="form-group">
        <label for="class_id">班级ID <span class="required-mark" v-if="!localForm.is_default">*</span></label>
        <input 
          type="text" 
          id="class_id" 
          v-model="localForm.class_id" 
          class="input" 
          :disabled="localForm.is_default"
          :class="{'input-disabled': localForm.is_default, 'input-error': !localForm.is_default && isSubmitted && !localForm.class_id}"
          required
        />
        <small class="form-text" v-if="!localForm.is_default && !isSubmitted">非默认配置时必填，用于识别此配置应用的班级</small>
        <small class="form-text text-muted" v-if="localForm.is_default">默认配置不能设置班级ID</small>
        <div class="text-danger" v-if="!localForm.is_default && isSubmitted && !localForm.class_id">请输入班级ID</div>
      </div>
    </div>
    
    <!-- 位置和照片设置 -->
    <div v-show="activeTab === 'location'">
      <h4 class="section-title">位置设置</h4>
      <!-- <div class="form-group">
        <label for="location_text">位置文本</label>
        <input type="text" id="location_text" v-model="localForm.location_text" class="input" placeholder="例如：某大学某教学楼" />
      </div> -->
      
      <!-- <div class="form-row"> -->
        <!-- <div class="col-half">
          <div class="form-group">
            <label for="longitude">经度</label>
            <input type="number" id="longitude" v-model="localForm.longitude" class="input" step="0.000001" placeholder="例如：116.123456" />
          </div>
        </div>
        <div class="col-half">
          <div class="form-group">
            <label for="latitude">纬度</label>
            <input type="number" id="latitude" v-model="localForm.latitude" class="input" step="0.000001" placeholder="例如：39.987654" />
          </div>
        </div> -->
      <!-- </div> -->
      
      <!-- <div class="form-group">
        <label for="accuracy">精度（米）</label>
        <input type="number" id="accuracy" v-model="localForm.accuracy" class="input" min="1" step="0.1" placeholder="默认：5.0" />
        <small class="form-text">定位精度，越小越精确</small>
      </div> -->
      
      
      <div class="form-group d-flex justify-content-between align-items-center">
        <div>
          <div for="use_random_position" class="setting-label">使用随机位置</div>
        </div>
        <div class="toggle-switch">
          <input type="checkbox" id="use_random_position" v-model="localForm.use_random_position" />
          <label for="use_random_position"></label>
        </div>
      </div>
      
      <div class="form-group" v-if="localForm.use_random_position">
        <label for="position_offset">位置随机偏移量</label>
        <input type="number" id="position_offset" v-model="localForm.position_offset" class="input" min="0.00001" step="0.00001" placeholder="默认：0.0001" />
        <small class="form-text">偏移范围，建议值：0.00005-0.0005</small>
      </div>
      
      <h4 class="mt-4 section-title">照片设置</h4>
      <div class="form-group d-flex justify-content-between align-items-center">
        <div>
          <div for="use_random_photo" class="setting-label">使用随机照片</div>
          <small class="form-text ms-2">用别人的照片,我赌老师不会检查</small>
        </div>
        <div class="toggle-switch">
          <input type="checkbox" id="use_random_photo" v-model="localForm.use_random_photo" />
          <label for="use_random_photo"></label>
        </div>
      </div>
    </div>
    
    <!-- 触发策略 -->
    <div v-show="activeTab === 'trigger'">
      <div class="form-group mb-4">
        <h4 class="mt-4 section-title">触发方式</h4>
        <div class="radio-card-group">
          <label 
            class="radio-card" 
            :class="{'active': localForm.trigger_type === 'manual'}"
          >
            <input 
              type="radio" 
              name="trigger_type" 
              value="manual" 
              v-model="localForm.trigger_type" 
            />
            <div class="radio-card-content">
              <div class="radio-card-title">手动触发</div>
              <div class="radio-card-desc">收到通知后手动确认签到</div>
            </div>
          </label>
          
          <label 
            class="radio-card" 
            :class="{'active': localForm.trigger_type === 'immediate'}"
          >
            <input 
              type="radio" 
              name="trigger_type" 
              value="immediate" 
              v-model="localForm.trigger_type" 
            />
            <div class="radio-card-content">
              <div class="radio-card-title">立即触发</div>
              <div class="radio-card-desc">检测到签到时立即执行</div>
            </div>
          </label>
          
          <label 
            class="radio-card" 
            :class="{'active': localForm.trigger_type === 'threshold'}"
          >
            <input 
              type="radio" 
              name="trigger_type" 
              value="threshold" 
              v-model="localForm.trigger_type" 
            />
            <div class="radio-card-content">
              <div class="radio-card-title">阈值触发</div>
              <div class="radio-card-desc">当签到人数达到阈值时触发</div>
            </div>
          </label>
        </div>
      </div>
      
      <div v-if="localForm.trigger_type === 'threshold'" class="card-inner">
        <h4>阈值设置</h4>
        
        <div class="threshold-selector mb-3">
          <div class="form-check-inline">
            <input 
              type="radio" 
              id="threshold_type_count" 
              name="threshold_type" 
              class="form-check-input" 
              :checked="!usePercentThreshold" 
              @change="usePercentThreshold = false"
            />
            <label for="threshold_type_count" class="form-check-label">按人数</label>
          </div>
          <div class="form-check-inline">
            <input 
              type="radio" 
              id="threshold_type_percent" 
              name="threshold_type" 
              class="form-check-input" 
              :checked="usePercentThreshold" 
              @change="usePercentThreshold = true"
            />
            <label for="threshold_type_percent" class="form-check-label">按百分比</label>
          </div>
        </div>
        
        <div class="threshold-input">
          <div v-if="!usePercentThreshold" class="form-group">
            <label for="threshold_count">人数阈值</label>
            <div class="input-with-description">
              <input 
                type="number" 
                id="threshold_count" 
                v-model="localForm.threshold_count" 
                class="input" 
                min="1" 
              />
              <div class="input-description">当已签到人数达到此值时触发</div>
            </div>
          </div>
          
          <div v-else class="form-group">
            <label for="threshold_percent">百分比阈值</label>
            <div class="input-with-description">
              <div class="input-append">
                <input 
                  type="number" 
                  id="threshold_percent" 
                  v-model="localForm.threshold_percent" 
                  class="input" 
                  min="0" 
                  max="100" 
                />
                <span class="input-append-text">%</span>
              </div>
              <div class="input-description">当已签到人数占总人数百分比达到此值时触发</div>
            </div>
          </div>

        <div class="form-group">
          <label for="poll_interval">轮询间隔</label>
          <input type="number" id="poll_interval" v-model="localForm.poll_interval" class="input" min="3" placeholder="3 - 60 秒 默认10" />
        </div>

        <div class="form-group">
          <label for="threshold_time">超时时间</label>
          <input type="number" id="threshold_time" v-model="localForm.threshold_time" class="input" min="30" placeholder="120 - 3600 秒 默认1200" />
          <small class="form-text">超时后不执行任何操作</small>
        </div>
      
        </div>
        
        <!-- <div class="form-group">
          <label for="threshold_time">超时时间（秒）</label>
          <div class="input-with-description">
            <input type="number" id="threshold_time" v-model="localForm.threshold_time" class="input" min="30" placeholder="默认：300" />
            <div class="input-description">超过此时间仍未达到阈值，则强制签到</div>
          </div>
        </div> -->
      </div>
      

      
      <!-- <div class="form-group">
        <label for="monitor_interval">监控间隔（秒）</label>
        <input type="number" id="monitor_interval" v-model="localForm.monitor_interval" class="input" min="10" placeholder="默认：30" />
        <small class="form-text">后台监控间隔</small>
      </div>
      
      <h4 class="mt-4 section-title">签到行为控制</h4>
      <div class="form-group">
        <label for="sign_delay">固定延迟（秒）</label>
        <input type="number" id="sign_delay" v-model="localForm.sign_delay" class="input" min="0" placeholder="默认：0" />
        <small class="form-text">签到前固定等待时间</small>
      </div>
      
      <div class="form-group">
        <label for="random_delay">随机延迟范围（秒）</label>
        <input type="number" id="random_delay" v-model="localForm.random_delay" class="input" min="0" placeholder="默认：0" />
        <small class="form-text">在固定延迟基础上，再随机等待0到此值的时间</small>
      </div> -->
    </div>
    
    <!-- 高级设置 -->
    <div v-show="activeTab === 'advanced'">
      <h4 class="section-title">通知设置</h4>
      <div class="settings-list">
        <div class="setting-item">
          <div>
            <div class="setting-label">检测到签到时通知</div>
            <div class="setting-desc">当系统检测到新的签到活动时收到通知</div>
          </div>
          <div class="toggle-switch">
            <input type="checkbox" id="notify_on_detect" v-model="localForm.notify_on_detect" />
            <label for="notify_on_detect"></label>
          </div>
        </div>
        
        <div class="setting-item">
          <div>
            <div class="setting-label">签到完成时通知</div>
            <div class="setting-desc">当签到成功完成后收到确认通知</div>
          </div>
          <div class="toggle-switch">
            <input type="checkbox" id="notify_on_sign" v-model="localForm.notify_on_sign" />
            <label for="notify_on_sign"></label>
          </div>
        </div>
      </div>
      
      <div v-if="notificationEnabled" class="alert alert-info mb-3">
          <div class="alert-title">需要设置推送通道</div>
          <div class="alert-content">您已开启通知功能，请至少填写一个推送通道Key</div>
              <div class="form-group">
          <label for="ios_bark_key">iOS Bark Key <span class="required-mark" v-if="notificationEnabled">*</span></label>
          <input 
            type="text" 
            id="ios_bark_key" 
            v-model="localForm.ios_bark_key" 
            class="input" 
            :class="{'input-error': notificationEnabled && !hasValidNotificationKey}"
            placeholder="用于iOS推送通知" 
          />
        </div>
        
        <div class="form-group">
          <label for="android_ntfy_key">Android Ntfy Key <span class="required-mark" v-if="notificationEnabled">*</span></label>
          <input 
            type="text" 
            id="android_ntfy_key" 
            v-model="localForm.android_ntfy_key" 
            class="input" 
            :class="{'input-error': notificationEnabled && !hasValidNotificationKey}"
            placeholder="用于Android推送通知" 
          />
        </div>
      </div>
      

      
      <!-- <h4 class="mt-4 section-title">自定义HTTP请求</h4>
      <div class="form-group">
        <label for="custom_headers">自定义请求头</label>
        <textarea 
          id="custom_headers" 
          v-model="customHeadersStr" 
          class="input" 
          rows="4" 
          placeholder="JSON格式，例如：&#10;{&#10;  &quot;User-Agent&quot;: &quot;Mozilla/5.0&quot;&#10;}"
          @blur="validateJsonField('customHeadersStr', 'custom_headers')"
        ></textarea>
        <div class="text-danger" v-if="jsonErrors.custom_headers">{{ jsonErrors.custom_headers }}</div>
      </div>
      
      <div class="form-group">
        <label for="custom_data">自定义请求数据</label>
        <textarea 
          id="custom_data" 
          v-model="customDataStr" 
          class="input" 
          rows="4" 
          placeholder="JSON格式，例如：&#10;{&#10;  &quot;customField&quot;: &quot;value&quot;&#10;}"
          @blur="validateJsonField('customDataStr', 'custom_data')"
        ></textarea>
        <div class="text-danger" v-if="jsonErrors.custom_data">{{ jsonErrors.custom_data }}</div>
      </div> -->
    </div>
    
    <div class="form-actions">
      <button type="button" class="btn btn-outline" @click="cancel">取消</button>
      <button type="button" class="btn btn-primary" :disabled="saving || hasJsonErrors" @click="save">
        {{ saving ? '保存中...' : '保存' }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfigForm',
  props: {
    form: {
      type: Object,
      required: true
    },
    saving: {
      type: Boolean,
      default: false
    },
    isFirstConfig: {
      type: Boolean,
      default: false
    }
  },
  data() {
    // 创建一个新对象
    const formCopy = JSON.parse(JSON.stringify(this.form));
    
    return {
      activeTab: 'basic',
      localForm: { 
        ...formCopy,
        is_default: this.isFirstConfig ? true : (formCopy.is_default || false)
      },
      customHeadersStr: '',
      customDataStr: '',
      usePercentThreshold: false,
      jsonErrors: {
        custom_headers: null,
        custom_data: null
      },
      isSubmitted: false
    }
  },
  computed: {
    hasJsonErrors() {
      return Object.values(this.jsonErrors).some(error => error !== null)
    },
    notificationEnabled() {
      return this.localForm.notify_on_detect || this.localForm.notify_on_sign
    },
    hasValidNotificationKey() {
      return !!(this.localForm.ios_bark_key || this.localForm.android_ntfy_key)
    },
    formIsValid() {
      if (this.hasJsonErrors) return false
      if (this.notificationEnabled && !this.hasValidNotificationKey) return false
      if (!this.localForm.is_default && !this.localForm.class_id) return false
      return true
    }
  },
  watch: {
    form: {
      handler(newVal) {
        // 创建深拷贝，避免直接引用同一对象
        const newValCopy = JSON.parse(JSON.stringify(newVal));
        
        this.localForm = { 
          ...newValCopy,
          is_default: this.isFirstConfig ? true : (newValCopy.is_default || false)
        };
        
        this.initJsonFields()
      },
      deep: true,
      immediate: true
    },
    'localForm.threshold_count': function(val) {
      if (val && val > 0) {
        this.usePercentThreshold = false
      }
    },
    'localForm.threshold_percent': function(val) {
      if (val && val > 0) {
        this.usePercentThreshold = true
      }
    }
  },
  methods: {
    initJsonFields() {
      // 初始化JSON字段的字符串表示
      this.customHeadersStr = this.localForm.custom_headers 
        ? JSON.stringify(this.localForm.custom_headers, null, 2) 
        : ''
      
      this.customDataStr = this.localForm.custom_data 
        ? JSON.stringify(this.localForm.custom_data, null, 2) 
        : ''
      
      // 初始化阈值选择
      this.usePercentThreshold = !!(this.localForm.threshold_percent && 
                               this.localForm.threshold_percent > 0)
    },
    
    validateJsonField(fieldStr, fieldName) {
      if (!this[fieldStr] || this[fieldStr].trim() === '') {
        this.jsonErrors[fieldName] = null
        this.localForm[fieldName] = null
        return true
      }
      
      try {
        const parsed = JSON.parse(this[fieldStr])
        this.localForm[fieldName] = parsed
        this.jsonErrors[fieldName] = null
        return true
      } catch (e) {
        this.jsonErrors[fieldName] = 'JSON格式错误: ' + e.message
        return false
      }
    },
    
    validateAllJsonFields() {
      let isValid = true
      isValid = this.validateJsonField('customHeadersStr', 'custom_headers') && isValid
      isValid = this.validateJsonField('customDataStr', 'custom_data') && isValid
      return isValid
    },
    
    save() {
      this.isSubmitted = true;
      
      if (!this.validateAllJsonFields()) {
        // 如果JSON验证失败，自动切换到高级设置标签
        this.activeTab = 'advanced'
        return
      }
      
      // 检查如果启用了通知，是否有至少一个推送key
      if (this.notificationEnabled && !this.hasValidNotificationKey) {
        this.activeTab = 'advanced'
        return
      }
      
      // 检查非默认配置是否有班级ID
      if (!this.localForm.is_default && !this.localForm.class_id) {
        this.activeTab = 'basic'
        return
      }
      
      // 处理阈值设置逻辑
      if (this.localForm.trigger_type === 'threshold') {
        if (this.usePercentThreshold) {
          this.localForm.threshold_count = 0
        } else {
          this.localForm.threshold_percent = 0
        }
      }
      
      this.$emit('save', this.localForm)
    },
    
    cancel() {
      this.isSubmitted = false;
      this.$emit('cancel')
    }
  },
  mounted() {
    this.initJsonFields()
  }
}
</script>

<style scoped>
.form-tabs {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--spacing-3);
  justify-content: space-between;
}

.tab-btn {
  background: none;
  border: none;
  padding: var(--spacing-2) var(--spacing-2);
  cursor: pointer;
  position: relative;
  color: var(--color-text-muted);
  transition: all 0.3s var(--transition-bounce);
  overflow: hidden;
  font-weight: 500;
  flex: 1;
}

.tab-btn:hover {
  color: var(--color-primary);
  transform: translateY(-1px);
}

.tab-btn:active {
  transform: translateY(1px);
}

.tab-btn.active {
  color: var(--color-primary);
  font-weight: 600;
}

.tab-btn::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 50%;
  width: 0;
  height: 2px;
  background-color: var(--color-primary);
  transition: all 0.3s var(--transition-bounce);
  transform: translateX(-50%);
}

.tab-btn.active::after {
  width: 100%;
}

.tab-btn:active::after {
  opacity: 0.7;
}

.section-title {
  font-size: 1rem;
  margin-bottom: var(--spacing-3);
  color: var(--color-primary);
  font-weight: 600;
  border-bottom: 1px dashed var(--color-border);
  padding-bottom: var(--spacing-1);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-2);
  margin-top: var(--spacing-4);
  padding-top: var(--spacing-3);
  border-top: 1px solid var(--color-border);
}

.form-row {
  display: flex;
  margin: 0 -10px;
}

.col-half {
  flex: 1;
  padding: 0 10px;
}

.radio-card-group {
  display: flex;
  gap: 12px;
  margin-bottom: var(--spacing-3);
}

.radio-card {
  flex: 1;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  padding: 15px;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.radio-card input {
  position: absolute;
  opacity: 0;
}

.radio-card:hover {
  border-color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.03);
}

.radio-card.active {
  border-color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.05);
  box-shadow: 0 4px 12px rgba(var(--color-primary-rgb), 0.1);
}

.radio-card-content {
  text-align: center;
}

.radio-card-title {
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.radio-card-desc {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.card-inner {
  background-color: rgba(var(--color-background-rgb), 0.5);
  border-radius: var(--border-radius);
  padding: 15px;
  margin-bottom: var(--spacing-3);
  border: 1px solid var(--color-border);
}

.card-inner h4 {
  font-size: 0.9rem;
  margin-bottom: 12px;
  color: var(--color-text);
  font-weight: 600;
}

.input-append {
  position: relative;
}

.input-append .input {
  padding-right: 40px;
}

.input-append-text {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  font-weight: 500;
}

.form-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.text-danger {
  color: var(--color-danger, #dc3545);
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.notification-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: var(--spacing-3);
}

@media (max-width: 576px) {
  .notification-buttons {
    flex-direction: column;
  }
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: var(--spacing-3);
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-radius: var(--border-radius);
  background-color: rgba(var(--color-background-rgb), 0.5);
  border: 1px solid var(--color-border);
}

.setting-label {
  font-weight: 500;
  margin-bottom: 4px;
}

.setting-desc {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
  flex-shrink: 0;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-switch label {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .3s;
  border-radius: 34px;
  margin: 0;
}

.toggle-switch label:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .3s;
  border-radius: 50%;
}

.toggle-switch input:checked + label {
  background-color: var(--color-primary);
}

.toggle-switch input:checked + label:before {
  transform: translateX(24px);
}

.toggle-switch input:focus + label {
  box-shadow: none;
}

.toggle-switch label:active,
.toggle-switch label:focus {
  outline: none;
  background-image: none !important;
}

.d-flex {
  display: flex;
}

.justify-content-between {
  justify-content: space-between;
}

.notification-btn {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background: none;
  transition: all 0.2s ease;
  cursor: pointer;
  text-align: left;
}

.notification-btn:hover {
  border-color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.03);
}

.notification-btn.active {
  border-color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.05);
  box-shadow: 0 2px 8px rgba(var(--color-primary-rgb), 0.1);
}

.notification-icon {
  margin-right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: rgba(var(--color-background-rgb), 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notification-btn.active .notification-icon {
  background-color: var(--color-primary);
  color: white;
}

.notification-text {
  flex: 1;
}

@media (max-width: 768px) {
  .form-tabs {
    overflow-x: auto;
    white-space: nowrap;
    padding-bottom: var(--spacing-1);
    flex-wrap: nowrap;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions button {
    width: 100%;
  }

  .radio-card-group {
    flex-direction: column;
  }

  .form-row {
    flex-direction: column;
  }

  .col-half {
    width: 100%;
    padding: 0;
  }
}

.required-mark {
  color: var(--color-danger, #dc3545);
  margin-left: 2px;
}

.input-error {
  border-color: var(--color-danger, #dc3545) !important;
}

.alert {
  padding: 12px 16px;
  border-radius: var(--border-radius);
  margin-bottom: 16px;
}

.alert-info {
  background-color: rgba(var(--color-primary-rgb), 0.1);
  border: 1px solid rgba(var(--color-primary-rgb), 0.2);
}

.alert-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.alert-content {
  font-size: 0.85rem;
}

.input-disabled {
  background-color: rgba(var(--color-background-rgb), 0.5);
  color: var(--color-text-muted);
  cursor: not-allowed;
}

.threshold-selector {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.form-check-inline {
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  padding: 6px 12px;
  border-radius: var(--border-radius);
  transition: all 0.25s ease;
  user-select: none;
}

.form-check-inline:hover {
  background-color: rgba(var(--color-background-rgb), 0.8);
}

.form-check-input {
  margin-right: 8px;
  cursor: pointer;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-border);
  border-radius: 50%;
  outline: none;
  transition: all 0.25s ease;
  position: relative;
  background-color: transparent;
}

.form-check-input:checked {
  border-color: var(--color-primary);
}

.form-check-input:checked::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-primary);
  animation: radio-pulse 0.3s ease-out;
}

@keyframes radio-pulse {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.form-check-input:focus {
  outline: none;
  box-shadow: none;
}

.form-check-input:active {
  transform: scale(0.9);
}

.form-check-input:focus-visible {
  outline: none;
  box-shadow: none;
}

.form-check-label {
  cursor: pointer;
  font-weight: 500;
  transition: all 0.25s ease;
}

.form-check-input:checked + .form-check-label {
  color: var(--color-primary);
}

.input-with-description {
  display: flex;
  flex-direction: column;
}

.input-description {
  margin-top: 4px;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

@media (min-width: 768px) {
  .input-with-description {
    flex-direction: row;
    align-items: center;
  }
  
  .input {
    width: 40%;
    min-width: 120px;
  }
  
  .input-append {
    width: 40%;
    min-width: 120px;
  }
  
  .input-description {
    margin-top: 0;
    margin-left: 12px;
    flex: 1;
  }
}
</style> 