<template>
    <div class="cluster-view">
        <div class="toolbar">
            <button class="primary-button cluster-detail" @click="backToClusters">Back</button>
            <h2>Cluster {{ clusterId }} Details</h2>
            <div class="id-box">
                <span>ID: <code class="mono">{{ clusterId }}</code></span>
                <span v-if="clusterStore.currentCluster?.cluster_id">UUID: <code class="mono">{{ clusterStore.currentCluster?.cluster_id }}</code></span>
                <button class="secondary-small-button" @click="copyToClipboard(clusterId)">Copy ID</button>
                <button v-if="clusterStore.currentCluster?.cluster_id" class="secondary-small-button" @click="copyToClipboard(clusterStore.currentCluster!.cluster_id)">Copy UUID</button>
            </div>
            <div class="spacer" />
            <label>
                Namespace:
                <select v-model="filters.namespace" @change="reloadPodsAndDeployments">
                    <option value="">All</option>
                    <option v-for="ns in namespaces" :key="ns.name" :value="ns.name">{{ ns.name }}</option>
                </select>
            </label>
            <label>
                Label:
                <input class="default-input" v-model="filters.labelSelector" placeholder="key=value" @keyup.enter="reloadPodsAndDeployments" />
            </label>
            <button class="primary-small-button" @click="reloadAll">Refresh</button>
        </div>

        <div class="content">
            <div class="left">
                <div class="panel">
                    <h3>Nodes</h3>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="n in nodes" :key="n.name">
                                <td>{{ n.name }}</td>
                                <td>
                                    <span :class="['status', (n.status || '').toLowerCase()==='ready' ? 'ok' : 'warn']">{{ n.status }}</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="panel">
                    <h3>Pods</h3>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Namespace</th>
                                <th>Name</th>
                                <th>Status</th>
                                <th>Node</th>
                                <th>Restarts</th>
                                <th>Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="p in pods" :key="p.namespace + '/' + p.name">
                                <td>{{ p.namespace }}</td>
                                <td>{{ p.name }}</td>
                                <td>{{ p.status }}</td>
                                <td>{{ p.node }}</td>
                                <td>{{ p.restarts }}</td>
                                <td>{{ p.created_at }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="right">
                <div class="panel">
                    <h3>Cluster Resource Utilization</h3>
                    <div ref="chartDom" class="chart"></div>
                    <div class="kv">
                        <div>Total CPU: {{ clusterResources.total_cpu }}</div>
                        <div>Used CPU: {{ clusterResources.used_cpu }}</div>
                        <div>Total Memory: {{ clusterResources.total_memory }}</div>
                        <div>Used Memory: {{ clusterResources.used_memory }}</div>
                    </div>
                </div>

                <div class="panel">
                    <h3>Deployments</h3>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Namespace</th>
                                <th>Name</th>
                                <th>Replicas</th>
                                <th>Ready</th>
                                <th>Updated</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="d in deployments" :key="d.namespace + '/' + d.name">
                                <td>{{ d.namespace }}</td>
                                <td>{{ d.name }}</td>
                                <td>{{ d.replicas }}</td>
                                <td>{{ d.ready }}</td>
                                <td>{{ d.updated }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import * as echarts from 'echarts';
import { getClusterUsage, getResourcesInfo } from '@/utils';
import { useClusterStore } from '@/stores/cluster';

const router = useRouter();
const route = useRoute();
const chartDom = ref<HTMLDivElement | null>(null);
let chartInstance: echarts.ECharts | null = null;
const clusterStore = useClusterStore();

const clusterResources = ref({
    cpu_utilization: '0%',
    memory_utilization: '0%',
    total_cpu: '',
    total_memory: '',
    used_cpu: '',
    used_memory: '',
});

const clusterId = ref<string>('');

const namespaces = ref<Array<{ name: string; status?: string }>>([]);
const nodes = ref<Array<{ name: string; status?: string }>>([]);
const pods = ref<Array<{ namespace: string; name: string; status?: string; node?: string; restarts?: number; created_at?: string }>>([]);
const deployments = ref<Array<{ namespace: string; name: string; replicas?: number; ready?: number; updated?: number }>>([]);

const filters = ref<{ namespace: string; labelSelector: string }>({ namespace: '', labelSelector: '' });

const loadNamespaces = async () => {
    if (!clusterId.value) return;
    const resp = await getResourcesInfo('namespaces', clusterId.value);
    namespaces.value = resp?.namespaces || [];
};

const loadNodes = async () => {
    if (!clusterId.value) return;
    const resp = await getResourcesInfo('nodes', clusterId.value);
    nodes.value = resp?.nodes || [];
};

const loadPods = async () => {
    if (!clusterId.value) return;
    const params: Record<string, string> = {};
    if (filters.value.namespace) params.namespace = filters.value.namespace;
    if (filters.value.labelSelector) params.labelSelector = filters.value.labelSelector;
    const resp = await getResourcesInfo('pods', clusterId.value, params);
    pods.value = resp?.pods || [];
};

const loadDeployments = async () => {
    if (!clusterId.value) return;
    const params: Record<string, string> = {};
    if (filters.value.namespace) params.namespace = filters.value.namespace;
    if (filters.value.labelSelector) params.labelSelector = filters.value.labelSelector;
    const resp = await getResourcesInfo('deployments', clusterId.value, params);
    deployments.value = resp?.deployments || [];
};

const drawChart = () => {
    if (!chartDom.value) return;
    if (!chartInstance) chartInstance = echarts.init(chartDom.value);
    const cpu = parseFloat((clusterResources.value.cpu_utilization || '0').toString().replace('%', '')) || 0;
    const mem = parseFloat((clusterResources.value.memory_utilization || '0').toString().replace('%', '')) || 0;
    chartInstance.setOption({
        title: { text: 'Cluster Resource Utilization' },
        tooltip: {},
        xAxis: { type: 'category', data: ['CPU', 'Memory'] },
        yAxis: { type: 'value', min: 0, max: 100 },
        series: [{ name: 'Utilization', type: 'bar', data: [cpu, mem] }],
    });
    chartInstance.resize();
};

const reloadUsage = async () => {
    if (!clusterId.value) return;
    const data = await getClusterUsage(clusterId.value);
    if (data) Object.assign(clusterResources.value, data);
    drawChart();
};

const reloadPodsAndDeployments = async () => {
    await Promise.all([loadPods(), loadDeployments()]);
};

const reloadAll = async () => {
    await Promise.all([loadNamespaces(), loadNodes(), reloadPodsAndDeployments(), reloadUsage()]);
};

const intervalId = ref<number | undefined>();
let resizeHandler: (() => void) | null = null;

onMounted(async () => {
    clusterStore.loadCurrentCluster();
    const routeId = (route.params.id as string) || clusterStore.currentCluster?.id;
    if (!routeId) {
        // 没有集群，返回列表
        backToClusters();
        return;
    }
    clusterId.value = String(routeId);

    await reloadAll();

    // 定时刷新资源使用
    intervalId.value = window.setInterval(reloadUsage, 10000);

    const onResize = () => chartInstance && chartInstance.resize();
    window.addEventListener('resize', onResize);
    resizeHandler = onResize;
});

onUnmounted(() => {
    if (intervalId.value) window.clearInterval(intervalId.value);
    if (resizeHandler) window.removeEventListener('resize', resizeHandler);
    if (chartInstance) chartInstance.dispose();
});

const backToClusters = () => {
    router.push({ name: 'clusters' });
};

function copyToClipboard(text: string) {
    if (!text) return;
    navigator.clipboard?.writeText(String(text)).then(() => {
        // no-op
    });
}
</script>

<style scoped>
.cluster-view {
    display: flex;
    flex-direction: column;
}
.toolbar {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.toolbar .spacer { flex: 1; }
.content {
    display: grid;
    grid-template-columns: 1.1fr 1fr;
    gap: 1.5rem;
    margin-top: 1rem;
}
.panel { background: #fff; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
.chart { width: 100%; height: 320px; }
.status.ok { color: #2ecc71; font-weight: 600; }
.status.warn { color: #e67e22; font-weight: 600; }
.primary-button.cluster-detail { margin-left: 0; }
.id-box { display: flex; align-items: center; gap: 0.5rem; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
</style>
