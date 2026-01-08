<template>
    <div class="page">
        <div class="page-header">
            <h2>Users Management</h2>
            <p class="hint">Manage platform users. JWT is used to authenticate API calls.</p>
        </div>

        <section class="current-user">
            <h3><i class="icon">👤</i> Current User</h3>
            <div v-if="meError" class="error-box">
                <i class="icon">⚠️</i>
                <span>{{ meError }}</span>
            </div>
            <div v-else-if="!me" class="empty-state">
                <i class="icon">🔒</i>
                <span>No login information available</span>
            </div>
            <div v-else class="me-box">
                <div class="info-item">
                    <span class="label">UUID:</span>
                    <span class="value">{{ me.uuid }}</span>
                </div>
                <div class="info-item">
                    <span class="label">Username:</span>
                    <span class="value">{{ me.username }}</span>
                </div>
            </div>
            <div class="actions">
                <el-button type="primary" plain @click="loadMe"> <i class="icon">🔄</i> Refresh </el-button>
                <el-button type="danger" plain @click="logout"> <i class="icon">🚪</i> Logout </el-button>
            </div>
        </section>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { fetchWithAuth } from '@/utils';
import { URLs } from '@/urls';

const router = useRouter();

type Me = { uuid: string; username: string } | null;
const me = ref<Me>(null);
const meError = ref('');

const loadMe = async () => {
    meError.value = '';
    try {
        const resp = await fetchWithAuth(URLs.AUTH_ME);
        const data = await resp.json();
        if (!resp.ok) throw new Error(data?.detail || `Load failed: ${resp.status}`);
        if (data?.user) {
            me.value = { uuid: data.user.uuid, username: data.user.username };
        } else {
            me.value = null;
        }
    } catch (e: unknown) {
        meError.value = e instanceof Error ? e.message : 'Load current user failed';
    }
};

const logout = () => {
    try {
        localStorage.removeItem('cloud-dashboard-token');
    } catch {}
    try {
        sessionStorage.removeItem('cloud-dashboard-token');
    } catch {}
    me.value = null;
    ElMessage.success('Logged out');
    router.push('/login');
};

onMounted(() => {
    loadMe();
});
</script>

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

.page > section {
    padding: 24px;
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: var(--shadow-sm);
    transition: all var(--duration-normal) var(--ease-out);
}

.page > section:hover {
    background: rgba(30, 41, 59, 0.8);
    border-color: rgba(148, 163, 184, 0.3);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.page > section h3 {
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 20px 0;
    color: var(--color-text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--glass-border);
}

.icon {
    font-style: normal;
    font-size: 16px;
}

.error-box {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.4);
    border-radius: var(--radius-sm);
    color: #fca5a5;
    margin-bottom: 16px;
    font-size: 14px;
}

.empty-state {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 24px;
    background: var(--color-surface);
    border: 2px dashed var(--glass-border);
    border-radius: var(--radius-sm);
    color: var(--color-text-muted);
    justify-content: center;
    margin-bottom: 16px;
    font-size: 14px;
}

.me-box {
    background: var(--color-surface);
    border: 1px solid var(--glass-border);
    padding: 0;
    border-radius: var(--radius-md);
    margin-bottom: 20px;
    overflow: hidden;
}

.info-item {
    display: flex;
    align-items: center;
    padding: 16px 20px;
    font-size: 14px;
    border-bottom: 1px solid var(--glass-border);
    transition: background-color 0.2s ease;
}

.info-item:last-child {
    border-bottom: none;
}

.info-item:hover {
    background-color: transparent;
}

.info-item .label {
    font-weight: 600;
    color: var(--color-text-secondary);
    min-width: 100px;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.info-item .value {
    color: var(--color-text-primary);
    font-family: 'Courier New', monospace;
    font-size: 14px;
    flex: 1;
    word-break: break-all;
}

.actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.el-button .icon {
    margin-right: 4px;
}

.actions :deep(.el-button) {
    min-width: 110px;
}

.actions :deep(.el-button--primary),
.actions :deep(.el-button--danger) {
    color: #fff;
}

.actions :deep(.el-button--primary) {
    background: var(--gradient-primary);
    border: none;
}

.actions :deep(.el-button--primary:hover) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.actions :deep(.el-button--danger) {
    background: var(--gradient-danger);
    border: none;
}

.actions :deep(.el-button--danger:hover) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.el-button .icon {
    margin-right: 4px;
}

@media (max-width: 768px) {
    .page {
        padding: 4px;
        gap: 16px;
    }

    .page > section {
        padding: 16px;
    }

    .page-header h2 {
        font-size: 24px;
    }

    .actions {
        flex-direction: column;
    }

    .actions .el-button {
        width: 100%;
    }

    .info-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 6px;
    }

    .info-item .label {
        min-width: auto;
    }

    .info-item .value {
        width: 100%;
        word-break: break-all;
    }
}
</style>
