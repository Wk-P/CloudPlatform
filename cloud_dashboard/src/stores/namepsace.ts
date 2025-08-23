import { ref } from 'vue';
import type { Namespace } from '@/interfaces';
import { defineStore } from 'pinia';

export const useNamespaceStore = defineStore('namespace', () => {
    const currentNamespace = ref<Namespace | null>(null);
    const localStoragePreStr = 'cloud-dashboard-';

    const setCurrentNamespace = (ns: Namespace) => {
        currentNamespace.value = ns;
        localStorage.setItem(`${localStoragePreStr}current-namespace`, JSON.stringify(currentNamespace.value));
    };

    const getCurrentNamespace = () => {
        return currentNamespace.value;
    };

    const removeCurrentNamespace = () => {
        currentNamespace.value = null;
        localStorage.removeItem(`${localStoragePreStr}current-namespace`);
    };

    const loadCurrentNamespace = () => {
        const cached = localStorage.getItem(`${localStoragePreStr}current-namespace`);
        if (cached) currentNamespace.value = JSON.parse(cached);
    };

    return {
        currentNamespace,
        setCurrentNamespace,
        getCurrentNamespace,
        removeCurrentNamespace,
        loadCurrentNamespace,
    };
});
