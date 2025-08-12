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
开发：利用 k8s 平台先创建对应的 
- django-agent (Cluster -> Service Accounts -> Roles) 目的是提供 token
- django-agent-read 目的是绑定到

### 监视应用模块
利用 metrics 模块进行数据收集



# 后端开发日志 Backend Development Log 
## 2025-08-12
Django 后端与 k8s API 更多连接
- Remote-DMA 设计
- zeek 监视
- API 制作
补充开发日志



## 2025-08-13
静态资源监测
- 节点
- pod
- 虚拟机
- namespace
- ...