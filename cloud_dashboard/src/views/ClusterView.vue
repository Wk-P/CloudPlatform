<template>
    <div class="">
        <button class="primary-button cluster-detail" @click="backToClusters">Back</button>
        <h2>Cluster {{ clusterStore.currentCluster?.id }} Details</h2>

        <div ref="chartDom" style="width: 600px; height: 400px"></div>
    </div>
</template>

<script lang="ts" setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import * as echarts from 'echarts';
import { getClusterUsage } from '@/utils';
import { useClusterStore } from '@/stores/cluster';

const router = useRouter();
const route = useRoute();
const chartDom = ref<HTMLDivElement | null>(null);
let chartInstance: echarts.ECharts | null = null;
const clusterStore = useClusterStore();

const cluster_resources = ref({
    cpu_utilization: '0%',
    memory_utilization: '0%',
    total_cpu: '',
    total_memory: '',
    used_cpu: '',
    used_memory: '',
});

const intervalId = ref();

onMounted(() => {
    const current_cluster_id = route.params.id as string;
    clusterStore.loadCurrentCluster();
    if (chartDom.value) {
        chartInstance = echarts.init(chartDom.value);
    }

    const updateChart = async () => {
        const data = await getClusterUsage(current_cluster_id);
        Object.assign(cluster_resources.value, data);

        if (chartInstance) {
            chartInstance.setOption({
                title: {
                    text: 'Cluster Resource Utilization',
                },
                tooltip: {},
                xAxis: {
                    type: 'category',
                    data: ['CPU', 'Memory'],
                },
                yAxis: {
                    type: 'value',
                },
                series: [
                    {
                        name: 'Utilization',
                        type: 'bar',
                        data: [
                            parseFloat(data.cpu_utilization.replace('%', '')),
                            parseFloat(data.memory_utilization.replace('%', '')),
                        ],
                    },
                ],
            });
        }
    };

    // 初始化 & 定时更新
    updateChart();
    intervalId.value = setInterval(updateChart, 10000);
});

onUnmounted(() => {
    clearInterval(intervalId.value);
    if (chartInstance) {
        chartInstance.dispose();
    }
});

const backToClusters = () => {
    router.push({ name: 'clusters' });
};
</script>

<style scoped>
.primary-button.cluster-detail {
    margin-left: 0;
}
</style>
