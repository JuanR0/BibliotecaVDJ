<template>
  <div class="solicitudes-areas">

    <!-- ══ HEADER ══ -->
    <header class="page-header">
      <div class="header-inner">
        <div class="header-texto">
          <p class="header-sup">Panel de administración</p>
          <h1 class="header-titulo">Solicitudes de Áreas</h1>
          <p class="header-sub">Aprueba o rechaza las reservas solicitadas por estudiantes</p>
        </div>
        <div class="header-stats">
          <div class="hstat hstat-pending">
            <span class="hstat-num">{{ solicitudes.length }}</span>
            <span class="hstat-lbl">Pendientes</span>
          </div>
          <button class="btn-refresh" @click="cargar" title="Refrescar">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- ══ TOOLBAR ══ -->
    <div class="toolbar">
      <div class="search-wrap">
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input v-model="busqueda" type="text" placeholder="Buscar por usuario o área..." class="search-input"/>
        <button v-if="busqueda" class="search-clear" @click="busqueda = ''">×</button>
      </div>
    </div>

    <!-- ══ TABLA ══ -->
    <div class="tabla-section">

      <div v-if="isLoading" class="estado-loading">
        <div class="spinner"></div>
        <p>Cargando solicitudes...</p>
      </div>

      <div v-else-if="error" class="estado-error">
        <p>{{ error }}</p>
        <button class="btn-primary" @click="cargar">Reintentar</button>
      </div>

      <div v-else-if="solicitudesFiltradas.length === 0" class="estado-vacio">
        <svg width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" class="vacio-ico">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p class="vacio-titulo">Sin solicitudes pendientes</p>
        <p class="vacio-desc">Todas las solicitudes han sido procesadas</p>
      </div>

      <div v-else class="tabla-wrap">
        <table class="tabla">
          <thead>
            <tr>
              <th>Estudiante</th>
              <th>Área</th>
              <th>Capacidad</th>
              <th>Hasta</th>
              <th>Solicitado</th>
              <th style="width:180px">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in solicitudesFiltradas" :key="s.id">
              <td>
                <div class="td-nombre">{{ s.usuario_prestado_nombre }}</div>
              </td>
              <td>
                <div class="td-area">{{ s.area_nombre }}</div>
              </td>
              <td class="td-cap">{{ s.area_capacidad || 'N/A' }} pers.</td>
              <td class="td-fecha">{{ formatFecha(s.fecha_devolucion_esperada) }}</td>
              <td class="td-fecha">{{ formatFecha(s.fecha_prestamo) }}</td>
              <td>
                <div class="acciones">
                  <button
                    class="btn-aprobar"
                    :disabled="procesandoId === s.id"
                    @click="abrirModalAprobar(s)"
                  >
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                    </svg>
                    Aprobar
                  </button>
                  <button
                    class="tbl-btn tbl-red"
                    style="padding:.3rem .5rem"
                    :disabled="procesandoId === s.id"
                    @click="abrirModalRechazar(s)"
                    title="Rechazar"
                  >
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ══ MODAL APROBAR ══ -->
    <div v-if="modal.visible && modal.tipo === 'aprobar'" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>Aprobar Reserva</h3>
          <button class="modal-close" @click="cerrarModal" :disabled="procesandoId !== null">×</button>
        </div>
        <div class="modal-body">
          <div class="modal-info">
            <div class="mi-row">
              <span class="mi-label">Estudiante</span>
              <span class="mi-valor">{{ modal.solicitud?.usuario_prestado_nombre }}</span>
            </div>
            <div class="mi-row">
              <span class="mi-label">Área</span>
              <span class="mi-valor">{{ modal.solicitud?.area_nombre }}</span>
            </div>
            <div class="mi-row">
              <span class="mi-label">Hasta</span>
              <span class="mi-valor">{{ formatFecha(modal.solicitud?.fecha_devolucion_esperada) }}</span>
            </div>
          </div>
          <div class="aprobacion-aviso">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <p>Al aprobar, el área pasará a estado <strong>Ocupada</strong> y el estudiante podrá utilizarla.</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="cerrarModal" :disabled="procesandoId !== null">Cancelar</button>
          <button class="btn-aprobar-modal" @click="confirmarAprobar" :disabled="procesandoId !== null">
            <span v-if="procesandoId !== null" class="spinner-mini"></span>
            {{ procesandoId !== null ? 'Procesando...' : '✓ Confirmar Aprobación' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══ MODAL RECHAZAR ══ -->
    <div v-if="modal.visible && modal.tipo === 'rechazar'" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>Rechazar Solicitud</h3>
          <button class="modal-close" @click="cerrarModal" :disabled="procesandoId !== null">×</button>
        </div>
        <div class="modal-body">
          <div class="modal-info">
            <div class="mi-row">
              <span class="mi-label">Estudiante</span>
              <span class="mi-valor">{{ modal.solicitud?.usuario_prestado_nombre }}</span>
            </div>
            <div class="mi-row">
              <span class="mi-label">Área</span>
              <span class="mi-valor">{{ modal.solicitud?.area_nombre }}</span>
            </div>
          </div>
          <div class="rechazo-aviso">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <p>El área volverá a estado <strong>Disponible</strong> y el estudiante podrá solicitar de nuevo.</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="cerrarModal" :disabled="procesandoId !== null">Cancelar</button>
          <button class="btn-modal-delete" @click="confirmarRechazar" :disabled="procesandoId !== null">
            <span v-if="procesandoId !== null" class="spinner-mini"></span>
            {{ procesandoId !== null ? 'Procesando...' : 'Sí, rechazar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══ TOAST ══ -->
    <transition name="toast-in">
      <div v-if="toast.visible" class="toast" :class="toast.tipo">
        {{ toast.mensaje }}
        <button class="toast-close" @click="toast.visible = false">×</button>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { prestamoAreasService } from '@/services/prestamoAreas'

import '@/styles/buttons.css'

// ── State ──────────────────────────────────────────────────────────────────
const solicitudes  = ref([])
const isLoading    = ref(false)
const error        = ref(null)
const busqueda     = ref('')
const procesandoId = ref(null)

const modal = ref({ visible: false, tipo: '', solicitud: null })
const toast = ref({ visible: false, mensaje: '', tipo: '' })

// ── Computed ───────────────────────────────────────────────────────────────
const solicitudesFiltradas = computed(() => {
  if (!busqueda.value.trim()) return solicitudes.value
  const q = busqueda.value.toLowerCase()
  return solicitudes.value.filter(s =>
    s.usuario_prestado_nombre?.toLowerCase().includes(q) ||
    s.area_nombre?.toLowerCase().includes(q)
  )
})

// ── Carga ──────────────────────────────────────────────────────────────────
const cargar = async () => {
  isLoading.value = true; error.value = null
  try {
    solicitudes.value = await prestamoAreasService.getPendientes()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error cargando solicitudes'
  } finally {
    isLoading.value = false
  }
}

// ── Modales ────────────────────────────────────────────────────────────────
const abrirModalAprobar  = (s) => { modal.value = { visible: true, tipo: 'aprobar', solicitud: s } }
const abrirModalRechazar = (s) => { modal.value = { visible: true, tipo: 'rechazar', solicitud: s } }
const cerrarModal = () => { if (!procesandoId.value) modal.value.visible = false }

const confirmarAprobar = async () => {
  const s = modal.value.solicitud
  if (!s) return
  procesandoId.value = s.id
  try {
    await prestamoAreasService.aprobarSolicitud(s.id)
    solicitudes.value = solicitudes.value.filter(x => x.id !== s.id)
    modal.value.visible = false
    mostrarToast(`Reserva aprobada — ${s.usuario_prestado_nombre} puede usar ${s.area_nombre}`)
  } catch (err) {
    mostrarToast(err.response?.data?.detail || 'Error al aprobar', 'toast-error')
  } finally {
    procesandoId.value = null
  }
}

const confirmarRechazar = async () => {
  const s = modal.value.solicitud
  if (!s) return
  procesandoId.value = s.id
  try {
    await prestamoAreasService.rechazarSolicitud(s.id)
    solicitudes.value = solicitudes.value.filter(x => x.id !== s.id)
    modal.value.visible = false
    mostrarToast(`Solicitud rechazada — ${s.area_nombre} vuelve a estar disponible`)
  } catch (err) {
    mostrarToast(err.response?.data?.detail || 'Error al rechazar', 'toast-error')
  } finally {
    procesandoId.value = null
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const formatFecha = (d) => {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-MX', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

const mostrarToast = (mensaje, tipo = 'toast-success') => {
  toast.value = { visible: true, mensaje, tipo }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

onMounted(cargar)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

:root {
  --green-dark:   #1a4731;
  --green-mid:    #2d6a4f;
  --green-light:  #52b788;
  --green-pale:   #d8f3dc;
  --gold-mid:     #c9900c;
  --gold-light:   #f4c542;
  --cream:        #f5f0e8;
  --cream-border: #d4e8da;
  --card-bg:      #fffef9;
  --shadow-sm:    0 2px 12px rgba(26,47,26,.08);
}

.solicitudes-areas {
  font-family: 'DM Sans', sans-serif; min-height: 100vh;
  background:
    radial-gradient(ellipse 70% 40% at 5% 0%, rgba(82,183,136,.08) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 90% 100%, rgba(201,144,12,.07) 0%, transparent 50%),
    var(--cream);
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.page-header { background: linear-gradient(135deg, #1a4731 0%, #2d6a4f 60%, #3a7d5e 100%); padding: 1.75rem 2rem 1.25rem; position: relative; overflow: hidden; }
.page-header::before { content: ''; position: absolute; inset: 0; pointer-events: none; background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E"); }
.header-inner  { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; position: relative; }
.header-sup    { font-size: .72rem; font-weight: 600; color: rgba(255,255,255,.5); text-transform: uppercase; letter-spacing: .1em; margin-bottom: .2rem; }
.header-titulo { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: #fff; margin-bottom: .25rem; }
.header-sub    { font-size: .8rem; color: rgba(255,255,255,.6); margin: 0; }
.header-stats  { display: flex; align-items: center; gap: .75rem; flex-shrink: 0; }
.hstat { display: flex; flex-direction: column; align-items: center; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.12); border-radius: 10px; padding: .5rem .875rem; min-width: 60px; }
.hstat-pending { background: rgba(99,102,241,.2); border-color: rgba(99,102,241,.3); }
.hstat-num { font-family: 'Playfair Display', serif; font-size: 1.3rem; font-weight: 700; color: #a5b4fc; line-height: 1; }
.hstat-lbl { font-size: .65rem; color: rgba(255,255,255,.55); text-transform: uppercase; letter-spacing: .07em; margin-top: 2px; }
.btn-refresh { width: 34px; height: 34px; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.12); border-radius: 8px; color: rgba(255,255,255,.7); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all .2s; }
.btn-refresh:hover { background: rgba(255,255,255,.18); color: #fff; }

/* ── Toolbar ─────────────────────────────────────────────────────────────── */
.toolbar { display: flex; align-items: center; gap: .75rem; padding: 1rem 1.5rem; background: var(--card-bg); border-bottom: 1.5px solid var(--cream-border); }
.search-wrap { display: flex; align-items: center; gap: .5rem; flex: 1; max-width: 360px; padding: .5rem .75rem; background: var(--cream); border: 1.5px solid var(--cream-border); border-radius: 9px; color: #9ab5a0; }
.search-input { flex: 1; border: none; background: none; font-family: 'DM Sans', sans-serif; font-size: .875rem; color: #1a2e1a; outline: none; }
.search-input::placeholder { color: #9ab5a0; }
.search-clear { background: none; border: none; color: #9ab5a0; cursor: pointer; font-size: 1rem; padding: 0; }
.search-clear:hover { color: var(--green-dark); }

/* ── Tabla ───────────────────────────────────────────────────────────────── */
.tabla-section { background: var(--card-bg); border: 1.5px solid var(--cream-border); border-radius: 0 0 16px 16px; overflow: hidden; box-shadow: var(--shadow-sm); margin: 0 1.5rem 1.5rem; }
.tabla-wrap { overflow-x: auto; }
.tabla { width: 100%; border-collapse: collapse; font-size: .82rem; }
.tabla thead { background: linear-gradient(135deg, #1a4731, #2d6a4f); }
.tabla thead th { padding: .75rem 1rem; text-align: left; color: rgba(255,255,255,.88); font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; }
.tabla tbody tr { border-bottom: 1px solid #f1f5f0; transition: background .15s; }
.tabla tbody tr:last-child { border-bottom: none; }
.tabla tbody tr:hover { background: #fafef8; }
.tabla td { padding: .75rem 1rem; vertical-align: middle; color: #334155; }
.td-nombre { font-weight: 600; color: #1a2e1a; }
.td-area   { color: #475569; }
.td-cap    { color: #64748b; font-size: .78rem; }
.td-fecha  { font-size: .78rem; color: #64748b; white-space: nowrap; }
.acciones  { display: flex; align-items: center; gap: .35rem; }

.btn-aprobar { padding: .35rem .875rem; background: var(--green-mid); color: #fff; border: none; border-radius: 8px; font-size: .78rem; font-weight: 700; cursor: pointer; white-space: nowrap; display: inline-flex; align-items: center; gap: .3rem; transition: background .2s; }
.btn-aprobar:hover:not(:disabled) { background: #111; }
.btn-aprobar:disabled { opacity: .5; cursor: not-allowed; }

/* ── Estados ─────────────────────────────────────────────────────────────── */
.estado-loading, .estado-error, .estado-vacio { display: flex; flex-direction: column; align-items: center; padding: 3.5rem 2rem; gap: .75rem; text-align: center; }
.spinner { width: 32px; height: 32px; border: 3px solid var(--green-pale); border-top-color: var(--green-mid); border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.estado-loading p, .estado-error p { color: #5a7a5a; font-size: .875rem; margin: 0; }
.estado-error p { color: #d62828; }
.vacio-ico    { color: #b8ddc8; }
.vacio-titulo { font-weight: 700; color: var(--green-dark); margin: 0; }
.vacio-desc   { font-size: .82rem; color: #5a7a5a; margin: 0; }

/* ── Modal ───────────────────────────────────────────────────────────────── */
.modal-overlay { position: fixed; inset: 0; background: transparent; display: flex; align-items: center; justify-content: center; z-index: 2000; }
.modal-overlay::before { content: ''; position: fixed; inset: 0; background: rgba(26,47,26,.55); backdrop-filter: blur(8px); z-index: -1; }
.modal { background: var(--card-bg); border-radius: 16px; width: 90%; max-width: 420px; border: 1.5px solid var(--cream-border); box-shadow: 0 24px 64px rgba(0,0,0,.2); animation: modalIn .25s cubic-bezier(.22,1,.36,1); position: relative; z-index: 1; }
.modal-sm { max-width: 400px; }
@keyframes modalIn { from { opacity: 0; transform: translateY(-14px) scale(.97); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.1rem 1.375rem .875rem; border-bottom: 1.5px solid #eef5f0; }
.modal-header h3 { font-family: 'Playfair Display', serif; font-size: 1.05rem; font-weight: 700; color: var(--green-dark); margin: 0; }
.modal-close { background: none; border: none; font-size: 1.3rem; color: #9ab5a0; cursor: pointer; padding: 0; line-height: 1; }
.modal-close:hover { color: var(--green-dark); }
.modal-body { padding: 1.25rem 1.375rem; display: flex; flex-direction: column; gap: 1rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: .625rem; padding: .875rem 1.375rem; border-top: 1.5px solid #eef5f0; }

.modal-info { display: flex; flex-direction: column; gap: .4rem; background: var(--cream); padding: .875rem; border-radius: 10px; }
.mi-row   { display: flex; gap: .75rem; font-size: .82rem; }
.mi-label { font-weight: 700; color: #9ab5a0; min-width: 80px; }
.mi-valor { color: #1a2e1a; }

.aprobacion-aviso { display: flex; gap: .625rem; padding: .75rem; background: var(--green-pale); border: 1px solid #b8ddc8; border-radius: 9px; font-size: .82rem; color: var(--green-dark); align-items: flex-start; }
.aprobacion-aviso p { margin: 0; line-height: 1.5; }

.rechazo-aviso { display: flex; gap: .625rem; padding: .75rem; background: #fff3f3; border: 1px solid #f5c0c0; border-radius: 9px; font-size: .82rem; color: #6b3333; align-items: flex-start; }
.rechazo-aviso svg { color: #d62828; flex-shrink: 0; margin-top: 2px; }
.rechazo-aviso p { margin: 0; line-height: 1.5; }

/* Botones modal — de buttons.css excepto btn-aprobar-modal */
.btn-modal-cancel { padding: .5rem 1rem; background: #fff; border: 1.5px solid var(--cream-border); border-radius: 8px; font-family: 'DM Sans', sans-serif; font-size: .82rem; font-weight: 600; color: #5a7a5a; cursor: pointer; transition: all .18s; }
.btn-modal-cancel:hover { background: #f8fafc; }
.btn-modal-cancel:disabled { opacity: .5; cursor: not-allowed; }

.btn-aprobar-modal { padding: .5rem 1.1rem; background: var(--green-mid); color: #fff; border: none; border-radius: 8px; font-family: 'DM Sans', sans-serif; font-size: .82rem; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: .4rem; transition: background .2s; }
.btn-aprobar-modal:hover:not(:disabled) { background: #111; }
.btn-aprobar-modal:disabled { opacity: .5; cursor: not-allowed; }

.btn-modal-delete { padding: .5rem 1.1rem; background: #d62828; color: #fff; border: none; border-radius: 8px; font-family: 'DM Sans', sans-serif; font-size: .82rem; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: .4rem; transition: background .2s; }
.btn-modal-delete:hover:not(:disabled) { background: #111; }
.btn-modal-delete:disabled { opacity: .5; cursor: not-allowed; }

.spinner-mini { width: 12px; height: 12px; border: 2px solid rgba(255,255,255,.3); border-top-color: #fff; border-radius: 50%; animation: spin .6s linear infinite; }

/* ── Toast ───────────────────────────────────────────────────────────────── */
.toast { position: fixed; bottom: 2rem; right: 2rem; display: flex; align-items: center; gap: .75rem; padding: .75rem 1.1rem; border-radius: 10px; font-size: .82rem; font-weight: 600; color: #fff; z-index: 9999; box-shadow: 0 4px 20px rgba(0,0,0,.15); }
.toast-success { background: #16a34a; }
.toast-error   { background: #d62828; }
.toast-close   { background: none; border: none; color: rgba(255,255,255,.75); font-size: 1.1rem; cursor: pointer; padding: 0; }
.toast-close:hover { color: #fff; }
.toast-in-enter-active, .toast-in-leave-active { transition: all .3s ease; }
.toast-in-enter-from, .toast-in-leave-to { opacity: 0; transform: translateX(16px); }
</style>