import { ref } from 'vue';
import type { Namespace } from '@/interfaces';
import { defineStore } from 'pinia';

export const useNamespaceStore = defineStore('namespace', () => {
    const currentNamespace = ref<Namespace | null>(null);
    const localStoragePreStr = 'cloud-dashboard-';

    const setCurrentNamespace = (cluster: Namespace) => {
        currentNamespace.value = cluster;

        localStorage.setItem(`${localStoragePreStr}current-cluster`, JSON.stringify(currentNamespace.value));
    };

    const getCurrentNamespace = () => {
        return currentNamespace.value;
    };

    const removeCurrentNamespace = () => {
        currentNamespace.value = null;
        localStorage.removeItem(`${localStoragePreStr}current-cluster`);
    };

    const loadCurrentNamespace = () => {
        const localStorageCurrentNamespace = localStorage.getItem(`${localStoragePreStr}current-cluster`);
        if (localStorageCurrentNamespace) currentNamespace.value = JSON.parse(localStorageCurrentNamespace);
    };

    return {
        currentNamespace,
        setCurrentNamespace,
        getCurrentNamespace,
        removeCurrentNamespace,
        loadCurrentNamespace,
    };
});
