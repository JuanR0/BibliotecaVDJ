<template>
  <div class="mis-multas">

    <!-- ===== BANNER DE BLOQUEO ===== -->
    <div v-if="tieneMultasPendientes" class="banner-bloqueo">
      <div class="banner-icono">⚠</div>
      <div class="banner-contenido">
        <p class="banner-titulo">Tienes multas pendientes</p>
        <p class="banner-descripcion">
          No puedes solicitar nuevos préstamos hasta que tus multas sean liquidadas.
          Acude a la biblioteca con tu comprobante de pago.
        </p>
      </div>
    </div>

    <!-- ===== ENCABEZADO ===== -->
    <div class="multas-header">
      <div class="header-texto">
        <h1 class="titulo">Mis Multas</h1>
        <p class="subtitulo">Historial de cargos registrados en tu cuenta</p>
      </div>

      <div class="header-stats">
        <div class="stat-chip" :class="{ 'chip-alerta': multasPendientes.length > 0 }">
          <span class="stat-num">{{ multasPendientes.length }}</span>
          <span class="stat-label">Pendientes</span>
        </div>
        <div class="stat-chip chip-ok">
          <span class="stat-num">{{ multasLiquidadas.length }}</span>
          <span class="stat-label">Liquidadas</span>
        </div>
      </div>
    </div>

    <!-- ===== FILTROS ===== -->
    <div class="multas-filtros">
      <select v-model="filtroEstado" class="filtro-select">
        <option value="">Todos los estados</option>
        <option value="1">Pendiente</option>
        <option value="2">Liquidada</option>
        <option value="3">Cancelada</option>
      </select>
    </div>

    <!-- ===== LOADING ===== -->
    <div v-if="isLoading" class="multas-loading">
      <div class="spinner"></div>
      <p>Cargando tus multas...</p>
    </div>

    <!-- ===== ERROR ===== -->
    <div v-else-if="error" class="multas-error">
      <span class="error-icono">✕</span>
      <p>{{ error }}</p>
      <button class="btn-reintentar" @click="cargar">Reintentar</button>
    </div>

    <!-- ===== LISTA VACÍA ===== -->
    <div v-else-if="multasFiltradas.length === 0" class="multas-vacio">
      <div class="vacio-icono">✓</div>
      <p class="vacio-titulo">Sin multas registradas</p>
      <p class="vacio-descripcion">Tu cuenta está al corriente.</p>
    </div>

    <!-- ===== LISTA DE MULTAS ===== -->
    <div v-else class="multas-lista">
      <div
        v-for="multa in multasFiltradas"
        :key="multa.id"
        class="multa-card"
        :class="getEstadoClase(multa.estado_multa_id)"
      >
        <!-- Indicador de estado lateral -->
        <div class="card-estado-barra"></div>

        <div class="card-contenido">
          <!-- Fila superior -->
          <div class="card-fila-top">
            <div class="card-info-principal">
              <span class="card-recurso">{{ multa.tipo_recurso_multa_nombre || 'Recurso' }}</span>
              <span
                class="card-badge"
                :class="getEstadoClase(multa.estado_multa_id)"
              >
                {{ multa.estado_multa_nombre || getEstadoNombre(multa.estado_multa_id) }}
              </span>
            </div>
            <div class="card-costo">
              {{ formatearCosto(multa.costo_monetario) }}
            </div>
          </div>

          <!-- Observaciones -->
          <p v-if="multa.observaciones" class="card-observaciones">
            {{ multa.observaciones }}
          </p>

          <!-- Fila de fechas -->
          <div class="card-fila-fechas">
            <div class="card-fecha-item">
              <span class="fecha-label">Fecha de multa</span>
              <span class="fecha-valor">{{ formatearFecha(multa.fecha_multa) }}</span>
            </div>
            <div v-if="multa.fecha_ultimo_cambio_estado" class="card-fecha-item">
              <span class="fecha-label">Último cambio</span>
              <span class="fecha-valor">{{ formatearFecha(multa.fecha_ultimo_cambio_estado) }}</span>
            </div>
            <div class="card-fecha-item">
              <span class="fecha-label">Registrada por</span>
              <span class="fecha-valor">{{ multa.usuario_multa_nombre || '—' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== TOAST ===== -->
    <transition name="toast">
      <div v-if="toast.visible" class="toast" :class="toast.tipo">
        {{ toast.mensaje }}
      </div>
    </transition>

  </div>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMultas } from '@/composables/useMultas'

const authStore = useAuthStore()

const {
  multas,
  isLoading,
  error,
  tieneMultasPendientes,
  multasPendientes,
  multasLiquidadas,
  cargarMisMultas,
  getEstadoNombre,
  getEstadoClase,
  formatearCosto,
  formatearFecha,
  filtrarMultas
} = useMultas()

// ===== FILTROS =====
const filtroEstado = ref('')

const multasFiltradas = computed(() =>
  filtrarMultas({
    estado_multa_id: filtroEstado.value !== '' ? filtroEstado.value : undefined
  })
)

// ===== TOAST =====
const toast = ref({ visible: false, mensaje: '', tipo: 'toast-info' })

const mostrarToast = (mensaje, tipo = 'toast-info') => {
  toast.value = { visible: true, mensaje, tipo }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

// ===== CARGA INICIAL =====
const cargar = async () => {
  try {
    const userId = authStore.userId
    if (!userId) {
      mostrarToast('No se pudo identificar al usuario.', 'toast-error')
      return
    }
    await cargarMisMultas(userId)
  } catch {
    mostrarToast('Error al cargar las multas. Intenta de nuevo.', 'toast-error')
  }
}

onMounted(cargar)
</script>


<style scoped>
/* ============================================
   MIS MULTAS — Estilos
   Paleta: neutros con acento rojo para alerta
   ============================================ */

.mis-multas {
  max-width: 860px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  font-family: 'Segoe UI', system-ui, sans-serif;
  color: #1a1a2e;
}

/* ===== BANNER BLOQUEO ===== */
.banner-bloqueo {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  background: #fff3f3;
  border: 1.5px solid #f5c0c0;
  border-left: 5px solid #d62828;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.75rem;
}

.banner-icono {
  font-size: 1.5rem;
  color: #d62828;
  flex-shrink: 0;
  margin-top: 2px;
}

.banner-titulo {
  font-weight: 700;
  font-size: 0.95rem;
  color: #d62828;
  margin: 0 0 0.25rem;
}

.banner-descripcion {
  font-size: 0.85rem;
  color: #6b3333;
  margin: 0;
  line-height: 1.5;
}

/* ===== HEADER ===== */
.multas-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.titulo {
  font-size: 1.6rem;
  font-weight: 800;
  margin: 0 0 0.25rem;
  color: #1a1a2e;
}

.subtitulo {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

.header-stats {
  display: flex;
  gap: 0.75rem;
}

.stat-chip {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f1f5f9;
  border-radius: 10px;
  padding: 0.5rem 1rem;
  min-width: 64px;
  border: 1.5px solid #e2e8f0;
}

.stat-chip.chip-alerta {
  background: #fff3f3;
  border-color: #f5c0c0;
}

.stat-chip.chip-ok {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.stat-num {
  font-size: 1.4rem;
  font-weight: 800;
  line-height: 1;
  color: #1a1a2e;
}

.chip-alerta .stat-num { color: #d62828; }
.chip-ok .stat-num { color: #16a34a; }

.stat-label {
  font-size: 0.7rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 2px;
}

/* ===== FILTROS ===== */
.multas-filtros {
  margin-bottom: 1.5rem;
}

.filtro-select {
  padding: 0.5rem 0.875rem;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #334155;
  background: #fff;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
}

.filtro-select:focus {
  border-color: #6366f1;
}

/* ===== LOADING ===== */
.multas-loading {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===== ERROR ===== */
.multas-error {
  text-align: center;
  padding: 3rem;
  color: #d62828;
}

.error-icono {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.5rem;
}

.btn-reintentar {
  margin-top: 1rem;
  padding: 0.5rem 1.25rem;
  background: #d62828;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-reintentar:hover { background: #b91c1c; }

/* ===== VACÍO ===== */
.multas-vacio {
  text-align: center;
  padding: 4rem 2rem;
  color: #64748b;
}

.vacio-icono {
  font-size: 3rem;
  color: #16a34a;
  margin-bottom: 0.75rem;
}

.vacio-titulo {
  font-size: 1.1rem;
  font-weight: 700;
  color: #334155;
  margin: 0 0 0.25rem;
}

.vacio-descripcion {
  font-size: 0.875rem;
  margin: 0;
}

/* ===== CARDS ===== */
.multas-lista {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.multa-card {
  display: flex;
  background: #fff;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.multa-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.07);
}

/* Barra lateral de color por estado */
.card-estado-barra {
  width: 5px;
  flex-shrink: 0;
  background: #e2e8f0;
}

.multa-card.estado-pendiente .card-estado-barra { background: #d62828; }
.multa-card.estado-liquidada .card-estado-barra { background: #16a34a; }
.multa-card.estado-cancelada .card-estado-barra { background: #64748b; }

.card-contenido {
  flex: 1;
  padding: 1rem 1.25rem;
}

.card-fila-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.card-info-principal {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.card-recurso {
  font-weight: 700;
  font-size: 0.975rem;
  color: #1a1a2e;
}

/* Badge de estado */
.card-badge {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
}

.card-badge.estado-pendiente {
  background: #fff3f3;
  color: #d62828;
  border: 1px solid #f5c0c0;
}

.card-badge.estado-liquidada {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}

.card-badge.estado-cancelada {
  background: #f8fafc;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.card-costo {
  font-size: 1.2rem;
  font-weight: 800;
  color: #1a1a2e;
  white-space: nowrap;
}

.card-observaciones {
  font-size: 0.85rem;
  color: #475569;
  margin: 0.25rem 0 0.75rem;
  line-height: 1.5;
}

.card-fila-fechas {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
  padding-top: 0.625rem;
  border-top: 1px solid #f1f5f9;
}

.card-fecha-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.fecha-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
  font-weight: 600;
}

.fecha-valor {
  font-size: 0.8rem;
  color: #475569;
  font-weight: 500;
}

/* ===== TOAST ===== */
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 0.75rem 1.25rem;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #fff;
  z-index: 9999;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.toast-info    { background: #6366f1; }
.toast-error   { background: #d62828; }
.toast-success { background: #16a34a; }

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

/* ===== RESPONSIVE ===== */
@media (max-width: 600px) {
  .multas-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .card-fila-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .card-costo {
    font-size: 1rem;
  }
}
</style>