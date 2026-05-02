import { ref } from 'vue'
import { areasService } from '@/services/areas'

const ESTADO_MAP = {
  1: 'Disponible',
  2: 'Ocupada',
  3: 'Mantenimiento',
  4: 'Reservada',
  5: 'No disponible'
}

export function useAreas() {
  const areas      = ref([])
  const estadosArea = ref([])
  const isLoading  = ref(false)
  const error      = ref(null)

  // ── Cargar áreas ──────────────────────────────────────────────────────
  const cargarAreas = async (params = {}) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await areasService.getAreas(params)
      const listaAreas = Array.isArray(response?.areas) ? response.areas : []

      areas.value = listaAreas.map(area => ({
        ...area,
        estado_nombre: area.estado_nombre || getEstadoNombre(area.estado_id)
      }))

      return areas.value
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Error cargando áreas'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const cargarEstados = async () => {
    try {
      const estados = await areasService.getEstadosArea()
      estadosArea.value = Array.isArray(estados) ? estados : []
      return estadosArea.value
    } catch (err) {
      console.error('Error cargando estados de área:', err)
      throw err
    }
  }

  // ── CRUD ──────────────────────────────────────────────────────────────
  const crearArea = async (areaData) => {
    isLoading.value = true
    try {
      const nuevaArea = await areasService.createArea(areaData)
      const areaEnriquecida = {
        ...nuevaArea,
        estado_nombre: getEstadoNombre(nuevaArea.estado_id)
      }
      areas.value.unshift(areaEnriquecida)
      return areaEnriquecida
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error creando área'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const actualizarArea = async (id, areaData) => {
    isLoading.value = true
    try {
      const areaActualizada = await areasService.updateArea(id, areaData)
      const index = areas.value.findIndex(a => Number(a.id) === Number(id))
      if (index !== -1) {
        areas.value[index] = {
          ...areas.value[index],
          ...areaActualizada,
          estado_nombre: getEstadoNombre(areaActualizada.estado_id)
        }
      }
      return areaActualizada
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error actualizando área'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const desactivarArea = async (id) => {
    try {
      const response = await areasService.desactivateArea(id)
      const index = areas.value.findIndex(a => Number(a.id) === Number(id))
      if (index !== -1) {
        areas.value[index] = {
          ...areas.value[index],
          estado_id: 5,
          estado_nombre: ESTADO_MAP[5],   // 'No disponible'
          fecha_ultimo_cambio_estado: new Date().toISOString()
        }
      }
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error desactivando área'
      throw err
    }
  }

  const reactivarArea = async (id) => {
    try {
      const response = await areasService.reactivateArea(id)
      const index = areas.value.findIndex(a => Number(a.id) === Number(id))
      if (index !== -1) {
        areas.value[index] = {
          ...areas.value[index],
          estado_id: 1,
          estado_nombre: ESTADO_MAP[1],   // 'Disponible'
          fecha_ultimo_cambio_estado: new Date().toISOString()
        }
      }
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error reactivando área'
      throw err
    }
  }

  // ── Utilidades ────────────────────────────────────────────────────────
  const getEstadoNombre = (estadoId) => {
    // Primero busca en los estados cargados del servidor
    const estado = estadosArea.value.find(e => e.id === estadoId)
    if (estado) return estado.estado
    return ESTADO_MAP[estadoId] || 'Desconocido'
  }

  const filtrarAreas = (filtros = {}) => {
    let resultado = [...areas.value]

    if (filtros.estado_id)
      resultado = resultado.filter(a => a.estado_id === parseInt(filtros.estado_id))

    if (filtros.es_prestable !== undefined)
      resultado = resultado.filter(a => a.es_prestable === filtros.es_prestable)

    if (filtros.nombre) {
      const busqueda = filtros.nombre.toLowerCase()
      resultado = resultado.filter(a => a.nombre.toLowerCase().includes(busqueda))
    }

    return resultado
  }

  const refrescarArea = async (id) => {
    try {
      const areaFresca = await areasService.getAreaById(id)
      const index = areas.value.findIndex(a => Number(a.id) === Number(id))
      if (index !== -1) {
        areas.value[index] = {
          ...areas.value[index],
          ...areaFresca,
          estado_nombre: areaFresca.estado_nombre || getEstadoNombre(areaFresca.estado_id)
        }
      }
      return areaFresca
    } catch (err) {
      console.error('Error refrescando área:', err)
      throw err
    }
  }

  return {
    areas, estadosArea, isLoading, error,
    cargarAreas, cargarEstados,
    crearArea, actualizarArea,
    desactivarArea, reactivarArea,
    filtrarAreas, refrescarArea,
    getEstadoNombre,
    ESTADO_MAP
  }
}