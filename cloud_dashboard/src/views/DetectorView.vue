<template>
    <div class="page">
        <h2>Anomaly Detector</h2>
        <div class="actions">
            <button class="primary-button" @click="loadBlacklist">Refresh Blacklist</button>
            <button class="primary-button" @click="loadTrend">Refresh Trend</button>
            <button class="primary-button" @click="loadRedisData">Refresh Redis Data</button>
        </div>

        <section class="blacklist">
            <h3>Ingress Blacklist</h3>
            <p class="hint">Auto-refreshes every 30 seconds. Data source TBD.</p>
            <div v-if="blError" class="error">{{ blError }}</div>
            <div v-if="blacklist.length">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Source (IP/CIDR/Pattern)</th>
                            <th>Control</th>
                            <th>Scope</th>
                            <th>Reason</th>
                            <th>Updated At</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(b, idx) in blacklist" :key="idx">
                            <td>{{ idx + 1 }}</td>
                            <td>{{ b.source || b.ip || b.cidr || b.pattern || '-' }}</td>
                            <td>{{ b.action || b.mode || b.control || '-' }}</td>
                            <td>{{ b.scope || b.target || '-' }}</td>
                            <td>{{ b.reason || b.note || '' }}</td>
                            <td>{{ b.updated_at || b.updatedAt || b.updateTime || '' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div v-else class="hint">No blacklist entries.</div>

            <div class="supported" v-if="supportedControls.length">
                <h4>Supported NGINX controls</h4>
                <table>
                    <thead>
                        <tr>
                            <th>Key</th>
                            <th>Type</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in supportedControls" :key="item.key">
                            <td>{{ item.key }}</td>
                            <td>{{ item.type }}</td>
                            <td>{{ item.desc }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>

        <section class="trend">
            <h3>Ingress Traffic Trend</h3>
            <p class="hint">Lightweight SVG chart (placeholder API).</p>
            <div v-if="trendError" class="error">{{ trendError }}</div>
            <div v-if="trendPoints.length" class="chart-wrap">
                <svg :viewBox="`0 0 ${chartW} ${chartH}`" class="chart" role="img">
                    <path :d="pathD" fill="none" stroke="#60a5fa" stroke-width="2" />
                    <circle
                        v-for="(p, idx) in trendPoints"
                        :key="idx"
                        :cx="pad + ((chartW - pad * 2) * (p.ts - trendPoints[0].ts)) / Math.max(1, trendPoints[trendPoints.length - 1].ts - trendPoints[0].ts)"
                        :cy="chartH - pad - ((chartH - pad * 2) * (p.value - Math.min(...trendPoints.map((t) => t.value)))) / Math.max(1, Math.max(...trendPoints.map((t) => t.value)) - Math.min(...trendPoints.map((t) => t.value)))"
                        r="2"
                        fill="#38bdf8"
                        opacity="0.6"
                    />
                    <circle v-if="lastPoint" :cx="lastPoint.x" :cy="lastPoint.y" r="3" fill="#ef4444" />
                </svg>
                <div class="chart-legend">
                    <span>Points: {{ trendPoints.length }}</span>
                    <span v-if="lastValue !== null">Last: {{ lastValue }}</span>
                </div>
            </div>
            <div v-else class="hint">No trend data yet.</div>
        </section>

        <section class="redisdata">
            <h3>Redis Data</h3>
            <p class="hint">Schema and visualization are placeholders pending backend contract.</p>
            <div v-if="redisError" class="error">{{ redisError }}</div>
            <div v-if="!redisData.length"><em>No redis data</em></div>
            <div v-else>
                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Total Records</th>
                            <th>Top Prediction</th>
                            <th>Similarity</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(row, idx) in pagedData" :key="idx">
                            <td>{{ row.timestamp || '-' }}</td>
                            <td>{{ row.total_records ?? '-' }}</td>
                            <td>
                                {{
                                    row.anomaly_detection_results && row.anomaly_detection_results.length
                                        ? row.anomaly_detection_results[0].zsl_pred
                                        : '-'
                                }}
                            </td>
                            <td>
                                {{
                                    row.anomaly_detection_results && row.anomaly_detection_results.length
                                        ? (typeof row.anomaly_detection_results[0].zsl_similarity === 'number'
                                            ? row.anomaly_detection_results[0].zsl_similarity.toFixed(3)
                                            : String(row.anomaly_detection_results[0].zsl_similarity))
                                        : '-'
                                }}
                            </td>
                            <td>
                                <details>
                                    <summary style="cursor: pointer">Show JSON</summary>
                                    <pre style="max-height: 360px; overflow:auto; background:#f8f8f8; padding:0.5rem; border-radius:0.3rem">{{ JSON.stringify(row, null, 2) }}</pre>
                                </details>
                            </td>
                        </tr>
                    </tbody>
                </table>

                <div class="pagination">
                    <button class="primary-small-button" @click="setPage(page - 1)" :disabled="page <= 1">Prev</button>
                    <span>Page</span>
                    <input class="default-input input-small" v-model.number="page" @change="setPage(page)" />
                    <span>/ {{ totalPages }}</span>
                    <button class="primary-small-button" @click="setPage(page + 1)" :disabled="page >= totalPages">Next</button>

                    <label class="per-page">Per page:
                        <select class="select-small default-input" v-model.number="pageSize" @change="setPageSize(pageSize)">
                            <option v-for="opt in [25,50,100]" :key="opt" :value="opt">{{ opt }}</option>
                        </select>
                    </label>

                    <span class="total">Total: {{ total }}</span>
                </div>
                <details class="raw-data">
                    <summary>Raw Redis Data</summary>
                    <pre>{{ JSON.stringify(redisData, null, 2) }}</pre>
                </details>
            </div>
        </section>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue';
import { fetchWithAuth } from '@/utils';
import { URLs } from '@/urls';

interface BlacklistItem {
    source?: string;
    ip?: string;
    cidr?: string;
    pattern?: string;
    action?: string;
    mode?: string;
    control?: string;
    scope?: string;
    target?: string;
    reason?: string;
    note?: string;
    updated_at?: string;
    updatedAt?: string;
    updateTime?: string;
    [key: string]: unknown;
}

function isRecord(v: unknown): v is Record<string, unknown> {
    return typeof v === 'object' && v !== null;
}

// Blacklist state
const blacklist = ref<BlacklistItem[]>([]);
const blError = ref('');

type ControlType = 'Annotation' | 'ConfigMap';
interface ControlKeyItem {
    key: string;
    type: ControlType;
    desc: string;
}
const supportedControls: ControlKeyItem[] = [
    {
        key: 'nginx.ingress.kubernetes.io/limit-rps',
        type: 'Annotation',
        desc: 'Requests-per-second limit (often keyed by client IP/route)',
    },
    { key: 'nginx.ingress.kubernetes.io/limit-burst', type: 'Annotation', desc: 'Burst capacity; pairs with limit-rps' },
    { key: 'nginx.ingress.kubernetes.io/limit-connections', type: 'Annotation', desc: 'Max concurrent connections' },
    {
        key: 'nginx.ingress.kubernetes.io/allowlist-source-range',
        type: 'Annotation',
        desc: 'Allowed source CIDR list (preferred)',
    },
    {
        key: 'nginx.ingress.kubernetes.io/whitelist-source-range',
        type: 'Annotation',
        desc: 'Legacy key (compatible); same as allowlist-source-range',
    },
    {
        key: 'nginx.ingress.kubernetes.io/configuration-snippet',
        type: 'Annotation',
        desc: 'Custom NGINX snippet (privileged; use with care)',
    },
    {
        key: 'allow-snippet-annotations',
        type: 'ConfigMap',
        desc: 'Allow usage of configuration-snippet annotation (global switch)',
    },
    { key: 'use-forwarded-headers', type: 'ConfigMap', desc: 'Trust X-Forwarded-* headers to obtain real external client IP' },
];

// TODO: Backend URL is TBD. Using a placeholder for now; replace this constant later.
// const BLACKLIST_URL = '/api/ingress/blacklist/';
let blTimer: number | undefined;

// Traffic Trend (simple line chart without external deps)
interface TrendPoint {
    ts: number;
    value: number;
}
// const TRAFFIC_TREND_URL = '/api/ingress/traffic/trend/'; // placeholder
const trend = ref<TrendPoint[]>([]);
const trendError = ref('');
let trendTimer: number | undefined;

const trendPoints = computed(() => trend.value);
const chartW = 800;
const chartH = 180;
const pad = 10;
const pathD = computed(() => {
    const pts = trendPoints.value;
    if (!pts.length) return '';
    const xs = pts.map((p) => p.ts);
    const ys = pts.map((p) => p.value);
    const minX = Math.min(...xs),
        maxX = Math.max(...xs);
    const minY = Math.min(...ys),
        maxY = Math.max(...ys);
    const dx = Math.max(1, maxX - minX);
    const dy = Math.max(1, maxY - minY);
    const xScale = (x: number) => pad + ((chartW - pad * 2) * (x - minX)) / dx;
    const yScale = (y: number) => chartH - pad - ((chartH - pad * 2) * (y - minY)) / dy;
    const move = `M ${xScale(pts[0].ts)} ${yScale(pts[0].value)}`;
    const lines = pts
        .slice(1)
        .map((p) => `L ${xScale(p.ts)} ${yScale(p.value)}`)
        .join(' ');
    return `${move} ${lines}`;
});
const lastPoint = computed(() => {
    const pts = trendPoints.value;
    if (!pts.length) return null as null | { x: number; y: number };
    const xs = pts.map((p) => p.ts);
    const ys = pts.map((p) => p.value);
    const minX = Math.min(...xs),
        maxX = Math.max(...xs);
    const minY = Math.min(...ys),
        maxY = Math.max(...ys);
    const dx = Math.max(1, maxX - minX);
    const dy = Math.max(1, maxY - minY);
    const xScale = (x: number) => pad + ((chartW - pad * 2) * (x - minX)) / dx;
    const yScale = (y: number) => chartH - pad - ((chartH - pad * 2) * (y - minY)) / dy;
    const p = pts[pts.length - 1];
    return { x: xScale(p.ts), y: yScale(p.value) };
});
const lastValue = computed(() => (trendPoints.value.length ? trendPoints.value[trendPoints.value.length - 1].value : null));

// Redis Data state
interface DetectionResult {
    // optional detailed fields from detector
    timestamp?: number | string; // may be epoch seconds (number) or ISO string
    packet?: Record<string, unknown>;
    anomaly_detection?: number;
    zsl_pred?: string;
    zsl_similarity?: number | string;
    [key: string]: unknown;
}

interface NewReport {
    // top-level timestamp may be ISO string; if missing we may derive from first result
    timestamp?: string;
    total_records?: number;
    anomaly_detection_results?: DetectionResult[];
    [key: string]: unknown;
}

const redisData = ref<NewReport[]>([]);
const redisError = ref('');

// Pagination state for redisData
const page = ref(1);
const pageSize = ref(50);
const total = computed(() => redisData.value.length);
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)));

const pagedData = computed(() => {
    const start = (page.value - 1) * pageSize.value;
    return redisData.value.slice(start, start + pageSize.value);
});

watch([redisData, pageSize], () => {
    // when data or page size changes, ensure current page is within range
    if (page.value > totalPages.value) page.value = totalPages.value;
    if (page.value < 1) page.value = 1;
});

function setPage(n: number) {
    if (n >= 1 && n <= totalPages.value) page.value = n;
}

function setPageSize(n: number) {
    pageSize.value = n;
    page.value = 1; // reset to first page on size change
}

async function loadBlacklist() {
    blError.value = '';
    try {
        const res = await fetchWithAuth(URLs.INGRESS_BLACKLIST);
        if (!res.ok) {
            blError.value = `Load blacklist failed: ${res.status}`;
            return;
        }
        const data: unknown = await res.json();
        const itemsUnknown: unknown = Array.isArray(data)
            ? data
            : isRecord(data) && Array.isArray((data as Record<string, unknown>).items)
              ? (data as Record<string, unknown>).items
              : isRecord(data) && Array.isArray((data as Record<string, unknown>).data)
                ? (data as Record<string, unknown>).data
                : [];
        const itemsArr = Array.isArray(itemsUnknown) ? itemsUnknown : [];
        blacklist.value = itemsArr.map((i) => i as BlacklistItem);
    } catch (e: unknown) {
        blError.value = e instanceof Error ? e.message : 'Load blacklist error';
    }
}

async function loadTrend() {
    trendError.value = '';
    try {
        const res = await fetchWithAuth(URLs.INGRESS_TRAFFIC_TREND);
        if (!res.ok) {
            trendError.value = `Load trend failed: ${res.status}`;
            return;
        }
        const data: unknown = await res.json();
        const listUnknown: unknown = Array.isArray(data)
            ? data
            : isRecord(data) && Array.isArray((data as Record<string, unknown>).points)
              ? (data as Record<string, unknown>).points
              : isRecord(data) && Array.isArray((data as Record<string, unknown>).data)
                ? (data as Record<string, unknown>).data
                : [];
        const items = Array.isArray(listUnknown) ? listUnknown : [];
        const parsed: TrendPoint[] = items
            .map((it): TrendPoint | null => {
                if (isRecord(it)) {
                    const v = it.value as unknown;
                    const tRaw = (it.ts ?? it.timestamp ?? it.time) as unknown;
                    const val = typeof v === 'number' ? v : Number(v);
                    const tsNum = typeof tRaw === 'number' ? tRaw : typeof tRaw === 'string' ? Date.parse(tRaw) : NaN;
                    if (!Number.isNaN(val) && !Number.isNaN(tsNum)) return { ts: tsNum, value: val };
                }
                return null;
            })
            .filter((x): x is TrendPoint => x !== null);
        // keep last 120 points max
        trend.value = parsed.sort((a, b) => a.ts - b.ts).slice(-120);
    } catch (e: unknown) {
        trendError.value = e instanceof Error ? e.message : 'Load trend error';
    }
}

async function loadRedisData() {
    redisError.value = '';
    try {
        // TODO: Replace URLs.INGRESS_REDIS_DATA_READ with the final API once available
        const res = await fetchWithAuth(URLs.INGRESS_REDIS_DATA_READ);
        if (!res.ok) {
            redisError.value = `Load redis data failed: ${res.status}`;
            return;
        }
        const data: unknown = await res.json();
        // Parse common shapes:
        // possible shapes: { new_reports: [...] }, { data: { new_reports: [...] } }, { new_report: [...] }, or directly [...]
        let reports: unknown[] = [];
        if (isRecord(data)) {
            const d = data as Record<string, unknown>;
            if (Array.isArray(d.new_reports)) reports = d.new_reports as unknown[];
            else if (Array.isArray(d.new_report)) reports = d.new_report as unknown[];
            else if (isRecord(d.data) && Array.isArray((d.data as Record<string, unknown>).new_reports)) reports = (d.data as Record<string, unknown>).new_reports as unknown[];
            else if (Array.isArray(d.data)) reports = d.data as unknown[];
        } else if (Array.isArray(data)) {
            reports = data;
        }

        // normalize to NewReport[] and sort by timestamp desc, keep latest 200
        const parsedReports: NewReport[] = (reports
            .filter(isRecord)
            .map((raw) => {
                const r = raw as Record<string, unknown>;
                const maybeResults = r['anomaly_detection_results'] ?? r['anomaly_detection_result'] ?? r['results'] ?? [];
                const resultsRaw = Array.isArray(maybeResults) ? maybeResults : [];

                const normalizedResults: DetectionResult[] = resultsRaw
                    .filter((it: unknown): it is Record<string, unknown> => isRecord(it))
                    .map((it: Record<string, unknown>) => {
                        const anomaly_detection = typeof it['anomaly_detection'] === 'number'
                            ? (it['anomaly_detection'] as number)
                            : (typeof it['anomaly_detection'] === 'string' ? Number(it['anomaly_detection'] as string) : 0);

                        const zsl_pred = typeof it['zsl_pred'] === 'string'
                            ? (it['zsl_pred'] as string)
                            : (typeof it['pred'] === 'string' ? (it['pred'] as string) : '');

                        const zsl_similarity = typeof it['zsl_similarity'] === 'number'
                            ? (it['zsl_similarity'] as number)
                            : (typeof it['zsl_similarity'] === 'string' ? Number(it['zsl_similarity'] as string) : undefined);

                        let timestamp: number | string | undefined = undefined;
                        if (typeof it['timestamp'] === 'number') timestamp = it['timestamp'] as number;
                        else if (typeof it['timestamp'] === 'string') timestamp = it['timestamp'] as string;
                        else if (typeof it['ts'] === 'number') timestamp = it['ts'] as number;
                        else if (typeof it['ts'] === 'string') timestamp = it['ts'] as string;

                        const packet = isRecord(it['packet']) ? (it['packet'] as Record<string, unknown>) : (isRecord(it['pkt']) ? (it['pkt'] as Record<string, unknown>) : undefined);

                        const nr: DetectionResult = {
                            ...it,
                            anomaly_detection,
                            zsl_pred,
                            zsl_similarity,
                            timestamp,
                            packet,
                        };
                        return nr;
                    });

                const total = typeof r.total_records === 'number' ? r.total_records : (typeof r.total === 'number' ? r.total : normalizedResults.length);
                let topTimestamp: string | undefined = undefined;
                if (typeof r.timestamp === 'string' && r.timestamp) topTimestamp = r.timestamp;
                else if (normalizedResults.length && typeof normalizedResults[0].timestamp === 'number') {
                    // epoch seconds -> ISO
                    topTimestamp = new Date((normalizedResults[0].timestamp as number) * 1000).toISOString();
                } else if (normalizedResults.length && typeof normalizedResults[0].timestamp === 'string') {
                    // maybe already ISO or numeric-string
                    const t = normalizedResults[0].timestamp as string;
                    const asNum = Number(t);
                    topTimestamp = !Number.isNaN(asNum) ? new Date(asNum * 1000).toISOString() : t;
                }

                const report: NewReport = {
                    ...r,
                    timestamp: topTimestamp,
                    total_records: total,
                    anomaly_detection_results: normalizedResults,
                };
                return report;
            })
            .filter((x) => !!x.timestamp)
            .sort((a, b) => {
                const ta = Date.parse(a.timestamp as string);
                const tb = Date.parse(b.timestamp as string);
                return tb - ta;
            })
            .slice(0, 200));

        redisData.value = parsedReports;
    } catch (e: unknown) {
        redisError.value = e instanceof Error ? e.message : 'Load redis data error';
    }
}

onMounted(() => {
    loadBlacklist();
    loadTrend();
    loadRedisData();
    blTimer = window.setInterval(loadBlacklist, 30_000);
    trendTimer = window.setInterval(loadTrend, 30_000);
});

onBeforeUnmount(() => {
    if (blTimer) window.clearInterval(blTimer);
    if (trendTimer) window.clearInterval(trendTimer);
});
</script>

<style scoped>
.page { max-width: 1080px; display: flex; flex-direction: column; gap: var(--space-4); }
.actions { display: flex; gap: var(--space-2); margin-bottom: 1rem; flex-wrap: wrap; }
.error { color: var(--color-danger); margin: 0.5rem 0; }
textarea { width: 100%; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: var(--radius-md); color: var(--color-text-primary); padding: var(--space-3); }
table { width: 100%; border-collapse: collapse; background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: var(--radius-md); overflow: hidden; }
th, td { border: 1px solid var(--glass-border); padding: 0.4rem 0.6rem; text-align: left; color: var(--color-text-primary); }
th { background: var(--color-surface-hover); }
.supported { margin-top: 1rem; }
.supported h4 { margin: 0.5rem 0; }
.pagination { margin-top: 0.5rem; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.pagination .per-page { margin-left: 1rem; }
.pagination .total { margin-left: auto; }
.raw-data { margin-top: 0.5rem; }
.raw-data pre { white-space: pre-wrap; word-break: break-word; }
.input-small { max-width: 64px; }
.select-small { max-width: 96px; }

.blacklist { margin-bottom: 1rem; }
.hint { color: var(--color-text-muted); font-size: 12px; margin: 0.25rem 0 0.5rem; }
.trend { margin: 1rem 0; }
.chart-wrap { width: 100%; max-width: 1080px; }
.chart { width: 100%; height: 180px; display: block; }
.chart-legend { color: var(--color-text-muted); font-size: 12px; margin-top: 0.25rem; display: flex; gap: 1rem; }
</style>
