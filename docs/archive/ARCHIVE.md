# Archived Documentation

Historical notes, configurations, and development logs. **May be outdated.**

---

## Project Work Log

### 已完成
#### 平台基础搭建
- Django 后端项目结构
- Vue 3 前端脚手架
- 基础路由和布局

#### 认证系统
- JWT 认证实现
- 用户注册/登录
- ServiceAccount Token 绑定

#### 集群管理
- 集群注册功能
- K8s API 集成
- 资源监控基础

#### 前端界面
- 现代化侧边栏导航
- Glassmorphism 设计风格
- 响应式布局

---

## Technical Notes

### k8s

#### Minikube Commands
```bash
minikube start
minikube ip  # Get cluster IP
minikube dashboard
```

#### ServiceAccount Setup
```bash
kubectl create serviceaccount zeek-admin-sa -n zeek-admin-ns
kubectl create clusterrolebinding zeek-admin-binding \
  --clusterrole=cluster-admin \
  --serviceaccount=zeek-admin-ns:zeek-admin-sa
```

#### Generate Token
```bash
kubectl create token zeek-admin-sa -n zeek-admin-ns --duration=8760h
```

#### Verify Permissions
```bash
kubectl auth can-i '*' '*' --as=system:serviceaccount:zeek-admin-ns:zeek-admin-sa
```

### openstack
(Historical notes - platform focus shifted to K8s)

---

## Script Documentation

### ServiceAccount + 绑定只读权限

创建只读权限的 ServiceAccount：

```bash
# 创建 namespace
kubectl create namespace readonly-ns

# 创建 ServiceAccount
kubectl create serviceaccount readonly-sa -n readonly-ns

# 创建只读 ClusterRole
kubectl create clusterrole readonly-role \
  --verb=get,list,watch \
  --resource=pods,services,deployments,nodes

# 绑定角色
kubectl create clusterrolebinding readonly-binding \
  --clusterrole=readonly-role \
  --serviceaccount=readonly-ns:readonly-sa
```

---

## ML Model Input Specs

### 模型输入问题

#### GPT 解答

**问题**: 异常检测模型的输入数据格式是什么？

**回答**: 
- 时间序列数据：CPU、内存、网络流量指标
- 特征向量：从 Prometheus/K8s metrics 提取
- 标注数据：正常/异常标签用于训练

#### 数据预处理
1. 归一化数值特征
2. 时间窗口滑动
3. 异常值过滤

---

## Zeek Network Monitoring

### zeek 二次开发

Zeek (原 Bro) 网络监控集成方案：

#### 安装
```bash
apt-get install zeek
```

#### 配置
- 监听网络接口
- 自定义脚本编写
- 日志输出到 Redis/Kafka

#### 与平台集成
- Zeek 检测异常流量
- 通过 Redis 传递数据到后端
- 触发防火墙规则更新

**注意**: 当前版本暂未深度集成 Zeek，保留为未来扩展方向。

---

**Last Updated**: Historical archive - refer to main documentation for current information.
