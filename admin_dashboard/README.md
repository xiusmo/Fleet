# 分布式任务调度系统 - 管理员控制台

这是分布式任务调度系统的管理员控制台前端项目，基于Vue 3 + Vite + Element Plus构建。

## 功能特性

- 🔐 管理员登录认证
- 📊 系统状态监控
- 👥 用户管理
- 🖥️ 工作节点管理
- 📝 系统日志查看
- 📢 公告管理
- 🔍 系统状态查看

## 开发环境设置

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 构建生产版本

```bash
# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 项目结构

```
src/
├── api/        # API接口定义
├── assets/     # 静态资源文件
├── components/ # 可复用组件
├── layouts/    # 布局组件
├── router/     # 路由配置
├── stores/     # Pinia状态管理
└── views/      # 页面视图组件
```

## 技术栈

- Vue 3 - 渐进式JavaScript框架
- Vite - 下一代前端工具
- Element Plus - 基于Vue 3的组件库
- Pinia - Vue的状态管理库
- Vue Router - Vue.js官方路由
- Axios - 基于Promise的HTTP客户端
