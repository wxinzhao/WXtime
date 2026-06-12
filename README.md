# 微信定时消息管理系统

基于 **Python + wxauto** 的微信定时消息发送系统。

## 项目结构

```
pythom/
├── backend/
│   ├── app.py          # Flask API + wxauto 微信服务
│   ├── models/         # 数据库模型
│   └── requirements.txt
└── frontend/           # Vue 3 前端
```

## 技术栈

- **后端**: Python Flask + wxauto + MySQL + APScheduler
- **前端**: Vue 3 + Naive UI
- **数据库**: MySQL

## 安装

### 1. 安装 Python 依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 创建数据库

```sql
CREATE DATABASE wechat_message_system CHARACTER SET utf8mb4;
```

## 运行

### 1. 启动后端

```bash
cd backend
python app.py
```

后端运行在 http://localhost:5000

### 2. 启动前端

```bash
cd frontend
npm run dev
```

前端运行在 http://localhost:5173

## 功能

- 快速发送微信消息
- 查看消息发送记录
- 创建定时任务（Cron表达式）
- 系统状态监控

## 注意事项

- 微信客户端必须保持打开状态（非最小化）
- 建议使用专门的微信小号
- 系统限制：每小时最多50条，活跃时段9:00-21:00
