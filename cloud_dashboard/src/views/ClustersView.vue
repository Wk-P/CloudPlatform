<template>
    <div class="clusters-page">
        <div class="header">
            <div>
                <h2>Clusters Management</h2>
                <p>Manage Kubernetes clusters</p>
            </div>
            <button class="primary-button" @click="showForm('register')">Register New Cluster</button>
        </div>

    <div v-if="loading" class="loading">Loading clusters...</div>
        <div v-else-if="!clustsersInfo.length" class="empty">No clusters yet. Click "Register New Cluster" to add one.</div>

        <table v-else class="clusters-info-table">
            <thead>
                <tr>
                    <th>Cluster ID</th>
                    <th>Cluster Name</th>
                    <th>API Server</th>
                    <th>Port</th>
                    <th>Cluster UUID</th>
                    <th>Option</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(cluster, index) in clustsersInfo" :key="cluster.id || cluster.cluster_id || index">
                    <td>{{ cluster.id }}</td>
                    <td>{{ cluster.name }}</td>
                    <td>{{ cluster.api_server }}</td>
                    <td>{{ cluster.port }}</td>
                    <td class="mono">{{ cluster.cluster_id }}</td>
                    <td>
                        <div class="button-group clusters-view">
                            <button class="primary-small-button" @click.prevent="toClusterDetail(cluster)">Detail</button>
                            <button class="primary-small-button" @click.prevent="showModifyForm(index)">Modify</button>
                            <button class="primary-small-button" @click.prevent="openBindSa(cluster)">Bind SA</button>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>



        <!-- register dialog -->
        <div v-show="dialog_show_flag.register" class="dialog-mask" @click.self="closeForm('register')">
            <form class="new-cluster-register-dialog register-form" @submit.prevent>
                <label for="new-cluster-name">
                    <span>Cluster Name:</span>
                    <input class="default-input" type="text" id="new-cluster-name" v-model.trim="new_cluster_params.name" placeholder="prod/qa/dev" />
                </label>
                <label for="new-cluster-api-server">
                    <span>Cluster API Server:</span>
                    <input class="default-input" type="text" id="new-cluster-api-server" v-model.trim="new_cluster_params.api_server" placeholder="10.0.0.1" />
                </label>
                <label for="new-cluster-port">
                    <span>Cluster Port:</span>
                    <input class="default-input" type="number" min="1" max="65535" id="new-cluster-port" v-model.trim="new_cluster_params.port" placeholder="6443" />
                </label>
                <label for="new-cluster-namespace">
                    <span>Namespace:</span>
                    <input class="default-input" type="text" id="new-cluster-namespace" v-model.trim="new_cluster_params.namespace" placeholder="default" />
                </label>
                <label for="new-cluster-sa-token">
                    <span>SA Token (required):</span>
                    <textarea class="default-input" id="new-cluster-sa-token" v-model.trim="new_cluster_params.sa_token" placeholder="Paste service account token" rows="3"></textarea>
                </label>

                <div class="button-group register-button-group">
                    <button type="button" class="primary-button" :disabled="submitting" @click="resetRegisterForm">Reset</button>
                    <button type="button" class="primary-button" :disabled="submitting" @click="submitRegisterNewClusterForm">{{ submitting ? 'Submitting...' : 'Submit' }}</button>
                    <button type="button" class="primary-button" :disabled="submitting" @click="closeForm('register')">Cancel</button>
                </div>
            </form>
        </div>

    <!-- modify dialog -->
        <div v-show="dialog_show_flag.modify" class="dialog-mask" @click.self="closeForm('modify')">
            <form class="modify-cluster-dialog">
                <label for="cluster-db-id">
                    <span>DB ID:</span>
                    <input v-if="current_cluster_params" class="default-input" type="text" id="cluster-db-id" :value="current_cluster_params.id" readonly />
                    <input v-else class="default-input" type="text" id="cluster-db-id" readonly :value="'None'" />
                </label>
                <label for="cluster-uuid">
                    <span>Cluster UUID:</span>
                    <input v-if="current_cluster_params" class="default-input" type="text" id="cluster-uuid" :value="current_cluster_params.cluster_id" readonly />
                    <input v-else class="default-input" type="text" id="cluster-uuid" readonly :value="'None'" />
                </label>
                <label for="cluster-name">
                    <span>Cluster Name:</span>
                    <input v-if="current_cluster_params" class="default-input" type="text" id="cluster-name" v-model="current_cluster_params.name" />
                    <input v-else class="default-input" type="text" id="cluster-name" readonly :value="'None'" />
                </label>
                <label for="cluster-api-server">
                    <span>Cluster API Server:</span>
                    <input v-if="current_cluster_params" class="default-input" type="text" id="cluster-api-server" v-model="current_cluster_params.api_server" />
                    <input v-else class="default-input" type="text" id="cluster-api-server" readonly :value="'None'" />
                </label>
                <label for="cluster-port">
                    <span>Cluster Port:</span>
                    <input v-if="current_cluster_params" class="default-input" type="text" id="cluster-port" v-model="current_cluster_params.port" />
                    <input v-else class="default-input" type="text" id="cluster-port" readonly :value="'None'" />
                </label>

                <div class="button-group">
                    <button type="button" class="primary-button" @click="modifyClusterHandler">Modify</button>
                    <button type="button" class="primary-button" @click="closeForm('modify')">Cancel</button>
                </div>
            </form>
        </div>

        <!-- bind sa dialog -->
        <div v-show="dialog_show_flag.bindsa" class="dialog-mask" @click.self="closeForm('bindsa')">
            <form class="new-cluster-register-dialog register-form" @submit.prevent>
                <label>
                    <span>Cluster:</span>
                    <input class="default-input" type="text" :value="bind_sa_target?.name || ''" readonly />
                </label>
                <label>
                    <span>Namespace:</span>
                    <input class="default-input" type="text" v-model.trim="bind_sa_namespace" placeholder="default" />
                </label>
                <label>
                    <span>SA Token:</span>
                    <textarea class="default-input" v-model.trim="bind_sa_token" placeholder="Paste service account token" rows="3"></textarea>
                </label>
                <div style="width:100%; color:#666; font-size: 12px; margin-top: 4px;">
                    <span>Decoded exp:</span>
                    <span class="mono">{{ decodedExpText }}</span>
                    <span> · </span>
                    <span :style="{ color: isTokenExpired ? '#c00' : '#0a0' }">{{ isTokenExpired ? 'Expired' : 'Valid' }}</span>
                </div>
                <div class="button-group register-button-group">
                    <button type="button" class="primary-button" :disabled="binding" @click="submitBindSa">{{ binding ? 'Binding...' : 'Bind' }}</button>
                    <button type="button" class="primary-button" :disabled="binding" @click="closeForm('bindsa')">Cancel</button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import type { Cluster, NewClusterParams } from '@/interfaces';
import { getResourcesInfo, registerNewCluster, textCheck, bindClusterSaToken } from '@/utils';
import { useClusterStore } from '@/stores/cluster';

const router = useRouter();
const clusterStore = useClusterStore();

const loading = ref<boolean>(false);
const submitting = ref<boolean>(false);

const clustsersInfo = ref<Cluster[]>([]);
const dialog_show_flag = ref<{ register: boolean; modify: boolean; bindsa: boolean }>({ register: false, modify: false, bindsa: false });
const new_cluster_params = ref<NewClusterParams>({ api_server: '', name: '', port: '', namespace: 'default', sa_token: '' });
const current_cluster_params = ref<Cluster | null>(null);
const bind_sa_target = ref<Cluster | null>(null);
const bind_sa_token = ref<string>('');
const bind_sa_namespace = ref<string>('default');
const binding = ref<boolean>(false);

// decode JWT exp for quick sanity check (no signature verify)
const decodedExpText = computed(() => {
    const t = bind_sa_token.value || '';
    const parts = t.split('.');
    if (parts.length !== 3) return '-';
    try {
        const b64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
        const json = atob(b64 + '='.repeat((4 - (b64.length % 4)) % 4));
        const payload = JSON.parse(json);
        if (!payload.exp) return '-';
        const d = new Date(payload.exp * 1000);
        return d.toISOString();
    } catch {
        return '-';
    }
});
const isTokenExpired = computed(() => {
    const t = bind_sa_token.value || '';
    const parts = t.split('.');
    if (parts.length !== 3) return false;
    try {
        const b64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
        const json = atob(b64 + '='.repeat((4 - (b64.length % 4)) % 4));
        const payload = JSON.parse(json);
        if (!payload.exp) return false;
        const now = Math.floor(Date.now() / 1000);
        return payload.exp <= now;
    } catch {
        return false;
    }
});

const resetRegisterForm = () => {
    if (new_cluster_params.value) {
        new_cluster_params.value.api_server = '';
        new_cluster_params.value.name = '';
        new_cluster_params.value.port = '';
    }
};

const showForm = (val: 'register' | 'modify' | 'bindsa') => {
    dialog_show_flag.value[val] = true;
};

const closeForm = (val: 'register' | 'modify' | 'bindsa') => {
    dialog_show_flag.value[val] = false;
};

const showModifyForm = (index: number) => {
    current_cluster_params.value = clustsersInfo.value[index];
    showForm('modify');
};

const openBindSa = (cluster: Cluster) => {
    bind_sa_target.value = cluster;
    bind_sa_token.value = '';
    bind_sa_namespace.value = 'default';
    dialog_show_flag.value.bindsa = true;
};

const submitBindSa = async () => {
    if (!bind_sa_target.value) return;
    if (!textCheck(bind_sa_token.value, true)) return alert('SA Token is required');
    try {
        binding.value = true;
        const { ok, status, result } = await bindClusterSaToken(bind_sa_target.value.id, bind_sa_token.value, bind_sa_namespace.value);
        if (!ok) {
            if (status === 401) {
                return alert('Unauthorized: please login again.');
            }
            // backend SA validation errors
            const msg = result?.detail || result?.error || (typeof result === 'string' ? result : 'Bind failed');
            return alert(msg);
        }
        dialog_show_flag.value.bindsa = false;
        alert('Bind success');
    } catch (e) {
        console.error(e);
        alert('Bind failed');
    } finally {
        binding.value = false;
    }
};

const submitRegisterNewClusterForm = async () => {
    const _p = new_cluster_params.value;
    if (!textCheck(_p.name, true)) return alert('Cluster Name Error');
    if (!textCheck(_p.api_server, true)) return alert('Cluster API Server Error');
    if (!textCheck(_p.port, true)) return alert('Cluster Port Error');
    if (!textCheck(_p.sa_token || '', true)) return alert('SA Token is required');

    try {
        submitting.value = true;
    const resp = await registerNewCluster(_p);
        if (resp?.new_cluster) {
            clustsersInfo.value.push(resp.new_cluster);
            closeForm('register');
            resetRegisterForm();
        } else if (resp?.id || resp?.cluster_id) {
            clustsersInfo.value.push(resp as Cluster);
            closeForm('register');
            resetRegisterForm();
        } else {
            alert(resp?.error || 'Cluster Register Failed');
        }
    } catch (e) {
        console.error(e);
        alert('Cluster Register Failed');
    } finally {
        submitting.value = false;
    }
};

// TODO: implement modify submit when backend endpoint is ready
const modifyClusterHandler = async () => {
    // placeholder for future implementation
    closeForm('modify');
};

const toClusterDetail = (cluster: Cluster) => {
    clusterStore.setCurrentCluster(cluster);
    router.push({ name: 'cluster-detail', params: { id: cluster.id } });
};



onMounted(async () => {
    clusterStore.removeCurrentCluster();
    loading.value = true;
    try {
        const data = await getResourcesInfo('clusters');
        clustsersInfo.value = data?.clusters || [];
    } catch (e) {
        console.error(e);
    } finally {
        loading.value = false;
    }
});
</script>

<style scoped>
.clusters-page { display: flex; flex-direction: column; gap: 1rem; }
.header { display: flex; align-items: center; gap: 1rem; }
.spacer { flex: 1; }
.loading, .empty { color: var(--color-text-muted); padding: 0.5rem 0; }

.dialog-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: center; padding: 2rem; z-index: 1000; backdrop-filter: blur(4px); }

.new-cluster-register-dialog {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    box-shadow: var(--glass-shadow);
    border-radius: 1rem;
    padding: 1rem 2rem;
    width: min(860px, 95vw);
    animation: 0.2s ease-out forwards slideFadeIn;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.register-form { margin: 1rem; display: flex; flex-direction: column; align-items: center; width: 80%; }
.register-form label { display: flex; flex-direction: row; align-items: center; width: 100%; margin: 0.5rem 0; }
.register-form label span { min-width: 180px; padding-right: 1rem; display: flex; flex-direction: column; justify-content: center; }
.register-form label input,
.register-form label textarea { flex: 1; }

.button-group { margin-top: 2rem; display: flex; flex-direction: row; justify-content: center; gap: 0.5rem; }
.register-button-group { margin-left: 0; padding-left: 0; justify-content: left; }
.register-button-group .primary-button { margin-left: 0; }

.modify-cluster-dialog {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    box-shadow: var(--glass-shadow);
    border-radius: 1rem;
    padding: 1rem 2rem;
    width: min(860px, 95vw);
    animation: 0.2s ease-out forwards slideFadeIn;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.modify-cluster-dialog label { display: flex; flex-direction: row; justify-content: space-between; width: 100%; margin: 0.5rem 0; }
.modify-cluster-dialog label span { padding-right: 1rem; display: flex; flex-direction: column; justify-content: center; margin: 1rem 0; }

@keyframes slideFadeIn {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}

.clusters-info-table { width: 100%; margin-top: 1.5rem; border-collapse: collapse; }
.clusters-info-table td, .clusters-info-table th { border: 1px solid var(--glass-border); padding: 0.75rem 1rem; text-align: left; color: var(--color-text-primary); }
.clusters-info-table th { padding: 0.75rem 1rem; background: var(--color-surface-hover); }


.dashboard-wrapper { display: flex; flex-direction: column; }

.clusters-view.router-link { padding: 1rem; }
.clusters-view.router-link:hover { background-color: var(--color-surface-hover); padding: 1rem; }

.clusters-view.button-group { margin: 0; justify-content: space-evenly; height: auto; }

tbody tr:nth-child(odd) { background: var(--color-surface); }
tbody tr:hover { background: var(--color-surface-hover); }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 0.9em; }
</style>
