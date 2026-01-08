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
                            <div class="metric-chip-value">{{ deploymentsCount }}</div>
                            <div class="metric-chip-label">Deployments</div>
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
                <table class="table" v-if="nodes.length">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Status</th>
                            <th>CPU</th>
                            <th>Memory</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="node in nodes" :key="node.name">
                            <td>{{ node.name }}</td>
                            <td>
                                <span :class="['status', node.status === 'Ready' ? 'ok' : 'warn']">
                                    {{ node.status }}
                                </span>
                            </td>
                            <td>{{ perNode[node.name]?.cpu || '-' }}</td>
                            <td>{{ perNode[node.name]?.memory || '-' }}</td>
                            <td>
                                <button
                                    class="mini primary-button"
                                    :disabled="perLoading[node.name]"
                                    @click="loadNode(node.name)"
                                >
                                    {{ perLoading[node.name] ? 'Loading...' : 'Load' }}
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <div v-else class="empty">No nodes found.</div>
            </div>
        </template>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { getClusters, getClusterUsage, getNodes, getNodeUsage, countResources } from '@/utils';
import type { Cluster } from '@/interfaces';

const loading = ref(false);
const currentClusterId = ref('');
const clusters = ref<Cluster[]>([]);
const updatedAt = ref('');

interface ClusterUsage {
    total_cpu?: string;
    used_cpu?: string;
    total_memory?: string;
    used_memory?: string;
    cpu_usage_percent?: number;
    memory_usage_percent?: number;
}
const clusterUsage = ref<ClusterUsage>({});
const cpuPercent = computed(() => clusterUsage.value.cpu_usage_percent ?? 0);
const memPercent = computed(() => clusterUsage.value.memory_usage_percent ?? 0);

const deploymentsCount = ref(0);
const podsCount = ref(0);
const servicesCount = ref(0);

interface Node {
    name: string;
    status: string;
}
const nodes = ref<Node[]>([]);
const perNode = ref<Record<string, { cpu: string; memory: string }>>({});
const perLoading = ref<Record<string, boolean>>({});

const loadClusters = async () => {
    try {
        const data = await getClusters();
        clusters.value = data;
        if (data.length && !currentClusterId.value) {
            currentClusterId.value = String(data[0].id);
        }
    } catch (e) {
        console.error(e);
    }
};

const loadClusterUsage = async () => {
    if (!currentClusterId.value) return;
    try {
        const data = await getClusterUsage(currentClusterId.value);
        clusterUsage.value = data as ClusterUsage;
    } catch (e) {
        console.error(e);
    }
};

const loadNodes = async () => {
    if (!currentClusterId.value) return;
    try {
        const data = await getNodes(currentClusterId.value);
        nodes.value = (data as Node[]) || [];
    } catch (e) {
        console.error(e);
    }
};

const loadPodsServicesCount = async () => {
    if (!currentClusterId.value) return;
    try {
        const data = await countResources(currentClusterId.value);
        const d = data as Record<string, unknown>;
        deploymentsCount.value = (d.deployments as number) || 0;
        podsCount.value = (d.pods as number) || 0;
        servicesCount.value = (d.services as number) || 0;
    } catch {
        deploymentsCount.value = 0;
        podsCount.value = 0;
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

onMounted(() => {
    loadClusters().then(() => {
        if (currentClusterId.value) {
            refreshAll();
        }
    });
});
</script>

<style scoped>
.monitoring-wrapper { width: 100%; display: flex; flex-direction: column; gap: var(--space-4); }
.toolbar { display: flex; align-items: center; gap: 12px; margin: 8px 0 16px; flex-wrap: wrap; }
.select { padding: 6px 8px; }
.updated { color: var(--color-text-muted); font-size: 12px; }
.empty { color: var(--color-text-muted); padding: 8px 0; }

.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; margin-bottom: 20px; }
.card {
    background: var(--glass-bg);
    border-radius: 14px;
    padding: 18px 18px 16px;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--glass-border);
}
.card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
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
    background: var(--color-surface);
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
    background: var(--color-surface);
    border: 1px solid var(--glass-border);
    border-radius: 8px;
}
.kv-label { color: var(--color-text-secondary); }
.kv-value { font-weight: 600; }

.metric-group {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 6px;
}
.metric-chip {
    background: var(--color-surface);
    border: 1px solid var(--glass-border);
    border-radius: 10px;
    padding: 10px;
    text-align: center;
}
.metric-chip-value { font-size: 22px; font-weight: 700; }
.metric-chip-label { font-size: 12px; color: var(--color-text-secondary); }

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
    border-bottom: 1px solid var(--glass-border);
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
    background: rgba(34, 197, 94, 0.12);
    color: #22c55e;
}
.status.warn {
    background: rgba(245, 158, 11, 0.12);
    color: #f59e0b;
}

.primary-button { padding: 6px 12px; margin-left: 0; }
.card-accent.cpu, .card-accent.mem, .card-accent.res { width: auto; }
</style>

