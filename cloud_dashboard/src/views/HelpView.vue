<template>
    <div class="page">
        <h2>Help Documentation</h2>
        <p class="hint">Quick guidelines for using the platform. Sections below summarize common flows and tips.</p>

        <el-collapse>
            <el-collapse-item title="Getting started" name="1">
                <ul>
                    <li>Login or register from the Login/Register pages. Tokens are stored in browser storage.</li>
                    <li>Frontend backend API endpoints are centralized in <code>src/urls/index.ts</code>.</li>
                    <li>Dev proxy forwards <code>/api</code> to backend: see <code>vite.config.ts</code>.</li>
                </ul>
            </el-collapse-item>

            <el-collapse-item title="User management" name="2">
                <p>
                    Use the <strong>Users</strong> page to:
                </p>
                <ul>
                    <li>View current user info (<code>/api/auth/me/</code>).</li>
                    <li>Create users (<code>/api/auth/register/</code>) and quickly switch login.</li>
                    <li>Logout to clear local token.</li>
                </ul>
            </el-collapse-item>

            <el-collapse-item title="Cluster management & monitoring" name="3">
                <ul>
                    <li>Clusters/Monitoring pages list nodes, pods, services, etc. via <code>/api/runtime/...</code>.</li>
                    <li>To add clusters, provide API server, port, namespace, and a valid SA token.</li>
                </ul>
            </el-collapse-item>

            <el-collapse-item title="Command console" name="4">
                <ul>
                    <li>Run basic operations (get/describe/logs/apply/delete/scale) with safeguards.</li>
                    <li>Commands are sent through a server endpoint that wraps execution; verify permissions first.</li>
                </ul>
            </el-collapse-item>

            <el-collapse-item title="Anomaly detector" name="5">
                <ul>
                    <li>Ingress Blacklist: GET <code>/api/ingress/blacklist/</code>.</li>
                    <li>Traffic Trend: GET <code>/api/ingress/traffic/trend/</code>, auto-refresh every 30s.</li>
                    <li>Supported controls table lists common NGINX ingress annotations/configs.</li>
                </ul>
            </el-collapse-item>

            <el-collapse-item title="Troubleshooting" name="6">
                <ul>
                    <li>401 Unauthorized: token missing/expired — you will be redirected to Login.</li>
                    <li>503 metrics unavailable: metrics-server may be down; some usage endpoints will degrade.</li>
                    <li>CORS issues: dev uses Vite proxy to <code>http://127.0.0.1:8000</code>; ensure backend is running.</li>
                    <li>JWT enforcement is configurable in backend <code>settings.JWT_SETTINGS.ENFORCE</code>.</li>
                </ul>
            </el-collapse-item>
        </el-collapse>
    </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.page { max-width: 980px; padding: 16px 20px; background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); }
.hint { color: var(--color-text-muted); font-size: 12px; margin: .25rem 0 .5rem; }
.el-collapse-item { margin-bottom: 10px; }
h2 { padding: 6px 8px; }
:deep(.el-collapse-item__header) { padding: 10px 14px; }
:deep(.el-collapse-item__content) { padding: 12px 16px; }
:deep(.el-collapse) { margin-top: 8px; }
:deep(.el-collapse-item__content ul) { margin: 0; padding-left: 18px; }
</style>
