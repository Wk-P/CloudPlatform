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

const handleLogin = () => {
    if (form.value.username && form.value.password) {
        router.push('/dashboard');
    } else {
        alert('Please enter password');
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
