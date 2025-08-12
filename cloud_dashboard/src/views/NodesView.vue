<template>
    <div class="nodes-view-wrapper">
        <h2>Nodes Details of Cluster {{ clusterStore.currentCluster?.id }}</h2>
        <p>
            <span>Namespace: {{ namespaceStore.currentNamespace?.name }}</span>
        </p>

        <div class="nodes-list">
            <table>

            </table>
        </div>
    </div>
</template>
<script lang="ts" setup>
import { useClusterStore } from '@/stores/cluster';
import { useNamespaceStore } from '@/stores/namepsace';
import { onMounted } from 'vue';

const clusterStore = useClusterStore();
const namespaceStore = useNamespaceStore();

onMounted(() => {
    clusterStore.loadCurrentCluster();
    namespaceStore.loadCurrentNamespace();
});

</script>
<style scoped></style>
