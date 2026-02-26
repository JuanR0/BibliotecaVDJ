import api from '@/services/api'

export const areasService = {
  // Obtener listado de áreas con paginación y filtros
  async getAreas(params = {}) {
    try {
      const response = await api.get('/api/areas/', { params })
      return response.data
    } catch (error) {
      console.error('Error obteniendo áreas:', error)
      throw error
    }
  },

  // Obtener área por ID
  async getAreaById(id) {
    try {
      const response = await api.get(`/api/areas/${id}`)
      return response.data
    } catch (error) {
      console.error(`Error obteniendo área ${id}:`, error)
      throw error
    }
  },

  // Crear nueva área
  async createArea(areaData) {
    try {
      const response = await api.post('/api/areas/', areaData)
      return response.data
    } catch (error) {
      console.error('Error creando área:', error)
      throw error
    }
  },

  // Actualizar área existente
  async updateArea(id, areaData) {
    try {
      const response = await api.put(`/api/areas/${id}`, areaData)
      return response.data
    } catch (error) {
      console.error(`Error actualizando área ${id}:`, error)
      throw error
    }
  },

  // Desactivar área (soft delete - estado 4)
  async desactivateArea(id) {
    try {
      const response = await api.patch(`/api/areas/${id}/desactivar`)
      return response.data
    } catch (error) {
      console.error(`Error desactivando área ${id}:`, error)
      throw error
    }
  },

  // Reactivar área (cambia de estado 4 a 1)
  async reactivateArea(id) {
    try {
      const response = await api.patch(`/api/areas/${id}/reactivar`)
      return response.data
    } catch (error) {
      console.error(`Error reactivando área ${id}:`, error)
      throw error
    }
  },

  // Obtener estados de área
  async getEstadosArea() {
    try {
      const response = await api.get('/api/areas/auxiliares/estados-area')
      return response.data
    } catch (error) {
      console.error('Error obteniendo estados de área:', error)
      throw error
    }
  },

  // Buscar áreas con filtros
  async searchAreas(filters = {}) {
    try {
      const response = await api.get('/api/areas/', { params: filters })
      return response.data
    } catch (error) {
      console.error('Error buscando áreas:', error)
      throw error
    }
  }
}