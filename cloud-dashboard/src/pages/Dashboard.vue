<template>
    <div>
        <h2>🏠 Cluster Management</h2>
        <p>Manage Kubernetes and OpenStack clusters here.</p>

        <el-row :gutter="20">
            <el-col :span="6">
                <el-card>
                    <h3>🖥️ Clusters</h3>
                    <p>{{ clusterCount }}</p>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card>
                    <h3>🚀 Running Pods</h3>
                    <p>{{ runningPods }}</p>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card>
                    <h3>📦 Running VMs</h3>
                    <p>{{ runningVMs }}</p>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card>
                    <h3>🌍 Network traffic</h3>
                    <p>{{ networkUsage }} Mbps</p>
                </el-card>
            </el-col>
        </el-row>

        <el-divider />

        <el-row>
            <el-col :span="12">
                <el-card>
                    <h3>📊 Resources usage</h3>
                    <el-progress :percentage="cpuUsage" text-inside status="success"></el-progress>
                    <el-progress :percentage="memoryUsage" text-inside status="warning"></el-progress>
                    <el-progress :percentage="storageUsage" text-inside status="exception"></el-progress>
                </el-card>
            </el-col>
            <el-col :span="12">
                <el-card>
                    <h3>🔥 Active services</h3>
                    <el-table :data="activeServices" border>
                        <el-table-column prop="name" label="service"></el-table-column>
                        <el-table-column prop="status" label="status">
                            <template #default="{ row }">
                                <el-tag :type="row.status === 'running' ? 'success' : 'danger'">
                                    {{ row.status }}
                                </el-tag>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script setup>
import { ref } from "vue";

const clusterCount = ref(3);
const runningPods = ref(125);
const runningVMs = ref(40);
const networkUsage = ref(1200); // Mbps

const cpuUsage = ref(65);
const memoryUsage = ref(80);
const storageUsage = ref(45);

const activeServices = ref([
    { name: "Kubernetes API", status: "running" },
    { name: "OpenStack Compute", status: "running" },
    { name: "Load Balancer", status: "error" },
]);
</script>

<style scoped>
.el-card {
    text-align: center;
    padding: 15px;
}
</style>
