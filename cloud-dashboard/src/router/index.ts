import { createRouter, createWebHistory } from "vue-router";

const routes = [
    {
        path: "/",
        redirect: "/dashboard",
    },
    {
        path: "/",
        component: () => import("@/layouts/DefaultLayout.vue"),
        children: [
            {
                path: "dashboard",
                component: () => import("@/pages/Dashboard.vue"),
            },
            {
                path: "clusters",
                component: () => import("@/pages/Cluster.vue"),
            },
            {
                path: "commands",
                component: () => import("@/pages/Commands.vue"),
            },
            {
                path: "monitoring",
                component: () => import("@/pages/Monitoring.vue"),
            },
            {
                path: "users",
                component: () => import("@/pages/Users.vue"),
            },
            {
                path: "help",
                component: () => import("@/pages/Help.vue"),
            },
        ],
    },
    {
        path: "/login",
        component: () => import("@/pages/Login.vue"),
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
