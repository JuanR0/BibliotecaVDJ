<template>
  <div class="mobiliario-management">
    <!-- Header -->
    <div class="catalog-header">
      <div class="header-content">
        <h1>Inventario de Mobiliario</h1>
        <p class="subtitle">Gestión y control del mobiliario de la biblioteca</p>
      </div>
      
      <!-- Estadísticas rápidas -->
      <div class="catalog-stats">
        <div class="stat-item">
          <span class="stat-icon">🪑</span>
          <div>
            <span class="stat-value">{{ stats.total || 0 }}</span>
            <span class="stat-label">Total mobiliario</span>
          </div>
        </div>
        <div class="stat-item">
          <span class="stat-icon">✅</span>
          <div>
            <span class="stat-value">{{ stats.activos || 0 }}</span>
            <span class="stat-label">Activos</span>
          </div>
        </div>
        <div class="stat-item">
          <span class="stat-icon">⚠️</span>
          <div>
            <span class="stat-value">{{ stats.desactivados || 0 }}</span>
            <span class="stat-label">Desactivados</span>
          </div>
        </div>
      </div>
      
      <!-- Botón crear -->
      <div class="header-right" v-if="canCreateMobiliario">
        <router-link to="/admin/mobiliario/crear" class="btn-create-mobiliario">
          <span class="btn-icon">➕</span>
          <span class="btn-text">Agregar Mobiliario</span>
        </router-link>
        
        <button 
          v-if="canReactivateMobiliario && stats.desactivados > 0"
          @click="goToReactivar"
          class="btn-reactivate-mobiliario"
        >
          <span class="btn-icon">🔄</span>
          <span class="btn-text">Reactivar Mobiliario</span>
          <span class="badge-count">{{ stats.desactivados }}</span>
        </button>
      </div>
    </div>

    <!-- Sistema de Búsqueda -->
    <div class="search-section">
      <div class="search-container">
        <div class="search-bar-wrapper">
          <div class="search-icon">🔍</div>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por descripción, área, tipo..."
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <button @click="handleSearch" class="search-button">
            Buscar
          </button>
          <button @click="toggleAdvancedFilters" class="filter-toggle">
            {{ showAdvancedFilters ? '▲' : '▼' }} Filtros Avanzados
          </button>
        </div>

        <!-- Filtros Avanzados -->
        <div v-if="showAdvancedFilters" class="advanced-filters">
          <div class="filters-grid">
            <div class="filter-group">
              <label>🪑 Tipo:</label>
              <select v-model="filters.tipo_mobiliario_id" class="filter-select">
                <option value="">Todos los tipos</option>
                <option 
                  v-for="tipo in tiposMobiliario" 
                  :key="tipo.id" 
                  :value="tipo.id"
                >
                  {{ tipo.nombre }}
                </option>
              </select>
            </div>

            <div class="filter-group">
              <label>📋 Estado:</label>
              <select v-model="filters.estado_id" class="filter-select">
                <option value="">Todos los estados</option>
                <option value="1">✅ Activo</option>
                <option value="2">⚠️ En uso</option>
                <option value="3">🔧 En reparación</option>
                
                <!-- Solo mostrar "Desactivados" para admins -->
                <option v-if="canViewDesactivados" value="4">Desactivado</option>
              </select>
            </div>

            <div class="filter-group">
              <label>📍 Área:</label>
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
              <label>📅 Fecha ingreso:</label>
              <input
                v-model="filters.fecha_desde"
                type="date"
                placeholder="Desde"
                class="filter-input"
              />
              <input
                v-model="filters.fecha_hasta"
                type="date"
                placeholder="Hasta"
                class="filter-input"
                style="margin-top: 0.5rem;"
              />
            </div>
          </div>

          <div class="filter-actions">
            <button @click="applyFilters" class="btn btn-primary">
              🔍 Aplicar Filtros
            </button>
            <button @click="resetFilters" class="btn btn-outline">
              🔄 Limpiar Filtros
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Vista de Resultados -->
    <div class="results-section">
      <!-- Controles de vista -->
      <div class="view-controls">
        <div class="view-options">
          <button 
            @click="viewMode = 'grid'" 
            :class="{ 'active': viewMode === 'grid' }" 
            class="view-btn"
          >
            ⏹️ Cuadrícula
          </button>
          <button 
            @click="viewMode = 'list'" 
            :class="{ 'active': viewMode === 'list' }" 
            class="view-btn"
          >
            📋 Lista
          </button>
        </div>
        
        <div class="sort-options">
          <label>Ordenar por:</label>
          <select v-model="sortBy" @change="sortMobiliario" class="sort-select">
            <option value="descripcion">Descripción (A-Z)</option>
            <option value="fecha_ingreso">Fecha ingreso (Más reciente)</option>
            <option value="tipo">Tipo</option>
            <option value="area">Área</option>
          </select>
        </div>
      </div>

      <!-- Estado de carga/error -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando inventario...</p>
      </div>

      <div v-if="error" class="error-state">
        <p>❌ Error: {{ error }}</p>
        <button @click="loadMobiliario" class="btn btn-primary">Reintentar</button>
      </div>

      <!-- VISTA CUADRICULA -->
      <div v-if="viewMode === 'grid' && !isLoading && !error" class="mobiliario-grid">
        <div v-for="item in paginatedItems" :key="item.id" class="mobiliario-card">
          <div class="mobiliario-card-header">
            <div class="mobiliario-status" :class="getStatusClass(item)">
              {{ getStatusText(item) }}
            </div>
            <div class="mobiliario-id">#{{ item.id }}</div>
          </div>
          
          <div class="mobiliario-icon">
            <span class="item-icon">🪑</span>
            <div class="item-badge" v-if="item.tipo_mobiliario_nombre">
              {{ item.tipo_mobiliario_nombre }}
            </div>
          </div>
          
          <div class="mobiliario-info">
            <h3 class="item-description">{{ item.descripcion }}</h3>
            
            <div class="item-details">
              <p><strong>📍 Área:</strong> {{ item.area_nombre || 'No asignada' }}</p>
              <p><strong>🪑 Tipo:</strong> {{ item.tipo_mobiliario_nombre }}</p>
              <p><strong>📋 Estado:</strong> {{ item.estado_nombre }}</p>
              <p><strong>👤 Creado por:</strong> {{ item.usuario_creador_nombre }}</p>
              <p><strong>📅 Fecha ingreso:</strong> {{ formatFecha(item.fecha_ingreso) }}</p>
              <p v-if="item.fecha_ultimo_cambio_estado">
                <strong>🔄 Último cambio:</strong> {{ formatFecha(item.fecha_ultimo_cambio_estado) }}
              </p>
            </div>
          </div>
          
          <div class="mobiliario-actions">
            <button @click="viewDetails(item.id)" class="btn btn-outline btn-small" title="Ver detalles">Detalles</button>
            
            <button v-if="canEditMobiliario" @click="goToEdit(item.id)" class="btn btn-warning btn-small":title="`Editar: ${item.descripcion}`">Editar</button>

            <button 
              v-if="canDesactivateMobiliario && item.estado_id !== 4" 
              @click="confirmDesactivate(item)" 
              class="btn btn-warning btn-small"
              :title="`Desactivar: ${item.descripcion}`"
              :disabled="isProcessing"
            >
              ⚠️ Desactivar
            </button>

            <button 
              v-if="canReactivateMobiliario && item.estado_id === 4" 
              @click="confirmReactivate(item)" 
              class="btn btn-success btn-small"
              :title="`Reactivar: ${item.descripcion}`"
              :disabled="isProcessing"
            >
              🔄 Reactivar
            </button>

            <button 
              v-if="canDeleteMobiliario && item.estado_id === 4" 
              @click="confirmDelete(item)" 
              class="btn btn-danger btn-small"
              :title="`Eliminar permanentemente: ${item.descripcion}`"
              :disabled="isProcessing"
            >
              🗑️ Eliminar
            </button>
          </div>
        </div>

        <!-- Sin resultados -->
        <div v-if="paginatedItems.length === 0" class="empty-card">
          <div class="empty-icon">🪑</div>
          <h3>No hay mobiliario registrado</h3>
          <p v-if="searchQuery || hasActiveFilters">
            No se encontraron resultados para tu búsqueda.
          </p>
          <p v-else>
            Comienza agregando nuevo mobiliario al inventario.
          </p>
          <router-link 
            v-if="canCreateMobiliario"
            to="/admin/mobiliario/crear" 
            class="btn btn-primary"
          >
            ➕ Agregar Primer Mobiliario
          </router-link>
        </div>
      </div>

      <!-- VISTA LISTA -->
      <div v-if="viewMode === 'list' && !isLoading && !error" class="mobiliario-list">
        <table class="mobiliario-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Descripción</th>
              <th>Tipo</th>
              <th>Área</th>
              <th>Estado</th>
              <th>Fecha Ingreso</th>
              <th v-if="canEditMobiliario || canDesactivateMobiliario">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in paginatedItems" :key="item.id">
              <td>{{ item.id }}</td>
              <td>
                <strong>{{ item.descripcion }}</strong>
                <div class="small-text">
                  Creado por: {{ item.usuario_creador_nombre }}
                </div>
              </td>
              <td>{{ item.tipo_mobiliario_nombre }}</td>
              <td>{{ item.area_nombre || 'N/A' }}</td>
              <td>
                <span :class="getStatusClass(item)" class="status-badge">
                  {{ getStatusText(item) }}
                </span>
              </td>
              <td>{{ formatFecha(item.fecha_ingreso) }}</td>
              <td v-if="canEditMobiliario || canDesactivateMobiliario">
                <div class="action-buttons">
                  <button 
                    @click="goToEdit(item.id)" 
                    class="btn-action"
                    title="Editar"
                    v-if="canEditMobiliario"
                  >
                    ✏️
                  </button>
                  
                  <button 
                    v-if="canDesactivateMobiliario && item.estado_id !== 4"
                    @click="confirmDesactivate(item)" 
                    class="btn-action"
                    title="Desactivar"
                    :disabled="isProcessing"
                  >
                    ⚠️
                  </button>
                  
                  <button 
                    v-if="canReactivateMobiliario && item.estado_id === 4"
                    @click="confirmReactivate(item)" 
                    class="btn-action"
                    title="Reactivar"
                    :disabled="isProcessing"
                  >
                    🔄
                  </button>
                  
                  <button 
                    v-if="canDeleteMobiliario && item.estado_id === 4"
                    @click="confirmDelete(item)" 
                    class="btn-action"
                    title="Eliminar permanentemente"
                    :disabled="isProcessing"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
            
            <tr v-if="paginatedItems.length === 0">
              <td colspan="7" class="empty-row">
                <div class="empty-state">
                  <div class="empty-icon">🪑</div>
                  <h3>No hay mobiliario registrado</h3>
                  <p>Comienza agregando nuevo mobiliario al inventario.</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginación -->
      <div v-if="!isLoading && !error && filteredItems.length > 0" class="pagination-section">
        <div class="pagination-info">
          Mostrando {{ startItem }}-{{ endItem }} de {{ filteredItems.length }} items
          <span v-if="searchQuery || hasActiveFilters" class="filtered-info">
            (Filtrado de {{ mobiliario.length }} total)
          </span>
        </div>
        
        <div class="pagination-controls">
          <button @click="prevPage" :disabled="currentPage === 1" class="pagination-btn">
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
            <span v-if="hasMorePages" class="page-ellipsis">...</span>
          </div>
          
          <button @click="nextPage" :disabled="currentPage === totalPages" class="pagination-btn">
            Siguiente →
          </button>
        </div>
        
        <div class="items-per-page">
          <label>Mostrar:</label>
          <select v-model="itemsPerPage" @change="resetPagination" class="page-select">
            <option value="12">12</option>
            <option value="24">24</option>
            <option value="48">48</option>
            <option value="100">100</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación desactivar -->
    <div v-if="showDesactivateModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>⚠️ Confirmar Desactivación</h3>
          <button @click="closeModal" class="modal-close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <p>¿Estás seguro de desactivar el siguiente mobiliario?</p>
          
          <div class="item-to-modify">
            <div class="item-info">
              <h4>{{ itemToModify?.descripcion }}</h4>
              <p><strong>Tipo:</strong> {{ itemToModify?.tipo_mobiliario_nombre }}</p>
              <p><strong>Área:</strong> {{ itemToModify?.area_nombre }}</p>
              <p><strong>Estado actual:</strong> {{ itemToModify?.estado_nombre }}</p>
            </div>
            
            <div class="warning-message">
              <div class="warning-icon">⚠️</div>
              <p>
                El mobiliario será marcado como "Desactivado" y se retirará del inventario activo.
                Podrás reactivarlo más tarde si es necesario.
              </p>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModal" class="btn btn-secondary" :disabled="isProcessing">
            Cancelar
          </button>
          <button @click="desactivateItem" class="btn btn-warning" :disabled="isProcessing">
            <span v-if="isProcessing" class="spinner-small"></span>
            {{ isProcessing ? 'Desactivando...' : 'Sí, Desactivar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación eliminar -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>🗑️ Confirmar Eliminación Permanente</h3>
          <button @click="closeDeleteModal" class="modal-close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <p>¿Estás seguro de eliminar PERMANENTEMENTE este mobiliario?</p>
          
          <div class="item-to-modify">
            <div class="item-info">
              <h4>{{ itemToDelete?.descripcion }}</h4>
              <p><strong>Tipo:</strong> {{ itemToDelete?.tipo_mobiliario_nombre }}</p>
              <p><strong>Área:</strong> {{ itemToDelete?.area_nombre }}</p>
              <p><strong>Estado:</strong> {{ itemToDelete?.estado_nombre }}</p>
            </div>
            
            <div class="danger-message">
              <div class="danger-icon">🚨</div>
              <p>
                <strong>¡ADVERTENCIA!</strong> Esta acción NO se puede deshacer.
                El mobiliario será eliminado permanentemente de la base de datos.
                Solo elimina si el mobiliario está dañado irreparablemente.
              </p>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeDeleteModal" class="btn btn-secondary" :disabled="isProcessing">
            Cancelar
          </button>
          <button @click="deleteItem" class="btn btn-danger" :disabled="isProcessing">
            <span v-if="isProcessing" class="spinner-small"></span>
            {{ isProcessing ? 'Eliminando...' : 'Sí, Eliminar Permanentemente' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast de éxito -->
    <div v-if="showToast" class="toast" :class="toastType">
      <div class="toast-icon">{{ toastIcon }}</div>
      <div class="toast-content">
        <strong>{{ toastTitle }}</strong>
        <p>{{ toastMessage }}</p>
      </div>
      <button @click="showToast = false" class="toast-close">×</button>
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

// State
const searchQuery = ref('')
const showAdvancedFilters = ref(false)
const viewMode = ref('grid')
const sortBy = ref('descripcion')
const isLoading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const itemsPerPage = ref(12)
const isProcessing = ref(false)

// Modales
const showDesactivateModal = ref(false)
const showDeleteModal = ref(false)
const itemToModify = ref(null)
const itemToDelete = ref(null)

// Toast
const showToast = ref(false)
const toastTitle = ref('')
const toastMessage = ref('')
const toastType = ref('success')
const toastIcon = ref('✅')

// Data
const mobiliario = ref([])
const tiposMobiliario = ref([])
const estadosMobiliario = ref([])
const areas = ref([])

// Stats
const stats = ref({
  total: 0,
  activos: 0,
  desactivados: 0
})

// Filtros
const filters = ref({
  tipo_mobiliario_id: '',
  estado_id: '',
  area_id: '',
  fecha_desde: '',
  fecha_hasta: ''
})

// Permisos
const canCreateMobiliario = computed(() => hasPermission('canCreateFurniture'))
const canEditMobiliario = computed(() => hasPermission('canEditFurniture'))
const canDeleteMobiliario = computed(() => hasPermission('canDeleteFurniture'))
const canReactivateMobiliario = computed(() => hasPermission('canReactivatFurniture'))
const canDesactivateMobiliario = computed(() => hasPermission('canDesactivateFurniture'))
const canViewDesactivados = computed(() => hasPermission('canViewMobiliario'))

// ========================================== FUNCIONES PRINCIPALES ==========================================

const loadMobiliario = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await mobiliarioService.getMobiliarios()
    
    // Data structure: { mobiliarios: [], total: 0, pagina: 0, por_pagina: 0 }
    if (response && response.mobiliarios) {
      mobiliario.value = response.mobiliarios
    } else if (Array.isArray(response)) {
      mobiliario.value = response
    } else {
      mobiliario.value = []
    }
    
    calculateStats()
    
    // Cargar catálogos si no están cargados
    if (tiposMobiliario.value.length === 0) {
      await loadCatalogos()
    }
    
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

const calculateStats = () => {
  const total = mobiliario.value.length
  const activos = mobiliario.value.filter(item => item.estado_id !== 4).length
  const desactivados = mobiliario.value.filter(item => item.estado_id === 4).length
  
  stats.value = {
    total,
    activos,
    desactivados
  }
}

// ========================================== FILTRADO Y BÚSQUEDA ==========================================

const filteredItems = computed(() => {
  let result = [...mobiliario.value]
  
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
  
  // Filtros por fecha
  if (filters.value.fecha_desde) {
    const fechaDesde = new Date(filters.value.fecha_desde)
    result = result.filter(item => {
      if (!item.fecha_ingreso) return false
      const fechaItem = new Date(item.fecha_ingreso)
      return fechaItem >= fechaDesde
    })
  }
  
  if (filters.value.fecha_hasta) {
    const fechaHasta = new Date(filters.value.fecha_hasta)
    fechaHasta.setHours(23, 59, 59, 999) // Incluir todo el día
    result = result.filter(item => {
      if (!item.fecha_ingreso) return false
      const fechaItem = new Date(item.fecha_ingreso)
      return fechaItem <= fechaHasta
    })
  }
  
  // Búsqueda por texto
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(item => 
      item.descripcion?.toLowerCase().includes(query) ||
      item.area_nombre?.toLowerCase().includes(query) ||
      item.tipo_mobiliario_nombre?.toLowerCase().includes(query) ||
      item.estado_nombre?.toLowerCase().includes(query) ||
      item.usuario_creador_nombre?.toLowerCase().includes(query)
    )
  }
  
  // Ordenamiento
  result.sort((a, b) => {
    if (sortBy.value === 'descripcion') {
      return (a.descripcion || '').localeCompare(b.descripcion || '')
    }
    if (sortBy.value === 'fecha_ingreso') {
      const dateA = a.fecha_ingreso ? new Date(a.fecha_ingreso) : new Date(0)
      const dateB = b.fecha_ingreso ? new Date(b.fecha_ingreso) : new Date(0)
      return dateB - dateA
    }
    if (sortBy.value === 'tipo') {
      return (a.tipo_mobiliario_nombre || '').localeCompare(b.tipo_mobiliario_nombre || '')
    }
    if (sortBy.value === 'area') {
      return (a.area_nombre || '').localeCompare(b.area_nombre || '')
    }
    return 0
  })
  
  return result
})

const hasActiveFilters = computed(() => {
  return Object.values(filters.value).some(value => 
    value !== '' && value !== null && value !== undefined
  ) || searchQuery.value.trim() !== ''
})

// ========================================== PAGINACIÓN ==========================================

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

const hasMorePages = computed(() => {
  return currentPage.value < totalPages.value - 2
})

// ========================================== ACCIONES DE UI ==========================================

const handleSearch = async () => {
  if (searchQuery.value.trim()) {
    try {
      isLoading.value = true
      const response = await mobiliarioService.searchMobiliario(searchQuery.value, filters.value)
      if (response && response.mobiliarios) {
        mobiliario.value = response.mobiliarios
      }
      calculateStats()
    } catch (err) {
      console.error('Error en búsqueda:', err)
      // Si falla la búsqueda específica, usa filtrado local
    } finally {
      isLoading.value = false
    }
  } else {
    loadMobiliario()
  }
  currentPage.value = 1
}

const toggleAdvancedFilters = () => {
  showAdvancedFilters.value = !showAdvancedFilters.value
}

const applyFilters = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  searchQuery.value = ''
  filters.value = {
    tipo_mobiliario_id: '',
    estado_id: '',
    area_id: '',
    fecha_desde: '',
    fecha_hasta: ''
  }
  currentPage.value = 1
  loadMobiliario()
}

const sortMobiliario = () => {
  currentPage.value = 1
}

// ========================================== FORMATOS Y ESTADOS ==========================================

const getStatusClass = (item) => {
  const classes = {
    1: 'status-available',    // Activo
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

// ========================================== NAVEGACIÓN ==========================================

const goToEdit = (id) => {
  router.push(`/admin/mobiliario/editar/${id}`)
}

const viewDetails = (id) => {
  // Puedes crear una vista de detalles si la necesitas
  console.log('Ver detalles del mobiliario:', id)
  // router.push(`/mobiliario/${id}`)
}

const goToReactivar = () => {
  // Filtrar para mostrar solo desactivados
  filters.value.estado_id = '4'
  currentPage.value = 1
  showToastMessage(
    'Filtro aplicado',
    'Mostrando solo mobiliario desactivado',
    'info',
    'ℹ️'
  )
}

// ========================================== ACCIONES CRUD ==========================================

const confirmDesactivate = (item) => {
  if (!canDesactivateMobiliario.value) {
    showToastMessage(
      'Permiso denegado',
      'No tienes permisos para desactivar mobiliario',
      'error',
      '🚫'
    )
    return
  }
  
  if (item.estado_id === 4) {
    showToastMessage(
      'Ya está desactivado',
      'Este mobiliario ya está desactivado',
      'warning',
      '⚠️'
    )
    return
  }
  
  itemToModify.value = item
  showDesactivateModal.value = true
}

const confirmReactivate = async (item) => {
  if (!canReactivateMobiliario.value) {
    showToastMessage(
      'Permiso denegado',
      'No tienes permisos para reactivar mobiliario',
      'error',
      '🚫'
    )
    return
  }
  
  if (!confirm(`¿Reactivar "${item.descripcion}"? Volverá al inventario activo.`)) {
    return
  }
  
  isProcessing.value = true
  try {
    await mobiliarioService.reactivateMobiliario(item.id)
    
    // Actualizar estado local
    const index = mobiliario.value.findIndex(m => m.id === item.id)
    if (index !== -1) {
      mobiliario.value[index].estado_id = 1
      mobiliario.value[index].estado_nombre = 'Activo'
    }
    
    calculateStats()
    showToastMessage(
      '¡Reactivado!',
      'El mobiliario ha sido reactivado exitosamente',
      'success',
      '✅'
    )
  } catch (err) {
    console.error('Error reactivando mobiliario:', err)
    showToastMessage(
      'Error',
      'No se pudo reactivar el mobiliario',
      'error',
      '❌'
    )
  } finally {
    isProcessing.value = false
  }
}

const confirmDelete = (item) => {
  if (!canDeleteMobiliario.value) {
    showToastMessage(
      'Permiso denegado',
      'No tienes permisos para eliminar mobiliario',
      'error',
      '🚫'
    )
    return
  }
  
  if (item.estado_id !== 4) {
    showToastMessage(
      'Acción no permitida',
      'Solo se puede eliminar mobiliario desactivado',
      'warning',
      '⚠️'
    )
    return
  }
  
  itemToDelete.value = item
  showDeleteModal.value = true
}

const desactivateItem = async () => {
  if (!itemToModify.value) return
  
  isProcessing.value = true
  try {
    await mobiliarioService.desactivateMobiliario(itemToModify.value.id)
    
    // Actualizar estado local
    const index = mobiliario.value.findIndex(m => m.id === itemToModify.value.id)
    if (index !== -1) {
      mobiliario.value[index].estado_id = 4
      mobiliario.value[index].estado_nombre = 'Desactivado'
    }
    
    calculateStats()
    showToastMessage(
      '¡Desactivado!',
      'El mobiliario ha sido desactivado exitosamente',
      'success',
      '✅'
    )
    
    closeModal()
  } catch (err) {
    console.error('Error desactivando mobiliario:', err)
    showToastMessage(
      'Error',
      'No se pudo desactivar el mobiliario',
      'error',
      '❌'
    )
  } finally {
    isProcessing.value = false
  }
}

const deleteItem = async () => {
  if (!itemToDelete.value) return
  
  isProcessing.value = true
  try {
    await mobiliarioService.deleteMobiliario(itemToDelete.value.id)
    
    // Eliminar del listado local
    mobiliario.value = mobiliario.value.filter(m => m.id !== itemToDelete.value.id)
    
    calculateStats()
    showToastMessage(
      '¡Eliminado!',
      'El mobiliario ha sido eliminado permanentemente',
      'success',
      '✅'
    )
    
    closeDeleteModal()
  } catch (err) {
    console.error('Error eliminando mobiliario:', err)
    showToastMessage(
      'Error',
      'No se pudo eliminar el mobiliario',
      'error',
      '❌'
    )
  } finally {
    isProcessing.value = false
  }
}

// ========================================== MODALES Y TOAST ==========================================

const closeModal = () => {
  if (!isProcessing.value) {
    showDesactivateModal.value = false
    itemToModify.value = null
  }
}

const closeDeleteModal = () => {
  if (!isProcessing.value) {
    showDeleteModal.value = false
    itemToDelete.value = null
  }
}

const showToastMessage = (title, message, type = 'success', icon = '✅') => {
  toastTitle.value = title
  toastMessage.value = message
  toastType.value = type
  toastIcon.value = icon
  showToast.value = true
  
  // Auto-ocultar después de 3 segundos
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// ========================================== PAGINACIÓN ==========================================

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

// ========================================== WATCHERS ==========================================

let searchTimeout
watch(searchQuery, (newQuery) => {
  clearTimeout(searchTimeout)
  if (newQuery.trim()) {
    searchTimeout = setTimeout(() => {
      currentPage.value = 1
    }, 500)
  }
})

watch(filters, () => {
  currentPage.value = 1
}, { deep: true })

// ========================================== CICLO DE VIDA ==========================================

onMounted(() => {
  loadMobiliario()
  
  // Debug para saber permisos actuales
  console.log('Permisos del usuario para mobiliario:', {
    crear: canCreateMobiliario.value,
    editar: canEditMobiliario.value,
    eliminar: canDeleteMobiliario.value,
    reactivar: canReactivateMobiliario.value,
    desactivar: canDesactivateMobiliario.value,
    ver: canViewDesactivados.value
  })
})
</script>

<style scoped>
/* Reutiliza los estilos de BookCatalog.vue */
/* Solo cambiar lo específico de mobiliario */

.mobiliario-management {
  padding: 1rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header específico para mobiliario */
.catalog-header {
  background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
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
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.btn-reactivate-mobiliario {
  background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

.btn-reactivate-mobiliario:hover {
  background: linear-gradient(135deg, #F57C00 0%, #EF6C00 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 152, 0, 0.3);
}

.badge-count {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #dc3545;
  color: white;
  font-size: 0.75rem;
  font-weight: bold;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 0.25rem;
}

/* Tarjetas de mobiliario */
.mobiliario-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.mobiliario-card {
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.mobiliario-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.mobiliario-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.mobiliario-status {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-available {
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

.mobiliario-id {
  font-family: monospace;
  font-size: 0.8rem;
  color: #666;
  background: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.mobiliario-icon {
  height: 150px;
  background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-icon {
  font-size: 4rem;
  color: white;
  opacity: 0.8;
}

.item-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.9);
  color: #2E7D32;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.7rem;
  font-weight: bold;
}

.mobiliario-info {
  padding: 1.5rem;
  flex: 1;
}

.item-description {
  font-size: 1.1rem;
  margin: 0 0 0.75rem 0;
  color: #333;
  line-height: 1.3;
}

.item-details {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.85rem;
}

.item-details p {
  margin: 0.25rem 0;
  color: #555;
}

.mobiliario-actions {
  padding: 1rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Tabla de mobiliario */
.mobiliario-table {
  width: 100%;
  background: white;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
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
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
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

/* Estados vacíos */
.empty-card {
  grid-column: 1 / -1;
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.5;
}

.empty-row {
  text-align: center;
  padding: 3rem !important;
}

/* Toast personalizados */
.toast.success {
  border-left-color: #28a745;
}

.toast.error {
  border-left-color: #dc3545;
}

.toast.warning {
  border-left-color: #ffc107;
}

.toast.info {
  border-left-color: #17a2b8;
}

.danger-message {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  padding: 0.75rem;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 6px;
  color: #721c24;
}

.danger-icon {
  font-size: 1.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .catalog-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .btn-create-mobiliario .btn-text,
  .btn-reactivate-mobiliario .btn-text {
    display: none;
  }
  
  .btn-create-mobiliario,
  .btn-reactivate-mobiliario {
    width: 100%;
    justify-content: center;
    padding: 0.75rem;
  }
  
  .mobiliario-grid {
    grid-template-columns: 1fr;
  }
  
  .mobiliario-actions {
    flex-direction: column;
  }
  
  .mobiliario-actions .btn {
    width: 100%;
    justify-content: center;
  }
  
  .action-buttons {
    justify-content: center;
  }
}
</style>