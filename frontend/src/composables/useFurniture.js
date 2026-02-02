import { ref } from 'vue'
import { mobiliarioService } from '@/services/mobiliario'

export const useMobiliario = (initialMobiliarioId = null) => {
  // Convertir a ref reactivo
  const mobiliarioId = ref(initialMobiliarioId)
  
  // Datos del mobiliario
  const mobiliario = ref(null)
  const originalData = ref(null)
  const formData = ref({
    descripcion: '',
    tipo_mobiliario_id: '',
    estado_id: '',
    area_id: ''
  })
  
  // Catálogos
  const tiposMobiliario = ref([])
  const estadosMobiliario = ref([])
  const areas = ref([])
  
  // Estados
  const isLoading = ref(false)
  const isLoadingCatalogos = ref(false)
  const error = ref(null)

  // ========== MÉTODOS PARA CATÁLOGOS ==========
  const loadCatalogos = async () => {
    isLoadingCatalogos.value = true
    
    try {
      const [tipos, estados, areasData] = await Promise.all([
        mobiliarioService.getTiposMobiliario(),
        mobiliarioService.getEstadosMobiliario(),
        mobiliarioService.getAreas()
      ])
      
      console.log('📊 Tipos raw:', tipos)
      console.log('📊 Estados raw:', estados)
      console.log('📊 Áreas raw:', areasData)
      
      // Procesar tipos - IMPORTANTE: tu API usa 'tipo' no 'nombre'
      tiposMobiliario.value = Array.isArray(tipos) 
        ? tipos.map(t => ({ 
            id: t.id, 
            nombre: t.tipo || t.nombre || 'Sin nombre' // 'tipo' aquí
          }))
        : []
      
      // Procesar estados - IMPORTANTE: tu API usa 'estado' no 'nombre'
      estadosMobiliario.value = Array.isArray(estados)
        ? estados.map(e => ({ 
            id: e.id, 
            nombre: e.estado || e.nombre || 'Sin nombre' // 'estado' aquí
          }))
        : []
      
      // Procesar áreas
      let areasArray = []
      if (areasData && typeof areasData === 'object') {
        // Tu API devuelve {areas: [], total: 0, ...}
        areasArray = areasData.areas || areasData.data || []
      } else if (Array.isArray(areasData)) {
        areasArray = areasData
      }
      
      areas.value = Array.isArray(areasArray)
        ? areasArray.map(a => ({ 
            id: a.id, 
            nombre: a.nombre || a.nombre_area || a.descripcion || 'Sin nombre'
          }))
        : []
      
      console.log('✅ Catálogos procesados:')
      console.log('Tipos:', tiposMobiliario.value)
      console.log('Estados:', estadosMobiliario.value)
      console.log('Áreas:', areas.value)
      
      return { tipos: tiposMobiliario.value, estados: estadosMobiliario.value, areas: areas.value }
    } catch (err) {
      console.error('❌ Error cargando catálogos:', err)
      throw err
    } finally {
      isLoadingCatalogos.value = false
    }
  }

  // ========== MÉTODOS PARA DATOS DEL MOBILIARIO ==========
  const loadMobiliarioData = async (id = null) => {
    const targetId = id || mobiliarioId.value
    if (!targetId) {
      throw new Error('No se proporcionó ID del mobiliario')
    }

    isLoading.value = true
    error.value = null
    
    try {
      console.log(`📡 Cargando mobiliario ID: ${targetId}`)
      const mobiliarioData = await mobiliarioService.getMobiliarioById(targetId)
      
      console.log('📦 Datos recibidos:', mobiliarioData)
      
      mobiliario.value = mobiliarioData
      
      // Guardar datos originales
      originalData.value = {
        descripcion: mobiliarioData.descripcion || '',
        tipo_mobiliario_id: mobiliarioData.tipo_mobiliario_id || '',
        estado_id: mobiliarioData.estado_id || '',
        area_id: mobiliarioData.area_id || null
      }
      
      // Inicializar formulario
      formData.value = { ...originalData.value }
      
      console.log('📝 Formulario inicializado:', formData.value)
      
      return mobiliarioData
    } catch (err) {
      console.error('❌ Error cargando datos del mobiliario:', err)
      error.value = err.response?.data?.detail || err.message || 'No se pudo cargar la información del mobiliario'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // ========== MÉTODO PARA INICIALIZACIÓN ==========
  const initialize = async (options = {}) => {
    const { 
      id = null, 
      loadCatalogos: shouldLoadCatalogos = true,
      loadMobiliarioData: shouldLoadMobiliarioData = false 
    } = options
    
    try {
      // Actualizar ID si se proporciona
      if (id !== null) {
        mobiliarioId.value = id
      }
      
      const promises = []
      
      // Cargar catálogos si se solicita
      if (shouldLoadCatalogos) {
        promises.push(loadCatalogos())
      }
      
      // Cargar datos del mobiliario si hay ID y se solicita
      if (shouldLoadMobiliarioData && mobiliarioId.value) {
        promises.push(loadMobiliarioData())
      }
      
      // Esperar todas las promesas
      await Promise.all(promises)
      
      // Configurar estado por defecto solo si es creación (sin ID)
      if (!mobiliarioId.value && estadosMobiliario.value.length > 0) {
        const estadoActivo = estadosMobiliario.value.find(e => {
          if (!e.nombre) return false
          const nombre = e.nombre.toLowerCase()
          return nombre.includes('activo') || nombre.includes('en uso') || nombre.includes('disponible')
        })
        
        if (estadoActivo) {
          formData.value.estado_id = estadoActivo.id
          console.log('⚙️ Estado por defecto configurado:', estadoActivo)
        }
      }
      
    } catch (err) {
      console.error('❌ Error en initialize:', err)
      throw err
    }
  }

  // ========== HELPERS ==========
  const getTipoNombre = (id) => {
    const tipo = tiposMobiliario.value.find(t => t.id === id)
    return tipo?.nombre || `ID: ${id}`
  }

  const getEstadoNombre = (id) => {
    const estado = estadosMobiliario.value.find(e => e.id === id)
    return estado?.nombre || `ID: ${id}`
  }

  const getAreaNombre = (id) => {
    if (!id) return 'Sin área'
    const area = areas.value.find(a => a.id === id)
    return area?.nombre || `ID: ${id}`
  }

  const resetForm = () => {
    if (originalData.value) {
      formData.value = { ...originalData.value }
      console.log('🔄 Formulario restaurado a valores originales')
    } else {
      // Para creación, limpiar formulario
      formData.value = {
        descripcion: '',
        tipo_mobiliario_id: '',
        estado_id: '',
        area_id: ''
      }
    }
  }

  const hasChanges = () => {
    if (!originalData.value) return false
    
    return (
      formData.value.descripcion !== originalData.value.descripcion ||
      formData.value.tipo_mobiliario_id !== originalData.value.tipo_mobiliario_id ||
      formData.value.estado_id !== originalData.value.estado_id ||
      formData.value.area_id !== originalData.value.area_id
    )
  }

  const getDetectedChanges = () => {
    const changes = []
    if (!originalData.value) return changes

    // Comparar cada campo
    if (formData.value.descripcion !== originalData.value.descripcion) {
      changes.push({
        field: 'descripcion',
        label: 'Descripción',
        from: originalData.value.descripcion || '(vacío)',
        to: formData.value.descripcion || '(vacío)'
      })
    }
    
    if (formData.value.tipo_mobiliario_id !== originalData.value.tipo_mobiliario_id) {
      changes.push({
        field: 'tipo_mobiliario_id',
        label: 'Tipo',
        from: getTipoNombre(originalData.value.tipo_mobiliario_id),
        to: getTipoNombre(formData.value.tipo_mobiliario_id)
      })
    }
    
    if (formData.value.estado_id !== originalData.value.estado_id) {
      changes.push({
        field: 'estado_id',
        label: 'Estado',
        from: getEstadoNombre(originalData.value.estado_id),
        to: getEstadoNombre(formData.value.estado_id)
      })
    }
    
    if (formData.value.area_id !== originalData.value.area_id) {
      changes.push({
        field: 'area_id',
        label: 'Área',
        from: getAreaNombre(originalData.value.area_id),
        to: getAreaNombre(formData.value.area_id)
      })
    }
    
    return changes
  }

  // Método para actualizar el ID
  const setId = (id) => {
    mobiliarioId.value = id
  }

  return {
    // Reactivos
    mobiliarioId,
    mobiliario,
    originalData,
    formData,
    tiposMobiliario,
    estadosMobiliario,
    areas,
    isLoading,
    isLoadingCatalogos,
    error,
    
    // Métodos principales
    loadCatalogos,
    loadMobiliarioData,
    initialize,
    setId,
    
    // Helpers
    getTipoNombre,
    getEstadoNombre,
    getAreaNombre,
    resetForm,
    hasChanges,
    getDetectedChanges
  }
}