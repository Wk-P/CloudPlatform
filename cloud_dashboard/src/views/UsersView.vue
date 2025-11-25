<template>
    <div class="page">
        <h2>Users management</h2>
        <p class="hint">Manage platform users. JWT is used to authenticate API calls.</p>

        <section class="current-user">
            <h3>Current User</h3>
            <div v-if="meError" class="error">{{ meError }}</div>
            <div v-else-if="!me">No login info</div>
            <div v-else class="me-box">
                <div><strong>UUID:</strong> {{ me.uuid }}</div>
                <div><strong>Username:</strong> {{ me.username }}</div>
            </div>
            <div class="row">
                <button class="primary-small-button" style="margin-left: 0;" @click="loadMe">Refresh</button>
                <button class="warning-small-button" @click="logout">Logout</button>
            </div>
        </section>

        <section class="register">
            <h3>Create User</h3>
            <el-alert v-if="createError" :title="createError" type="error" show-icon class="mb-12" />
            <el-form :model="regForm" label-width="120px" class="reg-form">
                <el-form-item label="Username">
                    <el-input v-model="regForm.username" placeholder="Enter username" />
                </el-form-item>
                <el-form-item label="Password">
                    <el-input v-model="regForm.password" type="password" placeholder="Enter password" show-password />
                </el-form-item>
                <div class="row">
                    <div class="spacer" />
                    <el-button type="primary" :loading="creating" @click="createUser">Create</el-button>
                    <el-button :disabled="creating" @click="resetForm">Reset</el-button>
                </div>
            </el-form>
        </section>

        <section class="recent">
            <h3>Recently Created</h3>
            <el-table :data="recentUsers" border style="width: 100%; margin-top: 8px">
                <el-table-column prop="username" label="username" />
                <el-table-column prop="uuid" label="uuid" />
                <el-table-column label="operation" width="140">
                    <template #default="{ row }">
                        <el-button size="small" @click="switchLogin(row)">Login as</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </section>
    </div>

</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { fetchWithAuth } from '@/utils';
import { URLs } from '@/urls';

type Me = { uuid: string; username: string } | null;
const me = ref<Me>(null);
const meError = ref('');

const regForm = ref({ username: '', password: '' });
const creating = ref(false);
const createError = ref('');
const recentUsers = ref<Array<{ username: string; uuid: string }>>([]);

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

const createUser = async () => {
    createError.value = '';
    if (!regForm.value.username || !regForm.value.password) {
        createError.value = 'username and password are required';
        return;
    }
    creating.value = true;
    try {
        const resp = await fetch(URLs.AUTH_REGISTER, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: regForm.value.username, password: regForm.value.password }),
        });
        const data = await resp.json();
        if (!resp.ok || !data?.token) {
            throw new Error(data?.detail || 'Create failed');
        }
        // store in recent list (uuid not returned by register; best-effort decode via /auth/me after saving token)
        try { localStorage.setItem('cloud-dashboard-token', data.token); } catch {}
        await loadMe();
        if (me.value) {
            recentUsers.value.unshift({ username: me.value.username, uuid: me.value.uuid });
            recentUsers.value = recentUsers.value.slice(0, 10);
        }
        ElMessage.success('User created');
    } catch (e: unknown) {
        createError.value = e instanceof Error ? e.message : 'Create failed';
    } finally {
        creating.value = false;
    }
};

const resetForm = () => {
    regForm.value = { username: '', password: '' };
};

const logout = () => {
    try { localStorage.removeItem('cloud-dashboard-token'); } catch {}
    try { sessionStorage.removeItem('cloud-dashboard-token'); } catch {}
    me.value = null;
    ElMessage.success('Logged out');
};

const switchLogin = (row: { username: string }) => {
    // quick login: try login, fallback to register
    (async () => {
        try {
            const payload = { username: row.username, password: regForm.value.password || 'password' };
            let resp = await fetch(URLs.AUTH_LOGIN, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (resp.status === 401) {
                const reg = await fetch(URLs.AUTH_REGISTER, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                if (!reg.ok) throw new Error('register failed');
                resp = await fetch(URLs.AUTH_LOGIN, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
            }
            const data = await resp.json();
            if (resp.ok && data?.token) {
                localStorage.setItem('cloud-dashboard-token', data.token);
                await loadMe();
                ElMessage.success(`Logged in as ${row.username}`);
            } else {
                ElMessage.error(data?.detail || 'Login failed');
            }
        } catch (e) {
            ElMessage.error(e instanceof Error ? e.message : 'Switch login failed');
        }
    })();
};

onMounted(() => {
    loadMe();
});
</script>

<style scoped>
.page {
    width: 100%;
}
.row { display: flex; align-items: center; gap: .5rem; flex-wrap: wrap; }
.spacer { flex: 1; }
.hint { color: #666; font-size: 12px; margin: .25rem 0 .5rem; }
.error { color: #b00; margin: .5rem 0; }
.me-box { background: #fafafa; border: 1px solid #eee; padding: .5rem .75rem; border-radius: 4px; }
.reg-form { max-width: 560px; }
.mb-12 { margin-bottom: 12px; }
/* clear default margins and add spacing only between feature sections */
.page > section { padding: 12px 16px; border: 1px solid #eee; border-radius: 4px; margin: 0; }
.page > section + section { margin-top: 16px; }
</style>
