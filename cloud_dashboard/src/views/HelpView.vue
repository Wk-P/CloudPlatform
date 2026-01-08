<template>
    <div class="page">
        <div class="page-header">
            <h2>Help Documentation</h2>
            <p class="hint">Quick guidelines for using the platform. Sections below summarize common flows and tips.</p>
        </div>

        <section class="help-content">
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
        </section>
    </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.page {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 24px;
    padding: 8px;
}

.page-header {
    margin-bottom: 8px;
}

.page-header h2 {
    font-size: 28px;
    font-weight: 600;
    margin: 0 0 8px 0;
    color: var(--color-text-primary);
}

.hint {
    color: var(--color-text-muted);
    font-size: 14px;
    margin: 0;
    line-height: 1.5;
}

.help-content {
    padding: 24px;
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: var(--shadow-sm);
    transition: all var(--duration-normal) var(--ease-out);
}

.help-content:hover {
    background: rgba(30, 41, 59, 0.8);
    border-color: rgba(148, 163, 184, 0.3);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.help-content :deep(.el-collapse) {
    border: none;
    background: transparent;
}

.help-content :deep(.el-collapse-item) {
    margin-bottom: 12px;
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    background: var(--color-surface);
    overflow: hidden;
}

.help-content :deep(.el-collapse-item__header) {
    padding: 14px 18px;
    background: var(--color-surface);
    color: var(--color-text-primary);
    font-weight: 600;
    font-size: 15px;
    border: none;
    transition: all 0.2s ease;
}

.help-content :deep(.el-collapse-item__header:hover) {
    background: var(--color-surface-hover);
}

.help-content :deep(.el-collapse-item__wrap) {
    border: none;
    background: transparent;
}

.help-content :deep(.el-collapse-item__content) {
    padding: 16px 20px;
    background: var(--color-surface);
    color: var(--color-text-primary);
    font-size: 14px;
    line-height: 1.6;
}

.help-content :deep(.el-collapse-item__content ul) {
    margin: 8px 0;
    padding-left: 24px;
}

.help-content :deep(.el-collapse-item__content li) {
    margin: 8px 0;
    color: var(--color-text-primary);
}

.help-content :deep(.el-collapse-item__content code) {
    background: rgba(148, 163, 184, 0.15);
    color: var(--color-primary);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
}

.help-content :deep(.el-collapse-item__content strong) {
    color: var(--color-text-primary);
    font-weight: 600;
}

@media (max-width: 768px) {
    .page {
        padding: 4px;
        gap: 16px;
    }

    .help-content {
        padding: 16px;
    }

    .page-header h2 {
        font-size: 24px;
    }

    .help-content :deep(.el-collapse-item__header) {
        padding: 12px 14px;
        font-size: 14px;
    }

    .help-content :deep(.el-collapse-item__content) {
        padding: 12px 14px;
        font-size: 13px;
    }
}
</style>
