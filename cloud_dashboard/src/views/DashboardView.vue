<template>
    <div class="dashboard-wrapper">
        <div class="action-bar">
            <div class="action-meta">
                <h2>Dashboard</h2>
                <p class="updated">Last updated: {{ updatedAt || '—' }}</p>
            </div>
            <button class="primary-button" :disabled="loading" @click="loadDashboard">
                {{ loading ? 'Refreshing...' : 'Refresh' }}
            </button>
        </div>

        <div class="card-wrapper">
            <div class="dashboard-card glass-card">
                <div class="card-head">
                    <h3>Clusters</h3>
                    <p class="card-sub">Registered cluster count</p>
                </div>
                <div class="card-body">
                    <div class="metric">{{ sum.clusters.sum }}</div>
                    <div class="metric-sub">Running {{ sum.clusters.running }} · Offline {{ sum.clusters.down }}</div>
                </div>
            </div>

            <div class="dashboard-card glass-card">
                <div class="card-head">
                    <h3>Nodes</h3>
                    <p class="card-sub">Nodes in current cluster</p>
                </div>
                <div class="card-body">
                    <div class="metric">{{ sum.nodes.sum }}</div>
                    <div class="metric-sub">Active {{ sum.nodes.active }} · Unhealthy {{ sum.nodes.down }}</div>
                </div>
            </div>

            <div class="dashboard-card glass-card">
                <div class="card-head">
                    <h3>Pods</h3>
                    <p class="card-sub">Workload status</p>
                </div>
                <div class="card-body">
                    <div class="metric">{{ sum.pods.sum }}</div>
                    <div class="metric-sub">Running {{ sum.pods.active }} · Not running {{ sum.pods.unactive }}</div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue';
import { getResourcesInfo } from '@/utils';
import { useClusterStore } from '@/stores/cluster';

const clusterStore = useClusterStore();

type SumState = {
    clusters: { sum: number; running: number; down: number };
    nodes: { sum: number; active: number; down: number };
    pods: { sum: number; active: number; unactive: number };
};

const sum = reactive<SumState>({
    clusters: { sum: 0, running: 0, down: 0 },
    nodes: { sum: 0, active: 0, down: 0 },
    pods: { sum: 0, active: 0, unactive: 0 },
});

const loading = ref(false);
const updatedAt = ref('');
const currentClusterId = ref<string | number | null>(null);

const loadDashboard = async () => {
    if (loading.value) return;
    loading.value = true;
    try {
        const clustersResp = await getResourcesInfo('clusters');
        const clusters = clustersResp?.clusters || [];
        const clustersCount = Array.isArray(clusters) ? clusters.length : 0;
        sum.clusters = { sum: clustersCount, running: clustersCount, down: 0 };

        clusterStore.loadCurrentCluster();
        const fromStore = clusterStore.getCurrentCluster?.();
        
        // 优先使用 store 中的 cluster，确保与其他页面一致
        if (fromStore && clusters.some((c: any) => c.id === fromStore.id)) {
            currentClusterId.value = fromStore.id;
        } else if (clusters[0]) {
            currentClusterId.value = clusters[0].id;
            clusterStore.setCurrentCluster(clusters[0]);
        } else {
            currentClusterId.value = null;
        }

        if (currentClusterId.value) {
            const nodesResp = await getResourcesInfo('nodes', String(currentClusterId.value));
            const nodes: Array<{ status?: string }> = nodesResp?.nodes || [];
            const nodesSum = nodes.length;
            const nodesActive = nodes.filter((n) => (n.status || '').toLowerCase() === 'ready').length;
            const nodesDown = Math.max(0, nodesSum - nodesActive);
            sum.nodes = { sum: nodesSum, active: nodesActive, down: nodesDown };

            const podsResp = await getResourcesInfo('pods', String(currentClusterId.value));
            const pods: Array<{ status?: string }> = podsResp?.pods || [];
            const podsSum = pods.length;
            const activeStatuses = new Set(['running', 'succeeded']);
            const podsActive = pods.filter((p) => activeStatuses.has((p.status || '').toLowerCase())).length;
            const podsUnactive = Math.max(0, podsSum - podsActive);
            sum.pods = { sum: podsSum, active: podsActive, unactive: podsUnactive };
        } else {
            sum.nodes = { sum: 0, active: 0, down: 0 };
            sum.pods = { sum: 0, active: 0, unactive: 0 };
        }

        updatedAt.value = new Date().toLocaleTimeString();
    } catch (e) {
        console.error(e);
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    loadDashboard();
});
</script>

<style scoped>
.dashboard-wrapper { display: flex; flex-direction: column; gap: var(--space-4); }
.action-bar { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); }
.action-meta { display: flex; flex-direction: column; gap: var(--space-1); }
.updated { color: var(--color-text-muted); font-size: 0.9rem; }

.card-wrapper { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: var(--space-4); width: 100%; }
.dashboard-card { width: 100%; padding: var(--space-6); border-radius: var(--radius-lg); background: var(--glass-bg); border: 1px solid var(--glass-border); box-shadow: var(--shadow-sm); }
.card-head h3 { margin: 0; }
.card-sub { color: var(--color-text-muted); font-size: 0.9rem; margin-top: 4px; }
.card-body { display: flex; flex-direction: column; gap: var(--space-2); align-items: flex-start; }
.metric { font-size: 2.4rem; font-weight: 700; }
.metric-sub { color: var(--color-text-secondary); }
</style>
