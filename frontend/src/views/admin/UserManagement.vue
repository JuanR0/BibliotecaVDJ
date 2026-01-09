<!-- views/admin/UserManagementView.vue -->
<template>
  <div class="user-management-view">
    <h1>👥 Gestión de Usuarios y Permisos</h1>
    
    <!-- Lista de usuarios -->
    <div class="users-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Código</th>
            <th>Tipo Usuario</th>
            <th>Permisos</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.nombre_completo }}</td>
            <td>{{ user.codigo_universitario }}</td>
            <td>
              <select v-model="user.tipo_usuario_id" @change="updateUserType(user)">
                <option value="1">Usuario Común</option>
                <option value="2">Admin Básico</option>
                <option value="3">Admin Avanzado</option>
                <option value="4">Super Admin</option>
              </select>
            </td>
            <td>
              <button @click="showPermissionsModal(user)" class="btn btn-small">
                🔧 Gestionar
              </button>
            </td>
            <td>
              <span :class="user.esta_activo ? 'status-active' : 'status-inactive'">
                {{ user.esta_activo ? '✅ Activo' : '❌ Inactivo' }}
              </span>
            </td>
            <td>
              <button @click="toggleUserStatus(user)" class="btn btn-small">
                {{ user.esta_activo ? 'Desactivar' : 'Activar' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal de permisos -->
    <div v-if="selectedUser" class="permissions-modal">
      <!-- Editor de permisos específicos -->
    </div>
  </div>
</template>