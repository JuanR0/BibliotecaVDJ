<template>
  <div class="mobiliario-management">

    <!-- ══ HEADER ══ -->
    <header class="page-header">
      <div class="header-inner">
        <div class="header-texto">
          <p class="header-sup">Panel de administración</p>
          <h1 class="header-titulo">Gestión de Mobiliario</h1>
          <p class="header-sub">Inventario de mobiliario de la biblioteca</p>
        </div>
        <div class="header-acciones">
          <button class="btn-toggle-inactivos" :class="{ 'btn-toggle-on': showInactivos }" @click="toggleInactivos">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
            </svg>
            {{ showInactivos ? 'Ocultar desactivados' : 'Mostrar desactivados' }}
          </button>
          <button class="btn-crear" @click="abrirModal()">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
            </svg>
            Agregar Mobiliario
          </button>
        </div>
      </div>

      <div class="header-stats">
        <div class="hstat"><span class="hstat-num">{{ stats.total }}</span><span class="hstat-lbl">Total</span></div>
        <div class="hstat"><span class="hstat-num">{{ stats.activos }}</span><span class="hstat-lbl">Activos</span></div>
        <div class="hstat hstat-warn" v-if="stats.reparacion > 0"><span class="hstat-num">{{ stats.reparacion }}</span><span class="hstat-lbl">En reparación</span></div>
        <div class="hstat hstat-muted" v-if="stats.inactivos > 0"><span class="hstat-num">{{ stats.inactivos }}</span><span class="hstat-lbl">Desactivados</span></div>
      </div>
    </header>

    <!-- ══ TOOLBAR ══ -->
    <div class="toolbar">
      <div class="search-wrap">
        <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input v-model="search" type="text" placeholder="Buscar por descripción, área, tipo..." class="search-input"/>
        <button v-if="search" class="search-clear" @click="search = ''">×</button>
      </div>
      <select v-model="filtros.tipo_mobiliario_id" class="filter-select">
        <option value="">Todos los tipos</option>
        <option v-for="t in cat.tipos" :key="t.id" :value="t.id">{{ t.tipo }}</option>
      </select>
      <select v-model="filtros.estado_id" class="filter-select">
        <option value="">Todos los estados</option>
        <option v-for="e in cat.estados" :key="e.id" :value="e.id">{{ e.estado }}</option>
      </select>
      <select v-model="filtros.area_id" class="filter-select" v-if="cat.areas.length">
        <option value="">Todas las áreas</option>
        <option v-for="a in cat.areas" :key="a.id" :value="a.id">{{ a.nombre }}</option>
      </select>
      <select v-model="sortBy" class="filter-select">
        <option value="descripcion">Descripción A-Z</option>
        <option value="reciente">Más recientes</option>
        <option value="tipo">Tipo</option>
        <option value="area">Área</option>
      </select>
      <button v-if="hayFiltros" class="btn-reset" @click="limpiarFiltros">Limpiar filtros</button>
    </div>

    <!-- ══ TABLA ══ -->
    <div class="tabla-section">
      <div v-if="cargando" class="estado-c"><div class="spinner"></div><p>Cargando inventario...</p></div>
      <div v-else-if="errorMsg" class="estado-e"><p>{{ errorMsg }}</p><button class="btn-primary" @click="cargar">Reintentar</button></div>

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
            <tr v-for="item in paginados" :key="item.id" :class="{ 'fila-inactiva': item.estado_id === 4 }">
              <td class="td-id">#{{ item.id }}</td>
              <td>
                <div class="td-desc">{{ item.descripcion }}</div>
                <div class="td-meta">{{ item.usuario_creador_nombre }}</div>
              </td>
              <td><span class="tipo-badge">{{ item.tipo_mobiliario_nombre }}</span></td>
              <td class="td-area">{{ item.area_nombre || 'No asignada' }}</td>
              <td><span class="estado-badge" :class="claseEstado(item)">{{ textoEstado(item) }}</span></td>
              <td><div class="td-fecha">{{ fmt(item.fecha_ingreso) }}</div></td>
              <td>
                <div class="acciones">
                  <button v-if="canEdit" class="tbl-btn tbl-blue" :disabled="procesando" @click="abrirModal(item)" title="Editar">
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                    Editar
                  </button>
                  <button v-if="canDeact && item.estado_id !== 4" class="tbl-btn tbl-gold" style="padding:.3rem .5rem" :disabled="procesando" @click="pedirConfirm(item,'desactivar')" title="Desactivar">
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                  </button>
                  <button v-if="canReact && item.estado_id === 4" class="tbl-btn tbl-green" style="padding:.3rem .5rem" :disabled="procesando" @click="pedirConfirm(item,'reactivar')" title="Reactivar">
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                  </button>
                  <button v-if="canDel && item.estado_id === 4" class="tbl-btn tbl-red" style="padding:.3rem .5rem" :disabled="procesando" @click="pedirConfirm(item,'eliminar')" title="Eliminar">
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="filtrados.length === 0" class="estado-v">
          <svg width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" class="vacio-ico"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
          <p class="vacio-titulo">No se encontró mobiliario</p>
          <p class="vacio-desc">{{ search || hayFiltros ? 'Ajusta los filtros o el término de búsqueda' : 'No hay mobiliario registrado' }}</p>
          <button class="btn-outline" @click="limpiarFiltros">Limpiar filtros</button>
        </div>
      </div>

      <!-- Paginación -->
      <div v-if="!cargando && filtrados.length > 0" class="paginacion">
        <span class="pag-info">{{ desde }}–{{ hasta }} de {{ filtrados.length }}</span>
        <div class="pag-controles">
          <button class="pag-btn" :disabled="pagina === 1" @click="pagina--">← Anterior</button>
          <span v-for="p in paginas" :key="p" class="pag-num" :class="{ 'pag-num-active': p === pagina }" @click="pagina = p">{{ p }}</span>
          <button class="pag-btn" :disabled="pagina === totalPaginas" @click="pagina++">Siguiente →</button>
        </div>
        <div class="pag-size">
          <label>Mostrar</label>
          <select v-model="porPagina" @change="pagina = 1" class="pag-select">
            <option :value="10">10</option><option :value="25">25</option><option :value="50">50</option>
          </select>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════
         MODAL ÚNICO: CREAR / EDITAR
         iasEditing cambia título y acción
    ══════════════════════════════════════ -->
    <div v-if="modal.visible" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ modal.isEditing ? 'Editar Mobiliario' : 'Agregar Mobiliario' }}</h3>
          <button class="modal-close" @click="cerrarModal" :disabled="procesando">×</button>
        </div>

        <div class="modal-body">
          <!-- Info de auditoría (solo en edición) -->
          <div v-if="modal.isEditing && modal.itemOriginal" class="auditoria">
            <div class="audit-row"><span class="audit-lbl">ID</span><span class="audit-val mono">#{{ modal.itemOriginal.id }}</span></div>
            <div class="audit-row"><span class="audit-lbl">Creado por</span><span class="audit-val">{{ modal.itemOriginal.usuario_creador_nombre }}</span></div>
            <div class="audit-row"><span class="audit-lbl">Fecha ingreso</span><span class="audit-val">{{ fmt(modal.itemOriginal.fecha_ingreso) }}</span></div>
          </div>

          <div v-if="cat.cargando" class="estado-c estado-c-sm">
            <div class="spinner spinner-sm"></div><p>Cargando catálogos...</p>
          </div>

          <div v-else class="form-grid">
            <!-- Descripción — span 2 columnas -->
            <div class="form-field form-field-full">
              <label class="form-label">Descripción <span class="req">*</span></label>
              <textarea v-model="modal.form.descripcion" class="form-input form-textarea" rows="3"
                placeholder="Ej: Mesa de lectura rectangular, silla ergonómica..." maxlength="255"></textarea>
              <p class="form-hint">{{ modal.form.descripcion?.length || 0 }}/255 caracteres</p>
            </div>

            <!-- Tipo -->
            <div class="form-field">
              <label class="form-label">Tipo de Mobiliario <span class="req">*</span></label>
              <select v-model="modal.form.tipo_mobiliario_id" class="form-select">
                <option value="" disabled>Selecciona un tipo</option>
                <option v-for="t in cat.tipos" :key="t.id" :value="t.id">{{ t.tipo }}</option>
              </select>
            </div>

            <!-- Estado -->
            <div class="form-field">
              <label class="form-label">Estado <span class="req">*</span></label>
              <select v-model="modal.form.estado_id" class="form-select">
                <option value="" disabled>Selecciona un estado</option>
                <option v-for="e in cat.estados" :key="e.id" :value="e.id">{{ e.estado }}</option>
              </select>
            </div>

            <!-- Área — span 2 columnas -->
            <div class="form-field form-field-full">
              <label class="form-label">Área / Ubicación</label>
              <select v-model="modal.form.area_id" class="form-select">
                <option value="">Sin área asignada</option>
                <option v-for="a in cat.areas" :key="a.id" :value="a.id">{{ a.nombre }}</option>
              </select>
            </div>
          </div>

          <div v-if="modal.error" class="form-error">{{ modal.error }}</div>
        </div>

        <div class="modal-footer">
          <button class="tbl-btn tbl-danger" @click="cerrarModal" :disabled="procesando">Cancelar</button>
          <button class="tbl-btn tbl-green" @click="guardar" :disabled="procesando || cat.cargando">
            <span v-if="procesando" class="spinner-mini"></span>
            {{ procesando ? 'Guardando...' : (modal.isEditing ? 'Guardar Cambios' : 'Crear Mobiliario') }}
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
          <div v-if="confirm.item" class="confirm-item">
            <strong>{{ confirm.item.descripcion }}</strong>
            <span>{{ confirm.item.tipo_mobiliario_nombre }}</span>
            <span>{{ confirm.item.area_nombre || 'Sin área' }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="tbl-btn tbl-danger" @click="cerrarConfirm" :disabled="procesando">Cancelar</button>
          <button class="tbl-btn tbl-green" @click="ejecutarAccion" :disabled="procesando">
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
import { ref, computed, onMounted, watch, reactive } from 'vue'
import { usePermissions } from '@/composables/usePermissions'
import { mobiliarioService } from '@/services/mobiliario'
import '@/styles/buttons.css'

const { hasPermission } = usePermissions()

// ── Permisos ───────────────────────────────────────────────────────────────
const canCreate = computed(() => hasPermission('canCreateFurniture'))
const canEdit   = computed(() => hasPermission('canEditFurniture'))
const canDel    = computed(() => hasPermission('canDeleteFurniture'))
const canReact  = computed(() => hasPermission('canReactivatFurniture'))
const canDeact  = computed(() => hasPermission('canDesactivateFurniture'))

// ── Datos principales ──────────────────────────────────────────────────────
const items    = ref([])
const cargando = ref(false)
const errorMsg = ref(null)
const procesando = ref(false)

// ── Catálogos compartidos (crear Y editar usan los mismos) ─────────────────
const cat = reactive({ tipos: [], estados: [], areas: [], cargando: false })

// ── Filtros / búsqueda / paginación ───────────────────────────────────────
const search  = ref('')
const filtros = ref({ tipo_mobiliario_id: '', estado_id: '', area_id: '' })
const sortBy  = ref('descripcion')
const showInactivos = ref(false)
const pagina   = ref(1)
const porPagina = ref(10)

// ── Modal único (crear + editar) ───────────────────────────────────────────
// isEditing=false → crear    isEditing=true → editar
const modal = ref({
  visible: false,
  isEditing: false,
  itemOriginal: null,    // referencia al item de la lista (para actualizar en sitio)
  error: '',
  form: { descripcion: '', tipo_mobiliario_id: '', estado_id: '', area_id: '' }
})

// ── Modal confirmar acción ─────────────────────────────────────────────────
const confirm = ref({ visible: false, titulo: '', mensaje: '', btnTexto: '', btnClass: '', accion: '', item: null })

// ── Toast ──────────────────────────────────────────────────────────────────
const toast = ref({ visible: false, msg: '', tipo: 'toast-success' })

// ── Computed ───────────────────────────────────────────────────────────────
const filtrados = computed(() => {
  let r = [...items.value]
  if (!showInactivos.value)           r = r.filter(i => i.estado_id !== 4)
  if (filtros.value.tipo_mobiliario_id) r = r.filter(i => i.tipo_mobiliario_id === parseInt(filtros.value.tipo_mobiliario_id))
  if (filtros.value.estado_id)          r = r.filter(i => i.estado_id === parseInt(filtros.value.estado_id))
  if (filtros.value.area_id)            r = r.filter(i => i.area_id === parseInt(filtros.value.area_id))
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    r = r.filter(i => i.descripcion?.toLowerCase().includes(q) || i.area_nombre?.toLowerCase().includes(q) || i.tipo_mobiliario_nombre?.toLowerCase().includes(q))
  }
  r.sort((a, b) => {
    if (sortBy.value === 'reciente') return new Date(b.fecha_ingreso || 0) - new Date(a.fecha_ingreso || 0)
    if (sortBy.value === 'tipo')     return (a.tipo_mobiliario_nombre || '').localeCompare(b.tipo_mobiliario_nombre || '')
    if (sortBy.value === 'area')     return (a.area_nombre || '').localeCompare(b.area_nombre || '')
    return (a.descripcion || '').localeCompare(b.descripcion || '')
  })
  return r
})

const stats = computed(() => ({
  total:     items.value.length,
  activos:   items.value.filter(i => i.estado_id === 1).length,
  reparacion:items.value.filter(i => i.estado_id === 3).length,
  inactivos: items.value.filter(i => i.estado_id === 4).length
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
const hayFiltros   = computed(() => Object.values(filtros.value).some(v => v !== '') || search.value.trim() !== '')

// ── Carga ──────────────────────────────────────────────────────────────────
const cargar = async () => {
  cargando.value = true; errorMsg.value = null
  try {
    const r = await mobiliarioService.getMobiliarios()
    items.value = r?.mobiliarios ?? (Array.isArray(r) ? r : [])
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || 'Error cargando el inventario'
  } finally {
    cargando.value = false
  }
}

const cargarCatalogos = async () => {
  if (cat.tipos.length) return
  cat.cargando = true
  try {
    const [tipos, estados, areasData] = await Promise.all([
    mobiliarioService.getTiposMobiliario(),
    mobiliarioService.getEstadosMobiliario(),
    mobiliarioService.getAreas()
  ])
  cat.tipos   = Array.isArray(tipos) ? tipos : (tipos?.tipos || [])
  cat.estados = Array.isArray(estados) ? estados : (estados?.estados || [])
  cat.areas   = Array.isArray(areasData) ? areasData : (areasData?.areas || [])
  } catch (e) { console.error('Error catálogos:', e) }
  finally { cat.cargando = false }
}

// ── Modal crear / editar ───────────────────────────────────────────────────
// abrirModal() sin argumento → crear
// abrirModal(item)           → editar
const abrirModal = async (item = null) => {
  
  if (item) {
    modal.value = {
      visible: true,
      isEditing: true,
      itemOriginal: item,
      error: '',
      form: {
        descripcion:        item.descripcion,
        tipo_mobiliario_id: item.tipo_mobiliario_id,
        estado_id:          item.estado_id,
        area_id:            item.area_id || ''
      }
    }
  } else {
    modal.value = {
      visible: true,
      isEditing: false,
      itemOriginal: null,
      error: '',
      form: { descripcion: '', tipo_mobiliario_id: '', estado_id: '', area_id: '' }
    }
  }

  // Cargar catálogos después si no están cargados
  if (!cat.tipos.length) {
    await cargarCatalogos()
    // Pre-seleccionar estado activo al crear
    if (!item) {
      const estadoActivo = cat.estados.find(e => (e.estado || '').toLowerCase().includes('en uso'))
      if (estadoActivo) modal.value.form.estado_id = estadoActivo.id
    }
  }
}
const cerrarModal = () => { if (!procesando.value) modal.value.visible = false }

// Validación compartida para crear y editar
const validarForm = () => {
  if (!modal.value.form.descripcion?.trim()) { modal.value.error = 'La descripción es requerida'; return false }
  if (!modal.value.form.tipo_mobiliario_id)  { modal.value.error = 'Selecciona un tipo de mobiliario'; return false }
  if (!modal.value.form.estado_id)           { modal.value.error = 'Selecciona un estado'; return false }
  modal.value.error = ''
  return true
}

const guardar = async () => {
  if (!validarForm()) return
  procesando.value = true
  const payload = {
    descripcion:        modal.value.form.descripcion.trim(),
    tipo_mobiliario_id: parseInt(modal.value.form.tipo_mobiliario_id),
    estado_id:          parseInt(modal.value.form.estado_id),
    area_id:            modal.value.form.area_id ? parseInt(modal.value.form.area_id) : null
  }
  try {
    if (modal.value.isEditing) {
      // EDITAR — actualizar en BD y reflejar en lista sin recargar
      const actualizado = await mobiliarioService.updateMobiliario(modal.value.itemOriginal.id, payload)
      const idx = items.value.findIndex(i => i.id === modal.value.itemOriginal.id)
      if (idx !== -1) Object.assign(items.value[idx], actualizado)
      mostrarToast('Mobiliario actualizado correctamente')
    } else {
      // CREAR — agregar al principio de la lista
      const nuevo = await mobiliarioService.createMobiliario(payload)
      items.value.unshift(nuevo)
      mostrarToast('Mobiliario registrado correctamente')
    }
    modal.value.visible = false
  } catch (e) {
    modal.value.error = e.response?.data?.detail || 'Error al guardar el mobiliario'
  } finally {
    procesando.value = false
  }
}

// ── Modal confirmar ────────────────────────────────────────────────────────
const CFG = {
  desactivar: { titulo: 'Desactivar Mobiliario', mensaje: d => `¿Desactivar "${d}"?`,                        btnTexto: 'Sí, desactivar',            btnClass: 'btn-modal-cancel' },
  reactivar:  { titulo: 'Reactivar Mobiliario',  mensaje: d => `¿Reactivar "${d}"?`,                         btnTexto: 'Sí, reactivar',             btnClass: 'btn-modal-confirm' },
  eliminar:   { titulo: 'Eliminar Mobiliario',   mensaje: d => `¿Eliminar permanentemente "${d}"? No se puede deshacer.`, btnTexto: 'Sí, eliminar permanentemente', btnClass: 'btn-modal-delete' }
}

const pedirConfirm = (item, accion) => {
  const cfg = CFG[accion]
  confirm.value = { visible: true, titulo: cfg.titulo, mensaje: cfg.mensaje(item.descripcion), btnTexto: cfg.btnTexto, btnClass: cfg.btnClass, accion, item }
}
const cerrarConfirm = () => { if (!procesando.value) confirm.value.visible = false }

const ejecutarAccion = async () => {
  const { accion, item } = confirm.value
  if (!item) return
  procesando.value = true
  try {
    switch (accion) {
      case 'desactivar':
        await mobiliarioService.desactivateMobiliario(item.id)
        item.estado_id = 4; item.estado_nombre = 'Desactivado'
        mostrarToast(`"${item.descripcion}" desactivado`)
        break
      case 'reactivar':
        await mobiliarioService.reactivateMobiliario(item.id)
        item.estado_id = 1; item.estado_nombre = 'Activo'
        mostrarToast(`"${item.descripcion}" reactivado`)
        break
      case 'eliminar':
        await mobiliarioService.deleteMobiliario(item.id)
        items.value = items.value.filter(i => i.id !== item.id)
        mostrarToast(`"${item.descripcion}" eliminado permanentemente`)
        break
    }
    confirm.value.visible = false
  } catch (e) {
    mostrarToast(e.response?.data?.detail || 'Error al ejecutar la acción', 'toast-error')
  } finally {
    procesando.value = false
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const ESTADO_CLASS = { 1: 'estado-activo', 2: 'estado-uso', 3: 'estado-reparacion', 4: 'estado-inactivo' }
const ESTADO_TEXT  = { 1: 'Activo', 2: 'En uso', 3: 'En reparacion', 4: 'Desactivado' }
const claseEstado  = i => ESTADO_CLASS[i.estado_id] || ''
const textoEstado = i => {
  const e = cat.estados.find(e => e.id === i.estado_id)
  return e?.estado || 'Desconocido'
}
const fmt = d => d ? new Date(d).toLocaleDateString('es-MX', { year: 'numeric', month: 'short', day: 'numeric' }) : 'N/A'
const limpiarFiltros  = () => { search.value = ''; filtros.value = { tipo_mobiliario_id: '', estado_id: '', area_id: '' }; pagina.value = 1 }
const toggleInactivos = () => { showInactivos.value = !showInactivos.value; pagina.value = 1 }
const mostrarToast = (msg, tipo = 'toast-success') => {
  toast.value = { visible: true, msg, tipo }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

watch([search, filtros, sortBy, showInactivos], () => { pagina.value = 1 })
onMounted(() => { cargar(); cargarCatalogos() })
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
}

.mobiliario-management { font-family:'DM Sans',sans-serif; min-height:100vh; background:radial-gradient(ellipse 70% 40% at 5% 0%,rgba(82,183,136,.08) 0%,transparent 55%),radial-gradient(ellipse 50% 40% at 90% 100%,rgba(201,144,12,.07) 0%,transparent 50%),var(--cream); }

/* ── Header ──────────────────────────────────────────────────────────────── */
.page-header { background:linear-gradient(135deg,#1a4731 0%,#2d6a4f 60%,#3a7d5e 100%); padding:1.75rem 2rem 1.25rem; position:relative; overflow:hidden; }
.page-header::before { content:''; position:absolute; inset:0; pointer-events:none; background:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E"); }
.header-inner { display:flex; justify-content:space-between; align-items:flex-start; gap:1.5rem; flex-wrap:wrap; position:relative; }
.header-sup   { font-size:.72rem; font-weight:600; color:rgba(255,255,255,.5); text-transform:uppercase; letter-spacing:.1em; margin-bottom:.2rem; }
.header-titulo{ font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700; color:#fff; margin-bottom:.3rem; }
.header-sub   { font-size:.8rem; color:rgba(255,255,255,.65); margin:0; }
.header-acciones { display:flex; gap:.75rem; align-items:center; flex-shrink:0; }
.btn-toggle-inactivos { display:flex; align-items:center; gap:.4rem; padding:.5rem 1rem; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.15); border-radius:8px; color:rgba(255,255,255,.75); font-family:'DM Sans',sans-serif; font-size:.8rem; font-weight:500; cursor:pointer; transition:all .2s; }
.btn-toggle-inactivos:hover,.btn-toggle-on { background:rgba(255,255,255,.18); color:#fff; }
.btn-crear { display:flex; align-items:center; gap:.4rem; padding:.5rem 1.1rem; background:linear-gradient(135deg,var(--gold-light),var(--gold-mid)); border:none; border-radius:8px; color:var(--green-dark); font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:700; cursor:pointer; box-shadow:0 4px 14px rgba(244,197,66,.3); transition:all .2s; }
.btn-crear:hover { transform:translateY(-1px); box-shadow:0 6px 20px rgba(244,197,66,.4); }
.header-stats { display:flex; gap:.75rem; margin-top:1.25rem; flex-wrap:wrap; position:relative; }
.hstat { display:flex; flex-direction:column; align-items:center; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.1); border-radius:9px; padding:.45rem .875rem; min-width:80px; }
.hstat-muted { opacity:.65; }
.hstat-warn  { background:rgba(244,197,66,.15); border-color:rgba(244,197,66,.2); }
.hstat-num   { font-family:'Playfair Display',serif; font-size:1.2rem; font-weight:700; color:#fff; line-height:1; }
.hstat-warn .hstat-num { color:var(--gold-light); }
.hstat-lbl   { font-size:.64rem; color:rgba(255,255,255,.55); text-transform:uppercase; letter-spacing:.07em; margin-top:2px; white-space:nowrap; }

/* ── Toolbar ─────────────────────────────────────────────────────────────── */
.toolbar { display:flex; align-items:center; gap:.75rem; padding:1rem 1.5rem; background:var(--card-bg); border-bottom:1.5px solid var(--cream-border); flex-wrap:wrap; }
.search-wrap { display:flex; align-items:center; gap:.5rem; flex:1; min-width:220px; padding:.5rem .75rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:9px; color:#9ab5a0; }
.search-input { flex:1; border:none; background:none; font-family:'DM Sans',sans-serif; font-size:.875rem; color:#1a2e1a; outline:none; }
.search-input::placeholder { color:#9ab5a0; }
.search-clear { background:none; border:none; color:#9ab5a0; cursor:pointer; font-size:1rem; padding:0; }
.search-clear:hover { color:var(--green-dark); }
.filter-select { padding:.5rem .75rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.82rem; color:#3d5a3d; outline:none; cursor:pointer; }
.filter-select:focus { border-color:var(--green-light); }
.btn-reset { padding:.5rem .875rem; background:none; border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.8rem; color:#5a7a5a; cursor:pointer; white-space:nowrap; transition:all .18s; }
.btn-reset:hover { background:#111; color:#fff; border-color:#111; }

/* ── Tabla ───────────────────────────────────────────────────────────────── */
.tabla-section { background:var(--card-bg); border:1.5px solid var(--cream-border); border-radius:0 0 16px 16px; overflow:hidden; box-shadow:var(--shadow-sm); margin:0 1.5rem 1.5rem; }
.tabla-wrap { overflow-x:auto; }
.tabla { width:100%; border-collapse:collapse; font-size:.82rem; }
.tabla thead { background:linear-gradient(135deg,#1a4731,#2d6a4f); }
.tabla thead th { padding:.75rem 1rem; text-align:left; color:rgba(255,255,255,.88); font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.06em; }
.tabla tbody tr { border-bottom:1px solid #f1f5f0; transition:background .15s; }
.tabla tbody tr:last-child { border-bottom:none; }
.tabla tbody tr:hover { background:#fafef8; }
.tabla tbody tr.fila-inactiva { background:#fff8f8; opacity:.8; }
.tabla tbody tr.fila-inactiva:hover { background:#fff0f0; }
.tabla td { padding:.75rem 1rem; vertical-align:middle; color:#334155; }
.td-id   { font-family:monospace; color:#9ab5a0; font-size:.78rem; }
.td-desc { font-weight:600; color:#1a2e1a; }
.td-meta { font-size:.72rem; color:#9ab5a0; margin-top:2px; }
.td-area { font-size:.82rem; color:#475569; }
.td-fecha{ font-size:.78rem; color:#64748b; }
.tipo-badge { display:inline-block; padding:.2rem .6rem; border-radius:20px; font-size:.7rem; font-weight:700; background:#e3f2fd; color:#1565c0; white-space:nowrap; }
.estado-badge { display:inline-block; padding:.2rem .55rem; border-radius:20px; font-size:.7rem; font-weight:700; }
.estado-activo     { background:var(--green-pale); color:var(--green-dark); border:1px solid #b8ddc8; }
.estado-uso        { background:var(--gold-pale);  color:var(--gold-mid);   border:1px solid #fde68a; }
.estado-reparacion { background:#dbeafe; color:#1e3a5f; border:1px solid #bfdbfe; }
.estado-inactivo   { background:#fff0f0; color:#b91c1c; border:1px solid #fca5a5; }
.acciones { display:flex; align-items:center; gap:.35rem; flex-wrap:wrap; }

/* ── Estados vacío/cargando/error ────────────────────────────────────────── */
.estado-c,.estado-e,.estado-v { display:flex; flex-direction:column; align-items:center; padding:3.5rem 2rem; gap:.75rem; text-align:center; }
.estado-c-sm { padding:1.25rem; }
.spinner    { width:36px; height:36px; border:3px solid var(--green-pale); border-top-color:var(--green-mid); border-radius:50%; animation:spin .7s linear infinite; }
.spinner-sm { width:20px; height:20px; border-width:2px; }
@keyframes spin { to { transform:rotate(360deg); } }
.estado-c p,.estado-e p { color:#5a7a5a; font-size:.875rem; margin:0; }
.estado-e p { color:#d62828; }
.vacio-ico   { color:#b8ddc8; }
.vacio-titulo{ font-weight:700; color:var(--green-dark); margin:0; }
.vacio-desc  { font-size:.82rem; color:#5a7a5a; margin:0; }

/* ── Paginación ──────────────────────────────────────────────────────────── */
.paginacion { display:flex; justify-content:space-between; align-items:center; padding:.875rem 1.25rem; border-top:1.5px solid #eef5f0; font-size:.8rem; color:#5a7a5a; flex-wrap:wrap; gap:.75rem; }
.pag-controles { display:flex; align-items:center; gap:.5rem; }
.pag-btn { padding:.35rem .75rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:7px; font-size:.78rem; font-weight:600; color:var(--green-mid); cursor:pointer; font-family:'DM Sans',sans-serif; transition:all .15s; }
.pag-btn:hover:not(:disabled) { background:#111; color:#fff; border-color:#111; }
.pag-btn:disabled { opacity:.4; cursor:not-allowed; }
.pag-num { padding:.3rem .65rem; border-radius:7px; cursor:pointer; font-size:.8rem; font-weight:500; color:var(--green-mid); transition:all .15s; }
.pag-num:hover      { background:#111; color:#fff; }
.pag-num-active     { background:var(--green-mid); color:#fff; }
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
.modal-close { background:none; border:none; font-size:1.3rem; color:#9ab5a0; cursor:pointer; padding:0; line-height:1; transition:color .15s; }
.modal-close:hover { color:var(--green-dark); }
.modal-body { padding:1.25rem 1.375rem; }
.modal-footer { display:flex; justify-content:flex-end; gap:.625rem; padding:.875rem 1.375rem; border-top:1.5px solid #eef5f0; position:sticky; bottom:0; background:var(--card-bg); border-radius:0 0 16px 16px; }

/* Auditoría (solo edición) */
.auditoria { display:grid; grid-template-columns:1fr 1fr 1fr; gap:.5rem; padding:.75rem; background:var(--cream); border-radius:9px; margin-bottom:1rem; }
.audit-row { display:flex; flex-direction:column; gap:2px; }
.audit-lbl { font-size:.65rem; font-weight:700; color:#9ab5a0; text-transform:uppercase; letter-spacing:.06em; }
.audit-val { font-size:.78rem; color:#1a2e1a; font-weight:600; }
.mono      { font-family:monospace; color:var(--green-mid); }

/* Formulario */
.form-grid      { display:grid; grid-template-columns:1fr 1fr; gap:1rem; }
.form-field     { display:flex; flex-direction:column; gap:5px; }
.form-field-full{ grid-column:1 / -1; }
.form-label     { font-size:.72rem; font-weight:700; color:var(--green-dark); text-transform:uppercase; letter-spacing:.07em; }
.req { color:#d62828; }
.form-input,.form-select { padding:.6rem .75rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.875rem; color:#1a2e1a; outline:none; transition:border-color .2s; box-sizing:border-box; width:100%; }
.form-textarea  { resize:vertical; min-height:80px; }
.form-input:focus,.form-select:focus { border-color:var(--green-light); }
.form-hint  { font-size:.7rem; color:#9ab5a0; margin:0; }
.form-error { margin-top:.75rem; padding:.6rem .875rem; background:#fff3f3; border:1px solid #f5c0c0; border-radius:9px; color:#d62828; font-size:.82rem; font-weight:600; }

/* Confirmar */
.confirm-msg  { font-size:.875rem; color:#334155; margin-bottom:.75rem; }
.confirm-item { display:flex; flex-direction:column; gap:2px; padding:.75rem; background:var(--cream); border-radius:9px; border-left:3px solid var(--green-light); font-size:.82rem; }
.confirm-item strong { color:var(--green-dark); }
.confirm-item span   { color:#9ab5a0; }

/* Botones modal (pueden venir de buttons.css o estar aquí para garantía) */
.btn-modal-cancel  { padding:.5rem 1rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:600; color:#5a7a5a; cursor:pointer; transition:all .18s; }
.btn-modal-cancel:hover { background:#f8fafc; }
.btn-modal-cancel:disabled { opacity:.5; cursor:not-allowed; }
.btn-modal-confirm { padding:.5rem 1.1rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:.4rem; transition:background .2s; }
.btn-modal-confirm:hover:not(:disabled) { background:#111; }
.btn-modal-confirm:disabled { opacity:.5; cursor:not-allowed; }
.btn-modal-delete  { padding:.5rem 1.1rem; background:#d62828; color:#fff; border:none; border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:.4rem; transition:background .2s; }
.btn-modal-delete:hover:not(:disabled) { background:#111; }
.btn-modal-delete:disabled { opacity:.5; cursor:not-allowed; }
.btn-primary  { padding:.45rem 1.1rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:700; cursor:pointer; }
.btn-primary:hover { background:#111; }
.btn-outline  { padding:.45rem 1rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:600; color:var(--green-mid); cursor:pointer; transition:all .18s; }
.btn-outline:hover { background:#111; color:#fff; border-color:#111; }
.spinner-mini { width:12px; height:12px; border:2px solid rgba(255,255,255,.3); border-top-color:#fff; border-radius:50%; animation:spin .6s linear infinite; }

/* ── Toast ───────────────────────────────────────────────────────────────── */
.toast { position:fixed; bottom:2rem; right:2rem; display:flex; align-items:center; gap:.75rem; padding:.75rem 1.1rem; border-radius:10px; font-size:.82rem; font-weight:600; color:#fff; z-index:9999; box-shadow:0 4px 20px rgba(0,0,0,.15); }
.toast-success { background:#16a34a; }
.toast-error   { background:#d62828; }
.toast-close   { background:none; border:none; color:rgba(255,255,255,.75); font-size:1.1rem; cursor:pointer; padding:0; line-height:1; margin-left:auto; }
.toast-close:hover { color:#fff; }
.toast-in-enter-active,.toast-in-leave-active { transition:all .3s ease; }
.toast-in-enter-from,.toast-in-leave-to { opacity:0; transform:translateX(16px); }
</style>