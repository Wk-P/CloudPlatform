<template>
    <div class="default-layout-wrapper">
        <!-- Sidebar Menu -->
        <div width="200px">
            <ul class="dl-menu">
                <li class="dl-menu-item">
                    <RouterLink class="router-link" :to="{ name: 'dashboard' }">Dashboard</RouterLink>
                </li>
                <li class="dl-menu-item">
                    <RouterLink class="router-link" :to="{ name: 'clusters' }">Clusters</RouterLink>
                </li>
                <li class="dl-menu-item">
                    <RouterLink class="router-link" :to="{ name: 'commands' }">Commands</RouterLink>
                </li>
                <li class="dl-menu-item">
                    <RouterLink class="router-link" :to="{ name: 'monitoring' }">Monitoring</RouterLink>
                </li>
                <li class="dl-menu-item">
                    <RouterLink class="router-link" :to="{ name: 'pods' }">Pods</RouterLink>
                </li>
                <li class="dl-menu-item">
                    <RouterLink class="router-link" :to="{ name: 'nodes' }">Nodes</RouterLink>
                </li>
                <li class="dl-menu-item">
                    <RouterLink class="router-link" :to="{ name: 'users' }">Users</RouterLink>
                </li>
                <li class="dl-menu-item">
                    <RouterLink class="router-link" :to="{ name: 'help' }">Help</RouterLink>
                </li>
            </ul>
        </div>

        <!-- Main Content -->
        <div class="main-content-wrapper">
            <h1>Cloud Management Dashboard</h1>
            <div>
                <RouterView />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
</script>

<style scoped>
.default-layout-wrapper {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: row;
}

.dl-menu {
    border: none;
}

.dl-menu-item {
    width: 200px;
}

.main-content-wrapper {
    padding: 1rem;
    width: 100%;
}

.router-link {
    padding: 1rem;
}

.main-content-wrapper h1 {
    text-align: center;
    background-color: rgba(0, 255, 255, 0.503);
    border-radius: 0.4rem;
    padding: 1rem;
    color: #222;
    margin-bottom: 1rem;
}
</style>
