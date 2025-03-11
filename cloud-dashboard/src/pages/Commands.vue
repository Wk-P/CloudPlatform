<template>
    <div>
        <h2>💻 Commands Console</h2>
        <p>Here run Kubernetes and OpenStack Commands.</p>

        <el-input v-model="command" placeholder="Enter kubectl or openstack commands" @keyup.enter="executeCommand"></el-input>

        <el-button type="primary" @click="executeCommand">RUN</el-button>

        <el-card class="command-output">
            <p v-if="output">📜 Result </p>
            <pre>{{ output }}</pre>
        </el-card>
    </div>
</template>

<script setup>
import { ref } from "vue";

const command = ref("");
const output = ref("");

const executeCommand = () => {
    if (!command.value) return;

    // TODO: backend apis run commands
    output.value = `Running command: ${command.value} ...\n(result waiting)`;
    command.value = ""; // blank input block
};
</script>

<style scoped>
.command-output {
    margin-top: 20px;
    padding: 10px;
    background-color: #f5f5f5;
    border-radius: 8px;
}
</style>
