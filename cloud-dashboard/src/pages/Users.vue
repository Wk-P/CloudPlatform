<template>
    <div>
        <h2>👤 Users management</h2>
        <p>Users management plane</p>

        <el-button type="primary" @click="dialogVisible = true">Add user</el-button>

        <el-table :data="users" border style="width: 100%; margin-top: 20px">
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="username" label="username"></el-table-column>
            <el-table-column prop="role" label="role"></el-table-column>
            <el-table-column label="operation">
                <template #default="{ row }">
                    <el-button type="danger" size="small" @click="deleteUser(row.id)">Delete</el-button>
                </template>
            </el-table-column>
        </el-table>

        <!-- 添加用户对话框 -->
        <el-dialog v-model="dialogVisible" title="add-user">
            <el-form :model="newUser">
                <el-form-item label="username">
                    <el-input v-model="newUser.username"></el-input>
                </el-form-item>
                <el-form-item label="role">
                    <el-select v-model="newUser.role">
                        <el-option label="admin" value="admin"></el-option>
                        <el-option label="user" value="user"></el-option>
                    </el-select>
                </el-form-item>
            </el-form>
            <el-button type="primary" @click="addUser">Add</el-button>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref } from "vue";

const users = ref([
    { id: 1, username: "admin", role: "admin" },
    { id: 2, username: "user1", role: "user" },
]);

const dialogVisible = ref(false);
const newUser = ref({ username: "", role: "user" });

const addUser = () => {
    if (!newUser.value.username) return;

    users.value.push({
        id: users.value.length + 1,
        username: newUser.value.username,
        role: newUser.value.role,
    });

    dialogVisible.value = false;
    newUser.value = { username: "", role: "user" };
};

const deleteUser = (id) => {
    users.value = users.value.filter((user) => user.id !== id);
};
</script>

<style scoped>
.el-table {
    margin-top: 20px;
}
</style>
