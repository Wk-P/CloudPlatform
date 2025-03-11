<template>
  <div>
    <h2>📦 Cluster management</h2>
    <p>Manage Kubernetes and OpenStack clusters </p>

    <el-table :data="clusters" border style="margin-top: 20px;">
      <el-table-column prop="name" label="clusters"></el-table-column>
      <el-table-column prop="nodes" label="nodes"></el-table-column>
      <el-table-column prop="cpu" label="CPU-usage"></el-table-column>
      <el-table-column prop="memory" label="memory-usage"></el-table-column>
      <el-table-column prop="status" label="status">
        <template #default="{ row }">
          <el-tag :type="row.status === 'running' ? 'success' : 'danger'">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="operation">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewCluster(row)">View</el-button>
          <el-button type="danger" size="small" @click="deleteCluster(row.id)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-button type="primary" @click="fetchClusters">Refresh</el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const clusters = ref([
  { id: 1, name: 'K8s-Cluster-1', nodes: 5, cpu: '70%', memory: '60%', status: 'running' },
  { id: 2, name: 'OpenStack-Cluster-1', nodes: 3, cpu: '50%', memory: '40%', status: 'running' },
  { id: 3, name: 'Test-Cluster', nodes: 2, cpu: '85%', memory: '90%', status: 'error' },
]);

const fetchClusters = () => {
  // TODO: Get data from api of backend
  console.log('Fetching cluster data...');
};

const viewCluster = (cluster) => {
  alert(`View details of ${cluster.name}`);
};

const deleteCluster = (id) => {
  clusters.value = clusters.value.filter(cluster => cluster.id !== id);
};
</script>

<style scoped>
.el-table {
  margin-top: 20px;
}
</style>
