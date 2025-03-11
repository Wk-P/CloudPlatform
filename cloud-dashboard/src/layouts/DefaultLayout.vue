<script setup>
import { useRoute, RouterView } from "vue-router";
const route = useRoute();
</script>

<template>
    <el-container>
        <!-- Sidebar Menu -->
        <el-aside width="200px">
            <el-menu :default-active="route.path" router>
                <el-menu-item index="/dashboard">🏠 Dashboard</el-menu-item>
                <el-menu-item index="/clusters">📦 Cluster</el-menu-item>
                <el-menu-item index="/commands">💻 Commands</el-menu-item>
                <el-menu-item index="/monitoring">📊 Monitoring</el-menu-item>
                <el-menu-item index="/users">👤 Users</el-menu-item>
                <el-menu-item index="/help">📖 Help & documents</el-menu-item>
            </el-menu>
        </el-aside>

        <!-- Main Content -->
        <el-container>
            <el-header>
                <h1>Cloud Management Dashboard</h1>
            </el-header>
            <el-main>
                <RouterView />
            </el-main>
        </el-container>
    </el-container>
</template>

<style scoped>
.el-header {
    background-color: #409eff;
    color: white;
    text-align: center;
    font-size: 20px;
    padding: 10px;
}
.el-aside {
    /* background-color: #f5f5f5; */
    height: 100vh;
    border: 1px solid var(--el-menu-border-color);
}

.el-menu {
    border: none;
}
</style>
