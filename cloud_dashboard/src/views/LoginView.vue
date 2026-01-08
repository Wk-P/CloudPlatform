<template>
    <div class="login-container">
        <el-card class="login-card">
            <h2 style="margin-bottom: 2rem">Login to cloud admin manage platform</h2>
            <el-alert v-if="errorMessage" :title="errorMessage" type="error" show-icon class="mb-12" />
            <el-form ref="loginForm" :model="form" :rules="rules" label-width="80px">
                <el-form-item label="username">
                    <el-input v-model="form.username" placeholder="Enter username" />
                </el-form-item>
                <el-form-item label="password">
                    <el-input v-model="form.password" type="password" placeholder="Enter password" show-password />
                </el-form-item>
                <div class="row">
                    <el-checkbox v-model="remember">Remember Me</el-checkbox>
                    <div class="spacer" />
                    <el-button type="primary" :loading="loading" @click="submitLogin">Login</el-button>
                    <el-button :disabled="loading" @click="goRegister">Register</el-button>
                    <el-button :disabled="loading" text @click="guestLogin">Guest</el-button>
                </div>
            </el-form>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import type { FormInstance } from 'element-plus';
import { URLs } from '@/urls';

const form = ref({ username: '', password: '' });
const router = useRouter();
const route = useRoute();
const loginForm = ref<FormInstance>();
const loading = ref(false);
const errorMessage = ref('');
const remember = ref(true);

const rules = {
    username: [
        { required: true, message: 'Please Enter username', trigger: 'blur' },
        { min: 2, message: 'At least 2 characters', trigger: 'blur' },
    ],
    password: [
        { required: true, message: 'Please Enter password', trigger: 'blur' },
        { min: 4, message: 'At least 4 characters', trigger: 'blur' },
    ],
};

function normalizeToken(t: string): string {
    let s = t.trim();
    if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
        s = s.slice(1, -1);
    }
    s = s.replace(/^Bearer\s+/i, '');
    return s;
}

function saveToken(token: string) {
    try {
        const norm = normalizeToken(token);
        if (remember.value) {
            localStorage.setItem('cloud-dashboard-token', norm);
        } else {
            sessionStorage.setItem('cloud-dashboard-token', norm);
        }
    } catch {
        localStorage.setItem('cloud-dashboard-token', normalizeToken(token));
    }
}

function goAfterLogin() {
    const redirect = (route.query.redirect as string) || '/dashboard';
    try {
        // allow absolute or encoded URLs within app path
        const target = decodeURIComponent(redirect);
        if (target.startsWith('/')) {
            window.location.href = target;
            return;
        }
    } catch {}
    window.location.href = '/dashboard';
}

const submitLogin = async () => {
    errorMessage.value = '';
    if (loginForm.value?.validate) {
        await new Promise<void>((resolve) =>
            loginForm.value!.validate!((ok: boolean) => {
                if (ok) resolve();
            }),
        );
    }
    const payload = { username: form.value.username, password: form.value.password };
    loading.value = true;
    try {
        let resp = await fetch(URLs.AUTH_LOGIN, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (resp.status === 401) {
            // auto-register then login
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
            saveToken(data.token);
            ElMessage.success('Login successful');
            goAfterLogin();
        } else {
            errorMessage.value = data?.detail || 'Login failed';
        }
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : 'Login failed';
        errorMessage.value = msg;
    } finally {
        loading.value = false;
    }
};

const goRegister = () => {
    // reset login form and go to register
    form.value.username = '';
    form.value.password = '';
    errorMessage.value = '';
    router.push('/register');
};

const guestLogin = async () => {
    errorMessage.value = '';
    loading.value = true;
    try {
        const resp = await fetch(URLs.AUTH_JWT_ISSUE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: form.value.username || 'anonymous' }),
        });
        const data = await resp.json();
        if (resp.ok && data?.token) {
            saveToken(data.token);
            ElMessage.success('Guest login successful');
            goAfterLogin();
        } else {
            errorMessage.value = data?.detail || 'Guest login failed';
        }
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : 'Guest login failed';
        errorMessage.value = msg;
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.login-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: radial-gradient(circle at 20% 20%, rgba(102,126,234,0.15), transparent 45%),
        radial-gradient(circle at 80% 80%, rgba(245,87,108,0.12), transparent 40%),
        var(--color-bg-primary);
    padding: var(--space-8) var(--space-4);
}

.login-card {
    width: clamp(360px, 92vw, 540px);
    padding: var(--space-8);
    border-radius: var(--radius-xl);
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    box-shadow: var(--glass-shadow);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    overflow: hidden;
}

.row { display: flex; align-items: center; gap: var(--space-2); flex-wrap: wrap; }
.spacer { flex: 1; }
.mb-12 { margin-bottom: 12px; }

.login-card :deep(.el-form),
.login-card :deep(.el-form-item),
.login-card :deep(.el-input),
.login-card :deep(.el-input__wrapper) {
    width: 100%;
}

.login-card :deep(.el-input__wrapper) {
    background-color: var(--color-surface);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-sm);
    padding: 8px 12px;
    box-shadow: none;
    transition: all 0.2s ease;
}

.login-card :deep(.el-input__wrapper:hover) {
    background-color: var(--color-surface-hover);
    border-color: rgba(148, 163, 184, 0.4);
}

.login-card :deep(.el-input__wrapper.is-focus) {
    background-color: var(--color-surface-hover);
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.login-card :deep(.el-input__inner) {
    color: var(--color-text-primary);
    font-size: 14px;
}

.login-card :deep(.el-input__inner::placeholder) {
    color: var(--color-text-muted);
}

.login-card :deep(.el-form-item__label) {
    color: var(--color-text-secondary);
    font-weight: 500;
}

.login-card :deep(.el-alert__content) { word-break: break-word; }
.login-card :deep(.el-button) { white-space: nowrap; }
</style>
