<template>
    <div class="commands-page">
        <div class="hero">
            <div>
                <h2>Command Console</h2>
                <p class="muted">Run kubectl-style actions, inspect objects, and apply manifests.</p>
            </div>
            <span class="pill">K8s Toolkit</span>
        </div>

        <div class="card">
            <div class="controls">
                <select v-model="action" class="default-input command-input">
                    <option value="get">get</option>
                    <option value="describe">describe</option>
                    <option value="logs">logs</option>
                    <option value="apply">apply</option>
                    <option value="delete">delete</option>
                    <option value="scale">scale</option>
                </select>

                <select v-if="action !== 'apply' && action !== 'scale'" v-model="resource" class="default-input command-input">
                    <option value="pods">pods</option>
                    <option value="services">services</option>
                    <option value="deployments">deployments</option>
                </select>

                <input v-model="clusterId" class="default-input command-input" placeholder="cluster id" />
                <input v-model="namespace" class="default-input command-input" placeholder="namespace (optional)" />

                <input
                    v-if="action !== 'apply' && action !== 'scale'"
                    v-model="name"
                    class="default-input command-input"
                    placeholder="resource name (optional)"
                />

                <input
                    v-if="action === 'logs'"
                    v-model.number="tailLines"
                    type="number"
                    min="0"
                    placeholder="tail lines"
                    class="default-input command-input"
                />

                <input
                    v-if="action === 'delete'"
                    v-model="kind"
                    class="default-input command-input"
                    placeholder="kind override (optional)"
                />

                <template v-if="action === 'scale'">
                    <input
                        v-model="name"
                        class="default-input command-input"
                        placeholder="deployment name"
                    />
                    <input
                        v-model.number="replicas"
                        type="number"
                        min="0"
                        placeholder="replicas"
                        class="default-input command-input"
                    />
                </template>
            </div>

            <div v-if="action === 'apply'">
                <div class="apply-toolbar">
                    <span class="hint">Paste YAML/JSON. We auto-parse JSON if possible.</span>
                    <div class="spacer"></div>
                    <button class="secondary-small-button" type="button" @click="fillNginx">Sample Nginx</button>
                    <button class="secondary-small-button" type="button" @click="tryExtractFromJson">Use JSON Fields</button>
                </div>
                <textarea
                    v-model="manifest"
                    class="manifest-input"
                    rows="10"
                    placeholder="apiVersion: apps/v1\nkind: Deployment\n..."
                ></textarea>
            </div>

            <button class="primary-small-button run-button" @click="executeCommand">RUN</button>
        </div>

        <div class="command-output">
            <h4 style="margin-bottom: 1rem">Result Output</h4>
            <div v-if="result">
                <!-- Basic meta -->
                <table class="result-table meta">
                    <tbody>
                        <tr>
                            <th class="item-head">command</th>
                            <td class="item-body cmd">{{ result.cmd }}</td>
                        </tr>
                        <tr>
                            <th class="item-head">status</th>
                            <td class="item-body">{{ result.cmd_status }} (code: {{ result.status_code }})</td>
                        </tr>
                    </tbody>
                </table>

                <!-- Parsed/structured output -->
                <div v-if="lastAction === 'get' && parsed?.kind === 'array'">
                    <div v-if="lastResource === 'pods'">
                        <h4>Pods</h4>
                        <div v-for="(items, ns) in groupedByNs" :key="ns" class="section">
                            <div class="section-title">Namespace: {{ ns }}</div>
                            <table class="result-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Status</th>
                                        <th>Node</th>
                                        <th>IP</th>
                                        <th>Restarts</th>
                                        <th>Created</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="it in items" :key="(it as any).name">
                                        <td class="mono">{{ (it as any).name }}</td>
                                        <td>{{ (it as any).status }}</td>
                                        <td>{{ (it as any).node }}</td>
                                        <td>{{ (it as any).ip }}</td>
                                        <td>{{ (it as any).restarts }}</td>
                                        <td>{{ (it as any).created_at }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div v-else-if="lastResource === 'services'">
                        <h4>Services</h4>
                        <div v-for="(items, ns) in groupedByNs" :key="ns" class="section">
                            <div class="section-title">Namespace: {{ ns }}</div>
                            <table class="result-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Type</th>
                                        <th>Cluster IP</th>
                                        <th>Ports</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="it in items" :key="(it as any).name">
                                        <td class="mono">{{ (it as any).name }}</td>
                                        <td>{{ (it as any).type }}</td>
                                        <td>{{ (it as any).cluster_ip }}</td>
                                        <td>
                                            {{
                                                Array.isArray((it as any).ports)
                                                    ? (it as any).ports.join(', ')
                                                    : (it as any).ports
                                            }}
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div v-else-if="lastResource === 'deployments'">
                        <h4>Deployments</h4>
                        <div v-for="(items, ns) in groupedByNs" :key="ns" class="section">
                            <div class="section-title">Namespace: {{ ns }}</div>
                            <table class="result-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Replicas</th>
                                        <th>Ready</th>
                                        <th>Updated</th>
                                        <th>Available</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="it in items" :key="(it as any).name">
                                        <td class="mono">{{ (it as any).name }}</td>
                                        <td>{{ (it as any).replicas }}</td>
                                        <td>{{ (it as any).ready }}</td>
                                        <td>{{ (it as any).updated }}</td>
                                        <td>{{ (it as any).available }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div v-else-if="lastAction === 'describe' && parsed?.kind === 'object'">
                    <h4>Details</h4>
                    <table class="result-table">
                        <tbody>
                            <tr v-for="(v, k) in parsed.data" :key="k">
                                <th class="item-head">{{ k }}</th>
                                <td class="item-body">{{ formatValue(v) }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div v-else>
                    <template v-if="result.status_code !== 0 && result.error">
                        <h4>Error</h4>
                        <pre class="pre-wrap">{{ result.error }}</pre>
                        <h4 style="margin-top: 0.75rem">Output</h4>
                        <pre class="pre-wrap">{{ result.output }}</pre>
                    </template>
                    <template v-else>
                        <h4>Output</h4>
                        <pre class="pre-wrap">{{ displayText }}</pre>
                    </template>
                </div>

                <details class="raw-toggle">
                    <summary>Show raw payload</summary>
                    <pre class="pre-wrap small">{{ displayText }}</pre>
                </details>
            </div>
            <div v-else class="result-empty">No output yet. Fill the form above and click RUN.</div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { CommandResult, Cluster } from '@/interfaces';
import { postCommand, type CommandPayload } from '@/utils';
import { computed, ref, onMounted } from 'vue';
import { useClusterStore } from '@/stores/cluster';

const action = ref<'get' | 'describe' | 'logs' | 'apply' | 'delete' | 'scale'>('get');
const resource = ref<'pods' | 'services' | 'deployments'>('pods');
const clusterId = ref('');
const namespace = ref('');
const name = ref('');
const tailLines = ref<number | undefined>(undefined);
const manifest = ref('');
const kind = ref('');
const replicas = ref<number | undefined>(undefined);
const result = ref<CommandResult | null>(null);
const lastAction = ref<typeof action.value>('get');
const lastResource = ref<typeof resource.value>('pods');

const executeCommand = async () => {
    if (!clusterId.value) {
        alert('Please input cluster id');
        return;
    }
    lastAction.value = action.value;
    lastResource.value = resource.value;
    let payload: CommandPayload;
    if (action.value === 'apply') {
        type Manifest = string | Record<string, unknown> | Array<Record<string, unknown>>;
        let derived: Manifest | undefined = manifest.value || undefined;
        // auto-detect JSON and extract
        if (manifest.value && (manifest.value.trim().startsWith('{') || manifest.value.trim().startsWith('['))) {
            try {
                const js: unknown = JSON.parse(manifest.value);
                const isRecord = (v: unknown): v is Record<string, unknown> =>
                    !!v && typeof v === 'object' && !Array.isArray(v);
                const isManifestList = (v: unknown): v is Array<Record<string, unknown>> =>
                    Array.isArray(v) && v.every((x) => !!x && typeof x === 'object' && !Array.isArray(x));
                if (isRecord(js)) {
                    const obj = js;
                    const m = obj.manifest as unknown;
                    if (m !== undefined) {
                        if (typeof m === 'string') {
                            derived = m;
                        } else if (isRecord(m)) {
                            derived = m as Record<string, unknown>;
                        } else if (isManifestList(m)) {
                            derived = m as Array<Record<string, unknown>>;
                        }
                        const cid = obj.cluster_id;
                        if (cid !== undefined) clusterId.value = String(cid as string | number);
                        const ns = obj.namespace;
                        if (ns !== undefined) namespace.value = String(ns as string);
                    } else {
                        // looks like a single manifest object
                        derived = obj as Record<string, unknown>;
                    }
                } else if (isManifestList(js)) {
                    derived = js as Array<Record<string, unknown>>;
                }
            } catch {
                // keep as raw string (YAML)
            }
        }
        payload = {
            action: 'apply',
            cluster_id: clusterId.value,
            namespace: namespace.value || undefined,
            manifest: derived,
        };
    } else if (action.value === 'delete') {
        payload = {
            action: 'delete',
            cluster_id: clusterId.value,
            namespace: namespace.value || undefined,
            resource: resource.value,
            name: name.value || undefined,
            kind: kind.value || undefined,
        };
    } else if (action.value === 'scale') {
        payload = {
            action: 'scale',
            cluster_id: clusterId.value,
            namespace: namespace.value || undefined,
            resource: 'deployments',
            name: name.value || undefined,
            replicas: replicas.value as number | undefined,
        };
    } else {
        payload = {
            action: action.value,
            cluster_id: clusterId.value,
            namespace: namespace.value || undefined,
            resource: resource.value,
            name: name.value || undefined,
            tail_lines: tailLines.value,
        };
    }

    result.value = await postCommand(payload);
};

onMounted(() => {
    try {
        const raw = useClusterStore() as unknown as {
            getCurrentCluster?: () => Cluster | null | undefined;
            currentCluster?: Cluster | null | undefined;
        };
        const c = typeof raw.getCurrentCluster === 'function' ? raw.getCurrentCluster() : raw.currentCluster;
        if (c?.id && !clusterId.value) clusterId.value = String(c.id);
    } catch {
        // ignore
    }
});

type Dict = Record<string, unknown>;
type Parsed = { kind: 'array'; data: Dict[] } | { kind: 'object'; data: Dict } | { kind: 'text'; data: string } | null;

const parsed = computed<Parsed>(() => {
    if (!result.value) return null;
    const raw = result.value.output || result.value.error || '';
    try {
        const js = JSON.parse(raw);
        if (Array.isArray(js)) return { kind: 'array', data: js };
        if (js && typeof js === 'object') return { kind: 'object', data: js };
    } catch {
        // not JSON
    }
    return { kind: 'text', data: raw };
});

const groupedByNs = computed<Record<string, Dict[]>>(() => {
    if (!parsed.value || parsed.value.kind !== 'array') return {};
    const groups: Record<string, Dict[]> = {};
    for (const item of parsed.value.data) {
        const ns = (item.ns as string) || 'default';
        (groups[ns] ||= []).push(item);
    }
    return groups;
});

function formatValue(v: unknown): string {
    if (v == null) return '';
    if (typeof v === 'object') return JSON.stringify(v, null, 2);
    return String(v);
}

const displayText = computed(() => {
    if (!result.value) return '';
    if (result.value.status_code !== 0 && result.value.error) return result.value.error;
    return result.value.output || result.value.error || '';
});

function fillNginx() {
    manifest.value = `apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: nginx-deploy\n  namespace: default\nspec:\n  replicas: 1\n  selector:\n    matchLabels:\n      app: nginx\n  template:\n    metadata:\n      labels:\n        app: nginx\n    spec:\n      containers:\n      - name: nginx\n        image: nginx:1.25\n        ports:\n        - containerPort: 80\n`;
}

function tryExtractFromJson() {
    if (!manifest.value) return;
    try {
        const js: unknown = JSON.parse(manifest.value);
        const isRecord = (v: unknown): v is Record<string, unknown> => !!v && typeof v === 'object' && !Array.isArray(v);
        if (isRecord(js)) {
            const obj = js;
            if (obj.cluster_id !== undefined) clusterId.value = String(obj.cluster_id as string | number);
            if (obj.namespace !== undefined) namespace.value = String(obj.namespace as string);
            if (obj.manifest !== undefined) {
                const m = obj.manifest as unknown;
                if (typeof m === 'string') {
                    manifest.value = m;
                } else {
                    manifest.value = JSON.stringify(m, null, 2);
                }
            } else {
                // treat parsed object as manifest itself
                manifest.value = JSON.stringify(obj, null, 2);
            }
        }
    } catch {
        // ignore
    }
}
</script>

<style scoped>
.commands-page { width: 100%; overflow-x: hidden; display: flex; flex-direction: column; gap: var(--space-4); }
.hero { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.hero h2 { margin: 0; }
.hero .muted { margin: 0.15rem 0 0; color: var(--color-text-muted); }
.pill {
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    border: 1px solid var(--glass-border);
    background: var(--glass-bg);
    color: var(--color-primary);
    font-weight: 600;
}

.card {
    width: 100%;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.command-output {
    width: 100%;
    padding: 2rem;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    box-sizing: border-box;
    overflow-x: hidden;
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
}

.result-table { width: 100%; border-collapse: collapse; table-layout: fixed; background: transparent; }
.result-table th, .result-table td { border: 1px solid var(--glass-border); padding: 0.5rem 0.75rem; text-align: left; vertical-align: top; word-break: break-word; overflow-wrap: anywhere; color: var(--color-text-primary); }
.result-table th { background: var(--color-surface-hover); }
.item-head { width: 220px; background: var(--color-surface-hover); }
.item-body { width: auto; word-break: break-word; overflow-wrap: anywhere; white-space: pre-wrap; }
.result-empty { color: var(--color-text-muted); }

.command-input { color: var(--color-primary); min-width: 200px; }
.manifest-input {
    width: 100%;
    min-width: 0;
    min-height: 140px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    color: var(--color-text-primary);
    padding: var(--space-3);
}
.apply-toolbar { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem; }
.apply-toolbar .spacer { flex: 1; }
.hint { color: var(--color-text-muted); }

.controls { display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; margin-bottom: 1rem; }

.run-button { align-self: flex-start; }

.cmd {
    font-weight: 600;
    color: var(--color-primary);
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
    overflow-wrap: anywhere;
}

summary {
    cursor: pointer;
}

.section {
    margin-top: 1rem;
}
.section-title {
    font-weight: 600;
    margin: 0.25rem 0 0.5rem;
}
.pre-wrap {
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: anywhere;
    max-width: 100%;
    box-sizing: border-box;
    overflow-x: hidden; /* no horizontal scroll; enforce wrapping */
}
.raw-toggle {
    margin-top: 1rem;
}
.result-table.meta {
    margin-bottom: 1rem;
}
.mono {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
    overflow-wrap: anywhere;
}
</style>
