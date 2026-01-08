### service account + 绑定只读权限
```
$ kubectl create serviceaccount django-agent
```
```
$ kubectl create clusterrolebinding django-agent-read \
  --clusterrole=view \
  --serviceaccount=default:django-agent
```


### 设定 token 并且获得内容 (token 定时 1 年)
```
$ kubectl create token django-agent --duration=8760h
```
```
eyJhbGciOiJSUzI1NiIsImtpZCI6IlZfRzRrQUpOaU5iTHM1N1ZPQnk2ODlMYm8xbkZzOXRPRjlxMXRGZ2pvX1EifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiXSwiZXhwIjoxNzgyNDY2OTgxLCJpYXQiOjE3NTA5MzA5ODEsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwianRpIjoiZjFmOTAyNzgtNTgxZS00ZTIwLThlNTktMjczODk2MmFjNTYwIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJkZWZhdWx0Iiwic2VydmljZWFjY291bnQiOnsibmFtZSI6ImRqYW5nby1hZ2VudCIsInVpZCI6ImQ0N2ViNjRjLWI1ZmItNGI0Ny1iZjdiLWQwNzkyNjY2ZmQ0MiJ9fSwibmJmIjoxNzUwOTMwOTgxLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6ZGVmYXVsdDpkamFuZ28tYWdlbnQifQ.x-JIm17kazqAP6A8dW9KV8or2M-w487UuabiqKRgDG4z_C0EFKflJ9REiuIvPu7qUMAn9aK6ntkA7wvE2kIKvA0liZZiMX5O_65oAdUncfzQrsCfKUWHDzkvks4_Amk7E-4RVmOOKii3bdVzAVC03IJw-VExL7Qdv5w17ZXMYRgfneC3XJxAxrKrBhTxxD3kACxb66Iqg1vGUKNSf8pLMi0EV6cG7he5P4qIkKb3WMGCZnFzibPmyrWbtY282wZgoq2gSjXmVvRvBPxxRM8d7BAI3vd7aABi9UuO2A4vok4E2MPmpQKOzsw_BZOAgNfADzy4jmAfOjWbFLfThJCLdQ
```

### 远端测试
curl -k https://192.168.49.2:8443/api --header "Authorization: Bearer <你的token>"


### 清理
kubectl delete sa django-agent
kubectl delete clusterrolebinding django-agent-read


### 附加 rbac 
为了扩展 rbac 读取权限
`cluster-read-all.yml`
```
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: django-agent-read-all
rules:
  - apiGroups: [""]
    resources:
      - pods
      - services
      - endpoints
      - nodes
      - namespaces
      - configmaps
      - secrets
      - persistentvolumes
      - persistentvolumeclaims
      - events
    verbs: ["get", "list", "watch"]

  - apiGroups: ["apps"]
    resources:
      - deployments
      - replicasets
      - daemonsets
      - statefulsets
    verbs: ["get", "list", "watch"]

  - apiGroups: ["batch"]
    resources:
      - jobs
      - cronjobs
    verbs: ["get", "list", "watch"]

  - apiGroups: ["autoscaling"]
    resources:
      - horizontalpodautoscalers
    verbs: ["get", "list", "watch"]

  - apiGroups: ["networking.k8s.io"]
    resources:
      - ingresses
      - networkpolicies
    verbs: ["get", "list", "watch"]

  - apiGroups: ["rbac.authorization.k8s.io"]
    resources:
      - roles
      - rolebindings
      - clusterroles
      - clusterrolebindings
    verbs: ["get", "list", "watch"]

  - apiGroups: ["apiextensions.k8s.io"]
    resources:
      - customresourcedefinitions
    verbs: ["get", "list", "watch"]
```
关联 role 和 cluster service account
`clusterrolebinding.yml`
```
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: django-agent-read-all-binding
subjects:
  - kind: ServiceAccount
    name: django-agent
    namespace: default
roleRef:
  kind: ClusterRole
  name: django-agent-read-all
  apiGroup: rbac.authorization.k8s.io
```