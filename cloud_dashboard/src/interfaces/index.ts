export interface Container {
    id: string;
    name: string;
    container_id: string;
}

export interface Pod {
    id: string;
    name: string;
    containers: Container[];
    pod_id: string;
}

export interface Node {
    id: string;
    name: string;
    pods: Pod[];
    node_id: string;
}

export interface Namespace {
    id: string;
    name: string;
    nanmespace_id: string;
}

// ClusterView
export interface Cluster {
    id: string;
    name: string;
    api_server: string;
    port: number;
    nodes: Node[];
    namespace: Namespace[];
    cluster_id: string;
    token: string;
}

export interface NewClusterParams {
    api_server: string;
    name: string;
    port: string;
    token: string;
}

// CommandView

export interface CommandResult {
    cmd: string;
    status_code: number;
    cmd_status: string;
    output: string;
    error: string;
}

// Metrics
export interface ClusterMetrics {
    cpu_utilization: string;
    memory_utilization: string;
    total_cpu: string;
    total_memory: string;
    used_cpu: string;
    used_memory: string;
}
