<template>
  <div class="qr-scanner-page">
    <div class="header">
      <div class="header-with-back">
        <button class="back-button" @click="goBack">
          <span class="back-icon">←</span> {{ hasHistory ? '返回上一级' : '返回主页' }}
        </button>
      </div>
    </div>

    <!-- 将video-wrapper移到这里，作为qr-scanner-page的直接子元素 -->
    <transition name="scanner">
      <div class="video-wrapper" v-if="isScanning">
        <video ref="video" class="camera-view"></video>
        <div class="scan-region-highlight-svg"></div>
      </div>
    </transition>

    <!-- HTTP环境警告 -->
    <div class="alert alert-warning" v-if="isHttpEnvironment">
      <h4>⚠️ 检测到HTTP环境</h4>
      <p>由于浏览器安全限制，摄像头功能在HTTP环境下不可用。您可以：</p>
      <ol>
        <li>使用下方的<strong>手动输入签到链接</strong>功能</li>
        <li>使用下方的<strong>上传二维码图片</strong>功能</li>
        <li>使用<strong>HTTPS</strong>访问本页面</li>
      </ol>
    </div>

    <div class="scanner-container" :class="{ 'expanded': isAlternativeExpanded, 'scanning': isScanning }">
      <transition-group name="controls" tag="div" class="controls">
        <button class="btn btn-block" key="start" @click="startScanning" v-if="!isScanning">
          <span class="icon">📷</span> 开始扫描
        </button>
        <button class="btn btn-block" key="test" @click="testCamera" v-if="!isScanning && !scanResult">
          <span class="icon">🔍</span> 测试摄像头
        </button>
        <button class="btn btn-danger btn-block" key="stop" @click="stopScanning" v-if="isScanning">
          停止扫描
        </button>
        <button class="btn btn-outline btn-block" key="flash" @click="toggleFlash" v-if="isScanning && hasFlash">
          {{ flashOn ? '关闭闪光灯 💡' : '打开闪光灯 🔦' }}
        </button>
      </transition-group>
    </div>

    <transition name="result">
      <div class="result-container" v-if="scanResult">
        <div class="card">
          <h3>最近扫描结果</h3>
          <div class="result-details">
            <div class="result-item">
              <span class="label">活动ID:</span>
              <span class="value">{{ scanResult.activity_id }}</span>
            </div>
            <div class="result-item">
              <span class="label">加密串:</span>
              <span class="value">{{ scanResult.enc }}</span>
            </div>
            <div class="result-item">
              <span class="label">状态:</span>
              <span class="value">{{ scanResult.status || '待处理' }}</span>
            </div>
            <div class="result-item" v-if="lastEncValue && lastEncValue !== scanResult.enc">
              <span class="label">前一次:</span>
              <span class="value">{{ lastEncValue.substring(0, 8) }}...</span>
            </div>
            <div class="result-item">
              <span class="label">检测时间:</span>
              <span class="value">{{ scanResult.lastDetectTime ? new Date(scanResult.lastDetectTime).toLocaleTimeString() : '-' }}</span>
            </div>
          </div>
        </div>
      </div>
    </transition>
    

    
    <AppSnackbar ref="snackbar" />

    <div class="sign-results" v-if="signResults && signResults.length > 0">
      <h3>签到结果详情</h3>
      <div class="results-card">
        <div v-for="(resultObj, resultIndex) in signResults" :key="resultIndex">
          <div v-for="(result, username) in resultObj" :key="username" class="result-user-item">
            <div class="username">{{ username }}</div>
            <div :class="['status', {'success': result.status === 'success', 'error': result.status === 'failed'}]">
              {{ result.status === 'success' ? '✅ 成功' : '❌ 失败' }}
            </div>
            <div class="message">{{ result.message }}</div>
          </div>
        </div>
      </div>
    </div>

        <!-- 添加折叠面板，包含替代输入方式 -->
        <div class="alternative-methods" :class="{ 'expanded': isAlternativeExpanded }">
      <div class="collapsible-header" @click="toggleAlternativeMethods">
        <h3>其他方式</h3>
        <span class="toggle-icon">▼</span>
      </div>
      
      <transition name="collapse">
        <div class="collapsible-content" v-show="isAlternativeExpanded">
          <div class="manual-input">
            <div class="card">
              <div class="form-group">
                <h4>手动输入签到链接</h4>
                <input 
                  type="text" 
                  id="manual_url" 
                  v-model="manualUrl" 
                  class="input" 
                  placeholder="https://mobilelearn.chaoxing.com/widget/sign/e?id=...&enc=..."
                />
              </div>
              <button class="btn btn-block" @click="handleManualInput" :disabled="!manualUrl">
                确认提交
              </button>
            </div>
          </div>
          
          <div class="card image-upload-card">
            <h4>上传二维码图片</h4>
            <p class="text-muted small">为提高识别率，请上传清晰的二维码。我不知道为什么直接上传识别率比实时扫描低这么多</p>
            
            <div class="upload-container">
              <input 
                type="file" 
                id="qr_image" 
                ref="fileInput"
                accept="image/*" 
                class="file-input" 
                @change="handleImageUpload" 
              />
              <label for="qr_image" class="btn btn-block">
                <span class="icon">📎</span> 选择图片
              </label>
              <span class="selected-file" v-if="selectedFile">
                已选择: {{ selectedFile.name }}
              </span>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- 添加帮助信息 -->
    <div class="help-section" v-if="!isScanning && !scanResult">
      <h3>使用帮助</h3>
      <div class="card">
        <h4>如果无法访问摄像头：</h4>
        <ul>
          <li>
            <strong>Safari/Chrome用户：</strong>
            点击地址栏左侧的ℹ️图标，确保摄像头权限已允许。
          </li>
          <li>
            <strong>移动端用户：</strong>
            前往设置→Safari/Chrome/浏览器→相机，确保摄像头权限已开启。
          </li>
        </ul>
        
        <h4>二维码扫描提示：</h4>
        <ul>
          <li>确保环境光线充足，二维码清晰可见。</li>
          <li>将二维码对准屏幕中央的框内，保持稳定。</li>
        </ul>
        
        <div class="share-section">
          <button class="btn btn-outline btn-block share-btn" @click="copyPageUrl">
            <span class="icon">🔗</span> 分享此页面
          </button>
          <span class="copy-success" v-if="copySuccess">✅ 链接与简介已复制</span>
        </div>
      </div>
    </div>

    <!-- Debug模式开关 -->
    <div class="debug-switch card">
      <div class="switch-header">
        <span class="switch-title">Debug模式</span>
        <label class="toggle-switch">
          <input type="checkbox" v-model="debugMode">
          <span class="toggle-slider"></span>
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import jsQR from 'jsqr'
import { qrCodeApi } from '../api'
import AppSnackbar from '../components/AppSnackbar.vue'
import { EventBus } from '../api'

export default {
  name: 'QrScanner',
  components: {
    AppSnackbar
  },
  data() {
    return {
      isScanning: false,
      scanResult: null,
      statusMessage: '',
      isSuccess: false,
      isError: false,
      signing: false,
      flashOn: false,
      hasFlash: false,
      manualUrl: '',
      signResults: null,
      isHttpEnvironment: false,
      
      // 扫描相关变量
      videoStream: null,
      canvasElement: null,
      canvasContext: null,
      scanInterval: null,
      scanAttempts: 0,
      maxScanAttempts: 40, // 2秒自动刷新
      lastDetectionTime: 0,
      detectionCooldown: 300, // 缩短冷却时间到300ms
      selectedFile: null,
      currentIp: '',
      currentPort: '',
      
      // 添加上一次的enc值记录
      lastEncValue: null,
      pendingSubmission: false,
      
      // 折叠面板状态
      isAlternativeExpanded: false,
      
      // 是否有历史记录
      hasHistory: false,
      
      // 视频透明度控制
      videoFullOpacity: true,
      
      // Debug模式控制
      debugMode: false,
      
      // 分享页面链接
      copySuccess: false,
    }
  },
  mounted() {
    // 检查是否为HTTP环境
    this.isHttpEnvironment = window.location.protocol === 'http:' && 
                           window.location.hostname !== 'localhost' && 
                           window.location.hostname !== '127.0.0.1';
    
    // 在HTTP环境下自动展开替代方式
    if (this.isHttpEnvironment) {
      this.isAlternativeExpanded = true;
    }
    
    // 检查是否有历史记录
    this.checkHasHistory();
    
    // 保存当前IP和端口号
    this.currentIp = window.location.hostname;
    this.currentPort = window.location.port;
    
    // 检查URL参数，如果有url参数，直接处理
    const urlParams = new URLSearchParams(window.location.search);
    const url = urlParams.get('url');
    if (url) {
      this.manualUrl = url;
      this.handleManualInput();
    }
    
    // 监听API错误
    EventBus.on('api-error', this.handleApiError);
  },
  beforeUnmount() {
    this.stopScanning();
    // 移除事件监听
    EventBus.off('api-error', this.handleApiError);
  },
  methods: {
    // 添加折叠面板切换方法
    toggleAlternativeMethods() {
      this.isAlternativeExpanded = !this.isAlternativeExpanded;
    },
    
    // 检查是否有历史记录
    checkHasHistory() {
      // 判断是否直接访问页面（没有来源页面）
      if (document.referrer) {
        // 有引用页面，表示不是直接访问
        this.hasHistory = true;
      } else {
        // 尝试使用history API检查
        try {
          this.hasHistory = window.history.length > 1;
        } catch(e) {
          console.error('检查历史记录失败:', e);
          this.hasHistory = false;
        }
      }
    },
    
    // 修改返回方法
    goBack() {
      // 如果正在扫描，则停止扫描而不是返回
      if (this.isScanning) {
        this.stopScanning();
        return;
      }
      
      // 如果已经有扫描结果，则重置扫描器
      if (this.scanResult) {
        this.resetScanner();
        return;
      }
      
      // 如果有历史记录，则返回上一级页面
      if (this.hasHistory) {
        this.$router.back();
      } else {
        // 没有历史记录，跳转到主页或登录页面
        this.$router.push('/login');
      }
    },
    
    async startScanning() {
      // 在HTTP环境下直接提示用户
      if (this.isHttpEnvironment) {
        this.showStatus('摄像头功能在HTTP环境下不可用，请使用手动输入或改用HTTPS', 'error', {
          label: '查看替代方式',
          callback: () => {
            this.isAlternativeExpanded = true;
          }
        });
        return;
      }
      
      this.isScanning = true;
      this.showStatus('正在请求相机权限...', 'info');
      
      try {
        // 首先检查浏览器支持
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          throw new Error('您的浏览器不支持摄像头访问，请尝试使用Chrome或Safari的最新版本');
        }
        
        // 检查是否在HTTPS环境下
        if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost') {
          this.showStatus('需要HTTPS安全环境才能访问摄像头', 'error');
          console.warn('需要HTTPS环境才能访问摄像头');
        }
        
        // 获取摄像头访问权限
        const constraints = {
          audio: false,
          video: {
            facingMode: 'environment', // 使用后置摄像头
            width: { ideal: 1280 },
            height: { ideal: 720 }
          }
        };
        
        // Safari和iOS特殊处理
        const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        
        if (isSafari || isIOS) {
          constraints.video.facingMode = {ideal: 'environment'};
          // 删除可能不支持的属性
          delete constraints.video.width;
          delete constraints.video.height;
        }
        
        console.log('请求摄像头权限...');
        this.videoStream = await navigator.mediaDevices.getUserMedia(constraints);
        console.log('摄像头权限获取成功！');
        
        // 检查是否支持闪光灯
        if (this.videoStream) {
          const track = this.videoStream.getVideoTracks()[0];
          this.hasFlash = 'torch' in track.getCapabilities();
        }
        
        const video = this.$refs.video;
        if (!video) {
          throw new Error('视频元素初始化失败');
        }
        
        video.srcObject = this.videoStream;
        video.setAttribute('playsinline', true); // iOS 支持内联播放
        video.setAttribute('autoplay', true);
        video.setAttribute('muted', true);
        
        // 视频加载后开始扫描过程
        video.onloadedmetadata = () => {
          video.play().catch(e => {
            console.error('视频播放失败', e);
            this.showStatus('视频播放失败: ' + e.message, 'error');
          });
          this.setupCanvas();
          this.startScanningLoop();
          this.showStatus('正在扫描...请将二维码对准框内', 'info');
        };
      } catch (error) {
        console.error('获取摄像头失败:', error);
        this.isScanning = false;
        
        // 详细区分错误类型
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
          this.showStatus('摄像头权限被拒绝，请在浏览器设置中允许摄像头访问', 'error');
          this.isAlternativeExpanded = true;
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
          this.showStatus('未检测到摄像头设备，请确认设备已连接', 'error');
          this.isAlternativeExpanded = true;
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
          this.showStatus('摄像头被其他应用占用，请关闭其他使用摄像头的应用', 'error');
          this.isAlternativeExpanded = true;
        } else if (error.name === 'OverconstrainedError' || error.name === 'ConstraintNotSatisfiedError') {
          this.showStatus('摄像头不满足要求参数，正在尝试替代选项...', 'info');
          // 尝试使用更宽松的约束
          this.startScanningWithFallback();
        } else if (error.name === 'SecurityError') {
          this.showStatus('安全错误: 需要在HTTPS环境下使用', 'error');
          this.isAlternativeExpanded = true;
        } else {
          this.showStatus('无法访问摄像头: ' + error.message, 'error');
          this.isAlternativeExpanded = true;
        }
      }
    },
    
    // 添加回退方法，使用更宽松的摄像头约束
    async startScanningWithFallback() {
      try {
        // 使用最基本的约束
        const constraints = {
          audio: false,
          video: true // 简单地请求任何可用的视频设备
        };
        
        this.videoStream = await navigator.mediaDevices.getUserMedia(constraints);
        
        const video = this.$refs.video;
        video.srcObject = this.videoStream;
        video.setAttribute('playsinline', true);
        video.setAttribute('autoplay', true);
        video.setAttribute('muted', true);
        
        video.onloadedmetadata = () => {
          video.play().catch(e => console.error('视频播放失败', e));
          this.setupCanvas();
          this.startScanningLoop();
          this.showStatus('正在扫描...使用备用摄像头模式', 'info');
        };
      } catch (error) {
        console.error('备用摄像头模式也失败:', error);
        this.isScanning = false;
        this.showStatus('无法访问任何摄像头，请检查设备和权限', 'error');
      }
    },
    
    setupCanvas() {
      // 创建一个离屏canvas用于图像处理
      this.canvasElement = document.createElement('canvas');
      this.canvasContext = this.canvasElement.getContext('2d', { willReadFrequently: true });
      
      // 设置canvas大小
      const video = this.$refs.video;
      this.canvasElement.width = video.videoWidth;
      this.canvasElement.height = video.videoHeight;
    },
    
    startScanningLoop() {
      // 每隔30ms尝试扫描一次，比原来的50ms更频繁
      this.scanInterval = setInterval(() => {
        this.scanVideoFrame();
        
        // 刷新计数
        this.scanAttempts++;
        if (this.scanAttempts >= this.maxScanAttempts) {
          // 重置扫描，模拟二维码刷新 - 2秒刷新
          this.showStatus('刷新扫描...', 'info');
          this.scanAttempts = 0;
        }
      }, 30);
    },
    
    scanVideoFrame() {
      if (!this.isScanning) return;
      
      const video = this.$refs.video;
      const canvas = this.canvasElement;
      const ctx = this.canvasContext;
      
      // 确保视频已经准备好
      if (video.readyState !== video.HAVE_ENOUGH_DATA) return;
      
      // 将视频帧绘制到canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // 获取图像数据
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      
      // 使用jsQR库解析二维码
      const code = jsQR(imageData.data, imageData.width, imageData.height, {
        inversionAttempts: 'dontInvert', // 不尝试反转颜色
      });
      
      // 如果检测到二维码
      if (code) {
        // 防止短时间内多次检测同一个码
        const now = Date.now();
        if (now - this.lastDetectionTime < this.detectionCooldown) return;
        this.lastDetectionTime = now;
        
        // 处理扫描结果
        this.handleScanResult(code.data);
      }
    },
    
    async handleScanResult(qrCodeUrl) {
      try {
        // 解析二维码URL
        const parseResult = qrCodeApi.parseQrCodeUrl(qrCodeUrl);
        
        if (!parseResult.valid) {
          this.showStatus('无效的二维码格式，请重新扫描', 'error');
          return;
        }
        
        // 提取签到参数
        const { activity_id, enc } = parseResult.data;
        
        if (!activity_id || !enc) {
          this.showStatus('二维码缺少必要参数，请确认是签到二维码', 'error');
          return;
        }
        
        // 检查enc是否发生变化
        const encChanged = this.lastEncValue !== enc;
        
        // 更新扫描结果
        this.scanResult = {
          activity_id,
          enc,
          url: qrCodeUrl,
          lastDetectTime: Date.now(),
          status: encChanged ? '检测到新的签到码' : '等待二维码刷新...'
        };
        
        // 判断是否需要提交签到
        if (encChanged && !this.pendingSubmission) {
          this.lastEncValue = enc;
          this.showStatus('检测到新的签到码，正在提交...', 'success');
          
          // 设置标志位，防止重复提交
          this.pendingSubmission = true;
          
          // 自动提交签到
          await this.autoSubmitSign();
          
          // 提交完成后恢复标志位
          this.pendingSubmission = false;
        } else if (!encChanged) {
          // 持续扫描但不提交
          console.log('二维码未变化，继续监控...');
        }
      } catch (error) {
        console.error('解析二维码失败:', error);
        this.showStatus('解析二维码失败: ' + error.message, 'error');
      }
    },
    
    stopScanning() {
      // 确保扫描循环先停止
      if (this.scanInterval) {
        clearInterval(this.scanInterval);
        this.scanInterval = null;
      }
      
      // 关闭闪光灯（如果开启）
      if (this.flashOn && this.videoStream) {
        try {
          const track = this.videoStream.getVideoTracks()[0];
          if (track && track.applyConstraints) {
            track.applyConstraints({
              advanced: [{ torch: false }]
            }).catch(err => console.error('无法关闭闪光灯:', err));
          }
          this.flashOn = false;
        } catch (e) {
          console.error('关闭闪光灯失败:', e);
        }
      }
      
      // 停止视频流
      if (this.videoStream) {
        try {
          const tracks = this.videoStream.getTracks();
          tracks.forEach(track => {
            try {
              track.stop();
            } catch (e) {
              console.error('停止轨道失败:', e);
            }
          });
          
          // 清理视频元素
          if (this.$refs.video) {
            this.$refs.video.srcObject = null;
          }
          
          this.videoStream = null;
        } catch (e) {
          console.error('停止视频流失败:', e);
        }
      }
      
      // 重置相关状态
      this.isScanning = false;
      this.hasFlash = false;
      this.scanAttempts = 0;
      this.lastDetectionTime = 0;
      
      // 输出日志以便调试
      console.log('摄像头已停止');
    },
    
    toggleFlash() {
      if (!this.videoStream) return;
      
      const track = this.videoStream.getVideoTracks()[0];
      
      // 切换闪光灯状态
      this.flashOn = !this.flashOn;
      
      try {
        track.applyConstraints({
          advanced: [{ torch: this.flashOn }]
        });
      } catch (error) {
        console.error('切换闪光灯失败:', error);
        this.showStatus('无法控制闪光灯', 'error');
        this.flashOn = false;
      }
    },
    
    handleManualInput() {
      if (!this.manualUrl) return;
      
      try {
        // 解析手动输入的URL
        const parseResult = qrCodeApi.parseQrCodeUrl(this.manualUrl);
        
        if (!parseResult.valid) {
          this.showStatus('无效的URL格式，请检查输入', 'error', {
            label: '清空重填',
            callback: () => {
              this.manualUrl = '';
              setTimeout(() => {
                document.getElementById('manual_url').focus();
              }, 100);
            }
          });
          return;
        }
        
        // 提取签到参数
        const { activity_id, enc } = parseResult.data;
        
        if (!activity_id || !enc) {
          this.showStatus('URL缺少必要参数，请确认是签到链接', 'error', {
            label: '清空重填',
            callback: () => {
              this.manualUrl = '';
              setTimeout(() => {
                document.getElementById('manual_url').focus();
              }, 100);
            }
          });
          return;
        }
        
        // 保存结果
        this.scanResult = {
          activity_id,
          enc,
          url: this.manualUrl
        };
        
        this.showStatus('解析URL成功，可以提交签到', 'success');
      } catch (error) {
        console.error('解析URL失败:', error);
        this.showStatus('解析URL失败: ' + error.message, 'error', {
          label: '重试',
          callback: () => {
            setTimeout(() => {
              document.getElementById('manual_url').focus();
            }, 100);
          }
        });
      }
    },
    
    showStatus(message, type = 'info', action = null) {
      this.statusMessage = message;
      this.isSuccess = type === 'success';
      this.isError = type === 'error';
      
      // 检查是否是重要通知（摄像头相关）或者是debugMode已开启
      const importantCameraMessages = [
        '摄像头功能在HTTP环境下不可用',
        '需要HTTPS安全环境才能访问摄像头',
        '摄像头权限被拒绝',
        '未检测到摄像头设备',
        '摄像头被其他应用占用',
        '摄像头不满足要求参数',
        '安全错误: 需要在HTTPS环境下使用',
        '无法访问摄像头',
        '浏览器不支持摄像头API', 
        '摄像头权限检查通过! 您可以开始扫描了',
        '二维码缺少必要参数，请确认是签到二维码',
        'URL缺少必要参数，请确认是签到链接',
        '未能识别二维码，请尝试更清晰的图片或直接使用摄像头扫描',
        '无效的二维码格式，请重新扫描'
      ];
      
      // 如果是重要通知或debugMode已开启，则显示snackbar
      const isImportantMessage = importantCameraMessages.some(keyword => message.includes(keyword));
      
      if (isImportantMessage || this.debugMode) {
        // 使用AppSnackbar组件显示消息
        // 确定消息类型
        let snackbarType;
        switch (type) {
          case 'error':
            snackbarType = 'client';
            break;
          case 'success':
            snackbarType = 'success';
            break;
          case 'warning':
            snackbarType = 'ratelimit';
            break;
          case 'info':
          default:
            snackbarType = 'info';
            break;
        }
        
        // 调用AppSnackbar的showError方法
        this.$refs.snackbar.showError({
          type: snackbarType,
          message: message,
          action: action
        });
      }
      
      // 对于成功消息，如果没有提供回调，设置自动清除状态
      if (type === 'success' && (!action || !action.callback)) {
        setTimeout(() => {
          if (this.statusMessage === message) {
            this.statusMessage = '';
            this.isSuccess = false;
          }
        }, 3000);
      }
    },
    
    resetScanner() {
      this.scanResult = null;
      this.statusMessage = '';
      this.signing = false;
      this.signResults = null;
      this.manualUrl = '';
      this.isSuccess = false;
      this.isError = false;
      this.lastEncValue = null;
      this.pendingSubmission = false;
      this.startScanning();
    },
    
    async submitSign() {
      if (!this.scanResult || this.signing) return;
      
      this.signing = true;
      this.showStatus('正在提交签到...', 'info');
      
      try {
        const response = await qrCodeApi.submitQrCodeSign({
          activity_id: this.scanResult.activity_id,
          enc: this.scanResult.enc
        });
        
        // API返回的是数组，每个元素是以用户名为键名的对象
        this.signResults = response.data;
        
        // 更新扫描结果状态
        if (this.scanResult) {
          this.scanResult.status = '签到已提交';
        }
        
        // 处理签到结果
        this.processSignResults();
      } catch (error) {
        console.error('提交签到失败:', error);
        const errorMsg = error.response?.data?.detail || '未知错误';
        const statusCode = error.response?.status || '';
        const url = error.config?.url || '';
        
        // 使用showStatus方法展示错误，这将触发snackbar显示
        this.showStatus(`签到失败: ${statusCode} ${url} - ${errorMsg}`, 'error');
        if (this.scanResult) this.scanResult.status = '提交失败';
        
        // 始终显示snackbar
        this.$refs.snackbar.showError({
          type: 'client',
          message: `请求错误: ${statusCode} ${url}`
        });
      } finally {
        this.signing = false;
      }
    },
    
    // 处理签到结果并返回是否有失败
    processSignResults() {
      const hasFailures = this.signResults.some(resultObj => {
        return Object.values(resultObj).some(result => result.status === 'failed');
      });
      
      if (hasFailures) {
        const allFailed = this.signResults.every(resultObj => {
          return Object.values(resultObj).every(result => result.status === 'failed');
        });
        
        if (allFailed) {
          this.showStatus('所有用户签到失败', 'error');
          if (this.scanResult) this.scanResult.status = '签到失败';
        } else {
          this.showStatus('部分用户签到成功，请查看详情', 'info');
          if (this.scanResult) this.scanResult.status = '部分成功';
        }
      } else {
        this.showStatus('所有用户签到成功！', 'success');
        if (this.scanResult) this.scanResult.status = '签到成功';
      }
      
      return hasFailures;
    },
    
    async testCamera() {
      this.showStatus('正在检查摄像头权限...', 'info');
      
      try {
        // 检查浏览器支持
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          throw new Error('浏览器不支持摄像头API');
        }
        
        // 请求最简单的视频访问
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: true
        });
        
        // 立即关闭流
        stream.getTracks().forEach(track => track.stop());
        
        this.showStatus('摄像头权限检查通过! 您可以开始扫描了', 'success');
        
        // 2秒后清除消息
        setTimeout(() => {
          if (this.statusMessage === '摄像头权限检查通过! 您可以开始扫描了') {
            this.statusMessage = '';
          }
        }, 2000);
      } catch (error) {
        console.error('摄像头权限检查失败:', error);
        
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
          this.showStatus('摄像头权限被拒绝，请检查浏览器设置', 'error', {
            label: '重试',
            callback: () => this.testCamera()
          });
        } else if (error.name === 'NotFoundError') {
          this.showStatus('未检测到摄像头设备', 'error');
        } else {
          this.showStatus('摄像头检查失败: ' + error.message, 'error', {
            label: '重试',
            callback: () => this.testCamera()
          });
        }
      }
    },
    
    // 处理图片上传
    async handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      this.selectedFile = file;
      this.showStatus('正在处理图片...', 'info');
      
      try {
        // 创建本地URL
        const imageUrl = URL.createObjectURL(file);
        
        // 加载图片
        const image = new Image();
        image.src = imageUrl;
        
        image.onload = () => {
          // 创建canvas并绘制图片
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          
          // 设置canvas尺寸为图片尺寸，但限制最大尺寸以提高性能
          const maxDimension = 1200;
          let width = image.width;
          let height = image.height;
          
          if (width > height && width > maxDimension) {
            height = Math.round((height * maxDimension) / width);
            width = maxDimension;
          } else if (height > maxDimension) {
            width = Math.round((width * maxDimension) / height);
            height = maxDimension;
          }
          
          canvas.width = width;
          canvas.height = height;
          
          // 绘制图片到canvas
          ctx.drawImage(image, 0, 0, width, height);
          
          // 先尝试直接解码
          this.tryDecodeQRFromCanvas(canvas, imageUrl, 'normal').then(success => {
            if (!success) {
              // 如果直接解码失败，尝试图像增强
              this.showStatus('首次识别未成功，正在尝试图像增强...', 'info');
              this.enhanceImageForQR(canvas).then(enhancedCanvas => {
                this.tryDecodeQRFromCanvas(enhancedCanvas, imageUrl, 'enhanced');
              });
            }
          });
        };
        
        image.onerror = () => {
          URL.revokeObjectURL(imageUrl);
          this.showStatus('图片加载失败', 'error', {
            label: '重试',
            callback: () => {
              this.$refs.fileInput.value = '';
              this.$refs.fileInput.click();
            }
          });
        };
      } catch (error) {
        console.error('处理图片失败:', error);
        this.showStatus('处理图片失败: ' + error.message, 'error', {
          label: '重试',
          callback: () => {
            this.$refs.fileInput.value = '';
            this.$refs.fileInput.click();
          }
        });
      }
    },
    
    // 新增方法：尝试从canvas解码二维码
    async tryDecodeQRFromCanvas(canvas, imageUrl, mode) {
      try {
        const ctx = canvas.getContext('2d');
        
        // 获取图像数据
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        
        // 尝试解码二维码，使用不同的参数
        let code = jsQR(imageData.data, imageData.width, imageData.height, {
          inversionAttempts: "attemptBoth", // 尝试黑白两种反转
        });
        
        if (!code && mode === 'enhanced') {
          // 尝试不同的扫描区域
          // 假设二维码在中央，尝试裁剪中央区域增加精度
          const centerSize = Math.min(canvas.width, canvas.height) * 0.7;
          const centerX = (canvas.width - centerSize) / 2;
          const centerY = (canvas.height - centerSize) / 2;
          
          try {
            const centerImageData = ctx.getImageData(centerX, centerY, centerSize, centerSize);
            code = jsQR(centerImageData.data, centerSize, centerSize, {
              inversionAttempts: "attemptBoth",
            });
          } catch (e) {
            console.error('中心区域提取失败:', e);
          }
        }
        
        // 释放URL对象
        if (imageUrl) URL.revokeObjectURL(imageUrl);
        
        if (code) {
          // 成功解析二维码
          this.showStatus('成功识别二维码！', 'success');
          this.handleScanResult(code.data);
          return true;
        } else if (mode === 'enhanced') {
          // 如果增强后还是识别失败
          this.showStatus('未能识别二维码，请尝试更清晰的图片或直接使用摄像头扫描', 'error', {
            label: '重新上传',
            callback: () => {
              this.$refs.fileInput.value = '';
              this.$refs.fileInput.click();
            }
          });
          return false;
        }
        
        return false;
      } catch (e) {
        console.error('二维码解析尝试失败:', e);
        return false;
      }
    },
    
    // 新增方法：增强图像以提高二维码识别率
    async enhanceImageForQR(sourceCanvas) {
      return new Promise(resolve => {
        const canvas = document.createElement('canvas');
        canvas.width = sourceCanvas.width;
        canvas.height = sourceCanvas.height;
        const ctx = canvas.getContext('2d');
        
        // 复制原始图像
        ctx.drawImage(sourceCanvas, 0, 0);
        
        // 获取图像数据
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        
        // 1. 增强对比度
        const contrast = 1.5; // 对比度增强系数
        const factor = (259 * (contrast + 255)) / (255 * (259 - contrast));
        
        for (let i = 0; i < data.length; i += 4) {
          // 红色通道
          data[i] = factor * (data[i] - 128) + 128;
          // 绿色通道
          data[i + 1] = factor * (data[i + 1] - 128) + 128;
          // 蓝色通道
          data[i + 2] = factor * (data[i + 2] - 128) + 128;
          // Alpha通道保持不变
        }
        
        // 2. 尝试二值化处理，帮助识别边界
        const threshold = 128;
        for (let i = 0; i < data.length; i += 4) {
          // 计算灰度值
          const gray = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
          
          // 应用阈值
          const val = gray > threshold ? 255 : 0;
          
          // 设置RGB通道
          data[i] = data[i + 1] = data[i + 2] = val;
        }
        
        // 应用处理后的图像数据
        ctx.putImageData(imageData, 0, 0);
        
        resolve(canvas);
      });
    },
    
    copyPageUrl() {
      const messageWithInstructions = `我正在使用xiusmo.com托管我的签到，你可以使用这个链接替我扫描签到二维码：xiusmo.com/qr-scanner`;
      this.copyToClipboard(messageWithInstructions);
    },
    
    // 复制到剪贴板
    copyToClipboard(text) {
      navigator.clipboard.writeText(text)
        .then(() => {
          this.copySuccess = true;
          this.showStatus('已复制到剪贴板', 'success');
          // 2秒后清除消息
          setTimeout(() => {
            this.copySuccess = false;
            if (this.statusMessage === '已复制到剪贴板') {
              this.statusMessage = '';
              this.isSuccess = false;
            }
          }, 2000);
          this.$refs.snackbar.show('链接已复制，可以分享给他人');
        })
        .catch(err => {
          console.error('复制失败:', err);
          this.showStatus('复制失败: ' + err.message, 'error');
          this.$refs.snackbar.show('复制失败，请手动复制地址栏链接');
        });
    },
    
    // 添加自动提交方法
    async autoSubmitSign() {
      if (!this.scanResult || this.signing) return;
      
      this.signing = true;
      
      try {
        const response = await qrCodeApi.submitQrCodeSign({
          activity_id: this.scanResult.activity_id,
          enc: this.scanResult.enc
        });
        
        // API返回的是数组，每个元素是以用户名为键名的对象
        this.signResults = response.data;
        
        // 更新扫描结果状态
        if (this.scanResult) {
          this.scanResult.status = '签到已提交';
        }
        
        // 处理签到结果
        this.processSignResults();
      } catch (error) {
        console.error('提交签到失败:', error);
        const errorMsg = error.response?.data?.detail || '未知错误';
        const statusCode = error.response?.status || '';
        const url = error.config?.url || '';
        
        // 使用showStatus方法展示错误，这将触发snackbar显示
        this.showStatus(`签到失败: ${statusCode} ${url} - ${errorMsg}`, 'error');
        if (this.scanResult) this.scanResult.status = '提交失败';
        
        // 始终显示snackbar
        this.$refs.snackbar.showError({
          type: 'client',
          message: `请求错误: ${statusCode} ${url}`
        });
      } finally {
        this.signing = false;
      }
    },
    
    // 切换视频容器透明度
    toggleVideoOpacity() {
      this.videoFullOpacity = !this.videoFullOpacity;
      
      // 获取视频容器元素
      const videoContainer = document.querySelector('.video-container');
      if (videoContainer) {
        if (this.videoFullOpacity) {
          videoContainer.style.opacity = '0.9';
        } else {
          videoContainer.style.opacity = '0.4';
        }
      }
    },
    
    // 处理API错误
    handleApiError(errorInfo) {
      // 如果是debugMode或请求与qr-code相关
      if (this.debugMode || (errorInfo.url && errorInfo.url.includes('qr-code'))) {
        this.$refs.snackbar.showError({
          type: 'client',
          message: `${errorInfo.status} ${errorInfo.url} - ${errorInfo.message}`
        });
      }
    },
  }
}
</script>

<style scoped>
.qr-scanner-page {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
  padding-bottom: 40px;
}

.header {
  text-align: center;
  margin-bottom: 20px;
}

.header-with-back {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin: 20px 0 50px;
}

.back-button {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(var(--color-primary-rgb, 0, 123, 255), 0.05);
  border: 1px solid rgba(var(--color-primary-rgb, 0, 123, 255), 0);
  display: flex;
  align-items: center;
  color: var(--color-primary);
  font-weight: 500;
  cursor: pointer;
  padding: 6px 12px;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  font-size: 0.95rem;
}

.back-button:hover {
  background-color: rgba(var(--color-primary-rgb, 0, 123, 255), 0.1);
  transform: translateY(-50%) translateX(0);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.12);
}

.back-icon {
  font-size: 1.3rem;
  margin-right: 6px;
  transition: transform 0.2s ease;
}

.back-button:hover .back-icon {
  transform: translateX(-3px);
}

/* 扫描器容器 */
.scanner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  min-height: 50px;
  transition: min-height 0.5s cubic-bezier(0.19, 1, 0.22, 1);
}

.video-wrapper {
  position: fixed;
  top: 30px;
  left: 50%;
  transform: translateX(-50%) translateY(0);
  width: 100%;
  max-width: 530px;
  height: 300px;
  z-index: 1000;
  will-change: transform, opacity;
  border-radius: 12px;
  overflow: hidden;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  background-color: rgba(0, 0, 0, 0.15);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(75, 75, 75, 0.2);
  transition: opacity 0.3s ease, box-shadow 0.3s ease;
  padding: 13px;

  -webkit-mask-image: 
    linear-gradient(to right, transparent 0, black 10px, black calc(100% - 10px), transparent 100%),
    linear-gradient(to bottom, transparent 0, black 10px, black calc(100% - 10px), transparent 100%);
  mask-image: 
    linear-gradient(to right, transparent 0, black 10px, black calc(100% - 10px), transparent 100%),
    linear-gradient(to bottom, transparent 0, black 10px, black calc(100% - 10px), transparent 100%);
  -webkit-mask-composite: destination-in;
  mask-composite: intersect;
}

.video-wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  /* background: radial-gradient(circle at center, transparent 0%, rgba(0, 0, 0, 0.4) 100%); */
  z-index: 1;
  pointer-events: none;
}

.camera-view {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
  opacity: 0.8;
  transition: opacity 0.3s ease;
  /* border: 1px solid rgba(255, 255, 255, 0.1); */
  position: relative;
  z-index: 2;
}

/* 扫描框 */
.scan-region-highlight-svg {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200px;
  height: 200px;
  transform: translate(-50%, -50%);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200' width='200' height='200' stroke='%2300AEFF' stroke-width='2' fill='none'%3E%3Cpath d='M30,10 L10,10 L10,30' /%3E%3Cpath d='M170,10 L190,10 L190,30' /%3E%3Cpath d='M190,170 L190,190 L170,190' /%3E%3Cpath d='M30,190 L10,190 L10,170' /%3E%3C/svg%3E");
  background-position: center center;
  background-repeat: no-repeat;
  background-size: 200px;
  pointer-events: none;
  z-index: 3;
}

/* 控制按钮 */
.controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 0;
  width: 100%;
  position: relative;
  z-index: 5;
  transition: margin-top 0.5s cubic-bezier(0.19, 1, 0.22, 1);
}

.scanner-container.scanning .controls {
  margin-top: 45%;
}

/* 按钮样式 */
.btn-block {
  transition: all 0.3s ease;
  width: 100%;
  display: block;
  text-align: center;
  background-color: var(--color-primary, #007bff);
  color: white;
  padding: 12px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  margin-bottom: 10px;
}

.btn-block:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  background-color: var(--color-primary-dark, #0056b3);
}

.btn-block:disabled {
  background-color: var(--color-primary-light, #8bbafe);
  cursor: not-allowed;
}

.btn-outline.btn-block {
  background-color: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.btn-outline.btn-block:hover {
  background-color: rgba(var(--color-primary-rgb, 0, 123, 255), 0.1);
}

.btn-danger.btn-block {
  background-color: var(--color-danger, #dc3545);
}

.btn-danger.btn-block:hover {
  background-color: var(--color-danger-dark, #bd2130);
}

.icon {
  margin-right: 8px;
}

/* 结果展示 */
.result-container {
  margin-top: 20px;
}

.card {
  background-color: var(--color-background);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-details {
  margin: 15px 0;
}

.result-item {
  display: flex;
  margin-bottom: 8px;
}

.label {
  font-weight: bold;
  width: 80px;
  flex-shrink: 0;
}

.value {
  word-break: break-all;
}

/* 签到结果 */
.sign-results {
  margin-top: 30px;
}

.results-card {
  background-color: var(--color-background);
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-user-item {
  padding: 10px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  flex-wrap: wrap;
}

.result-user-item:last-child {
  border-bottom: none;
}

.username {
  font-weight: bold;
  margin-right: 10px;
}

.status {
  margin-right: 10px;
}

.status.success {
  color: #28a745;
}

.status.error {
  color: #dc3545;
}

.message {
  color: var(--color-text-muted);
  flex: 1;
  min-width: 100%;
  margin-top: 5px;
}

/* 帮助信息 */
.help-section {
  margin-top: 30px;
}

.help-section h3 {
  margin-bottom: 15px;
}

.help-section h4 {
  margin: 15px 0 10px;
  color: var(--color-primary);
  font-size: 1rem;
}

.help-section ul {
  padding-left: 20px;
  margin-bottom: 15px;
}

.help-section li {
  margin-bottom: 8px;
  line-height: 1.5;
}

/* 图片上传 */
.image-upload-card {
  margin-top: 20px;
}

.upload-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
}

.file-input {
  position: absolute;
  opacity: 0;
  width: 0.1px;
  height: 0.1px;
  overflow: hidden;
}

.selected-file {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

/* 警告提示 */
.alert {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.alert-warning {
  background-color: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  color: #856404;
}

.alert h4 {
  margin: 0 0 10px;
  color: inherit;
}

.alert ol {
  margin-bottom: 0;
  padding-left: 20px;
}

.alert li {
  margin-bottom: 5px;
}

/* 折叠面板 */
.alternative-methods {
  margin: 20px 0;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.collapsible-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: rgba(var(--color-primary-rgb, 0, 123, 255), 0.05);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.collapsible-header:hover {
  background-color: rgba(var(--color-primary-rgb, 0, 123, 255), 0.1);
}

.collapsible-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--color-primary);
}

.toggle-icon {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  transition: transform 0.3s ease;
}

.expanded .toggle-icon {
  transform: rotate(180deg);
}

.collapsible-content {
  padding: 20px;
  transform-origin: top;
  will-change: transform, opacity, max-height;
}

/* 动画效果 */
.collapse-enter-active,
.collapse-leave-active {
  transition: max-height 0.3s ease, opacity 0.3s ease, transform 0.3s ease;
  max-height: 1000px;
  overflow: hidden;
}

.collapse-enter-from,
.collapse-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
  padding-top: 0;
  padding-bottom: 0;
}

.scanner-enter-active {
  transition: opacity 0.5s ease, transform 0.5s cubic-bezier(0.19, 1, 0.22, 1);
}

.scanner-leave-active {
  transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.19, 1, 0.22, 1);
}

.scanner-enter-from,
.scanner-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-100vh);
}

.controls-move,
.controls-enter-active,
.controls-leave-active {
  transition: all 0.5s cubic-bezier(0.19, 1, 0.22, 1) !important;
  will-change: opacity, transform;
  position: relative;
}

.controls-enter-from,
.controls-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.controls-leave-active {
  position: absolute;
  width: 100%;
}

/* Debug模式 */
.debug-switch {
  transition: all 0.3s ease;
  border: 1px solid var(--color-border);
  margin: 30px 0 200px;
}

.debug-switch:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.switch-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.switch-title {
  font-weight: 600;
  font-size: 1.1rem;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #e0e0e0;
  transition: .4s;
  border-radius: 24px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

input:checked + .toggle-slider {
  background-color: var(--color-primary);
}

input:checked + .toggle-slider:before {
  transform: translateX(24px);
}

/* 移动端适配 */
@media (max-width: 500px) {
  .video-wrapper {
    height: 300px;
    max-width: 95%;
    padding: 8px;
  }
  
  /* .video-wrapper::before {
    background: radial-gradient(circle at center, transparent 0%, rgba(0, 0, 0, 0.5) 100%);
  } */
  
  /* .scanner-container.scanning {
    min-height: 300px;
  } */
  
  .scanner-container.scanning .controls {
    margin-top: 250px;
  }
  
  .scan-region-highlight-svg {
    width: 160px;
    height: 160px;
    background-size: 160px;
  }
  
  .message {
    min-width: auto;
    margin-top: 0;
  }
}

.share-section {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.share-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.share-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.copy-success {
  margin-top: 0.5rem;
  color: var(--color-success);
  font-size: 0.9rem;
  opacity: 1;
  transition: opacity 0.3s ease;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style> 