<template>
  <div class="laptops-view">

    <!-- ══ HEADER ══ -->
    <header class="page-header">
      <div class="header-inner">
        <div class="header-texto">
          <p class="header-sup">{{ esAdmin ? 'Panel de administración' : 'Centro Integral de Documentación' }}</p>
          <h1 class="header-titulo">{{ esAdmin ? 'Gestión de Equipos' : 'Equipos Disponibles' }}</h1>
          <p class="header-sub">{{ esAdmin ? 'Inventario de equipos de cómputo' : 'Consulta los equipos disponibles para préstamo' }}</p>
        </div>

        <div class="header-acciones">
          <!-- Admin: toggle retirados -->
          <button v-if="esAdmin" class="btn-toggle-inactivos" :class="{ 'btn-toggle-on': showRetirados }" @click="toggleRetirados">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
            </svg>
            {{ showRetirados ? 'Ocultar retirados' : 'Mostrar retirados' }}
          </button>

          <!-- Admin nivel 3+: crear -->
          <button v-if="canCreate" class="btn-crear" @click="abrirModal()">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
            </svg>
            Agregar Equipo
          </button>
        </div>
      </div>

      <!-- Stats -->
      <div class="header-stats">
        <div class="hstat hstat-green">
          <span class="hstat-num">{{ stats.disponibles }}</span>
          <span class="hstat-lbl">Disponibles</span>
        </div>
        <div class="hstat" v-if="esAdmin">
          <span class="hstat-num">{{ stats.total }}</span>
          <span class="hstat-lbl">Total</span>
        </div>
        <div class="hstat hstat-warn" v-if="esAdmin && stats.mantenimiento > 0">
          <span class="hstat-num">{{ stats.mantenimiento }}</span>
          <span class="hstat-lbl">Mantenimiento</span>
        </div>
        <div class="hstat hstat-muted" v-if="esAdmin && stats.retirados > 0">
          <span class="hstat-num">{{ stats.retirados }}</span>
          <span class="hstat-lbl">Retirados</span>
        </div>
      </div>
    </header>

    <!-- ══ TOOLBAR ══ -->
    <div class="toolbar">
      <!-- Búsqueda — todos los niveles -->
      <div class="search-wrap">
        <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input v-model="search" type="text" class="search-input" placeholder="Buscar por modelo, marca, serie..."/>
        <button v-if="search" class="search-clear" @click="search = ''">×</button>
      </div>

      <!-- Filtros solo para admin -->
      <template v-if="esAdmin">
        <select v-model="filtros.estado_id" class="filter-select">
          <option value="">Todos los estados</option>
          <option v-for="e in cat.estados" :key="e.id" :value="e.id">{{ e.estado }}</option>
        </select>

        <select v-model="filtros.tipo_equipo_id" class="filter-select">
          <option value="">Todos los tipos</option>
          <option v-for="t in cat.tipos" :key="t.id" :value="t.id">{{ t.tipo }}</option>
        </select>

        <select v-model="filtros.marca_id" class="filter-select">
          <option value="">Todas las marcas</option>
          <option v-for="m in cat.marcas" :key="m.id" :value="m.id">{{ m.marca }}</option>
        </select>

        <button v-if="hayFiltros" class="btn-reset" @click="limpiarFiltros">Limpiar filtros</button>
      </template>

      <!-- Estudiante: solo toggle disponible/todos prestables -->
      <template v-else>
        <button
          class="filter-toggle"
          :class="{ 'filter-toggle-on': soloDisponibles }"
          @click="soloDisponibles = !soloDisponibles"
        >
          <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          {{ soloDisponibles ? 'Solo disponibles' : 'Todos' }}
        </button>
      </template>
    </div>

    <!-- ══ CONTENIDO ══ -->
    <div class="contenido">

      <div v-if="isLoading" class="estado-c"><div class="spinner"></div><p>Cargando equipos...</p></div>
      <div v-else-if="errorMsg" class="estado-e"><p>{{ errorMsg }}</p><button class="btn-retry" @click="cargar">Reintentar</button></div>

      <div v-else-if="filtrados.length === 0" class="estado-v">
        <svg width="48" height="48" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.2" class="vacio-ico">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
        <p class="vacio-titulo">{{ search ? 'Sin resultados' : 'No hay equipos disponibles' }}</p>
        <p class="vacio-desc">{{ search ? 'Intenta con otros términos' : 'No hay equipos en esta categoría' }}</p>
      </div>

      <!-- ── CUADRÍCULA (igual que AreasEstudio) ── -->
      <div v-else class="cards-grid">
        <div
          v-for="equipo in paginados"
          :key="equipo.id"
          class="equipo-card"
          :class="getCardClass(equipo)"
        >
          <!-- Indicador de estado -->
          <div class="estado-indicator" :class="getIndicatorClass(equipo)"></div>

          <div class="card-top">
            <div class="card-icono" :class="getIconoClass(equipo)">
              <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <span class="estado-chip" :class="getChipClass(equipo)">{{ equipo.estado_nombre }}</span>
            <span v-if="equipo.es_prestable" class="prestable-chip">Prestable</span>
          </div>

          <div class="card-body">
            <p class="equipo-serie">{{ equipo.numero_serie }}</p>
            <h3 class="equipo-modelo">{{ equipo.modelo }}</h3>
            <p class="equipo-marca">{{ equipo.marca_nombre }}</p>

            <div class="equipo-detalles">
              <div class="detalle-row" v-if="equipo.tipo_equipo_nombre">
                <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
                </svg>
                <span>{{ equipo.tipo_equipo_nombre }}</span>
              </div>
              <div class="detalle-row" v-if="equipo.area_nombre">
                <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                <span>{{ equipo.area_nombre }}</span>
              </div>
              <div class="detalle-row" v-if="esAdmin && equipo.especificaciones">
                <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <span class="especificaciones">{{ equipo.especificaciones }}</span>
              </div>
            </div>
          </div>

          <!-- Acciones — solo admin -->
          <div v-if="esAdmin" class="card-footer">
            <button v-if="canEdit" class="tbl-btn tbl-green" @click="abrirModal(equipo)" title="Editar">
              <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
              Editar
            </button>

            <button
              v-if="canEdit && equipo.estado_id !== ESTADO_RETIRADO && equipo.estado_id !== ESTADO_PRESTADO"
              class="tbl-btn tbl-gold" style="padding:.3rem .5rem"
              @click="pedirConfirm(equipo, 'retirar')" title="Retirar"
            >
              <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </button>

            <button
              v-if="canEdit && equipo.estado_id === ESTADO_RETIRADO"
              class="tbl-btn tbl-green" style="padding:.3rem .5rem"
              @click="pedirConfirm(equipo, 'reactivar')" title="Reactivar"
            >
              <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </button>

            <button
              v-if="canDelete && equipo.estado_id === ESTADO_RETIRADO"
              class="tbl-btn tbl-red" style="padding:.3rem .5rem"
              @click="pedirConfirm(equipo, 'eliminar')" title="Eliminar permanentemente"
            >
              <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Paginación -->
      <div v-if="!isLoading && filtrados.length > 0" class="paginacion">
        <span class="pag-info">{{ desde }}–{{ hasta }} de {{ filtrados.length }}</span>
        <div class="pag-controles">
          <button class="pag-btn" :disabled="pagina === 1" @click="pagina--">← Anterior</button>
          <span v-for="p in paginas" :key="p" class="pag-num" :class="{ 'pag-num-active': p === pagina }" @click="pagina = p">{{ p }}</span>
          <button class="pag-btn" :disabled="pagina === totalPaginas" @click="pagina++">Siguiente →</button>
        </div>
        <div class="pag-size">
          <label>Mostrar</label>
          <select v-model="porPagina" @change="pagina = 1" class="pag-select">
            <option :value="12">12</option><option :value="24">24</option><option :value="48">48</option>
          </select>
        </div>
      </div>
    </div>

    <!-- ══ MODAL CREAR / EDITAR ══ -->
    <div v-if="modal.visible" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ modal.isEditing ? 'Editar Equipo' : 'Agregar Equipo' }}</h3>
          <button class="modal-close" @click="cerrarModal" :disabled="procesando">×</button>
        </div>

        <div class="modal-body">
          <div v-if="cat.cargando" class="estado-c estado-c-sm">
            <div class="spinner spinner-sm"></div><p>Cargando catálogos...</p>
          </div>

          <div v-else class="form-grid">
            <div class="form-field">
              <label class="form-label">Número de serie <span class="req">*</span></label>
              <input v-model="modal.form.numero_serie" type="text" class="form-input" placeholder="SN-2024-001"/>
            </div>

            <div class="form-field">
              <label class="form-label">Modelo <span class="req">*</span></label>
              <input v-model="modal.form.modelo" type="text" class="form-input" placeholder="ThinkPad E14"/>
            </div>

            <div class="form-field">
              <label class="form-label">Marca <span class="req">*</span></label>
              <select v-model="modal.form.marca_id" class="form-select">
                <option value="" disabled>Selecciona una marca</option>
                <option v-for="m in cat.marcas" :key="m.id" :value="m.id">{{ m.marca }}</option>
              </select>
            </div>

            <div class="form-field">
              <label class="form-label">Tipo <span class="req">*</span></label>
              <select v-model="modal.form.tipo_equipo_id" class="form-select">
                <option value="" disabled>Selecciona un tipo</option>
                <option v-for="t in cat.tipos" :key="t.id" :value="t.id">{{ t.tipo }}</option>
              </select>
            </div>

            <div class="form-field">
              <label class="form-label">Estado <span class="req">*</span></label>
              <select v-model="modal.form.estado_id" class="form-select">
                <option v-for="e in estadosEditables" :key="e.id" :value="e.id">{{ e.estado }}</option>
              </select>
            </div>

            <div class="form-field">
              <label class="form-label">Área</label>
              <select v-model="modal.form.area_id" class="form-select">
                <option :value="null">Sin área asignada</option>
                <option v-for="a in cat.areas" :key="a.id" :value="a.id">{{ a.nombre }}</option>
              </select>
            </div>

            <div class="form-field form-field-full">
              <label class="form-label">Especificaciones</label>
              <textarea v-model="modal.form.especificaciones" class="form-input form-textarea" rows="2" placeholder="RAM, procesador, almacenamiento..."></textarea>
            </div>

            <div class="form-field form-field-full">
              <label class="form-label">¿Es prestable?</label>
              <div class="tipo-toggle">
                <button type="button" class="toggle-opt" :class="{ 'toggle-opt-on': modal.form.es_prestable }" @click="modal.form.es_prestable = true">Sí</button>
                <button type="button" class="toggle-opt" :class="{ 'toggle-opt-off': !modal.form.es_prestable }" @click="modal.form.es_prestable = false">No</button>
              </div>
            </div>
          </div>

          <div v-if="modal.error" class="form-error">{{ modal.error }}</div>
        </div>

        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="cerrarModal" :disabled="procesando">Cancelar</button>
          <button class="btn-modal-confirm" @click="guardar" :disabled="procesando || cat.cargando">
            <span v-if="procesando" class="spinner-mini"></span>
            {{ procesando ? 'Guardando...' : (modal.isEditing ? 'Guardar Cambios' : 'Crear Equipo') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══ MODAL CONFIRMAR ══ -->
    <div v-if="confirm.visible" class="modal-overlay" @click.self="cerrarConfirm">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>{{ confirm.titulo }}</h3>
          <button class="modal-close" @click="cerrarConfirm" :disabled="procesando">×</button>
        </div>
        <div class="modal-body">
          <p class="confirm-msg">{{ confirm.mensaje }}</p>
          <div v-if="confirm.equipo" class="confirm-item">
            <strong>{{ confirm.equipo.modelo }}</strong>
            <span>{{ confirm.equipo.marca_nombre }}</span>
            <span>{{ confirm.equipo.numero_serie }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="cerrarConfirm" :disabled="procesando">Cancelar</button>
          <button :class="confirm.btnClass" @click="ejecutar" :disabled="procesando">
            <span v-if="procesando" class="spinner-mini"></span>
            {{ procesando ? 'Procesando...' : confirm.btnTexto }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══ TOAST ══ -->
    <transition name="toast-in">
      <div v-if="toast.visible" class="toast" :class="toast.tipo">
        {{ toast.msg }}
        <button class="toast-close" @click="toast.visible = false">×</button>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { equiposService } from '@/services/equipos'
import '@/styles/buttons.css'

const auth = useAuthStore()

// ── Permisos ───────────────────────────────────────────────────────────────
const esAdmin   = computed(() => auth.tipoUsuarioId >= 2)
const canCreate = computed(() => auth.tipoUsuarioId >= 3)
const canEdit   = computed(() => auth.tipoUsuarioId >= 3)
const canDelete = computed(() => auth.tipoUsuarioId >= 3)

// ── Constantes de estado ───────────────────────────────────────────────────
const ESTADO_DISPONIBLE   = 1
const ESTADO_PRESTADO     = 2
const ESTADO_RETIRADO     = 5

// ── State ──────────────────────────────────────────────────────────────────
const equipos   = ref([])
const isLoading = ref(false)
const errorMsg  = ref(null)
const procesando = ref(false)
const search    = ref('')
const pagina    = ref(1)
const porPagina = ref(12)
const showRetirados  = ref(false)
const soloDisponibles = ref(true)

const filtros = ref({ estado_id: '', tipo_equipo_id: '', marca_id: '' })

// Catálogos
const cat = reactive({ estados: [], tipos: [], marcas: [], areas: [], cargando: false })

// Modal crear/editar
const modal = ref({
  visible: false, isEditing: false, equipoOriginal: null, error: '',
  form: { numero_serie: '', modelo: '', marca_id: '', tipo_equipo_id: '', estado_id: 1, area_id: null, especificaciones: '', es_prestable: true }
})

// Modal confirmar
const confirm = ref({ visible: false, titulo: '', mensaje: '', btnTexto: '', btnClass: '', accion: '', equipo: null })

// Toast
const toast = ref({ visible: false, msg: '', tipo: 'toast-success' })

// ── Computed ───────────────────────────────────────────────────────────────
const filtrados = computed(() => {
  let r = [...equipos.value]

  if (!esAdmin.value) {
    // Estudiante: solo prestables disponibles
    r = r.filter(e => e.es_prestable && e.estado_id === ESTADO_DISPONIBLE)
    if (!soloDisponibles.value) r = equipos.value.filter(e => e.es_prestable)
  } else {
    // Admin
    if (!showRetirados.value) r = r.filter(e => e.estado_id !== ESTADO_RETIRADO)
    if (filtros.value.estado_id)      r = r.filter(e => e.estado_id === parseInt(filtros.value.estado_id))
    if (filtros.value.tipo_equipo_id) r = r.filter(e => e.tipo_equipo_id === parseInt(filtros.value.tipo_equipo_id))
    if (filtros.value.marca_id)       r = r.filter(e => e.marca_id === parseInt(filtros.value.marca_id))
  }

  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    r = r.filter(e =>
      e.modelo?.toLowerCase().includes(q) ||
      e.marca_nombre?.toLowerCase().includes(q) ||
      e.numero_serie?.toLowerCase().includes(q) ||
      e.tipo_nombre?.toLowerCase().includes(q)
    )
  }
  return r
})

const stats = computed(() => ({
  total:        equipos.value.length,
  disponibles:  equipos.value.filter(e => e.estado_id === ESTADO_DISPONIBLE).length,
  mantenimiento:equipos.value.filter(e => e.estado_id === 3).length,
  retirados:    equipos.value.filter(e => e.estado_id === ESTADO_RETIRADO).length,
}))

const totalPaginas = computed(() => Math.ceil(filtrados.value.length / porPagina.value) || 1)
const paginados    = computed(() => { const s = (pagina.value - 1) * porPagina.value; return filtrados.value.slice(s, s + porPagina.value) })
const desde        = computed(() => (pagina.value - 1) * porPagina.value + 1)
const hasta        = computed(() => Math.min(pagina.value * porPagina.value, filtrados.value.length))
const paginas      = computed(() => {
  const max = 5, tot = totalPaginas.value
  if (tot <= max) return Array.from({ length: tot }, (_, i) => i + 1)
  let start = Math.max(1, pagina.value - 2)
  const end = Math.min(tot, start + max - 1)
  if (end - start + 1 < max) start = end - max + 1
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})
const hayFiltros = computed(() => Object.values(filtros.value).some(v => v !== '') || search.value.trim() !== '')

// Estados editables — excluye Retirado del selector (se maneja con botón)
const estadosEditables = computed(() => cat.estados.filter(e => e.id !== ESTADO_RETIRADO))

// ── Carga ──────────────────────────────────────────────────────────────────
const cargar = async () => {
  isLoading.value = true; errorMsg.value = null
  try {
    const r = await equiposService.getEquipos()
    equipos.value = r?.equipos ?? (Array.isArray(r) ? r : [])
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || 'Error cargando equipos'
  } finally {
    isLoading.value = false
  }
}

const cargarCatalogos = async () => {
  if (cat.tipos.length) return
  cat.cargando = true
  try {
    const [estados, tipos, marcas] = await Promise.all([
      equiposService.getEstados(),
      equiposService.getTipos(),
      equiposService.getMarcas(),
    ])
    cat.estados = estados
    cat.tipos   = tipos
    cat.marcas  = marcas

    // Cargar áreas también
    try {
      const { areasService } = await import('@/services/areas')
      const r = await areasService.getAreas()
      cat.areas = r?.areas ?? []
    } catch { cat.areas = [] }

  } catch (e) { console.error('Error catálogos:', e) }
  finally { cat.cargando = false }
}

// ── Modal crear/editar ─────────────────────────────────────────────────────
const abrirModal = async (equipo = null) => {
  await cargarCatalogos()
  if (equipo) {
    modal.value = {
      visible: true, isEditing: true, equipoOriginal: equipo, error: '',
      form: {
        numero_serie:     equipo.numero_serie,
        modelo:           equipo.modelo,
        marca_id:         equipo.marca_id,
        tipo_equipo_id:   equipo.tipo_equipo_id,
        estado_id:        equipo.estado_id,
        area_id:          equipo.area_id || null,
        especificaciones: equipo.especificaciones || '',
        es_prestable:     equipo.es_prestable,
      }
    }
  } else {
    modal.value = {
      visible: true, isEditing: false, equipoOriginal: null, error: '',
      form: { numero_serie: '', modelo: '', marca_id: '', tipo_equipo_id: '', estado_id: 1, area_id: null, especificaciones: '', es_prestable: true }
    }
  }
}

const cerrarModal = () => { if (!procesando.value) modal.value.visible = false }

const validar = () => {
  const f = modal.value.form
  if (!f.numero_serie?.trim()) { modal.value.error = 'El número de serie es requerido'; return false }
  if (!f.modelo?.trim())       { modal.value.error = 'El modelo es requerido'; return false }
  if (!f.marca_id)             { modal.value.error = 'Selecciona una marca'; return false }
  if (!f.tipo_equipo_id)       { modal.value.error = 'Selecciona un tipo'; return false }
  modal.value.error = ''
  return true
}

const guardar = async () => {
  if (!validar()) return
  procesando.value = true
  const payload = { ...modal.value.form, area_id: modal.value.form.area_id || null }
  try {
    if (modal.value.isEditing) {
      const actualizado = await equiposService.updateEquipo(modal.value.equipoOriginal.id, payload)
      const idx = equipos.value.findIndex(e => e.id === modal.value.equipoOriginal.id)
      if (idx !== -1) Object.assign(equipos.value[idx], actualizado)
      mostrarToast('Equipo actualizado correctamente')
    } else {
      const nuevo = await equiposService.createEquipo(payload)
      equipos.value.unshift(nuevo)
      mostrarToast('Equipo creado correctamente')
    }
    modal.value.visible = false
  } catch (e) {
    modal.value.error = e.response?.data?.detail || 'Error al guardar'
  } finally {
    procesando.value = false
  }
}

// ── Modal confirmar ────────────────────────────────────────────────────────
const CFG = {
  retirar:   { titulo: 'Retirar Equipo',   mensaje: m => `¿Retirar "${m}"?`,                             btnTexto: 'Sí, retirar',    btnClass: 'btn-modal-cancel' },
  reactivar: { titulo: 'Reactivar Equipo', mensaje: m => `¿Reactivar "${m}"?`,                           btnTexto: 'Sí, reactivar',  btnClass: 'btn-modal-confirm' },
  eliminar:  { titulo: 'Eliminar Equipo',  mensaje: m => `¿Eliminar permanentemente "${m}"? No se puede deshacer.`, btnTexto: 'Sí, eliminar',   btnClass: 'btn-modal-delete' }
}

const pedirConfirm = (equipo, accion) => {
  const cfg = CFG[accion]
  confirm.value = { visible: true, titulo: cfg.titulo, mensaje: cfg.mensaje(equipo.modelo), btnTexto: cfg.btnTexto, btnClass: cfg.btnClass, accion, equipo }
}
const cerrarConfirm = () => { if (!procesando.value) confirm.value.visible = false }

const ejecutar = async () => {
  const { accion, equipo } = confirm.value
  if (!equipo) return
  procesando.value = true
  try {
    switch (accion) {
      case 'retirar':
        await equiposService.retirarEquipo(equipo.id)
        equipo.estado_id = ESTADO_RETIRADO; equipo.estado_nombre = 'Retirado'
        mostrarToast(`"${equipo.modelo}" retirado`)
        break
      case 'reactivar':
        await equiposService.reactivarEquipo(equipo.id)
        equipo.estado_id = ESTADO_DISPONIBLE; equipo.estado_nombre = 'Disponible'
        mostrarToast(`"${equipo.modelo}" reactivado`)
        break
      case 'eliminar':
        await equiposService.eliminarEquipo(equipo.id)
        equipos.value = equipos.value.filter(e => e.id !== equipo.id)
        mostrarToast(`"${equipo.modelo}" eliminado permanentemente`)
        break
    }
    confirm.value.visible = false
  } catch (e) {
    mostrarToast(e.response?.data?.detail || 'Error al ejecutar', 'toast-error')
  } finally {
    procesando.value = false
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const getCardClass = (e) => ({
  'card-disponible':    e.estado_id === 1,
  'card-prestado':      e.estado_id === 2,
  'card-mantenimiento': e.estado_id === 3,
  'card-asignado':      e.estado_id === 4,
  'card-retirado':      e.estado_id === 5,
})
const getIndicatorClass = (e) => ({
  'ind-disponible':    e.estado_id === 1,
  'ind-prestado':      e.estado_id === 2,
  'ind-mantenimiento': e.estado_id === 3,
  'ind-asignado':      e.estado_id === 4,
  'ind-retirado':      e.estado_id === 5,
})
const getIconoClass = (e) => ({
  'icono-disponible':    e.estado_id === 1,
  'icono-prestado':      e.estado_id === 2,
  'icono-mantenimiento': e.estado_id === 3,
  'icono-asignado':      e.estado_id === 4,
  'icono-retirado':      e.estado_id === 5,
})
const getChipClass = (e) => ({
  'chip-disponible':    e.estado_id === 1,
  'chip-prestado':      e.estado_id === 2,
  'chip-mantenimiento': e.estado_id === 3,
  'chip-asignado':      e.estado_id === 4,
  'chip-retirado':      e.estado_id === 5,
})

const limpiarFiltros  = () => { filtros.value = { estado_id: '', tipo_equipo_id: '', marca_id: '' }; search.value = ''; pagina.value = 1 }
const toggleRetirados = () => { showRetirados.value = !showRetirados.value; pagina.value = 1 }
const mostrarToast    = (msg, tipo = 'toast-success') => {
  toast.value = { visible: true, msg, tipo }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

watch([search, filtros, soloDisponibles, showRetirados], () => { pagina.value = 1 })
onMounted(() => { cargar(); if (esAdmin.value) cargarCatalogos() })
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

:root {
  --green-dark:   #1a4731; --green-mid:    #2d6a4f;
  --green-light:  #52b788; --green-pale:   #d8f3dc;
  --gold-mid:     #c9900c; --gold-light:   #f4c542;
  --gold-pale:    #fef9e7; --cream:        #f5f0e8;
  --cream-border: #d4e8da; --card-bg:      #fffef9;
  --shadow-sm:    0 2px 12px rgba(26,47,26,.08);
  --shadow-md:    0 8px 24px rgba(26,71,49,.12);
}

.laptops-view { font-family:'DM Sans',sans-serif; min-height:100vh; background:radial-gradient(ellipse 70% 40% at 5% 0%,rgba(82,183,136,.08) 0%,transparent 55%),radial-gradient(ellipse 50% 40% at 90% 100%,rgba(201,144,12,.07) 0%,transparent 50%),var(--cream); }

/* ── Header ──────────────────────────────────────────────────────────────── */
.page-header { background:linear-gradient(135deg,#1a4731 0%,#2d6a4f 60%,#3a7d5e 100%); padding:1.75rem 2rem 1.25rem; position:relative; overflow:hidden; }
.page-header::before { content:''; position:absolute; inset:0; pointer-events:none; background:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E"); }
.header-inner  { display:flex; justify-content:space-between; align-items:flex-start; gap:1.5rem; flex-wrap:wrap; position:relative; }
.header-sup    { font-size:.72rem; font-weight:600; color:rgba(255,255,255,.5); text-transform:uppercase; letter-spacing:.1em; margin-bottom:.2rem; }
.header-titulo { font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700; color:#fff; margin-bottom:.3rem; }
.header-sub    { font-size:.8rem; color:rgba(255,255,255,.65); margin:0; }
.header-acciones { display:flex; gap:.75rem; align-items:center; flex-shrink:0; }
.btn-toggle-inactivos { display:flex; align-items:center; gap:.4rem; padding:.5rem 1rem; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.15); border-radius:8px; color:rgba(255,255,255,.75); font-family:'DM Sans',sans-serif; font-size:.8rem; font-weight:500; cursor:pointer; transition:all .2s; }
.btn-toggle-inactivos:hover,.btn-toggle-on { background:rgba(255,255,255,.18); color:#fff; }
.btn-crear { display:flex; align-items:center; gap:.4rem; padding:.5rem 1.1rem; background:linear-gradient(135deg,var(--gold-light),var(--gold-mid)); border:none; border-radius:8px; color:var(--green-dark); font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:700; cursor:pointer; box-shadow:0 4px 14px rgba(244,197,66,.3); transition:all .2s; }
.btn-crear:hover { transform:translateY(-1px); box-shadow:0 6px 20px rgba(244,197,66,.4); }
.header-stats { display:flex; gap:.75rem; margin-top:1.25rem; flex-wrap:wrap; position:relative; }
.hstat { display:flex; flex-direction:column; align-items:center; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.1); border-radius:9px; padding:.45rem .875rem; min-width:80px; }
.hstat-green { background:rgba(82,183,136,.2); border-color:rgba(82,183,136,.3); }
.hstat-warn  { background:rgba(244,197,66,.15); border-color:rgba(244,197,66,.2); }
.hstat-muted { opacity:.65; }
.hstat-num { font-family:'Playfair Display',serif; font-size:1.2rem; font-weight:700; color:#fff; line-height:1; }
.hstat-green .hstat-num { color:#a7f3d0; }
.hstat-warn  .hstat-num { color:var(--gold-light); }
.hstat-lbl { font-size:.64rem; color:rgba(255,255,255,.55); text-transform:uppercase; letter-spacing:.07em; margin-top:2px; white-space:nowrap; }

/* ── Toolbar ─────────────────────────────────────────────────────────────── */
.toolbar { display:flex; align-items:center; gap:.75rem; padding:1rem 1.5rem; background:var(--card-bg); border-bottom:1.5px solid var(--cream-border); flex-wrap:wrap; }
.search-wrap { display:flex; align-items:center; gap:.5rem; flex:1; min-width:220px; padding:.5rem .75rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:9px; color:#9ab5a0; }
.search-input { flex:1; border:none; background:none; font-family:'DM Sans',sans-serif; font-size:.875rem; color:#1a2e1a; outline:none; }
.search-input::placeholder { color:#9ab5a0; }
.search-clear { background:none; border:none; color:#9ab5a0; cursor:pointer; font-size:1rem; padding:0; }
.search-clear:hover { color:var(--green-dark); }
.filter-select { padding:.5rem .75rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.82rem; color:#3d5a3d; outline:none; cursor:pointer; }
.filter-toggle { display:flex; align-items:center; gap:.4rem; padding:.5rem .875rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:600; color:#5a7a5a; cursor:pointer; transition:all .18s; }
.filter-toggle-on { background:var(--green-pale); color:var(--green-dark); border-color:#b8ddc8; }
.btn-reset { padding:.5rem .875rem; background:none; border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.8rem; color:#5a7a5a; cursor:pointer; white-space:nowrap; transition:all .18s; }
.btn-reset:hover { background:#111; color:#fff; border-color:#111; }

/* ── Contenido ───────────────────────────────────────────────────────────── */
.contenido { padding:1.5rem; }
.estado-c,.estado-e,.estado-v { display:flex; flex-direction:column; align-items:center; padding:3.5rem 2rem; gap:.75rem; text-align:center; }
.estado-c-sm { padding:1.25rem; }
.spinner { width:36px; height:36px; border:3px solid var(--green-pale); border-top-color:var(--green-mid); border-radius:50%; animation:spin .7s linear infinite; }
.spinner-sm { width:20px; height:20px; border-width:2px; }
@keyframes spin { to { transform:rotate(360deg); } }
.estado-c p,.estado-e p { color:#5a7a5a; font-size:.875rem; margin:0; }
.estado-e p { color:#d62828; }
.vacio-ico   { color:#b8ddc8; }
.vacio-titulo{ font-weight:700; color:var(--green-dark); margin:0; }
.vacio-desc  { font-size:.82rem; color:#5a7a5a; margin:0; }
.btn-retry   { padding:.5rem 1.1rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-size:.82rem; font-weight:700; cursor:pointer; }

/* ── Cards ───────────────────────────────────────────────────────────────── */
.cards-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:1.1rem; }

.equipo-card { background:var(--card-bg); border:1.5px solid var(--cream-border); border-radius:16px; padding:1.25rem; display:flex; flex-direction:column; gap:.875rem; box-shadow:var(--shadow-sm); position:relative; overflow:hidden; transition:transform .2s, box-shadow .2s; }
.equipo-card:hover { transform:translateY(-3px); box-shadow:var(--shadow-md); }

.card-disponible    { border-top:3px solid var(--green-light); }
.card-prestado      { border-top:3px solid #f59e0b; }
.card-mantenimiento { border-top:3px solid #60a5fa; }
.card-asignado      { border-top:3px solid #a78bfa; }
.card-retirado      { border-top:3px solid #cbd5e1; opacity:.75; }

.estado-indicator { position:absolute; top:1rem; right:1rem; width:10px; height:10px; border-radius:50%; }
.ind-disponible    { background:var(--green-light); box-shadow:0 0 6px rgba(82,183,136,.5); }
.ind-prestado      { background:#f59e0b; }
.ind-mantenimiento { background:#60a5fa; }
.ind-asignado      { background:#a78bfa; }
.ind-retirado      { background:#cbd5e1; }

.card-top { display:flex; align-items:center; gap:.75rem; flex-wrap:wrap; }
.card-icono { width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.icono-disponible    { background:var(--green-pale); color:var(--green-mid); }
.icono-prestado      { background:#fef3c7; color:#92400e; }
.icono-mantenimiento { background:#dbeafe; color:#1e40af; }
.icono-asignado      { background:#ede9fe; color:#5b21b6; }
.icono-retirado      { background:#f1f5f9; color:#94a3b8; }

.estado-chip { font-size:.68rem; font-weight:700; padding:.2rem .55rem; border-radius:20px; white-space:nowrap; text-transform:uppercase; letter-spacing:.05em; }
.chip-disponible    { background:var(--green-pale); color:var(--green-dark); border:1px solid #b8ddc8; }
.chip-prestado      { background:#fef3c7; color:#92400e; border:1px solid #fcd34d; }
.chip-mantenimiento { background:#dbeafe; color:#1e40af; border:1px solid #bfdbfe; }
.chip-asignado      { background:#ede9fe; color:#5b21b6; border:1px solid #ddd6fe; }
.chip-retirado      { background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; }

.prestable-chip { font-size:.65rem; font-weight:700; padding:.15rem .5rem; border-radius:20px; background:rgba(244,197,66,.15); border:1px solid rgba(244,197,66,.3); color:var(--gold-mid); }

.card-body { flex:1; display:flex; flex-direction:column; gap:.3rem; }
.equipo-serie  { font-family:monospace; font-size:.7rem; color:#9ab5a0; margin:0; }
.equipo-modelo { font-family:'Playfair Display',serif; font-size:.95rem; font-weight:700; color:var(--green-dark); margin:0; }
.equipo-marca  { font-size:.78rem; color:#5a7a5a; margin:0; }
.equipo-detalles { display:flex; flex-direction:column; gap:.25rem; margin-top:.25rem; }
.detalle-row { display:flex; align-items:flex-start; gap:.35rem; font-size:.75rem; color:#64748b; }
.especificaciones { white-space:pre-wrap; line-height:1.4; }

.card-footer { display:flex; gap:.35rem; flex-wrap:wrap; padding-top:.5rem; border-top:1px solid #f1f5f0; margin-top:auto; }

/* ── Paginación ──────────────────────────────────────────────────────────── */
.paginacion { display:flex; justify-content:space-between; align-items:center; padding:.875rem 0; margin-top:1.25rem; font-size:.8rem; color:#5a7a5a; flex-wrap:wrap; gap:.75rem; }
.pag-controles { display:flex; align-items:center; gap:.5rem; }
.pag-btn { padding:.35rem .75rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:7px; font-size:.78rem; font-weight:600; color:var(--green-mid); cursor:pointer; font-family:'DM Sans',sans-serif; transition:all .15s; }
.pag-btn:hover:not(:disabled) { background:#111; color:#fff; border-color:#111; }
.pag-btn:disabled { opacity:.4; cursor:not-allowed; }
.pag-num { padding:.3rem .65rem; border-radius:7px; cursor:pointer; font-size:.8rem; font-weight:500; color:var(--green-mid); transition:all .15s; }
.pag-num:hover     { background:#111; color:#fff; }
.pag-num-active    { background:var(--green-mid); color:#fff; }
.pag-size { display:flex; align-items:center; gap:.5rem; }
.pag-select { padding:.3rem .55rem; border:1.5px solid var(--cream-border); border-radius:7px; font-size:.8rem; color:var(--green-dark); background:#fff; cursor:pointer; }

/* ── Modales ─────────────────────────────────────────────────────────────── */
.modal-overlay { position:fixed; inset:0; background:transparent; display:flex; align-items:center; justify-content:center; z-index:2000; }
.modal-overlay::before { content:''; position:fixed; inset:0; background:rgba(26,47,26,.55); backdrop-filter:blur(8px); z-index:-1; }
.modal { background:var(--card-bg); border-radius:16px; width:90%; max-width:520px; border:1.5px solid var(--cream-border); box-shadow:0 24px 64px rgba(0,0,0,.2); animation:modalIn .25s cubic-bezier(.22,1,.36,1); position:relative; z-index:1; max-height:90vh; overflow-y:auto; }
.modal-sm { max-width:420px; }
@keyframes modalIn { from { opacity:0; transform:translateY(-14px) scale(.97); } to { opacity:1; transform:translateY(0) scale(1); } }
.modal-header { display:flex; justify-content:space-between; align-items:center; padding:1.1rem 1.375rem .875rem; border-bottom:1.5px solid #eef5f0; position:sticky; top:0; background:var(--card-bg); z-index:1; border-radius:16px 16px 0 0; }
.modal-header h3 { font-family:'Playfair Display',serif; font-size:1.05rem; font-weight:700; color:var(--green-dark); margin:0; }
.modal-close { background:none; border:none; font-size:1.3rem; color:#9ab5a0; cursor:pointer; padding:0; }
.modal-close:hover { color:var(--green-dark); }
.modal-body { padding:1.25rem 1.375rem; }
.modal-footer { display:flex; justify-content:flex-end; gap:.625rem; padding:.875rem 1.375rem; border-top:1.5px solid #eef5f0; position:sticky; bottom:0; background:var(--card-bg); border-radius:0 0 16px 16px; }
.form-grid { display:grid; grid-template-columns:1fr 1fr; gap:1rem; }
.form-field { display:flex; flex-direction:column; gap:5px; }
.form-field-full { grid-column:1 / -1; }
.form-label { font-size:.72rem; font-weight:700; color:var(--green-dark); text-transform:uppercase; letter-spacing:.07em; }
.req { color:#d62828; }
.form-input,.form-select { padding:.6rem .75rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.875rem; color:#1a2e1a; outline:none; transition:border-color .2s; box-sizing:border-box; width:100%; }
.form-textarea { resize:vertical; min-height:70px; }
.form-input:focus,.form-select:focus { border-color:var(--green-light); }
.form-error { margin-top:.75rem; padding:.6rem .875rem; background:#fff3f3; border:1px solid #f5c0c0; border-radius:9px; color:#d62828; font-size:.82rem; font-weight:600; }
.tipo-toggle { display:flex; gap:.5rem; }
.toggle-opt { flex:1; padding:.5rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:600; color:#5a7a5a; cursor:pointer; transition:all .2s; }
.toggle-opt-on  { background:var(--green-pale); color:var(--green-dark); border-color:#b8ddc8; }
.toggle-opt-off { background:#fff0f0; color:#b91c1c; border-color:#fca5a5; }
.confirm-msg  { font-size:.875rem; color:#334155; margin-bottom:.75rem; }
.confirm-item { display:flex; flex-direction:column; gap:2px; padding:.75rem; background:var(--cream); border-radius:9px; border-left:3px solid var(--green-light); font-size:.82rem; }
.confirm-item strong { color:var(--green-dark); }
.confirm-item span   { color:#9ab5a0; }
.btn-modal-cancel  { padding:.5rem 1rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:600; color:#5a7a5a; cursor:pointer; }
.btn-modal-confirm { padding:.5rem 1.1rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:.4rem; }
.btn-modal-confirm:hover:not(:disabled) { background:#111; }
.btn-modal-delete  { padding:.5rem 1.1rem; background:#d62828; color:#fff; border:none; border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:.4rem; }
.btn-modal-delete:hover:not(:disabled) { background:#111; }
.btn-modal-cancel:disabled,.btn-modal-confirm:disabled,.btn-modal-delete:disabled { opacity:.5; cursor:not-allowed; }
.spinner-mini { width:12px; height:12px; border:2px solid rgba(255,255,255,.3); border-top-color:#fff; border-radius:50%; animation:spin .6s linear infinite; }

/* ── Toast ───────────────────────────────────────────────────────────────── */
.toast { position:fixed; bottom:2rem; right:2rem; display:flex; align-items:center; gap:.75rem; padding:.75rem 1.1rem; border-radius:10px; font-size:.82rem; font-weight:600; color:#fff; z-index:9999; box-shadow:0 4px 20px rgba(0,0,0,.15); }
.toast-success { background:#16a34a; }
.toast-error   { background:#d62828; }
.toast-close   { background:none; border:none; color:rgba(255,255,255,.75); font-size:1.1rem; cursor:pointer; padding:0; margin-left:auto; }
.toast-close:hover { color:#fff; }
.toast-in-enter-active,.toast-in-leave-active { transition:all .3s ease; }
.toast-in-enter-from,.toast-in-leave-to { opacity:0; transform:translateX(16px); }

@media (max-width:768px) {
  .contenido { padding:1rem; }
  .toolbar { padding:.75rem 1rem; }
  .cards-grid { grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); }
}
</style>