<template>
    <div>
        <h2>📊 Resources monitoring</h2>
        <p>Check Kubernetes and OpenStack Resources information</p>

        <el-row :gutter="20">
            <el-col :span="8">
                <el-card>
                    <h3>CPU usage</h3>
                    <p>{{ cpuUsage }}%</p>
                </el-card>
            </el-col>

            <el-col :span="8">
                <el-card>
                    <h3>Memory usage</h3>
                    <p>{{ memoryUsage }}%</p>
                </el-card>
            </el-col>

            <el-col :span="8">
                <el-card>
                    <h3>Disk usage</h3>
                    <p>{{ storageUsage }}%</p>
                </el-card>
            </el-col>
        </el-row>

        <el-button type="primary" @click="fetchMetrics">Refresh</el-button>
    </div>
</template>

<script setup>
import { ref } from "vue";

const cpuUsage = ref(0);
const memoryUsage = ref(0);
const storageUsage = ref(0);

const fetchMetrics = () => {
    // TODO: get data from backend api
    cpuUsage.value = Math.floor(Math.random() * 100);
    memoryUsage.value = Math.floor(Math.random() * 100);
    storageUsage.value = Math.floor(Math.random() * 100);
};
</script>

<style scoped>
.el-card {
    text-align: center;
    font-size: 18px;
    padding: 10px;
}
</style>
