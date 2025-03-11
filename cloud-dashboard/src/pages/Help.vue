<template>
    <div>
        <h2>📖 Help Documentation</h2>
        <p>Find guidelines on how to use the Cloud Management Platform here.</p>

        <el-collapse>
            <el-collapse-item title="How to manage Kubernetes clusters?" name="1">
                <p>Go to the <strong>Cluster Management</strong> page to view all Kubernetes clusters and perform scaling, deletion, and other operations.</p>
            </el-collapse-item>

            <el-collapse-item title="How to execute commands?" name="2">
                <p>In the <strong>Command Console</strong> page, you can execute <code>kubectl</code> and <code>openstack</code> commands to manage your cloud resources.</p>
            </el-collapse-item>

            <el-collapse-item title="How to monitor cluster resources?" name="3">
                <p>Navigate to the <strong>Resource Monitoring</strong> page to check CPU, memory, and storage usage.</p>
            </el-collapse-item>

            <el-collapse-item title="How to manage users?" name="4">
                <p>In the <strong>User Management</strong> page, you can add new users and assign permissions.</p>
            </el-collapse-item>

            <el-collapse-item title="How to get technical support?" name="5">
                <p>If you encounter any issues, contact the administrator or check the FAQ section below.</p>
            </el-collapse-item>
        </el-collapse>
    </div>
</template>

<script setup></script>

<style scoped>
.el-collapse-item {
    margin-bottom: 10px;
}
</style>
