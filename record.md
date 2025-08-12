### k8s

k8s 官方： https://kubernetes.io/zh-cn/docs/concepts/cluster-administration/networking/
k8s 博客： https://atbug.com/deep-dive-k8s-network-mode-and-communication/
k8s B 站 ： 【深入理解 k8s 网络(1): 概述】 https://www.bilibili.com/video/BV1gD4y1B7Cq/?share_source=copy_web&vd_source=692c1a09eb133b51b0694079cb7e419e

### openstack

openstack 官方： https://docs.openstack.org/mitaka/zh_CN/install-guide-obs/common/get_started_networking.html
openstack Red Hat： https://docs.redhat.com/zh-cn/documentation/red_hat_openstack_platform/9/html/networking_guide/openstack_networking_concepts#openstack_networking_diagram

（里面不全面或者不够多，建议找视频，目前针对 k8s）

environment settings
script:

```
# 重新创建 namespace
$ kubectl create namespace my-platform

# 正确创建 ServiceAccount（名字对齐）
$ kubectl create serviceaccount platform-admin -n my-platform

# 绑定 cluster-admin 权限
$ kubectl create clusterrolebinding platform-admin-binding \
  --clusterrole=cluster-admin \
  --serviceaccount=my-platform:platform-admin

# 生成 token
$ kubectl -n my-platform create token platform-admin
```

response (token 2025.04.30):

-   Saved in k8s_test_auth_token/token.json
    ` { "token": "<token>", "datetime": "<YYYY-MM-DD>" }`

-   minikub settings (test env)

```
    $ minikube start \
    --driver=docker \
    --cpus=2 --memory=4096 \
    --wait=apiserver,system_pods
```

nginx settings
192.168.0.247 -> minikube cluster ip

connect test

```
    $ curl -k https://192.168.0.247:8443/api \
    -H "Authorization: Bearer <token>"
```

### 手动更新
开发环境下先用 create 创建 token -> 手动写入 token.json, token 项就够了
-> 调用 auth.py -> 3. 更新token