<template>
    <div class="dashboard-wrapper">
        <h2>Dashboard</h2>
        <p>Overview resources information</p>
        <button class="primary-button dashboard-view" @click="windowRefresh">Refresh</button>

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
import { computed, onMounted, ref, watch } from 'vue';
import { windowRefresh } from '@/utils';
import * as echarts from 'echarts';

// interface demo
const sum = ref({
    clusters: {
        sum: 10,
        running: 6,
        down: 4,
    },
    pods: {
        sum: 4,
        active: 2,
        unactive: 2,
    },
    nodes: {
        sum: 5,
        active: 3,
        down: 2,
    },
});

const currentTime = computed(() => new Date().toTimeString());

const drawCharts = () => {
    for (const key in sum.value) {
        const chartDom = document.getElementById(`chart-${key}`);
        if (!chartDom) continue;

        const resChart = echarts.init(chartDom);
        const data = sum.value[key as keyof typeof sum.value];
        resChart.setOption({
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
    }
};

onMounted(() => {
    drawCharts();
});

watch(sum, () => {
    drawCharts();
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
    width: 80%;
    margin: 2rem;
}

.dashboard-card .card-head {
    text-align: center;
}

.dashboard-card .card-body {
    height: 500px;
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
</style>
