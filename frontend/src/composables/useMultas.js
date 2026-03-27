import { ref, computed } from 'vue'
import { multasService } from '@/services/multas'

export function useMultas() {
  const multas = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  // ========== COMPUTED ==========

  const tieneMultasPendientes = computed(() =>
    multas.value.some(m => Number(m.estado_multa_id) === 1)
  )

  const multasPendientes = computed(() =>
    multas.value.filter(m => Number(m.estado_multa_id) === 1)
  )

  const multasLiquidadas = computed(() =>
    multas.value.filter(m => Number(m.estado_multa_id) === 2)
  )

  // ========== CARGAR DATOS ==========

  /**
   * Carga las multas del usuario actual (vista usuario)
   */
  const cargarMisMultas = async (usuarioId) => {
    isLoading.value = true
    error.value = null
    try {
      const data = await multasService.getMultasByUsuario(usuarioId)
      multas.value = Array.isArray(data) ? data : []
      return multas.value
    } catch (err) {
      error.value =
        err.response?.data?.detail ||
        err.message ||
        'Error cargando tus multas'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Carga todas las multas (vista admin)
   */
  const cargarTodasLasMultas = async () => {
    isLoading.value = true
    error.value = null
    try {
      const data = await multasService.getMultas()
      multas.value = Array.isArray(data) ? data : []
      return multas.value
    } catch (err) {
      error.value =
        err.response?.data?.detail ||
        err.message ||
        'Error cargando multas'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Carga solo multas pendientes (vista admin)
   */
  const cargarMultasPendientes = async () => {
    isLoading.value = true
    error.value = null
    try {
      const data = await multasService.getMultasPendientes()
      multas.value = Array.isArray(data) ? data : []
      return multas.value
    } catch (err) {
      error.value =
        err.response?.data?.detail ||
        err.message ||
        'Error cargando multas pendientes'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // ========== ACCIONES ADMIN ==========

  /**
   * Liquidar una multa (solo admin)
   */
  const liquidarMulta = async (multaId, pagoData) => {
    isLoading.value = true
    try {
      const multaActualizada = await multasService.liquidarMulta(multaId, pagoData)

      const index = multas.value.findIndex(m => Number(m.id) === Number(multaId))
      if (index !== -1) {
        multas.value[index] = {
          ...multas.value[index],
          ...multaActualizada
        }
      }

      return multaActualizada
    } catch (err) {
      error.value =
        err.response?.data?.detail ||
        err.message ||
        'Error liquidando multa'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Crear una multa manualmente (solo admin)
   */
  const crearMulta = async (multaData) => {
    isLoading.value = true
    try {
      const nuevaMulta = await multasService.crearMulta(multaData)
      multas.value.unshift(nuevaMulta)
      return nuevaMulta
    } catch (err) {
      error.value =
        err.response?.data?.detail ||
        err.message ||
        'Error creando multa'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // ========== UTILIDADES ==========

  const getEstadoNombre = (estadoId) => {
    const estadoMap = {
      1: 'Pendiente',
      2: 'Liquidada',
      3: 'Cancelada'
    }
    return estadoMap[estadoId] || 'Desconocido'
  }

  const getEstadoClase = (estadoId) => {
    const claseMap = {
      1: 'estado-pendiente',
      2: 'estado-liquidada',
      3: 'estado-cancelada'
    }
    return claseMap[estadoId] || ''
  }

  const formatearCosto = (costoStr) => {
    if (!costoStr) return '$0.00'
    const numero = parseFloat(costoStr)
    if (isNaN(numero)) return '$0.00'
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(numero)
  }

  const formatearFecha = (fechaISO) => {
    if (!fechaISO) return '—'
    return new Date(fechaISO).toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const filtrarMultas = (filtros = {}) => {
    let resultado = [...multas.value]

    if (filtros.estado_multa_id !== undefined && filtros.estado_multa_id !== '') {
      resultado = resultado.filter(
        m => Number(m.estado_multa_id) === Number(filtros.estado_multa_id)
      )
    }

    if (filtros.busqueda) {
      const b = filtros.busqueda.toLowerCase()
      resultado = resultado.filter(
        m =>
          m.usuario_multado_nombre?.toLowerCase().includes(b) ||
          m.observaciones?.toLowerCase().includes(b) ||
          m.tipo_recurso_multa_nombre?.toLowerCase().includes(b)
      )
    }

    return resultado
  }

  return {
    // State
    multas,
    isLoading,
    error,

    // Computed
    tieneMultasPendientes,
    multasPendientes,
    multasLiquidadas,

    // Actions — usuario
    cargarMisMultas,

    // Actions — admin
    cargarTodasLasMultas,
    cargarMultasPendientes,
    liquidarMulta,
    crearMulta,

    // Utils
    getEstadoNombre,
    getEstadoClase,
    formatearCosto,
    formatearFecha,
    filtrarMultas
  }
}