<template>
  <div class="dashboard-container">

    <!-- ===== HEADER ===== -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="user-welcome">
          <h1 class="welcome-title">👋 Hola, {{ userName }}</h1>
          <p class="welcome-subtitle">Panel de usuario · Tipo {{ userType }}</p>
        </div>
        <div class="user-info-card">
          <div class="user-avatar">
            <span class="avatar-icon">👨‍💼</span>
          </div>
          <div class="user-details">
            <div class="user-detail-item">
              <span class="detail-label">Código:</span>
              <span class="detail-value">{{ userCode }}</span>
            </div>
            <div class="user-detail-item">
              <span class="detail-label">Último acceso:</span>
              <span class="detail-value">{{ lastAccess }}</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- ===== BANNER MULTAS PENDIENTES ===== -->
    <div v-if="tieneMultasPendientes" class="banner-multas">
      <span class="banner-icon">⚠️</span>
      <div class="banner-texto">
        <strong>Tienes multas pendientes</strong>
        <p>No puedes solicitar nuevos préstamos. Acude a la biblioteca con tu comprobante de pago.</p>
      </div>
      <button class="banner-btn" @click="$router.push('/user/multas')">Ver mis multas</button>
    </div>

    <!-- ===== CONTENIDO PRINCIPAL ===== -->
    <main class="dashboard-main">

      <!-- Acciones Rápidas -->
      <section class="quick-actions-section">
        <h2 class="section-title">Acciones Rápidas</h2>
        <div class="actions-grid">
          <button @click="navigateTo('/admin/libros')" class="action-card secondary">
            <span class="action-icon">📚</span>
            <span class="action-title">Ver Catálogo</span>
            <span class="action-desc">Explorar libros disponibles</span>
          </button>
          <button @click="navigateTo('/user/multas')" class="action-card"
            :class="tieneMultasPendientes ? 'danger' : 'accent'">
            <span class="action-icon">{{ tieneMultasPendientes ? '⚠️' : '✅' }}</span>
            <span class="action-title">Mis Multas</span>
            <span class="action-desc">
              {{ tieneMultasPendientes ? 'Tienes multas pendientes' : 'Sin multas pendientes' }}
            </span>
          </button>
          <button @click="refreshData" class="action-card info">
            <span class="action-icon">🔄</span>
            <span class="action-title">Actualizar</span>
            <span class="action-desc">Refrescar información</span>
          </button>
        </div>
      </section>

      <!-- Estadísticas -->
      <section class="stats-section">
        <h2 class="section-title">📊 Resumen</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-header">
              <span class="stat-icon">📚</span>
              <span class="stat-title">Activos</span>
            </div>
            <div class="stat-value">{{ activeBooks }}</div>
            <div class="stat-desc">Libros en préstamo</div>
          </div>
          <div class="stat-card stat-warning" v-if="porVencer > 0">
            <div class="stat-header">
              <span class="stat-icon">⏰</span>
              <span class="stat-title">Por vencer</span>
            </div>
            <div class="stat-value">{{ porVencer }}</div>
            <div class="stat-desc">En los próximos 7 días</div>
          </div>
          <div class="stat-card stat-danger" v-if="vencidos > 0">
            <div class="stat-header">
              <span class="stat-icon">🚨</span>
              <span class="stat-title">Vencidos</span>
            </div>
            <div class="stat-value">{{ vencidos }}</div>
            <div class="stat-desc">Requieren devolución urgente</div>
          </div>
        </div>
      </section>

      <!-- Tabla de Préstamos -->
      <section class="resources-section">
        <div class="section-header">
          <h2 class="section-title">Mis Préstamos Activos</h2>
          <div class="section-tabs">
            <button @click="activeTab = 'books'" :class="['tab-btn', { active: activeTab === 'books' }]">
              📚 Libros
            </button>
            <button @click="activeTab = 'areas'" :class="['tab-btn', { active: activeTab === 'areas' }]">
              🏢 Áreas
            </button>
          </div>
        </div>

        <div v-if="loadingPrestamos" class="loading-state">
          <div class="spinner-sm"></div>
          <p>Cargando préstamos...</p>
        </div>

        <div v-else class="resources-table-container">
          <table class="resources-table">
            <thead>
              <tr>
                <th>Recurso</th>
                <th>Fecha Préstamo</th>
                <th>Fecha Devolución</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in filteredResources"
                :key="item.id"
                :class="{ 'row-overdue': item.status === 'overdue', 'row-warning': item.status === 'warning' }"
              >
                <td class="resource-name">
                  <span class="resource-icon">{{ getResourceIcon(item.type) }}</span>
                  {{ item.name }}
                </td>
                <td>{{ formatDate(item.loanDate) }}</td>
                <td>
                  <span class="fecha-devolucion">{{ formatDate(item.returnDate) }}</span>
                  <!-- Badge de días restantes -->
                  <span v-if="item.status === 'warning'" class="badge-vencimiento badge-warning">
                    {{ item.diasRestantes === 0 ? 'Vence hoy' : `${item.diasRestantes}d restantes` }}
                  </span>
                  <span v-if="item.status === 'overdue'" class="badge-vencimiento badge-overdue">
                    {{ Math.abs(item.diasRestantes) }}d vencido
                  </span>
                </td>
                <td>
                  <span :class="['status-badge', item.status]">
                    {{ getStatusText(item.status) }}
                  </span>
                </td>
                <td>
                  <button
                    v-if="item.status === 'active' || item.status === 'warning' || item.status === 'overdue'"
                    @click="returnResource(item)"
                    :disabled="returningLoanId === item.id"
                    class="action-btn return-btn"
                  >
                    <span v-if="returningLoanId === item.id">Procesando...</span>
                    <span v-else>Registrar Devolución</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="filteredResources.length === 0" class="empty-state">
            <span class="empty-icon">📭</span>
            <p>No hay recursos prestados actualmente</p>
          </div>
        </div>
      </section>
    </main>

    <!-- ===== TOAST NORMAL ===== -->
    <transition name="toast-fade">
      <div v-if="toast.visible && !toast.esMulta" class="toast" :class="toast.tipo">
        <span class="toast-icon">{{ toast.icono }}</span>
        <div class="toast-content">
          <strong>{{ toast.titulo }}</strong>
          <p v-if="toast.descripcion">{{ toast.descripcion }}</p>
        </div>
        <button @click="toast.visible = false" class="toast-close">×</button>
      </div>
    </transition>

    <!-- ===== TOAST MULTA (especial, más grande) ===== -->
    <transition name="toast-fade">
      <div v-if="toast.visible && toast.esMulta" class="toast toast-multa">
        <span class="toast-icon-multa">⚠️</span>
        <div class="toast-content-multa">
          <strong class="toast-multa-titulo">Multa registrada</strong>
          <p class="toast-multa-monto">{{ toast.montoMulta }}</p>
          <p class="toast-multa-desc">{{ toast.descripcion }}</p>
          <button class="toast-multa-btn" @click="irAMisMultas">Ver mis multas →</button>
        </div>
        <button @click="toast.visible = false" class="toast-close-multa">×</button>
      </div>
    </transition>

  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { prestamoLibroService } from '@/services/PrestamoLibro'
import { multasService } from '@/services/multas'
import {
  RESOURCE_ICONS,
  RESOURCE_TYPE,
  ACTIVITY_ICONS
} from '@/utils/resourseHelper'

export default {
  name: 'UserMenu',

  data() {
    return {
      prestamos: [],
      loadingPrestamos: false,
      returningLoanId: null,
      activeTab: 'books',
      tieneMultasPendientes: false,

      toast: {
        visible: false,
        tipo: '',
        icono: '',
        titulo: '',
        descripcion: '',
        esMulta: false,
        montoMulta: ''
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

    lastAccess() {
      return new Date().toLocaleDateString('es-MX', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
      })
    },

    filteredResources() {
      if (this.activeTab === 'books') return this.prestamos
      return []
    },

    activeBooks() {
      return this.prestamos.filter(p =>
        p.status === 'active' || p.status === 'warning' || p.status === 'overdue'
      ).length
    },

    porVencer() {
      return this.prestamos.filter(p => p.status === 'warning').length
    },

    vencidos() {
      return this.prestamos.filter(p => p.status === 'overdue').length
    }
  },

  mounted() {
    this.loadPrestamos()
    this.verificarMultasPendientes()
  },

  methods: {

    // ── Carga de préstamos ──────────────────────────────────────────────
    async loadPrestamos() {
      try {
        this.loadingPrestamos = true
        // soloVigentes = false para mostrar activos + vencidos sin devolver
        this.prestamos = await prestamoLibroService.getPrestamosUsuario(false)
      } catch (error) {
        console.error('Error cargando préstamos:', error)
        this.mostrarToast('error', '❌', 'Error', 'No se pudieron cargar los préstamos')
      } finally {
        this.loadingPrestamos = false
      }
    },

    // ── Verificar multas pendientes ─────────────────────────────────────
    async verificarMultasPendientes() {
      try {
        const userId = this.authStore.userId
        if (!userId) return
        // Trae solo pendientes (solo_pendientes=true por defecto en el endpoint)
        const multas = await multasService.getMultasByUsuario(userId)
        this.tieneMultasPendientes = Array.isArray(multas) && multas.length > 0

        // Actualizar el store para que otros componentes lo sepan
        if (this.authStore.actualizarEstadoMultas) {
          this.authStore.actualizarEstadoMultas(multas)
        }
      } catch {
        // Silencioso — no bloquear el dashboard si falla
      }
    },

    // ── Devolución de libro ─────────────────────────────────────────────
    async returnResource(resource) {
      try {
        this.returningLoanId = resource.id

        // La respuesta ahora es: { prestamo, multa_generada, mensaje }
        const respuesta = await prestamoLibroService.devolverPrestamo(resource.id)

        // Actualizar lista local
        await this.loadPrestamos()

        if (respuesta.multa_generada) {
          // ── Devolución tardía: mostrar toast de multa ──
          const monto = new Intl.NumberFormat('es-MX', {
            style: 'currency', currency: 'MXN'
          }).format(respuesta.multa_generada.costo_monetario)

          this.mostrarToastMulta(
            monto,
            `${respuesta.multa_generada.dias_excedidos} día(s) de retraso. ` +
            `Preséntate en la biblioteca con tu comprobante de pago para liquidar la multa.`
          )

          // Actualizar banner de multas
          this.tieneMultasPendientes = true
          if (this.authStore.actualizarEstadoMultas) {
            this.authStore.actualizarEstadoMultas([{ estado_multa_id: 1 }])
          }
        } else {
          // ── Devolución a tiempo ──
          this.mostrarToast('success', '✅', 'Devolución registrada', respuesta.mensaje)
        }

      } catch (error) {
        const msg = error.response?.data?.detail || 'Error al registrar devolución'
        this.mostrarToast('error', '❌', 'Error', msg)
      } finally {
        this.returningLoanId = null
      }
    },

    // ── Navegación ──────────────────────────────────────────────────────
    navigateTo(route) { this.$router.push(route) },

    irAMisMultas() {
      this.toast.visible = false
      this.$router.push('/user/multas')
    },

    refreshData() {
      this.loadPrestamos()
      this.verificarMultasPendientes()
    },

    // ── Toasts ──────────────────────────────────────────────────────────
    mostrarToast(tipo, icono, titulo, descripcion = '') {
      this.toast = {
        visible: true,
        tipo: `toast-${tipo}`,
        icono,
        titulo,
        descripcion,
        esMulta: false,
        montoMulta: ''
      }
      setTimeout(() => { this.toast.visible = false }, 4000)
    },

    mostrarToastMulta(monto, descripcion) {
      this.toast = {
        visible: true,
        esMulta: true,
        montoMulta: monto,
        descripcion,
        tipo: '',
        icono: '',
        titulo: ''
      }
      // El toast de multa persiste más tiempo y el usuario lo cierra manualmente
    },

    // ── Helpers de tabla ────────────────────────────────────────────────
    formatDate(dateString) {
      if (!dateString) return '—'
      return new Date(dateString).toLocaleDateString('es-MX')
    },

    getStatusText(status) {
      const statuses = {
        active:    'Activo',
        warning:   'Por vencer',
        overdue:   'Vencido',
        completed: 'Devuelto'
      }
      return statuses[status] || status
    },

    getResourceIcon(type) {
      return RESOURCE_ICONS[type] || '📦'
    }
  }
}
</script>

<style scoped>
/* ── Base ────────────────────────────────────────────────────────────────── */
.dashboard-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.dashboard-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px 40px;
  border-bottom-left-radius: 30px;
  border-bottom-right-radius: 30px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}
.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 30px;
}
.welcome-title  { font-size: 28px; font-weight: 700; margin-bottom: 8px; }
.welcome-subtitle { font-size: 16px; opacity: 0.9; }

.user-info-card {
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  min-width: 260px;
}
.avatar-icon {
  font-size: 40px;
  background: rgba(255,255,255,0.2);
  padding: 15px;
  border-radius: 50%;
  display: block;
}
.user-details   { display: flex; flex-direction: column; gap: 8px; }
.user-detail-item { display: flex; gap: 10px; font-size: 14px; }
.detail-label   { font-weight: 600; min-width: 80px; }
.detail-value   { opacity: 0.9; }

/* ── Banner multas ───────────────────────────────────────────────────────── */
.banner-multas {
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: 1200px;
  margin: 1.5rem auto 0;
  padding: 1rem 1.5rem;
  background: #fff3f3;
  border: 1.5px solid #f5c0c0;
  border-left: 5px solid #d62828;
  border-radius: 12px;
}
.banner-icon    { font-size: 1.5rem; flex-shrink: 0; }
.banner-texto   { flex: 1; }
.banner-texto strong { display: block; color: #d62828; font-size: 0.95rem; margin-bottom: 2px; }
.banner-texto p  { margin: 0; font-size: 0.82rem; color: #6b3333; }
.banner-btn {
  background: #d62828; color: #fff;
  border: none; border-radius: 8px;
  padding: 0.45rem 1rem; font-size: 0.82rem; font-weight: 600;
  cursor: pointer; white-space: nowrap;
  transition: background 0.2s;
}
.banner-btn:hover { background: #b91c1c; }

/* ── Main ────────────────────────────────────────────────────────────────── */
.dashboard-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}
.section-title {
  font-size: 20px; font-weight: 700;
  color: #2d3436; margin-bottom: 20px;
}

/* ── Acciones rápidas ────────────────────────────────────────────────────── */
.quick-actions-section { margin-bottom: 40px; }
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}
.action-card {
  background: white; border: none; border-radius: 16px;
  padding: 25px; text-align: left; cursor: pointer;
  display: flex; flex-direction: column; gap: 12px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
}
.action-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.12); }
.action-card.secondary { border-left: 5px solid #764ba2; }
.action-card.accent    { border-left: 5px solid #2ecc71; }
.action-card.info      { border-left: 5px solid #3498db; }
.action-card.danger    { border-left: 5px solid #d62828; background: #fff9f9; }
.action-icon  { font-size: 28px; }
.action-title { font-size: 18px; font-weight: 600; color: #2d3436; }
.action-desc  { font-size: 14px; color: #636e72; }

/* ── Stats ───────────────────────────────────────────────────────────────── */
.stats-section { margin-bottom: 40px; }
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
}
.stat-card {
  background: white; border-radius: 16px;
  padding: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.08);
}
.stat-card.stat-warning { background: #fff8e1; border-left: 4px solid #f59e0b; }
.stat-card.stat-danger  { background: #fff3f3; border-left: 4px solid #d62828; }
.stat-header  { display: flex; align-items: center; gap: 10px; margin-bottom: 15px; }
.stat-icon    { font-size: 24px; }
.stat-title   { font-size: 14px; font-weight: 600; color: #636e72; text-transform: uppercase; }
.stat-value   { font-size: 36px; font-weight: 700; color: #2d3436; line-height: 1; }
.stat-desc    { font-size: 13px; color: #636e72; margin-top: 8px; }

/* ── Tabla recursos ──────────────────────────────────────────────────────── */
.resources-section {
  background: white; border-radius: 16px;
  padding: 30px; margin-bottom: 40px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.08);
}
.section-header {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 25px; flex-wrap: wrap; gap: 15px;
}
.section-tabs   { display: flex; gap: 10px; background: #f8f9fa; padding: 5px; border-radius: 12px; }
.tab-btn {
  padding: 10px 20px; border: none; background: transparent;
  border-radius: 8px; font-size: 14px; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
}
.tab-btn.active { background: white; color: #667eea; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }

.resources-table-container { overflow-x: auto; }
.resources-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.resources-table th {
  background: #f8f9fa; padding: 15px;
  text-align: left; font-weight: 600;
  color: #636e72; border-bottom: 2px solid #e9ecef;
}
.resources-table td {
  padding: 15px; border-bottom: 1px solid #e9ecef; vertical-align: middle;
}

/* Filas con color por estado */
.row-warning { background: #fffbeb !important; }
.row-overdue { background: #fff5f5 !important; }

.resource-name  { display: flex; align-items: center; gap: 10px; font-weight: 500; }
.resource-icon  { font-size: 20px; }
.fecha-devolucion { display: block; }

/* Badges de vencimiento */
.badge-vencimiento {
  display: inline-block; margin-top: 4px;
  font-size: 11px; font-weight: 700;
  padding: 2px 8px; border-radius: 20px;
}
.badge-warning {
  background: #fef3c7; color: #92400e;
  border: 1px solid #fcd34d;
}
.badge-overdue {
  background: #fee2e2; color: #b91c1c;
  border: 1px solid #fca5a5;
}

/* Status badges en tabla */
.status-badge {
  padding: 6px 12px; border-radius: 20px;
  font-size: 12px; font-weight: 600; text-transform: uppercase;
}
.status-badge.active    { background: #d1ecf1; color: #0c5460; }
.status-badge.warning   { background: #fff3cd; color: #856404; }
.status-badge.overdue   { background: #f8d7da; color: #721c24; }
.status-badge.completed { background: #d4edda; color: #155724; }
.status-badge.pending   { background: #fff3cd; color: #856404; }

.action-btn {
  padding: 8px 16px; border: none; border-radius: 8px;
  font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.return-btn           { background: #cce5ff; color: #004085; }
.return-btn:hover     { background: #b8daff; }
.return-btn:disabled  { opacity: 0.5; cursor: not-allowed; }

.loading-state  { text-align: center; padding: 3rem; color: #636e72; }
.spinner-sm {
  width: 32px; height: 32px;
  border: 3px solid #e9ecef; border-top-color: #667eea;
  border-radius: 50%; animation: spin 0.7s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state  { text-align: center; padding: 40px; color: #636e72; }
.empty-icon   { font-size: 48px; margin-bottom: 15px; display: block; }

/* ── Toast normal ────────────────────────────────────────────────────────── */
.toast {
  position: fixed; bottom: 2rem; right: 2rem;
  display: flex; align-items: flex-start; gap: 0.75rem;
  padding: 1rem 1.25rem; border-radius: 12px;
  max-width: 360px; z-index: 9999;
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
  color: #fff;
}
.toast-success  { background: #16a34a; }
.toast-error    { background: #d62828; }
.toast-info     { background: #6366f1; }
.toast-icon     { font-size: 1.25rem; flex-shrink: 0; margin-top: 2px; }
.toast-content strong { display: block; font-size: 0.9rem; margin-bottom: 2px; }
.toast-content p      { margin: 0; font-size: 0.8rem; opacity: 0.9; }
.toast-close {
  background: none; border: none; color: rgba(255,255,255,0.7);
  font-size: 1.2rem; cursor: pointer; margin-left: auto; padding: 0;
  line-height: 1;
}
.toast-close:hover { color: #fff; }

/* ── Toast multa (especial) ──────────────────────────────────────────────── */
.toast-multa {
  position: fixed; bottom: 2rem; right: 2rem;
  display: flex; align-items: flex-start; gap: 1rem;
  padding: 1.25rem 1.5rem;
  background: #fff;
  border: 2px solid #f5c0c0;
  border-left: 5px solid #d62828;
  border-radius: 14px;
  max-width: 400px; z-index: 9999;
  box-shadow: 0 8px 40px rgba(214, 40, 40, 0.2);
}
.toast-icon-multa   { font-size: 1.75rem; flex-shrink: 0; margin-top: 2px; }
.toast-content-multa { flex: 1; }
.toast-multa-titulo { display: block; font-size: 1rem; font-weight: 800; color: #d62828; margin-bottom: 4px; }
.toast-multa-monto  { font-size: 1.4rem; font-weight: 800; color: #1a1a2e; margin: 0 0 4px; }
.toast-multa-desc   { font-size: 0.8rem; color: #475569; margin: 0 0 0.75rem; line-height: 1.5; }
.toast-multa-btn {
  background: #d62828; color: #fff;
  border: none; border-radius: 8px;
  padding: 0.4rem 0.9rem; font-size: 0.8rem; font-weight: 700;
  cursor: pointer; transition: background 0.2s;
}
.toast-multa-btn:hover { background: #b91c1c; }
.toast-close-multa {
  background: none; border: none;
  font-size: 1.3rem; color: #94a3b8;
  cursor: pointer; padding: 0; line-height: 1;
}
.toast-close-multa:hover { color: #1a1a2e; }

/* ── Transición toast ────────────────────────────────────────────────────── */
.toast-fade-enter-active,
.toast-fade-leave-active { transition: all 0.3s ease; }
.toast-fade-enter-from,
.toast-fade-leave-to     { opacity: 0; transform: translateX(20px); }

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .dashboard-header { padding: 20px; border-radius: 0 0 20px 20px; }
  .header-content   { flex-direction: column; text-align: center; }
  .user-info-card   { width: 100%; justify-content: center; }
  .actions-grid     { grid-template-columns: 1fr; }
  .stats-grid       { grid-template-columns: repeat(2, 1fr); }
  .banner-multas    { flex-direction: column; text-align: center; margin: 1rem; }
  .toast, .toast-multa { left: 1rem; right: 1rem; bottom: 1rem; max-width: none; }
}
</style>