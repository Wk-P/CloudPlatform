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
        { min: 2, message: 'At least 2 characters', trigger: 'blur' }
    ],
    password: [
        { required: true, message: 'Please Enter password', trigger: 'blur' },
        { min: 4, message: 'At least 4 characters', trigger: 'blur' }
    ]
};

function saveToken(token: string) {
    try {
        if (remember.value) {
            localStorage.setItem('cloud-dashboard-token', token);
        } else {
            sessionStorage.setItem('cloud-dashboard-token', token);
        }
    } catch {
        localStorage.setItem('cloud-dashboard-token', token);
    }
}

function goAfterLogin() {
    const redirect = (route.query.redirect as string) || '/dashboard';
    try {
        // allow absolute or encoded URLs within app path
        const target = decodeURIComponent(redirect);
        if (target.startsWith('/')) {
            router.push(target);
            return;
        }
    } catch {}
    router.push('/dashboard');
}

const submitLogin = async () => {
    errorMessage.value = '';
    if (loginForm.value?.validate) {
        await new Promise<void>((resolve) => loginForm.value!.validate!((ok: boolean) => { if (ok) resolve(); }));
    }
    const payload = { username: form.value.username, password: form.value.password };
    loading.value = true;
    try {
        let resp = await fetch('/api/auth/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (resp.status === 401) {
            // auto-register then login
            const reg = await fetch('/api/auth/register/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!reg.ok) throw new Error('register failed');
            resp = await fetch('/api/auth/login/', {
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
        const resp = await fetch('/api/auth/jwt/issue/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: form.value.username || 'anonymous' })
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
    justify-content: center;
    align-items: center;
    height: 100vh;
    background: #f5f5f5;
}
.login-card {
    width: clamp(360px, 90vw, auto);
    padding: 20px;
    box-sizing: border-box;
    overflow: hidden;
}
.row { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.spacer { flex: 1; }
.mb-12 { margin-bottom: 12px; }

.login-card :deep(.el-form),
.login-card :deep(.el-form-item),
.login-card :deep(.el-input),
.login-card :deep(.el-input__wrapper) { width: 100%; }

.login-card :deep(.el-alert__content) { word-break: break-word; }

.login-card :deep(.el-button) { white-space: nowrap; }
</style>
