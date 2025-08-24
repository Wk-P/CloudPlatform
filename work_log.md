## 已完成
### 平台基础搭建
1. 用户系统
    - 实现用户对于本系统的登录以及和 k8s 账户的绑定
2. 监视 Cluster 状态
    - Cluster, Node, Pod, Container, Image 等资源状态，例如数量、可用性、版本等信息
    - Cluster 运行时的 Node 等的容器的 CPU、Memory 等资源利用状态
3. 指令操作
    - 通过 Kubectl 指令访问 Cluster API 获取更多需要用户需要的信息


## 未完成
1. 集群节点之间利用zero-copy异常流量探测
    - 利用DMA实现zero-copy
2. 针对异常流量做出对应措施
3. 日志系统
    - 记录用户指令操作记录以及 Cluster 运行状态日志

## 当前框架结构（2025-08-24）
- 总览
    - 后端：Django 5.1，应用模块包含 authentication、runtime_monitoring、state_manager、anomaly_detection；开发环境数据库使用 SQLite。
    - 前端：Vue 3 + Vite + TypeScript + Pinia + Vue Router + Element Plus。

- 身份与授权
    - 平台身份：自研 HS256 JWT，保存在 localStorage 或 sessionStorage；全局路由守卫与 401 统一处理（清理平台 JWT 并跳转 /login?redirect=...）。
    - 集群授权：按“用户-集群”维度绑定 Kubernetes SA Token（模型 K8sAccount）；KubeCluster 不再存储 token。

- 核心模型
    - ManagerCustomUser（UUID 主键）。
    - KubeCluster（runtime_monitoring）。
    - K8sAccount（authentication，FK user + cluster，字段含 token、namespace、k8s_api_server_url）。
    - CommandRecord（state_manager，用于持久化命令执行输出）。

- 主要接口
    - 认证：/api/auth/register/、/api/auth/login/、/api/auth/me/、/api/auth/k8s/account/bind/、/api/auth/k8s/sa-info/。
    - 运行时：/api/runtime/clusters/baseinfo/、/api/runtime/clusters/<id>/{nodes,pods,services,deployments,daemonsets,statefulsets,replicasets,namespaces}。
    - 命令：/api/state/run/cmd/（支持 apply/delete/scale）。

- 前端页面与逻辑
    - LoginView：登录并依据 redirect 返回原目标页。
    - ClustersView：集群管理与“绑定 SA”对话框（本地解码 SA JWT 的 exp 并显示有效性）。
    - CommandsView：支持 apply/delete/scale；YAML/JSON 多文档解析与结果展示；错误优先显示。
    - 网络层：fetchWithAuth 统一附带 Authorization；401 时仅清理平台 JWT 并跳转登录（不触碰 SA Token）。
    - 路由：未登录访问任意受保护页面均重定向到 /login。

- 典型流程
    1. 用户登录获取平台 JWT。
    2. 注册/选择集群。
    3. 为该用户-集群绑定 SA Token。
    4. 浏览运行时资源或执行命令；若平台 JWT 过期则自动跳转登录，完成后按 redirect 返回原页面。