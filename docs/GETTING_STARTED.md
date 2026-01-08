# 快速开发指南

## 🎯 5分钟快速启动

### 前置条件
- Python 3.12+
- Node.js 22+
- Git

### 1️⃣ 克隆项目
```bash
git clone <repository-url>
cd CloudPlatform
```

### 2️⃣ 后端设置
```bash
# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
cd cloud_backend
pip install -r requirements.txt

# 数据库初始化
python manage.py migrate

# 创建管理员账户
python manage.py createsuperuser

# 启动后端服务
python manage.py runserver
```

后端运行在: http://localhost:8000

### 3️⃣ 前端设置
```bash
# 在新终端窗口
cd cloud_dashboard

# 安装 pnpm (如未安装)
npm install -g pnpm

# 安装依赖
pnpm install

# 启动前端服务
pnpm dev
```

前端运行在: http://localhost:5173

### 4️⃣ 访问应用
- **前端界面**: http://localhost:5173
- **后端 Admin**: http://localhost:8000/admin
- **API 文档**: http://localhost:8000/api/docs

## 📝 开发流程

### 后端开发

#### 创建新的 API 端点
1. 在对应 app 的 `views.py` 中添加视图
2. 在 `urls.py` 中注册路由
3. 如需数据库，在 `models.py` 中定义模型
4. 运行迁移：
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 示例：添加新 API
```python
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response

class MyNewView(APIView):
    def get(self, request):
        return Response({'message': 'Hello World'})

# urls.py
from .views import MyNewView

urlpatterns = [
    path('my-endpoint/', MyNewView.as_view()),
]
```

### 前端开发

#### 创建新页面
1. 在 `src/views/` 中创建 Vue 组件
2. 在 `src/router/index.ts` 中注册路由
3. 在导航中添加链接（如需要）

#### 示例：添加新页面
```typescript
// src/views/MyNewView.vue
<template>
  <div>
    <h1>My New Page</h1>
  </div>
</template>

<script setup lang="ts">
// Your logic here
</script>

// src/router/index.ts
{
  path: '/my-page',
  name: 'MyPage',
  component: () => import('@/views/MyNewView.vue')
}
```

#### API 调用
```typescript
import { fetchWithAuth } from '@/utils'

const response = await fetchWithAuth('/api/my-endpoint/')
if (response.ok) {
  const data = await response.json()
  console.log(data)
}
```

## 🔧 常用命令

### 后端
```bash
# 启动开发服务器
python manage.py runserver

# 创建迁移
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 运行测试
python manage.py test

# 进入 Shell
python manage.py shell
```

### 前端
```bash
# 开发模式
pnpm dev

# 构建生产版本
pnpm build

# 预览构建结果
pnpm preview

# 类型检查
pnpm type-check

# 代码检查
pnpm lint

# 格式化代码
pnpm format
```

## 🐛 调试技巧

### 后端调试
```python
# 使用 print 或 logging
import logging
logger = logging.getLogger(__name__)
logger.debug('Debug message')

# Django Shell 测试
python manage.py shell
>>> from authentication.models import ManagerCustomUser
>>> ManagerCustomUser.objects.all()
```

### 前端调试
```typescript
// 使用 console
console.log('Debug info', variable)

// Vue DevTools (浏览器插件)
// 安装: https://devtools.vuejs.org/
```

## 📦 项目结构

```
CloudPlatform/
├── cloud_backend/              # Django 后端
│   ├── authentication/         # 用户认证
│   ├── runtime_monitoring/     # 集群监控
│   ├── state_manager/          # 状态管理
│   ├── anomaly_detection/      # 异常检测
│   ├── cloud_backend/          # 配置
│   ├── manage.py
│   └── requirements.txt
├── cloud_dashboard/            # Vue 前端
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   ├── stores/            # Pinia 状态
│   │   ├── router/            # 路由
│   │   ├── utils/             # 工具函数
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
└── docs/                       # 文档
```

## ✅ 检查清单

开始开发前：
- [ ] 虚拟环境已激活
- [ ] 依赖已安装
- [ ] 数据库已迁移
- [ ] 后端服务运行正常
- [ ] 前端服务运行正常
- [ ] 能访问 Admin 面板
- [ ] 能访问 API 文档

## 🆘 遇到问题？

1. 查看 [文档中心](README.md)
2. 检查 [API 参考](api/quick-reference.md)
3. 查看归档的 [工作日志](archive/work_log.md)
4. 联系开发团队

## 🎓 学习资源

- [Django 文档](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue 3 文档](https://vuejs.org/)
- [TypeScript 文档](https://www.typescriptlang.org/)
- [Element Plus](https://element-plus.org/)
