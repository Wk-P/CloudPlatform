# CloudPlatform - 云资源管理平台

[![Django](https://img.shields.io/badge/Django-5.1.7-green.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.5-blue.svg)](https://vuejs.org/)
[![Python](https://img.shields.io/badge/Python-3.12-yellow.svg)](https://www.python.org/)

## 📖 项目简介

CloudPlatform 是一个综合性云资源可视化管理系统，专为高效管理 Kubernetes、OpenStack 等云服务平台而设计。系统提供无缝的资源控制、管理和监控能力，并集成智能防火墙以检测和缓解异常外部流量。

### ✨ 核心功能

- 🎯 **统一管理面板** - 通过可视化界面替代命令行操作 Kubernetes/OpenStack
- 👤 **用户认证系统** - JWT 认证 + Kubernetes SA Token 绑定
- 📊 **集群监控** - 实时监控 Cluster、Node、Pod、Container 等资源状态
- 💻 **资源利用率** - CPU、内存等资源实时监控
- 🛡️ **异常检测** - 智能流量分析与入侵检测
- 🔧 **命令执行** - 通过 Kubectl 访问 Cluster API

## 🏗️ 技术架构

### 后端
- **框架**: Django 5.1.7
- **API**: Django REST Framework + drf-spectacular (OpenAPI)
- **数据库**: SQLite (开发) / MySQL (生产)
- **认证**: 自研 HS256 JWT
- **K8s 集成**: kubernetes-client

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite 7.0
- **状态管理**: Pinia
- **路由**: Vue Router
- **UI 组件**: Element Plus
- **图表**: ECharts

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Node.js 22+
- pnpm 10+

### 后端安装

```bash
cd cloud_backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 前端安装

```bash
cd cloud_dashboard
pnpm install
pnpm dev
```

## 📚 文档目录

### 开发文档
- [后端开发文档](docs/dev/backend.md) - Django 应用架构、API 设计
- [前端开发文档](docs/dev/frontend.md) - Vue 组件、路由、状态管理
- [开发指南](docs/dev/devdocs.md) - 开发规范与最佳实践

### 归档文档
- [工作日志](docs/archive/work_log.md) - 项目进度记录
- [功能记录](docs/archive/record.md) - 功能变更历史
- [脚本文档](docs/archive/ScriptDoc.md) - 工具脚本说明
- [模型输入](docs/archive/model_input.md) - 数据模型设计
- [Zeek 集成](docs/archive/zeek.md) - 流量分析配置

## 📁 项目结构

```
CloudPlatform/
├── cloud_backend/          # Django 后端
│   ├── authentication/     # 用户认证、K8s Token 管理
│   ├── runtime_monitoring/ # 集群监控、资源状态
│   ├── state_manager/      # 命令执行记录
│   ├── anomaly_detection/  # 异常检测、流量分析
│   └── cloud_backend/      # 项目配置
├── cloud_dashboard/        # Vue 前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── stores/        # Pinia 状态
│   │   ├── router/        # 路由配置
│   │   └── utils/         # 工具函数
│   └── public/
├── docs/                   # 文档目录
│   ├── dev/               # 开发文档
│   ├── api/               # API 文档
│   └── archive/           # 归档文档
└── mysql/                  # MySQL 配置

```

## 🔗 访问地址

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000/api
- **Admin 管理**: http://localhost:8000/admin
- **API 文档**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 👥 开发团队

- **项目进度**: [Google Sheets](https://docs.google.com/spreadsheets/d/1ARk2cffz5Z87JNdB0r9kxZUGX4lG_xVBqmeZGHFJQAs/edit?usp=sharing)

## 📄 许可证

[项目许可证信息]


