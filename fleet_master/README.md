# 分布式任务调度系统

这是一个基于FastAPI的分布式任务调度系统，支持任务提交、分发和状态跟踪。

## 功能特性

- 用户认证与授权（JWT）
- 任务提交与管理
- 工作节点管理
- 任务状态跟踪
- 管理员界面

## 技术栈

- FastAPI: Web框架
- SQLModel: ORM层
- PostgreSQL: 数据库
- Uvicorn: ASGI服务器
- Pydantic: 数据验证
- JWT: 身份认证

## 快速开始

### 环境准备

1. 确保已安装Python 3.11+
2. 安装PostgreSQL数据库
3. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

编辑`.env`文件，设置数据库连接和其他配置：

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/task_scheduler
SECRET_KEY=your_secret_key_here
```

### 运行

```bash
uvicorn app.main:app --reload
```

访问 http://localhost:8000/api/v1/docs 查看API文档。

## 项目结构

```
fleet_task_scheduler/
│
├── app/                  # 应用代码
│   ├── api/              # API路由
│   │   └── v1/           # API v1版本
│   │       ├── auth.py   # 认证相关API
│   │       ├── tasks.py  # 任务相关API
│   │       ├── workers.py # 工作节点相关API
│   │       └── admin.py  # 管理员相关API
│   │
│   ├── core/             # 核心功能
│   │   ├── config.py     # 配置管理
│   │   ├── security.py   # 安全相关
│   │   └── events.py     # 应用事件处理
│   │
│   ├── db/               # 数据库相关
│   │   ├── base.py       # 基础模型
│   │   └── session.py    # 数据库会话
│   │
│   ├── models/           # 数据模型
│   │   ├── user.py       # 用户模型
│   │   ├── task.py       # 任务模型
│   │   └── worker.py     # 工作节点模型
│   │
│   ├── schemas/          # 数据校验模式
│   │   ├── user.py       # 用户相关模式
│   │   ├── task.py       # 任务相关模式
│   │   └── worker.py     # 工作节点相关模式
│   │
│   ├── services/         # 业务逻辑服务
│   │   ├── auth.py       # 认证服务
│   │   ├── task.py       # 任务服务
│   │   └── worker.py     # 工作节点服务
│   │
│   └── main.py           # 应用入口
│
├── tests/                # 测试代码
│
├── .env                  # 环境变量
├── requirements.txt      # 依赖管理
└── README.md             # 项目说明
```

## API接口

系统提供以下主要API接口：

### 认证相关

- POST `/api/v1/auth/register`: 注册新用户
- POST `/api/v1/auth/login`: 用户登录
- GET `/api/v1/auth/me`: 获取当前用户信息

### 任务相关

- POST `/api/v1/tasks`: 创建新任务
- GET `/api/v1/tasks`: 获取当前用户的所有任务
- GET `/api/v1/tasks/{task_id}`: 获取任务详情
- POST `/api/v1/tasks/result`: 提交任务结果

### 工作节点相关

- POST `/api/v1/workers`: 注册新工作节点
- GET `/api/v1/workers`: 获取所有工作节点
- POST `/api/v1/workers/{worker_id}/heartbeat`: 更新工作节点心跳

### 管理员相关

- GET `/api/v1/admin/users`: 获取所有用户
- GET `/api/v1/admin/dashboard`: 获取仪表盘信息

## 从服务器开发

从服务器需要实现以下功能：

1. 定期向主服务器发送心跳
2. 从主服务器获取任务
3. 执行任务
4. 向主服务器报告任务状态和结果

## 许可证

MIT
