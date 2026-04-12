<template>
  <div class="user-menu">

    <!-- ══════════════════════════════════════
         HEADER
    ══════════════════════════════════════ -->
    <header class="page-header">
      <div class="header-inner">

        <div class="header-saludo">
          <p class="saludo-label">Bienvenido de vuelta</p>
          <h1 class="saludo-nombre">{{ userName }}</h1>
          <p class="saludo-meta">
            <span class="meta-chip">{{ getRoleName(userType) }}</span>
            <span class="meta-sep">·</span>
            <span class="meta-codigo">{{ userCode }}</span>
          </p>
        </div>

        <!-- Stats rápidos en header -->
        <div class="header-stats">
          <div class="hstat" :class="{ 'hstat-alert': vencidos > 0 }">
            <span class="hstat-num">{{ activeBooks }}</span>
            <span class="hstat-lbl">Activos</span>
          </div>
          <div class="hstat hstat-warn" v-if="porVencer > 0">
            <span class="hstat-num">{{ porVencer }}</span>
            <span class="hstat-lbl">Por vencer</span>
          </div>
          <div class="hstat hstat-danger" v-if="vencidos > 0">
            <span class="hstat-num">{{ vencidos }}</span>
            <span class="hstat-lbl">Vencidos</span>
          </div>
          <button class="btn-refresh" @click="refreshData" title="Actualizar">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </button>
        </div>

      </div>
    </header>

    <!-- ══════════════════════════════════════
         BANNER MULTAS
    ══════════════════════════════════════ -->
    <div v-if="tieneMultasPendientes" class="banner-multas">
      <div class="banner-ico">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
      </div>
      <div class="banner-body">
        <strong>Tienes multas pendientes</strong>
        <p>No puedes solicitar nuevos préstamos hasta liquidarlas. Acude a la biblioteca con tu comprobante.</p>
      </div>
      <button class="banner-cta" @click="$router.push('/user/multas')">Ver multas →</button>
    </div>

    <!-- ══════════════════════════════════════
         CONTENIDO
    ══════════════════════════════════════ -->
    <div class="page-body">

      <!-- ── PRÉSTAMOS ACTIVOS ── -->
      <section class="section-card">
        <div class="section-head">
          <div class="section-title-wrap">
            <h2 class="section-title">Préstamos activos</h2>
            <span class="section-count">{{ prestamosActivos.length }}</span>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loadingPrestamos" class="estado-loading">
          <div class="spinner"></div>
          <p>Cargando préstamos...</p>
        </div>

        <!-- Vacío -->
        <div v-else-if="prestamosActivos.length === 0" class="estado-vacio">
          <div class="vacio-ico">
            <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
          </div>
          <p class="vacio-titulo">Sin préstamos activos</p>
          <p class="vacio-desc">Explora el catálogo para solicitar un libro</p>
          <button class="btn-catalogo" @click="$router.push('/admin/libros')">
            Ver catálogo →
          </button>
        </div>

        <!-- Lista de préstamos activos -->
        <div v-else class="prestamos-lista">
          <div
            v-for="item in prestamosActivos"
            :key="item.id"
            class="prestamo-card"
            :class="{
              'prestamo-overdue': item.status === 'overdue',
              'prestamo-warning': item.status === 'warning'
            }"
          >
            <!-- Indicador lateral de estado -->
            <div class="prestamo-indicator"></div>

            <div class="prestamo-body">
              <div class="prestamo-top">
                <div class="prestamo-info">
                  <p class="prestamo-nombre">{{ item.name }}</p>
                  <div class="prestamo-meta">
                    <span class="prestamo-fecha-lbl">Prestado</span>
                    <span class="prestamo-fecha">{{ formatDate(item.loanDate) }}</span>
                  </div>
                </div>

                <div class="prestamo-derecha">
                  <!-- Badge de estado -->
                  <span class="status-badge" :class="`badge-${item.status}`">
                    {{ getStatusText(item.status) }}
                  </span>

                  <!-- Botón devolver -->
                  <button
                    class="btn-devolver"
                    @click="returnResource(item)"
                    :disabled="returningLoanId === item.id"
                  >
                    <span v-if="returningLoanId === item.id" class="btn-spinner"></span>
                    <span v-else>Devolver</span>
                  </button>
                </div>
              </div>

              <!-- Fecha devolución con urgencia -->
              <div class="prestamo-devolucion">
                <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                <span class="dev-label">Devolución:</span>
                <span class="dev-fecha">{{ formatDate(item.returnDate) }}</span>
                <span v-if="item.status === 'warning'" class="dev-urgencia dev-warn">
                  {{ item.diasRestantes === 0 ? 'Vence hoy' : `${item.diasRestantes}d restantes` }}
                </span>
                <span v-if="item.status === 'overdue'" class="dev-urgencia dev-overdue">
                  {{ Math.abs(item.diasRestantes) }}d vencido
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ── HISTORIAL (colapsable) ── -->
      <section class="section-card section-historial">
        <button class="historial-toggle" @click="historialAbierto = !historialAbierto">
          <div class="section-title-wrap">
            <h2 class="section-title">Historial de préstamos</h2>
            <span class="section-count">{{ prestamosHistorial.length }}</span>
          </div>
          <svg
            class="toggle-chevron"
            :class="{ 'chevron-open': historialAbierto }"
            width="16" height="16" fill="none" viewBox="0 0 24 24"
            stroke="currentColor" stroke-width="2.5"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
          </svg>
        </button>

        <transition name="historial-slide">
          <div v-if="historialAbierto" class="historial-body">

            <!-- Buscador dentro del historial -->
            <div class="historial-search">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
              <input
                v-model="busquedaHistorial"
                type="text"
                placeholder="Buscar en historial..."
                class="historial-input"
              />
            </div>

            <div v-if="loadingPrestamos" class="estado-loading estado-loading-sm">
              <div class="spinner spinner-sm"></div>
            </div>

            <div v-else-if="historialFiltrado.length === 0" class="estado-vacio estado-vacio-sm">
              <p>{{ busquedaHistorial ? 'Sin resultados para esa búsqueda' : 'Sin historial registrado' }}</p>
            </div>

            <div v-else class="historial-lista">
              <div
                v-for="item in historialPaginado"
                :key="item.id"
                class="historial-item"
              >
                <div class="historial-item-ico">
                  <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                  </svg>
                </div>
                <div class="historial-item-info">
                  <p class="historial-item-nombre">{{ item.name }}</p>
                  <p class="historial-item-fechas">
                    {{ formatDate(item.loanDate) }} → {{ formatDate(item.returnDate) }}
                  </p>
                </div>
                <span class="historial-badge">Devuelto</span>
              </div>
            </div>

            <!-- Paginación historial -->
            <div v-if="totalPaginasHistorial > 1" class="historial-paginacion">
              <button
                class="pag-btn"
                :disabled="paginaHistorial === 1"
                @click="paginaHistorial--"
              >← Anterior</button>
              <span class="pag-info">{{ paginaHistorial }} / {{ totalPaginasHistorial }}</span>
              <button
                class="pag-btn"
                :disabled="paginaHistorial === totalPaginasHistorial"
                @click="paginaHistorial++"
              >Siguiente →</button>
            </div>

          </div>
        </transition>
      </section>

    </div>

    <!-- ══════════════════════════════════════
         TOAST NORMAL
    ══════════════════════════════════════ -->
    <transition name="toast-in">
      <div v-if="toast.visible && !toast.esMulta" class="toast" :class="toast.tipo">
        <span class="toast-ico">{{ toast.icono }}</span>
        <div>
          <strong>{{ toast.titulo }}</strong>
          <p v-if="toast.descripcion">{{ toast.descripcion }}</p>
        </div>
        <button class="toast-close" @click="toast.visible = false">×</button>
      </div>
    </transition>

    <!-- ══════════════════════════════════════
         TOAST MULTA
    ══════════════════════════════════════ -->
    <transition name="toast-in">
      <div v-if="toast.visible && toast.esMulta" class="toast-multa">
        <div class="toast-multa-ico">⚠️</div>
        <div class="toast-multa-body">
          <strong>Multa registrada</strong>
          <p class="toast-multa-monto">{{ toast.montoMulta }}</p>
          <p class="toast-multa-desc">{{ toast.descripcion }}</p>
          <button class="toast-multa-cta" @click="irAMisMultas">Ver mis multas →</button>
        </div>
        <button class="toast-close toast-close-dark" @click="toast.visible = false">×</button>
      </div>
    </transition>

  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { prestamoLibroService } from '@/services/PrestamoLibro'
import { multasService } from '@/services/multas'

export default {
  name: 'UserMenu',

  data() {
    return {
      prestamos: [],
      loadingPrestamos: false,
      returningLoanId: null,
      tieneMultasPendientes: false,
      historialAbierto: false,
      busquedaHistorial: '',
      paginaHistorial: 1,
      itemsPorPagina: 8,

      toast: {
        visible: false, tipo: '', icono: '',
        titulo: '', descripcion: '',
        esMulta: false, montoMulta: ''
      }
    }
  },

  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },

  computed: {
    userName()  { return this.authStore.userName },
    userCode()  { return this.authStore.userCode },
    userType()  { return this.authStore.tipoUsuarioId },

    // Solo préstamos activos (active, warning, overdue)
    prestamosActivos() {
      return this.prestamos.filter(p =>
        p.status === 'active' || p.status === 'warning' || p.status === 'overdue'
      )
    },

    // Historial: solo completados
    prestamosHistorial() {
      return this.prestamos.filter(p => p.status === 'completed')
    },

    historialFiltrado() {
      if (!this.busquedaHistorial.trim()) return this.prestamosHistorial
      const q = this.busquedaHistorial.toLowerCase()
      return this.prestamosHistorial.filter(p =>
        p.name?.toLowerCase().includes(q)
      )
    },

    totalPaginasHistorial() {
      return Math.ceil(this.historialFiltrado.length / this.itemsPorPagina) || 1
    },

    historialPaginado() {
      const start = (this.paginaHistorial - 1) * this.itemsPorPagina
      return this.historialFiltrado.slice(start, start + this.itemsPorPagina)
    },

    activeBooks() { return this.prestamosActivos.length },
    porVencer()   { return this.prestamos.filter(p => p.status === 'warning').length },
    vencidos()    { return this.prestamos.filter(p => p.status === 'overdue').length }
  },

  watch: {
    // Resetear página al buscar
    busquedaHistorial() { this.paginaHistorial = 1 }
  },

  mounted() {
    this.loadPrestamos()
    this.verificarMultasPendientes()
  },

  methods: {
    async loadPrestamos() {
      try {
        this.loadingPrestamos = true
        this.prestamos = await prestamoLibroService.getPrestamosUsuario(false)
      } catch {
        this.mostrarToast('error', '✕', 'Error', 'No se pudieron cargar los préstamos')
      } finally {
        this.loadingPrestamos = false
      }
    },

    async verificarMultasPendientes() {
      try {
        const userId = this.authStore.userId
        if (!userId) return
        const multas = await multasService.getMultasByUsuario(userId)
        this.tieneMultasPendientes = Array.isArray(multas) && multas.length > 0
        if (this.authStore.actualizarEstadoMultas) {
          this.authStore.actualizarEstadoMultas(multas)
        }
      } catch { /* silencioso */ }
    },

    async returnResource(resource) {
      try {
        this.returningLoanId = resource.id
        const respuesta = await prestamoLibroService.devolverPrestamo(resource.id)
        await this.loadPrestamos()

        if (respuesta.multa_generada) {
          const monto = new Intl.NumberFormat('es-MX', {
            style: 'currency', currency: 'MXN'
          }).format(respuesta.multa_generada.costo_monetario)
          this.mostrarToastMulta(
            monto,
            `${respuesta.multa_generada.dias_excedidos} día(s) de retraso. ` +
            `Preséntate en la biblioteca con tu comprobante de pago.`
          )
          this.tieneMultasPendientes = true
          if (this.authStore.actualizarEstadoMultas) {
            this.authStore.actualizarEstadoMultas([{ estado_multa_id: 1 }])
          }
        } else {
          this.mostrarToast('success', '✓', 'Devolución registrada', respuesta.mensaje)
        }
      } catch (error) {
        this.mostrarToast('error', '✕', 'Error', error.response?.data?.detail || 'Error al devolver')
      } finally {
        this.returningLoanId = null
      }
    },

    refreshData() {
      this.loadPrestamos()
      this.verificarMultasPendientes()
    },

    irAMisMultas() {
      this.toast.visible = false
      this.$router.push('/user/multas')
    },

    getRoleName(tipoId) {
      return { 1: 'Usuario', 2: 'Admin Básico', 3: 'Admin Avanzado', 4: 'Super Admin' }[tipoId] || 'Usuario'
    },

    formatDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' })
    },

    getStatusText(status) {
      return { active: 'Activo', warning: 'Por vencer', overdue: 'Vencido', completed: 'Devuelto' }[status] || status
    },

    mostrarToast(tipo, icono, titulo, descripcion = '') {
      this.toast = { visible: true, tipo: `toast-${tipo}`, icono, titulo, descripcion, esMulta: false, montoMulta: '' }
      setTimeout(() => { this.toast.visible = false }, 4000)
    },

    mostrarToastMulta(monto, descripcion) {
      this.toast = { visible: true, esMulta: true, montoMulta: monto, descripcion, tipo: '', icono: '', titulo: '' }
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

/* ── Variables BookCatalog ───────────────────────────────────────────────── */
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

/* ── Page ────────────────────────────────────────────────────────────────── */
.user-menu {
  min-height: 100vh;
  font-family: 'DM Sans', sans-serif;
  background:
    radial-gradient(ellipse 70% 40% at 5% 0%, rgba(82,183,136,.1) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 90% 100%, rgba(201,144,12,.08) 0%, transparent 50%),
    var(--cream);
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.page-header {
  background: linear-gradient(135deg, #1a4731 0%, #2d6a4f 60%, #3a7d5e 100%);
  padding: 2rem 2rem 1.75rem;
  position: relative;
  overflow: hidden;
}

/* Patrón de puntos igual al BookCatalog */
.page-header::before {
  content: '';
  position: absolute; inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E");
  pointer-events: none;
}

.header-inner {
  position: relative;
  max-width: 900px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.saludo-label {
  font-size: .75rem; font-weight: 600;
  color: rgba(255,255,255,.55);
  text-transform: uppercase; letter-spacing: .1em;
  margin-bottom: .2rem;
}
.saludo-nombre {
  font-family: 'Playfair Display', serif;
  font-size: 1.75rem; font-weight: 700;
  color: #fff; margin-bottom: .4rem; line-height: 1.15;
}
.saludo-meta {
  display: flex; align-items: center; gap: .5rem;
  font-size: .8rem;
}
.meta-chip {
  background: rgba(244,197,66,.18);
  color: var(--gold-light);
  border: 1px solid rgba(244,197,66,.25);
  padding: .15rem .55rem; border-radius: 20px;
  font-weight: 600; font-size: .72rem;
  text-transform: uppercase; letter-spacing: .06em;
}
.meta-sep  { color: rgba(255,255,255,.3); }
.meta-codigo { color: rgba(255,255,255,.6); font-family: monospace; font-size: .78rem; }

/* Stats en header */
.header-stats {
  display: flex; align-items: center; gap: .75rem;
  flex-shrink: 0;
}
.hstat {
  display: flex; flex-direction: column; align-items: center;
  background: rgba(255,255,255,.1);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 10px; padding: .5rem .875rem;
  min-width: 60px;
}
.hstat-warn   { background: rgba(244,197,66,.15); border-color: rgba(244,197,66,.2); }
.hstat-danger { background: rgba(214,40,40,.18);  border-color: rgba(214,40,40,.25); }
.hstat-num {
  font-family: 'Playfair Display', serif;
  font-size: 1.3rem; font-weight: 700; color: #fff; line-height: 1;
}
.hstat-warn .hstat-num   { color: var(--gold-light); }
.hstat-danger .hstat-num { color: #fca5a5; }
.hstat-lbl {
  font-size: .65rem; color: rgba(255,255,255,.55);
  text-transform: uppercase; letter-spacing: .07em; margin-top: 2px;
}
.btn-refresh {
  width: 34px; height: 34px;
  background: rgba(255,255,255,.1);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 8px; color: rgba(255,255,255,.7);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: background .2s, color .2s;
}
.btn-refresh:hover { background: rgba(255,255,255,.18); color: #fff; }

/* ── Banner multas ───────────────────────────────────────────────────────── */
.banner-multas {
  display: flex; align-items: center; gap: 1rem;
  margin: 1.25rem 1.5rem 0;
  padding: .875rem 1.25rem;
  background: #fff3f3;
  border: 1.5px solid #f5c0c0;
  border-left: 4px solid #d62828;
  border-radius: 12px;
  max-width: 900px;
}
.banner-ico { color: #d62828; flex-shrink: 0; display: flex; }
.banner-body { flex: 1; }
.banner-body strong { display: block; font-size: .875rem; color: #d62828; margin-bottom: 2px; }
.banner-body p { font-size: .78rem; color: #6b3333; margin: 0; }
.banner-cta {
  background: #d62828; color: #fff;
  border: none; border-radius: 8px;
  padding: .4rem .9rem; font-size: .8rem; font-weight: 700;
  cursor: pointer; white-space: nowrap; flex-shrink: 0;
  transition: background .2s;
}
.banner-cta:hover { background: #b91c1c; }

/* ── Page body ───────────────────────────────────────────────────────────── */
.page-body {
  padding: 1.5rem;
  max-width: 900px;
  display: flex; flex-direction: column; gap: 1.25rem;
}

/* ── Section card ────────────────────────────────────────────────────────── */
.section-card {
  background: var(--card-bg);
  border: 1.5px solid var(--cream-border);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.section-head {
  padding: 1.1rem 1.375rem .875rem;
  border-bottom: 1.5px solid #eef5f0;
}

.section-title-wrap {
  display: flex; align-items: center; gap: .625rem;
}
.section-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.05rem; font-weight: 700;
  color: var(--green-dark); margin: 0;
}
.section-count {
  background: var(--green-pale);
  color: var(--green-dark);
  font-size: .72rem; font-weight: 700;
  padding: .15rem .5rem; border-radius: 20px;
  border: 1px solid var(--cream-border);
}

/* ── Estados loading/vacío ───────────────────────────────────────────────── */
.estado-loading {
  display: flex; flex-direction: column; align-items: center;
  padding: 2.5rem; gap: .75rem; color: #5a7a5a; font-size: .875rem;
}
.estado-loading-sm { padding: 1.25rem; }
.spinner {
  width: 32px; height: 32px;
  border: 3px solid var(--green-pale); border-top-color: var(--green-mid);
  border-radius: 50%; animation: spin .7s linear infinite;
}
.spinner-sm { width: 20px; height: 20px; border-width: 2px; }
@keyframes spin { to { transform: rotate(360deg); } }

.estado-vacio {
  display: flex; flex-direction: column; align-items: center;
  padding: 3rem 2rem; gap: .5rem; text-align: center;
}
.estado-vacio-sm { padding: 1.5rem; }
.vacio-ico  { color: #b8ddc8; margin-bottom: .25rem; }
.vacio-titulo { font-weight: 700; color: var(--green-dark); font-size: .95rem; margin: 0; }
.vacio-desc   { font-size: .82rem; color: #5a7a5a; margin: 0; }

.btn-catalogo {
  margin-top: .5rem; padding: .5rem 1.1rem;
  background: var(--green-mid); color: #000000;
  border: none; border-radius: 8px;
  font-size: .82rem; font-weight: 700; cursor: pointer;
  transition: background .2s;
}
.btn-catalogo:hover { background: #79b900; }

/* ── Préstamo card ───────────────────────────────────────────────────────── */
.prestamos-lista {
  display: flex; flex-direction: column;
}

.prestamo-card {
  display: flex;
  border-bottom: 1px solid #f1f5f0;
  transition: background .15s;
}
.prestamo-card:last-child { border-bottom: none; }
.prestamo-card:hover      { background: #fafef8; }

/* Indicador lateral */
.prestamo-indicator {
  width: 4px; flex-shrink: 0;
  background: #b8ddc8;
}
.prestamo-warning .prestamo-indicator { background: var(--gold-light); }
.prestamo-overdue .prestamo-indicator { background: #d62828; }

.prestamo-body {
  flex: 1; padding: 1rem 1.25rem; display: flex; flex-direction: column; gap: .5rem;
}

.prestamo-top {
  display: flex; justify-content: space-between;
  align-items: flex-start; gap: 1rem; flex-wrap: wrap;
}

.prestamo-nombre {
  font-weight: 700; font-size: .9rem; color: #1a2e1a; margin: 0;
}
.prestamo-meta {
  display: flex; gap: .4rem; align-items: center; margin-top: 2px;
}
.prestamo-fecha-lbl {
  font-size: .7rem; color: #9ab5a0; text-transform: uppercase; letter-spacing: .05em;
}
.prestamo-fecha { font-size: .75rem; color: #5a7a5a; }

.prestamo-derecha {
  display: flex; align-items: center; gap: .625rem; flex-shrink: 0;
}

/* Status badges */
.status-badge {
  font-size: .68rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .06em; padding: .2rem .55rem; border-radius: 20px;
  white-space: nowrap;
}
.badge-active  { background: var(--green-pale); color: var(--green-dark); border: 1px solid #b8ddc8; }
.badge-warning { background: var(--gold-pale); color: var(--gold-mid); border: 1px solid #fde68a; }
.badge-overdue { background: #fff0f0; color: #b91c1c; border: 1px solid #fca5a5; }

/* Botón devolver */
.btn-devolver {
  padding: .38rem .875rem;
  background: var(--green-mid); color: #fff;
  border: none; border-radius: 8px;
  font-size: .78rem; font-weight: 700;
  cursor: pointer; white-space: nowrap;
  display: inline-flex; align-items: center; gap: .3rem;
  transition: background .2s;
}
.btn-devolver:hover:not(:disabled) { background: #111; }
.btn-devolver:disabled { opacity: .5; cursor: not-allowed; }

.btn-spinner {
  width: 12px; height: 12px;
  border: 2px solid rgba(255,255,255,.3); border-top-color: #fff;
  border-radius: 50%; animation: spin .6s linear infinite;
}

/* Fila de fecha devolución */
.prestamo-devolucion {
  display: flex; align-items: center; gap: .4rem;
  font-size: .75rem; color: #5a7a5a;
}
.dev-label { color: #9ab5a0; }
.dev-fecha  { color: #3d5a3d; }
.dev-urgencia {
  font-weight: 700; font-size: .7rem;
  padding: .1rem .45rem; border-radius: 20px;
}
.dev-warn    { background: var(--gold-pale); color: var(--gold-mid); }
.dev-overdue { background: #fff0f0; color: #b91c1c; }

/* ── Historial colapsable ────────────────────────────────────────────────── */
.historial-toggle {
  width: 100%; padding: 1.1rem 1.375rem .875rem;
  display: flex; justify-content: space-between; align-items: center;
  background: none; border: none; cursor: pointer;
  text-align: left;
  transition: background .15s;
}
.historial-toggle:hover { background: #fafef8; }

.toggle-chevron {
  color: #9ab5a0; flex-shrink: 0;
  transition: transform .28s cubic-bezier(.4,0,.2,1);
}
.chevron-open { transform: rotate(180deg); }

/* Transición historial */
.historial-slide-enter-active { transition: all .3s cubic-bezier(.4,0,.2,1); }
.historial-slide-leave-active { transition: all .2s ease-in; }
.historial-slide-enter-from   { opacity: 0; transform: translateY(-8px); }
.historial-slide-leave-to     { opacity: 0; transform: translateY(-4px); }

.historial-body {
  border-top: 1.5px solid #eef5f0;
  padding: .875rem 1.375rem 1.1rem;
  display: flex; flex-direction: column; gap: .875rem;
}

/* Buscador historial */
.historial-search {
  display: flex; align-items: center; gap: .5rem;
  padding: .5rem .75rem;
  background: var(--cream);
  border: 1.5px solid var(--cream-border); border-radius: 8px;
  color: #9ab5a0;
}
.historial-input {
  flex: 1; border: none; background: none;
  font-family: 'DM Sans', sans-serif; font-size: .82rem;
  color: #1a2e1a; outline: none;
}
.historial-input::placeholder { color: #9ab5a0; }

/* Items historial */
.historial-lista { display: flex; flex-direction: column; gap: .375rem; }

.historial-item {
  display: flex; align-items: center; gap: .75rem;
  padding: .625rem .75rem;
  border-radius: 9px; background: #f8fdf9;
  border: 1px solid #eef5f0;
  transition: background .15s;
}
.historial-item:hover { background: #f0faf3; }

.historial-item-ico {
  width: 28px; height: 28px;
  background: var(--green-pale); border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  color: var(--green-mid); flex-shrink: 0;
}
.historial-item-info { flex: 1; min-width: 0; }
.historial-item-nombre {
  font-size: .82rem; font-weight: 600; color: #1a2e1a;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin: 0;
}
.historial-item-fechas {
  font-size: .72rem; color: #9ab5a0; margin: 1px 0 0;
}
.historial-badge {
  font-size: .65rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .06em; padding: .15rem .5rem; border-radius: 20px;
  background: var(--green-pale); color: var(--green-dark);
  border: 1px solid #b8ddc8; flex-shrink: 0;
}

/* Paginación historial */
.historial-paginacion {
  display: flex; justify-content: center; align-items: center; gap: .75rem;
  padding-top: .5rem; border-top: 1px solid #eef5f0;
}
.pag-btn {
  padding: .35rem .75rem;
  background: #fff; border: 1.5px solid var(--cream-border);
  border-radius: 7px; font-size: .78rem; font-weight: 600;
  color: var(--green-mid); cursor: pointer; font-family: 'DM Sans', sans-serif;
  transition: all .15s;
}
.pag-btn:hover:not(:disabled) { background: #111; color: #fff; border-color: #111; }
.pag-btn:disabled { opacity: .4; cursor: not-allowed; }
.pag-info { font-size: .78rem; color: #5a7a5a; }

/* ── Toasts ──────────────────────────────────────────────────────────────── */
.toast {
  position: fixed; bottom: 2rem; right: 2rem;
  display: flex; align-items: flex-start; gap: .75rem;
  padding: .875rem 1.1rem; border-radius: 12px;
  max-width: 340px; z-index: 9999;
  box-shadow: 0 8px 30px rgba(0,0,0,.15);
  color: #fff; font-size: .82rem;
}
.toast-success { background: #16a34a; }
.toast-error   { background: #d62828; }
.toast-ico     { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }
.toast strong  { display: block; font-size: .875rem; margin-bottom: 2px; }
.toast p       { margin: 0; opacity: .9; font-size: .78rem; }
.toast-close {
  background: none; border: none; color: rgba(255,255,255,.7);
  font-size: 1.1rem; cursor: pointer; margin-left: auto; padding: 0; line-height: 1;
}
.toast-close:hover { color: #fff; }

.toast-multa {
  position: fixed; bottom: 2rem; right: 2rem;
  display: flex; align-items: flex-start; gap: 1rem;
  padding: 1.1rem 1.25rem;
  background: #fff; border: 2px solid #f5c0c0;
  border-left: 5px solid #d62828; border-radius: 14px;
  max-width: 380px; z-index: 9999;
  box-shadow: 0 8px 40px rgba(214,40,40,.15);
}
.toast-multa-ico    { font-size: 1.5rem; flex-shrink: 0; margin-top: 2px; }
.toast-multa-body   { flex: 1; }
.toast-multa-body strong { display: block; font-size: .9rem; font-weight: 800; color: #d62828; margin-bottom: 3px; }
.toast-multa-monto  { font-size: 1.3rem; font-weight: 800; color: #1a1a2e; margin: 0 0 3px; }
.toast-multa-desc   { font-size: .75rem; color: #475569; margin: 0 0 .6rem; line-height: 1.5; }
.toast-multa-cta {
  background: #d62828; color: #fff;
  border: none; border-radius: 7px;
  padding: .35rem .8rem; font-size: .75rem; font-weight: 700;
  cursor: pointer; transition: background .2s;
}
.toast-multa-cta:hover { background: #b91c1c; }
.toast-close-dark { color: #94a3b8; }
.toast-close-dark:hover { color: #1a1a2e; }

.toast-in-enter-active,
.toast-in-leave-active { transition: all .3s ease; }
.toast-in-enter-from,
.toast-in-leave-to { opacity: 0; transform: translateX(16px); }

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 600px) {
  .page-header    { padding: 1.5rem 1.25rem 1.25rem; }
  .header-inner   { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .header-stats   { width: 100%; }
  .saludo-nombre  { font-size: 1.4rem; }
  .page-body      { padding: 1rem; }
  .banner-multas  { margin: 1rem 1rem 0; flex-direction: column; text-align: center; }
  .prestamo-top   { flex-direction: column; }
  .prestamo-derecha { align-self: flex-start; }
  .toast, .toast-multa { left: 1rem; right: 1rem; bottom: 1rem; max-width: none; }
}
</style>