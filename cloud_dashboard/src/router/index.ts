import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            redirect: { name: 'dashboard' },
        },
        {
            path: '/',
            component: () => import('@/layouts/DefaultLayout.vue'),
            meta: { requiresAuth: true },
            children: [
                {
                    path: 'dashboard',
                    name: 'dashboard',
                    component: () => import('@/views/DashboardView.vue'),
                },
                {
                    path: 'clusters',
                    name: 'clusters',
                    component: () => import('@/views/ClustersView.vue'),
                },
                {
                    path: 'cluster/:id',
                    name: 'cluster-detail',
                    component: () => import('@/views/ClusterView.vue'),
                },
                {
                    path: 'commands',
                    name: 'commands',
                    component: () => import('@/views/CommandsView.vue'),
                },
                {
                    path: 'monitoring',
                    name: 'monitoring',
                    component: () => import('@/views/MonitoringView.vue'),
                },
                {
                    path: 'users',
                    name: 'users',
                    component: () => import('@/views/UsersView.vue'),
                },
                {
                    path: 'help',
                    name: 'help',
                    component: () => import('@/views/HelpView.vue'),
                },
                {
                    path: 'detector',
                    name: 'detector',
                    component: () => import('@/views/DetectorView.vue'),
                },
            ],
        },
        {
            path: '/login',
            name: 'login',
            component: () => import('@/views/LoginView.vue'),
        },
        {
            path: '/register',
            name: 'register',
            component: () => import('@/views/RegisterView.vue'),
        },
    ],
});

export default router;

// ---- Auth helpers ----
function normalizeToken(t: string | null): string | null {
    if (!t) return null;
    let s = t.trim();
    // strip wrapping quotes if any
    if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
        s = s.slice(1, -1);
    }
    // strip Bearer prefix (case-insensitive)
    s = s.replace(/^Bearer\s+/i, '');
    return s;
}

function getStoredToken(): string | null {
    const raw =
        localStorage.getItem('cloud-dashboard-token') ||
        sessionStorage.getItem('cloud-dashboard-token');
    return normalizeToken(raw);
}

// note: clearStoredToken removed since guard only checks presence now

// base64UrlToBase64 helper removed (not used in current guard)

// JWT helpers removed for now; can be re-enabled when enforcing token expiry

// Global auth guard: redirect to /login when no platform token
router.beforeEach((to, _from, next) => {
    const needsAuth = to.matched.some(r => {
        const m = r.meta as Record<string, unknown> | undefined;
        return Boolean(m && (m as { requiresAuth?: boolean }).requiresAuth);
    });
    if (!needsAuth) return next();
    const token = getStoredToken();
    if (!token) return next({ name: 'login', query: { redirect: to.fullPath } });
    next();
});
