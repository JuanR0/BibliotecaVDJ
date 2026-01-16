<template>
  <div class="user-management">
    <!-- Header con título y botón crear -->
    <div class="management-header">
      <div class="header-content">
        <h1>👥 Gestión de Usuarios</h1>
        <p class="subtitle">Administra los usuarios del sistema bibliotecario</p>
        <div class="user-info" v-if="authStore.userName">
          <small>
            Super Admin: {{ authStore.userName }} 
            ({{ authStore.userCode }})
          </small>
        </div>
      </div>
      
      <div class="header-actions">
        <button @click="goToCreateUser" class="btn btn-primary btn-create-user" title="Crear nuevo usuario">
          <span class="btn-icon">➕</span>
          <span class="btn-text">Nuevo Usuario</span>
        </button>
        
        <button @click="toggleShowInactive" class="btn btn-outline" :class="{ 'active': showInactiveUsers }">
          {{ showInactiveUsers ? 'Ocultar Inactivos' : 'Mostrar Inactivos' }}
        </button>
      </div>
    </div>

    <!-- Estadísticas rápidas -->
    <div class="user-stats">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <div class="stat-value">{{ filteredUsers.length }}</div>
          <div class="stat-label">Usuarios Activos</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👤</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.commonUsers }}</div>
          <div class="stat-label">Usuarios Comunes</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🛡️</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.adminUsers }}</div>
          <div class="stat-label">Administradores</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.inactiveUsers }}</div>
          <div class="stat-label">Usuarios Inactivos</div>
        </div>
      </div>
    </div>

    <!-- Barra de búsqueda y filtros -->
    <div class="search-section">
      <div class="search-container">
        <div class="search-bar">
          <div class="search-icon">🔍</div>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por código, nombre..."
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <button @click="handleSearch" class="search-btn">
            Buscar
          </button>
        </div>
        
        <div class="filters-row">
          <div class="filter-group">
            <label>Tipo de usuario:</label>
            <select v-model="filters.tipo_usuario_id" class="filter-select">
              <option value="">Todos los tipos</option>
              <option value="1">Usuario Común</option>
              <option value="2">Admin Básico</option>
              <option value="3">Admin Avanzado</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>Ordenar por:</label>
            <select v-model="sortBy" class="filter-select">
              <option value="nombre">Nombre (A-Z)</option>
              <option value="codigo">Código (A-Z)</option>
              <option value="fecha_registro">Fecha registro (Más reciente)</option>
              <option value="tipo">Tipo de usuario</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Estado de carga -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando usuarios...</p>
    </div>

    <!-- Estado de error -->
    <div v-else-if="error" class="error-state">
      <p>❌ Error: {{ error }}</p>
      <button @click="loadUsers" class="btn btn-primary">Reintentar</button>
    </div>

    <!-- Tabla de usuarios -->
    <div v-else class="users-table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Código Universitario</th>
            <th>Nombre Completo</th>
            <th>Tipo de Usuario</th>
            <th>Estado</th>
            <th>Fecha Registro</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in paginatedUsers" :key="user.id" 
              :class="{ 'inactive': !user.esta_activo }">
            <td class="user-id">#{{ user.id }}</td>
            <td>
              <div class="user-code">{{ user.codigo_universitario }}</div>
            </td>
            <td>
              <strong>{{ user.nombre_completo }}</strong>
              <div class="user-meta">
                <small>Relación: {{ getRelacionNombre(user.relacion_institucional_id) }}</small>
              </div>
            </td>
            <td>
              <span :class="getTipoUsuarioClass(user.tipo_usuario_id)" class="user-type-badge">
                {{ getTipoUsuarioNombre(user.tipo_usuario_id) }}
              </span>
            </td>
            <td>
              <span :class="getEstadoClass(user.esta_activo)" class="status-badge">
                {{ user.esta_activo ? '✅ Activo' : '❌ Inactivo' }}
              </span>
            </td>
            <td>
              {{ formatFecha(user.fecha_registro) }}
              <div v-if="user.fecha_ultimo_cambio_estado" class="small-text">
                Último cambio: {{ formatFecha(user.fecha_ultimo_cambio_estado) }}
              </div>
            </td>
            <td class="actions-cell">
              <div class="actions-buttons">
                <!-- Botón Ver Detalles -->
                <button 
                  @click="viewUserDetails(user)" 
                  class="btn-action" 
                  title="Ver detalles"
                >
                  👁️
                </button>
                
                <!-- Botón Editar (solo si no es super admin) -->
                <button 
                  v-if="canEditUser(user)"
                  @click="openEditModal(user)" 
                  class="btn-action" 
                  title="Editar usuario"
                  :disabled="isProcessing"
                >
                  ✏️
                </button>
                
                <!-- Botón Activar/Desactivar -->
                <button v-if="user.esta_activo && canEditUser(user)" @click="confirmDeactivate(user)" class="btn-action btn-action-warning" title="Desactivar usuario" :disabled="isProcessing">⏸️</button>
                
                <button 
                  v-else-if="!user.esta_activo"
                  @click="confirmActivate(user)" 
                  class="btn-action btn-action-success" 
                  title="Activar usuario"
                  :disabled="isProcessing"
                >
                  ▶️
                </button>
                
                <!-- Botón Eliminar (solo para usuarios inactivos) -->
                <button v-if="!user.esta_activo" @click="confirmDelete(user)" class="btn-action btn-action-danger" title="Eliminar permanentemente" :disabled="isProcessing">🗑️</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Sin resultados -->
      <div v-if="!isLoading && filteredUsers.length === 0" class="empty-state">
        <div class="empty-icon">👤</div>
        <h3>No se encontraron usuarios</h3>
        <p v-if="searchQuery || hasActiveFilters">
          No hay resultados para tu búsqueda. Intenta con otros términos.
        </p>
        <p v-else>
          No hay usuarios registrados en el sistema.
        </p>
        <button @click="resetFilters" class="btn btn-primary">
          🔄 Mostrar todos
        </button>
      </div>
    </div>

    <!-- Paginación -->
    <div v-if="!isLoading && !error && filteredUsers.length > 0" class="pagination-section">
      <div class="pagination-info">
        Mostrando {{ startItem }}-{{ endItem }} de {{ filteredUsers.length }} usuarios
      </div>
      
      <div class="pagination-controls">
        <button 
          @click="prevPage" 
          :disabled="currentPage === 1" 
          class="pagination-btn"
        >
          ← Anterior
        </button>
        
        <div class="page-numbers">
          <span 
            v-for="page in visiblePages" 
            :key="page" 
            @click="goToPage(page)" 
            :class="{ 'active': page === currentPage }" 
            class="page-number"
          >
            {{ page }}
          </span>
        </div>
        
        <button 
          @click="nextPage" 
          :disabled="currentPage === totalPages" 
          class="pagination-btn"
        >
          Siguiente →
        </button>
      </div>
      
      <div class="items-per-page">
        <label>Mostrar:</label>
        <select v-model="itemsPerPage" @change="resetPagination" class="page-select">
          <option value="10">10</option>
          <option value="25">25</option>
          <option value="50">50</option>
        </select>
      </div>
    </div>

    <!-- Modal de Edición -->
    <div v-if="showEditModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>✏️ Editar Usuario</h3>
          <button @click="closeEditModal" class="modal-close-btn" :disabled="isProcessing">×</button>
        </div>
        
        <div class="modal-body">
          <div v-if="userToEdit" class="edit-form">
            <div class="form-group">
              <label>Código Universitario:</label>
              <input 
                type="text" 
                v-model="editForm.codigo_universitario" 
                class="form-input"
                disabled
              />
              <small class="form-hint">No se puede modificar</small>
            </div>
            
            <div class="form-group">
              <label>Nombre Completo:</label>
              <input 
                type="text" 
                v-model="editForm.nombre_completo" 
                class="form-input"
                placeholder="Nombre completo"
              />
            </div>
            
            <div class="form-group">
              <label>Tipo de Usuario:</label>
              <select v-model="editForm.tipo_usuario_id" class="form-select">
                <option 
                  v-for="type in userTypes" 
                  :key="type.id" 
                  :value="type.id"
                  :disabled="type.id === 4"
                >
                  {{ type.nombre }} - {{ type.descripcion }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Relación Institucional:</label>
              <select v-model="editForm.relacion_institucional_id" class="form-select">
                <option 
                  v-for="rel in institutionalRelations" 
                  :key="rel.id" 
                  :value="rel.id"
                >
                  {{ rel.nombre }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Estado:</label>
              <div class="status-toggle">
                <button 
                  @click="editForm.esta_activo = true"
                  :class="{ 'active': editForm.esta_activo }"
                  class="toggle-btn toggle-active"
                >
                  ✅ Activo
                </button>
                <button 
                  @click="editForm.esta_activo = false"
                  :class="{ 'active': !editForm.esta_activo }"
                  class="toggle-btn toggle-inactive"
                >
                  ❌ Inactivo
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeEditModal" class="btn btn-secondary" :disabled="isProcessing">
            Cancelar
          </button>
          <button @click="saveUserChanges" class="btn btn-primary" :disabled="isProcessing">
            <span v-if="isProcessing" class="spinner-small"></span>
            {{ isProcessing ? 'Guardando...' : 'Guardar Cambios' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmación -->
    <div v-if="showConfirmModal" class="modal-overlay">
      <div class="modal-content confirm-modal">
        <div class="modal-header">
          <h3>{{ confirmModalTitle }}</h3>
          <button @click="closeConfirmModal" class="modal-close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <p>{{ confirmModalMessage }}</p>
          <div v-if="userToAction" class="user-preview">
            <strong>{{ userToAction.nombre_completo }}</strong>
            <div>Código: {{ userToAction.codigo_universitario }}</div>
            <div>Tipo: {{ getTipoUsuarioNombre(userToAction.tipo_usuario_id) }}</div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeConfirmModal" class="btn btn-secondary" :disabled="isProcessing">
            Cancelar
          </button>
          <button @click="executeAction" class="btn btn-danger" :disabled="isProcessing">
            <span v-if="isProcessing" class="spinner-small"></span>
            {{ confirmModalActionText }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast de éxito -->
    <div v-if="showSuccessToast" class="toast success">
      <div class="toast-icon">✅</div>
      <div class="toast-content">
        <strong>{{ successMessage }}</strong>
        <p>{{ successDetails }}</p>
      </div>
      <button @click="showSuccessToast = false" class="toast-close">×</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { userService } from '@/services/users'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Verificar permisos - solo tipo 4 puede acceder
if (authStore.tipoUsuarioId !== 4) {
  router.push('/')
}

// State principal
const users = ref([])
const isLoading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const itemsPerPage = ref(10)
const showInactiveUsers = ref(false)
const isProcessing = ref(false)

// Búsqueda y filtros
const searchQuery = ref('')
const filters = ref({
  tipo_usuario_id: ''
})
const sortBy = ref('nombre')

// Modales
const showEditModal = ref(false)
const showConfirmModal = ref(false)
const userToEdit = ref(null)
const userToAction = ref(null)
const actionType = ref('') // 'activate', 'deactivate', 'delete'

// Formularios
const editForm = ref({
  id: null,
  codigo_universitario: '',
  nombre_completo: '',
  tipo_usuario_id: 1,
  relacion_institucional_id: 1,
  esta_activo: true
})

// Toast
const showSuccessToast = ref(false)
const successMessage = ref('')
const successDetails = ref('')

// Computed
const userTypes = computed(() => userService.getUserTypes())
const institutionalRelations = computed(() => userService.getInstitutionalRelations())

const filteredUsers = computed(() => {
  let result = [...users.value]
  
  // Filtrar super admins (tipo 4)
  result = userService.filterNonSuperAdmins(result)
  
  // Filtrar inactivos
  if (!showInactiveUsers.value) {
    result = result.filter(user => user.esta_activo || user.estaActivo == false)
  }
  
  // Aplicar filtro de tipo
  if (filters.value.tipo_usuario_id) {
    result = result.filter(user => user.tipo_usuario_id === parseInt(filters.value.tipo_usuario_id))
  }
  
  // Búsqueda por texto
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(user => 
      user.codigo_universitario?.toLowerCase().includes(query) ||
      user.nombre_completo?.toLowerCase().includes(query)
    )
  }
  
  // Ordenar
  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'nombre':
        return a.nombre_completo?.localeCompare(b.nombre_completo)
      case 'codigo':
        return a.codigo_universitario?.localeCompare(b.codigo_universitario)
      case 'fecha_registro':
        return new Date(b.fecha_registro) - new Date(a.fecha_registro)
      case 'tipo':
        return a.tipo_usuario_id - b.tipo_usuario_id
      default:
        return 0
    }
  })
  
  return result
})

const stats = computed(() => {
  const allUsers = userService.filterNonSuperAdmins(users.value)
  return {
    commonUsers: allUsers.filter(u => u.tipo_usuario_id === 1).length,
    adminUsers: allUsers.filter(u => u.tipo_usuario_id >= 2 && u.tipo_usuario_id <= 3).length,
    inactiveUsers: allUsers.filter(u => !u.esta_activo).length
  }
})

const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / itemsPerPage.value) || 1
})

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredUsers.value.slice(start, end)
})

const startItem = computed(() => {
  return (currentPage.value - 1) * itemsPerPage.value + 1
})

const endItem = computed(() => {
  const end = currentPage.value * itemsPerPage.value
  return end > filteredUsers.value.length ? filteredUsers.value.length : end
})

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  
  if (totalPages.value <= maxVisible) {
    for (let i = 1; i <= totalPages.value; i++) pages.push(i)
  } else {
    let start = Math.max(1, currentPage.value - 2)
    let end = Math.min(totalPages.value, start + maxVisible - 1)
    
    if (end - start + 1 < maxVisible) {
      start = end - maxVisible + 1
    }
    
    for (let i = start; i <= end; i++) pages.push(i)
  }
  
  return pages
})

const hasActiveFilters = computed(() => {
  return Object.values(filters.value).some(value => 
    value !== '' && value !== null && value !== undefined
  ) || searchQuery.value.trim() !== ''
})

const confirmModalTitle = computed(() => {
  switch (actionType.value) {
    case 'activate': return '✅ Activar Usuario'
    case 'deactivate': return '⏸️ Desactivar Usuario'
    case 'delete': return '🗑️ Eliminar Usuario Permanentemente'
    default: return 'Confirmar Acción'
  }
})

const confirmModalMessage = computed(() => {
  if (!userToAction.value) return ''
  
  switch (actionType.value) {
    case 'activate':
      return `¿Estás seguro de que deseas activar al usuario "${userToAction.value.nombre_completo}"?`
    case 'deactivate':
      return `¿Estás seguro de que deseas desactivar al usuario "${userToAction.value.nombre_completo}"?`
    case 'delete':
      return `¿Estás seguro de que deseas eliminar permanentemente al usuario "${userToAction.value.nombre_completo}"? Esta acción no se puede deshacer.`
    default:
      return ''
  }
})

const confirmModalActionText = computed(() => {
  switch (actionType.value) {
    case 'activate': return 'Sí, Activar'
    case 'deactivate': return 'Sí, Desactivar'
    case 'delete': return 'Sí, Eliminar Permanentemente'
    default: return 'Confirmar'
  }
})

// Métodos
const loadUsers = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    const params = {
      pagina: currentPage.value,
      por_pagina: itemsPerPage.value * 3 // Traer más para filtrado local
    }
    
    const response = await userService.getUsers(params)
    users.value = response.usuarios || []
    
  } catch (err) {
    error.value = err.message
    console.error('Error cargando usuarios:', err)
  } finally {
    isLoading.value = false
  }
}

const canEditUser = (user) => {
  return userService.canEditUser(user)
}

const getTipoUsuarioNombre = (tipoId) => {
  return userService.getTipoUsuarioNombre(tipoId)
}

const getTipoUsuarioClass = (tipoId) => {
  const classes = {
    1: 'tipo-comun',
    2: 'tipo-admin',
    3: 'tipo-admin-avanzado',
    4: 'tipo-super-admin'
  }
  return classes[tipoId] || 'tipo-desconocido'
}

const getRelacionNombre = (relacionId) => {
  const rel = institutionalRelations.value.find(r => r.id === relacionId)
  return rel ? rel.nombre : 'Desconocida'
}

const getEstadoClass = (estaActivo) => {
  return estaActivo ? 'status-active' : 'status-inactive'
}

const formatFecha = (fechaString) => {
  return userService.formatFecha(fechaString)
}

const handleSearch = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  searchQuery.value = ''
  filters.value = { tipo_usuario_id: '' }
  currentPage.value = 1
}

const toggleShowInactive = () => {
  showInactiveUsers.value = !showInactiveUsers.value
  currentPage.value = 1
}

// Navegación
const goToCreateUser = () => {
  router.push('/SuperAdmin/usuarios/crear')
}

// Modales
const openEditModal = (user) => {
  if (!canEditUser(user)) {
    alert('No se puede editar este usuario')
    return
  }
  
  userToEdit.value = user
  editForm.value = {
    id: user.id,
    codigo_universitario: user.codigo_universitario,
    nombre_completo: user.nombre_completo,
    tipo_usuario_id: user.tipo_usuario_id,
    relacion_institucional_id: user.relacion_institucional_id,
    esta_activo: user.esta_activo
  }
  showEditModal.value = true
}

const closeEditModal = () => {
  if (!isProcessing.value) {
    showEditModal.value = false
    userToEdit.value = null
    editForm.value = {
      id: null,
      codigo_universitario: '',
      nombre_completo: '',
      tipo_usuario_id: 1,
      relacion_institucional_id: 1,
      esta_activo: true
    }
  }
}

const saveUserChanges = async () => {
  if (!userToEdit.value || isProcessing.value) return
  
  isProcessing.value = true
  
  try {
    // Preparar datos para enviar
    const updateData = {
      nombre_completo: editForm.value.nombre_completo,
      tipo_usuario_id: editForm.value.tipo_usuario_id,
      relacion_institucional_id: editForm.value.relacion_institucional_id,
      esta_activo: editForm.value.esta_activo
    }
    
    await userService.updateUser(userToEdit.value.id, updateData)
    
    // Actualizar usuario en la lista
    const index = users.value.findIndex(u => u.id === userToEdit.value.id)
    if (index !== -1) {
      Object.assign(users.value[index], updateData)
    }
    
    // Mostrar toast de éxito
    successMessage.value = 'Usuario actualizado exitosamente'
    successDetails.value = `Los cambios en ${userToEdit.value.nombre_completo} han sido guardados`
    showSuccessToast.value = true
    
    // Cerrar modal
    closeEditModal()
    
    // Ocultar toast después de 3 segundos
    setTimeout(() => {
      showSuccessToast.value = false
    }, 3000)
    
  } catch (err) {
    alert(`Error al actualizar usuario: ${err.message}`)
  } finally {
    isProcessing.value = false
  }
}

// Confirmación de acciones
const confirmActivate = (user) => {
  userToAction.value = user
  actionType.value = 'activate'
  showConfirmModal.value = true
}

const confirmDeactivate = (user) => {
  if (!canEditUser(user)) {
    alert('No se puede desactivar este usuario')
    return
  }
  userToAction.value = user
  actionType.value = 'deactivate'
  showConfirmModal.value = true
}

const confirmDelete = (user) => {
  if (!user.esta_activo) {
    userToAction.value = user
    actionType.value = 'delete'
    showConfirmModal.value = true
  }
}

const closeConfirmModal = () => {
  if (!isProcessing.value) {
    showConfirmModal.value = false
    userToAction.value = null
    actionType.value = ''
  }
}

const executeAction = async () => {
  if (!userToAction.value || isProcessing.value) return
  
  isProcessing.value = true
  
  try {
    switch (actionType.value) {
      case 'activate':
        await userService.reactivateUser(userToAction.value.id)
        userToAction.value.esta_activo = true
        successMessage.value = 'Usuario activado'
        successDetails.value = `${userToAction.value.nombre_completo} ha sido reactivado`
        break
        
      case 'deactivate':
        await userService.deactivateUser(userToAction.value.id)
        userToAction.value.esta_activo = false
        successMessage.value = 'Usuario desactivado'
        successDetails.value = `${userToAction.value.nombre_completo} ha sido desactivado`
        break
        
      case 'delete':
        await userService.deleteUser(userToAction.value.id)
        users.value = users.value.filter(u => u.id !== userToAction.value.id)
        successMessage.value = 'Usuario eliminado'
        successDetails.value = `${userToAction.value.nombre_completo} ha sido eliminado permanentemente`
        break
    }
    
    showSuccessToast.value = true
    setTimeout(() => {
      showSuccessToast.value = false
    }, 3000)
    
    closeConfirmModal()
    
  } catch (err) {
    alert(`Error: ${err.message}`)
  } finally {
    isProcessing.value = false
  }
}

// Paginación
const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const resetPagination = () => {
  currentPage.value = 1
}

// Ver detalles (placeholder)
const viewUserDetails = (user) => {
  alert(`Detalles del usuario:\n\nNombre: ${user.nombre_completo}\nCódigo: ${user.codigo_universitario}\nTipo: ${getTipoUsuarioNombre(user.tipo_usuario_id)}\nEstado: ${user.esta_activo ? 'Activo' : 'Inactivo'}\nFecha registro: ${formatFecha(user.fecha_registro)}`)
}

// Watch
watch([searchQuery, filters, sortBy, showInactiveUsers], () => {
  currentPage.value = 1
})

// Ciclo de vida
onMounted(() => {
  loadUsers()
})
</script>


<!--ESTILIZACION-->
<style scoped>
.user-management {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.management-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  border-radius: 12px;
  color: white;
}

.header-content h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.5rem;
}

.user-info small {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.btn-create-user {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-create-user:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

/* Estadísticas */
.user-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 2rem;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

/* Búsqueda */
.search-section {
  margin-bottom: 2rem;
}

.search-container {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.search-bar {
  display: flex;
  margin-bottom: 1rem;
}

.search-icon {
  display: flex;
  align-items: center;
  padding: 0 1rem;
  background: #f8f9fa;
  border: 2px solid #dee2e6;
  border-right: none;
  border-radius: 0.5rem 0 0 0.5rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #dee2e6;
  border-left: none;
  border-right: none;
  font-size: 1rem;
}

.search-btn {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 0 1.5rem;
  border-radius: 0 0.5rem 0.5rem 0;
  cursor: pointer;
  font-weight: 600;
}

.filters-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #555;
}

.filter-select {
  padding: 0.5rem;
  border: 2px solid #dee2e6;
  border-radius: 0.5rem;
  background: white;
  min-width: 150px;
}

/* Tabla */
.users-table-container {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  background: #f8f9fa;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #e9ecef;
}

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

.users-table tbody tr:hover {
  background: #f8f9fa;
}

.users-table tbody tr.inactive {
  background: #fff5f5;
  opacity: 0.8;
}

.users-table tbody tr.inactive:hover {
  background: #ffeaea;
}

/* Badges */
.user-type-badge, .status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: bold;
}

.tipo-comun {
  background: #e3f2fd;
  color: #1565c0;
}

.tipo-admin {
  background: #fff3e0;
  color: #f57c00;
}

.tipo-admin-avanzado {
  background: #e8f5e9;
  color: #2e7d32;
}

.tipo-super-admin {
  background: #f3e5f5;
  color: #7b1fa2;
}

.status-active {
  background: #d4edda;
  color: #155724;
}

.status-inactive {
  background: #f8d7da;
  color: #721c24;
}

/* Acciones */
.actions-cell {
  width: 200px;
}

.actions-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-action {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.btn-action:hover {
  background: #f8f9fa;
  transform: scale(1.1);
}

.btn-action-warning:hover {
  background: #fff3cd;
}

.btn-action-success:hover {
  background: #d4edda;
}

.btn-action-danger:hover {
  background: #f8d7da;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6c757d;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close-btn:hover {
  background: #f8f9fa;
}

.modal-body {
  padding: 1.5rem;
}

/* Formulario */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

.form-input, .form-select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #dee2e6;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.form-input:disabled {
  background: #f8f9fa;
  color: #6c757d;
}

.form-hint {
  display: block;
  margin-top: 0.25rem;
  color: #6c757d;
  font-size: 0.85rem;
}

.status-toggle {
  display: flex;
  gap: 0.5rem;
}

.toggle-btn {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #dee2e6;
  background: white;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-btn.active {
  border-color: #4f46e5;
  background: #4f46e5;
  color: white;
}

.toggle-active:hover:not(.active) {
  border-color: #28a745;
  color: #28a745;
}

.toggle-inactive:hover:not(.active) {
  border-color: #dc3545;
  color: #dc3545;
}

/* Confirm modal */
.confirm-modal {
  max-width: 400px;
}

.user-preview {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  border-left: 4px solid #dc3545;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  max-width: 350px;
  z-index: 3000;
  animation: toastSlideIn 0.3s ease-out;
  border-left: 4px solid #28a745;
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.toast-icon {
  font-size: 1.8rem;
}

.toast-content {
  flex: 1;
}

.toast-content strong {
  display: block;
  margin-bottom: 0.25rem;
  color: #212529;
}

.toast-content p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.toast-close {
  background: none;
  border: none;
  color: #6c757d;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-close:hover {
  background: #f8f9fa;
}

/* Estados */
.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 3px solid #e9ecef;
  border-top: 3px solid #4f46e5;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

.spinner-small {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.5;
}

.empty-state h3 {
  margin-bottom: 0.5rem;
  color: #333;
}

.empty-state p {
  color: #666;
  margin-bottom: 1.5rem;
}

/* Paginación */
.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.pagination-info {
  color: #666;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 2px solid #dee2e6;
  background: white;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
}

.page-number {
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-number:hover {
  background: #f8f9fa;
}

.page-number.active {
  background: #4f46e5;
  color: white;
}

.items-per-page {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
}

/* Responsive */
@media (max-width: 768px) {
  .management-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .user-stats {
    grid-template-columns: 1fr;
  }
  
  .users-table {
    display: block;
    overflow-x: auto;
  }
  
  .pagination-section {
    flex-direction: column;
    gap: 1rem;
    align-items: center;
  }
  
  .toast {
    left: 20px;
    right: 20px;
    max-width: none;
  }
}

/* Utilitarios */
.small-text {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.25rem;
}

.user-meta {
  margin-top: 0.25rem;
}

.user-id {
  font-family: 'Courier New', monospace;
  color: #666;
}

.user-code {
  font-family: 'Courier New', monospace;
  font-weight: bold;
  color: #333;
}
</style>