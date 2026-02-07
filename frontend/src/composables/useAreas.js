// src/composables/useAreas.js - VERSIÓN CORREGIDA
import { ref, computed } from 'vue'
import { areasService } from '@/services/areas'

export function useAreas() {
  const areas = ref([])
  const estadosArea = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  // ========== CARGAR DATOS ==========
  const cargarAreas = async (params = {}) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await areasService.getAreas(params)
      
      // Asegurar que tenemos un array válido
      if (response && Array.isArray(response.areas)) {
        areas.value = response.areas.map(area => ({
          // Campos obligatorios con valores por defecto
          id: area.id || 0,
          nombre: area.nombre || 'Sin nombre',
          capacidad: area.capacidad ?? null,
          es_prestable: area.es_prestable ?? false,
          estado_id: area.estado_id || 1,
          usuario_registro_nombre: area.usuario_registro_nombre || 'Desconocido',
          fecha_registro: area.fecha_registro || new Date().toISOString(),
          fecha_ultimo_cambio_estado: area.fecha_ultimo_cambio_estado || area.fecha_registro || new Date().toISOString(),
          // Campos calculados
          estado_nombre: area.estado_nombre || getEstadoNombre(area.estado_id)
        }))
      } else {
        areas.value = []
      }
      
      return areas.value
      
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error cargando áreas'
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

  // ========== CRUD OPERACIONES ==========
  const crearArea = async (areaData) => {
    isLoading.value = true
    try {
      const nuevaArea = await areasService.createArea(areaData)
      
      // Enriquecer el objeto antes de agregarlo
      const areaEnriquecida = {
        id: nuevaArea.id,
        nombre: nuevaArea.nombre,
        capacidad: nuevaArea.capacidad ?? null,
        es_prestable: nuevaArea.es_prestable ?? false,
        estado_id: nuevaArea.estado_id || 1,
        usuario_registro_nombre: nuevaArea.usuario_registro_nombre || 'Tú',
        fecha_registro: nuevaArea.fecha_registro || new Date().toISOString(),
        fecha_ultimo_cambio_estado: nuevaArea.fecha_ultimo_cambio_estado || nuevaArea.fecha_registro || new Date().toISOString(),
        estado_nombre: nuevaArea.estado_nombre || getEstadoNombre(nuevaArea.estado_id)
      }
      
      // Agregar al inicio
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
      console.log('🔄 Actualizando área:', { id, areaData })
      
      const areaActualizada = await areasService.updateArea(id, areaData)
      console.log('✅ Respuesta del servidor:', areaActualizada)
      
      // Buscar el índice en la lista local
      const index = areas.value.findIndex(a => a.id === id)
      
      if (index !== -1) {
        // Hacer MERGE (no reemplazo completo)
        areas.value[index] = {
          ...areas.value[index], // Mantener todos los campos existentes
          ...areaActualizada,     // Sobrescribir con campos nuevos
          // Campos críticos (asegurar que existen)
          id: id,
          nombre: areaActualizada.nombre || areas.value[index].nombre,
          capacidad: areaActualizada.capacidad ?? areas.value[index].capacidad,
          es_prestable: areaActualizada.es_prestable ?? areas.value[index].es_prestable,
          estado_id: areaActualizada.estado_id || areas.value[index].estado_id,
          // Actualizar estado_nombre
          estado_nombre: areaActualizada.estado_nombre || 
                        getEstadoNombre(areaActualizada.estado_id) || 
                        areas.value[index].estado_nombre
        }
        
        console.log('📝 Área actualizada en lista local:', areas.value[index])
      } else {
        console.warn('⚠️ Área no encontrada en lista local, agregando...')
        // Si no existe en local, agregarla
        const areaEnriquecida = {
          id: areaActualizada.id,
          nombre: areaActualizada.nombre,
          capacidad: areaActualizada.capacidad ?? null,
          es_prestable: areaActualizada.es_prestable ?? false,
          estado_id: areaActualizada.estado_id || 1,
          usuario_registro_nombre: areaActualizada.usuario_registro_nombre || 'Desconocido',
          fecha_registro: areaActualizada.fecha_registro || new Date().toISOString(),
          fecha_ultimo_cambio_estado: areaActualizada.fecha_ultimo_cambio_estado || new Date().toISOString(),
          estado_nombre: areaActualizada.estado_nombre || getEstadoNombre(areaActualizada.estado_id)
        }
        areas.value.push(areaEnriquecida)
      }
      
      return areaActualizada
      
    } catch (err) {
      console.error('❌ Error en actualizarArea:', err)
      error.value = err.response?.data?.detail || err.message || 'Error actualizando área'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const desactivarArea = async (id) => {
    try {
      console.log('🔄 Desactivando área:', id)
      
      const response = await areasService.desactivateArea(id)
      console.log('✅ Respuesta desactivar:', response)
      
      // Actualizar en lista local
      const index = areas.value.findIndex(a => a.id === id)
      if (index !== -1) {
        // Solo actualizar campos relevantes
        areas.value[index] = {
          ...areas.value[index], // Mantener todo
          estado_id: 4,
          estado_nombre: 'Retirada',
          fecha_ultimo_cambio_estado: new Date().toISOString()
        }
      }
      
      return response
      
    } catch (err) {
      console.error('❌ Error desactivando área:', err)
      error.value = err.response?.data?.detail || 'Error desactivando área'
      throw err
    }
  }

  const reactivarArea = async (id) => {
    try {
      console.log('🔄 Reactivando área:', id)
      
      const response = await areasService.reactivateArea(id)
      console.log('✅ Respuesta reactivar:', response)
      
      // Actualizar en lista local
      const index = areas.value.findIndex(a => a.id === id)
      if (index !== -1) {
        areas.value[index] = {
          ...areas.value[index], // Mantener todo
          estado_id: 1,
          estado_nombre: 'Disponible',
          fecha_ultimo_cambio_estado: new Date().toISOString()
        }
      }
      
      return response
      
    } catch (err) {
      console.error('❌ Error reactivando área:', err)
      error.value = err.response?.data?.detail || 'Error reactivando área'
      throw err
    }
  }

  // ========== UTILIDADES ==========
  const getEstadoNombre = (estadoId) => {
    const estado = estadosArea.value.find(e => e.id === estadoId)
    if (estado) return estado.estado
    
    // Fallback si no hay estados cargados
    const estadoMap = {
      1: 'Disponible',
      2: 'Ocupado',
      3: 'En mantenimiento',
      4: 'Retirada',
      5: 'No disponible'
    }
    return estadoMap[estadoId] || 'Desconocido'
  }

  const filtrarAreas = (filtros = {}) => {
    let resultado = [...areas.value]

    if (filtros.estado_id) {
      resultado = resultado.filter(a => a.estado_id === parseInt(filtros.estado_id))
    }

    if (filtros.es_prestable !== undefined) {
      resultado = resultado.filter(a => a.es_prestable === filtros.es_prestable)
    }

    if (filtros.nombre) {
      const busqueda = filtros.nombre.toLowerCase()
      resultado = resultado.filter(a => 
        a.nombre.toLowerCase().includes(busqueda)
      )
    }

    return resultado
  }

  // ========== REFRESCAR DATOS ==========
  const refrescarArea = async (id) => {
    try {
      const areaFresca = await areasService.getAreaById(id)
      
      const index = areas.value.findIndex(a => a.id === id)
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
    // State
    areas,
    estadosArea,
    isLoading,
    error,

    // Actions
    cargarAreas,
    cargarEstados,
    crearArea,
    actualizarArea,
    desactivarArea,
    reactivarArea,
    filtrarAreas,
    refrescarArea
  }
}