# 📚 CloudPlatform 文档中心

欢迎查阅 CloudPlatform 云资源管理平台的完整文档。

## 📖 文档导航

### 🚀 快速开始
- [项目主页](../README.md) - 项目概览与快速开始指南
- [安装指南](../README.md#快速开始) - 前后端环境搭建
- [API 文档](http://localhost:8000/api/docs) - Swagger UI 交互式 API 文档

### 💻 开发文档

#### 后端开发
- [后端架构文档](dev/backend.md) - Django 应用模块设计
  - 认证系统 (authentication)
  - 运行时监控 (runtime_monitoring)
  - 状态管理 (state_manager)
  - 异常检测 (anomaly_detection)

#### 前端开发
- [前端开发文档](dev/frontend.md) - Vue 3 组件与路由设计
  - 全局认证与路由守卫
  - API 封装 (fetchWithAuth)
  - 状态管理 (Pinia)
  - 页面组件说明

#### 开发规范
- [开发指南](dev/devdocs.md) - 编码规范与最佳实践

### 📦 API 参考

访问运行中的 API 文档：
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Schema**: http://localhost:8000/api/schema

#### API 端点概览

**认证 API** (`/api/auth/`)
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录
- `GET /api/auth/me/` - 获取当前用户信息
- `POST /api/auth/k8s/account/` - 管理 K8s 账户
- `POST /api/auth/k8s/account/bind/` - 绑定 K8s 账户到集群

**集群监控 API** (`/api/runtime/`)
- `GET /api/runtime/clusters/` - 获取集群列表
- `POST /api/runtime/clusters/register/` - 注册新集群
- `GET /api/runtime/nodes/` - 获取节点列表
- `GET /api/runtime/pods/` - 获取 Pod 列表
- `GET /api/runtime/resources/` - 获取资源使用情况

**状态管理 API** (`/api/state/`)
- `POST /api/state/command/` - 执行命令
- `GET /api/state/history/` - 查询命令历史

**异常检测 API** (`/api/anomaly/`)
- `GET /api/anomaly/blacklist/` - 获取黑名单
- `POST /api/anomaly/blacklist/` - 添加黑名单项
- `GET /api/anomaly/traffic/` - 获取流量样本

### 📝 归档文档

历史记录与参考资料：
- [工作日志](archive/work_log.md) - 项目开发进度与完成情况
- [功能记录](archive/record.md) - 功能变更与版本历史
- [脚本文档](archive/ScriptDoc.md) - 工具脚本使用说明
- [模型设计](archive/model_input.md) - 数据模型输入文档
- [Zeek 集成](archive/zeek.md) - 网络流量分析配置

## 🏗️ 技术栈详解

### 后端技术
- **Django 5.1.7** - Web 框架
- **Django REST Framework** - RESTful API
- **drf-spectacular** - OpenAPI/Swagger 文档生成
- **django-cors-headers** - CORS 跨域支持
- **kubernetes-client** - Kubernetes Python 客户端
- **PyMySQL** - MySQL 数据库驱动

### 前端技术
- **Vue 3.5** - 渐进式 JavaScript 框架
- **TypeScript 5.8** - 类型安全
- **Vite 7.0** - 构建工具
- **Pinia 3.0** - 状态管理
- **Vue Router 4.5** - 路由管理
- **Element Plus 2.10** - UI 组件库
- **ECharts 5.6** - 数据可视化

## 🔧 开发工具

### 推荐 IDE
- **VS Code** - 推荐插件：
  - Vue - Official
  - Python
  - Pylance
  - ESLint
  - Prettier

### 开发命令

**后端开发**
```bash
# 激活虚拟环境
source .venv/bin/activate

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver

# 运行测试
python manage.py test
```

**前端开发**
```bash
# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建生产版本
pnpm build

# 类型检查
pnpm type-check

# 代码检查
pnpm lint

# 代码格式化
pnpm format
```

## 🐛 故障排除

### 常见问题

**Q: Django 导入错误 "No module named 'django'"**
```bash
# 确保激活了虚拟环境
source .venv/bin/activate
pip install -r requirements.txt
```

**Q: 前端启动失败 "Cannot find module 'vite'"**
```bash
# 重新安装依赖
rm -rf node_modules
pnpm install
```

**Q: Kubernetes 连接失败**
- 检查 K8s API Server 地址和端口
- 验证 ServiceAccount Token 是否有效
- 确认网络连接和防火墙设置

**Q: CORS 跨域错误**
- 检查 `settings.py` 中的 `CORS_ALLOWED_ORIGINS`
- 确保前端地址已添加到白名单

## 📞 获取帮助

- **问题反馈**: [GitHub Issues]
- **开发讨论**: [Google Sheets](https://docs.google.com/spreadsheets/d/1ARk2cffz5Z87JNdB0r9kxZUGX4lG_xVBqmeZGHFJQAs/edit?usp=sharing)

## 📅 更新日志

查看 [工作日志](archive/work_log.md) 了解最新开发进度和功能更新。

---

**最后更新**: 2026-01-08
