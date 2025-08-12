import type { CommandResult, NewClusterParams } from '@/interfaces';

const runtime_api = {
    url: '/api/runtime',
    resources: {
        clusters: '/clusters/baseinfo/',
        cluster: '/cluster/',
        nodes: '/nodes/',
        pods: '/pods/',
        deployment: '/deployments/',
        daemonsets: '/daemonsets/',
        statefulsets: '/statefulstes/',
    },
    options: {
        cluster: {
            add: '/cluster/add/',
        },
    },
};

const state_api = {
    url: '/api/state',
    cmd: {
        run: '/run/cmd/',
    },
    cluster: '/resources/cluster/',
    node: {
        single: '/resources/node/',
        namespace: '/resources/nodes/',
        all: '/resources/nodes/'
    }
};

const getRuntimeApiFullUrl = (resource_name: keyof typeof runtime_api.resources, cluster_id?: string) => {
    if (resource_name === 'clusters') {
        return `${runtime_api.url}${runtime_api.resources.clusters}`;
    } else {
        return `${runtime_api.url}/${cluster_id}${runtime_api.resources[resource_name]}`;
    }
};

export const registerNewCluster = async (new_cluster_params: NewClusterParams) => {
    try {
        const url = `${runtime_api.url}${runtime_api.options.cluster.add}`;
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                api_server: new_cluster_params.api_server,
                port: new_cluster_params.port,
                token: new_cluster_params.token,
                name: new_cluster_params.name,
            }),
        });
        const result = await response.json();
        return result;
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const getResourcesInfo = async (resource_name: keyof typeof runtime_api.resources, cluster_id?: string) => {
    try {
        const url = getRuntimeApiFullUrl(resource_name, cluster_id);
        const response = await fetch(url);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const textCheck = (val: string, strict: boolean) => {
    // not strict mode
    if (!strict) {
        if (val == null) {
            return false;
        } else {
            return false;
        }
    } else {
        if (val == null || val === '') {
            return false;
        } else {
            return true;
        }
    }
};

export const windowRefresh = () => {
    window.location.reload();
};

export const postCommand = async (cmd: string) => {
    try {
        const url = `${state_api.url}${state_api.cmd.run}`;
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cmd: cmd,
            }),
        });
        const result = await response.json();

        const cmd_result: CommandResult = {
            cmd: cmd,
            cmd_status: result.status,
            status_code: result.returncode,
            output: result.stdout,
            error: result.stderr,
        };
        return cmd_result;
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const getClusterUsage = async (id: string) => {
    try {
        const url = `${state_api.url}${state_api.cluster}${id}/`;
        const response = await fetch(url);
        const result = await response.json();
        console.log(result);
        return result;
    } catch (error) {
        console.error(error);
        return null;
    }
};


export const getAllNodesList  = async (id: string) => {
    try {
        const url = `${runtime_api.url}${runtime_api.resources.cluster}${id}${runtime_api.resources.nodes}`;
        const response = await fetch(url);
        const result = await response.json();
        console.log(result);
        return result;
    } catch (error) {
        console.error(error);
        return null;
    }
}

export const getNodeUsage = async (cluster_id: string, name: string) => {
    try {
        const url = `${state_api.url}${state_api.node.single}${cluster_id}/${name}/`;
        const response = await fetch(url);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error(error);
        return null;
    }
}
