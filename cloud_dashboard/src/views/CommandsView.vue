<template>
    <div>
        <h2>Commands Console</h2>
        <p>Here run Kubernetes and OpenStack Commands.</p>

        <input v-model="command" class="default-input command-input" placeholder="Enter kubectl or openstack commands" />

        <button class="primary-small-button" @click="executeCommand">RUN</button>

        <div class="command-output">
            <h4 style="margin-bottom: 1rem">Result Output</h4>
            <table class="result-table">
                <tr v-for="(value, key) in result" :key="key">
                    <th class="item-head">{{ key.replace('_', ' ') }}</th>
                    <td class="item-body" :class="{ cmd: key === 'cmd' }">{{ value }}</td>
                </tr>
            </table>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { CommandResult } from '@/interfaces';
import { postCommand } from '@/utils';
import { ref } from 'vue';

const command = ref<string>('');
const result = ref<CommandResult | null>(null);

const executeCommand = async () => {
    if (!command.value) return;

    result.value = await postCommand(command.value);
};
</script>

<style scoped>
.command-output {
    margin-top: 20px;
    padding: 2rem;
    background-color: white;
    border-radius: 8px;
    box-shadow: 3px 3px 1rem 0.5rem #aaa;
}

.result-table,
.item-body,
.item-head {
    border: #444 solid 1px;
}

.item-body,
.item-head {
    padding: 0.5rem 1rem;
}

.item-head {
    width: 200px;
}

.item-body {
    text-align: left;
    width: 500px;
    text-wrap: wrap;
}

.command-input {
    margin-right: 2rem;
    color: rgb(38, 38, 232);
}

.cmd {
    font-weight: bold;
    color: rgb(38, 38, 232);
}
</style>
