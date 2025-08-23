<template>
    <div class="login-container">
        <el-card class="login-card">
            <h2>Login to cloud admin management</h2>
            <el-form ref="loginForm" :model="form" label-width="80px">
                <el-form-item label="username">
                    <el-input v-model="form.username" placeholder="Enter username"></el-input>
                </el-form-item>
                <el-form-item label="password">
                    <el-input
                        v-model="form.password"
                        type="password"
                        placeholder="Enter password"
                    ></el-input>
                </el-form-item>
                <el-button type="primary" @click="handleLogin">Login</el-button>
            </el-form>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const form = ref({ username: '', password: '' });
const router = useRouter();

const handleLogin = async () => {
    try {
        const resp = await fetch('/api/auth/jwt/issue/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: form.value.username || 'anonymous' }),
        });
        const data = await resp.json();
        if (data?.token) {
            localStorage.setItem('cloud-dashboard-token', data.token);
            router.push('/dashboard');
        } else {
            alert('Login failed');
        }
    } catch {
        alert('Login failed');
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
    width: 400px;
    padding: 20px;
}
</style>
