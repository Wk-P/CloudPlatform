# API 快速参考

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: Bearer Token (JWT)
- **Content-Type**: `application/json`

## 认证流程

### 1. 用户注册
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "user123",
  "password": "password123"
}
```

**响应**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "username": "user123"
  }
}
```

### 2. 用户登录
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "user123",
  "password": "password123"
}
```

### 3. 获取当前用户
```http
GET /api/auth/me/
Authorization: Bearer <token>
```

## 集群管理

### 注册集群
```http
POST /api/runtime/clusters/register/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "prod-cluster",
  "api_server": "192.168.0.247",
  "port": 8443,
  "description": "Production Kubernetes Cluster"
}
```

### 获取集群列表
```http
GET /api/runtime/clusters/
Authorization: Bearer <token>
```

### 绑定 K8s 账户
```http
POST /api/auth/k8s/account/bind/
Authorization: Bearer <token>
Content-Type: application/json

{
  "cluster_id": 1,
  "token": "<k8s-sa-token>",
  "namespace": "default"
}
```

## 资源监控

### 获取节点列表
```http
GET /api/runtime/nodes/?cluster_id=1
Authorization: Bearer <token>
```

### 获取 Pod 列表
```http
GET /api/runtime/pods/?cluster_id=1&namespace=default
Authorization: Bearer <token>
```

### 获取资源使用情况
```http
GET /api/runtime/resources/?cluster_id=1
Authorization: Bearer <token>
```

## 命令执行

### 执行命令
```http
POST /api/state/command/
Authorization: Bearer <token>
Content-Type: application/json

{
  "cluster_id": "1",
  "command": "kubectl get pods -n default"
}
```

**响应**
```json
{
  "id": 1,
  "status": "done",
  "returncode": 0,
  "stdout": "NAME                     READY   STATUS    RESTARTS   AGE\nnginx-xxx                1/1     Running   0          1d",
  "stderr": ""
}
```

### 查询命令历史
```http
GET /api/state/history/
Authorization: Bearer <token>
```

## 异常检测

### 获取黑名单
```http
GET /api/anomaly/blacklist/
Authorization: Bearer <token>
```

### 添加黑名单项
```http
POST /api/anomaly/blacklist/
Authorization: Bearer <token>
Content-Type: application/json

{
  "ip": "192.168.1.100",
  "action": "block",
  "reason": "Suspicious activity detected"
}
```

### 获取流量样本
```http
GET /api/anomaly/traffic/?start=2026-01-01&end=2026-01-08
Authorization: Bearer <token>
```

## 错误响应

### 400 Bad Request
```json
{
  "detail": "username and password are required"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid token: Token expired"
}
```

### 404 Not Found
```json
{
  "detail": "Cluster not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

## 完整文档

访问以下地址查看完整的交互式 API 文档：
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
