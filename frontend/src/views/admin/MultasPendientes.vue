<template>
  <div class="multas-admin">

    <!-- ===== HEADER ===== -->
    <div class="page-header">
      <div class="header-texto">
        <h1 class="titulo">Multas Pendientes</h1>
        <p class="subtitulo">Gestión y liquidación de multas de usuarios</p>
      </div>
      <div class="header-derecha">
        <div class="header-stats">
          <div class="stat-chip chip-alerta">
            <span class="stat-num">{{ multas.length }}</span>
            <span class="stat-label">Pendientes</span>
          </div>
          <div class="stat-chip chip-total">
            <span class="stat-num">{{ totalRecaudable }}</span>
            <span class="stat-label">Total a cobrar</span>
          </div>
        </div>
        <button class="btn-crear-multa" @click="abrirModalCrear">
          + Registrar Multa
        </button>
      </div>
    </div>

    <!-- ===== FILTROS ===== -->
    <div class="filtros-bar">
      <input
        v-model="busqueda"
        type="text"
        placeholder="Buscar por usuario, recurso u observaciones..."
        class="input-busqueda"
      />
      <button @click="cargar" class="btn-refrescar" :disabled="isLoading">
        {{ isLoading ? 'Cargando...' : '↻ Refrescar' }}
      </button>
    </div>

    <!-- ===== LOADING ===== -->
    <div v-if="isLoading" class="estado-loading">
      <div class="spinner"></div>
      <p>Cargando multas pendientes...</p>
    </div>

    <!-- ===== ERROR ===== -->
    <div v-else-if="error" class="estado-error">
      <p>{{ error }}</p>
      <button @click="cargar" class="btn-retry">Reintentar</button>
    </div>

    <!-- ===== VACÍO ===== -->
    <div v-else-if="multasFiltradas.length === 0" class="estado-vacio">
      <div class="vacio-icono">✓</div>
      <p class="vacio-titulo">Sin multas pendientes</p>
      <p class="vacio-desc">Todos los usuarios están al corriente.</p>
    </div>

    <!-- ===== TABLA ===== -->
    <div v-else class="tabla-wrapper">
      <table class="tabla-multas">
        <thead>
          <tr>
            <th>#</th>
            <th>Usuario multado</th>
            <th>Tipo de recurso</th>
            <th>Monto</th>
            <th>Fecha multa</th>
            <th>Observaciones</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="multa in multasFiltradas" :key="multa.id">
            <td class="td-id">{{ multa.id }}</td>
            <td class="td-usuario">
              <span class="usuario-nombre">{{ multa.usuario_multado_nombre || '—' }}</span>
            </td>
            <td>
              <span class="chip-recurso">{{ multa.tipo_recurso_multa_nombre || '—' }}</span>
            </td>
            <td class="td-monto">{{ formatearCosto(multa.costo_monetario) }}</td>
            <td class="td-fecha">{{ formatearFecha(multa.fecha_multa) }}</td>
            <td class="td-obs">
              <span class="obs-texto" :title="multa.observaciones">
                {{ truncar(multa.observaciones, 60) }}
              </span>
            </td>
            <td>
              <button
                class="btn-liquidar"
                @click="abrirModalLiquidar(multa)"
                :disabled="liquidandoId === multa.id"
              >
                {{ liquidandoId === multa.id ? 'Procesando...' : 'Liquidar' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ===================================================
         MODAL: LIQUIDAR MULTA
    ==================================================== -->
    <div v-if="modalLiquidar.visible" class="modal-overlay" @click.self="cerrarModalLiquidar">
      <div class="modal">
        <div class="modal-header">
          <h3>Liquidar Multa #{{ modalLiquidar.multa?.id }}</h3>
          <button class="modal-close" @click="cerrarModalLiquidar">×</button>
        </div>
        <div class="modal-body">
          <div class="modal-info-row">
            <span class="info-label">Usuario:</span>
            <span class="info-valor">{{ modalLiquidar.multa?.usuario_multado_nombre }}</span>
          </div>
          <div class="modal-info-row">
            <span class="info-label">Monto:</span>
            <span class="info-valor monto-highlight">
              {{ formatearCosto(modalLiquidar.multa?.costo_monetario) }}
            </span>
          </div>
          <div class="modal-info-row">
            <span class="info-label">Recurso:</span>
            <span class="info-valor">{{ modalLiquidar.multa?.tipo_recurso_multa_nombre }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">Observaciones de liquidación</label>
            <textarea
              v-model="modalLiquidar.observaciones"
              class="form-textarea"
              placeholder="Ej: Pago recibido en caja. Comprobante #12345"
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancelar" @click="cerrarModalLiquidar">Cancelar</button>
          <button
            class="btn-confirmar-liquidar"
            @click="confirmarLiquidacion"
            :disabled="liquidandoId !== null"
          >
            {{ liquidandoId ? 'Procesando...' : '✓ Confirmar Liquidación' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ===================================================
         MODAL: CREAR MULTA MANUAL
    ==================================================== -->
    <div v-if="modalCrear.visible" class="modal-overlay" @click.self="cerrarModalCrear">
      <div class="modal modal-crear">
        <div class="modal-header">
          <h3>Registrar Multa Manual</h3>
          <button class="modal-close" @click="cerrarModalCrear">×</button>
        </div>

        <div class="modal-body">

          <!-- Buscar usuario -->
          <div class="form-group">
            <label class="form-label">
              Usuario a multar <span class="required">*</span>
            </label>
            <div class="usuario-search-wrap">
              <input
                v-model="modalCrear.busquedaUsuario"
                type="text"
                class="form-input"
                placeholder="Buscar por nombre o código universitario..."
                @input="limpiarSeleccion"
                :disabled="!!modalCrear.usuarioSeleccionado"
              />

              <!-- Dropdown resultados -->
              <div
                v-if="modalCrear.busquedaUsuario.length >= 2
                      && usuariosFiltrados.length > 0
                      && !modalCrear.usuarioSeleccionado"
                class="usuario-dropdown"
              >
                <div
                  v-for="u in usuariosFiltrados"
                  :key="u.id"
                  class="usuario-option"
                  @mousedown.prevent="seleccionarUsuario(u)"
                >
                  <span class="option-nombre">{{ u.nombre_completo }}</span>
                  <span class="option-codigo">
                    {{ u.codigo_universitario || `ID: ${u.id}` }}
                  </span>
                </div>
              </div>

              <div
                v-if="modalCrear.busquedaUsuario.length >= 2
                      && usuariosFiltrados.length === 0
                      && !modalCrear.usuarioSeleccionado
                      && !cargandoUsuarios"
                class="usuario-dropdown"
              >
                <div class="option-vacio">Sin resultados para "{{ modalCrear.busquedaUsuario }}"</div>
              </div>

              <div v-if="cargandoUsuarios" class="usuario-dropdown">
                <div class="option-vacio">Cargando usuarios...</div>
              </div>
            </div>

            <!-- Chip de usuario seleccionado -->
            <div v-if="modalCrear.usuarioSeleccionado" class="usuario-seleccionado">
              <div class="usuario-sel-info">
                <span class="usuario-sel-nombre">
                  {{ modalCrear.usuarioSeleccionado.nombre_completo }}
                </span>
                <span class="usuario-sel-codigo">
                  {{ modalCrear.usuarioSeleccionado.codigo_universitario
                     || `ID: ${modalCrear.usuarioSeleccionado.id}` }}
                </span>
              </div>
              <button
                class="btn-quitar-usuario"
                @click="quitarUsuario"
                title="Cambiar usuario"
              >×</button>
            </div>
          </div>

          <!-- Tipo de recurso -->
          <div class="form-group">
            <label class="form-label">
              Tipo de recurso <span class="required">*</span>
            </label>
            <select v-model="modalCrear.form.tipo_recurso_multa_id" class="form-select">
              <option value="" disabled>Selecciona un tipo</option>
              <option v-for="tipo in tiposRecurso" :key="tipo.id" :value="tipo.id">
                {{ tipo.nombre }}
              </option>
            </select>
          </div>

          <!-- Tipo de pago -->
          <div class="form-group">
            <label class="form-label">
              Tipo de pago <span class="required">*</span>
            </label>
            <select v-model="modalCrear.form.tipo_pago_id" class="form-select">
              <option value="" disabled>Selecciona tipo de pago</option>
              <option v-for="tipo in tiposPago" :key="tipo.id" :value="tipo.id">
                {{ tipo.nombre }}
              </option>
            </select>
          </div>

          <!-- Monto -->
          <div class="form-group">
            <label class="form-label">Costo monetario (MXN)</label>
            <div class="input-prefix-wrap">
              <span class="input-prefix">$</span>
              <input
                v-model.number="modalCrear.form.costo_monetario"
                type="number"
                min="0"
                step="0.01"
                class="form-input input-con-prefix"
                placeholder="0.00"
              />
            </div>
          </div>

          <!-- Observaciones -->
          <div class="form-group">
            <label class="form-label">Observaciones</label>
            <textarea
              v-model="modalCrear.form.observaciones"
              class="form-textarea"
              placeholder="Describe el motivo de la multa..."
              rows="3"
            ></textarea>
          </div>

          <!-- Error de validación -->
          <div v-if="modalCrear.errorValidacion" class="error-validacion">
            ⚠ {{ modalCrear.errorValidacion }}
          </div>

        </div>

        <div class="modal-footer">
          <button
            class="btn-cancelar"
            @click="cerrarModalCrear"
            :disabled="creandoMulta"
          >
            Cancelar
          </button>
          <button
            class="btn-confirmar-crear"
            @click="confirmarCrearMulta"
            :disabled="creandoMulta"
          >
            <span v-if="creandoMulta" class="spinner-mini"></span>
            {{ creandoMulta ? 'Registrando...' : '+ Registrar Multa' }}
          </button>
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
import { useMultas } from '@/composables/useMultas'
import { userService } from '@/services/users'

const {
  multas,
  isLoading,
  error,
  cargarMultasPendientes,
  liquidarMulta,
  crearMulta,
  formatearCosto,
  formatearFecha
} = useMultas()

// ── Catálogos ──────────────────────────────────────────────────────────────
// IDs confirmados desde la BD (tabla tipos_recurso_multa)
const tiposRecurso = [
  { id: 1, nombre: 'Libro' },
  { id: 2, nombre: 'Equipo de cómputo' },
  { id: 3, nombre: 'Mobiliario' },
  { id: 4, nombre: 'Infraestructura' },
  { id: 5, nombre: 'Otro' }
]

// tipos_pago — ajusta estos IDs ejecutando: SELECT id, tipo FROM tipos_pago;
// Por ahora se cargan dinámicamente desde el backend vía base.py o similar.
// Si no tienes endpoint, define aquí los IDs reales de tu tabla tipos_pago:
const tiposPago = [
  { id: 1, nombre: 'Monetario' },
  { id: 2, nombre: 'En especie' },
  { id: 3, nombre: 'Ambos' }
]

// ── Estado UI ──────────────────────────────────────────────────────────────
const busqueda         = ref('')
const liquidandoId     = ref(null)
const creandoMulta     = ref(false)
const cargandoUsuarios = ref(false)
const todosLosUsuarios = ref([])

const toast = ref({ visible: false, mensaje: '', tipo: '' })

// ── Modal liquidar ─────────────────────────────────────────────────────────
const modalLiquidar = ref({
  visible: false,
  multa: null,
  observaciones: ''
})

// ── Modal crear ────────────────────────────────────────────────────────────
const formVacio = () => ({
  tipo_recurso_multa_id: 1,   // preselecciona "Libro"
  tipo_pago_id: '',
  costo_monetario: 0,
  observaciones: ''
})

const modalCrear = ref({
  visible: false,
  busquedaUsuario: '',
  usuarioSeleccionado: null,
  errorValidacion: '',
  form: formVacio()
})

// ── Computed ───────────────────────────────────────────────────────────────
const multasFiltradas = computed(() => {
  if (!busqueda.value.trim()) return multas.value
  const b = busqueda.value.toLowerCase()
  return multas.value.filter(m =>
    m.usuario_multado_nombre?.toLowerCase().includes(b) ||
    m.tipo_recurso_multa_nombre?.toLowerCase().includes(b) ||
    m.observaciones?.toLowerCase().includes(b)
  )
})

const totalRecaudable = computed(() => {
  const total = multas.value.reduce(
    (acc, m) => acc + parseFloat(m.costo_monetario || 0), 0
  )
  return new Intl.NumberFormat('es-MX', {
    style: 'currency', currency: 'MXN'
  }).format(total)
})

// Filtra usuarios por búsqueda — mínimo 2 caracteres, excluye super admins
const usuariosFiltrados = computed(() => {
  const q = modalCrear.value.busquedaUsuario.toLowerCase().trim()
  if (q.length < 2) return []
  return todosLosUsuarios.value
    .filter(u => u.tipo_usuario_id !== 4)
    .filter(u =>
      u.nombre_completo?.toLowerCase().includes(q) ||
      u.codigo_universitario?.toLowerCase().includes(q)
    )
    .slice(0, 8)
})

// ── Carga de datos ─────────────────────────────────────────────────────────
const cargar = async () => {
  try { await cargarMultasPendientes() } catch { /* manejado en composable */ }
}

const cargarUsuarios = async () => {
  if (todosLosUsuarios.value.length > 0) return
  cargandoUsuarios.value = true
  try {
    // El backend devuelve { usuarios: [], total, pagina, por_pagina }
    // Pedimos página grande para tener todos los usuarios en memoria
    const data = await userService.getUsers({ pagina: 1, por_pagina: 100, activos_only: true })
    todosLosUsuarios.value = Array.isArray(data)
      ? data
      : (data.usuarios ?? data.items ?? [])
  } catch (err) {
    console.error('Error cargando usuarios:', err)
    mostrarToast('No se pudieron cargar los usuarios', 'toast-error')
  } finally {
    cargandoUsuarios.value = false
  }
}

// ── Modal liquidar: acciones ───────────────────────────────────────────────
const abrirModalLiquidar = (multa) => {
  modalLiquidar.value = { visible: true, multa, observaciones: '' }
}

const cerrarModalLiquidar = () => {
  if (liquidandoId.value) return
  modalLiquidar.value = { visible: false, multa: null, observaciones: '' }
}

const confirmarLiquidacion = async () => {
  const multa = modalLiquidar.value.multa
  if (!multa) return
  liquidandoId.value = multa.id
  try {
    await liquidarMulta(multa.id, {
      observaciones: modalLiquidar.value.observaciones || null
    })
    const idx = multas.value.findIndex(m => m.id === multa.id)
    if (idx !== -1) multas.value.splice(idx, 1)
    cerrarModalLiquidar()
    mostrarToast(`Multa #${multa.id} liquidada correctamente`, 'toast-success')
  } catch (err) {
    mostrarToast(
      err.response?.data?.detail || 'Error al liquidar la multa',
      'toast-error'
    )
  } finally {
    liquidandoId.value = null
  }
}

// ── Modal crear: acciones ──────────────────────────────────────────────────
const abrirModalCrear = async () => {
  modalCrear.value = {
    visible: true,
    busquedaUsuario: '',
    usuarioSeleccionado: null,
    errorValidacion: '',
    form: formVacio()
  }
  await cargarUsuarios()
}

const cerrarModalCrear = () => {
  if (creandoMulta.value) return
  modalCrear.value.visible = false
}

const limpiarSeleccion = () => {
  // Resetea la selección si el usuario empieza a escribir de nuevo
  modalCrear.value.usuarioSeleccionado = null
  modalCrear.value.errorValidacion = ''
}

const seleccionarUsuario = (usuario) => {
  modalCrear.value.usuarioSeleccionado = usuario
  modalCrear.value.busquedaUsuario = usuario.nombre_completo
  modalCrear.value.errorValidacion = ''
}

const quitarUsuario = () => {
  modalCrear.value.usuarioSeleccionado = null
  modalCrear.value.busquedaUsuario = ''
}

const validarFormulario = () => {
  const { usuarioSeleccionado, form } = modalCrear.value

  if (!usuarioSeleccionado) {
    modalCrear.value.errorValidacion = 'Selecciona un usuario de la lista'
    return false
  }
  if (!form.tipo_recurso_multa_id) {
    modalCrear.value.errorValidacion = 'Selecciona un tipo de recurso'
    return false
  }
  if (!form.tipo_pago_id) {
    modalCrear.value.errorValidacion = 'Selecciona un tipo de pago'
    return false
  }
  if (form.costo_monetario < 0) {
    modalCrear.value.errorValidacion = 'El costo no puede ser negativo'
    return false
  }

  modalCrear.value.errorValidacion = ''
  return true
}

const confirmarCrearMulta = async () => {
  if (!validarFormulario()) return
  creandoMulta.value = true
  try {
    const { usuarioSeleccionado, form } = modalCrear.value

    await crearMulta({
      usuario_multado_id:    usuarioSeleccionado.id,
      tipo_pago_id:          Number(form.tipo_pago_id),
      tipo_recurso_multa_id: Number(form.tipo_recurso_multa_id),
      costo_monetario:       form.costo_monetario || 0,
      observaciones:         form.observaciones || null
    })

    await cargarMultasPendientes()
    cerrarModalCrear()
    mostrarToast(
      `Multa registrada para ${usuarioSeleccionado.nombre_completo}`,
      'toast-success'
    )
  } catch (err) {
    mostrarToast(
      err.response?.data?.detail || 'Error al registrar la multa',
      'toast-error'
    )
  } finally {
    creandoMulta.value = false
  }
}

// ── Utils ──────────────────────────────────────────────────────────────────
const truncar = (texto, max) => {
  if (!texto) return '—'
  return texto.length > max ? texto.substring(0, max) + '...' : texto
}

const mostrarToast = (mensaje, tipo = 'toast-info') => {
  toast.value = { visible: true, mensaje, tipo }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

onMounted(cargar)
</script>

<style scoped>
.multas-admin {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.page-header {
  display: flex; justify-content: space-between;
  align-items: flex-end; flex-wrap: wrap;
  gap: 1rem; margin-bottom: 1.5rem;
}
.titulo    { font-size: 1.6rem; font-weight: 800; color: #1a1a2e; margin: 0 0 4px; }
.subtitulo { font-size: 0.875rem; color: #64748b; margin: 0; }

.header-derecha {
  display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
}
.header-stats { display: flex; gap: 0.75rem; }
.stat-chip {
  display: flex; flex-direction: column; align-items: center;
  padding: 0.5rem 1rem; border-radius: 10px;
  min-width: 80px; border: 1.5px solid;
}
.chip-alerta { background: #fff3f3; border-color: #f5c0c0; }
.chip-total  { background: #f0fdf4; border-color: #bbf7d0; }
.stat-num    { font-size: 1.3rem; font-weight: 800; color: #1a1a2e; }
.chip-alerta .stat-num { color: #d62828; }
.chip-total  .stat-num { color: #16a34a; }
.stat-label  {
  font-size: 0.7rem; color: #64748b;
  text-transform: uppercase; letter-spacing: 0.05em;
}

.btn-crear-multa {
  padding: 0.6rem 1.25rem;
  background: #1a1a2e; color: #fff;
  border: none; border-radius: 8px;
  font-size: 0.875rem; font-weight: 700;
  cursor: pointer; white-space: nowrap;
  transition: background 0.2s, transform 0.15s;
}
.btn-crear-multa:hover { background: #d62828; transform: translateY(-1px); }

/* ── Filtros ─────────────────────────────────────────────────────────────── */
.filtros-bar { display: flex; gap: 0.75rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.input-busqueda {
  flex: 1; min-width: 220px; padding: 0.55rem 0.875rem;
  border: 1.5px solid #e2e8f0; border-radius: 8px;
  font-size: 0.875rem; color: #334155; outline: none;
  transition: border-color 0.2s;
}
.input-busqueda:focus { border-color: #6366f1; }
.btn-refrescar {
  padding: 0.55rem 1.1rem; background: #6366f1; color: #fff;
  border: none; border-radius: 8px; font-size: 0.875rem;
  font-weight: 600; cursor: pointer; transition: background 0.2s;
}
.btn-refrescar:hover    { background: #4f46e5; }
.btn-refrescar:disabled { opacity: 0.6; cursor: not-allowed; }

/* ── Estados ─────────────────────────────────────────────────────────────── */
.estado-loading, .estado-error, .estado-vacio {
  text-align: center; padding: 4rem 2rem;
}
.spinner {
  width: 36px; height: 36px;
  border: 3px solid #e2e8f0; border-top-color: #6366f1;
  border-radius: 50%; animation: spin 0.7s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin { to { transform: rotate(360deg); } }
.estado-error p { color: #d62828; }
.btn-retry {
  margin-top: 1rem; padding: 0.5rem 1.25rem;
  background: #d62828; color: #fff;
  border: none; border-radius: 8px; cursor: pointer;
}
.vacio-icono  { font-size: 3rem; color: #16a34a; }
.vacio-titulo { font-size: 1.1rem; font-weight: 700; color: #334155; }
.vacio-desc   { color: #64748b; font-size: 0.875rem; }

/* ── Tabla ───────────────────────────────────────────────────────────────── */
.tabla-wrapper { overflow-x: auto; }
.tabla-multas {
  width: 100%; border-collapse: collapse; font-size: 0.875rem;
  background: #fff; border: 1.5px solid #e2e8f0;
  border-radius: 12px; overflow: hidden;
}
.tabla-multas thead { background: #1a1a2e; }
.tabla-multas thead th {
  padding: 0.875rem 1rem; text-align: left;
  color: rgba(255,255,255,0.9); font-size: 0.75rem;
  font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;
}
.tabla-multas tbody tr {
  border-bottom: 1px solid #f1f5f9; transition: background 0.15s;
}
.tabla-multas tbody tr:last-child { border-bottom: none; }
.tabla-multas tbody tr:hover      { background: #f8fafc; }
.tabla-multas td { padding: 0.875rem 1rem; vertical-align: middle; color: #334155; }

.td-id          { font-family: monospace; color: #64748b; font-size: 0.8rem; }
.usuario-nombre { font-weight: 600; color: #1a1a2e; }
.chip-recurso {
  background: #ede9fe; color: #5b21b6;
  padding: 0.2rem 0.65rem; border-radius: 20px;
  font-size: 0.75rem; font-weight: 600;
}
.td-monto { font-weight: 800; font-size: 1rem; color: #d62828; }
.td-fecha { color: #64748b; font-size: 0.8rem; }
.td-obs   { max-width: 200px; }
.obs-texto { font-size: 0.78rem; color: #475569; cursor: default; }

.btn-liquidar {
  padding: 0.4rem 1rem; background: #16a34a; color: #fff;
  border: none; border-radius: 8px; font-size: 0.8rem;
  font-weight: 700; cursor: pointer; white-space: nowrap;
  transition: background 0.2s;
}
.btn-liquidar:hover    { background: #15803d; }
.btn-liquidar:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Modal base ──────────────────────────────────────────────────────────── */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000; backdrop-filter: blur(3px);
}
.modal {
  background: #fff; border-radius: 16px; width: 90%; max-width: 460px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  animation: modalIn 0.25s ease-out;
  max-height: 90vh; overflow-y: auto;
}
.modal-crear { max-width: 520px; }
@keyframes modalIn {
  from { opacity: 0; transform: translateY(-16px); }
  to   { opacity: 1; transform: translateY(0); }
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1.25rem 1.5rem 1rem; border-bottom: 1.5px solid #f1f5f9;
  position: sticky; top: 0; background: #fff; z-index: 1;
  border-radius: 16px 16px 0 0;
}
.modal-header h3 { margin: 0; font-size: 1.1rem; color: #1a1a2e; font-weight: 800; }
.modal-close {
  background: none; border: none; font-size: 1.4rem;
  color: #94a3b8; cursor: pointer; line-height: 1; padding: 0;
}
.modal-close:hover { color: #1a1a2e; }
.modal-body { padding: 1.25rem 1.5rem; }

/* Info en modal liquidar */
.modal-info-row {
  display: flex; gap: 0.75rem; margin-bottom: 0.75rem; font-size: 0.875rem;
}
.info-label      { font-weight: 700; color: #64748b; min-width: 70px; }
.info-valor      { color: #1a1a2e; }
.monto-highlight { font-size: 1.2rem; font-weight: 800; color: #d62828; }

/* Formulario */
.form-group { margin-bottom: 1.1rem; }
.form-label {
  display: block; font-size: 0.78rem; font-weight: 700;
  color: #64748b; margin-bottom: 5px;
  text-transform: uppercase; letter-spacing: 0.05em;
}
.required { color: #d62828; }

.form-input, .form-select {
  width: 100%; padding: 0.6rem 0.875rem;
  border: 1.5px solid #e2e8f0; border-radius: 8px;
  font-size: 0.875rem; font-family: inherit; color: #334155;
  background: #fff; outline: none; transition: border-color 0.2s;
  box-sizing: border-box;
}
.form-input:focus, .form-select:focus { border-color: #6366f1; }
.form-input:disabled { background: #f8fafc; cursor: not-allowed; }

.form-textarea {
  width: 100%; padding: 0.65rem 0.875rem;
  border: 1.5px solid #e2e8f0; border-radius: 8px;
  font-size: 0.875rem; font-family: inherit; color: #334155;
  resize: vertical; outline: none; transition: border-color 0.2s;
  box-sizing: border-box;
}
.form-textarea:focus { border-color: #6366f1; }

/* Prefijo $ */
.input-prefix-wrap { position: relative; }
.input-prefix {
  position: absolute; left: 0.75rem; top: 50%;
  transform: translateY(-50%); color: #64748b;
  font-weight: 700; font-size: 0.9rem; pointer-events: none;
}
.input-con-prefix { padding-left: 1.75rem; }

/* Buscador de usuario */
.usuario-search-wrap { position: relative; }
.usuario-dropdown {
  position: absolute; top: calc(100% + 4px); left: 0; right: 0;
  background: #fff; border: 1.5px solid #e2e8f0; border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12); z-index: 100;
  max-height: 220px; overflow-y: auto;
}
.usuario-option {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.65rem 0.875rem; cursor: pointer;
  border-bottom: 1px solid #f1f5f9; transition: background 0.15s;
}
.usuario-option:last-child { border-bottom: none; }
.usuario-option:hover      { background: #f0f4ff; }
.option-nombre { font-weight: 600; font-size: 0.875rem; color: #1a1a2e; }
.option-codigo { font-size: 0.75rem; color: #64748b; font-family: monospace; }
.option-vacio  {
  padding: 0.75rem 0.875rem; color: #94a3b8;
  font-size: 0.85rem; text-align: center;
}

/* Chip usuario seleccionado */
.usuario-seleccionado {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 0.5rem; padding: 0.6rem 0.875rem;
  background: #f0f4ff; border: 1.5px solid #c7d2fe; border-radius: 8px;
}
.usuario-sel-info   { display: flex; flex-direction: column; gap: 2px; }
.usuario-sel-nombre { font-weight: 700; font-size: 0.875rem; color: #1a1a2e; }
.usuario-sel-codigo { font-size: 0.75rem; color: #6366f1; font-family: monospace; }
.btn-quitar-usuario {
  background: none; border: none; font-size: 1.2rem;
  color: #94a3b8; cursor: pointer; padding: 0 4px; line-height: 1;
  transition: color 0.15s;
}
.btn-quitar-usuario:hover { color: #d62828; }

/* Error validación */
.error-validacion {
  margin-top: 0.75rem; padding: 0.6rem 0.875rem;
  background: #fff3f3; border: 1px solid #f5c0c0;
  border-radius: 8px; color: #d62828;
  font-size: 0.82rem; font-weight: 600;
}

/* Footer modal */
.modal-footer {
  display: flex; justify-content: flex-end; gap: 0.75rem;
  padding: 1rem 1.5rem; border-top: 1.5px solid #f1f5f9;
  position: sticky; bottom: 0; background: #fff;
  border-radius: 0 0 16px 16px;
}
.btn-cancelar {
  padding: 0.5rem 1rem; background: #fff;
  border: 1.5px solid #e2e8f0; border-radius: 8px;
  font-size: 0.875rem; font-weight: 600; color: #64748b;
  cursor: pointer; transition: all 0.2s;
}
.btn-cancelar:hover    { background: #f8fafc; }
.btn-cancelar:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-confirmar-liquidar {
  padding: 0.5rem 1.25rem; background: #16a34a; color: #fff;
  border: none; border-radius: 8px; font-size: 0.875rem;
  font-weight: 700; cursor: pointer; transition: background 0.2s;
}
.btn-confirmar-liquidar:hover    { background: #15803d; }
.btn-confirmar-liquidar:disabled { opacity: 0.55; cursor: not-allowed; }

.btn-confirmar-crear {
  padding: 0.5rem 1.25rem; background: #1a1a2e; color: #fff;
  border: none; border-radius: 8px; font-size: 0.875rem;
  font-weight: 700; cursor: pointer; transition: background 0.2s;
  display: inline-flex; align-items: center; gap: 0.4rem;
}
.btn-confirmar-crear:hover    { background: #d62828; }
.btn-confirmar-crear:disabled { opacity: 0.55; cursor: not-allowed; }

.spinner-mini {
  display: inline-block; width: 13px; height: 13px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.6s linear infinite;
}

/* ── Toast ───────────────────────────────────────────────────────────────── */
.toast {
  position: fixed; bottom: 2rem; right: 2rem;
  padding: 0.75rem 1.25rem; border-radius: 10px;
  font-size: 0.875rem; font-weight: 600; color: #fff;
  z-index: 9999; box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.toast-success { background: #16a34a; }
.toast-error   { background: #d62828; }
.toast-info    { background: #6366f1; }
.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(12px); }

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 700px) {
  .page-header    { flex-direction: column; align-items: flex-start; }
  .header-derecha { width: 100%; justify-content: space-between; }
  .tabla-multas   { font-size: 0.78rem; }
  .tabla-multas thead th,
  .tabla-multas td { padding: 0.65rem 0.75rem; }
  .td-obs { display: none; }
  .modal-footer { flex-direction: column; }
  .modal-footer > * { width: 100%; justify-content: center; }
}
</style>