<template>
  <div class="gestion-prestamos">

    <!-- ══ HEADER ══ -->
    <header class="page-header">
      <div class="header-inner">
        <div class="header-texto">
          <p class="header-sup">Panel — Bibliotecario</p>
          <h1 class="header-titulo">Préstamos de Equipos</h1>
          <p class="header-sub">Gestiona préstamos de laptops y computadoras</p>
        </div>
        <button class="btn-nuevo" @click="abrirModalCrear">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
          </svg>
          Nuevo Préstamo
        </button>
      </div>
    </header>

    <!-- ══ TABS ══ -->
    <div class="toolbar">
      <div class="tabs">
        <button v-for="tab in tabs" :key="tab.id" class="tab-btn" :class="{ 'tab-active': activeTab === tab.id }" @click="cambiarTab(tab.id)">
          {{ tab.label }}
          <span v-if="tab.count > 0" class="tab-badge" :class="tab.badgeClass">{{ tab.count }}</span>
        </button>
      </div>
      <div class="search-wrap">
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        <input v-model="busqueda" type="text" class="search-input" placeholder="Buscar por estudiante, modelo, serie..."/>
        <button v-if="busqueda" class="search-clear" @click="busqueda = ''">×</button>
      </div>
      <!-- Auto-refresh cada 60s cuando hay vigentes -->
      <div v-if="activeTab !== 'historial'" class="refresh-info">
        <span class="refresh-dot"></span>
        Actualiza automáticamente
      </div>
    </div>

    <!-- ══ TABLA ══ -->
    <div class="tabla-section">
      <div v-if="isLoading" class="estado-c"><div class="spinner"></div><p>Cargando...</p></div>
      <div v-else-if="errorMsg" class="estado-e"><p>{{ errorMsg }}</p><button class="btn-retry" @click="cargar">Reintentar</button></div>
      <div v-else-if="filtrados.length === 0" class="estado-v">
        <svg width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" class="vacio-ico">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
        <p class="vacio-titulo">{{ busqueda ? 'Sin resultados' : activeTab === 'historial' ? 'Sin historial' : 'No hay equipos prestados' }}</p>
      </div>

      <div v-else class="tabla-wrap">
        <table class="tabla">
          <thead>
            <tr>
              <th style="width:55px">ID</th>
              <th>Equipo</th>
              <th style="width:180px">Estudiante</th>
              <th style="width:110px">Inicio</th>
              <th style="width:160px">{{ activeTab === 'historial' ? 'Devuelto' : 'Devolución' }}</th>
              <th style="width:150px">Estado</th>
              <th v-if="activeTab !== 'historial'" style="width:110px">Acción</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in paginados" :key="p.id" :class="getRowClass(p)">
              <td class="td-id">#{{ p.id }}</td>
              <td>
                <div class="td-titulo">{{ p.equipo_modelo }}</div>
                <div class="td-sub">{{ p.equipo_marca }} · {{ p.equipo_tipo }}</div>
                <div class="td-sub mono">{{ p.equipo_numero_serie }}</div>
              </td>
              <td>
                <div class="td-nombre">{{ p.usuario_prestado_nombre }}</div>
                <div class="td-sub">Por: {{ p.usuario_presta_nombre }}</div>
              </td>
              <td class="td-fecha">{{ fmtHora(p.fecha_prestamo) }}</td>
              <td>
                <div class="td-fecha">{{ activeTab === 'historial' ? fmtHora(p.fecha_devolucion) : fmtHora(p.fecha_devolucion) }}</div>
                <div v-if="activeTab !== 'historial'" class="tiempo-info">{{ formatTiempo(p.fecha_devolucion) }}</div>
              </td>
              <td>
                <span class="tiempo-badge" :class="getTiempoBadgeClass(p)">{{ getTiempoBadgeText(p) }}</span>
              </td>
              <td v-if="activeTab !== 'historial'">
                <button class="tbl-btn tbl-green" @click="abrirModalDevolver(p)">
                  <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/></svg>
                  Devolver
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!isLoading && filtrados.length > 0" class="paginacion">
        <span class="pag-info">{{ desde }}–{{ hasta }} de {{ filtrados.length }}</span>
        <div class="pag-controles">
          <button class="pag-btn" :disabled="pagina === 1" @click="pagina--">← Anterior</button>
          <span v-for="pg in paginas" :key="pg" class="pag-num" :class="{ 'pag-num-active': pg === pagina }" @click="pagina = pg">{{ pg }}</span>
          <button class="pag-btn" :disabled="pagina === totalPaginas" @click="pagina++">Siguiente →</button>
        </div>
        <select v-model="porPagina" @change="pagina = 1" class="pag-select">
          <option :value="15">15</option><option :value="30">30</option>
        </select>
      </div>
    </div>

    <!-- ══ MODAL CREAR ══ -->
    <div v-if="modalCrear.visible" class="modal-overlay" @click.self="cerrarModalCrear">
      <div class="modal">
        <div class="modal-header">
          <h3>Registrar Préstamo de Equipo</h3>
          <button class="modal-close" @click="cerrarModalCrear" :disabled="procesando">×</button>
        </div>
        <div class="modal-body">

          <!-- Equipo -->
          <div class="form-field">
            <label class="form-label">Equipo <span class="req">*</span></label>
            <div v-if="!crearForm.equipoSeleccionado">
              <input v-model="crearForm.busquedaEquipo" type="text" class="form-input" placeholder="Buscar por modelo, marca o serie..." @input="buscarEquipos"/>
              <div v-if="buscandoEquipos" class="sug-cargando">Buscando...</div>
              <div v-else-if="equiposSug.length" class="sugerencias">
                <div v-for="e in equiposSug" :key="e.id" class="sug-item" @click="selEquipo(e)">
                  <div class="sug-titulo">{{ e.modelo }} — {{ e.marca_nombre }}</div>
                  <div class="sug-sub">{{ e.numero_serie }} · {{ e.tipo_nombre }}</div>
                </div>
              </div>
              <div v-else-if="crearForm.busquedaEquipo.length >= 2" class="sug-vacio">Sin resultados</div>
            </div>
            <div v-else class="seleccionado">
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" style="flex-shrink:0;color:var(--green-mid)"><path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
              <div class="sel-info">
                <div class="sel-titulo">{{ crearForm.equipoSeleccionado.modelo }} — {{ crearForm.equipoSeleccionado.marca_nombre }}</div>
                <div class="sel-sub">{{ crearForm.equipoSeleccionado.numero_serie }}</div>
              </div>
              <button class="sel-quitar" @click="crearForm.equipoSeleccionado = null; crearForm.busquedaEquipo = ''">×</button>
            </div>
          </div>

          <!-- Estudiante -->
          <div class="form-field">
            <label class="form-label">Estudiante <span class="req">*</span></label>
            <div v-if="!crearForm.usuarioSeleccionado">
              <input v-model="crearForm.busquedaUsuario" type="text" class="form-input" placeholder="Buscar por nombre o código..." @input="buscarUsuarios"/>
              <div v-if="buscandoUsuarios" class="sug-cargando">Buscando...</div>
              <div v-else-if="usuariosSug.length" class="sugerencias">
                <div v-for="u in usuariosSug" :key="u.id" class="sug-item" @click="selUsuario(u)">
                  <div class="sug-titulo">{{ u.nombre_completo }}</div>
                  <div class="sug-sub">{{ u.codigo_universitario }}</div>
                </div>
              </div>
              <div v-else-if="crearForm.busquedaUsuario.length >= 2" class="sug-vacio">Sin resultados</div>
            </div>
            <div v-else class="seleccionado">
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" style="flex-shrink:0;color:var(--green-mid)"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
              <div class="sel-info">
                <div class="sel-titulo">{{ crearForm.usuarioSeleccionado.nombre_completo }}</div>
                <div class="sel-sub">{{ crearForm.usuarioSeleccionado.codigo_universitario }}</div>
              </div>
              <button class="sel-quitar" @click="crearForm.usuarioSeleccionado = null; crearForm.busquedaUsuario = ''">×</button>
            </div>
          </div>

          <!-- Hora de devolución -->
          <div class="form-field">
            <label class="form-label">Devolución esperada <span class="req">*</span></label>
            <input type="datetime-local" v-model="crearForm.fecha_devolucion" class="form-input" :min="ahora"/>
            <p class="form-hint">El equipo se presta por horas — indica la hora de regreso</p>
          </div>

          <div class="form-field">
            <label class="form-label">Observaciones</label>
            <textarea v-model="crearForm.observaciones" class="form-input form-textarea" rows="2" placeholder="Estado del equipo, notas..."></textarea>
          </div>

          <div v-if="modalCrear.error" class="form-error">{{ modalCrear.error }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="cerrarModalCrear" :disabled="procesando">Cancelar</button>
          <button class="btn-modal-confirm" @click="guardarPrestamo" :disabled="procesando">
            <span v-if="procesando" class="spinner-mini"></span>
            {{ procesando ? 'Registrando...' : 'Registrar Préstamo' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══ MODAL DEVOLVER ══ -->
    <div v-if="modalDevolver.visible" class="modal-overlay" @click.self="cerrarModalDevolver">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>Registrar Devolución</h3>
          <button class="modal-close" @click="cerrarModalDevolver" :disabled="procesando">×</button>
        </div>
        <div class="modal-body">
          <div class="resumen-prestamo">
            <div class="rp-row"><span class="rp-lbl">Equipo</span><span class="rp-val">{{ modalDevolver.prestamo?.equipo_modelo }} — {{ modalDevolver.prestamo?.equipo_marca }}</span></div>
            <div class="rp-row"><span class="rp-lbl">Serie</span><span class="rp-val mono">{{ modalDevolver.prestamo?.equipo_numero_serie }}</span></div>
            <div class="rp-row"><span class="rp-lbl">Estudiante</span><span class="rp-val">{{ modalDevolver.prestamo?.usuario_prestado_nombre }}</span></div>
            <div class="rp-row"><span class="rp-lbl">Debía devolver</span><span class="rp-val">{{ fmtHora(modalDevolver.prestamo?.fecha_devolucion) }}</span></div>
          </div>

          <!-- Badge de tiempo al momento de devolver -->
          <div v-if="modalDevolver.prestamo" class="tiempo-actual" :class="'tiempo-actual-' + calcularEstadoTiempo(modalDevolver.prestamo.fecha_devolucion)">
            <strong>{{ getTiempoBadgeText(modalDevolver.prestamo) }}</strong> — {{ formatTiempo(modalDevolver.prestamo.fecha_devolucion) }}
          </div>

          <div class="form-field">
            <label class="form-label">Observaciones</label>
            <textarea v-model="modalDevolver.observaciones" class="form-input form-textarea" rows="2" placeholder="Condición del equipo al devolver..."></textarea>
          </div>
          <div v-if="modalDevolver.error" class="form-error">{{ modalDevolver.error }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="cerrarModalDevolver" :disabled="procesando">Cancelar</button>
          <button class="btn-modal-confirm" @click="confirmarDevolucion" :disabled="procesando">
            <span v-if="procesando" class="spinner-mini"></span>
            {{ procesando ? 'Registrando...' : 'Confirmar Devolución' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <transition name="toast-in">
      <div v-if="toast.visible" class="toast" :class="toast.tipo">
        {{ toast.msg }}
        <button class="toast-close" @click="toast.visible = false">×</button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { prestamoEquipoService, calcularEstadoTiempo, minutosRestantes, formatTiempo } from '@/services/PrestamoRecursos'
import api from '@/services/api'
import '@/styles/buttons.css'

// ── State ──────────────────────────────────────────────────────────────────
const prestamos  = ref([])
const isLoading  = ref(false)
const errorMsg   = ref(null)
const procesando = ref(false)
const busqueda   = ref('')
const activeTab  = ref('vigentes')
const pagina     = ref(1)
const porPagina  = ref(15)

const modalCrear    = ref({ visible: false, error: '' })
const modalDevolver = ref({ visible: false, prestamo: null, observaciones: '', error: '' })
const toast         = ref({ visible: false, msg: '', tipo: 'toast-success' })

const crearForm = ref({ busquedaEquipo: '', equipoSeleccionado: null, busquedaUsuario: '', usuarioSeleccionado: null, fecha_devolucion: '', observaciones: '' })
const equiposSug      = ref([])
const usuariosSug     = ref([])
const buscandoEquipos  = ref(false)
const buscandoUsuarios = ref(false)

// Auto-refresh cada 60s para actualizar badges
let intervalo = null

// ── Tabs ───────────────────────────────────────────────────────────────────
const tabs = computed(() => {
  const vigentes     = prestamos.value.filter(p => p.estado_prestamo_id === 1)
  const enPeligro    = vigentes.filter(p => ['peligro', 'excedido'].includes(calcularEstadoTiempo(p.fecha_devolucion)))
  return [
    { id: 'vigentes',  label: 'Vigentes',  count: vigentes.length,  badgeClass: 'badge-green' },
    { id: 'alertas',   label: 'Alertas',   count: enPeligro.length, badgeClass: 'badge-red' },
    { id: 'historial', label: 'Historial', count: 0, badgeClass: '' },
  ]
})

// ── Computed ───────────────────────────────────────────────────────────────
const filtrados = computed(() => {
  let r = [...prestamos.value]
  if (activeTab.value === 'vigentes') r = r.filter(p => p.estado_prestamo_id === 1 && !['peligro','excedido'].includes(calcularEstadoTiempo(p.fecha_devolucion)))
  if (activeTab.value === 'alertas')  r = r.filter(p => p.estado_prestamo_id === 1 && ['advertencia','peligro','excedido'].includes(calcularEstadoTiempo(p.fecha_devolucion)))

  if (busqueda.value.trim()) {
    const q = busqueda.value.toLowerCase()
    r = r.filter(p =>
      p.equipo_modelo?.toLowerCase().includes(q) ||
      p.equipo_marca?.toLowerCase().includes(q)  ||
      p.equipo_numero_serie?.toLowerCase().includes(q) ||
      p.usuario_prestado_nombre?.toLowerCase().includes(q)
    )
  }
  return r
})

const totalPaginas = computed(() => Math.ceil(filtrados.value.length / porPagina.value) || 1)
const paginados    = computed(() => filtrados.value.slice((pagina.value-1)*porPagina.value, pagina.value*porPagina.value))
const desde        = computed(() => (pagina.value-1)*porPagina.value + 1)
const hasta        = computed(() => Math.min(pagina.value*porPagina.value, filtrados.value.length))
const paginas      = computed(() => {
  const max = 5, tot = totalPaginas.value
  if (tot <= max) return Array.from({length: tot}, (_, i) => i+1)
  let s = Math.max(1, pagina.value-2), e = Math.min(tot, s+max-1)
  if (e-s+1 < max) s = e-max+1
  return Array.from({length: e-s+1}, (_, i) => s+i)
})

const ahora = computed(() => {
  const d = new Date(); d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
})

// ── Helpers visuales ───────────────────────────────────────────────────────
const fmtHora = (d) => d ? new Date(d).toLocaleString('es-MX', { day:'2-digit', month:'short', hour:'2-digit', minute:'2-digit' }) : '—'

const getTiempoBadgeClass = (p) => {
  if (p.estado_prestamo_id === 3) return 'badge-terminado'
  const est = calcularEstadoTiempo(p.fecha_devolucion)
  return { vigente: 'badge-vigente', advertencia: 'badge-advertencia', peligro: 'badge-peligro', excedido: 'badge-excedido' }[est] || ''
}

const getTiempoBadgeText = (p) => {
  if (p.estado_prestamo_id === 3) return 'Terminado'
  const est = calcularEstadoTiempo(p.fecha_devolucion)
  return { vigente: 'Al corriente', advertencia: '⚠ Advertencia', peligro: '🔴 Peligro', excedido: 'Excedió tiempo' }[est] || '—'
}

const getRowClass = (p) => {
  if (p.estado_prestamo_id === 3) return ''
  const est = calcularEstadoTiempo(p.fecha_devolucion)
  return { advertencia: 'fila-advertencia', peligro: 'fila-peligro', excedido: 'fila-excedido' }[est] || ''
}

const mostrarToast = (msg, tipo = 'toast-success') => {
  toast.value = { visible: true, msg, tipo }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

// ── Carga ──────────────────────────────────────────────────────────────────
const cargar = async () => {
  isLoading.value = true; errorMsg.value = null
  try {
    prestamos.value = await (activeTab.value === 'historial'
      ? prestamoEquipoService.getHistorial()
      : prestamoEquipoService.getVigentes())
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || 'Error cargando préstamos'
  } finally { isLoading.value = false }
}

const cambiarTab = async (tab) => { activeTab.value = tab; pagina.value = 1; await cargar() }

// ── Autocomplete ───────────────────────────────────────────────────────────
let timerE, timerU

const buscarEquipos = () => {
  clearTimeout(timerE); equiposSug.value = []
  const q = crearForm.value.busquedaEquipo.trim()
  if (q.length < 2) return
  buscandoEquipos.value = true
  timerE = setTimeout(async () => {
    try {
      const r = await api.get('/api/equipos-computo/', { params: { estado_id: 1, es_prestable: true, por_pagina: 8 } })
      const todos = r.data?.equipos ?? []
      equiposSug.value = todos.filter(e =>
        e.modelo?.toLowerCase().includes(q.toLowerCase()) ||
        e.marca_nombre?.toLowerCase().includes(q.toLowerCase()) ||
        e.numero_serie?.toLowerCase().includes(q.toLowerCase())
      ).slice(0, 8)
    } catch { equiposSug.value = [] }
    finally { buscandoEquipos.value = false }
  }, 350)
}

const buscarUsuarios = () => {
  clearTimeout(timerU); usuariosSug.value = []
  const q = crearForm.value.busquedaUsuario.trim()
  if (q.length < 2) return
  buscandoUsuarios.value = true
  timerU = setTimeout(async () => {
    try {
      const r = await api.get('/api/usuarios/buscar', { params: { q } })
      usuariosSug.value = r.data
    } catch { usuariosSug.value = [] }
    finally { buscandoUsuarios.value = false }
  }, 350)
}

const selEquipo  = (e) => { crearForm.value.equipoSeleccionado = e; crearForm.value.busquedaEquipo = ''; equiposSug.value = [] }
const selUsuario = (u) => { crearForm.value.usuarioSeleccionado = u; crearForm.value.busquedaUsuario = ''; usuariosSug.value = [] }

// ── Modal crear ────────────────────────────────────────────────────────────
const abrirModalCrear = () => {
  crearForm.value = { busquedaEquipo: '', equipoSeleccionado: null, busquedaUsuario: '', usuarioSeleccionado: null, fecha_devolucion: '', observaciones: '' }
  equiposSug.value = []; usuariosSug.value = []
  modalCrear.value = { visible: true, error: '' }
}
const cerrarModalCrear = () => { if (!procesando.value) modalCrear.value.visible = false }

const guardarPrestamo = async () => {
  if (!crearForm.value.equipoSeleccionado)   { modalCrear.value.error = 'Selecciona un equipo'; return }
  if (!crearForm.value.usuarioSeleccionado)  { modalCrear.value.error = 'Selecciona un estudiante'; return }
  if (!crearForm.value.fecha_devolucion)     { modalCrear.value.error = 'Indica la hora de devolución'; return }
  procesando.value = true
  try {
    const nuevo = await prestamoEquipoService.crearPrestamo({
      equipos_computo_id:  crearForm.value.equipoSeleccionado.id,
      usuario_prestado_id: crearForm.value.usuarioSeleccionado.id,
      fecha_devolucion:    crearForm.value.fecha_devolucion,
      observaciones:       crearForm.value.observaciones || null
    })
    if (activeTab.value !== 'historial') prestamos.value.unshift(nuevo)
    modalCrear.value.visible = false
    mostrarToast(`Préstamo de "${crearForm.value.equipoSeleccionado.modelo}" registrado`)
  } catch (e) {
    modalCrear.value.error = e.response?.data?.detail || 'Error al registrar'
  } finally { procesando.value = false }
}

// ── Modal devolver ─────────────────────────────────────────────────────────
const abrirModalDevolver  = (p) => { modalDevolver.value = { visible: true, prestamo: p, observaciones: '', error: '' } }
const cerrarModalDevolver = () => { if (!procesando.value) modalDevolver.value.visible = false }

const confirmarDevolucion = async () => {
  const p = modalDevolver.value.prestamo; if (!p) return
  procesando.value = true
  try {
    await prestamoEquipoService.registrarDevolucion(p.id, modalDevolver.value.observaciones || null)
    prestamos.value = prestamos.value.filter(x => x.id !== p.id)
    modalDevolver.value.visible = false
    mostrarToast(`Equipo "${p.equipo_modelo}" devuelto correctamente`)
  } catch (e) {
    modalDevolver.value.error = e.response?.data?.detail || 'Error al devolver'
  } finally { procesando.value = false }
}

watch([busqueda], () => { pagina.value = 1 })

onMounted(() => {
  cargar()
  // Refrescar cada 60s para actualizar badges de tiempo
  intervalo = setInterval(() => { if (activeTab.value !== 'historial') cargar() }, 60000)
})
onUnmounted(() => clearInterval(intervalo))
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');
:root { --green-dark:#1a4731; --green-mid:#2d6a4f; --green-light:#52b788; --green-pale:#d8f3dc; --gold-mid:#c9900c; --gold-light:#f4c542; --cream:#f5f0e8; --cream-border:#d4e8da; --card-bg:#fffef9; --shadow-sm:0 2px 12px rgba(26,47,26,.08); }

.gestion-prestamos { font-family:'DM Sans',sans-serif; min-height:100vh; background:radial-gradient(ellipse 70% 40% at 5% 0%,rgba(82,183,136,.08) 0%,transparent 55%),radial-gradient(ellipse 50% 40% at 90% 100%,rgba(201,144,12,.07) 0%,transparent 50%),var(--cream); }

.page-header { background:linear-gradient(135deg,#1a4731 0%,#2d6a4f 60%,#3a7d5e 100%); padding:1.75rem 2rem; position:relative; overflow:hidden; }
.page-header::before { content:''; position:absolute; inset:0; pointer-events:none; background:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E"); }
.header-inner { display:flex; justify-content:space-between; align-items:center; gap:1.5rem; flex-wrap:wrap; position:relative; }
.header-sup   { font-size:.72rem; font-weight:600; color:rgba(255,255,255,.5); text-transform:uppercase; letter-spacing:.1em; margin-bottom:.2rem; }
.header-titulo{ font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700; color:#fff; margin-bottom:.3rem; }
.header-sub   { font-size:.8rem; color:rgba(255,255,255,.65); margin:0; }
.btn-nuevo { display:flex; align-items:center; gap:.4rem; padding:.55rem 1.25rem; background:linear-gradient(135deg,var(--gold-light),var(--gold-mid)); border:none; border-radius:8px; color:var(--green-dark); font-family:'DM Sans',sans-serif; font-size:.85rem; font-weight:700; cursor:pointer; box-shadow:0 4px 14px rgba(244,197,66,.3); transition:all .2s; flex-shrink:0; }
.btn-nuevo:hover { transform:translateY(-1px); }

.toolbar { display:flex; align-items:center; gap:1rem; padding:.875rem 1.5rem; background:var(--card-bg); border-bottom:1.5px solid var(--cream-border); flex-wrap:wrap; }
.tabs { display:flex; gap:.375rem; flex-shrink:0; }
.tab-btn { display:flex; align-items:center; gap:.5rem; padding:.45rem .875rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:600; color:#5a7a5a; cursor:pointer; transition:all .18s; }
.tab-btn:hover { background:#111; color:#fff; border-color:#111; }
.tab-active { background:var(--green-mid) !important; color:#fff !important; border-color:var(--green-mid) !important; }
.tab-badge { font-size:.68rem; font-weight:700; padding:.1rem .4rem; border-radius:20px; }
.badge-green { background:rgba(255,255,255,.25); color:#fff; }
.badge-red   { background:rgba(239,68,68,.25); color:#fca5a5; }
.search-wrap { display:flex; align-items:center; gap:.5rem; flex:1; min-width:200px; padding:.5rem .75rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:9px; color:#9ab5a0; }
.search-input { flex:1; border:none; background:none; font-family:'DM Sans',sans-serif; font-size:.875rem; color:#1a2e1a; outline:none; }
.search-input::placeholder { color:#9ab5a0; }
.search-clear { background:none; border:none; color:#9ab5a0; cursor:pointer; font-size:1rem; padding:0; }
.refresh-info { display:flex; align-items:center; gap:.4rem; font-size:.72rem; color:#9ab5a0; white-space:nowrap; }
.refresh-dot  { width:6px; height:6px; border-radius:50%; background:var(--green-light); animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }

.tabla-section { background:var(--card-bg); border:1.5px solid var(--cream-border); border-radius:0 0 16px 16px; overflow:hidden; box-shadow:var(--shadow-sm); margin:0 1.5rem 1.5rem; }
.tabla-wrap { overflow-x:auto; }
.tabla { width:100%; border-collapse:collapse; font-size:.82rem; }
.tabla thead { background:linear-gradient(135deg,#1a4731,#2d6a4f); }
.tabla thead th { padding:.75rem 1rem; text-align:left; color:rgba(255,255,255,.88); font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.06em; }
.tabla tbody tr { border-bottom:1px solid #f1f5f0; transition:background .15s; }
.tabla tbody tr:last-child { border-bottom:none; }
.tabla tbody tr:hover { background:#fafef8; }
.tabla tbody tr.fila-advertencia { background:#fffbeb; }
.tabla tbody tr.fila-peligro     { background:#fff5f5; }
.tabla tbody tr.fila-excedido    { background:#fff0f0; opacity:.85; }
.tabla td { padding:.75rem 1rem; vertical-align:middle; color:#334155; }
.td-id     { font-family:monospace; color:#9ab5a0; font-size:.78rem; }
.td-titulo { font-weight:600; color:#1a2e1a; }
.td-sub    { font-size:.72rem; color:#9ab5a0; margin-top:2px; }
.td-nombre { font-weight:500; color:#334155; }
.td-fecha  { font-size:.8rem; color:#64748b; }
.mono      { font-family:monospace; }
.tiempo-info { font-size:.7rem; color:#9ab5a0; margin-top:2px; }

/* Badges de tiempo */
.tiempo-badge { display:inline-block; padding:.25rem .65rem; border-radius:20px; font-size:.7rem; font-weight:700; white-space:nowrap; }
.badge-vigente     { background:var(--green-pale); color:var(--green-dark); border:1px solid #b8ddc8; }
.badge-advertencia { background:#fef3c7; color:#92400e; border:1px solid #fcd34d; }
.badge-peligro     { background:#fff0f0; color:#b91c1c; border:1px solid #fca5a5; }
.badge-excedido    { background:#fee2e2; color:#991b1b; border:1px solid #f87171; font-style:italic; }
.badge-terminado   { background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; }

/* Banner de tiempo en modal */
.tiempo-actual { padding:.75rem; border-radius:9px; font-size:.82rem; margin-bottom:.5rem; text-align:center; }
.tiempo-actual-vigente     { background:var(--green-pale); color:var(--green-dark); }
.tiempo-actual-advertencia { background:#fef3c7; color:#92400e; }
.tiempo-actual-peligro     { background:#fff0f0; color:#b91c1c; }
.tiempo-actual-excedido    { background:#fee2e2; color:#991b1b; }

.estado-c,.estado-e,.estado-v { display:flex; flex-direction:column; align-items:center; padding:3.5rem 2rem; gap:.75rem; text-align:center; }
.spinner { width:32px; height:32px; border:3px solid var(--green-pale); border-top-color:var(--green-mid); border-radius:50%; animation:spin .7s linear infinite; }
@keyframes spin { to{transform:rotate(360deg)} }
.estado-c p,.estado-e p { color:#5a7a5a; font-size:.875rem; margin:0; }
.vacio-ico   { color:#b8ddc8; }
.vacio-titulo{ font-weight:700; color:var(--green-dark); margin:0; }
.btn-retry   { padding:.5rem 1.1rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-size:.82rem; font-weight:700; cursor:pointer; }

.paginacion { display:flex; justify-content:space-between; align-items:center; padding:.875rem 1.25rem; border-top:1.5px solid #eef5f0; font-size:.8rem; color:#5a7a5a; flex-wrap:wrap; gap:.75rem; }
.pag-controles { display:flex; align-items:center; gap:.5rem; }
.pag-btn { padding:.35rem .75rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:7px; font-size:.78rem; font-weight:600; color:var(--green-mid); cursor:pointer; transition:all .15s; }
.pag-btn:hover:not(:disabled) { background:#111; color:#fff; border-color:#111; }
.pag-btn:disabled { opacity:.4; cursor:not-allowed; }
.pag-num { padding:.3rem .65rem; border-radius:7px; cursor:pointer; font-size:.8rem; font-weight:500; color:var(--green-mid); transition:all .15s; }
.pag-num:hover { background:#111; color:#fff; }
.pag-num-active { background:var(--green-mid); color:#fff; }
.pag-select { padding:.3rem .55rem; border:1.5px solid var(--cream-border); border-radius:7px; font-size:.8rem; color:var(--green-dark); background:#fff; cursor:pointer; }

.modal-overlay { position:fixed; inset:0; background:transparent; display:flex; align-items:center; justify-content:center; z-index:2000; }
.modal-overlay::before { content:''; position:fixed; inset:0; background:rgba(26,47,26,.55); backdrop-filter:blur(8px); z-index:-1; }
.modal { background:var(--card-bg); border-radius:16px; width:90%; max-width:500px; border:1.5px solid var(--cream-border); box-shadow:0 24px 64px rgba(0,0,0,.2); animation:modalIn .25s cubic-bezier(.22,1,.36,1); position:relative; z-index:1; max-height:90vh; overflow-y:auto; }
.modal-sm { max-width:420px; }
@keyframes modalIn { from{opacity:0;transform:translateY(-14px) scale(.97)} to{opacity:1;transform:translateY(0) scale(1)} }
.modal-header { display:flex; justify-content:space-between; align-items:center; padding:1.1rem 1.375rem .875rem; border-bottom:1.5px solid #eef5f0; position:sticky; top:0; background:var(--card-bg); z-index:1; border-radius:16px 16px 0 0; }
.modal-header h3 { font-family:'Playfair Display',serif; font-size:1.05rem; font-weight:700; color:var(--green-dark); margin:0; }
.modal-close { background:none; border:none; font-size:1.3rem; color:#9ab5a0; cursor:pointer; padding:0; }
.modal-body { padding:1.25rem 1.375rem; display:flex; flex-direction:column; gap:.875rem; }
.modal-footer { display:flex; justify-content:flex-end; gap:.625rem; padding:.875rem 1.375rem; border-top:1.5px solid #eef5f0; position:sticky; bottom:0; background:var(--card-bg); border-radius:0 0 16px 16px; }
.form-field { display:flex; flex-direction:column; gap:5px; }
.form-label { font-size:.72rem; font-weight:700; color:var(--green-dark); text-transform:uppercase; letter-spacing:.07em; }
.req { color:#d62828; }
.form-input { padding:.6rem .75rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.875rem; color:#1a2e1a; outline:none; transition:border-color .2s; box-sizing:border-box; width:100%; }
.form-input:focus { border-color:var(--green-light); }
.form-textarea { resize:vertical; min-height:60px; }
.form-hint { font-size:.7rem; color:#9ab5a0; margin:0; }
.form-error { padding:.6rem .875rem; background:#fff3f3; border:1px solid #f5c0c0; border-radius:9px; color:#d62828; font-size:.82rem; font-weight:600; }
.sugerencias { background:#fff; border:1.5px solid var(--cream-border); border-radius:10px; box-shadow:var(--shadow-sm); overflow:hidden; margin-top:.3rem; max-height:220px; overflow-y:auto; }
.sug-item { padding:.625rem .875rem; cursor:pointer; border-bottom:1px solid #f5f5f5; transition:background .15s; }
.sug-item:last-child { border-bottom:none; }
.sug-item:hover { background:var(--green-pale); }
.sug-titulo { font-size:.82rem; font-weight:600; color:#1a2e1a; }
.sug-sub    { font-size:.72rem; color:#9ab5a0; margin-top:1px; }
.sug-vacio,.sug-cargando { font-size:.78rem; color:#9ab5a0; padding:.5rem .875rem; font-style:italic; }
.seleccionado { display:flex; align-items:center; gap:.75rem; padding:.75rem; background:var(--green-pale); border:1px solid #b8ddc8; border-radius:9px; margin-top:.3rem; }
.sel-info { flex:1; min-width:0; }
.sel-titulo { font-size:.82rem; font-weight:600; color:var(--green-dark); }
.sel-sub    { font-size:.72rem; color:#5a7a5a; }
.sel-quitar { background:none; border:none; color:#9ab5a0; cursor:pointer; font-size:1.1rem; flex-shrink:0; padding:0; }
.resumen-prestamo { display:flex; flex-direction:column; gap:.3rem; padding:.875rem; background:var(--cream); border-radius:10px; }
.rp-row { display:flex; gap:.75rem; font-size:.82rem; }
.rp-lbl { color:#9ab5a0; font-weight:600; min-width:110px; flex-shrink:0; }
.rp-val { color:#1a2e1a; font-weight:500; }
.btn-modal-cancel  { padding:.5rem 1rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:600; color:#5a7a5a; cursor:pointer; }
.btn-modal-cancel:disabled { opacity:.5; cursor:not-allowed; }
.btn-modal-confirm { padding:.5rem 1.1rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:.4rem; transition:background .2s; }
.btn-modal-confirm:hover:not(:disabled) { background:#111; }
.btn-modal-confirm:disabled { opacity:.5; cursor:not-allowed; }
.spinner-mini { width:12px; height:12px; border:2px solid rgba(255,255,255,.3); border-top-color:#fff; border-radius:50%; animation:spin .6s linear infinite; }
.toast { position:fixed; bottom:2rem; right:2rem; display:flex; align-items:center; gap:.75rem; padding:.75rem 1.1rem; border-radius:10px; font-size:.82rem; font-weight:600; color:#fff; z-index:9999; box-shadow:0 4px 20px rgba(0,0,0,.15); }
.toast-success { background:#16a34a; }
.toast-error   { background:#d62828; }
.toast-close   { background:none; border:none; color:rgba(255,255,255,.75); font-size:1.1rem; cursor:pointer; padding:0; margin-left:auto; }
.toast-in-enter-active,.toast-in-leave-active { transition:all .3s ease; }
.toast-in-enter-from,.toast-in-leave-to { opacity:0; transform:translateX(16px); }
</style>