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