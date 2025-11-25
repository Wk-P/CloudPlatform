<template>
    <div class="default-layout-wrapper">
        <!-- Sidebar Menu -->
        <div width="200px" class="ul-back">
            <ul class="dl-menu">
                <li v-for="(item, index) in navList" :key=index class="dl-menu-item" :class="{ active: isActive(index) }">
                    <RouterLink class="router-link" :to="{ name: item.name }">{{ item.label }}</RouterLink>
                </li>
            </ul>
        </div>

        <!-- Main Content -->
        <div class="main-content-wrapper">
            <div class="top-bar">
                <h1>Cloud Management Dashboard</h1>
            </div>
                <RouterView />
        </div>
    </div>
</template>

<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router';

// ul.li change to ref list
const navList = [
    {
        name: 'dashboard',
        label: 'Dashboard'
    },
    {
        name: 'clusters',
        label: 'Clusters'
    },
    {
        name: 'commands',
        label: 'Commands'
    },
    {
        name: 'monitoring',
        label: 'Monitoring'
    },
    {
        name: 'users',
        label: 'Users'
    },
    {
        name: 'detector',
        label: 'Detector'
    },
    {
        name: 'help',
        label: 'Help'
    }
]

const isActive = (index: number) => {
    return index == navList.findIndex(item => item.name === route.name);
};

const route = useRoute();
</script>

<style scoped>
.default-layout-wrapper {
    display: flex;
    flex-direction: row;
    max-width: 100dvw;
    overflow-x: hidden;
    min-height: 100vh;
}

.dl-menu {
    border: none;
    list-style: none;
    margin: 0;   /* remove default UL margins to prevent extra width */
    padding: 0;  /* remove default UL padding */
}

.dl-menu-item {
    width: 100%;
}

.main-content-wrapper {
    padding: 1rem;
    flex: 1;
}

.router-link {
    display: block;
    padding: 1rem;
    box-sizing: border-box;
}

.main-content-wrapper h1 {
    text-align: center;
    background-color: rgba(0, 255, 255, 0.503);
    border-radius: 0.5rem;
    padding: 0.5rem;
    color: #222;
    margin-bottom: 1rem;
}

.top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.top-bar h1 {
    flex: 1;
    margin-right: 12px;
}

.danger-button {
    background-color: #e2321f;
    color: #fff;
    border: none;
    padding: 10px 22px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1.2rem;
}
.danger-button:hover { background-color: #c73527; }

.ul-back {
    background-color: #22a0ca;
    width: 200px;
    max-width: 200px;
    min-width: 200px;
    box-sizing: border-box;
}

.active {
    background-color: rgba(0, 255, 255, 0.503);
}
</style>
