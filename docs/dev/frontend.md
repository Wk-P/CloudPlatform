# 开发计划
开发计划
- **Google drive**   
`https://docs.google.com/spreadsheets/d/1ARk2cffz5Z87JNdB0r9kxZUGX4lG_xVBqmeZGHFJQAs/edit?usp=sharing`
<br>
<br>
<br>

# 前端开发日志
## 2025年8月24日
- 全局认证与导航
	- 新增 fetchWithAuth 封装：统一附带 Authorization，遇到 401 仅清除平台 JWT 并重定向到 /login?redirect=<当前路径>；支持从 localStorage 与 sessionStorage 读取平台 JWT。
	- 路由守卫：未登录访问任何非登录/注册页面时，统一跳转登录；登录成功后按 redirect 返回原页面。
- ClustersView
	- 新增“绑定 SA”对话框（命名空间 + Token）；本地解码 SA JWT exp 并显示 Valid/Expired；401 时提示重新登录。
- 工具库（src/utils/index.ts）
	- 将 registerNewCluster/getResourcesInfo/getNamespaces/postCommand/bindClusterSaToken 等 API 切换到 fetchWithAuth；统一错误返回结构（含 ok/status/message）。
- 其它
	- 修复 Headers 合并的类型问题，TypeScript 校验通过。

## 2025年8月25日
- 新增 Zeek Detector 页面（ZeekDetectorView.vue）
	- 支持查看 Agent 列表（agent_id/version/status/last_heartbeat）。
	- 支持获取/编辑/保存默认配置（/api/anomaly/zeek/config/）。
	- 路由：新增 /zeek，侧边栏加入 Zeek 菜单项。

## 2025年8月23日
- Commands Console（CommandsView.vue）
	- 表单扩展：新增动作 apply/delete/scale；按动作展示对应输入项（manifest、kind/name、replicas 等）。
	- 交互增强：
		- 支持直接粘贴 YAML/JSON 清单；支持粘贴包含 action/cluster_id/manifest 的整段 JSON 并自动提取。
		- 新增“填充 Nginx 示例”“尝试解析 JSON”按钮；manifest 文本域等宽字体与最小尺寸优化。
	- 结果展示：失败时优先显示 Error，再显示 Output；原始载荷切换展示更清晰。
	- TypeScript：移除 any，用类型守卫保障解析逻辑；通过类型检查。
- 工具库（src/utils/index.ts）
	- 导出并扩展 CommandPayload，支持 apply/delete/scale，新增 manifest/kind/replicas 字段；resource 对 apply 可选。
	- postCommand 统一构建命令摘要（buildCmd），错误气泡更友好（返回码/消息）。

## 2025年8月21日
