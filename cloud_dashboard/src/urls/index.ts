// Centralized backend API endpoints for the frontend
// Use these keys from views/components instead of hardcoding URLs

export const URLs = {
    // Auth
    AUTH_REGISTER: '/api/auth/register/',
    AUTH_LOGIN: '/api/auth/login/',
    AUTH_JWT_ISSUE: '/api/auth/jwt/issue/',
    AUTH_ME: '/api/auth/me/',

    // Anomaly detection / Ingress
    INGRESS_BLACKLIST: '/api/anomaly/ingress/blacklist/',
    INGRESS_TRAFFIC_TREND: '/api/anomaly/ingress/traffic/trend/',

    INGRESS_REDIS_DATA_READ: '/api/anomaly/ingress/redis/data/read/',
} as const;

export type UrlKey = keyof typeof URLs;

// Optional helper to build URLs with query params
export function withQuery(base: string, params: Record<string, string | number | boolean | undefined | null>) {
    const usp = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') usp.set(k, String(v));
    });
    const q = usp.toString();
    return q ? `${base}?${q}` : base;
}
