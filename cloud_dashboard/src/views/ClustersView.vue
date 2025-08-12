<template>
    <div>
        <h2>📦 Clusters management</h2>
        <p>Manage Kubernetes and OpenStack clusters</p>

        <table class="clusters-info-table">
            <thead>
                <tr>
                    <th>Cluster Name</th>
                    <th>Cluster ID</th>
                    <th>Option</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(cluster, index) in clustsersInfo" :key="index">
                    <td>{{ cluster.name }}</td>
                    <td>{{ cluster.cluster_id }}</td>
                    <td>
                        <div class="button-group clusters-view">
                            <button class="primary-small-button" @click.prevent="toClusterDetail(cluster)">Detail</button>
                            <button class="primary-small-button" @click.prevent="showModifyForm(index)">Modify</button>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
        <div class="button-group register-button-group">
            <button class="primary-button" @click="showForm('register')">Register New Cluster</button>
        </div>

        <!-- register dialog -->
        <div v-show="dialog_show_flag.register" class="new-cluster-register-dialog">
            <form class="register-form">
                <label for="new-cluster-name">
                    <span>Cluster Name:</span>
                    <input class="default-input" type="text" id="new-cluster-name" v-model="new_cluster_params.name" />
                </label>
                <label for="new-cluster-api-server">
                    <span>Cluster API Server:</span
                    ><input
                        class="default-input"
                        type="text"
                        id="new-cluster-api-server"
                        v-model="new_cluster_params.api_server" /></label
                ><label for="new-clsuter-port">
                    <span>Cluster Port:</span
                    ><input class="default-input" type="text" id="new-cluster-port" v-model="new_cluster_params.port" /></label
                ><label for="new-cluster-token">
                    <span>Cluster Token:</span
                    ><input class="default-input" type="text" id="new-cluster-token" v-model="new_cluster_params.token"
                /></label>
                <div class="button-group">
                    <button type="button" class="primary-button" @click="resetRegisterForm">Reset</button>
                    <button type="button" class="primary-button" @click="submitRegisterNewClusterForm">Submit</button>
                    <button type="button" class="primary-button" @click="closeForm('register')">Cancel</button>
                </div>
            </form>
        </div>

        <!-- modify dialog -->
        <div v-show="dialog_show_flag.modify" class="modify-cluster-dialog">
            <form>
                <label for="cluster-id">
                    <span>Cluster ID:</span>
                    <input
                        v-if="current_cluster_params"
                        class="default-input"
                        type="text"
                        id="cluster-id"
                        v-model="current_cluster_params.cluster_id"
                        readonly
                    />
                    <input v-else class="default-input" type="text" id="cluster-id" readonly :value="'None'" />
                </label>
                <label for="cluster-name">
                    <span>Cluster Name:</span>
                    <input
                        v-if="current_cluster_params"
                        class="default-input"
                        type="text"
                        id="cluster-name"
                        v-model="current_cluster_params.name"
                    />
                    <input v-else class="default-input" type="text" id="cluster-name" readonly :value="'None'" />
                </label>
                <label for="cluster-api-server">
                    <span>Cluster API Server:</span
                    ><input
                        v-if="current_cluster_params"
                        class="default-input"
                        type="text"
                        id="cluster-api-server"
                        v-model="current_cluster_params.api_server" />
                    <input v-else class="default-input" type="text" id="cluster-api-server" readonly :value="'None'"
                /></label>
                <label for="clsuter-port">
                    <span>Cluster Port:</span
                    ><input
                        v-if="current_cluster_params"
                        class="default-input"
                        type="text"
                        id="cluster-port"
                        v-model="current_cluster_params.port" />
                    <input v-else class="default-input" type="text" id="cluster-port" readonly :value="'None'" /></label
                ><label for="cluster-token">
                    <span>Cluster Token:</span
                    ><input
                        v-if="current_cluster_params"
                        class="default-input"
                        type="text"
                        id="cluster-token"
                        v-model="current_cluster_params.token" />
                    <input v-else class="default-input" type="text" id="cluster-token" readonly :value="'None'"
                /></label>
                <div class="button-group">
                    <button type="button" class="primary-button" @click="modifyClusterHandler">Modify</button>
                    <button type="button" class="primary-button" @click="closeForm('modify')">Cancel</button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { Cluster, NewClusterParams } from '@/interfaces';
import { getResourcesInfo, textCheck } from '@/utils';
import { onMounted, reactive, ref } from 'vue';
import { registerNewCluster } from '@/utils';
import { useRouter } from 'vue-router';
import { useClusterStore } from '@/stores/cluster';

const clustsersInfo = ref<Cluster[]>([]);
const current_cluster_params = ref<Cluster | null>(null);
const router = useRouter();
const clusterStore = useClusterStore();

const new_cluster_params = ref<NewClusterParams>({
    api_server: '',
    name: '',
    port: '',
    token: '',
});

const dialog_show_flag = reactive({
    register: false,
    modify: false,
});

const resetRegisterForm = () => {
    if (new_cluster_params.value) {
        for (const key in new_cluster_params.value) {
            new_cluster_params.value[key as keyof NewClusterParams] = '';
        }
    }
};

const showForm = (val: string) => {
    if (val === 'register') {
        dialog_show_flag.register = true;
        return;
    }
    if (val === 'modify') {
        dialog_show_flag.modify = true;
    }
};

const closeForm = (val: string) => {
    if (val === 'register') {
        dialog_show_flag.register = false;
        return;
    }
    if (val === 'modify') {
        dialog_show_flag.modify = false;
    }
};

const showModifyForm = (index: number) => {
    current_cluster_params.value = clustsersInfo.value[index];
    showForm('modify');
};

const submitRegisterNewClusterForm = async () => {
    // check form
    const _p = new_cluster_params.value;
    if (!textCheck(_p.name, true)) {
        alert('Cluster Name Error');
        return;
    }
    if (!textCheck(_p.api_server, true)) {
        alert('Cluser API Server Error');
        return;
    }
    if (!textCheck(_p.port, true)) {
        alert('Cluster Port Error');
        return;
    }
    if (!textCheck(_p.token, true)) {
        alert('Cluster Token Error');
        return;
    }

    if (new_cluster_params.value) {
        const data = await registerNewCluster(new_cluster_params.value);
        // data is Cluster Interface type
        if (data) clustsersInfo.value.push(data);
        else alert('Cluster Register Failed');
        showForm('register');
    } else {
        console.warn('new cluster params not ready');
    }
};

// modify cluster info: name, port, api-server, token
const modifyClusterHandler = async () => {
    /* submit form by POST with
        body: JSON.stringfy({
            name: new_name,
            port: new_port,
            api_server: new_api_server,
            token: new_token
        })
    */
};

const toClusterDetail = (cluster: Cluster) => {
    clusterStore.setCurrentCluster(cluster);
    router.push({
        name: 'cluster-detail',
        params: {
            id: cluster.id,
        },
    });
};

onMounted(async () => {
    // load base information
    clusterStore.removeCurrentCluster();

    const data = await getResourcesInfo('clusters');
    // data = {"clusters": value => (name, id)}
    clustsersInfo.value = data.clusters;
});
</script>

<style scoped>
.new-cluster-register-dialog {
    position: fixed;
    background-color: whitesmoke;
    box-shadow: 3px 3px 1rem 0.5rem #aaa;
    border-radius: 1rem;
    padding: 1rem 4rem;
    top: 4rem;
    right: 1rem;
    width: 1000px;
    animation: 0.3s ease-out forwards slideFadeIn;

    display: flex;
    flex-direction: row;
    justify-content: center;
}

.register-form {
    margin: 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 80%;
}

.register-form label {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
}

.register-form label span {
    padding-right: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.button-group {
    margin-top: 2rem;
    display: flex;
    flex-direction: row;
    justify-content: center;
}

.modify-cluster-dialog {
    position: fixed;
    background-color: whitesmoke;
    box-shadow: 3px 3px 1rem 0.5rem #aaa;
    border-radius: 1rem;
    padding: 1rem 4rem;
    top: 27rem;
    right: 1rem;
    width: 1000px;
    animation: 0.3s ease-out forwards slideFadeIn;

    display: flex;
    flex-direction: row;
    justify-content: center;
}

.modify-cluster-dialog form {
    margin: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    width: 80%;
}

.modify-cluster-dialog form label {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
}

.modify-cluster-dialog form label span {
    padding-right: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin: 1rem 0;
}

@keyframes slideFadeIn {
    from {
        opacity: 0;
        transform: translateX(30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.clusters-info-table {
    width: 85%;
    margin-top: 2rem;
    margin-right: 10rem;
}

.clusters-info-table td,
.clusters-info-table th {
    border: 2px solid #555;
    padding: 1.5rem;
    text-align: center;
}

.clusters-info-table th {
    padding: 1rem 2rem;
}

.dashboard-wrapper {
    display: flex;
    flex-direction: column;
}

.register-button-group {
    margin-left: 0;
    padding-left: 0;
    justify-content: left;
}

.register-button-group .primary-button {
    margin-left: 0;
}

.clusters-view.router-link {
    padding: 1rem;
}
.clusters-view.router-link:hover {
    background-color: #999;
    padding: 1rem;
}

.clusters-view.button-group {
    margin: 0;
    justify-content: space-evenly;
    height: auto;
}
</style>
