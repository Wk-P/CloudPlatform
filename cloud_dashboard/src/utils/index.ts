import type { CommandResult, NewClusterParams } from '@/interfaces';

const runtime_api = {
    url: '/api/runtime',
    resources: {
        clusters: '/clusters/baseinfo/',
        nodes: '/nodes/',
        pods: '/pods/',
        services: '/services/',
        events: '/events/',
        deployments: '/deployments/',
        daemonsets: '/daemonsets/',
        statefulsets: '/statefulsets/',
    replicasets: '/replicasets/',
    jobs: '/jobs/',
    ingresses: '/ingresses/',
    hpas: '/hpas/',
    cronjobs: '/cronjobs/',
        namespaces: '/namespaces/',
    },
    options: {
        cluster: {
            add: '/clusters/add/',
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

const authHeaders = (): HeadersInit => {
    const token = localStorage.getItem('cloud-dashboard-token') || sessionStorage.getItem('cloud-dashboard-token');
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return headers;
};

// Clear only platform JWT (do not touch any SA token copied in forms)
const clearPlatformToken = () => {
    try { localStorage.removeItem('cloud-dashboard-token'); } catch {}
    try { sessionStorage.removeItem('cloud-dashboard-token'); } catch {}
};

// Redirect to login with original path preserved
const redirectToLogin = () => {
    const redirect = encodeURIComponent(window.location.pathname + window.location.search);
    window.location.href = `/login?redirect=${redirect}`;
};

// Wrapper to auto-attach Authorization and handle 401 globally
export const fetchWithAuth = async (url: string, init: RequestInit = {}) => {
    const base = authHeaders();
    let hdrs: HeadersInit = base;
    if (init.headers) {
        // normalize to object and merge
        if (init.headers instanceof Headers) {
            const obj: Record<string, string> = {};
            init.headers.forEach((v, k) => { obj[k] = v; });
            hdrs = { ...obj, ...base } as HeadersInit;
        } else if (Array.isArray(init.headers)) {
            const obj: Record<string, string> = {};
            init.headers.forEach(([k, v]) => { obj[k] = v as string; });
            hdrs = { ...obj, ...base } as HeadersInit;
        } else {
            hdrs = { ...(init.headers as Record<string, string>), ...base } as HeadersInit;
        }
    }
    const resp = await fetch(url, { ...init, headers: hdrs });
    if (resp.status === 401) {
        clearPlatformToken();
        // best-effort redirect; current call can still read resp if needed
        redirectToLogin();
    }
    return resp;
};

const getRuntimeApiFullUrl = (resource_name: keyof typeof runtime_api.resources, cluster_id?: string) => {
    if (resource_name === 'clusters') {
        return `${runtime_api.url}${runtime_api.resources.clusters}`;
    }
    return `${runtime_api.url}/clusters/${cluster_id}${runtime_api.resources[resource_name]}`;
};

export const registerNewCluster = async (new_cluster_params: NewClusterParams) => {
    try {
        const url = `${runtime_api.url}${runtime_api.options.cluster.add}`;
        const response = await fetchWithAuth(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                api_server: new_cluster_params.api_server,
                port: new_cluster_params.port,
                name: new_cluster_params.name,
                namespace: new_cluster_params.namespace || 'default',
                sa_token: new_cluster_params.sa_token,
            }),
        });
        const result = await response.json();
        return result;
    } catch (error) {
        console.error(error);
        return null;
    }
};

const buildQuery = (params?: Record<string, string | number | boolean | undefined | null>) => {
    if (!params) return '';
    const sp = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
        if (v === undefined || v === null || v === '') return;
        sp.append(k, String(v));
    });
    const qs = sp.toString();
    return qs ? `?${qs}` : '';
};

export const getResourcesInfo = async (
    resource_name: keyof typeof runtime_api.resources,
    cluster_id?: string,
    params?: Record<string, string | number | boolean | undefined | null>
) => {
    try {
        const base = getRuntimeApiFullUrl(resource_name, cluster_id);
        const url = `${base}${buildQuery(params)}`;
    const response = await fetchWithAuth(url);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const getNamespaces = async (cluster_id: string) => {
    try {
        const url = `${runtime_api.url}/clusters/${cluster_id}${runtime_api.resources.namespaces}`;
    const response = await fetchWithAuth(url);
        return await response.json();
    } catch (e) {
        console.error(e);
        return null;
    }
};

export const updateUserSaToken = async (sa_token: string) => {
    try {
        const response = await fetchWithAuth('/api/auth/sa-token/update/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sa_token }),
        });
        const result = await response.json();
        return { ok: response.ok, result };
    } catch (e) {
        console.error(e);
        return { ok: false, result: null };
    }
};

export const bindClusterSaToken = async (cluster_id: string | number, token: string, namespace?: string) => {
    try {
        const response = await fetch('/api/auth/k8s/account/bind/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...authHeaders() },
            body: JSON.stringify({ cluster_id, token, namespace: namespace || 'default' }),
        });
        const result = await response.json();
    return { ok: response.ok, status: response.status, result };
    } catch (e) {
        console.error(e);
    return { ok: false, status: 0, result: null };
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

export type CommandPayload = {
    action: 'get' | 'describe' | 'logs' | 'apply' | 'delete' | 'scale';
    resource?: 'pods' | 'services' | 'deployments';
    cluster_id: string;
    namespace?: string;
    name?: string;
    tail_lines?: number;
    // advanced
    manifest?: string | Record<string, unknown> | Array<Record<string, unknown>>;
    kind?: string; // delete can pass kind directly (overrides resource mapping)
    replicas?: number; // for scale
};

export const postCommand = async (payload: CommandPayload) => {
    const buildCmd = () => {
        const ns = payload.namespace ? ` -n ${payload.namespace}` : '';
        const res = payload.resource ? ` ${payload.resource}` : '';
        if (payload.action === 'apply') return `apply`;
        if (payload.action === 'delete') {
            const k = payload.kind || payload.resource || '';
            const nm = payload.name ? ` ${payload.name}` : '';
            return `delete ${k}${nm}${ns}`.trim();
        }
        if (payload.action === 'scale') {
            const nm = payload.name ? ` ${payload.name}` : '';
            const r = payload.replicas != null ? ` --replicas=${payload.replicas}` : '';
            return `scale deployments${nm}${ns}${r}`.trim();
        }
        const nm = payload.name ? ` ${payload.name}` : '';
        const tl = payload.tail_lines ? ` --tail=${payload.tail_lines}` : '';
        return `${payload.action}${res}${ns}${nm}${tl}`.trim();
    };
    try {
        const url = `${state_api.url}${state_api.cmd.run}`;
        const response = await fetchWithAuth(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await response.json();

        if (!response.ok) {
            const cmd_error: CommandResult = {
                cmd: buildCmd(),
                cmd_status: 'error',
                status_code: response.status,
                output: '',
                error: result?.error || response.statusText || 'Request failed',
            };
            return cmd_error;
        }

        const cmd_result: CommandResult = {
            cmd: buildCmd(),
            cmd_status: result.status,
            status_code: result.returncode,
            output: result.stdout,
            error: result.stderr,
        };
        return cmd_result;
    } catch (error) {
        console.error(error);
        const fallback: CommandResult = {
            cmd: buildCmd(),
            cmd_status: 'error',
            status_code: -1,
            output: '',
            error: (error instanceof Error ? error.message : 'Network or unknown error'),
        };
        return fallback;
    }
};

export const getClusterUsage = async (id: string) => {
    try {
        const url = `${state_api.url}${state_api.cluster}${id}/`;
        const response = await fetchWithAuth(url);
        const result = await response.json();
        console.log(result);
        return result;
    } catch (error) {
        console.error(error);
        return null;
    }
};

export const getClusters = async () => {
    try {
        const url = getRuntimeApiFullUrl('clusters');
        const response = await fetchWithAuth(url);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const getNodes = async (cluster_id: string) => {
    try {
        const url = `${runtime_api.url}/clusters/${cluster_id}${runtime_api.resources.nodes}`;
        const response = await fetchWithAuth(url);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error(error);
        return [];
    }
};

export const countResources = async (cluster_id: string) => {
    try {
        const [deployments, pods, services] = await Promise.all([
            fetchWithAuth(`${runtime_api.url}/clusters/${cluster_id}${runtime_api.resources.deployments}`).then(r => r.json()),
            fetchWithAuth(`${runtime_api.url}/clusters/${cluster_id}${runtime_api.resources.pods}`).then(r => r.json()),
            fetchWithAuth(`${runtime_api.url}/clusters/${cluster_id}${runtime_api.resources.services}`).then(r => r.json()),
        ]);
        return {
            deployments: Array.isArray(deployments) ? deployments.length : 0,
            pods: Array.isArray(pods) ? pods.length : 0,
            services: Array.isArray(services) ? services.length : 0,
        };
    } catch (error) {
        console.error(error);
        return { deployments: 0, pods: 0, services: 0 };
    }
};

export const getAllNodesList = async (id: string) => {
    try {
    const url = `${runtime_api.url}/clusters/${id}${runtime_api.resources.nodes}`;
    const response = await fetchWithAuth(url);
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
    const response = await fetchWithAuth(url);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error(error);
        return null;
    }
}