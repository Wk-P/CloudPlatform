<template>
    <div>
        <h2>Resources monitoring</h2>
        <p>Check Kubernetes Resources information</p>

        <button class="primary-button monitoring-view" @click="fetchMetrics">Refresh</button>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

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
.monitoring-view.primary-button {
    margin-left: 0;
}
</style>
