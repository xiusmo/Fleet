<template>
  <div class="leave-note-editor">
    <AppHeader />
    
    <div class="container main-content">
      <h1 class="page-title">编辑请假条</h1>
      
      <!-- 模板选择区域 -->
      <div class="templates-section card mb-4" v-if="savedTemplates.length > 0">
        <h2 class="section-title">已保存的模板</h2>
        <div class="templates-list">
          <div v-for="template in savedTemplates" :key="template.id" class="template-item">
            <div class="template-info">
              <h3>{{ template.name }}</h3>
              <p class="text-muted">创建于: {{ formatDate(template.createdAt) }}</p>
            </div>
            <div class="template-actions">
              <button class="btn btn-sm btn-outline" @click="applyTemplate(template.id)">应用</button>
              <button class="btn btn-sm btn-outline-danger" @click="deleteTemplate(template.id)">删除</button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="form-container card">
        <div class="avatar-upload-section">
          <label>学生照片</label>
          <div class="avatar-container">
            <div class="avatar-preview" :style="avatarPreviewStyle" @click="changeAvatar">
              <span v-if="!formData.avatar" class="avatar-placeholder">点击上传头像</span>
              <img v-if="formData.avatar" :src="formData.avatar" alt="头像" class="avatar-image">
            </div>
            <input type="file" ref="avatarInput" accept="image/*" @change="handleAvatarUpload" class="avatar-input">
            <div class="avatar-actions" v-if="formData.avatar">
              <button class="btn btn-sm" @click="changeAvatar">更换</button>
              <button class="btn btn-sm btn-outline-danger" @click="removeAvatar">移除</button>
            </div>
          </div>
        </div>

            <div class="quick-date-buttons">
                <label>一键填写日期</label>
                <button class="btn btn-sm" @click="generateQuickLeave('today')">今天</button>
                <button class="btn btn-sm" @click="generateQuickLeave('tomorrow')">明天</button>
                <button class="btn btn-sm" @click="showDatePickerModal = true">自定义</button>
            </div>

        <div class="form-group">
          <label>开始时间</label>
          <div class="date-input-group">
            <input v-model="formData.startTime" type="datetime-local" class="form-control">
          </div>
        </div>
        
        <div class="form-group">
          <label>结束时间</label>
          <input v-model="formData.endTime" type="datetime-local" class="form-control">
        </div>
        
        <div class="form-group">
          <label>申请发起时间</label>
          <input v-model="formData.applyTime" type="datetime-local" class="form-control">
        </div>

        <div class="form-group">
          <label>审批时间</label>
          <input v-model="formData.approveTime" type="datetime-local" class="form-control">
        </div>

        <div class="form-group">
          <label>姓名</label>
          <input v-model="formData.name" type="text" class="form-control" placeholder="请输入姓名">
        </div>
        
        <div class="form-group">
          <label>学号</label>
          <input v-model="formData.studentId" type="text" class="form-control" placeholder="请输入学号">
        </div>
        
        <div class="form-group">
          <label>请假类型</label>
          <select v-model="formData.leaveType" class="form-control">
            <option value="事假">事假</option>
            <option value="病假">病假</option>
            <option value="实习">实习</option>
            <option value="其他">其他</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>学院</label>
          <input v-model="formData.college" type="text" class="form-control" placeholder="请输入学院">
        </div>
        
        <div class="form-group">
          <label>专业</label>
          <input v-model="formData.major" type="text" class="form-control" placeholder="请输入专业">
        </div>
        
        <div class="form-group">
          <label>班级</label>
          <input v-model="formData.className" type="text" class="form-control" placeholder="请输入班级">
        </div>
        
        <div class="form-group">
          <label>本人电话</label>
          <input v-model="formData.phone" type="text" class="form-control" placeholder="请输入本人电话">
        </div>
        
        <div class="form-group">
          <label>家长姓名</label>
          <input v-model="formData.parentName" type="text" class="form-control" placeholder="请输入家长姓名">
        </div>
        
        <div class="form-group">
          <label>家长电话</label>
          <input v-model="formData.parentPhone" type="text" class="form-control" placeholder="请输入家长电话">
        </div>
        
        <div class="form-group">
          <label>申请事由</label>
          <input v-model="formData.reason" type="text" class="form-control" placeholder="请输入申请事由">
        </div>
        
        <div class="form-group">
          <label>请假课程</label>
          <input v-model="formData.courses" type="text" class="form-control" placeholder="请输入请假课程">
        </div>
        
        <div class="form-group">
          <label>外出地点</label>
          <input v-model="formData.destination" type="text" class="form-control" placeholder="请输入外出地点">
        </div>
        
        <div class="form-group">
          <label>交通工具</label>
          <input v-model="formData.transportation" type="text" class="form-control" placeholder="请输入交通工具">
        </div>
        
        <div class="form-group">
          <label>家庭地址</label>
          <input v-model="formData.homeAddress" type="text" class="form-control" placeholder="请输入家庭地址">
        </div>
        
        <div class="form-group">
          <label>请假位置</label>
          <input v-model="formData.leavePosition" type="text" class="form-control" placeholder="请输入请假位置">
        </div>
        
        <div class="form-group">
          <label>销假位置</label>
          <input v-model="formData.returnPosition" type="text" class="form-control" placeholder="请输入销假位置">
        </div>
        
        <div class="form-group">
          <label>宿舍楼</label>
          <input v-model="formData.dormBuilding" type="text" class="form-control" placeholder="请输入宿舍楼">
        </div>
        
        <div class="form-group">
          <label>宿舍号</label>
          <input v-model="formData.dormRoom" type="text" class="form-control" placeholder="请输入宿舍号">
        </div>
        
        <div class="form-group">
          <label>审批人</label>
          <input v-model="formData.approver" type="text" class="form-control" placeholder="请输入审批人姓名和工号，如：[2029002778|李某]">
        </div>
        
        <!-- 请假状态相关信息 -->
        <div class="form-divider">请假状态与流程</div>
        
        <div class="form-group">
          <label>状态选择</label>
          <div class="status-options">
            <div class="status-option" :class="{ 'active': formData.status === 'approved' }" @click="formData.status = 'approved'">
              <img src="/leave_note/请销假_files/审批通过.png" alt="审批通过" class="status-icon">
              <span>审批通过</span>
            </div>
            <div class="status-option" :class="{ 'active': formData.status === 'returning' }" @click="formData.status = 'returning'">
              <img src="/leave_note/请销假_files/销假中.png" alt="销假中" class="status-icon">
              <span>销假中</span>
            </div>
            <div class="status-option" :class="{ 'active': formData.status === 'returned' }" @click="formData.status = 'returned'">
              <img src="/leave_note/请销假_files/已销假.png" alt="已销假" class="status-icon">
              <span>已销假</span>
            </div>
          </div>
        </div>
        
        <div class="form-actions">
          <button class="btn btn-outline" @click="saveAsTemplate">保存为模板</button>
          <button class="btn btn-primary" @click="generateLeaveNote">生成请假条</button>
        </div>
      </div>
    </div>
    
    <!-- 保存模板的模态框 -->
    <div class="modal-overlay" v-if="showSaveModal" @click.self="showSaveModal = false">
      <div class="modal-container">
        <div class="modal-header">
          <h3>保存为模板</h3>
          <button class="modal-close" @click="showSaveModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>模板名称</label>
            <input v-model="templateName" type="text" class="form-control" placeholder="请输入模板名称">
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showSaveModal = false">取消</button>
          <button class="btn btn-primary" @click="confirmSaveTemplate">保存</button>
        </div>
      </div>
    </div>
    
    <!-- 自定义日期选择模态框 -->
    <div class="modal-overlay" v-if="showDatePickerModal" @click.self="showDatePickerModal = false">
      <div class="modal-container">
        <div class="modal-header">
          <h3>选择请假日期</h3>
          <button class="modal-close" @click="showDatePickerModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>请假日期</label>
            <input v-model="customLeaveDate" type="date" class="form-control">
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showDatePickerModal = false">取消</button>
          <button class="btn btn-primary" @click="generateQuickLeave('custom')">生成</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AppHeader from '../components/AppHeader.vue'
import { formatDate } from '../utils/date'

export default {
  name: 'LeaveNoteEditor',
  components: {
    AppHeader
  },
  data() {
    return {
      formData: {
        name: '',
        studentId: '',
        leaveType: '事假',
        college: '',
        major: '',
        className: '',
        startTime: '',
        endTime: '',
        phone: '',
        parentName: '',
        parentPhone: '',
        reason: '',
        courses: '',
        destination: '',
        transportation: '',
        homeAddress: '',
        leavePosition: '',
        returnPosition: '',
        dormBuilding: '',
        dormRoom: '',
        approver: '',
        approveTime: '',
        avatar: '', // 头像数据（Base64格式）
        status: 'approved',
        applyTime: ''
      },
      savedTemplates: [], // 保存的模板列表
      showSaveModal: false,
      templateName: '', // 模板名称
      isCropModalVisible: false,
      tempAvatar: '', // 临时头像数据（Base64格式）
      showDatePickerModal: false, // 自定义日期选择模态框
      customLeaveDate: '', // 自定义请假日期
    }
  },
  computed: {
    // 头像预览样式，支持点击上传
    avatarPreviewStyle() {
      return {
        cursor: 'pointer',
        backgroundColor: this.formData.avatar ? 'transparent' : 'var(--color-input-bg)'
      };
    }
  },
  created() {
    // 确保在挂载时应用当前主题
    document.documentElement.setAttribute('data-theme', localStorage.getItem('theme') || 'light')
    
    // 初始化默认时间
    this.initializeDefaultTimes()
    
    // 加载保存的模板
    this.loadSavedTemplates()
    
    // 加载上次填写的数据
    this.loadLastFormData()
  },
  methods: {
    // 初始化默认时间
    initializeDefaultTimes() {
      const now = new Date()
      
      // 格式化为datetime-local格式: YYYY-MM-DDThh:mm
      const formatDateTimeLocal = (date) => {
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        
        return `${year}-${month}-${day}T${hours}:${minutes}`
      }
      
      // 设置默认时间
      if (!this.formData.startTime) {
        // 开始时间设为当前时间
        this.formData.startTime = formatDateTimeLocal(now)
      }
      
      if (!this.formData.endTime) {
        // 结束时间设为当前时间后1天
        const endTime = new Date(now)
        endTime.setDate(endTime.getDate() + 1)
        this.formData.endTime = formatDateTimeLocal(endTime)
      }
      
      if (!this.formData.applyTime) {
        // 申请时间设为当前时间前15分钟
        const applyTime = new Date(now)
        applyTime.setMinutes(applyTime.getMinutes() - 15)
        this.formData.applyTime = formatDateTimeLocal(applyTime)
      }
      
      if (!this.formData.approveTime) {
        // 审批时间设为当前时间前5分钟
        const approveTime = new Date(now)
        approveTime.setMinutes(approveTime.getMinutes() - 5)
        this.formData.approveTime = formatDateTimeLocal(approveTime)
      }
    },
    // 格式化日期
    formatDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    },
    
    // 保存到本地存储
    saveToLocalStorage() {
      // 保存当前表单数据作为最近使用的数据
      localStorage.setItem('lastLeaveNoteFormData', JSON.stringify(this.formData))
    },
    
    // 加载上次填写的数据
    loadLastFormData() {
      const savedData = localStorage.getItem('lastLeaveNoteFormData')
      if (savedData) {
        try {
          const parsedData = JSON.parse(savedData)
          this.formData = { ...this.formData, ...parsedData }
        } catch (e) {
          console.error('加载上次数据失败:', e)
        }
      }
    },
    
    // 保存为模板
    saveAsTemplate() {
      this.showSaveModal = true
    },
    
    // 确认保存模板
    confirmSaveTemplate() {
      if (!this.templateName) {
        this.templateName = '未命名模板'
      }
      
      // 获取已有模板
      const templates = JSON.parse(localStorage.getItem('leaveNoteTemplates') || '[]')
      
      // 添加新模板
      templates.push({
        id: Date.now().toString(),
        name: this.templateName,
        data: { ...this.formData },
        createdAt: new Date().toISOString()
      })
      
      // 保存到本地存储
      localStorage.setItem('leaveNoteTemplates', JSON.stringify(templates))
      
      // 更新模板列表
      this.savedTemplates = templates
      
      // 关闭模态框并重置
      this.showSaveModal = false
      this.templateName = ''
      
    },
    
    // 加载保存的模板
    loadSavedTemplates() {
      try {
        const templates = JSON.parse(localStorage.getItem('leaveNoteTemplates') || '[]')
        this.savedTemplates = templates
      } catch (e) {
        console.error('加载模板失败:', e)
        this.savedTemplates = []
      }
    },
    
    // 应用模板
    applyTemplate(templateId) {
      const template = this.savedTemplates.find(t => t.id === templateId)
      if (template && template.data) {
        this.formData = { ...this.formData, ...template.data }
      }
    },
    
    // 删除模板
    deleteTemplate(templateId) {
        const templates = this.savedTemplates.filter(t => t.id !== templateId)
        localStorage.setItem('leaveNoteTemplates', JSON.stringify(templates))
        this.savedTemplates = templates
    },
    
    // 处理头像上传
    handleAvatarUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // 检查文件大小（限制为1MB）
      if (file.size > 1024 * 1024) {
        // 提示用户图片将被压缩
        console.log('图片大小超过1MB，将自动压缩')
      }
      
      const reader = new FileReader()
      reader.onload = (e) => {
        // 加载图片进行压缩
        const img = new Image()
        img.onload = () => {
          // 压缩图片
          const compressedDataUrl = this.compressImage(img)
          
          // 保存到临时变量
          this.tempAvatar = compressedDataUrl
          
          // 直接应用图片（暂不使用裁剪功能）
          this.formData.avatar = this.tempAvatar
          this.saveToLocalStorage()
        }
        img.src = e.target.result
      }
      reader.readAsDataURL(file)
    },
    
    // 压缩图片
    compressImage(img) {
      const maxWidth = 300 // 最大宽度
      const maxHeight = 300 // 最大高度
      
      let width = img.width
      let height = img.height
      
      // 计算缩放比例
      if (width > height) {
        if (width > maxWidth) {
          height *= maxWidth / width
          width = maxWidth
        }
      } else {
        if (height > maxHeight) {
          width *= maxHeight / height
          height = maxHeight
        }
      }
      
      // 创建Canvas进行绘制和压缩
      const canvas = document.createElement('canvas')
      canvas.width = width
      canvas.height = height
      
      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, width, height)
      
      // 返回压缩后的DataURL，使用较低的质量
      return canvas.toDataURL('image/jpeg', 0.7)
    },
    
    // 点击更换头像
    changeAvatar() {
      this.$refs.avatarInput.click()
    },
    
    // 移除头像
    removeAvatar() {
      this.formData.avatar = ''
      this.$refs.avatarInput.value = ''
      this.saveToLocalStorage()
    },
    
    // 一键生成今天、明天或自定义日期的假条
    generateQuickLeave(dateType) {
      // 获取基准日期
      let leaveDate = new Date()
      
      if (dateType === 'tomorrow') {
        // 设置为明天
        leaveDate.setDate(leaveDate.getDate() + 1)
      } else if (dateType === 'custom') {
        // 如果是自定义日期且已选择
        if (this.customLeaveDate) {
          leaveDate = new Date(this.customLeaveDate)
          this.showDatePickerModal = false
        } else {
          // 如果未选择日期，提示并返回
          alert('请选择有效的日期')
          return
        }
      }
      
      // 设置开始时间为当天8点整
      const startTime = new Date(leaveDate)
      startTime.setHours(8, 0, 0, 0)
      
      // 设置结束时间为当天21点整
      const endTime = new Date(leaveDate)
      endTime.setHours(21, 0, 0, 0)
      
      // 生成前一天下午的随机申请时间（15:00 - 23:00之间）
      const applyDate = new Date(leaveDate)
      applyDate.setDate(applyDate.getDate() - 1)
      applyDate.setHours(
        15 + Math.floor(Math.random() * 8), // 小时：15-22点
        Math.floor(Math.random() * 60), // 分钟：0-59分
        Math.floor(Math.random() * 60) // 秒：0-59秒
      )
      
      // 生成申请当天晚上的随机审批时间（申请时间后2-5小时）
      const minApproveTime = new Date(applyDate.getTime() + (2 * 60 * 60 * 1000)) // 申请后至少2小时
      const maxApproveTime = new Date(applyDate.getTime() + (5 * 60 * 60 * 1000)) // 申请后最多5小时
      
      // 在最小和最大时间之间生成随机时间
      const approveTime = new Date(
        minApproveTime.getTime() + 
        Math.random() * (maxApproveTime.getTime() - minApproveTime.getTime())
      )
      
      // 格式化为datetime-local格式: YYYY-MM-DDThh:mm
      const formatDateTime = (date) => {
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        
        return `${year}-${month}-${day}T${hours}:${minutes}`
      }
      
      // 更新表单数据
      this.formData.startTime = formatDateTime(startTime)
      this.formData.endTime = formatDateTime(endTime)
      this.formData.applyTime = formatDateTime(applyDate)
      this.formData.approveTime = formatDateTime(approveTime)
      
      // 保存到本地存储
      this.saveToLocalStorage()
    },
    
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return ''
      
      const date = new Date(dateTimeStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      const seconds = String(date.getSeconds()).padStart(2, '0')
      
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    },
    
    calculateDays() {
      if (!this.formData.startTime || !this.formData.endTime) return ''
      
      const start = new Date(this.formData.startTime)
      const end = new Date(this.formData.endTime)
      const diffTime = Math.abs(end - start)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays < 1) {
        return '1天'
      } else {
        return `${diffDays}天`
      }
    },
    
    generateApplyTime() {
      const now = new Date()
      const year = now.getFullYear()
      const month = String(now.getMonth() + 1).padStart(2, '0')
      const day = String(now.getDate()).padStart(2, '0')
      const hours = String(now.getHours()).padStart(2, '0')
      const minutes = String(now.getMinutes()).padStart(2, '0')
      const seconds = String(now.getSeconds()).padStart(2, '0')
      
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    },
    
    // 修复资源路径
    fixResourcePaths(doc) {
      // 修复脚本路径
      const scripts = doc.querySelectorAll('script')
      scripts.forEach(script => {
        const src = script.getAttribute('src')
        if (src && src.startsWith('./请销假_files/')) {
          script.setAttribute('src', `/leave_note${src.substring(1)}`)
        }
      })
      
      // 修复样式表路径
      const links = doc.querySelectorAll('link')
      links.forEach(link => {
        const href = link.getAttribute('href')
        if (href && href.startsWith('./请销假_files/')) {
          link.setAttribute('href', `/leave_note${href.substring(1)}`)
        }
      })
      
      // 修复图片路径
      const images = doc.querySelectorAll('img')
      images.forEach(img => {
        const src = img.getAttribute('src')
        if (src && src.startsWith('./请销假_files/')) {
          img.setAttribute('src', `/leave_note${src.substring(1)}`)
        }
      })
    },
    
    // 添加折叠面板的点击事件
    fixCollapseEvents(doc) {
      // 为生成的文档添加点击折叠面板事件
      const collapseItems = doc.querySelectorAll('.van-collapse-item__title')
      
      // 添加折叠面板过渡动画样式
      const styleElement = doc.createElement('style')
      styleElement.textContent = `
        .van-collapse-item__wrapper {
          transition: height 0.3s ease-out, opacity 0.3s ease-out;
          overflow: hidden;
        }
        
        .van-collapse-item__title {
          cursor: pointer;
        }
        
        .van-collapse-item__title--expanded .van-cell__right-icon {
          transform: rotate(90deg);
        }
        
        .van-icon-arrow {
          transition: transform 0.3s;
        }
      `
      doc.head.appendChild(styleElement)
      
      const clickHandlerScript = doc.createElement('script')
      clickHandlerScript.textContent = `
        // 添加折叠面板点击事件处理
        document.addEventListener('DOMContentLoaded', function() {
          const collapseItems = document.querySelectorAll('.van-collapse-item__title');
          
          collapseItems.forEach(item => {
            item.addEventListener('click', function(e) {
              // 阻止其他点击事件
              e.preventDefault();
              e.stopPropagation();
              
              // 切换展开状态类
              const isExpanded = this.classList.contains('van-collapse-item__title--expanded');
              
              if (isExpanded) {
                this.classList.remove('van-collapse-item__title--expanded');
                this.setAttribute('aria-expanded', 'false');
              } else {
                this.classList.add('van-collapse-item__title--expanded');
                this.setAttribute('aria-expanded', 'true');
              }
              
              // 切换内容区域的显示
              const wrapper = this.nextElementSibling;
              if (wrapper && wrapper.classList.contains('van-collapse-item__wrapper')) {
                if (isExpanded) {
                  let height = wrapper.scrollHeight;
                  requestAnimationFrame(() => {
                    wrapper.style.height = height + 'px';
                    
                    requestAnimationFrame(() => {
                      wrapper.style.height = '0px';
                      wrapper.style.opacity = '0';
                      
                      // 等待过渡结束后隐藏
                      setTimeout(() => {
                        wrapper.style.display = 'none';
                      }, 300);
                    });
                  });
                } else {
                  wrapper.style.display = '';
                  wrapper.style.height = '0px';
                  wrapper.style.opacity = '0';
                  
                  requestAnimationFrame(() => {
                    wrapper.style.height = wrapper.scrollHeight + 'px';
                    wrapper.style.opacity = '1';
                    
                    // 过渡结束后移除固定高度，防止内容变化时出现问题
                    setTimeout(() => {
                      wrapper.style.height = '';
                    }, 300);
                  });
                }
              }
              
              // 箭头旋转
              const arrow = this.querySelector('.van-icon-arrow');
              if (arrow) {
                arrow.style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(90deg)';
              }
            });
          });
          
          // 初始状态设置（确保相应面板处于展开状态）
          setTimeout(() => {
            // 为申请内容和审批进度面板添加默认展开
            const collapseItems = document.querySelectorAll('.van-collapse-item');
            
            if (collapseItems.length >= 2) {
              // 申请内容(第二个面板)
              const secondPanel = collapseItems[1].querySelector('.van-collapse-item__title');
              if (secondPanel && !secondPanel.classList.contains('van-collapse-item__title--expanded')) {
                secondPanel.click();
              }
            }
            
            if (collapseItems.length >= 3) {
              // 审批进度(第三个面板)
              const thirdPanel = collapseItems[2].querySelector('.van-collapse-item__title');
              if (thirdPanel && !thirdPanel.classList.contains('van-collapse-item__title--expanded')) {
                thirdPanel.click();
              }
            }
          }, 100);
        });
      `;
      
      // 添加脚本到文档头部
      doc.head.appendChild(clickHandlerScript);
    },
    
    // 修复审批进度中的学生姓名和辅导员信息
    fixApprovalSteps(doc) {
      // 获取所有步骤
      const steps = doc.querySelectorAll('.van-step.van-step--vertical')
      
      if (steps && steps.length >= 2) {
        // 修复学生姓名步骤（第一个步骤）
        const studentStep = steps[0]
        if (studentStep && studentStep.hasAttribute('data-v-2886a3a2') && studentStep.getAttribute('data-v-2886a3a2') === '学生姓名') {
          // 更新为实际学生姓名
          studentStep.setAttribute('data-v-2886a3a2', this.formData.name)
        }
        
        // 修复发起申请步骤（第二个步骤）
        const applyStep = steps[1]
        if (applyStep) {
          // 修改发起申请文本，拼接学生姓名
          const titleElement = applyStep.querySelector('.van-step__title h3')
          if (titleElement) {
            titleElement.textContent = `${this.formData.name}发起申请`
          }
          
          // 更新申请时间
          const applyTimeElement = applyStep.querySelector('.van-step__title p')
          if (applyTimeElement) {
            applyTimeElement.textContent = this.formData.applyTime ? 
              this.formatDateTime(this.formData.applyTime) : 
              this.generateApplyTime()
          }
        }
        
        // 修复辅导员信息步骤（第三个步骤）
        const approverStep = steps[2]
        if (approverStep) {
          const approverElement = approverStep.querySelector('.van-step__title h3 span')
          if (approverElement) {
            approverElement.textContent = ` ${this.formData.approver || "[辅导员编号|辅导员姓名]"}`
          }
          
          // 修改审批时间
          const approveTimeElement = approverStep.querySelector('.van-step__title p:last-child')
          if (approveTimeElement) {
            approveTimeElement.textContent = this.formatDateTime(this.formData.approveTime)
          }
        }
      }
    },
    
    generateLeaveNote() {
      // 在生成请假条前自动保存当前数据
      this.saveToLocalStorage()

      // 先打开新窗口，防止 Safari 拦截
      const newWindow = window.open('', '_blank')
      if (!newWindow) {
        alert('请允许弹窗，否则无法生成请假条')
        return
      }
      // 显示加载提示
      newWindow.document.write('<p style="padding:2em;text-align:center;">正在生成请假条，请稍候...</p>')

      // 获取HTML模板
      fetch('/leave_note/请销假.html')
        .then(response => response.text())
        .then(html => {
          // 创建临时DOM来修改HTML内容
          const parser = new DOMParser()
          const doc = parser.parseFromString(html, 'text/html')

          // 添加App Header
          this.addAppHeader(doc)

          // 修改个人信息
          const nameElement = doc.querySelector('.nameWrap span:first-child')
          if (nameElement) {
            nameElement.innerHTML = `${this.formData.name} - ${this.formData.leaveType}<br data-v-2886a3a2="">`
          }

          const studentIdElement = doc.querySelector('.nameWrap span:last-child')
          if (studentIdElement) {
            studentIdElement.textContent = this.formData.studentId
          }

          // 修改头像
          if (this.formData.avatar) {
            // 查找头像显示区域（imgWrap下面的van-image）
            const imgWrap = doc.querySelector('.imgWrap')
            if (imgWrap) {
              const vanImage = imgWrap.querySelector('.van-image')
              if (vanImage) {
                // 替换van-image内部结构
                vanImage.innerHTML = ''

                // 创建新的图片元素
                const img = doc.createElement('img')
                img.src = this.formData.avatar
                img.style.width = '100%'
                img.style.height = '100%'
                img.style.objectFit = 'cover'
                img.style.borderRadius = '4px'
                img.style.border = '1px solid #eee'

                // 移除可能存在的错误图标
                const errorIcon = vanImage.querySelector('.van-image__error')
                if (errorIcon) {
                  errorIcon.remove()
                }

                vanImage.appendChild(img)

                // 移除错误类
                vanImage.classList.remove('van-image__error')

                // 确保显示
                vanImage.style.display = 'block'
                imgWrap.style.display = 'block'
              }
            }
          }

          // 修改申请人信息
          const infoSection = doc.querySelector('.van-collapse-item__content .list-item-info')
          if (infoSection && infoSection.parentElement) {
            const infoParent = infoSection.parentElement
            infoParent.innerHTML = `
              <div data-v-2886a3a2="" class="list-item-info">姓名：${this.formData.name}</div>
              <div data-v-2886a3a2="" class="list-item-info">学院：${this.formData.college}</div>
              <div data-v-2886a3a2="" class="list-item-info">专业：${this.formData.major}</div>
              <div data-v-2886a3a2="" class="list-item-info">班级：${this.formData.className}</div>
            `
          }

          // 修改申请内容
          const contentSections = doc.querySelectorAll('.van-collapse-item')
          if (contentSections && contentSections.length > 1) {
            const contentSection = contentSections[1].querySelector('.list-item-info')
            if (contentSection && contentSection.parentElement) {
              const contentParent = contentSection.parentElement
              contentParent.innerHTML = `
                <div data-v-2886a3a2="" class="list-item-info">开始时间：${this.formatDateTime(this.formData.startTime)}</div>
                <div data-v-2886a3a2="" class="list-item-info">结束时间：${this.formatDateTime(this.formData.endTime)}</div>
                <div data-v-2886a3a2="" class="list-item-info">本人电话：${this.formData.phone}</div>
                <div data-v-2886a3a2="" class="list-item-info">家长姓名：${this.formData.parentName}</div>
                <div data-v-2886a3a2="" class="list-item-info">家长电话：${this.formData.parentPhone}</div>
                <div data-v-2886a3a2="" class="list-item-info">申请事由：${this.formData.reason}</div>
                <div data-v-2886a3a2="" class="list-item-info">请假课程：${this.formData.courses}</div>
                <div data-v-2886a3a2="" class="list-item-info">外出地点：${this.formData.destination}</div>
                <div data-v-2886a3a2="" class="list-item-info">交通工具：${this.formData.transportation}</div>
                <div data-v-2886a3a2="" class="list-item-info">家庭地址：${this.formData.homeAddress}</div>
                <div data-v-2886a3a2="" class="list-item-info">申请时长：${this.calculateDays()}</div>
                <div data-v-2886a3a2="" class="list-item-info">附&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;件：<br data-v-2886a3a2=""><!----></div>
                <div data-v-2886a3a2="" class="list-item-info">请假位置：${this.formData.leavePosition}</div>
                <div data-v-2886a3a2="" class="list-item-info">销假位置：${this.formData.returnPosition}</div>
                <div data-v-2886a3a2="" class="list-item-info">宿舍楼：${this.formData.dormBuilding}</div>
                <div data-v-2886a3a2="" class="list-item-info">宿舍号：${this.formData.dormRoom}</div>
                <div data-v-2886a3a2="">
                  <div data-v-2886a3a2=""><img data-v-2886a3a2="" src="${this.getStatusImageSrc(this.formData.status)}" alt="" class="applyCard"></div>
                </div>
              `
            }
          }

          // 修改审批进度
          const approvalSections = doc.querySelectorAll('.van-step__title')
          if (approvalSections && approvalSections.length > 1) {
            // 修改申请时间
            const applyTimeElement = approvalSections[0].querySelector('p')
            if (applyTimeElement) {
              applyTimeElement.textContent = this.formData.applyTime ? 
                this.formatDateTime(this.formData.applyTime) : 
                this.generateApplyTime()
            }

            // 修改审批人信息
            const approverElement = approvalSections[1].querySelector('h3 span')
            if (approverElement) {
              approverElement.textContent = ` ${this.formData.approver}`
            }

            // 修改审批时间
            const approveTimeElement = approvalSections[1].querySelectorAll('p')[2]
            if (approveTimeElement) {
              approveTimeElement.textContent = this.formatDateTime(this.formData.approveTime)
            }

            // 根据状态添加额外的步骤
            const stepsContainer = doc.querySelector('.van-steps__items')
            if (stepsContainer && (this.formData.status === 'returning' || this.formData.status === 'returned')) {
              // 创建销假中或已销假的步骤
              const newStep = doc.createElement('div')
              newStep.className = 'van-hairline van-step van-step--vertical'

              const statusText = this.formData.status === 'returning' ? '销假中' : '已销假'
              const statusTime = this.formatDateTime(new Date())

              newStep.innerHTML = `
                <div class="van-step__title">
                  <i data-v-2886a3a2="" class="blue van-icon van-icon-checked" style="position: absolute; left: -14px; top: 10px; z-index: 10;"></i>
                  <h3 data-v-2886a3a2="" class="blue">状态更新</h3>
                  <p data-v-2886a3a2="" class="blue">${statusText}</p>
                  <p data-v-2886a3a2="" class="blue"></p>
                  <p data-v-2886a3a2="" class="blue">${statusTime}</p>
                </div>
                <div class="van-step__circle-container">
                  <i class="van-icon van-icon-checked van-step__icon"></i>
                </div>
                <div class="van-step__line"></div>
              `

              stepsContainer.appendChild(newStep)
            }
          }

          // 添加状态图标
          if (this.formData.status) {
            const statusImageSrc = this.getStatusImageSrc(this.formData.status)
            if (statusImageSrc) {
              // 找到申请卡片图标位置
              const applyCard = doc.querySelector('.applyCard')
              if (applyCard) {
                // 替换图标
                applyCard.src = statusImageSrc
              }
            }
          }

          // 修复资源路径
          this.fixResourcePaths(doc)

          // 修复折叠面板点击事件
          this.fixCollapseEvents(doc)

          // 修复审批进度中的学生姓名和辅导员信息
          this.fixApprovalSteps(doc)

          // 写入新窗口内容
          newWindow.document.open()
          newWindow.document.write(doc.documentElement.outerHTML)
          newWindow.document.close()
        })
        .catch(error => {
          newWindow.document.body.innerHTML = '<p style="color:red;">生成失败，请重试</p>'
          console.error('生成请假条失败:', error)
          alert('生成请假条失败，请重试')
        })
    },
    
    // 获取状态图标路径
    getStatusImageSrc(status) {
      switch (status) {
        case 'approved':
          return '/leave_note/请销假_files/审批通过.png';
        case 'returning':
          return '/leave_note/请销假_files/销假中.png';
        case 'returned':
          return '/leave_note/请销假_files/已销假.png';
        default:
          return '/leave_note/请销假_files/审批通过.png';
      }
    },
    
    // 显示头像裁剪模态框
    showCropModal() {
      this.isCropModalVisible = true
    },
    
    // 取消裁剪
    cancelCrop() {
      this.isCropModalVisible = false
    },
    
    // 确认裁剪
    confirmCrop() {
      // 处理裁剪后的头像
      this.formData.avatar = this.tempAvatar
      this.saveToLocalStorage()
      this.isCropModalVisible = false
    },
    
    // 添加App Header
    addAppHeader(doc) {
      // 获取body元素
      const body = doc.body
      const firstChild = body.firstChild
      
      // 创建App Header
      const appHeader = doc.createElement('div')
      appHeader.className = 'app-header'
      appHeader.innerHTML = `
        <div class="header-left">
          <div class="back-button">
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path fill="white" d="M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z"></path>
            </svg>
          </div>
        </div>
        <div class="header-title">请销假</div>
        <div class="header-right">
          <div class="close-button">
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path fill="white" d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"></path>
            </svg>
          </div>
          <div class="menu-button">
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path fill="white" d="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z"></path>
            </svg>
          </div>
        </div>
      `
      
      // 在body开始位置插入header
      body.insertBefore(appHeader, firstChild)
      
      // 添加Header样式
      const style = doc.createElement('style')
      style.textContent = `
        .app-header {
          position: sticky;
          top: 0;
          left: 0;
          right: 0;
          height: 56px;
          background-color: #5b9afc;
          color: white;
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0 16px;
          z-index: 100;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .header-left, .header-right {
          display: flex;
          align-items: center;
        }
        
        .header-title {
          font-size: 20px;
          font-weight: 500;
        }
        
        .back-button, .close-button, .menu-button {
          width: 36px;
          height: 36px;
          display: flex;
          justify-content: center;
          align-items: center;
          cursor: pointer;
        }
        
        .header-right {
          gap: 8px;
        }
        
        body {
          margin: 0;
          padding: 0;
        }
      `
      doc.head.appendChild(style)
    },
  }
}
</script>

<style>
.leave-note-editor {
  min-height: 100vh;
  background-color: var(--color-background);
}

.main-content {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  margin-bottom: 20px;
  color: var(--color-text);
  font-size: 24px;
}

.form-container {
  background: var(--color-card-bg);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 头像上传相关样式 */
.avatar-upload-section {
  margin-bottom: 20px;
}

.avatar-upload-section label {
  display: block;
  margin-bottom: 10px;
  font-weight: 500;
  color: var(--color-text);
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.avatar-preview {
  width: 120px;
  height: 120px;
  border-radius: 5px;
  border: 2px dashed var(--color-border);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  position: relative;
}

.avatar-placeholder {
  color: var(--color-text-muted);
  font-size: 14px;
  text-align: center;
  padding: 10px;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-input {
  display: none;
}

.avatar-actions {
  display: flex;
  gap: 10px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: var(--color-text);
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  background-color: var(--color-input-bg);
  color: var(--color-text);
}

.form-control:focus {
  border-color: var(--color-primary);
  outline: none;
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.2);
}

.form-actions {
  margin-top: 20px;
  text-align: center;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}


.btn-outline {
  background-color: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.btn-outline:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-outline-danger {
  background-color: transparent;
  border: 1px solid var(--color-danger);
  color: var(--color-danger);
}

.btn-outline-danger:hover {
  background-color: var(--color-danger);
  color: white;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 14px;
}

.card {
  background: var(--color-card-bg);
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.mb-4 {
  margin-bottom: 20px;
}

/* 模板列表样式 */
.templates-section {
  padding: 20px;
}

.section-title {
  margin-bottom: 15px;
  font-size: 20px;
  color: var(--color-text);
}

.templates-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.template-item {
  background-color: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.template-info h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: var(--color-text);
}

.text-muted {
  color: var(--color-text-muted);
  font-size: 12px;
}

.template-actions {
  display: flex;
  justify-content: space-between;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-container {
  background-color: var(--color-card-bg);
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--color-text);
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--color-text-muted);
}

.modal-close:hover {
  color: var(--color-text);
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 深色模式适配 */
[data-theme='dark'] .leave-note-editor {
  background-color: var(--color-background);
}

[data-theme='dark'] .form-container,
[data-theme='dark'] .card,
[data-theme='dark'] .template-item,
[data-theme='dark'] .modal-container {
  background: var(--color-card-bg);
}

[data-theme='dark'] .form-control {
  background-color: var(--color-input-bg);
  color: var(--color-text);
  border-color: var(--color-border);
}

[data-theme='dark'] .btn-primary {
  background-color: var(--color-primary);
}


[data-theme='dark'] .btn-outline {
  border-color: var(--color-border);
  color: var(--color-text);
}

[data-theme='dark'] .btn-outline:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

/* 裁剪相关样式 */
.crop-modal {
  width: 500px;
  max-width: 90%;
}

.avatar-crop-container {
  width: 100%;
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  background-color: var(--color-input-bg);
  border-radius: 4px;
}

.crop-image {
  max-width: 100%;
  max-height: 100%;
}

/* 表单分割线 */
.form-divider {
  margin: 20px 0 15px;
  padding-bottom: 8px;
  font-size: 18px;
  font-weight: 500;
  color: var(--color-primary);
  border-bottom: 1px solid var(--color-border);
}

/* 状态选择样式 */
.status-options {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 10px;
}

.status-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  padding: 10px;
  border: 2px solid var(--color-border);
  border-radius: 8px;
  transition: all 0.3s ease;
  width: 100px;
}

.status-option:hover {
  border-color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.05);
}

.status-option.active {
  border-color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.1);
}

.status-icon {
  width: 60px;
  height: 60px;
  margin-bottom: 10px;
  object-fit: contain;
}

.status-option span {
  font-size: 14px;
  color: var(--color-text);
}

.status-option .status-text {
  margin-top: 5px;
  font-size: 12px;
}

.applyCard {
  width: auto;
  height: 25px;
  margin-top: 5px;
}

/* Responsive styling */
@media (max-width: 768px) {
  /* ... existing code ... */
}

.date-input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-date-buttons {
  display: flex;
  gap: 8px;
  padding-left: 10px;
}

.quick-date-buttons .btn {
  font-size: 13px;
  padding: 4px 10px;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  background-color: var(--color-card-bg);
}

.quick-date-buttons .btn:hover {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}
</style> 