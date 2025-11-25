<template>
    <div class="monitoring-wrapper">
        <h2>Resources Monitoring</h2>
        <p>Observe cluster usage and key Kubernetes resources</p>

        <div class="toolbar">
            <label>Cluster:</label>
            <select v-model="currentClusterId" @change="refreshAll" class="select">
                <option v-for="c in clusters" :key="c.id" :value="String(c.id)">{{ c.name || `cluster-${c.id}` }}</option>
            </select>
            <button class="primary-button" :disabled="loading" @click="refreshAll">Refresh</button>
            <span class="updated" v-if="updatedAt">Updated: {{ updatedAt }}</span>
        </div>

        <div v-if="!currentClusterId" class="empty">No cluster. Go to Clusters to add one.</div>

        <template v-else>
            <div class="cards">
                <div class="card card-accent cpu">
                    <div class="card-header">
                        <h3>CPU</h3>
                    </div>
                    <div class="metric-big">{{ cpuPercent }}%</div>
                    <div class="progress">
                        <div class="progress-bar" :style="{ width: cpuPercent + '%' }"></div>
                    </div>
                    <div class="kv-row">
                        <div class="kv-item"><span class="kv-label">Total</span><span class="kv-value">{{ clusterUsage.total_cpu || '-' }}</span></div>
                        <div class="kv-item"><span class="kv-label">Used</span><span class="kv-value">{{ clusterUsage.used_cpu || '-' }}</span></div>
                    </div>
                </div>
                <div class="card card-accent mem">
                    <div class="card-header">
                        <h3>Memory</h3>
                    </div>
                    <div class="metric-big">{{ memPercent }}%</div>
                    <div class="progress">
                        <div class="progress-bar" :style="{ width: memPercent + '%' }"></div>
                    </div>
                    <div class="kv-row">
                        <div class="kv-item"><span class="kv-label">Total</span><span class="kv-value">{{ clusterUsage.total_memory || '-' }}</span></div>
                        <div class="kv-item"><span class="kv-label">Used</span><span class="kv-value">{{ clusterUsage.used_memory || '-' }}</span></div>
                    </div>
                </div>
                <div class="card card-accent res">
                    <div class="card-header">
                        <h3>Resources</h3>
                    </div>
                    <div class="metric-group">
                        <div class="metric-chip">
                            <div class="metric-chip-value">{{ nodes.length }}</div>
                            <div class="metric-chip-label">Nodes</div>
                        </div>
                        <div class="metric-chip">
                            <div class="metric-chip-value">{{ podsCount }}</div>
                            <div class="metric-chip-label">Pods</div>
                        </div>
                        <div class="metric-chip">
                            <div class="metric-chip-value">{{ servicesCount }}</div>
                            <div class="metric-chip-label">Services</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="nodes">
                <h3>Nodes</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Status</th>
                            <th>CPU</th>
                            <th>Memory</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="n in nodes" :key="n.name">
                            <td>{{ n.name }}</td>
                            <td>
                                <span :class="['status', n.status && n.status.toLowerCase() === 'ready' ? 'ok' : 'warn']">
                                    {{ n.status }}
                                </span>
                            </td>
                            <td>{{ perNode[n.name]?.cpu || '-' }}</td>
                            <td>{{ perNode[n.name]?.memory || '-' }}</td>
                            <td>
                                <button class="mini primary-button" :disabled="perLoading[n.name]" @click="loadNode(n.name)">Usage</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </template>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { getResourcesInfo, getClusterUsage, getAllNodesList, getNodeUsage } from '@/utils';
import { useClusterStore } from '@/stores/cluster';

type ClusterItem = { id: number | string; name?: string };
type NodeRow = { name: string; status?: string };

const clusters = ref<ClusterItem[]>([]);
const currentClusterId = ref<string>('');
const clusterUsage = ref<Record<string, string>>({});
const nodes = ref<NodeRow[]>([]);
const perNode = ref<Record<string, { cpu: string; memory: string }>>({});
const perLoading = ref<Record<string, boolean>>({});
const podsCount = ref<number>(0);
const servicesCount = ref<number>(0);
const loading = ref(false);
const updatedAt = ref('');

const clusterStore = useClusterStore();

const cpuPercent = computed<number>(() => {
    const raw = String(clusterUsage.value.cpu_utilization || '').replace('%', '').trim();
    const n = Number(raw);
    if (Number.isFinite(n)) return Math.max(0, Math.min(100, Math.round(n)));
    return 0;
});
const memPercent = computed<number>(() => {
    const raw = String(clusterUsage.value.memory_utilization || '').replace('%', '').trim();
    const n = Number(raw);
    if (Number.isFinite(n)) return Math.max(0, Math.min(100, Math.round(n)));
    return 0;
});

const loadClusters = async () => {
    const resp = await getResourcesInfo('clusters');
    const list: ClusterItem[] = resp?.clusters || [];
    clusters.value = list;
    if (!list.length) {
        currentClusterId.value = '';
        return;
    }
    // try store
    clusterStore.loadCurrentCluster();
    const fromStore = clusterStore.getCurrentCluster?.();
    currentClusterId.value = String(fromStore?.id || list[0].id);
};

const loadClusterUsage = async () => {
    try {
        const resp = await getClusterUsage(currentClusterId.value);
        clusterUsage.value = resp || {};
    } catch (e) {
        console.error(e);
        clusterUsage.value = {};
    }
};

const loadNodes = async () => {
    try {
        const resp = await getAllNodesList(currentClusterId.value);
        const list: Array<{ name: string; status?: string }> = Array.isArray(resp?.nodes) ? resp.nodes : [];
        nodes.value = list.map((n: { name: string; status?: string }) => ({ name: n.name, status: n.status }));
    } catch (e) {
        console.error(e);
        nodes.value = [];
    }
};

const loadPodsServicesCount = async () => {
    try {
        const podsResp = await getResourcesInfo('pods', currentClusterId.value);
        podsCount.value = Array.isArray(podsResp?.pods) ? podsResp.pods.length : 0;
    } catch {
        podsCount.value = 0;
    }
    try {
        const svcResp = await getResourcesInfo('services', currentClusterId.value);
        servicesCount.value = Array.isArray(svcResp?.services) ? svcResp.services.length : 0;
    } catch {
        servicesCount.value = 0;
    }
};

const loadNode = async (name: string) => {
    if (!name) return;
    perLoading.value[name] = true;
    try {
        const data = await getNodeUsage(currentClusterId.value, name);
        if (data) {
            const cpu = `${(data as Record<string, unknown>).used_cpu ?? '?'} / ${(data as Record<string, unknown>).total_cpu ?? '?'}`;
            const memory = `${(data as Record<string, unknown>).used_memory ?? '?'} / ${(data as Record<string, unknown>).total_memory ?? '?'}`;
            perNode.value[name] = { cpu, memory };
        }
    } catch (e) {
        console.error(e);
    } finally {
        perLoading.value[name] = false;
    }
};

const refreshAll = async () => {
    if (!currentClusterId.value) return;
    if (loading.value) return;
    loading.value = true;
    try {
        await Promise.all([loadClusterUsage(), loadNodes(), loadPodsServicesCount()]);
        updatedAt.value = new Date().toLocaleTimeString();
    } finally {
        loading.value = false;
    }
};

onMounted(async () => {
    await loadClusters();
    await refreshAll();
});
</script>

<style scoped>
.monitoring-wrapper {
    width: 100%;
}
.toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 8px 0 16px;
    flex-wrap: wrap;
}
.select {
    padding: 6px 8px;
}
.updated {
    color: #666;
    font-size: 12px;
}
.empty {
    color: #999;
    padding: 8px 0;
}

.cards {
    display: grid;
    grid-template-columns: repeat(3, minmax(260px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}
.card {
    background: #ffffff;
    border-radius: 14px;
    padding: 18px 18px 16px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.06);
    border: 1px solid #eef1f5;
}
.card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}
.card-icon {
    font-size: 22px;
}
.card h3 {
    margin: 0;
    font-size: 18px;
}
.metric-big {
    font-size: 34px;
    font-weight: 700;
    margin: 8px 0 10px;
}
.progress {
    height: 10px;
    width: 100%;
    background: #f1f5f9;
    border-radius: 999px;
    overflow: hidden;
}
.progress-bar {
    height: 100%;
    width: 0%;
    transition: width 0.35s ease;
    background: linear-gradient(90deg, #60a5fa, #2563eb);
}
.card.mem .progress-bar {
    background: linear-gradient(90deg, #fca5a5, #ef4444);
}
.kv-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-top: 12px;
}
.kv-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 10px;
    background: #fafafa;
    border-radius: 8px;
}
.kv-label { color: #6b7280; }
.kv-value { font-weight: 600; }

.metric-group {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 6px;
}
.metric-chip {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
}
.metric-chip-value { font-size: 22px; font-weight: 700; }
.metric-chip-label { font-size: 12px; color: #6b7280; }

.nodes {
    margin-top: 12px;
}
.table {
    width: 100%;
    border-collapse: collapse;
}
.table th,
.table td {
    padding: 8px;
    border-bottom: 1px solid #eee;
    text-align: left;
}
.mini {
    padding: 4px 8px;
}
.status {
    padding: 8px 15px;
    border-radius: 5px;
    font-size: 14px;
}
.status.ok {
    background: #e8f5e9;
    color: #2e7d32;
    font-size: 14px;
}
.status.warn {
    background: #fff3e0;
    color: #ef6c00;
}

.primary-button {
    padding: 6px 12px;
}
.monitoring-view.primary-button {
    margin-left: 0;
}

.card-accent.cpu {
    width: auto;
}

.card-accent.mem {
    width: auto;
}

.card-accent.res {
    width: auto;
}

</style>
