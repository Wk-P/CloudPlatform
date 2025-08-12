import { ref } from "vue";
import type { Cluster } from "@/interfaces";
import { defineStore } from "pinia";

export const useClusterStore = defineStore('cluster', () => {
    const currentCluster = ref<Cluster | null>(null);
    const localStoragePreStr = 'cloud-dashboard-';

    const setCurrentCluster = (cluster: Cluster) => {
        currentCluster.value = cluster;

        localStorage.setItem(`${localStoragePreStr}current-cluster`, JSON.stringify(currentCluster.value));
    }

    const getCurrentCluster = () => {
        return currentCluster.value;
    }

    const removeCurrentCluster = () => {
        currentCluster.value = null;
        localStorage.removeItem(`${localStoragePreStr}current-cluster`);
    }

    const loadCurrentCluster = () => {
        const localStorageCurrentCluster = localStorage.getItem(`${localStoragePreStr}current-cluster`);
        if (localStorageCurrentCluster) currentCluster.value = JSON.parse(localStorageCurrentCluster);
    }

    return {
        currentCluster, setCurrentCluster, getCurrentCluster, removeCurrentCluster, loadCurrentCluster
    }
})