<template>
    <div class="modern-layout">
        <!-- Modern Sidebar -->
        <aside class="sidebar">
            <!-- Logo Section -->
            <div class="sidebar-header">
                <div class="logo">
                    <div class="logo-icon">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M12 2L2 7L12 12L22 7L12 2Z"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            />
                            <path
                                d="M2 17L12 22L22 17"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            />
                            <path
                                d="M2 12L12 17L22 12"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            />
                        </svg>
                    </div>
                    <span class="logo-text">CloudPlatform</span>
                </div>
            </div>

            <!-- Navigation Menu -->
            <nav class="sidebar-nav">
                <div class="nav-section">
                    <span class="nav-section-title">Main Menu</span>
                    <ul class="nav-list">
                        <li v-for="(item, index) in navList" :key="index" class="nav-item">
                            <RouterLink :to="{ name: item.name }" class="nav-link" :class="{ active: isActive(index) }">
                                <span class="nav-icon" v-html="item.icon"></span>
                                <span class="nav-label">{{ item.label }}</span>
                                <span v-if="isActive(index)" class="nav-indicator"></span>
                            </RouterLink>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Sidebar Footer -->
            <div class="sidebar-footer">
                <div class="user-card glass-card">
                    <div class="user-avatar">
                        <span>{{ userInitial }}</span>
                    </div>
                    <div class="user-info">
                        <div class="user-name">Admin</div>
                        <div class="user-role">Administrator</div>
                    </div>
                </div>
            </div>
        </aside>

        <!-- Main Content Area -->
        <main class="main-content">
            <!-- Top Header Bar -->
            <header class="content-header glass-card">
                <div class="header-left">
                    <h1 class="page-title">{{ currentPageTitle }}</h1>
                </div>
                <div class="header-right">
                    <button class="btn-icon" title="Notifications">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            />
                            <path
                                d="M13.73 21a2 2 0 0 1-3.46 0"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            />
                        </svg>
                        <span class="notification-badge">3</span>
                    </button>
                    <button class="btn-icon" title="Settings">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle
                                cx="12"
                                cy="12"
                                r="3"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            />
                            <path
                                d="M12 1v6m0 6v6m6-11.66l-3 5.2m-6 0l-3-5.2M20.66 7l-5.2 3m0 6l5.2 3M3.34 7l5.2 3m0 6l-5.2 3"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            />
                        </svg>
                    </button>
                </div>
            </header>

            <!-- Page Content -->
            <div class="content-body">
                <RouterView v-slot="{ Component }">
                    <transition name="page" mode="out-in">
                        <component :is="Component" />
                    </transition>
                </RouterView>
            </div>
        </main>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { RouterView, useRoute } from 'vue-router';

const navList = [
    {
        name: 'dashboard',
        label: 'Dashboard',
        icon: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="3" y="3" width="7" height="7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><rect x="14" y="3" width="7" height="7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><rect x="14" y="14" width="7" height="7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><rect x="3" y="14" width="7" height="7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    },
    {
        name: 'clusters',
        label: 'Clusters',
        icon: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><polyline points="3.27 6.96 12 12.01 20.73 6.96" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="12" y1="22.08" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    },
    {
        name: 'commands',
        label: 'Commands',
        icon: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><polyline points="4 17 10 11 4 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="12" y1="19" x2="20" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    },
    {
        name: 'monitoring',
        label: 'Monitoring',
        icon: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    },
    {
        name: 'users',
        label: 'Users',
        icon: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    },
    {
        name: 'detector',
        label: 'Detector',
        icon: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="12" y1="9" x2="12" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="12" y1="17" x2="12.01" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    },
    {
        name: 'help',
        label: 'Help',
        icon: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="12" y1="17" x2="12.01" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    },
];

const route = useRoute();

const isActive = (index: number) => {
    return navList[index].name === route.name;
};

const currentPageTitle = computed(() => {
    const current = navList.find((item) => item.name === route.name);
    return current?.label || 'CloudPlatform';
});

const userInitial = computed(() => 'A');
</script>

<style scoped>
/* ==================== LAYOUT ==================== */
.modern-layout {
    display: flex;
    min-height: 100vh;
    background: var(--color-bg-primary);
}

/* ==================== SIDEBAR ==================== */
.sidebar {
    width: var(--sidebar-width);
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid var(--glass-border);
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    z-index: 100;
}

/* Sidebar Header */
.sidebar-header {
    padding: var(--space-6);
    border-bottom: 1px solid var(--glass-border);
}

.logo {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.logo-icon {
    width: 40px;
    height: 40px;
    background: var(--gradient-primary);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
}

.logo-icon svg {
    width: 24px;
    height: 24px;
}

.logo-text {
    font-size: 1.25rem;
    font-weight: 700;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Sidebar Navigation */
.sidebar-nav {
    flex: 1;
    padding: var(--space-4);
    overflow-y: auto;
}

.nav-section {
    margin-bottom: var(--space-6);
}

.nav-section-title {
    display: block;
    padding: var(--space-2) var(--space-3);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--color-text-muted);
}

.nav-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
}

.nav-link {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-md);
    color: var(--color-text-secondary);
    text-decoration: none;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all var(--duration-normal) var(--ease-out);
    position: relative;
    overflow: hidden;
}

.nav-link::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    width: 3px;
    height: 100%;
    background: var(--gradient-primary);
    opacity: 0;
    transition: opacity var(--duration-normal) var(--ease-out);
}

.nav-link:hover {
    background: var(--color-surface-hover);
    color: var(--color-text-primary);
}

.nav-link.active {
    background: var(--color-surface-active);
    color: var(--color-primary-light);
}

.nav-link.active::before {
    opacity: 1;
}

.nav-icon {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: inherit;
}

.nav-icon svg {
    width: 100%;
    height: 100%;
}

.nav-label {
    flex: 1;
}

.nav-indicator {
    width: 6px;
    height: 6px;
    background: var(--gradient-primary);
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%,
    100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

/* Sidebar Footer */
.sidebar-footer {
    padding: var(--space-4);
    border-top: 1px solid var(--glass-border);
}

.user-card {
    padding: var(--space-3);
    display: flex;
    align-items: center;
    gap: var(--space-3);
    cursor: pointer;
}

.user-avatar {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);
    background: var(--gradient-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 0.875rem;
}

.user-info {
    flex: 1;
}

.user-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--color-text-primary);
}

.user-role {
    font-size: 0.75rem;
    color: var(--color-text-muted);
}

/* ==================== MAIN CONTENT ==================== */
.main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* Content Header */
.content-header {
    margin: var(--space-4);
    padding: var(--space-4) var(--space-6);
    display: flex;
    align-items: center;
    justify-content: space-between;
    animation: slideIn var(--duration-normal) var(--ease-out);
}

.header-left {
    flex: 1;
}

.page-title {
    font-size: 1.5rem;
    font-weight: 700;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.header-right {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.btn-icon {
    width: 40px;
    height: 40px;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-text-secondary);
    cursor: pointer;
    transition: all var(--duration-normal) var(--ease-out);
    position: relative;
}

.btn-icon svg {
    width: 20px;
    height: 20px;
}

.btn-icon:hover {
    background: var(--color-surface-hover);
    color: var(--color-text-primary);
    border-color: var(--color-primary);
}

.notification-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    width: 18px;
    height: 18px;
    background: var(--gradient-danger);
    border-radius: 50%;
    font-size: 0.625rem;
    font-weight: 600;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-md);
}

/* Content Body */
.content-body {
    flex: 1;
    padding: 0 var(--space-4) var(--space-4);
    overflow-y: auto;
}

/* ==================== PAGE TRANSITION ==================== */
.page-enter-active,
.page-leave-active {
    transition: all var(--duration-normal) var(--ease-out);
}

.page-enter-from {
    opacity: 0;
    transform: translateY(10px);
}

.page-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 768px) {
    .sidebar {
        width: 80px;
    }

    .logo-text,
    .nav-label,
    .nav-section-title,
    .user-info {
        display: none;
    }

    .sidebar-header {
        padding: var(--space-4);
    }

    .logo {
        justify-content: center;
    }

    .nav-link {
        justify-content: center;
        padding: var(--space-3);
    }

    .user-card {
        justify-content: center;
    }
}
</style>
