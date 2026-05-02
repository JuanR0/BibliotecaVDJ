<template>
  <div class="mobiliario-management">

    <!-- ══════════════════════════════════════
         HEADER
    ══════════════════════════════════════ -->
    <header class="page-header">
      <div class="header-inner">
        <div class="header-texto">
          <p class="header-sup">Panel de administración</p>
          <h1 class="header-titulo">Gestión de Mobiliario</h1>
          <p class="header-sub">Inventario de mobiliario de la biblioteca</p>
        </div>

        <div class="header-acciones">
          <button
            class="btn-toggle-inactivos"
            :class="{ 'btn-toggle-on': showInactiveMobiliario }"
            @click="toggleShowInactive"
          >
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
            </svg>
            {{ showInactiveMobiliario ? 'Ocultar desactivados' : 'Mostrar desactivados' }}
          </button>

          <router-link v-if="canCreateMobiliario" to="/admin/mobiliario/crear" class="btn-crear">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
            </svg>
            Agregar Mobiliario
          </router-link>
        </div>
      </div>

      <!-- Stats en header -->
      <div class="header-stats">
        <div class="hstat">
          <span class="hstat-num">{{ stats.total || 0 }}</span>
          <span class="hstat-lbl">Total</span>
        </div>
        <div class="hstat">
          <span class="hstat-num">{{ stats.activos || 0 }}</span>
          <span class="hstat-lbl">Activos</span>
        </div>
        <div class="hstat hstat-warn" v-if="stats.enReparacion > 0">
          <span class="hstat-num">{{ stats.enReparacion || 0 }}</span>
          <span class="hstat-lbl">En reparación</span>
        </div>
        <div class="hstat hstat-muted" v-if="stats.desactivados > 0">
          <span class="hstat-num">{{ stats.desactivados || 0 }}</span>
          <span class="hstat-lbl">Desactivados</span>
        </div>
      </div>
    </header>

    <!-- ══════════════════════════════════════
         TOOLBAR
    ══════════════════════════════════════ -->
    <div class="toolbar">
      <div class="search-wrap">
        <svg class="search-ico" width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar por descripción, área, tipo..."
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">×</button>
      </div>

      <select v-model="filters.tipo_mobiliario_id" class="filter-select">
        <option value="">Todos los tipos</option>
        <option value="1">Sillas</option>
        <option value="2">Mesas</option>
        <option value="3">Escritorios</option>
        <option value="4">Sillones</option>
      </select>

      <select v-model="filters.estado_id" class="filter-select">
        <option value="">Todos los estados</option>
        <option value="1">Activo</option>
        <option value="2">En uso</option>
        <option value="3">En reparación</option>
        <option v-if="canViewDesactivados" value="4">Desactivado</option>
      </select>

      <select v-model="filters.area_id" class="filter-select" v-if="areas.length > 0">
        <option value="">Todas las áreas</option>
        <option v-for="area in areas" :key="area.id" :value="area.id">{{ area.nombre }}</option>
      </select>

      <select v-model="sortBy" class="filter-select">
        <option value="descripcion">Descripción A-Z</option>
        <option value="fecha_ingreso">Más recientes</option>
        <option value="tipo">Tipo</option>
        <option value="area">Área</option>
      </select>

      <button class="btn-reset" @click="resetFilters" v-if="hasActiveFilters">
        Limpiar filtros
      </button>
    </div>

    <!-- ══════════════════════════════════════
         TABLA
    ══════════════════════════════════════ -->
    <div class="tabla-section">

      <div v-if="isLoading" class="estado-loading">
        <div class="spinner"></div>
        <p>Cargando inventario...</p>
      </div>

      <div v-else-if="error" class="estado-error">
        <p>{{ error }}</p>
        <button class="btn-primary" @click="loadMobiliario">Reintentar</button>
      </div>

      <div v-else class="tabla-wrap">
        <table class="tabla">
          <thead>
            <tr>
              <th style="width:60px">ID</th>
              <th>Descripción</th>
              <th style="width:130px">Tipo</th>
              <th style="width:160px">Área</th>
              <th style="width:130px">Estado</th>
              <th style="width:130px">Ingreso</th>
              <th style="width:160px">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in paginatedItems"
              :key="item.id"
              :class="{ 'fila-inactiva': item.estado_id === 4 }"
            >
              <td class="td-id">#{{ item.id }}</td>

              <td>
                <div class="td-desc">{{ item.descripcion }}</div>
                <div class="td-meta">Creado por: {{ item.usuario_creador_nombre }}</div>
              </td>

              <td>
                <span class="tipo-badge">{{ item.tipo_mobiliario_nombre }}</span>
              </td>

              <td class="td-area">{{ item.area_nombre || 'No asignada' }}</td>

              <td>
                <span class="estado-badge" :class="getStatusClass(item)">
                  {{ getStatusText(item) }}
                </span>
              </td>

              <td>
                <div class="td-fecha">{{ formatFecha(item.fecha_ingreso) }}</div>
                <div v-if="item.fecha_ultimo_cambio_estado" class="td-meta">
                  Cambio: {{ formatFecha(item.fecha_ultimo_cambio_estado) }}
                </div>
              </td>

              <td>
                <div class="acciones">
                  <!-- Editar — tbl-btn viene de buttons.css -->
                  <button v-if="canEditMobiliario" class="tbl-btn tbl-blue" title="Editar mobiliario" :disabled="isProcessing" @click="openEditModal(item)">
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                    Editar
                  </button>

                  <!-- Desactivar -->
                  <button v-if="canDesactivateMobiliario && item.estado_id !== 4" class="tbl-btn tbl-warning" style="padding:.3rem .5rem" title="Desactivar mobiliario" :disabled="isProcessing" @click="confirmAction(item, 'desactivate')">
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                  </button>

                  <!-- Reactivar -->
                  <button v-if="canReactivateMobiliario && item.estado_id === 4" class="tbl-btn tbl-green" style="padding:.3rem .5rem" title="Reactivar mobiliario" :disabled="isProcessing" @click="confirmAction(item, 'reactivate')">
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                  </button>

                  <!-- Eliminar -->
                  <button v-if="canDeleteMobiliario && item.estado_id === 4" class="tbl-btn tbl-danger" style="padding:.3rem .5rem" title="Eliminar permanentemente" :disabled="isProcessing" @click="confirmAction(item, 'delete')">
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Vacío -->
        <div v-if="filteredItems.length === 0" class="estado-vacio">
          <svg width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" class="vacio-ico">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
          </svg>
          <p class="vacio-titulo">No se encontró mobiliario</p>
          <p class="vacio-desc">
            {{ searchQuery || hasActiveFilters ? 'Intenta con otros términos o ajusta los filtros' : 'No hay mobiliario registrado en el sistema' }}
          </p>
          <button class="btn-outline" @click="resetFilters">Limpiar filtros</button>
        </div>
      </div>

      <!-- Paginación -->
      <div v-if="!isLoading && filteredItems.length > 0" class="paginacion">
        <span class="pag-info">{{ startItem }}–{{ endItem }} de {{ filteredItems.length }}</span>
        <div class="pag-controles">
          <button class="pag-btn" :disabled="currentPage === 1" @click="prevPage">← Anterior</button>
          <span
            v-for="page in visiblePages" :key="page"
            class="pag-num" :class="{ 'pag-num-active': page === currentPage }"
            @click="goToPage(page)"
          >{{ page }}</span>
          <button class="pag-btn" :disabled="currentPage === totalPages" @click="nextPage">Siguiente →</button>
        </div>
        <div class="pag-size">
          <label>Mostrar</label>
          <select v-model="itemsPerPage" @change="resetPagination" class="pag-select">
            <option :value="10">10</option>
            <option :value="25">25</option>
            <option :value="50">50</option>
          </select>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════
         MODAL: CONFIRMAR ACCIÓN
    ══════════════════════════════════════ -->
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="closeConfirmModal">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>{{ confirmModalTitle }}</h3>
          <button class="modal-close" @click="closeConfirmModal" :disabled="isProcessing">×</button>
        </div>

        <div class="modal-body">
          <p class="confirm-msg">{{ confirmModalMessage }}</p>
          <div v-if="itemToAction" class="confirm-item">
            <strong>{{ itemToAction.descripcion }}</strong>
            <span>{{ itemToAction.tipo_mobiliario_nombre }}</span>
            <span>{{ itemToAction.area_nombre || 'Sin área' }}</span>
          </div>
        </div>

        <div class="modal-footer">
          <!-- btn-modal-cancel, btn-modal-confirm, btn-modal-delete vienen de buttons.css -->
          <button class="btn-modal-cancel" @click="closeConfirmModal" :disabled="isProcessing">
            Cancelar
          </button>
          <button
            :class="confirmModalBtnClass"
            @click="executeAction"
            :disabled="isProcessing"
          >
            <span v-if="isProcessing" class="spinner-mini"></span>
            {{ isProcessing ? 'Procesando...' : confirmModalActionText }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════
         TOAST
    ══════════════════════════════════════ -->
    <transition name="toast-in">
      <div v-if="showSuccessToast" class="toast toast-success">
        <span>{{ successMessage }}</span>
        <p v-if="successDetails" class="toast-desc">{{ successDetails }}</p>
        <button class="toast-close" @click="showSuccessToast = false">×</button>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { mobiliarioService } from '@/services/mobiliario'
import { usePermissions } from '@/composables/usePermissions'

// ── Import centralizado de botones ─────────────────────────────────────────
import '@/styles/buttons.css'

const router = useRouter()
const { hasPermission } = usePermissions()

// ── State ──────────────────────────────────────────────────────────────────
const mobiliario          = ref([])
const isLoading           = ref(false)
const error               = ref(null)
const currentPage         = ref(1)
const itemsPerPage        = ref(10)
const showInactiveMobiliario = ref(false)
const isProcessing        = ref(false)

// Búsqueda y filtros
const searchQuery = ref('')
const filters     = ref({ tipo_mobiliario_id: '', estado_id: '', area_id: '' })
const sortBy      = ref('descripcion')

// Data auxiliar
const tiposMobiliario   = ref([])
const estadosMobiliario = ref([])
const areas             = ref([])

// Modales
const showEditModal    = ref(false)
const showConfirmModal = ref(false)
const itemToAction     = ref(null)
const actionType       = ref('')

// Toast
const showSuccessToast = ref(false)
const successMessage   = ref('')
const successDetails   = ref('')

// ── Permisos ───────────────────────────────────────────────────────────────
const canCreateMobiliario    = computed(() => hasPermission('canCreateFurniture'))
const canEditMobiliario      = computed(() => hasPermission('canEditFurniture'))
const canDeleteMobiliario    = computed(() => hasPermission('canDeleteFurniture'))
const canReactivateMobiliario = computed(() => hasPermission('canReactivatFurniture'))
const canDesactivateMobiliario = computed(() => hasPermission('canDesactivateFurniture'))
const canViewDesactivados    = computed(() => hasPermission('canViewMobiliario'))

// ── Computed ───────────────────────────────────────────────────────────────
const filteredItems = computed(() => {
  let result = [...mobiliario.value]

  if (!showInactiveMobiliario.value) result = result.filter(i => i.estado_id !== 4)
  if (filters.value.tipo_mobiliario_id) result = result.filter(i => i.tipo_mobiliario_id === parseInt(filters.value.tipo_mobiliario_id))
  if (filters.value.estado_id)         result = result.filter(i => i.estado_id === parseInt(filters.value.estado_id))
  if (filters.value.area_id)           result = result.filter(i => i.area_id === parseInt(filters.value.area_id))

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    result = result.filter(i =>
      i.descripcion?.toLowerCase().includes(q) ||
      i.area_nombre?.toLowerCase().includes(q) ||
      i.tipo_mobiliario_nombre?.toLowerCase().includes(q)
    )
  }

  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'descripcion':  return (a.descripcion || '').localeCompare(b.descripcion || '')
      case 'fecha_ingreso':{
        const da = a.fecha_ingreso ? new Date(a.fecha_ingreso) : new Date(0)
        const db = b.fecha_ingreso ? new Date(b.fecha_ingreso) : new Date(0)
        return db - da
      }
      case 'tipo': return (a.tipo_mobiliario_nombre || '').localeCompare(b.tipo_mobiliario_nombre || '')
      case 'area': return (a.area_nombre || '').localeCompare(b.area_nombre || '')
      default:     return 0
    }
  })

  return result
})

const stats = computed(() => ({
  total:        mobiliario.value.length,
  activos:      mobiliario.value.filter(i => i.estado_id === 1).length,
  desactivados: mobiliario.value.filter(i => i.estado_id === 4).length,
  enReparacion: mobiliario.value.filter(i => i.estado_id === 3).length
}))

const totalPages    = computed(() => Math.ceil(filteredItems.value.length / itemsPerPage.value) || 1)
const paginatedItems = computed(() => {
  const s = (currentPage.value - 1) * itemsPerPage.value
  return filteredItems.value.slice(s, s + itemsPerPage.value)
})
const startItem = computed(() => (currentPage.value - 1) * itemsPerPage.value + 1)
const endItem   = computed(() => Math.min(currentPage.value * itemsPerPage.value, filteredItems.value.length))
const visiblePages = computed(() => {
  const max = 5, total = totalPages.value
  if (total <= max) return Array.from({ length: total }, (_, i) => i + 1)
  let start = Math.max(1, currentPage.value - 2)
  const end = Math.min(total, start + max - 1)
  if (end - start + 1 < max) start = end - max + 1
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})
const hasActiveFilters = computed(() =>
  Object.values(filters.value).some(v => v !== '' && v !== null) || searchQuery.value.trim() !== ''
)

// Computed del modal de confirmación
const confirmModalTitle = computed(() => {
  return { desactivate: 'Desactivar Mobiliario', reactivate: 'Reactivar Mobiliario', delete: 'Eliminar Mobiliario' }[actionType.value] || 'Confirmar Acción'
})
const confirmModalMessage = computed(() => {
  if (!itemToAction.value) return ''
  const msgs = {
    desactivate: `¿Desactivar "${itemToAction.value.descripcion}"? Será marcado como desactivado.`,
    reactivate:  `¿Reactivar "${itemToAction.value.descripcion}"? Volverá al inventario activo.`,
    delete:      `¿Eliminar permanentemente "${itemToAction.value.descripcion}"? Esta acción NO se puede deshacer.`
  }
  return msgs[actionType.value] || ''
})
const confirmModalActionText = computed(() => {
  return { desactivate: 'Sí, desactivar', reactivate: 'Sí, reactivar', delete: 'Sí, eliminar permanentemente' }[actionType.value] || 'Confirmar'
})
const confirmModalBtnClass = computed(() => {
  return { desactivate: 'btn-modal-cancel', reactivate: 'btn-modal-confirm', delete: 'btn-modal-delete' }[actionType.value] || 'btn-modal-confirm'
})

// ── Carga ──────────────────────────────────────────────────────────────────
const loadMobiliario = async () => {
  isLoading.value = true; error.value = null
  try {
    const response = await mobiliarioService.getMobiliarios()
    mobiliario.value = response?.mobiliarios ?? (Array.isArray(response) ? response : [])
    await loadCatalogos()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error cargando el inventario'
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
    tiposMobiliario.value   = tipos
    estadosMobiliario.value = estados
    areas.value             = areasData
  } catch (err) {
    console.error('Error cargando catálogos:', err)
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const getStatusClass = (item) => ({
  1: 'estado-activo', 2: 'estado-uso', 3: 'estado-reparacion', 4: 'estado-inactivo'
})[item.estado_id] || ''

const getStatusText = (item) => ({
  1: 'Activo', 2: 'En uso', 3: 'En reparación', 4: 'Desactivado'
})[item.estado_id] || item.estado_nombre || 'Desconocido'

const formatFecha = (fecha) => {
  if (!fecha) return 'N/A'
  try { return new Date(fecha).toLocaleDateString('es-MX', { year: 'numeric', month: 'short', day: 'numeric' }) }
  catch { return 'Fecha inválida' }
}

// ── Acciones ───────────────────────────────────────────────────────────────
const handleSearch       = () => { currentPage.value = 1 }
const resetFilters       = () => { searchQuery.value = ''; filters.value = { tipo_mobiliario_id: '', estado_id: '', area_id: '' }; currentPage.value = 1 }
const toggleShowInactive = () => { showInactiveMobiliario.value = !showInactiveMobiliario.value; currentPage.value = 1 }

const openEditModal = (item) => { router.push(`/admin/mobiliario/editar/${item.id}`) }

const confirmAction = (item, type) => {
  const perms = { desactivate: canDesactivateMobiliario, reactivate: canReactivateMobiliario, delete: canDeleteMobiliario }
  if (!perms[type]?.value) { showToast('Sin permisos para esta acción', ''); return }
  itemToAction.value = item
  actionType.value   = type
  showConfirmModal.value = true
}

const closeConfirmModal = () => {
  if (!isProcessing.value) { showConfirmModal.value = false; itemToAction.value = null; actionType.value = '' }
}

const executeAction = async () => {
  if (!itemToAction.value || isProcessing.value) return
  isProcessing.value = true
  try {
    switch (actionType.value) {
      case 'desactivate':
        await mobiliarioService.desactivateMobiliario(itemToAction.value.id)
        itemToAction.value.estado_id = 4; itemToAction.value.estado_nombre = 'Desactivado'
        showToast('Mobiliario desactivado', `"${itemToAction.value.descripcion}" ha sido desactivado`)
        break
      case 'reactivate':
        await mobiliarioService.reactivateMobiliario(itemToAction.value.id)
        itemToAction.value.estado_id = 1; itemToAction.value.estado_nombre = 'Activo'
        showToast('Mobiliario reactivado', `"${itemToAction.value.descripcion}" ha sido reactivado`)
        break
      case 'delete':
        await mobiliarioService.deleteMobiliario(itemToAction.value.id)
        mobiliario.value = mobiliario.value.filter(m => m.id !== itemToAction.value.id)
        showToast('Mobiliario eliminado', `"${itemToAction.value.descripcion}" ha sido eliminado permanentemente`)
        break
    }
    closeConfirmModal()
  } catch (err) {
    showToast('Error al ejecutar la acción', err.response?.data?.detail || err.message)
  } finally {
    isProcessing.value = false
  }
}

const showToast = (title, details = '') => {
  successMessage.value   = title
  successDetails.value   = details
  showSuccessToast.value = true
  setTimeout(() => { showSuccessToast.value = false }, 3000)
}

// ── Paginación ─────────────────────────────────────────────────────────────
const prevPage      = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage      = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const goToPage      = (p) => { if (p >= 1 && p <= totalPages.value) currentPage.value = p }
const resetPagination = () => { currentPage.value = 1 }

watch([searchQuery, filters, sortBy, showInactiveMobiliario], () => { currentPage.value = 1 })
onMounted(loadMobiliario)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

/*
 * Botones centralizados en src/styles/buttons.css
 * Clases usadas: .btn-primary, .btn-outline, .btn-modal-cancel,
 * .btn-modal-confirm, .btn-modal-delete, .tbl-btn, .tbl-green,
 * .tbl-gold, .tbl-red, .spinner-mini
 */

:root {
  --green-dark:   #1a4731;
  --green-mid:    #2d6a4f;
  --green-light:  #52b788;
  --green-pale:   #d8f3dc;
  --gold-mid:     #c9900c;
  --gold-light:   #f4c542;
  --gold-pale:    #fef9e7;
  --cream:        #f5f0e8;
  --cream-border: #d4e8da;
  --card-bg:      #fffef9;
  --shadow-sm:    0 2px 12px rgba(26,47,26,.08);
}

.mobiliario-management {
  font-family: 'DM Sans', sans-serif; min-height: 100vh;
  background:
    radial-gradient(ellipse 70% 40% at 5% 0%, rgba(82,183,136,.08) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 90% 100%, rgba(201,144,12,.07) 0%, transparent 50%),
    var(--cream);
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.page-header { background: linear-gradient(135deg, #1a4731 0%, #2d6a4f 60%, #3a7d5e 100%); padding: 1.75rem 2rem 1.25rem; position: relative; overflow: hidden; }
.page-header::before { content: ''; position: absolute; inset: 0; pointer-events: none; background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E"); }
.header-inner  { display: flex; justify-content: space-between; align-items: flex-start; gap: 1.5rem; flex-wrap: wrap; position: relative; }
.header-sup    { font-size: .72rem; font-weight: 600; color: rgba(255,255,255,.5); text-transform: uppercase; letter-spacing: .1em; margin-bottom: .2rem; }
.header-titulo { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: #fff; margin-bottom: .3rem; }
.header-sub    { font-size: .8rem; color: rgba(255,255,255,.65); margin: 0; }
.header-acciones { display: flex; gap: .75rem; align-items: center; flex-shrink: 0; }

.btn-toggle-inactivos {
  display: flex; align-items: center; gap: .4rem; padding: .5rem 1rem;
  background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.15);
  border-radius: 8px; color: rgba(255,255,255,.75);
  font-family: 'DM Sans', sans-serif; font-size: .8rem; font-weight: 500;
  cursor: pointer; transition: all .2s;
}
.btn-toggle-inactivos:hover, .btn-toggle-on { background: rgba(255,255,255,.18); color: #fff; }

.btn-crear {
  display: inline-flex; align-items: center; gap: .4rem; padding: .5rem 1.1rem;
  background: linear-gradient(135deg, var(--gold-light), var(--gold-mid));
  border: none; border-radius: 8px; color: var(--green-dark);
  font-family: 'DM Sans', sans-serif; font-size: .82rem; font-weight: 700;
  cursor: pointer; text-decoration: none;
  box-shadow: 0 4px 14px rgba(244,197,66,.3); transition: all .2s;
}
.btn-crear:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(244,197,66,.4); }

.header-stats { display: flex; gap: .75rem; margin-top: 1.25rem; position: relative; flex-wrap: wrap; }
.hstat { display: flex; flex-direction: column; align-items: center; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.1); border-radius: 9px; padding: .45rem .875rem; min-width: 80px; }
.hstat-muted { opacity: .65; }
.hstat-warn  { background: rgba(244,197,66,.15); border-color: rgba(244,197,66,.2); }
.hstat-num { font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: #fff; line-height: 1; }
.hstat-warn .hstat-num { color: var(--gold-light); }
.hstat-lbl { font-size: .64rem; color: rgba(255,255,255,.55); text-transform: uppercase; letter-spacing: .07em; margin-top: 2px; white-space: nowrap; }

/* ── Toolbar ─────────────────────────────────────────────────────────────── */
.toolbar { display: flex; align-items: center; gap: .75rem; padding: 1rem 1.5rem; background: var(--card-bg); border-bottom: 1.5px solid var(--cream-border); flex-wrap: wrap; }
.search-wrap { display: flex; align-items: center; gap: .5rem; flex: 1; min-width: 220px; padding: .5rem .75rem; background: var(--cream); border: 1.5px solid var(--cream-border); border-radius: 9px; color: #9ab5a0; }
.search-ico { flex-shrink: 0; }
.search-input { flex: 1; border: none; background: none; font-family: 'DM Sans', sans-serif; font-size: .875rem; color: #1a2e1a; outline: none; }
.search-input::placeholder { color: #9ab5a0; }
.search-clear { background: none; border: none; color: #9ab5a0; cursor: pointer; font-size: 1rem; padding: 0; line-height: 1; }
.search-clear:hover { color: var(--green-dark); }
.filter-select { padding: .5rem .75rem; background: var(--cream); border: 1.5px solid var(--cream-border); border-radius: 9px; font-family: 'DM Sans', sans-serif; font-size: .82rem; color: #3d5a3d; outline: none; cursor: pointer; }
.filter-select:focus { border-color: var(--green-light); }
.btn-reset { padding: .5rem .875rem; background: none; border: 1.5px solid var(--cream-border); border-radius: 9px; font-family: 'DM Sans', sans-serif; font-size: .8rem; color: #5a7a5a; cursor: pointer; white-space: nowrap; transition: all .18s; }
.btn-reset:hover { background: #111; color: #fff; border-color: #111; }

/* ── Tabla ───────────────────────────────────────────────────────────────── */
.tabla-section { background: var(--card-bg); border: 1.5px solid var(--cream-border); border-radius: 0 0 16px 16px; overflow: hidden; box-shadow: var(--shadow-sm); margin: 0 1.5rem 1.5rem; }
.tabla-wrap { overflow-x: auto; }
.tabla { width: 100%; border-collapse: collapse; font-size: .82rem; }
.tabla thead { background: linear-gradient(135deg, #1a4731, #2d6a4f); }
.tabla thead th { padding: .75rem 1rem; text-align: left; color: rgba(255,255,255,.88); font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; }
.tabla tbody tr { border-bottom: 1px solid #f1f5f0; transition: background .15s; }
.tabla tbody tr:last-child { border-bottom: none; }
.tabla tbody tr:hover { background: #fafef8; }
.tabla tbody tr.fila-inactiva { background: #fff8f8; opacity: .8; }
.tabla tbody tr.fila-inactiva:hover { background: #fff0f0; }
.tabla td { padding: .75rem 1rem; vertical-align: middle; color: #334155; }

.td-id   { font-family: monospace; color: #9ab5a0; font-size: .78rem; }
.td-desc { font-weight: 600; color: #1a2e1a; }
.td-meta { font-size: .72rem; color: #9ab5a0; margin-top: 2px; }
.td-area { font-size: .82rem; color: #475569; }
.td-fecha{ font-size: .78rem; color: #64748b; }

.tipo-badge { display: inline-block; padding: .2rem .6rem; border-radius: 20px; font-size: .7rem; font-weight: 700; background: #e3f2fd; color: #1565c0; white-space: nowrap; }

.estado-badge { display: inline-block; padding: .2rem .55rem; border-radius: 20px; font-size: .7rem; font-weight: 700; }
.estado-activo    { background: var(--green-pale); color: var(--green-dark); border: 1px solid #b8ddc8; }
.estado-uso       { background: var(--gold-pale); color: var(--gold-mid); border: 1px solid #fde68a; }
.estado-reparacion{ background: #dbeafe; color: #1e3a5f; border: 1px solid #bfdbfe; }
.estado-inactivo  { background: #fff0f0; color: #b91c1c; border: 1px solid #fca5a5; }

.acciones { display: flex; align-items: center; gap: .35rem; flex-wrap: wrap; }

/* ── Estados ─────────────────────────────────────────────────────────────── */
.estado-loading, .estado-error, .estado-vacio { display: flex; flex-direction: column; align-items: center; padding: 3.5rem 2rem; gap: .75rem; text-align: center; }
.spinner { width: 36px; height: 36px; border: 3px solid var(--green-pale); border-top-color: var(--green-mid); border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.estado-loading p { color: #5a7a5a; font-size: .875rem; }
.estado-error p   { color: #d62828; font-size: .875rem; }
.vacio-ico    { color: #b8ddc8; }
.vacio-titulo { font-weight: 700; color: var(--green-dark); margin: 0; }
.vacio-desc   { font-size: .82rem; color: #5a7a5a; margin: 0; }

/* ── Paginación ──────────────────────────────────────────────────────────── */
.paginacion { display: flex; justify-content: space-between; align-items: center; padding: .875rem 1.25rem; border-top: 1.5px solid #eef5f0; font-size: .8rem; color: #5a7a5a; flex-wrap: wrap; gap: .75rem; }
.pag-controles { display: flex; align-items: center; gap: .5rem; }
.pag-btn { padding: .35rem .75rem; background: #fff; border: 1.5px solid var(--cream-border); border-radius: 7px; font-size: .78rem; font-weight: 600; color: var(--green-mid); cursor: pointer; font-family: 'DM Sans', sans-serif; transition: all .15s; }
.pag-btn:hover:not(:disabled) { background: #111; color: #fff; border-color: #111; }
.pag-btn:disabled { opacity: .4; cursor: not-allowed; }
.pag-num { padding: .3rem .65rem; border-radius: 7px; cursor: pointer; font-size: .8rem; font-weight: 500; color: var(--green-mid); transition: all .15s; }
.pag-num:hover      { background: #111; color: #fff; }
.pag-num-active     { background: var(--green-mid); color: #fff; }
.pag-size { display: flex; align-items: center; gap: .5rem; }
.pag-select { padding: .3rem .55rem; border: 1.5px solid var(--cream-border); border-radius: 7px; font-size: .8rem; color: var(--green-dark); background: #fff; cursor: pointer; }

/* ── Modal ───────────────────────────────────────────────────────────────── */
.modal-overlay { position: fixed; inset: 0; background: rgba(26,47,26,.5); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 2000; }
.modal { background: var(--card-bg); border-radius: 16px; width: 90%; max-width: 540px; border: 1.5px solid var(--cream-border); box-shadow: 0 24px 64px rgba(0,0,0,.2); animation: modalIn .25s cubic-bezier(.22,1,.36,1); }
.modal-sm { max-width: 420px; }
@keyframes modalIn { from { opacity: 0; transform: translateY(-14px) scale(.97); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.1rem 1.375rem .875rem; border-bottom: 1.5px solid #eef5f0; }
.modal-header h3 { font-family: 'Playfair Display', serif; font-size: 1.05rem; font-weight: 700; color: var(--green-dark); margin: 0; }
.modal-close { background: none; border: none; font-size: 1.3rem; color: #9ab5a0; cursor: pointer; padding: 0; line-height: 1; transition: color .15s; }
.modal-close:hover { color: var(--green-dark); }
.modal-body { padding: 1.25rem 1.375rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: .625rem; padding: .875rem 1.375rem; border-top: 1.5px solid #eef5f0; }

.confirm-msg  { font-size: .875rem; color: #334155; margin-bottom: .75rem; }
.confirm-item { display: flex; flex-direction: column; gap: 2px; padding: .75rem; background: var(--cream); border-radius: 9px; border-left: 3px solid var(--green-light); font-size: .82rem; }
.confirm-item strong { color: var(--green-dark); }
.confirm-item span   { color: #9ab5a0; }

/* ── Toast ───────────────────────────────────────────────────────────────── */
.toast { position: fixed; bottom: 2rem; right: 2rem; display: flex; align-items: flex-start; gap: .75rem; padding: .75rem 1.1rem; border-radius: 10px; font-size: .82rem; font-weight: 600; color: #fff; z-index: 9999; box-shadow: 0 4px 20px rgba(0,0,0,.15); }
.toast-success { background: #16a34a; }
.toast-desc    { margin: .2rem 0 0; opacity: .9; font-size: .78rem; font-weight: 400; }
.toast-close   { background: none; border: none; color: rgba(255,255,255,.75); font-size: 1.1rem; cursor: pointer; padding: 0; line-height: 1; margin-left: auto; }
.toast-close:hover { color: #fff; }
.toast-in-enter-active, .toast-in-leave-active { transition: all .3s ease; }
.toast-in-enter-from, .toast-in-leave-to { opacity: 0; transform: translateX(16px); }
</style>