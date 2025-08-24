# 开发计划 Development Schedule
- **Google drive**   
`https://docs.google.com/spreadsheets/d/1ARk2cffz5Z87JNdB0r9kxZUGX4lG_xVBqmeZGHFJQAs/edit?usp=sharing`
<br>
<br>
<br>


# 后端开发文档 Backend Development Documents
## 架构
Django (Version 5.1.7)

## 文件结构
### anomaly_detection
功能：异常检测相关API和后端调度


### authentication
功能：管理 k8s 登录令牌(token)


### running_monitoring
功能：动态资源监视与 API


### state_manager
功能：静态资源监视与 API


## 后端组织形式

### 访问账户相关
1. Service Accounts
    - 基础账户，控制 token 发布，以便能访问 k8s API
2. Roles
    - 只在单个 namepsace 生效
3. Cluster Roles
    - 在 Cluster 所有的 namespace 生效
4. Cluster Roles Binding
    - 给予 Service Account 对应的 Cluster Role 权限
5. Roles Binding
    - 给予 Service Account 对应的 namespace 权限


### k8s token 验证
目前：手动请求令牌（长时间），关闭 https 严格 SSL 证书检查，token 放入 http 中的 header。   
开发：利用 k8s 平台先创建对应的 Service Account 和权限控制清单
<br>
访问权限细则请查看 `minikube dashboard`   
文档如下（待补充）

### 监视应用模块
基础静态资源通过
利用 metrics 模块进行数据收集


### 数据库保存模型
1. Cluster 
2. SA
3. Command 



# 后端开发日志 Backend Development Log 
## 2025-08-24
- 认证与会话
    - 保持平台 JWT 与 Kubernetes SA Token 的职责分离；新增前端 401 统一处理策略后，后端接口行为未变更：平台 JWT 失效返回 401，业务错误按 4xx/5xx 分类。
- SA 绑定与多集群
    - 已提供 /api/auth/k8s/account/bind/ 接口用于为当前用户与指定集群绑定/更新 SA Token；其余运行时/状态查询均从用户-集群维度解析 SA。
- 运行时与命令
    - 继续沿用动态客户端执行 apply/delete/scale；输入校验与错误抛出维持昨日逻辑，便于前端进行统一错误展示。
- 运维
    - 修正测试 token.json 的格式与有效期以便联调；数据库模型维持 K8sAccount 绑定（user+cluster）。

## 2025-08-23
- Kubernetes 高级指令支持（state_manager.views.run_command）
    - 新增 actions: apply、delete、scale；使用 DynamicClient 执行 Server-Side Apply（apply-patch+yaml），失败回退 create；delete 支持 kind/resource 映射与命名空间/集群作用域判断；scale 通过 AppsV1Api patch Scale。
    - 支持 manifest 直接传字符串（YAML 多文档或 JSON 对象/数组）；解析失败返回明确错误；新增“未解析到对象”的提示，避免空结果。
    - 强化参数校验与错误处理：按动作的必填校验，集群 ID（id/cluster_id）解析，已知错误返回 400/404，未知错误捕获为 500。
    - 命令运行记录持久化（CommandRecord）：stdout/stderr/returncode/status；长输出安全截断。
- 安全/认证
    - 接口继续使用 JWT Bearer 校验（jwt_required）。
- RBAC 与联调
    - 提供 Linux 下查看/赋权 SA 的一次性脚本；测试环境示例绑定 cluster-admin，并给出回滚命令。
    - 联调验证 apply 流程（修正 YAML 换行与 apiVersion 拼写问题），成功创建/更新 Deployment。

## 2025-08-12
Django 后端与 k8s API 更多连接
- Remote-DMA 设计
- zeek 监视
- API 制作

问题总结：
1. zeek 抓取到的数据和模型输入不匹配 （预处理问题）   
2. 需要针对模型检测到的异常流量做出反应：
    - IP 封锁
    - 流量大小限制
3. DMA 实现
    - 硬件不满足，目前决定使用软件形式暂时实现


补充开发日志


## 2025-08-13
1. 完善 API 结构
- 针对不同资源完善 API

2. 静态资源监测
- 节点
- pod
- 虚拟机
- namespace
- ...