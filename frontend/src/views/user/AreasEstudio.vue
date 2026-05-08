<template>
  <div class="areas-estudio">

    <!-- ══ HEADER ══ -->
    <header class="page-header">
      <div class="header-inner">
        <div class="header-texto">
          <p class="header-sup">Biblioteca Universitaria</p>
          <h1 class="header-titulo">Áreas de Estudio</h1>
          <p class="header-sub">Consulta la disponibilidad y reserva tu espacio</p>
        </div>
        <div class="header-stats">
          <div class="hstat hstat-green">
            <span class="hstat-num">{{ disponibles }}</span>
            <span class="hstat-lbl">Disponibles</span>
          </div>
          <button class="btn-refresh" @click="refrescar" title="Actualizar">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- ══ BANNER: ya tienes área activa ══ -->
    <div v-if="miAreaActiva" class="banner-activa">
      <div class="banner-ico">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      </div>
      <div class="banner-body">
        <strong>
          {{ miAreaActiva.estado_prestamo_id === 2
            ? `Tienes una reserva pendiente de aprobación: ${miAreaActiva.area_nombre}`
            : `Estás usando: ${miAreaActiva.area_nombre}` }}
        </strong>
        <p>
          {{ miAreaActiva.estado_prestamo_id === 2
            ? 'Un administrador debe aprobar tu solicitud antes de que puedas acceder al área.'
            : `Hasta: ${formatFecha(miAreaActiva.fecha_devolucion_esperada)}` }}
        </p>
      </div>
    </div>

    <!-- ══ LEYENDA + BÚSQUEDA ══ -->
    <div class="leyenda">
      <div class="leyenda-item"><span class="leyenda-dot dot-disponible"></span><span>Disponible</span></div>
      <div class="leyenda-item"><span class="leyenda-dot dot-ocupada"></span><span>Ocupada</span></div>
      <div class="leyenda-item"><span class="leyenda-dot dot-reservada"></span><span>Reservada</span></div>
      <div class="leyenda-item"><span class="leyenda-dot dot-mantenimiento"></span><span>Mantenimiento</span></div>
      <div class="search-wrap">
        <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input v-model="busqueda" type="text" placeholder="Buscar área..." class="search-input"/>
        <button v-if="busqueda" class="search-clear" @click="busqueda = ''">×</button>
      </div>
    </div>

    <!-- ══ GRID ══ -->
    <div class="contenido">
      <div v-if="isLoading" class="estado-loading">
        <div class="spinner"></div>
        <p>Cargando áreas de estudio...</p>
      </div>

      <div v-else-if="error" class="estado-error">
        <p>{{ error }}</p>
        <button class="btn-retry" @click="refrescar">Reintentar</button>
      </div>

      <div v-else-if="areasFiltradas.length === 0" class="estado-vacio">
        <svg width="48" height="48" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.2" class="vacio-ico">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
        </svg>
        <p class="vacio-titulo">{{ busqueda ? 'Sin resultados' : 'No hay áreas disponibles' }}</p>
      </div>

      <div v-else class="cards-grid">
        <div
          v-for="area in areasFiltradas"
          :key="area.id"
          class="area-card"
          :class="getCardClass(area)"
        >
          <div class="estado-indicator" :class="getIndicatorClass(area)"></div>

          <div class="card-top">
            <div class="card-icono" :class="getIconoClass(area)">
              <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
            </div>
            <span class="estado-chip" :class="getChipClass(area)">{{ area.estado_nombre }}</span>
          </div>

          <h3 class="card-nombre">{{ area.nombre }}</h3>

          <div class="card-detalles">
            <div class="detalle-row">
              <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              <span>Capacidad: <strong>{{ area.capacidad || 'N/A' }} personas</strong></span>
            </div>
          </div>

          <div class="card-footer">
            <!-- Disponible y el usuario no tiene área activa -->
            <button
              v-if="area.estado_id === 1 && !miAreaActiva"
              class="btn-reservar"
              @click="abrirModalReservar(area)"
            >
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              Reservar
            </button>

            <!-- Disponible pero ya tiene área activa -->
            <span v-else-if="area.estado_id === 1 && miAreaActiva" class="btn-estado btn-bloqueada">
              Ya tienes un área activa
            </span>

            <!-- Ocupada -->
            <span v-else-if="area.estado_id === 2" class="btn-estado btn-ocupada">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
              En uso
            </span>

            <!-- Mantenimiento -->
            <span v-else-if="area.estado_id === 3" class="btn-estado btn-mantenimiento">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              Mantenimiento
            </span>

            <!-- Reservada (esperando aprobación) -->
            <span v-else-if="area.estado_id === 4" class="btn-estado btn-reservada">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              Pendiente aprobación
            </span>

            <span v-else class="btn-estado btn-nodisponible">No disponible</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ MODAL RESERVAR ══ -->
    <div v-if="modalReservar.visible" class="modal-overlay" @click.self="cerrarModalReservar">
      <div class="modal">
        <div class="modal-header">
          <h3>Solicitar Reserva</h3>
          <button class="modal-close" @click="cerrarModalReservar" :disabled="reservando">×</button>
        </div>
        <div class="modal-body">
          <div class="reserva-info">
            <div class="reserva-ico">
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
            </div>
            <div>
              <p class="reserva-nombre">{{ modalReservar.area?.nombre }}</p>
              <p class="reserva-cap">Capacidad: {{ modalReservar.area?.capacidad || 'N/A' }} personas</p>
            </div>
          </div>

          <!-- Aviso del nuevo flujo -->
          <div class="flujo-aviso">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <p>Tu solicitud quedará <strong>pendiente de aprobación</strong>. Un administrador del CID deberá aprobarla para que el área quede disponible para ti.</p>
          </div>

          <div class="form-field">
            <label class="form-label">Hasta qué hora la utilizarás <span class="req">*</span></label>
            <input
              type="datetime-local"
              v-model="reservaForm.fecha_devolucion_esperada"
              class="form-input"
              :min="fechaMinima"
            />
          </div>

          <div v-if="modalReservar.error" class="form-error">{{ modalReservar.error }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="cerrarModalReservar" :disabled="reservando">Cancelar</button>
          <button class="btn-reservar-confirm" @click="confirmarReserva" :disabled="reservando">
            <span v-if="reservando" class="spinner-mini"></span>
            {{ reservando ? 'Enviando...' : 'Enviar Solicitud' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══ TOAST ══ -->
    <transition name="toast-in">
      <div v-if="toast.visible" class="toast" :class="toast.tipo">
        <span>{{ toast.mensaje }}</span>
        <button class="toast-close" @click="toast.visible = false">×</button>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAreas } from '@/composables/useAreas'
import { prestamoAreasService } from '@/services/prestamoAreas'

import '@/styles/buttons.css'

const authStore = useAuthStore()
const { areas, isLoading, error, cargarAreas } = useAreas()

// ── State ──────────────────────────────────────────────────────────────────
const busqueda    = ref('')
const reservando  = ref(false)
const miAreaActiva = ref(null)   // solicitud activa del usuario (vigente o pendiente)

const modalReservar = ref({ visible: false, area: null, error: '' })
const reservaForm   = ref({ fecha_devolucion_esperada: null })
const toast         = ref({ visible: false, mensaje: '', tipo: '' })

// ── Computed ───────────────────────────────────────────────────────────────
const areasPrestables = computed(() =>
  areas.value.filter(a => a.es_prestable && a.estado_id === 1)
)

const areasFiltradas = computed(() => {
  if (!busqueda.value.trim()) return areasPrestables.value
  const q = busqueda.value.toLowerCase()
  return areasPrestables.value.filter(a => a.nombre.toLowerCase().includes(q))
})

const disponibles = computed(() => areasPrestables.value.filter(a => a.estado_id === 1).length)

const fechaMinima = computed(() => {
  const ahora = new Date()
  ahora.setMinutes(ahora.getMinutes() - ahora.getTimezoneOffset())
  return ahora.toISOString().slice(0, 16)
})

// ── Clases ─────────────────────────────────────────────────────────────────
const getCardClass = (area) => ({
  'card-disponible':    area.estado_id === 1,
  'card-ocupada':       area.estado_id === 2,
  'card-mantenimiento': area.estado_id === 3,
  'card-reservada':     area.estado_id === 4,
})

const getIndicatorClass = (area) => ({
  'ind-disponible':    area.estado_id === 1,
  'ind-ocupada':       area.estado_id === 2,
  'ind-mantenimiento': area.estado_id === 3,
  'ind-reservada':     area.estado_id === 4,
})

const getIconoClass = (area) => ({
  'icono-disponible':    area.estado_id === 1,
  'icono-ocupada':       area.estado_id === 2,
  'icono-mantenimiento': area.estado_id === 3,
  'icono-reservada':     area.estado_id === 4,
})

const getChipClass = (area) => ({
  'chip-disponible':    area.estado_id === 1,
  'chip-ocupada':       area.estado_id === 2,
  'chip-mantenimiento': area.estado_id === 3,
  'chip-reservada':     area.estado_id === 4,
})

// ── Carga ──────────────────────────────────────────────────────────────────
const refrescar = async () => {
  await cargarAreas()
  await verificarAreaActiva()
}

const verificarAreaActiva = async () => {
  try {
    const solicitudes = await prestamoAreasService.getMisSolicitudes()
    miAreaActiva.value = Array.isArray(solicitudes) && solicitudes.length > 0
      ? solicitudes[0]
      : null
  } catch {
    miAreaActiva.value = null
  }
}

// ── Modal reservar ─────────────────────────────────────────────────────────
const abrirModalReservar = (area) => {
  modalReservar.value = { visible: true, area, error: '' }
  reservaForm.value   = { fecha_devolucion_esperada: null }
}

const cerrarModalReservar = () => {
  if (!reservando.value) modalReservar.value.visible = false
}

const confirmarReserva = async () => {
  if (!reservaForm.value.fecha_devolucion_esperada) {
    modalReservar.value.error = 'Selecciona la hora de devolución'
    return
  }

  reservando.value = true
  try {
    await prestamoAreasService.crearPrestamo({
      area_id:                   modalReservar.value.area.id,
      usuario_prestado_id:       authStore.userId,
      fecha_devolucion_esperada: reservaForm.value.fecha_devolucion_esperada,
    })

    modalReservar.value.visible = false
    mostrarToast(`Solicitud enviada para "${modalReservar.value.area?.nombre}". Espera la aprobación del administrador.`)
    await refrescar()
  } catch (err) {
    modalReservar.value.error = err.response?.data?.detail || 'Error al enviar la solicitud'
  } finally {
    reservando.value = false
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const formatFecha = (d) => {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-MX', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
  })
}

const mostrarToast = (mensaje, tipo = 'toast-success') => {
  toast.value = { visible: true, mensaje, tipo }
  setTimeout(() => { toast.value.visible = false }, 4000)
}

onMounted(async () => {
  await cargarAreas()
  await verificarAreaActiva()
})
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
  --shadow-md:    0 8px 24px rgba(26,71,49,.12);
}

.areas-estudio { font-family: 'DM Sans', sans-serif; min-height: 100vh; background: radial-gradient(ellipse 70% 40% at 5% 0%, rgba(82,183,136,.08) 0%, transparent 55%), radial-gradient(ellipse 50% 40% at 90% 100%, rgba(201,144,12,.07) 0%, transparent 50%), var(--cream); }

/* ── Header ──────────────────────────────────────────────────────────────── */
.page-header { background: linear-gradient(135deg, #1a4731 0%, #2d6a4f 60%, #3a7d5e 100%); padding: 1.75rem 2rem 1.25rem; position: relative; overflow: hidden; }
.page-header::before { content: ''; position: absolute; inset: 0; pointer-events: none; background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E"); }
.header-inner  { display: flex; justify-content: space-between; align-items: flex-start; gap: 1.5rem; flex-wrap: wrap; position: relative; }
.header-sup    { font-size: .72rem; font-weight: 600; color: rgba(255,255,255,.5); text-transform: uppercase; letter-spacing: .1em; margin-bottom: .2rem; }
.header-titulo { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: #fff; margin-bottom: .3rem; }
.header-sub    { font-size: .8rem; color: rgba(255,255,255,.65); margin: 0; }
.header-stats  { display: flex; align-items: center; gap: .75rem; flex-shrink: 0; }
.hstat { display: flex; flex-direction: column; align-items: center; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.1); border-radius: 9px; padding: .45rem .875rem; min-width: 70px; }
.hstat-green { background: rgba(82,183,136,.2); border-color: rgba(82,183,136,.3); }
.hstat-gold  { background: rgba(244,197,66,.15); border-color: rgba(244,197,66,.2); }
.hstat-num { font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: #fff; line-height: 1; }
.hstat-green .hstat-num { color: #a7f3d0; }
.hstat-gold  .hstat-num { color: var(--gold-light); }
.hstat-lbl { font-size: .64rem; color: rgba(255,255,255,.55); text-transform: uppercase; letter-spacing: .07em; margin-top: 2px; white-space: nowrap; }
.btn-refresh { width: 34px; height: 34px; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.12); border-radius: 8px; color: rgba(255,255,255,.7); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all .2s; }
.btn-refresh:hover { background: rgba(255,255,255,.18); color: #fff; }

/* ── Banner área activa ──────────────────────────────────────────────────── */
.banner-activa { display: flex; align-items: center; gap: 1rem; margin: 0 0 0; padding: .875rem 2rem; background: #eef2ff; border-bottom: 1.5px solid #c7d2fe; }
.banner-ico { color: #4338ca; flex-shrink: 0; display: flex; }
.banner-body strong { display: block; font-size: .875rem; color: #4338ca; margin-bottom: 2px; }
.banner-body p { font-size: .78rem; color: #4338ca; opacity: .75; margin: 0; }

/* ── Leyenda ─────────────────────────────────────────────────────────────── */
.leyenda { display: flex; align-items: center; gap: 1.25rem; flex-wrap: wrap; padding: .875rem 2rem; background: var(--card-bg); border-bottom: 1.5px solid var(--cream-border); }
.leyenda-item { display: flex; align-items: center; gap: .4rem; font-size: .78rem; color: #5a7a5a; }
.leyenda-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.dot-disponible    { background: var(--green-light); }
.dot-ocupada       { background: #f59e0b; }
.dot-reservada     { background: #6366f1; }
.dot-mantenimiento { background: #60a5fa; }
.search-wrap { display: flex; align-items: center; gap: .4rem; margin-left: auto; padding: .4rem .7rem; background: var(--cream); border: 1.5px solid var(--cream-border); border-radius: 9px; color: #9ab5a0; }
.search-input { border: none; background: none; font-family: 'DM Sans', sans-serif; font-size: .82rem; color: #1a2e1a; outline: none; width: 160px; }
.search-input::placeholder { color: #9ab5a0; }
.search-clear { background: none; border: none; color: #9ab5a0; cursor: pointer; font-size: 1rem; padding: 0; line-height: 1; }
.search-clear:hover { color: var(--green-dark); }

/* ── Contenido ───────────────────────────────────────────────────────────── */
.contenido { padding: 1.5rem 2rem; }
.estado-loading, .estado-error, .estado-vacio { display: flex; flex-direction: column; align-items: center; padding: 4rem 2rem; gap: .75rem; text-align: center; }
.spinner { width: 36px; height: 36px; border: 3px solid var(--green-pale); border-top-color: var(--green-mid); border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.estado-loading p, .estado-error p { color: #5a7a5a; margin: 0; font-size: .875rem; }
.estado-error p { color: #d62828; }
.vacio-ico    { color: #b8ddc8; }
.vacio-titulo { font-size: .95rem; font-weight: 600; color: var(--green-dark); margin: 0; }
.btn-retry { padding: .5rem 1.1rem; background: var(--green-mid); color: #fff; border: none; border-radius: 8px; font-size: .82rem; font-weight: 700; cursor: pointer; }

/* ── Cards ───────────────────────────────────────────────────────────────── */
.cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1.1rem; }
.area-card { background: var(--card-bg); border: 1.5px solid var(--cream-border); border-radius: 16px; padding: 1.25rem; display: flex; flex-direction: column; gap: .875rem; box-shadow: var(--shadow-sm); position: relative; overflow: hidden; transition: transform .2s, box-shadow .2s; }
.area-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }

.card-disponible    { border-top: 3px solid var(--green-light); }
.card-ocupada       { border-top: 3px solid #f59e0b; }
.card-mantenimiento { border-top: 3px solid #60a5fa; }
.card-reservada     { border-top: 3px solid #6366f1; }

.estado-indicator { position: absolute; top: 1rem; right: 1rem; width: 10px; height: 10px; border-radius: 50%; }
.ind-disponible    { background: var(--green-light); box-shadow: 0 0 6px rgba(82,183,136,.5); }
.ind-ocupada       { background: #f59e0b; }
.ind-mantenimiento { background: #60a5fa; }
.ind-reservada     { background: #6366f1; }

.card-top { display: flex; align-items: center; gap: .75rem; }
.card-icono { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.icono-disponible    { background: var(--green-pale); color: var(--green-mid); }
.icono-ocupada       { background: #fef3c7; color: #92400e; }
.icono-mantenimiento { background: #dbeafe; color: #1e40af; }
.icono-reservada     { background: #eef2ff; color: #4338ca; }

.estado-chip { font-size: .68rem; font-weight: 700; padding: .2rem .55rem; border-radius: 20px; white-space: nowrap; text-transform: uppercase; letter-spacing: .05em; }
.chip-disponible    { background: var(--green-pale); color: var(--green-dark); border: 1px solid #b8ddc8; }
.chip-ocupada       { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
.chip-mantenimiento { background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }
.chip-reservada     { background: #eef2ff; color: #4338ca; border: 1px solid #c7d2fe; }

.card-nombre { font-family: 'Playfair Display', serif; font-size: 1rem; font-weight: 700; color: var(--green-dark); margin: 0; }

.card-detalles { display: flex; flex-direction: column; gap: .3rem; }
.detalle-row { display: flex; align-items: center; gap: .4rem; font-size: .78rem; color: #5a7a5a; }
.detalle-row strong { color: #1a2e1a; }

.card-footer { margin-top: auto; }

.btn-reservar { width: 100%; padding: .6rem; background: var(--green-mid); color: #fff; border: none; border-radius: 10px; font-family: 'DM Sans', sans-serif; font-size: .82rem; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: .4rem; transition: background .2s, transform .15s; }
.btn-reservar:hover { background: #111; transform: translateY(-1px); }

.btn-estado { width: 100%; padding: .55rem; border-radius: 10px; border: none; font-family: 'DM Sans', sans-serif; font-size: .78rem; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: .4rem; cursor: default; }
.btn-ocupada       { background: #fef3c7; color: #92400e; }
.btn-mantenimiento { background: #dbeafe; color: #1e40af; }
.btn-reservada     { background: #eef2ff; color: #4338ca; }
.btn-nodisponible  { background: #f1f5f9; color: #94a3b8; }
.btn-bloqueada     { background: #f1f5f9; color: #94a3b8; font-size: .72rem; }

/* ── Modal ───────────────────────────────────────────────────────────────── */
.modal-overlay { position: fixed; inset: 0; background: transparent; display: flex; align-items: center; justify-content: center; z-index: 2000; }
.modal-overlay::before { content: ''; position: fixed; inset: 0; background: rgba(26,47,26,.55); backdrop-filter: blur(8px); z-index: -1; }
.modal { background: var(--card-bg); border-radius: 16px; width: 90%; max-width: 420px; border: 1.5px solid var(--cream-border); box-shadow: 0 24px 64px rgba(0,0,0,.2); animation: modalIn .25s cubic-bezier(.22,1,.36,1); position: relative; z-index: 1; }
@keyframes modalIn { from { opacity: 0; transform: translateY(-14px) scale(.97); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.1rem 1.375rem .875rem; border-bottom: 1.5px solid #eef5f0; }
.modal-header h3 { font-family: 'Playfair Display', serif; font-size: 1.05rem; font-weight: 700; color: var(--green-dark); margin: 0; }
.modal-close { background: none; border: none; font-size: 1.3rem; color: #9ab5a0; cursor: pointer; padding: 0; line-height: 1; }
.modal-close:hover { color: var(--green-dark); }
.modal-body { padding: 1.25rem 1.375rem; display: flex; flex-direction: column; gap: 1rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: .625rem; padding: .875rem 1.375rem; border-top: 1.5px solid #eef5f0; }

.reserva-info { display: flex; align-items: center; gap: .875rem; padding: .875rem; background: var(--green-pale); border-radius: 10px; }
.reserva-ico { width: 42px; height: 42px; background: var(--green-mid); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #fff; flex-shrink: 0; }
.reserva-nombre { font-weight: 700; font-size: .9rem; color: var(--green-dark); margin: 0 0 2px; }
.reserva-cap    { font-size: .75rem; color: #5a7a5a; margin: 0; }

.flujo-aviso { display: flex; gap: .5rem; padding: .75rem; background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 9px; font-size: .78rem; color: #4338ca; align-items: flex-start; }
.flujo-aviso p { margin: 0; line-height: 1.5; }

.form-field { display: flex; flex-direction: column; gap: 5px; }
.form-label { font-size: .72rem; font-weight: 700; color: var(--green-dark); text-transform: uppercase; letter-spacing: .07em; }
.req { color: #d62828; }
.form-input { padding: .6rem .75rem; background: #fff; border: 1.5px solid var(--cream-border); border-radius: 9px; font-family: 'DM Sans', sans-serif; font-size: .875rem; color: #1a2e1a; outline: none; width: 100%; box-sizing: border-box; transition: border-color .2s; }
.form-input:focus { border-color: var(--green-light); }
.form-error { padding: .6rem .875rem; background: #fff3f3; border: 1px solid #f5c0c0; border-radius: 9px; color: #d62828; font-size: .82rem; font-weight: 600; }

.btn-modal-cancel { padding: .5rem 1rem; background: #fff; border: 1.5px solid var(--cream-border); border-radius: 8px; font-family: 'DM Sans', sans-serif; font-size: .82rem; font-weight: 600; color: #5a7a5a; cursor: pointer; transition: all .18s; }
.btn-modal-cancel:hover { background: #f8fafc; }
.btn-modal-cancel:disabled { opacity: .5; cursor: not-allowed; }

.btn-reservar-confirm { padding: .5rem 1.1rem; background: var(--green-mid); color: #fff; border: none; border-radius: 8px; font-family: 'DM Sans', sans-serif; font-size: .82rem; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: .4rem; transition: background .2s; }
.btn-reservar-confirm:hover:not(:disabled) { background: #111; }
.btn-reservar-confirm:disabled { opacity: .5; cursor: not-allowed; }

.spinner-mini { width: 12px; height: 12px; border: 2px solid rgba(255,255,255,.3); border-top-color: #fff; border-radius: 50%; animation: spin .6s linear infinite; }

/* ── Toast ───────────────────────────────────────────────────────────────── */
.toast { position: fixed; bottom: 2rem; right: 2rem; display: flex; align-items: center; gap: .75rem; padding: .75rem 1.1rem; border-radius: 10px; font-size: .82rem; font-weight: 600; color: #fff; z-index: 9999; box-shadow: 0 4px 20px rgba(0,0,0,.15); max-width: 400px; }
.toast-success { background: #16a34a; }
.toast-error   { background: #d62828; }
.toast-close   { background: none; border: none; color: rgba(255,255,255,.75); font-size: 1.1rem; cursor: pointer; padding: 0; line-height: 1; margin-left: auto; }
.toast-close:hover { color: #fff; }
.toast-in-enter-active, .toast-in-leave-active { transition: all .3s ease; }
.toast-in-enter-from, .toast-in-leave-to { opacity: 0; transform: translateX(16px); }

@media (max-width: 768px) {
  .contenido  { padding: 1rem; }
  .leyenda    { padding: .75rem 1rem; gap: .75rem; }
  .search-wrap{ margin-left: 0; width: 100%; }
  .search-input { width: 100%; }
  .cards-grid { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }
  .banner-activa { padding: .875rem 1rem; }
}
</style>