<template>
  <div class="areas-management">

    <!-- ══════════════════════════════════════
         HEADER
    ══════════════════════════════════════ -->
    <header class="page-header">
      <div class="header-inner">
        <div class="header-texto">
          <p class="header-sup">Panel de administración</p>
          <h1 class="header-titulo">Gestión de Áreas</h1>
          <p class="header-sub">Administra las áreas y cubículos de la biblioteca</p>
        </div>

        <div class="header-acciones">
          <button class="btn-refresh" @click="forceReload" title="Recargar datos">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </button>

          <button v-if="puedeCrearAreas" class="btn-crear" @click="openCreateModal">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
            </svg>
            Nueva Área
          </button>
        </div>
      </div>

      <!-- Stats en header -->
      <div class="header-stats">
        <div class="hstat">
          <span class="hstat-num">{{ areas.length }}</span>
          <span class="hstat-lbl">Total</span>
        </div>
        <div class="hstat">
          <span class="hstat-num">{{ areasPrestables.length }}</span>
          <span class="hstat-lbl">Prestables</span>
        </div>
        <div class="hstat">
          <span class="hstat-num">{{ areasInternas.length }}</span>
          <span class="hstat-lbl">Internas</span>
        </div>
      </div>
    </header>

    <!-- ══════════════════════════════════════
         TABS + BÚSQUEDA
    ══════════════════════════════════════ -->
    <div class="toolbar">
      <!-- Tabs -->
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ 'tab-active': activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
          <span class="tab-count" :class="{ 'tab-count-active': activeTab === tab.id }">
            {{ getTabCount(tab.id) }}
          </span>
        </button>
      </div>

      <!-- Búsqueda -->
      <div class="search-wrap">
        <svg class="search-ico" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input v-model="search" type="text" placeholder="Buscar área..." class="search-input"/>
        <button v-if="search" class="search-clear" @click="search = ''">×</button>
      </div>
    </div>

    <!-- ══════════════════════════════════════
         CONTENIDO
    ══════════════════════════════════════ -->
    <div class="content-section">

      <!-- Loading -->
      <div v-if="isLoading" class="estado-loading">
        <div class="spinner"></div>
        <p>Cargando áreas...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="estado-error">
        <p>{{ error }}</p>
        <button class="btn-primary" @click="loadData">Reintentar</button>
      </div>

      <template v-else>

        <!-- ── TAB PRESTABLES: cards ───────────────────────────── -->
        <div v-if="activeTab === 'prestables'">
          <div v-if="areasPrestables.length === 0" class="estado-vacio">
            <svg width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" class="vacio-ico">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
            <p class="vacio-titulo">Sin áreas prestables</p>
            <p class="vacio-desc">{{ search ? 'Sin resultados para esa búsqueda' : 'No hay áreas prestables registradas' }}</p>
            <button v-if="puedeCrearAreas && !search" class="btn-primary" @click="openCreateModal">Crear primera área</button>
          </div>

          <div v-else class="cards-grid">
            <div
              v-for="area in areasPrestables"
              :key="area.id"
              class="area-card"
              :class="{
                'card-disponible':  area.estado_id === 1,
                'card-ocupada':     area.estado_id === 2,
                'card-reparacion':  area.estado_id === 3,
                'card-inactiva':    area.estado_id === 5
              }"
            >
              <!-- Indicador lateral -->
              <div class="card-indicator"></div>

              <div class="card-body">
                <div class="card-top">
                  <h3 class="card-nombre">{{ area.nombre }}</h3>
                  <span class="card-estado-badge" :class="getEstadoClass(area)">
                    {{ area.estado_nombre || 'Desconocido' }}
                  </span>
                </div>

                <div class="card-info">
                  <div class="card-info-row">
                    <span class="ci-label">Capacidad</span>
                    <span class="ci-valor">{{ area.capacidad || 'N/A' }}</span>
                  </div>
                  <div class="card-info-row">
                    <span class="ci-label">Creado por</span>
                    <span class="ci-valor">{{ area.usuario_registro_nombre || '—' }}</span>
                  </div>
                </div>

                <!-- Acciones — clases de buttons.css -->
                <div class="card-acciones">
                  <button class="tbl-btn tbl-green" title="Editar" @click="handleEdit(area)">
                    <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                    Editar
                  </button>

                  <button v-if="area.estado_id === 2" class="tbl-btn tbl-green" title="Devolver área" @click="devolverArea(area)">
                    <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/>
                    </svg>
                    Devolver
                  </button>

                  <button v-if="area.estado_id !== 4 && area.estado_id !== 5" class="tbl-btn tbl-gold" style="padding:.3rem .5rem" title="Desactivar" @click="handleDesactivate(area)">
                    <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                  </button>

                  <button v-if="area.estado_id === 5" class="tbl-btn tbl-green" style="padding:.3rem .5rem" title="Reactivar" @click="handleReactivate(area)">
                    <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ── TAB INTERNAS / TODAS: tabla ────────────────────── -->
        <div v-else class="tabla-wrap">
          <table class="tabla">
            <thead>
              <tr>
                <th>Nombre</th>
                <th style="width:110px">Tipo</th>
                <th style="width:100px">Capacidad</th>
                <th style="width:140px">Estado</th>
                <th style="width:160px">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="area in currentTabAreas" :key="area.id">
                <td class="td-nombre">{{ area.nombre }}</td>
                <td>
                  <span class="tipo-badge" :class="area.es_prestable ? 'tipo-prestable' : 'tipo-interna'">
                    {{ area.es_prestable ? 'Prestable' : 'Interna' }}
                  </span>
                </td>
                <td class="td-cap">{{ area.capacidad || 'N/A' }}</td>
                <td>
                  <span class="estado-badge" :class="getEstadoClass(area)">
                    {{ area.estado_nombre || 'Desconocido' }}
                  </span>
                </td>
                <td>
                  <div class="acciones">
                    <button class="tbl-btn tbl-green" title="Editar" @click="handleEdit(area)">
                      <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                      </svg>
                      Editar
                    </button>

                    <button v-if="area.estado_id !== 4 && area.estado_id !== 5" class="tbl-btn tbl-gold" style="padding:.3rem .5rem" title="Desactivar" @click="handleDesactivate(area)">
                      <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                    </button>

                    <button v-if="area.estado_id === 5" class="tbl-btn tbl-green" style="padding:.3rem .5rem" title="Reactivar" @click="handleReactivate(area)">
                      <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="currentTabAreas.length === 0">
                <td colspan="5" class="td-vacio">
                  {{ search ? 'Sin resultados para esa búsqueda' : 'No hay áreas en esta categoría' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </template>
    </div>

    <!-- ══════════════════════════════════════
         MODAL: CREAR / EDITAR ÁREA
    ══════════════════════════════════════ -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ isEditing ? 'Editar Área' : 'Nueva Área' }}</h3>
          <button class="modal-close" @click="closeModal" :disabled="isSaving">×</button>
        </div>

        <div class="modal-body">
          <div class="form-field">
            <label class="form-label">Nombre <span class="req">*</span></label>
            <input v-model="formData.nombre" type="text" class="form-input" placeholder="Nombre del área"/>
          </div>

          <div class="form-field">
            <label class="form-label">Tipo <span class="req">*</span></label>
            <div class="tipo-toggle">
              <button type="button" class="toggle-opt" :class="{ 'toggle-opt-on': formData.es_prestable }" @click="formData.es_prestable = true">
                Prestable
              </button>
              <button type="button" class="toggle-opt" :class="{ 'toggle-opt-off': !formData.es_prestable }" @click="formData.es_prestable = false">
                Interna
              </button>
            </div>
          </div>

          <div class="form-field">
            <label class="form-label">
              Capacidad {{ formData.es_prestable ? '' : '(opcional)' }}
              <span v-if="formData.es_prestable" class="req">*</span>
            </label>
            <input
              v-model.number="formData.capacidad"
              type="number"
              :min="formData.es_prestable ? 1 : 0"
              class="form-input"
              placeholder="Ej: 8"
            />
          </div>

          <div class="form-field" v-if="isEditing">
            <label class="form-label">Estado</label>
            <select v-model="formData.estado_id" class="form-select">
              <option v-for="estado in estadosArea.filter(e => e.id !== 5)" :key="estado.id" :value="estado.id">
                {{ estado.estado }}
              </option>
            </select>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-modal-cancel" type="button" @click="closeModal" :disabled="isSaving">Cancelar</button>
          <button class="btn-modal-confirm" type="button" @click="handleSave" :disabled="isSaving">
            <span v-if="isSaving" class="spinner-mini"></span>
            {{ isSaving ? 'Guardando...' : (isEditing ? 'Guardar Cambios' : 'Crear Área') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════
         MODAL: CONFIRMAR ACCIÓN
    ══════════════════════════════════════ -->
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="closeConfirmModal">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>{{ confirmTitle }}</h3>
          <button class="modal-close" @click="closeConfirmModal" :disabled="isSaving">×</button>
        </div>
        <div class="modal-body">
          <p class="confirm-msg">{{ confirmMessage }}</p>
          <div v-if="confirmArea" class="confirm-item">
            <strong>{{ confirmArea.nombre }}</strong>
            <span>{{ confirmArea.es_prestable ? 'Prestable' : 'Interna' }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="closeConfirmModal" :disabled="isSaving">Cancelar</button>
          <button
            :class="confirmAction === 'reactivate' ? 'btn-modal-confirm' : 'btn-modal-delete'"
            @click="executeConfirmedAction"
            :disabled="isSaving"
          >
            <span v-if="isSaving" class="spinner-mini"></span>
            {{ isSaving ? 'Procesando...' : (confirmAction === 'reactivate' ? 'Sí, reactivar' : 'Sí, desactivar') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════
         MODAL: RESERVAR ÁREA
    ══════════════════════════════════════ -->
    <div v-if="showPrestamoModal" class="modal-overlay" @click.self="closePrestamoModal">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>Reservar Área</h3>
          <button class="modal-close" @click="closePrestamoModal">×</button>
        </div>
        <div class="modal-body">
          <div class="reserva-area-info">
            <span class="reserva-label">Área</span>
            <span class="reserva-valor">{{ selectedArea?.nombre }}</span>
          </div>

          <div class="form-field">
            <label class="form-label">Usuario <span class="req">*</span></label>
            <select v-model="prestamoForm.usuario_prestado_id" class="form-select">
              <option value="" disabled>Selecciona un usuario</option>
              <option v-for="usuario in usuarios" :key="usuario.id" :value="usuario.id">
                {{ usuario.nombre_completo }}
              </option>
            </select>
          </div>

          <div class="form-field">
            <label class="form-label">Hora de devolución <span class="req">*</span></label>
            <input type="datetime-local" v-model="prestamoForm.fecha_devolucion_esperada" class="form-input"/>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="closePrestamoModal">Cancelar</button>
          <button class="btn-modal-confirm" @click="crearPrestamoArea">Confirmar Reserva</button>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════
         TOAST
    ══════════════════════════════════════ -->
    <transition name="toast-in">
      <div v-if="showToast" class="toast" :class="toastType === 'error' ? 'toast-error' : 'toast-success'">
        <span>{{ toastMessage }}</span>
        <button class="toast-close" @click="showToast = false">×</button>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAreas } from '@/composables/useAreas'
import { prestamoAreasService } from '@/services/prestamoAreas'
import { useUsers } from '@/composables/useUsers'

// ── Import centralizado de botones ─────────────────────────────────────────
import '@/styles/buttons.css'

const search    = ref('')
const authStore = useAuthStore()
const {
  areas, estadosArea, isLoading, error,
  cargarAreas, cargarEstados,
  crearArea, actualizarArea, desactivarArea, reactivarArea
} = useAreas()

const { usuarios, cargarUsuarios } = useUsers()

// ── State ──────────────────────────────────────────────────────────────────
const activeTab       = ref('prestables')
const showModal       = ref(false)
const showConfirmModal = ref(false)
const showPrestamoModal = ref(false)
const isSaving        = ref(false)
const showToast       = ref(false)
const toastMessage    = ref('')
const toastType       = ref('success')

// Préstamo
const selectedArea  = ref(null)
const prestamoForm  = ref({ area_id: null, usuario_prestado_id: null, fecha_devolucion_esperada: null, observaciones: '' })

// Formulario área
const formData = ref({ id: null, nombre: '', capacidad: null, es_prestable: true, estado_id: 1 })

// Confirmación
const confirmAction  = ref(null)
const confirmArea    = ref(null)
const confirmTitle   = ref('')
const confirmMessage = ref('')

// ── Permisos ───────────────────────────────────────────────────────────────
const puedeCrearAreas      = computed(() => authStore.puedeCrearAreas)
const puedeEditarAreas     = computed(() => authStore.puedeEditarAreas)
const puedeDesactivarAreas = computed(() => authStore.puedeDesactivarAreas)
const puedeReactivarAreas  = computed(() => authStore.puedeReactivarAreas)

// ── Tabs ───────────────────────────────────────────────────────────────────
const tabs = [
  { id: 'prestables', label: 'Prestables' },
  { id: 'internas',   label: 'Internas' },
  { id: 'todas',      label: 'Todas' }
]

// ── Computed ───────────────────────────────────────────────────────────────
const areasPrestables = computed(() =>
  areas.value.filter(a =>
    a.es_prestable && a.estado_id !== 5 &&
    a.nombre.toLowerCase().includes(search.value.toLowerCase())
  )
)

const areasInternas = computed(() =>
  areas.value.filter(a =>
    !a.es_prestable && a.estado_id !== 5 &&
    a.nombre.toLowerCase().includes(search.value.toLowerCase())
  )
)

const todasLasAreas = computed(() =>
  areas.value.filter(a =>
    a.estado_id !== 4 &&
    a.nombre.toLowerCase().includes(search.value.toLowerCase())
  )
)

const currentTabAreas = computed(() => {
  switch (activeTab.value) {
    case 'prestables': return areasPrestables.value
    case 'internas':   return areasInternas.value
    case 'todas':      return todasLasAreas.value
    default:           return []
  }
})

const getTabCount = (tabId) => {
  switch (tabId) {
    case 'prestables': return areasPrestables.value.length
    case 'internas':   return areasInternas.value.length
    case 'todas':      return todasLasAreas.value.length
    default:           return 0
  }
}

const isEditing = computed(() => !!formData.value.id)

// ── Helpers ────────────────────────────────────────────────────────────────
const getEstadoClass = (area) => ({
  1: 'estado-disponible',
  2: 'estado-ocupada',
  3: 'estado-reparacion',
  4: 'estado-inactiva',
  5: 'estado-pendiente'
})[area.estado_id] || ''

// ── Carga ──────────────────────────────────────────────────────────────────
const loadData = async () => {
  try { await cargarAreas(); await cargarEstados() }
  catch (err) { console.error('Error cargando datos:', err) }
}

const forceReload = () => { loadData(); showToastMessage('Datos recargados') }

// ── Modal crear/editar ─────────────────────────────────────────────────────
const openCreateModal = () => {
  formData.value = { id: null, nombre: '', capacidad: null, es_prestable: true, estado_id: 1 }
  showModal.value = true
}

const handleEdit = (area) => {
  if (!puedeEditarAreas.value) { showToastMessage('Sin permisos para editar', 'error'); return }
  formData.value = { id: area.id, nombre: area.nombre, capacidad: area.capacidad, es_prestable: area.es_prestable, estado_id: area.estado_id }
  showModal.value = true
}

const closeModal = () => { if (!isSaving.value) showModal.value = false }

const handleSave = async () => {
  if (isSaving.value) return
  if (!formData.value.nombre.trim()) { showToastMessage('El nombre es requerido', 'error'); return }
  if (formData.value.es_prestable && !formData.value.capacidad) { showToastMessage('La capacidad es requerida para áreas prestables', 'error'); return }

  isSaving.value = true
  try {
    const payload = { nombre: formData.value.nombre, capacidad: formData.value.capacidad, es_prestable: formData.value.es_prestable, estado_id: formData.value.estado_id }
    if (isEditing.value) {
      await actualizarArea(formData.value.id, payload)
      showToastMessage('Área actualizada correctamente')
    } else {
      await crearArea(payload)
      showToastMessage('Área creada correctamente')
    }
    showModal.value = false
  } catch (err) {
    showToastMessage(err.message || 'Error al guardar', 'error')
  } finally {
    isSaving.value = false
  }
}

// ── Desactivar / Reactivar ─────────────────────────────────────────────────
const handleDesactivate = (area) => {
  if (!puedeDesactivarAreas.value) { showToastMessage('Sin permisos para desactivar', 'error'); return }
  confirmArea.value = area; confirmAction.value = 'desactivate'
  confirmTitle.value = 'Desactivar Área'
  confirmMessage.value = `¿Desactivar el área "${area.nombre}"?`
  showConfirmModal.value = true
}

const handleReactivate = (area) => {
  if (!puedeReactivarAreas.value) { showToastMessage('Sin permisos para reactivar', 'error'); return }
  confirmArea.value = area; confirmAction.value = 'reactivate'
  confirmTitle.value = 'Reactivar Área'
  confirmMessage.value = `¿Reactivar el área "${area.nombre}"?`
  showConfirmModal.value = true
}

const closeConfirmModal = () => {
  if (!isSaving.value) { showConfirmModal.value = false; confirmArea.value = null; confirmAction.value = null }
}

const executeConfirmedAction = async () => {
  if (!confirmArea.value || isSaving.value) return
  isSaving.value = true
  try {
    if (confirmAction.value === 'desactivate') {
      await desactivarArea(confirmArea.value.id)
      showToastMessage('Área desactivada')
    } else {
      await reactivarArea(confirmArea.value.id)
      showToastMessage('Área reactivada')
    }
    closeConfirmModal()
  } catch (err) {
    showToastMessage(err.message || 'Error en la acción', 'error')
  } finally {
    isSaving.value = false
  }
}

// ── Préstamo área ──────────────────────────────────────────────────────────
const openPrestamoModal = (area) => {
  selectedArea.value = area
  prestamoForm.value = { area_id: area.id, usuario_prestado_id: null, fecha_devolucion_esperada: null, observaciones: '' }
  showPrestamoModal.value = true
}

const closePrestamoModal = () => { showPrestamoModal.value = false; selectedArea.value = null }

const crearPrestamoArea = async () => {
  try {
    await prestamoAreasService.crearPrestamo(prestamoForm.value)
    showToastMessage('Área reservada correctamente')
    closePrestamoModal()
    await cargarAreas()
  } catch (err) {
    showToastMessage('Error creando reserva', 'error')
  }
}

const devolverArea = async (area) => {
  if (!confirm(`¿Devolver el área "${area.nombre}"?`)) return
  try {
    const response = await prestamoAreasService.getPrestamosVigentes()
    const prestamos = response.prestamos || response || []
    const prestamoActivo = prestamos.find(p => Number(p.area_id) === Number(area.id))
    if (!prestamoActivo) { showToastMessage('No se encontró préstamo activo', 'error'); return }
    await prestamoAreasService.devolverPrestamo(prestamoActivo.id)
    showToastMessage('Área devuelta correctamente')
    await cargarAreas()
  } catch (err) {
    showToastMessage('Error devolviendo área', 'error')
  }
}

// ── Toast ──────────────────────────────────────────────────────────────────
const showToastMessage = (message, type = 'success') => {
  toastMessage.value = message; toastType.value = type; showToast.value = true
  setTimeout(() => { showToast.value = false }, 3000)
}

onMounted(async () => { await Promise.all([loadData(), cargarUsuarios()]) })
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

/*
 * Botones centralizados en src/styles/buttons.css
 * Clases usadas: .btn-primary, .btn-modal-cancel, .btn-modal-confirm,
 * .btn-modal-delete, .tbl-btn, .tbl-green, .tbl-gold, .tbl-blue, .spinner-mini
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
  --shadow-md:    0 8px 24px rgba(26,71,49,.12);
}

.areas-management {
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

.btn-refresh {
  width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.15);
  border-radius: 8px; color: rgba(255,255,255,.75); cursor: pointer; transition: all .2s;
}
.btn-refresh:hover { background: rgba(255,255,255,.18); color: #fff; }

.btn-crear {
  display: flex; align-items: center; gap: .4rem; padding: .5rem 1.1rem;
  background: linear-gradient(135deg, var(--gold-light), var(--gold-mid));
  border: none; border-radius: 8px; color: var(--green-dark);
  font-family: 'DM Sans', sans-serif; font-size: .82rem; font-weight: 700;
  cursor: pointer; box-shadow: 0 4px 14px rgba(244,197,66,.3); transition: all .2s;
}
.btn-crear:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(244,197,66,.4); }

.header-stats { display: flex; gap: .75rem; margin-top: 1.25rem; position: relative; flex-wrap: wrap; }
.hstat { display: flex; flex-direction: column; align-items: center; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.1); border-radius: 9px; padding: .45rem .875rem; min-width: 80px; }
.hstat-num { font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: #fff; line-height: 1; }
.hstat-lbl { font-size: .64rem; color: rgba(255,255,255,.55); text-transform: uppercase; letter-spacing: .07em; margin-top: 2px; white-space: nowrap; }

/* ── Toolbar (tabs + búsqueda) ───────────────────────────────────────────── */
.toolbar {
  display: flex; align-items: center; gap: 1rem;
  padding: .875rem 1.5rem;
  background: var(--card-bg); border-bottom: 1.5px solid var(--cream-border);
  flex-wrap: wrap;
}

/* Tabs */
.tabs { display: flex; gap: .375rem; flex-shrink: 0; }
.tab-btn {
  display: flex; align-items: center; gap: .5rem;
  padding: .45rem .875rem;
  background: var(--cream); border: 1.5px solid var(--cream-border);
  border-radius: 9px; font-family: 'DM Sans', sans-serif;
  font-size: .82rem; font-weight: 600; color: #5a7a5a;
  cursor: pointer; transition: all .18s;
}
.tab-btn:hover { background: #111; color: #fff; border-color: #111; }
.tab-active { background: var(--green-mid) !important; color: #fff !important; border-color: var(--green-mid) !important; }

.tab-count {
  background: rgba(0,0,0,.1); color: inherit;
  font-size: .68rem; font-weight: 700;
  padding: .1rem .45rem; border-radius: 20px;
}
.tab-count-active { background: rgba(255,255,255,.25); }

/* Búsqueda */
.search-wrap {
  display: flex; align-items: center; gap: .5rem; flex: 1; min-width: 200px;
  padding: .5rem .75rem; background: var(--cream);
  border: 1.5px solid var(--cream-border); border-radius: 9px; color: #9ab5a0;
}
.search-ico { flex-shrink: 0; }
.search-input { flex: 1; border: none; background: none; font-family: 'DM Sans', sans-serif; font-size: .875rem; color: #1a2e1a; outline: none; }
.search-input::placeholder { color: #9ab5a0; }
.search-clear { background: none; border: none; color: #9ab5a0; cursor: pointer; font-size: 1rem; padding: 0; line-height: 1; }
.search-clear:hover { color: var(--green-dark); }

/* ── Contenido ───────────────────────────────────────────────────────────── */
.content-section { padding: 1.5rem; }

/* Estados */
.estado-loading, .estado-error, .estado-vacio { display: flex; flex-direction: column; align-items: center; padding: 3rem 2rem; gap: .75rem; text-align: center; background: var(--card-bg); border: 1.5px solid var(--cream-border); border-radius: 16px; }
.spinner { width: 36px; height: 36px; border: 3px solid var(--green-pale); border-top-color: var(--green-mid); border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.estado-loading p, .estado-error p { color: #5a7a5a; font-size: .875rem; margin: 0; }
.estado-error p { color: #d62828; }
.vacio-ico    { color: #b8ddc8; }
.vacio-titulo { font-weight: 700; color: var(--green-dark); margin: 0; }
.vacio-desc   { font-size: .82rem; color: #5a7a5a; margin: 0; }

/* ── Cards (prestables) ──────────────────────────────────────────────────── */
.cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.1rem; }

.area-card {
  display: flex; background: var(--card-bg);
  border: 1.5px solid var(--cream-border); border-radius: 14px;
  overflow: hidden; box-shadow: var(--shadow-sm); transition: transform .2s, box-shadow .2s;
}
.area-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }

/* Indicador lateral de estado */
.card-indicator { width: 5px; flex-shrink: 0; }
.card-disponible .card-indicator  { background: var(--green-light); }
.card-ocupada .card-indicator     { background: var(--gold-light); }
.card-reparacion .card-indicator  { background: #60a5fa; }
.card-inactiva .card-indicator    { background: #cbd5e1; }

.card-body { flex: 1; padding: 1rem 1.1rem; display: flex; flex-direction: column; gap: .75rem; }

.card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: .5rem; }
.card-nombre { font-family: 'Playfair Display', serif; font-size: .95rem; font-weight: 700; color: var(--green-dark); margin: 0; }

.card-info { display: flex; flex-direction: column; gap: .3rem; background: #f3faf5; padding: .625rem .75rem; border-radius: 8px; }
.card-info-row { display: flex; justify-content: space-between; font-size: .78rem; }
.ci-label { color: #9ab5a0; }
.ci-valor { color: #1a2e1a; font-weight: 600; }

.card-acciones { display: flex; gap: .35rem; flex-wrap: wrap; }

/* Badges de estado en cards y tabla */
.card-estado-badge, .estado-badge {
  display: inline-block; padding: .2rem .55rem;
  border-radius: 20px; font-size: .68rem; font-weight: 700; white-space: nowrap;
}
.estado-disponible { background: var(--green-pale); color: var(--green-dark); border: 1px solid #b8ddc8; }
.estado-ocupada    { background: var(--gold-pale);  color: var(--gold-mid);   border: 1px solid #fde68a; }
.estado-reparacion { background: #dbeafe; color: #1e3a5f; border: 1px solid #bfdbfe; }
.estado-inactiva   { background: #fff0f0; color: #b91c1c; border: 1px solid #fca5a5; }
.estado-pendiente  { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; }

/* Badges tipo */
.tipo-badge { display: inline-block; padding: .2rem .55rem; border-radius: 20px; font-size: .7rem; font-weight: 700; }
.tipo-prestable { background: #e3f2fd; color: #1565c0; }
.tipo-interna   { background: #f3e5f5; color: #7b1fa2; }

/* ── Tabla ───────────────────────────────────────────────────────────────── */
.tabla-wrap { background: var(--card-bg); border: 1.5px solid var(--cream-border); border-radius: 14px; overflow: hidden; box-shadow: var(--shadow-sm); }
.tabla { width: 100%; border-collapse: collapse; font-size: .82rem; }
.tabla thead { background: linear-gradient(135deg, #1a4731, #2d6a4f); }
.tabla thead th { padding: .75rem 1rem; text-align: left; color: rgba(255,255,255,.88); font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; }
.tabla tbody tr { border-bottom: 1px solid #f1f5f0; transition: background .15s; }
.tabla tbody tr:last-child { border-bottom: none; }
.tabla tbody tr:hover { background: #fafef8; }
.tabla td { padding: .75rem 1rem; vertical-align: middle; color: #334155; }
.td-nombre { font-weight: 600; color: #1a2e1a; }
.td-cap    { color: #64748b; font-size: .8rem; }
.td-vacio  { text-align: center; color: #9ab5a0; font-size: .82rem; padding: 2rem !important; }
.acciones  { display: flex; align-items: center; gap: .35rem; flex-wrap: wrap; }

/* ── Modales ─────────────────────────────────────────────────────────────── */
.modal-overlay {
  position: fixed; inset: 0;
  background: transparent;
  display: flex; align-items: center; justify-content: center; z-index: 2000;
}
.modal-overlay::before {
  content: ''; position: fixed; inset: 0;
  background: rgba(26,47,26,.55); backdrop-filter: blur(8px); z-index: -1;
}
.modal { background: var(--card-bg); border-radius: 16px; width: 90%; max-width: 480px; border: 1.5px solid var(--cream-border); box-shadow: 0 24px 64px rgba(0,0,0,.2); animation: modalIn .25s cubic-bezier(.22,1,.36,1); position: relative; z-index: 1; }
.modal-sm { max-width: 400px; }
@keyframes modalIn { from { opacity: 0; transform: translateY(-14px) scale(.97); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.1rem 1.375rem .875rem; border-bottom: 1.5px solid #eef5f0; }
.modal-header h3 { font-family: 'Playfair Display', serif; font-size: 1.05rem; font-weight: 700; color: var(--green-dark); margin: 0; }
.modal-close { background: none; border: none; font-size: 1.3rem; color: #9ab5a0; cursor: pointer; padding: 0; line-height: 1; transition: color .15s; }
.modal-close:hover { color: var(--green-dark); }
.modal-body { padding: 1.25rem 1.375rem; display: flex; flex-direction: column; gap: 1rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: .625rem; padding: .875rem 1.375rem; border-top: 1.5px solid #eef5f0; }

/* Formulario modal */
.form-field { display: flex; flex-direction: column; gap: 5px; }
.form-label { font-size: .72rem; font-weight: 700; color: var(--green-dark); text-transform: uppercase; letter-spacing: .07em; }
.req { color: #d62828; }
.form-input, .form-select { padding: .6rem .75rem; background: #fff; border: 1.5px solid var(--cream-border); border-radius: 9px; font-family: 'DM Sans', sans-serif; font-size: .875rem; color: #1a2e1a; outline: none; transition: border-color .2s; width: 100%; box-sizing: border-box; }
.form-input:focus, .form-select:focus { border-color: var(--green-light); }

/* Toggle tipo */
.tipo-toggle { display: flex; gap: .5rem; }
.toggle-opt { flex: 1; padding: .5rem; background: #fff; border: 1.5px solid var(--cream-border); border-radius: 9px; font-family: 'DM Sans', sans-serif; font-size: .82rem; font-weight: 600; color: #5a7a5a; cursor: pointer; transition: all .2s; }
.toggle-opt-on  { background: var(--green-pale); color: var(--green-dark); border-color: #b8ddc8; }
.toggle-opt-off { background: #f0f7f2; color: var(--green-mid); border-color: #b8ddc8; }

/* Confirmación */
.confirm-msg  { font-size: .875rem; color: #334155; margin: 0 0 .75rem; }
.confirm-item { display: flex; flex-direction: column; gap: 2px; padding: .75rem; background: var(--cream); border-radius: 9px; border-left: 3px solid var(--green-light); font-size: .82rem; }
.confirm-item strong { color: var(--green-dark); }
.confirm-item span   { color: #9ab5a0; }

/* Reserva */
.reserva-area-info { display: flex; justify-content: space-between; align-items: center; padding: .75rem; background: var(--green-pale); border-radius: 9px; font-size: .85rem; }
.reserva-label { color: #5a7a5a; font-weight: 600; }
.reserva-valor { color: var(--green-dark); font-weight: 700; }

/* ── Toast ───────────────────────────────────────────────────────────────── */
.toast { position: fixed; bottom: 2rem; right: 2rem; display: flex; align-items: center; gap: .75rem; padding: .75rem 1.1rem; border-radius: 10px; font-size: .82rem; font-weight: 600; color: #fff; z-index: 9999; box-shadow: 0 4px 20px rgba(0,0,0,.15); }
.toast-success { background: #16a34a; }
.toast-error   { background: #d62828; }
.toast-close   { background: none; border: none; color: rgba(255,255,255,.75); font-size: 1.1rem; cursor: pointer; padding: 0; line-height: 1; }
.toast-close:hover { color: #fff; }
.toast-in-enter-active, .toast-in-leave-active { transition: all .3s ease; }
.toast-in-enter-from, .toast-in-leave-to { opacity: 0; transform: translateX(16px); }
</style>