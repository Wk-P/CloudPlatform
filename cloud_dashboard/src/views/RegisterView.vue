<template>
    <div class="register-container">
        <el-card class="register-card">
            <h2>Create your account</h2>
            <el-alert v-if="errorMessage" :title="errorMessage" type="error" show-icon class="mb-12" />
            <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
                <el-form-item label="Username" prop="username">
                    <el-input v-model="form.username" placeholder="Enter username" />
                </el-form-item>
                <el-form-item label="Password" prop="password">
                    <el-input v-model="form.password" type="password" placeholder="Enter password" show-password />
                </el-form-item>

                <div class="row">
                    <div class="spacer" />
                    <el-button :loading="loading" type="primary" @click="submit">Register</el-button>
                    <el-button :disabled="loading" @click="toLogin">Back to Login</el-button>
                </div>
            </el-form>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, type FormInstance } from 'element-plus';
import { URLs } from '@/urls';

const router = useRouter();
const formRef = ref<FormInstance>();
const loading = ref(false);
const errorMessage = ref('');

const form = ref({
    username: '',
    password: '',
});

const rules = {
    username: [
        { required: true, message: 'Please enter username', trigger: 'blur' },
        { min: 2, message: 'At least 2 characters', trigger: 'blur' },
    ],
    password: [
        { required: true, message: 'Please enter password', trigger: 'blur' },
        { min: 4, message: 'At least 4 characters', trigger: 'blur' },
    ],
};

function saveToken(token: string) {
    localStorage.setItem('cloud-dashboard-token', token);
}

const submit = async () => {
    errorMessage.value = '';
    if (formRef.value?.validate) {
        await new Promise<void>((resolve) =>
            formRef.value!.validate!((ok: boolean) => {
                if (ok) resolve();
            }),
        );
    }
    loading.value = true;
    try {
        // 1) register account
        const reg = await fetch(URLs.AUTH_REGISTER, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: form.value.username,
                password: form.value.password,
            }),
        });
        const regData = await reg.json();
        if (!reg.ok || !regData?.token) {
            throw new Error(regData?.detail || 'Register failed');
        }
        saveToken(regData.token);

        ElMessage.success('Registered successfully');
        router.push('/login');
    } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : 'Register failed';
        errorMessage.value = msg;
    } finally {
        loading.value = false;
    }
};

const toLogin = () => router.push('/login');
</script>

<style scoped>
.register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 4vh 2vw;
    background: #f5f5f5;
    min-height: 100vh;
}
.register-card {
    width: clamp(420px, 92vw, 720px);
    padding: 20px;
    box-sizing: border-box;
}
.row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.spacer {
    flex: 1;
}
.mb-12 {
    margin-bottom: 12px;
}
</style>
