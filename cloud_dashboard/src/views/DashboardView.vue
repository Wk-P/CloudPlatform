<template>
    <div class="dashboard-wrapper">
        <h2>Dashboard</h2>
        <p>Overview resources information</p>
        <div class="action-bar">
            <button class="primary-button" @click="loadDashboard">Refresh</button>
        </div>

        <div class="card-wrapper">
            <div class="dashboard-card card" v-for="(value, key) in sum" :key="key">
                <!-- resource name -->
                <h3 class="card-head">{{ key }}</h3>

                <!-- sum and status -->
                <div class="card-body">
                    <div class="cb-sub" v-for="(sv, sk) in value" :key="sk">
                        <div>{{ sk }}</div>
                        <div>{{ sv }}</div>
                    </div>
                    <div :id="`chart-${key}`" style="width: 300px; height: 210px"></div>
                </div>
                <!-- data updated time -->
                <div class="card-foot">
                    <span>Update Time: </span>
                    <span>{{ currentTime }}</span>
                </div>
            </div>
        </div>
    </div>
</template>
<script lang="ts" setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue';
import { getResourcesInfo } from '@/utils';
import * as echarts from 'echarts';
import { useClusterStore } from '@/stores/cluster';

// interface demo
const sum = ref<{ [k: string]: Record<string, number> }>({
    clusters: { sum: 0, running: 0, down: 0 },
    pods: { sum: 0, active: 0, unactive: 0 },
    nodes: { sum: 0, active: 0, down: 0 },
});

const clusterStore = useClusterStore();
const currentClusterId = ref<string | null>(null);
const loading = ref(false);

// live clock
const currentTime = ref<string>('');
let clockTimer: number | undefined;

const chartsMap: Record<string, echarts.ECharts> = {};

const drawCharts = () => {
    for (const key in sum.value) {
        const chartDom = document.getElementById(`chart-${key}`);
        if (!chartDom) continue;

        // reuse instance if exists; otherwise init
        let inst = echarts.getInstanceByDom(chartDom as HTMLDivElement);
        if (!inst) {
            inst = echarts.init(chartDom);
            chartsMap[key] = inst;
        }
        const data = sum.value[key as keyof typeof sum.value];
        inst.setOption({
            tooltip: {},
            xAxis: {
                type: 'category',
                data: Object.keys(data),
                axisLine: {
                    lineStyle: {
                        color: '#333',
                        width: 2,
                    },
                },
                axisTick: {
                    alignWithLabel: true,
                    lineStyle: {
                        color: '#333',
                    },
                },
                axisLabel: {
                    color: '#555',
                    fontSize: 12,
                },
            },
            yAxis: {
                type: 'value',
                min: 0,
                axisLine: {
                    lineStyle: {
                        color: '#333',
                        width: 2,
                    },
                },
                axisTick: {
                    lineStyle: {
                        color: '#333',
                    },
                },
                axisLabel: {
                    color: '#555',
                    fontSize: 12,
                },
                splitLine: {
                    lineStyle: {
                        type: 'dashed',
                        color: '#ccc',
                    },
                },
            },
            series: [
                {
                    data: Object.values(data),
                    type: 'bar',
                    itemStyle: {
                        color: '#409EFF', // bar color
                        borderRadius: [4, 4, 0, 0],
                    },
                },
            ],
        });
        inst.resize();
    }
};

const loadDashboard = async () => {
    if (loading.value) return;
    loading.value = true;
    try {
        // 1) clusters
        const clustersResp = await getResourcesInfo('clusters');
        const clusters = clustersResp?.clusters || [];
        const clustersCount = Array.isArray(clusters) ? clusters.length : 0;
        // naive running/down: assume registered clusters are running (0 down) for now
        sum.value.clusters = { sum: clustersCount, running: clustersCount, down: 0 };

        // resolve target cluster id
        clusterStore.loadCurrentCluster();
        const fromStore = clusterStore.getCurrentCluster?.();
        currentClusterId.value = fromStore?.id || (clusters[0]?.id ?? null);

        if (currentClusterId.value) {
            // 2) nodes of the cluster
            const nodesResp = await getResourcesInfo('nodes', String(currentClusterId.value));
            const nodes: Array<{ status?: string }> = nodesResp?.nodes || [];
            const nodesSum = nodes.length;
            // backend returns status string; treat 'Ready' as active
            const nodesActive = nodes.filter((n) => (n.status || '').toLowerCase() === 'ready').length;
            const nodesDown = Math.max(0, nodesSum - nodesActive);
            sum.value.nodes = { sum: nodesSum, active: nodesActive, down: nodesDown };

            // 3) pods of the cluster
            const podsResp = await getResourcesInfo('pods', String(currentClusterId.value));
            const pods: Array<{ status?: string }> = podsResp?.pods || [];
            const podsSum = pods.length;
            const activeStatuses = new Set(['running', 'succeeded']);
            const podsActive = pods.filter((p) => activeStatuses.has((p.status || '').toLowerCase())).length;
            const podsUnactive = Math.max(0, podsSum - podsActive);
            sum.value.pods = { sum: podsSum, active: podsActive, unactive: podsUnactive };
        } else {
            // no clusters
            sum.value.nodes = { sum: 0, active: 0, down: 0 };
            sum.value.pods = { sum: 0, active: 0, unactive: 0 };
        }
    } catch (e: unknown) {
        console.error(e);
        let status = 0;
        // axios error
        if (typeof e === 'object' && e !== null) {
            // axios: { response: { status: number } }
            if ('response' in e && typeof (e as { response?: { status?: number } }).response?.status === 'number') {
                status = (e as { response: { status: number} }).response.status;
            }
            // fetch: { status: number }
            else if ('status' in e && typeof (e as { status?: number }).status === 'number') {
                status = (e as { status: number }).status;
            }
            // backend custom error: { error: string }
            else if ('error' in e && typeof (e as { error?: string }).error === 'string') {
                if ((e as { error: string }).error.includes('500')) status = 500;
            }
        }
        if (status === 500) {
            if (typeof window !== 'undefined' && 'ElMessage' in window && typeof window.ElMessage === 'function') {
                window.ElMessage('Internal Server Error (500)', { type: 'error' });
            } else {
                alert('Internal Server Error (500)');
            }
        }
    } finally {
        loading.value = false;
        drawCharts();
    }
};



onMounted(() => {
    // start clock
    const updateClock = () => {
        const d = new Date();
        const pad = (n: number) => String(n).padStart(2, '0');
        currentTime.value = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
    };
    updateClock();
    clockTimer = window.setInterval(updateClock, 1000);

    loadDashboard();
    // responsive
    const onResize = () => {
        Object.values(chartsMap).forEach((c) => c.resize());
    };
    window.addEventListener('resize', onResize);
    resizeHandler = onResize;
});

watch(sum, () => {
    drawCharts();
});

let resizeHandler: (() => void) | null = null;

onBeforeUnmount(() => {
    if (clockTimer) window.clearInterval(clockTimer);
    if (resizeHandler) window.removeEventListener('resize', resizeHandler);
    Object.values(chartsMap).forEach((c) => c.dispose());
});
</script>
<style scoped>
.card-wrapper {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    width: 100%;
    justify-content: space-evenly;
}
.dashboard-card {
    width: 90%;
    margin: 2rem;
}

.dashboard-card .card-head {
    text-align: center;
}

.dashboard-card .card-body {
    min-height: 360px;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem 0;
}

.dashboard-card .card-body .cb-sub {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    width: 80%;
    margin-bottom: 1rem;
}

.dashboard-card .card-foot {
    color: #666;
}

.primary-button.dashboard-view {
    margin-left: 0;
}
.action-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
}
.danger-button {
    background-color: #e03e2f;
    color: #fff;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
}
.danger-button:hover {
    background-color: #c73527;
}
</style>
