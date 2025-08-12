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
                    path: 'pods',
                    name: 'pods',
                    component: () => import('@/views/PodsView.vue'),
                },
                {
                    path: 'nodes',
                    name: 'nodes',
                    component: () => import('@/views/NodesView.vue'),
                },
            ],
        },
        {
            path: '/login',
            name: 'login',
            component: () => import('@/views/LoginView.vue'),
        },
    ],
});

export default router;
