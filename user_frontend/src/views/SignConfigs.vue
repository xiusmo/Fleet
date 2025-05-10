<template>
  <div class="sign-configs">
    <AppHeader />
    
    <div class="container main-content">
      <h1 class="page-title">签到配置</h1>
      
      <div class="config-controls mb-4 d-flex justify-content-between align-items-center">
        <div class="search-container">
          <input 
            type="search" 
            class="input" 
            placeholder="搜索配置..." 
            v-model="searchQuery" 
            autocomplete="off" 
          />
        </div>
        <button class="btn btn-primary" @click="openCreateModal">
          <span>+ 新建配置</span>
        </button>
      </div>
      
      <!-- 骨架屏加载动画 -->
      <div v-if="loading" class="config-skeleton" :class="{'fade-out': fadeOutSkeleton}">
        <div class="config-list">
          <div v-for="n in 3" :key="`config-skeleton-${n}`" class="skeleton-wrapper">
            <div class="config-card card skeleton-card">
              <div class="config-card-inner">
                <div class="config-header">
                  <div class="config-title">
                    <div class="title-wrapper">
                      <div class="skeleton-text skeleton-title"></div>
                      <div class="skeleton-badge"></div>
                    </div>
                    <div class="skeleton-text skeleton-class-id"></div>
                  </div>
                  <div class="config-actions">
                    <div class="skeleton-btn"></div>
                    <div class="skeleton-btn"></div>
                    <div class="skeleton-btn"></div>
                  </div>
                </div>
                <div class="config-details">
                  <div class="config-row">
                    <div class="skeleton-text skeleton-label"></div>
                    <div class="skeleton-text skeleton-value"></div>
                  </div>
                  <div class="config-row">
                    <div class="skeleton-text skeleton-label"></div>
                    <div class="skeleton-text skeleton-value"></div>
                  </div>
                  <div class="config-row">
                    <div class="skeleton-text skeleton-label"></div>
                    <div class="skeleton-text skeleton-value"></div>
                  </div>
                  <div class="config-row">
                    <div class="skeleton-text skeleton-label"></div>
                    <div class="skeleton-text skeleton-value"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else-if="configs.length === 0 && !loading" class="empty-state card py-5">
        <div class="text-center">
          <h3 class="mb-3">暂无签到配置</h3>
          <p class="text-muted mb-4">将默认为手动签到。</p>
        </div>
      </div>
      
      <div v-else class="config-list active-container">
        <!-- 加载详细信息的状态提示 -->
        <div v-if="loadingDetails" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载详细信息中...</p>
        </div>
        
        <!-- 配置列表 -->
        <transition-group name="config-list" tag="div" class="config-list-container">
          <div 
            v-for="config in sortedConfigs" 
            :key="`config-${config.uuid}`" 
            :id="config.uuid" 
            class="config-card card mb-4 config-list-item"
          >
            <div class="real-data-wrapper" :class="{'active': !loading}">
              <div class="config-card-inner">
                <div class="config-header">
                  <div class="config-title">
                    <div class="title-wrapper">
                      <h3>{{ config.name }}</h3>
                      <transition name="badge-fade">
                        <span v-if="config.is_default" class="default-badge">默认</span>
                      </transition>
                    </div>
                    <p v-if="config.class_id" class="text-muted">班级ID: {{ config.class_id }}</p>
                  </div>
                  <div class="config-actions">
                    <button class="action-btn edit-btn" @click="editConfig(config)" title="编辑">
                      <span class="icon">✏️</span>
                      <span class="action-text">编辑</span>
                    </button>
                    <button 
                      class="action-btn delete-btn" 
                      @click="confirmDeleteConfig(config)"
                      :disabled="isDeleting === config.uuid"
                      title="删除"
                    >
                      <span class="icon">🗑️</span>
                      <span class="action-text">{{ isDeleting === config.uuid ? '删除中...' : '删除' }}</span>
                    </button>
                    <button 
                      v-if="!config.is_default" 
                      class="action-btn default-btn" 
                      @click="setAsDefault(config)"
                      title="设为默认"
                    >
                      <span class="icon">⭐</span>
                      <span class="action-text">设为默认</span>
                    </button>
                  </div>
                </div>
                
                <!-- 配置详情展示 -->
                <transition name="details-fade">
                  <ConfigDetails 
                    v-if="detailedConfigs && detailedConfigs[config.uuid]" 
                    :config="detailedConfigs[config.uuid]"
                    :getTriggerTypeText="getTriggerTypeText"
                    class="config-details"
                  />
                </transition>
                
                <!-- 未加载详细信息时的占位显示 -->
                <div class="config-details skeleton-container" v-if="!detailedConfigs || !detailedConfigs[config.uuid]">
                  <div class="skeleton-loading">
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line skeleton-line-70"></div>
                    <div class="skeleton-line skeleton-line-90"></div>
                    <div class="skeleton-line skeleton-line-50"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </transition-group>
      </div>
    </div>
    
    <!-- 配置表单模态框 -->
    <ModalDialog 
      :show="showModal" 
      :title="isEditing ? '编辑配置' : '创建配置'"
      @close="closeModal"
    >
      <ConfigForm 
        :form="form" 
        :saving="saving"
        @save="saveConfig"
        @cancel="closeModal"
      />
    </ModalDialog>
    
    <!-- 确认删除模态框 -->
    <ModalDialog 
      :show="showDeleteConfirm" 
      title="确认删除"
      @close="closeDeleteConfirm"
    >
      <p>您确定要删除配置 "{{ configToDelete?.name }}" 吗？</p>
      <p class="text-muted">此操作不可撤销</p>
      
      <div class="form-actions">
        <button type="button" class="btn btn-outline" @click="closeDeleteConfirm">取消</button>
        <button type="button" class="btn btn-danger" @click="deleteConfig" :disabled="isDeleting">
          {{ isDeleting ? '删除中...' : '确认删除' }}
        </button>
      </div>
    </ModalDialog>
  </div>
</template>

<script>
import AppHeader from '../components/AppHeader.vue'
import ConfigDetails from '../components/ConfigDetails.vue'
import ConfigForm from '../components/ConfigForm.vue'
import ModalDialog from '../components/ModalDialog.vue'
import { configApi } from '../api'

export default {
  name: 'SignConfigsPage',
  components: {
    AppHeader,
    ConfigDetails,
    ConfigForm,
    ModalDialog
  },
  data() {
    return {
      configs: [],
      detailedConfigs: Object.create(null),
      waitForConfigsAndThenRedirect: null,
      loading: true,
      loadingDetails: false,
      saving: false,
      isDeleting: null,
      searchQuery: '',
      showModal: false,
      showDeleteConfirm: false,
      configToDelete: null,
      isEditing: false,
      form: this.getDefaultForm(),
      fadeOutSkeleton: false,
      dataReady: false,
      transitioningData: false
    }
  },
  computed: {
    filteredConfigs() {
      if (!this.searchQuery) return this.configs
      
      const query = this.searchQuery.toLowerCase()
      return this.configs.filter(config => {
        return (
          (config.name && config.name.toLowerCase().includes(query)) ||
          (config.class_id && config.class_id.toLowerCase().includes(query)) ||
          (this.detailedConfigs[config.uuid]?.course_id && 
           this.detailedConfigs[config.uuid].course_id.toLowerCase().includes(query))
        )
      })
    },
    
    sortedConfigs() {
      // 复制一份过滤后的配置列表进行排序
      return [...this.filteredConfigs].sort((a, b) => {
        // 默认配置置顶
        if (a.is_default && !b.is_default) return -1;
        if (!a.is_default && b.is_default) return 1;
        
        // 如果默认状态相同，则按名称排序，确保顺序稳定
        if (a.name && b.name) {
          return a.name.localeCompare(b.name);
        }
        
        // 最后按UUID排序，确保每次渲染的顺序一致
        return a.uuid.localeCompare(b.uuid);
      });
    }
  },
  methods: {
    getDefaultForm() {
      return {
        name: '',
        is_default: true,
        class_id: '',
        
        // 位置设置
        location_text: '',
        longitude: null,
        latitude: null,
        accuracy: 5.0,
        use_random_position: false,
        position_offset: 0.0001,
        
        // 照片设置
        use_random_photo: false,
        
        // 签到触发策略
        trigger_type: 'immediate',
        threshold_count: 1,
        threshold_percent: 0,
        threshold_time: 1200,
        poll_interval: 10,
        
        // 签到行为控制
        sign_delay: 0,
        random_delay: 0,
        
        // 监控间隔
        monitor_interval: 30,
        
        // 通知设置
        notify_on_detect: false,
        notify_on_sign: false,
        
        // 高级设置
        ios_bark_key: null,
        android_ntfy_key: null,
        custom_headers: null,
        custom_data: null
      }
    },
    
    async fetchConfigs() {
      this.loading = true
      try {
        const response = await configApi.getSignConfigs()
        
        // 确保response.data是数组
        if (response && response.data) {
          this.configs = Array.isArray(response.data) ? [...response.data] : []
        } else {
          this.configs = []
        }
        
        if(this.configs.length === 0) {
          this.fadeOutSkeleton = true
          setTimeout(() => {
            this.loading = false
          }, 300)
          return
        }
        
        this.loadingDetails = true
        
        // 并行获取每个配置的详细信息
        const detailPromises = this.configs.map(config => 
          configApi.getSignConfig(config.uuid)
            .then(response => ({ uuid: config.uuid, data: response.data }))
            .catch(() => ({ uuid: config.uuid, data: {...config} }))
        )
        
        // 一次性处理所有返回结果
        const results = await Promise.all(detailPromises)
        
        // 构建新的详细配置对象
        const newDetailedConfigs = Object.create(null)
        results.forEach(result => {
          newDetailedConfigs[result.uuid] = result.data
        })
        
        // 整体替换对象，确保反应式更新
        this.detailedConfigs = newDetailedConfigs
        
        // 平滑过渡: 先设置数据准备好标志
        this.dataReady = true
        
        // 先淡出骨架屏
        this.fadeOutSkeleton = true
        
        // 延迟隐藏骨架屏，让淡出动画有时间播放
        setTimeout(() => {
          this.loading = false
          this.loadingDetails = false
          
          // 延迟给真实数据添加active类，产生淡入效果
          setTimeout(() => {
            this.transitioningData = true
            
            // 给时间让CSS过渡动画完成
            setTimeout(() => {
              this.transitioningData = false
            }, 800)
          }, 50)
        }, 300)
      } catch (error) {
        console.error('获取配置失败', error)
        this.fadeOutSkeleton = true
        
        setTimeout(() => {
          this.loading = false
          this.loadingDetails = false
        }, 300)
      }
    },
    
    openCreateModal() {
      this.$router.push({
        path: this.$route.path,
        query: { action: 'create' }
      }).then(() => {
        this.isEditing = false
        this.form = this.getDefaultForm()
        this.showModal = true
      })
    },
    
    editConfig(config) {
      this.$router.push({
        path: this.$route.path,
        query: { action: 'edit', id: config.uuid }
      })
    },
    
    closeModal() {
      this.$router.push({ path: this.$route.path })
    },
    
    async saveConfig(formData) {
      this.saving = true
      
      try {
        // 清理无效数据
        const cleanedData = { ...formData }
        Object.keys(cleanedData).forEach(key => {
          if (cleanedData[key] === '' || cleanedData[key] === null) {
            delete cleanedData[key]
          }
        })
        
        let savedConfig
        
        if (this.isEditing) {
          // 检查UUID是否存在且有效
          if (!cleanedData.uuid) {
            throw new Error('配置UUID不存在或无效，无法更新配置')
          }
          
          // 使用更新API（PUT请求）来更新已有配置
          const response = await configApi.updateSignConfig(cleanedData.uuid, cleanedData)
          savedConfig = response.data
          
          // 更新详细配置缓存
          this.detailedConfigs[savedConfig.uuid] = savedConfig
          
          // 更新配置列表中的对应项
          const configIndex = this.configs.findIndex(c => c.uuid === savedConfig.uuid)
          if (configIndex !== -1) {
            this.configs.splice(configIndex, 1, savedConfig)
          }
        } else {
          // 使用创建API（POST请求）来新建配置
          const response = await configApi.createSignConfig(cleanedData)
          savedConfig = response.data
          
          // 更新缓存及列表
          this.detailedConfigs[savedConfig.uuid] = savedConfig
          this.configs.push(savedConfig)
        }
        
        // 如果设置了默认标志，更新其他配置的默认状态
        if (savedConfig.is_default) {
          // 创建新数组并更新
          const updatedConfigs = this.configs.map(c => {
            if (c.uuid !== savedConfig.uuid && c.is_default) {
              // 将其他默认配置更新为非默认
              const newConfig = {...c, is_default: false};
              
              // 同时更新详细配置
              if (this.detailedConfigs[c.uuid]) {
                this.detailedConfigs[c.uuid] = {
                  ...this.detailedConfigs[c.uuid],
                  is_default: false
                };
              }
              
              return newConfig;
            }
            return c;
          });
          
          // 对配置进行排序
          const sortedConfigs = [...updatedConfigs].sort((a, b) => {
            // 默认配置置顶
            if (a.is_default && !b.is_default) return -1;
            if (!a.is_default && b.is_default) return 1;
            
            // 如果默认状态相同，则按名称排序
            if (a.name && b.name) {
              return a.name.localeCompare(b.name);
            }
            
            // 最后按UUID排序
            return a.uuid.localeCompare(b.uuid);
          });
          
          // 完全替换configs数组
          this.configs = sortedConfigs;
        }
        
        // 清除URL查询参数
        this.$router.push({ path: this.$route.path })
      } catch (error) {
        console.error('保存配置失败', error)
        alert('保存失败: ' + (error.response?.data?.detail || '发生未知错误'))
      } finally {
        this.saving = false
      }
    },
    
    confirmDeleteConfig(config) {
      this.$router.push({
        path: this.$route.path,
        query: { action: 'delete', id: config.uuid }
      }).then(() => {
        this.configToDelete = config
        this.showDeleteConfirm = true
      })
    },
    
    closeDeleteConfirm() {
      this.$router.push({ path: this.$route.path })
    },
    
    async deleteConfig() {
      if (!this.configToDelete) return
      
      this.isDeleting = this.configToDelete.uuid
      
      try {
        await configApi.deleteSignConfig(this.configToDelete.uuid)
        
        // 从详细配置中也移除该配置
        delete this.detailedConfigs[this.configToDelete.uuid]
        
        // 从配置列表中移除
        const configIndex = this.configs.findIndex(c => c.uuid === this.configToDelete.uuid)
        if (configIndex !== -1) {
          this.configs.splice(configIndex, 1)
        }
        
        // 清除URL查询参数
        this.$router.push({ path: this.$route.path })
      } catch (error) {
        console.error('删除配置失败', error)
        alert('删除失败: ' + (error.response?.data?.detail || '发生未知错误'))
      } finally {
        this.isDeleting = null
        this.configToDelete = null
        this.showDeleteConfirm = false
      }
    },
    
    async setAsDefault(config) {
      try {
        const updateData = {
          uuid: config.uuid,
          is_default: true
        }
        
        await configApi.updateSignConfig(config.uuid, updateData)
        
        // 第一步：使用不可变更新更新对象属性
        const newConfigs = this.configs.map(c => {
          if (c.uuid === config.uuid) {
            // 默认值为true的新配置
            const newConfig = {...c, is_default: true};
            
            // 更新详细配置
            if (this.detailedConfigs[config.uuid]) {
              this.detailedConfigs[config.uuid] = {
                ...this.detailedConfigs[config.uuid], 
                is_default: true
              };
            }
            
            return newConfig;
          } 
          else if (c.is_default) {
            // 将之前的默认配置改为非默认
            const newConfig = {...c, is_default: false};
            
            // 更新详细配置
            if (this.detailedConfigs[c.uuid]) {
              this.detailedConfigs[c.uuid] = {
                ...this.detailedConfigs[c.uuid], 
                is_default: false
              };
            }
            
            return newConfig;
          }
          
          // 其他配置保持不变
          return c;
        });
        
        // 第二步：对原始数组进行重新排序
        const sortedConfigs = [...newConfigs].sort((a, b) => {
          // 默认配置置顶
          if (a.is_default && !b.is_default) return -1;
          if (!a.is_default && b.is_default) return 1;
          
          // 如果默认状态相同，则按名称排序
          if (a.name && b.name) {
            return a.name.localeCompare(b.name);
          }
          
          // 最后按UUID排序
          return a.uuid.localeCompare(b.uuid);
        });
        
        // 完全替换configs数组，确保Vue检测到原始数组顺序的变化
        this.configs = sortedConfigs;
      } catch (error) {
        console.error('设置默认配置失败', error)
        alert('设置失败: ' + (error.response?.data?.detail || '发生未知错误'))
      }
    },
    
    getTriggerTypeText(type) {
      switch (type) {
        case 'manual': return '手动触发'
        case 'auto': return '自动触发'
        case 'threshold': return '阈值触发'
        default: return type || '未设置'
      }
    },
    
    async fetchConfigDetail(uuid) {
      try {
        if (!uuid) {
          throw new Error('没有提供有效的UUID');
        }
        
        const response = await configApi.getSignConfig(uuid);
        const detailedConfig = response.data;
        
        // 确保配置有UUID
        if (!detailedConfig.uuid) {
          detailedConfig.uuid = uuid;
        }
        
        this.isEditing = true;
        this.form = JSON.parse(JSON.stringify(detailedConfig));
        this.showModal = true;
      } catch (error) {
        console.error('获取配置详情失败', error);
        alert('获取配置详情失败: ' + (error.response?.data?.detail || error.message || '发生未知错误'));
      }
    }
  },
  mounted() {
    this.fetchConfigs()
    
    if (this.$route.hash) {
      this.$nextTick(() => {
        const id = this.$route.hash.substring(1)
        const element = document.getElementById(id)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' })
        }
      })
    }
  },
  watch: {
    '$route': {
      immediate: true,
      deep: true,
      handler(newRoute) {
        if (newRoute.query.action === 'create') {
          this.isEditing = false;
          this.form = this.getDefaultForm();
          this.showModal = true;
        } else if (newRoute.query.action === 'edit' && newRoute.query.id) {
          // 确保ID不是undefined或空字符串
          if (!newRoute.query.id || newRoute.query.id === 'undefined') {
            console.error('无效的UUID:', newRoute.query.id);
            this.$router.push({ path: newRoute.path });
            return;
          }
          this.fetchConfigDetail(newRoute.query.id);
        } else if (newRoute.query.action === 'delete' && newRoute.query.id) {
          // 确保ID不是undefined或空字符串
          if (!newRoute.query.id || newRoute.query.id === 'undefined') {
            console.error('无效的UUID:', newRoute.query.id);
            this.$router.push({ path: newRoute.path });
            return;
          }
          this.$nextTick(() => {
            const configToDelete = this.configs.find(c => c.uuid === newRoute.query.id);
            if (configToDelete) {
              this.configToDelete = configToDelete;
              this.showDeleteConfirm = true;
            }
          });
        } else if (newRoute.hash && !Object.keys(newRoute.query).length) {
          const uuid = newRoute.hash.substring(1);
          if (this.configs.length === 0) {
            this.waitForConfigsAndThenRedirect = uuid;
          } else {
            this.$router.replace({
              path: this.$route.path,
              query: { action: 'edit', id: uuid }
            });
          }
        } else {
          if (this.showModal) this.showModal = false;
          if (this.showDeleteConfirm) this.showDeleteConfirm = false;
        }
      }
    },
    
    configs: {
      handler(newConfigs) {
        if (newConfigs.length > 0 && this.waitForConfigsAndThenRedirect) {
          const uuid = this.waitForConfigsAndThenRedirect;
          this.$router.replace({
            path: this.$route.path,
            query: { action: 'edit', id: uuid }
          });
          this.waitForConfigsAndThenRedirect = null;
        }
      }
    }
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

.search-container {
  max-width: 500px;
  width: 50%;
}

.search-container input[type="search"] {
  width: 100%;
  padding-left: 12px;
}

.search-container input[type="search"]::-webkit-search-cancel-button {
  cursor: pointer;
}

/* 配置列表容器 */
.config-list {
  position: relative;
  min-height: 200px;
  transition: opacity 0.4s ease-out;
  overflow: visible !important;
}

.config-list-container {
  display: flex;
  flex-direction: column;
  position: relative;
  width: 100%;
  /* 确保容器不会限制子元素的动画 */
  overflow: visible !important;
}

/* 列表项动画 */
.config-list-item {
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  width: 100%;
  will-change: transform;
  z-index: 1;
}

.config-list-enter-active,
.config-list-leave-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
  position: relative !important;
  z-index: 2 !important;
  backface-visibility: hidden;
  transform-style: preserve-3d;
  pointer-events: none;
  will-change: transform, opacity;
}

.config-list-enter-from,
.config-list-leave-to {
  opacity: 0 !important;
  transform: translateY(30px) !important;
}

.config-list-move {
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
  position: relative !important;
  z-index: 1 !important;
  backface-visibility: hidden;
  transform-style: preserve-3d;
  will-change: transform;
}

/* 加载状态 */
.loading-state {
  display: none;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin-bottom: 1rem;
  border: 3px solid rgba(var(--color-primary-rgb), 0.2);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 配置卡片 */
.config-card {
  padding: 0;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.config-card-inner {
  padding: var(--spacing-3);
}

.config-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12);
  border-color: rgba(var(--color-primary-rgb), 0.3);
}

/* 配置头部 */
.config-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-3);
}

.config-title {
  flex: 1;
  min-width: 0;
}

.title-wrapper {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.config-title h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  margin-right: var(--spacing-2);
}

.default-badge, .skeleton-badge {
  background-color: var(--color-primary);
  color: white;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
}

/* 配置详情部分 */
.config-details {
  margin-top: var(--spacing-3);
  border-top: 1px solid var(--color-border);
  padding-top: var(--spacing-3);
}

/* 详情动画 */
.details-fade-enter-active,
.details-fade-leave-active {
  transition: all 0.3s ease;
}

.details-fade-enter-from,
.details-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 骨架屏 */
.config-skeleton {
  position: relative;
  overflow: hidden;
  width: 100%;
}

.skeleton-wrapper, .config-card-wrapper {
  margin-bottom: 16px;
  transition: all 0.3s ease-out;
  width: 100%;
  min-width: 0;
}

.skeleton-card {
  background-color: var(--color-card-bg);
  padding: 0;
  animation: pulse 1.5s infinite ease-in-out;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(var(--color-shadow-rgb), 0.05);
}

.skeleton-text {
  background-color: var(--color-border);
  height: 16px;
  border-radius: 4px;
  margin-bottom: 8px;
}

.skeleton-title {
  width: 60%;
  height: 20px;
  margin: 0;
  margin-right: var(--spacing-2);
}

.skeleton-badge {
  width: 40px;
  height: 18px;
  background-color: var(--color-primary);
  opacity: 0.5;
  border-radius: 10px;
  flex-shrink: 0;
  padding: 0;
}

.skeleton-class-id {
  width: 40%;
  height: 16px;
  margin-top: 4px;
  margin-bottom: 0;
}

.skeleton-label {
  width: 30%;
  height: 14px;
}

.skeleton-value {
  width: 60%;
  height: 14px;
}

.skeleton-btn {
  width: 32px;
  height: 32px;
  background-color: var(--color-border);
  border-radius: 6px;
  margin-left: 8px;
}

@keyframes pulse {
  0% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.6;
  }
}

/* 徽章动画 */
.badge-fade-enter-active,
.badge-fade-leave-active {
  transition: all 0.3s ease;
}

.badge-fade-enter-from,
.badge-fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

/* 操作按钮 */
.config-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 6px;
  background-color: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: rgba(var(--color-background-rgb), 0.8);
  border-color: var(--color-primary);
  transform: translateY(-2px);
}

.action-btn:active {
  transform: translateY(0);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.icon {
  font-size: 1rem;
}

.edit-btn:hover {
  color: var(--color-primary);
}

.delete-btn:hover {
  color: var(--color-danger);
  border-color: var(--color-danger);
}

.default-btn:hover {
  color: #f59e0b;
  border-color: #f59e0b;
}

.empty-state {
  padding: var(--spacing-5);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-2);
  margin-top: var(--spacing-4);
  padding-top: var(--spacing-3);
  border-top: 1px solid var(--color-border);
}

@media (max-width: 768px) {
  .config-header {
    flex-direction: column;
  }
  
  .config-actions {
    margin-top: var(--spacing-2);
    justify-content: flex-start;
  }
  
  .action-text {
    display: none;
  }
  
  .action-btn {
    padding: 8px;
  }
  
  .icon {
    margin: 0;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions button {
    width: 100%;
  }
}

/* 数据加载过渡效果 */
.fade-out {
  opacity: 0;
  transition: opacity 0.3s ease-out;
}

.active-container {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from { 
    opacity: 0;
  }
  to { 
    opacity: 1; 
  }
}

.real-data-wrapper {
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.5s ease-out, transform 0.5s ease-out;
  will-change: opacity, transform;
  width: 100%;
  min-width: 0;
}

.real-data-wrapper.active {
  opacity: 1;
  transform: translateY(0);
}

/* 让真实数据一个接一个出现 */
.real-data-wrapper:nth-child(1) {
  transition-delay: 0.1s;
}

.real-data-wrapper:nth-child(2) {
  transition-delay: 0.2s;
}

.real-data-wrapper:nth-child(3) {
  transition-delay: 0.3s;
}

.real-data-wrapper:nth-child(4) {
  transition-delay: 0.4s;
}

.skeleton-card .config-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.skeleton-card .title-wrapper {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.skeleton-card .config-title {
  flex: 1;
  min-width: 0;
}

.skeleton-card .config-details {
  margin-top: var(--spacing-3);
  border-top: 1px solid var(--color-border);
  padding-top: var(--spacing-3);
}

.skeleton-card .config-row {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-bottom: var(--spacing-2);
}

.skeleton-card .skeleton-label {
  margin-right: var(--spacing-2);
}
</style>