<template>
  <div class="mobiliario-management">
    <!-- Header con título y controles -->
    <div class="management-header">
      <div class="header-content">
        <h1>🪑 Gestión de Mobiliario</h1>
        <p class="subtitle">Administra el inventario de mobiliario de la biblioteca</p>
      </div>
      
      <div class="header-actions">
        <button 
          @click="toggleShowInactive" 
          class="btn-action btn-action-warning" 
          :class="{ 'active': showInactiveMobiliario }"
        >
          {{ showInactiveMobiliario ? 'Ocultar Desactivados' : 'Mostrar Desactivados' }}
        </button>
        
        <router-link 
          v-if="canCreateMobiliario"
          to="/admin/mobiliario/crear" 
          class="btn-create-mobiliario"
        >
          ➕ Agregar Mobiliario
        </router-link>
      </div>
    </div>

    <!-- Estadísticas rápidas -->
    <div class="mobiliario-stats">
      <div class="stat-card">
        <div class="stat-icon">🪑</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.total || 0 }}</div>
          <div class="stat-label">Total Mobiliario</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.activos || 0 }}</div>
          <div class="stat-label">Activos</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⚠️</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.desactivados || 0 }}</div>
          <div class="stat-label">Desactivados</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🔧</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.enReparacion || 0 }}</div>
          <div class="stat-label">En Reparación</div>
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
            placeholder="Buscar por descripción, área, tipo..."
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <button @click="handleSearch" class="search-btn">
            Buscar
          </button>
        </div>
        
        <div class="filters-row">
          <div class="filter-group">
            <label>Tipo:</label>
            <select v-model="filters.tipo_mobiliario_id" class="filter-select">
              <option value="">TODOS LOS TIPOS</option>
              <option value="1">Sillas</option>
              <option value="2">Mesas</option>
              <option value="3">Escritorios</option>
              <option value="4">Sillones</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>Estado:</label>
            <select v-model="filters.estado_id" class="filter-select">
              <option value="">Todos los estados</option>
              <option value="1">✅ Activo</option>
              <option value="2">⚠️ En uso</option>
              <option value="3">🔧 En reparación</option>
              <option v-if="canViewDesactivados" value="4">❌ Desactivado</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>Área:</label>
            <select v-model="filters.area_id" class="filter-select" v-if="areas.length > 0">
              <option value="">Todas las áreas</option>
              <option v-for="area in areas" :key="area.id" :value="area.id">
                {{ area.nombre }}
              </option>
            </select>
            <input
              v-else
              v-model="filters.area_id"
              type="number"
              placeholder="ID de área"
              class="filter-input"
              min="1"
            />
          </div>
          
          <div class="filter-group">
            <label>Ordenar por:</label>
            <select v-model="sortBy" class="filter-select">
              <option value="descripcion">Descripción (A-Z)</option>
              <option value="fecha_ingreso">Fecha ingreso (Más reciente)</option>
              <option value="tipo">Tipo</option>
              <option value="area">Área</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Estado de carga -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando inventario...</p>
    </div>

    <!-- Estado de error -->
    <div v-else-if="error" class="error-state">
      <p>❌ Error: {{ error }}</p>
      <button @click="loadMobiliario" class="btn btn-primary">Reintentar</button>
    </div>

    <!-- Tabla de mobiliario -->
    <div v-else class="mobiliario-table-container">
      <table class="mobiliario-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Descripción</th>
            <th>Tipo</th>
            <th>Área</th>
            <th>Estado</th>
            <th>Fecha Ingreso</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in paginatedItems" :key="item.id" 
              :class="{ 'inactive': item.estado_id === 4 }">
            <td class="item-id">#{{ item.id }}</td>
            <td>
              <strong>{{ item.descripcion }}</strong>
              <div class="item-meta">
                <small>Creado por: {{ item.usuario_creador_nombre }}</small>
              </div>
            </td>
            <td>{{ item.tipo_mobiliario_nombre }}</td>
            <td>{{ item.area_nombre || 'No asignada' }}</td>
            <td>
              <span :class="getStatusClass(item)" class="status-badge">
                {{ getStatusText(item) }}
              </span>
            </td>
            <td>
              {{ formatFecha(item.fecha_ingreso) }}
              <div v-if="item.fecha_ultimo_cambio_estado" class="small-text">
                Último cambio: {{ formatFecha(item.fecha_ultimo_cambio_estado) }}
              </div>
            </td>
            <td class="actions-cell">
              <div class="actions-buttons">
                <!-- Botón Editar -->
                <button 
                  v-if="canEditMobiliario"
                  @click="openEditModal(item)" 
                  class="btn-action" 
                  title="Editar mobiliario"
                  :disabled="isProcessing"
                >
                  ✏️
                </button>
                
                <!-- Botón Desactivar -->
                <button 
                  v-if="canDesactivateMobiliario && item.estado_id !== 4"
                  @click="confirmAction(item, 'desactivate')" 
                  class="btn-action btn-action-warning" 
                  title="Desactivar mobiliario"
                  :disabled="isProcessing"
                >
                  ⚠️
                </button>
                
                <!-- Botón Reactivar -->
                <button 
                  v-if="canReactivateMobiliario && item.estado_id === 4"
                  @click="confirmAction(item, 'reactivate')" 
                  class="btn-action btn-action-success" 
                  title="Reactivar mobiliario"
                  :disabled="isProcessing"
                >
                  🔄
                </button>
                
                <!-- Botón Eliminar -->
                <button 
                  v-if="canDeleteMobiliario && item.estado_id === 4"
                  @click="confirmAction(item, 'delete')" 
                  class="btn-action btn-action-danger" 
                  title="Eliminar permanentemente"
                  :disabled="isProcessing"
                >
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Sin resultados -->
      <div v-if="!isLoading && filteredItems.length === 0" class="empty-state">
        <div class="empty-icon">🪑</div>
        <h3>No se encontró mobiliario</h3>
        <p v-if="searchQuery || hasActiveFilters">
          No hay resultados para tu búsqueda. Intenta con otros términos.
        </p>
        <p v-else>
          No hay mobiliario registrado en el sistema.
        </p>
        <button @click="resetFilters" class="btn btn-primary">
          🔄 Mostrar todos
        </button>
      </div>
    </div>

    <!-- Paginación -->
    <div v-if="!isLoading && !error && filteredItems.length > 0" class="pagination-section">
      <div class="pagination-info">
        Mostrando {{ startItem }}-{{ endItem }} de {{ filteredItems.length }} items
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

    <!-- Modal de Edición (se implementará en Fase 2) -->
    <div v-if="showEditModal" class="modal-overlay">
      <!-- Este modal se manejará en Fase 2 -->
      <div class="modal-content">
        <div class="modal-header">
          <h3>✏️ Editar Mobiliario</h3>
          <button @click="closeEditModal" class="modal-close-btn">×</button>
        </div>
        <div class="modal-body">
          <p>La edición se manejará como modal overlay en la Fase 2.</p>
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
          <div v-if="itemToAction" class="item-preview">
            <strong>{{ itemToAction.descripcion }}</strong>
            <div>Tipo: {{ itemToAction.tipo_mobiliario_nombre }}</div>
            <div>Área: {{ itemToAction.area_nombre || 'No asignada' }}</div>
            <div>Estado: {{ getStatusText(itemToAction) }}</div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeConfirmModal" class="btn btn-secondary" :disabled="isProcessing">
            Cancelar
          </button>
          <button @click="executeAction" class="btn" :class="confirmModalBtnClass" :disabled="isProcessing">
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
import { mobiliarioService } from '@/services/mobiliario'
import { usePermissions } from '@/composables/usePermissions'

const router = useRouter()
const { hasPermission } = usePermissions()

// State principal
const mobiliario = ref([])
const isLoading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const itemsPerPage = ref(10)
const showInactiveMobiliario = ref(false)
const isProcessing = ref(false)

// Búsqueda y filtros
const searchQuery = ref('')
const filters = ref({
  tipo_mobiliario_id: '',
  estado_id: '',
  area_id: ''
})
const sortBy = ref('descripcion')

// Data auxiliar
const tiposMobiliario = ref([])
const estadosMobiliario = ref([])
const areas = ref([])

// Modales
const showEditModal = ref(false)
const showConfirmModal = ref(false)
const itemToAction = ref(null)
const actionType = ref('') // 'desactivate', 'reactivate', 'delete'

// Toast
const showSuccessToast = ref(false)
const successMessage = ref('')
const successDetails = ref('')

// Permisos
const canCreateMobiliario = computed(() => hasPermission('canCreateFurniture'))
const canEditMobiliario = computed(() => hasPermission('canEditFurniture'))
const canDeleteMobiliario = computed(() => hasPermission('canDeleteFurniture'))
const canReactivateMobiliario = computed(() => hasPermission('canReactivatFurniture'))
const canDesactivateMobiliario = computed(() => hasPermission('canDesactivateFurniture'))
const canViewDesactivados = computed(() => hasPermission('canViewMobiliario'))

// Computed
const filteredItems = computed(() => {
  let result = [...mobiliario.value]
  
  // Filtrar desactivados
  if (!showInactiveMobiliario.value) {
    result = result.filter(item => item.estado_id !== 4)
  }
  
  // Aplicar filtros
  if (filters.value.tipo_mobiliario_id) {
    result = result.filter(item => 
      item.tipo_mobiliario_id === parseInt(filters.value.tipo_mobiliario_id)
    )
  }
  
  if (filters.value.estado_id) {
    result = result.filter(item => 
      item.estado_id === parseInt(filters.value.estado_id)
    )
  }
  
  if (filters.value.area_id) {
    result = result.filter(item => 
      item.area_id === parseInt(filters.value.area_id)
    )
  }
  
  // Búsqueda por texto
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(item => 
      item.descripcion?.toLowerCase().includes(query) ||
      item.area_nombre?.toLowerCase().includes(query) ||
      item.tipo_mobiliario_nombre?.toLowerCase().includes(query)
    )
  }
  
  // Ordenar
  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'descripcion':
        return (a.descripcion || '').localeCompare(b.descripcion || '')
      case 'fecha_ingreso':
        const dateA = a.fecha_ingreso ? new Date(a.fecha_ingreso) : new Date(0)
        const dateB = b.fecha_ingreso ? new Date(b.fecha_ingreso) : new Date(0)
        return dateB - dateA
      case 'tipo':
        return (a.tipo_mobiliario_nombre || '').localeCompare(b.tipo_mobiliario_nombre || '')
      case 'area':
        return (a.area_nombre || '').localeCompare(b.area_nombre || '')
      default:
        return 0
    }
  })
  
  return result
})

const stats = computed(() => {
  const total = mobiliario.value.length
  const activos = mobiliario.value.filter(item => item.estado_id === 1).length
  const desactivados = mobiliario.value.filter(item => item.estado_id === 4).length
  const enReparacion = mobiliario.value.filter(item => item.estado_id === 3).length
  
  return {
    total,
    activos,
    desactivados,
    enReparacion
  }
})

const totalPages = computed(() => {
  return Math.ceil(filteredItems.value.length / itemsPerPage.value) || 1
})

const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredItems.value.slice(start, end)
})

const startItem = computed(() => {
  return (currentPage.value - 1) * itemsPerPage.value + 1
})

const endItem = computed(() => {
  const end = currentPage.value * itemsPerPage.value
  return end > filteredItems.value.length ? filteredItems.value.length : end
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
    case 'desactivate': return '⚠️ Desactivar Mobiliario'
    case 'reactivate': return '🔄 Reactivar Mobiliario'
    case 'delete': return '🗑️ Eliminar Mobiliario Permanentemente'
    default: return 'Confirmar Acción'
  }
})

const confirmModalMessage = computed(() => {
  if (!itemToAction.value) return ''
  
  switch (actionType.value) {
    case 'desactivate':
      return `¿Estás seguro de desactivar "${itemToAction.value.descripcion}"? El mobiliario será marcado como desactivado.`
    case 'reactivate':
      return `¿Estás seguro de reactivar "${itemToAction.value.descripcion}"? El mobiliario volverá al inventario activo.`
    case 'delete':
      return `¿Estás seguro de eliminar permanentemente "${itemToAction.value.descripcion}"? Esta acción NO se puede deshacer.`
    default:
      return ''
  }
})

const confirmModalActionText = computed(() => {
  switch (actionType.value) {
    case 'desactivate': return 'Sí, Desactivar'
    case 'reactivate': return 'Sí, Reactivar'
    case 'delete': return 'Sí, Eliminar Permanentemente'
    default: return 'Confirmar'
  }
})

const confirmModalBtnClass = computed(() => {
  switch (actionType.value) {
    case 'desactivate': return 'btn-warning'
    case 'reactivate': return 'btn-success'
    case 'delete': return 'btn-danger'
    default: return 'btn-primary'
  }
})

// Métodos principales
const loadMobiliario = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await mobiliarioService.getMobiliarios()
    
    if (response && response.mobiliarios) {
      mobiliario.value = response.mobiliarios
    } else if (Array.isArray(response)) {
      mobiliario.value = response
    } else {
      mobiliario.value = []
    }
    
    // Cargar catálogos
    await loadCatalogos()
    
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error cargando el inventario'
    console.error('Error cargando mobiliario:', err)
  } finally {
    isLoading.value = false
  }
}

const loadCatalogos = async () => {
  try {
    const [tipos, estados, areasData] = await Promise.all([
      mobiliarioService.getTiposMobiliario(),
      mobiliarioService.getEstadosMobiliario(),
      mobiliarioService.getAreas()
    ])
    
    tiposMobiliario.value = tipos
    estadosMobiliario.value = estados
    areas.value = areasData
  } catch (err) {
    console.error('Error cargando catálogos:', err)
  }
}

// Formatos y utilidades
const getStatusClass = (item) => {
  const classes = {
    1: 'status-active',       // Activo
    2: 'status-in-use',       // En uso
    3: 'status-repair',       // En reparación
    4: 'status-inactive'      // Desactivado
  }
  return classes[item.estado_id] || 'status-unknown'
}

const getStatusText = (item) => {
  const statusMap = {
    1: '✅ Activo',
    2: '⚠️ En uso',
    3: '🔧 En reparación',
    4: '❌ Desactivado'
  }
  return statusMap[item.estado_id] || item.estado_nombre || 'Desconocido'
}

const formatFecha = (fecha) => {
  if (!fecha) return 'N/A'
  try {
    return new Date(fecha).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch {
    return 'Fecha inválida'
  }
}

// Búsqueda y filtros
const handleSearch = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  searchQuery.value = ''
  filters.value = {
    tipo_mobiliario_id: '',
    estado_id: '',
    area_id: ''
  }
  currentPage.value = 1
}

const toggleShowInactive = () => {
  showInactiveMobiliario.value = !showInactiveMobiliario.value
  currentPage.value = 1
}

// Modal de edición (placeholder para Fase 2)
const openEditModal = (item) => {
  // Por ahora navegamos a la ruta de edición
  // En Fase 2 esto será un modal overlay
  router.push(`/admin/mobiliario/editar/${item.id}`)
}

const closeEditModal = () => {
  showEditModal.value = false
}

// Confirmación de acciones
const confirmAction = (item, type) => {
  // Verificar permisos
  if (type === 'desactivate' && !canDesactivateMobiliario.value) {
    showToast('Permiso denegado', 'No tienes permisos para desactivar mobiliario', 'error')
    return
  }
  if (type === 'reactivate' && !canReactivateMobiliario.value) {
    showToast('Permiso denegado', 'No tienes permisos para reactivar mobiliario', 'error')
    return
  }
  if (type === 'delete' && !canDeleteMobiliario.value) {
    showToast('Permiso denegado', 'No tienes permisos para eliminar mobiliario', 'error')
    return
  }
  
  itemToAction.value = item
  actionType.value = type
  showConfirmModal.value = true
}

const closeConfirmModal = () => {
  if (!isProcessing.value) {
    showConfirmModal.value = false
    itemToAction.value = null
    actionType.value = ''
  }
}

const executeAction = async () => {
  if (!itemToAction.value || isProcessing.value) return
  
  isProcessing.value = true
  
  try {
    switch (actionType.value) {
      case 'desactivate':
        await mobiliarioService.desactivateMobiliario(itemToAction.value.id)
        itemToAction.value.estado_id = 4
        itemToAction.value.estado_nombre = 'Desactivado'
        successMessage.value = 'Mobiliario desactivado'
        successDetails.value = `"${itemToAction.value.descripcion}" ha sido desactivado`
        break
        
      case 'reactivate':
        await mobiliarioService.reactivateMobiliario(itemToAction.value.id)
        itemToAction.value.estado_id = 1
        itemToAction.value.estado_nombre = 'Activo'
        successMessage.value = 'Mobiliario reactivado'
        successDetails.value = `"${itemToAction.value.descripcion}" ha sido reactivado`
        break
        
      case 'delete':
        await mobiliarioService.deleteMobiliario(itemToAction.value.id)
        mobiliario.value = mobiliario.value.filter(m => m.id !== itemToAction.value.id)
        successMessage.value = 'Mobiliario eliminado'
        successDetails.value = `"${itemToAction.value.descripcion}" ha sido eliminado permanentemente`
        break
    }
    
    showSuccessToast.value = true
    setTimeout(() => {
      showSuccessToast.value = false
    }, 3000)
    
    closeConfirmModal()
    
  } catch (err) {
    console.error(`Error en acción ${actionType.value}:`, err)
    showToast('Error', `No se pudo completar la acción: ${err.response?.data?.detail || err.message}`, 'error')
  } finally {
    isProcessing.value = false
  }
}

// Toast helper
const showToast = (title, message, type = 'success') => {
  successMessage.value = title
  successDetails.value = message
  showSuccessToast.value = true
  
  setTimeout(() => {
    showSuccessToast.value = false
  }, 3000)
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

// Watchers
watch([searchQuery, filters, sortBy, showInactiveMobiliario], () => {
  currentPage.value = 1
})

// Ciclo de vida
onMounted(() => {
  loadMobiliario()
})
</script>

<style scoped>
/* ===== ESTILOS PRINCIPALES (similares a UserManagement) ===== */

.mobiliario-management {
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
  background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%); /* Verde para mobiliario */
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

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.btn-create-mobiliario {
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
  text-decoration: none;
}

.btn-create-mobiliario:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
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

.btn-action:hover:not(:disabled) {
  background: #f8f9fa;
  transform: scale(1.1);
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-action-warning:hover:not(:disabled) {
  background: #fff3cd;
}

.btn-action-success:hover:not(:disabled) {
  background: #d4edda;
}

.btn-action-danger:hover:not(:disabled) {
  background: #f8d7da;
}

/* Estadísticas */
.mobiliario-stats {
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
  background: #2E7D32;
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

.filter-input {
  padding: 0.5rem;
  border: 2px solid #dee2e6;
  border-radius: 0.5rem;
  min-width: 150px;
}

/* Tabla */
.mobiliario-table-container {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.mobiliario-table {
  width: 100%;
  border-collapse: collapse;
}

.mobiliario-table th {
  background: #f8f9fa;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #e9ecef;
}

.mobiliario-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

.mobiliario-table tbody tr:hover {
  background: #f8f9fa;
}

.mobiliario-table tbody tr.inactive {
  background: #fff5f5;
  opacity: 0.8;
}

.mobiliario-table tbody tr.inactive:hover {
  background: #ffeaea;
}

/* Badges de estado */
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-active {
  background: #d4edda;
  color: #155724;
}

.status-in-use {
  background: #fff3cd;
  color: #856404;
}

.status-repair {
  background: #d1ecf1;
  color: #0c5460;
}

.status-inactive {
  background: #f8d7da;
  color: #721c24;
}

.status-unknown {
  background: #e9ecef;
  color: #495057;
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

/* Confirm modal */
.confirm-modal {
  max-width: 400px;
}

.item-preview {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  border-left: 4px solid #dc3545;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
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
  border-top: 3px solid #2E7D32;
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
  background: #2E7D32;
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

/* Botones */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #2E7D32;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1B5E20;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.btn-warning:hover:not(:disabled) {
  background: #e0a800;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #218838;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

/* Utilitarios */
.small-text {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.25rem;
}

.item-meta {
  margin-top: 0.25rem;
}

.item-id {
  font-family: 'Courier New', monospace;
  color: #666;
}

/* Responsive */
@media (max-width: 768px) {
  .management-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .header-actions {
    width: 100%;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .btn-create-mobiliario {
    width: 100%;
    justify-content: center;
  }
  
  .mobiliario-stats {
    grid-template-columns: 1fr 1fr;
  }
  
  .filters-row {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .mobiliario-table {
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
</style>