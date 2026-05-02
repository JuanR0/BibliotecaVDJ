<template>
  <div class="devoluciones-admin">

    <!-- ══ HEADER ══ -->
    <header class="page-header">
      <div class="header-inner">
        <div class="header-texto">
          <p class="header-sup">Panel de administración</p>
          <h1 class="header-titulo">Devoluciones Pendientes</h1>
          <p class="header-sub">Aprueba las solicitudes de devolución de libros</p>
        </div>
        <div class="header-stats">
          <div class="hstat hstat-pending">
            <span class="hstat-num">{{ prestamos.length }}</span>
            <span class="hstat-lbl">En espera</span>
          </div>
          <button class="btn-refresh" @click="cargar" title="Refrescar">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- ══ BUSCADOR POR TICKET (CID) ══ -->
    <div class="ticket-search-bar">
      <div class="ticket-search-wrap">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"/>
        </svg>
        <input
          v-model="busquedaTicket"
          type="number"
          placeholder="Ingresar número de ticket del estudiante..."
          class="ticket-input"
          @keyup.enter="buscarPorTicket"
        />
        <button class="btn-buscar-ticket" @click="buscarPorTicket" :disabled="buscandoTicket">
          {{ buscandoTicket ? 'Buscando...' : 'Buscar ticket' }}
        </button>
      </div>
      <p class="ticket-hint">El estudiante presenta su número de ticket al llegar al CID</p>
    </div>

    <!-- Resultado búsqueda por ticket -->
    <div v-if="resultadoTicket" class="resultado-ticket">
      <div class="resultado-header">
        <span class="resultado-titulo">Préstamo encontrado — Ticket #{{ resultadoTicket.numero_ticket }}</span>
        <button class="btn-limpiar" @click="resultadoTicket = null">× Limpiar</button>
      </div>
      <div class="resultado-body">
        <div class="resultado-info">
          <div class="ri-row">
            <span class="ri-label">Estudiante</span>
            <span class="ri-valor">{{ resultadoTicket.usuario_prestado_nombre }}</span>
          </div>
          <div class="ri-row">
            <span class="ri-label">Libro</span>
            <span class="ri-valor">{{ resultadoTicket.libro_titulo }}</span>
          </div>
          <div class="ri-row">
            <span class="ri-label">Fecha esperada</span>
            <span class="ri-valor">{{ formatDate(resultadoTicket.fecha_devolucion_esperada) }}</span>
          </div>
          <div class="ri-row">
            <span class="ri-label">Solicitud enviada</span>
            <span class="ri-valor">{{ formatDate(resultadoTicket.fecha_solicitud_dev) }}</span>
          </div>
          <div class="ri-row">
            <span class="ri-label">Días de retraso</span>
            <span class="ri-valor" :class="calcularDias(resultadoTicket) > 0 ? 'valor-danger' : 'valor-ok'">
              {{ calcularDias(resultadoTicket) > 0
                ? `${calcularDias(resultadoTicket)} día(s) — multa: $${(calcularDias(resultadoTicket) * 5).toFixed(2)} MXN`
                : 'Sin retraso' }}
            </span>
          </div>
        </div>
        <button
          class="btn-aprobar-ticket"
          @click="abrirModalAprobar(resultadoTicket)"
          :disabled="aprobandoId === resultadoTicket.id"
        >
          ✓ Aprobar devolución
        </button>
      </div>
    </div>

    <!-- ══ LISTA DE PENDIENTES ══ -->
    <div class="lista-section">

      <div class="lista-toolbar">
        <div class="search-wrap">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <input v-model="busqueda" type="text"
            placeholder="Buscar por usuario o libro..." class="search-input"/>
        </div>
      </div>

      <div v-if="isLoading" class="estado-loading">
        <div class="spinner"></div>
        <p>Cargando solicitudes...</p>
      </div>

      <div v-else-if="error" class="estado-error">
        <p>{{ error }}</p>
        <button class="btn-retry" @click="cargar">Reintentar</button>
      </div>

      <div v-else-if="prestamosFiltrados.length === 0" class="estado-vacio">
        <div class="vacio-ico">
          <svg width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <p class="vacio-titulo">Sin devoluciones pendientes</p>
        <p class="vacio-desc">Todas las solicitudes han sido procesadas</p>
      </div>

      <div v-else class="tabla-wrap">
        <table class="tabla">
          <thead>
            <tr>
              <th>Ticket</th>
              <th>Estudiante</th>
              <th>Libro</th>
              <th>Fecha esperada</th>
              <th>Solicitud enviada</th>
              <th>Retraso estimado</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in prestamosFiltrados" :key="p.id">
              <td>
                <span class="td-ticket">{{ p.numero_ticket || '—' }}</span>
              </td>
              <td class="td-usuario">{{ p.usuario_prestado_nombre }}</td>
              <td class="td-libro">{{ p.libro_titulo }}</td>
              <td class="td-fecha">{{ formatDate(p.fecha_devolucion_esperada) }}</td>
              <td class="td-fecha">{{ formatDate(p.fecha_solicitud_dev) }}</td>
              <td>
                <span
                  class="retraso-badge"
                  :class="calcularDias(p) > 0 ? 'retraso-si' : 'retraso-no'"
                >
                  {{ calcularDias(p) > 0
                    ? `${calcularDias(p)}d — $${(calcularDias(p) * 5).toFixed(2)}`
                    : 'A tiempo' }}
                </span>
              </td>
              <td>
                <button
                  class="btn-aprobar"
                  @click="abrirModalAprobar(p)"
                  :disabled="aprobandoId === p.id"
                >
                  {{ aprobandoId === p.id ? 'Procesando...' : '✓ Aprobar' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ══ MODAL APROBAR ══ -->
    <div v-if="modalAprobar.visible" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Aprobar Devolución</h3>
          <button class="modal-close" @click="cerrarModal" :disabled="aprobandoId !== null">×</button>
        </div>

        <div class="modal-body">
          <div class="modal-info-rows">
            <div class="mi-row">
              <span class="mi-label">Estudiante</span>
              <span class="mi-valor">{{ modalAprobar.prestamo?.usuario_prestado_nombre }}</span>
            </div>
            <div class="mi-row">
              <span class="mi-label">Libro</span>
              <span class="mi-valor">{{ modalAprobar.prestamo?.libro_titulo }}</span>
            </div>
            <div class="mi-row">
              <span class="mi-label">Ticket</span>
              <span class="mi-valor mono">#{{ modalAprobar.prestamo?.numero_ticket }}</span>
            </div>
            <div class="mi-row">
              <span class="mi-label">Solicitud</span>
              <span class="mi-valor">{{ formatDate(modalAprobar.prestamo?.fecha_solicitud_dev) }}</span>
            </div>
          </div>

          <!-- Alerta de multa si hay retraso -->
          <div v-if="modalAprobar.diasRetraso > 0" class="multa-preview">
            <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <div>
              <p class="multa-titulo">Se generará una multa</p>
              <p class="multa-detalle">
                {{ modalAprobar.diasRetraso }} día(s) de retraso ×
                $5.00 MXN = <strong>${{ (modalAprobar.diasRetraso * 5).toFixed(2) }} MXN</strong>
              </p>
              <p class="multa-nota">
                El cálculo usa la fecha en que el estudiante solicitó la devolución
                ({{ formatDate(modalAprobar.prestamo?.fecha_solicitud_dev) }}),
                no la fecha de hoy.
              </p>
            </div>
          </div>

          <div v-else class="sin-multa-preview">
            <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
            <p>Devolución a tiempo — sin multa</p>
          </div>

          <div class="form-group">
            <label class="form-label">Observaciones (opcional)</label>
            <textarea
              v-model="modalAprobar.observaciones"
              class="form-textarea"
              placeholder="Ej: Libro en buen estado. Entregado en ventanilla 3."
              rows="2"
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancelar" @click="cerrarModal"
            :disabled="aprobandoId !== null">Cancelar</button>
          <button class="btn-confirmar" @click="confirmarAprobacion"
            :disabled="aprobandoId !== null">
            <span v-if="aprobandoId !== null" class="spinner-mini"></span>
            {{ aprobandoId !== null ? 'Procesando...' : '✓ Confirmar Aprobación' }}
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
import { prestamoLibroService } from '@/services/PrestamoLibro'

// ── State ──────────────────────────────────────────────────────────────────
const prestamos      = ref([])
const isLoading      = ref(false)
const error          = ref(null)
const busqueda       = ref('')
const aprobandoId    = ref(null)

// Búsqueda por ticket
const busquedaTicket  = ref('')
const buscandoTicket  = ref(false)
const resultadoTicket = ref(null)

// Modal aprobar
const modalAprobar = ref({
  visible: false, prestamo: null,
  observaciones: '', diasRetraso: 0
})

// Toast
const toast = ref({ visible: false, mensaje: '', tipo: '' })

// ── Computed ───────────────────────────────────────────────────────────────
const prestamosFiltrados = computed(() => {
  if (!busqueda.value.trim()) return prestamos.value
  const q = busqueda.value.toLowerCase()
  return prestamos.value.filter(p =>
    p.usuario_prestado_nombre?.toLowerCase().includes(q) ||
    p.libro_titulo?.toLowerCase().includes(q) ||
    String(p.numero_ticket || '').includes(q)
  )
})

// ── Carga ──────────────────────────────────────────────────────────────────
const cargar = async () => {
  isLoading.value = true
  error.value     = null
  try {
    prestamos.value = await prestamoLibroService.getPendientesDevolucion()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error cargando solicitudes'
  } finally {
    isLoading.value = false
  }
}

// ── Buscar por ticket ──────────────────────────────────────────────────────
const buscarPorTicket = async () => {
  if (!busquedaTicket.value) return
  buscandoTicket.value  = true
  resultadoTicket.value = null
  try {
    resultadoTicket.value = await prestamoLibroService.buscarPorTicket(
      Number(busquedaTicket.value)
    )
  } catch (err) {
    mostrarToast(
      err.response?.status === 404
        ? `No se encontró el ticket #${busquedaTicket.value}`
        : 'Error al buscar el ticket',
      'toast-error'
    )
  } finally {
    buscandoTicket.value = false
  }
}

// ── Modal aprobar ──────────────────────────────────────────────────────────
const abrirModalAprobar = (prestamo) => {
  const dias = calcularDias(prestamo)
  modalAprobar.value = {
    visible: true, prestamo,
    observaciones: '', diasRetraso: dias
  }
}

const cerrarModal = () => {
  if (aprobandoId.value) return
  modalAprobar.value.visible = false
}

const confirmarAprobacion = async () => {
  const prestamo = modalAprobar.value.prestamo
  if (!prestamo) return

  aprobandoId.value = prestamo.id
  try {
    const respuesta = await prestamoLibroService.aprobarDevolucion(
      prestamo.id,
      modalAprobar.value.observaciones || null
    )

    // Quitar de la lista
    prestamos.value = prestamos.value.filter(p => p.id !== prestamo.id)

    // Limpiar resultado de búsqueda por ticket si era el mismo
    if (resultadoTicket.value?.id === prestamo.id) {
      resultadoTicket.value = null
    }

    cerrarModal()

    const msg = respuesta.multa_generada
      ? `Devolución aprobada. Multa generada: $${respuesta.multa_generada.costo_monetario} MXN`
      : 'Devolución aprobada correctamente. Sin retraso.'

    mostrarToast(msg, respuesta.multa_generada ? 'toast-warning' : 'toast-success')

  } catch (err) {
    mostrarToast(
      err.response?.data?.detail || 'Error al aprobar la devolución',
      'toast-error'
    )
  } finally {
    aprobandoId.value = null
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const calcularDias = (prestamo) => {
  if (!prestamo?.fecha_solicitud_dev || !prestamo?.fecha_devolucion_esperada) return 0
  const esperada = new Date(prestamo.fecha_devolucion_esperada)
  const solicitud = new Date(prestamo.fecha_solicitud_dev)
  esperada.setHours(0,0,0,0)
  solicitud.setHours(0,0,0,0)
  const diff = Math.floor((solicitud - esperada) / (1000 * 60 * 60 * 24))
  return Math.max(0, diff)
}

const formatDate = (d) => {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-MX', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

const mostrarToast = (mensaje, tipo = 'toast-success') => {
  toast.value = { visible: true, mensaje, tipo }
  setTimeout(() => { toast.value.visible = false }, 4000)
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

.devoluciones-admin {
  min-height: 100vh; font-family: 'DM Sans', sans-serif;
  background: radial-gradient(ellipse 70% 40% at 5% 0%, rgba(82,183,136,.08) 0%, transparent 55%), radial-gradient(ellipse 50% 40% at 90% 100%, rgba(201,144,12,.07) 0%, transparent 50%), var(--cream);
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.page-header { background:linear-gradient(135deg,#1a4731 0%,#2d6a4f 60%,#3a7d5e 100%); padding:1.75rem 2rem 1.25rem; position:relative; overflow:hidden; }
.page-header::before { content:''; position:absolute; inset:0; pointer-events:none; background:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E"); }
.header-inner  { position:relative; display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; flex-wrap:wrap; }
.header-sup    { font-size:.72rem; font-weight:600; color:rgba(255,255,255,.5); text-transform:uppercase; letter-spacing:.1em; margin-bottom:.2rem; }
.header-titulo { font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700; color:#fff; margin-bottom:.25rem; }
.header-sub    { font-size:.8rem; color:rgba(255,255,255,.6); margin:0; }
.header-stats  { display:flex; align-items:center; gap:.75rem; flex-shrink:0; }
.hstat { display:flex; flex-direction:column; align-items:center; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.12); border-radius:10px; padding:.5rem .875rem; min-width:60px; }
.hstat-pending { background:rgba(99,102,241,.2); border-color:rgba(99,102,241,.3); }
.hstat-num  { font-family:'Playfair Display',serif; font-size:1.3rem; font-weight:700; color:#a5b4fc; line-height:1; }
.hstat-lbl  { font-size:.65rem; color:rgba(255,255,255,.55); text-transform:uppercase; letter-spacing:.07em; margin-top:2px; }
.btn-refresh { width:34px; height:34px; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.12); border-radius:8px; color:rgba(255,255,255,.7); cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all .2s; }
.btn-refresh:hover { background:rgba(255,255,255,.18); color:#fff; }

/* ── Buscador ticket ─────────────────────────────────────────────────────── */
.ticket-search-bar { margin:1.25rem 1.5rem 0; max-width:900px; }
.ticket-search-wrap { display:flex; align-items:center; gap:.75rem; padding:.75rem 1rem; background:var(--card-bg); border:2px solid #c7d2fe; border-radius:12px; box-shadow:0 4px 16px rgba(99,102,241,.1); }
.ticket-search-wrap svg { color:#6366f1; flex-shrink:0; }
.ticket-input { flex:1; border:none; background:none; font-family:'DM Sans',sans-serif; font-size:.95rem; color:#1a2e1a; outline:none; }
.ticket-input::placeholder { color:#9ab5a0; }
.ticket-input::-webkit-inner-spin-button, .ticket-input::-webkit-outer-spin-button { -webkit-appearance:none; }
.btn-buscar-ticket { padding:.5rem 1.1rem; background:#6366f1; color:#fff; border:none; border-radius:8px; font-size:.82rem; font-weight:700; cursor:pointer; white-space:nowrap; transition:background .2s; }
.btn-buscar-ticket:hover:not(:disabled) { background:#4338ca; }
.btn-buscar-ticket:disabled { opacity:.5; cursor:not-allowed; }
.ticket-hint { font-size:.75rem; color:#9ab5a0; margin:.5rem 0 0 .25rem; }

/* ── Resultado ticket ────────────────────────────────────────────────────── */
.resultado-ticket { margin:.875rem 1.5rem 0; max-width:900px; background:var(--card-bg); border:1.5px solid #c7d2fe; border-left:4px solid #6366f1; border-radius:12px; overflow:hidden; box-shadow:var(--shadow-sm); }
.resultado-header { display:flex; justify-content:space-between; align-items:center; padding:.75rem 1.25rem; background:#eef2ff; border-bottom:1px solid #c7d2fe; }
.resultado-titulo { font-size:.875rem; font-weight:700; color:#4338ca; }
.btn-limpiar { background:none; border:none; font-size:.8rem; color:#6366f1; cursor:pointer; font-weight:600; }
.btn-limpiar:hover { color:#4338ca; }
.resultado-body { padding:1rem 1.25rem; display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap; }
.resultado-info { display:flex; flex-direction:column; gap:.4rem; flex:1; }
.ri-row { display:flex; gap:.75rem; font-size:.82rem; }
.ri-label { font-weight:700; color:#9ab5a0; min-width:110px; }
.ri-valor { color:#1a2e1a; }
.valor-danger { color:#d62828; font-weight:700; }
.valor-ok     { color:var(--green-mid); font-weight:700; }
.btn-aprobar-ticket { padding:.6rem 1.25rem; background:var(--green-mid); color:#fff; border:none; border-radius:10px; font-size:.875rem; font-weight:700; cursor:pointer; white-space:nowrap; transition:background .2s; }
.btn-aprobar-ticket:hover:not(:disabled) { background:#111; }
.btn-aprobar-ticket:disabled { opacity:.5; cursor:not-allowed; }

/* ── Lista pendientes ────────────────────────────────────────────────────── */
.lista-section { margin:1.25rem 1.5rem; max-width:900px; background:var(--card-bg); border:1.5px solid var(--cream-border); border-radius:16px; overflow:hidden; box-shadow:var(--shadow-sm); }
.lista-toolbar { padding:.875rem 1.25rem; border-bottom:1.5px solid #eef5f0; }
.search-wrap { display:flex; align-items:center; gap:.5rem; padding:.5rem .75rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:9px; color:#9ab5a0; max-width:360px; }
.search-input { flex:1; border:none; background:none; font-family:'DM Sans',sans-serif; font-size:.82rem; color:#1a2e1a; outline:none; }
.search-input::placeholder { color:#9ab5a0; }

.estado-loading, .estado-error, .estado-vacio { display:flex; flex-direction:column; align-items:center; padding:3rem 2rem; gap:.75rem; text-align:center; }
.spinner { width:32px; height:32px; border:3px solid var(--green-pale); border-top-color:var(--green-mid); border-radius:50%; animation:spin .7s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }
.vacio-ico { color:#b8ddc8; }
.vacio-titulo { font-weight:700; color:var(--green-dark); margin:0; }
.vacio-desc   { font-size:.82rem; color:#5a7a5a; margin:0; }

.tabla-wrap { overflow-x:auto; }
.tabla { width:100%; border-collapse:collapse; font-size:.82rem; }
.tabla thead { background:linear-gradient(135deg,#1a4731,#2d6a4f); }
.tabla thead th { padding:.75rem 1rem; text-align:left; color:rgba(255,255,255,.88); font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.06em; }
.tabla tbody tr { border-bottom:1px solid #f1f5f0; transition:background .15s; }
.tabla tbody tr:last-child { border-bottom:none; }
.tabla tbody tr:hover { background:#fafef8; }
.tabla td { padding:.75rem 1rem; vertical-align:middle; color:#334155; }
.td-ticket   { font-family:monospace; font-weight:700; color:#6366f1; font-size:.85rem; }
.td-usuario  { font-weight:600; color:#1a2e1a; }
.td-libro    { color:#475569; max-width:180px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.td-fecha    { font-size:.78rem; color:#64748b; white-space:nowrap; }
.retraso-badge { display:inline-block; padding:.2rem .6rem; border-radius:20px; font-size:.72rem; font-weight:700; white-space:nowrap; }
.retraso-si { background:#fff0f0; color:#b91c1c; border:1px solid #fca5a5; }
.retraso-no { background:var(--green-pale); color:var(--green-dark); border:1px solid #b8ddc8; }
.btn-aprobar { padding:.35rem .875rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-size:.78rem; font-weight:700; cursor:pointer; white-space:nowrap; transition:background .2s; }
.btn-aprobar:hover:not(:disabled) { background:#111; }
.btn-aprobar:disabled { opacity:.5; cursor:not-allowed; }

/* ── Modal ───────────────────────────────────────────────────────────────── */
.modal-overlay { position:fixed; inset:0; background:transparent; display:flex; align-items:center; justify-content:center; z-index:2000; }
.modal-overlay::before { content:''; position:fixed; inset:0; background:rgba(26,47,26,.6); backdrop-filter:blur(8px); z-index:-1; }
.modal { background:var(--card-bg); border-radius:16px; width:90%; max-width:480px; border:1.5px solid var(--cream-border); box-shadow:0 24px 64px rgba(0,0,0,.2); animation:modalIn .25s cubic-bezier(.22,1,.36,1); position:relative; z-index:1; }
@keyframes modalIn { from { opacity:0; transform:translateY(-14px) scale(.97); } to { opacity:1; transform:translateY(0) scale(1); } }
.modal-header { display:flex; justify-content:space-between; align-items:center; padding:1.1rem 1.375rem .875rem; border-bottom:1.5px solid #eef5f0; }
.modal-header h3 { font-family:'Playfair Display',serif; font-size:1.05rem; font-weight:700; color:var(--green-dark); margin:0; }
.modal-close { background:none; border:none; font-size:1.3rem; color:#9ab5a0; cursor:pointer; padding:0; line-height:1; }
.modal-close:hover { color:var(--green-dark); }
.modal-body   { padding:1.25rem 1.375rem; display:flex; flex-direction:column; gap:1rem; }
.modal-info-rows { display:flex; flex-direction:column; gap:.4rem; background:var(--cream); padding:.875rem; border-radius:10px; }
.mi-row   { display:flex; gap:.75rem; font-size:.82rem; }
.mi-label { font-weight:700; color:#9ab5a0; min-width:80px; }
.mi-valor { color:#1a2e1a; }
.mono     { font-family:monospace; color:#6366f1; font-weight:700; }

.multa-preview { display:flex; gap:.75rem; padding:.875rem; background:#fff3f3; border:1px solid #f5c0c0; border-radius:10px; }
.multa-preview svg { color:#d62828; flex-shrink:0; margin-top:2px; }
.multa-titulo  { font-weight:700; font-size:.875rem; color:#d62828; margin:0 0 3px; }
.multa-detalle { font-size:.82rem; color:#6b3333; margin:0 0 3px; }
.multa-nota    { font-size:.72rem; color:#9ab5a0; margin:0; }

.sin-multa-preview { display:flex; gap:.625rem; padding:.75rem; background:var(--green-pale); border:1px solid #b8ddc8; border-radius:10px; font-size:.82rem; color:var(--green-dark); font-weight:600; align-items:center; }
.sin-multa-preview svg { color:var(--green-mid); flex-shrink:0; }
.sin-multa-preview p  { margin:0; }

.form-group  { display:flex; flex-direction:column; gap:5px; }
.form-label  { font-size:.72rem; font-weight:700; color:var(--green-dark); text-transform:uppercase; letter-spacing:.07em; }
.form-textarea { padding:.6rem .75rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.875rem; color:#1a2e1a; resize:vertical; outline:none; transition:border-color .2s; }
.form-textarea:focus { border-color:var(--green-light); }

.modal-footer { display:flex; justify-content:flex-end; gap:.625rem; padding:.875rem 1.375rem; border-top:1.5px solid #eef5f0; }
.btn-cancelar { padding:.5rem 1rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:600; color:#5a7a5a; cursor:pointer; transition:all .18s; }
.btn-cancelar:hover { background:#f8fafc; }
.btn-cancelar:disabled { opacity:.5; cursor:not-allowed; }
.btn-confirmar { padding:.5rem 1.1rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:.4rem; transition:background .2s; }
.btn-confirmar:hover:not(:disabled) { background:#111; }
.btn-confirmar:disabled { opacity:.5; cursor:not-allowed; }
.spinner-mini { width:12px; height:12px; border:2px solid rgba(255,255,255,.3); border-top-color:#fff; border-radius:50%; animation:spin .6s linear infinite; }

/* ── Toast ───────────────────────────────────────────────────────────────── */
.toast { position:fixed; bottom:2rem; right:2rem; display:flex; align-items:center; gap:.75rem; padding:.75rem 1.1rem; border-radius:10px; font-size:.82rem; font-weight:600; color:#fff; z-index:9999; box-shadow:0 4px 20px rgba(0,0,0,.15); }
.toast-success { background:#16a34a; }
.toast-error   { background:#d62828; }
.toast-warning { background:#c9900c; }
.toast-close   { background:none; border:none; color:rgba(255,255,255,.75); font-size:1.1rem; cursor:pointer; padding:0; line-height:1; margin-left:.5rem; }
.toast-close:hover { color:#fff; }
.toast-in-enter-active, .toast-in-leave-active { transition:all .3s ease; }
.toast-in-enter-from, .toast-in-leave-to { opacity:0; transform:translateX(16px); }
</style>