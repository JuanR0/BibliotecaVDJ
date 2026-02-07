import { api } from './api'

export const mobiliarioService = {
  // Obtener todos los mobiliarios
  async getMobiliarios(params = {}) {
    try {
      console.log('📤 Llamando GET /api/mobiliario con:', params)
      const response = await api.get('/mobiliario', { params })
      return response.data
    } catch (error) {
      console.error('Error obteniendo mobiliario:', error)
      throw error
    }
  },

  // OBTENER MOBILIARIO POR ID
  async getMobiliarioById(id) {
    try {
      const response = await api.get(`/mobiliario/${id}`)
      return response.data
    } catch (error) {
      console.error(`Error obteniendo mobiliario ${id}:`, error)
      throw error
    }
  },

  // BUSCAR MOBILIARIO
  async searchMobiliario(query, params = {}) {
    const cleanParams = {};
    
    Object.entries(params).forEach(([key, value]) => {
      // Solo incluir si tiene valor y no es string vacío
      if (value !== undefined && value !== null && value !== '') {
        // Convertir tipos según el campo
        if (key.endsWith('_id') && !isNaN(value)) {
          cleanParams[key] = parseInt(value);
        } else if (key === 'incluir_desactivados') {
          cleanParams[key] = Boolean(value);
        } else if (key === 'pagina' || key === 'por_pagina') {
          cleanParams[key] = parseInt(value);
        } else {
          cleanParams[key] = value;
        }
      }
    });
    
    // Agregar búsqueda por descripción si hay query
    if (query && query.trim()) {
      cleanParams.descripcion = query.trim();
    }
    
    console.log('📤 Llamando GET /api/mobiliario con:', cleanParams);
    const response = await api.get('/mobiliario', { params: cleanParams });
    return response.data;
  },

  // CREAR MOBILIARIO
  async createMobiliario(mobiliarioData) {
    try {
      console.log('📤 Creando mobiliario:', mobiliarioData)
      const response = await api.post('/mobiliario', mobiliarioData)
      return response.data
    } catch (error) {
      console.error('Error creando mobiliario:', error)
      throw error
    }
  },

  // ACTUALIZAR MOBILIARIO
  async updateMobiliario(id, mobiliarioData) {
    try {
      console.log(`📤 Actualizando mobiliario ${id}:`, mobiliarioData)
      const response = await api.put(`/mobiliario/${id}`, mobiliarioData)
      return response.data
    } catch (error) {
      console.error(`Error actualizando mobiliario ${id}:`, error)
      throw error
    }
  },

  // DESACTIVAR MOBILIARIO (soft delete)
  async desactivateMobiliario(id) {
    try {
      console.log(`📤 Desactivando mobiliario ${id}`)
      const response = await api.patch(`/mobiliario/${id}/desactivar`)
      return response.data
    } catch (error) {
      console.error(`Error desactivando mobiliario ${id}:`, error)
      throw error
    }
  },

  // REACTIVAR MOBILIARIO
  async reactivateMobiliario(id) {
    try {
      console.log(`📤 Reactivando mobiliario ${id}`)
      const response = await api.patch(`/mobiliario/${id}/reactivar`)
      return response.data
    } catch (error) {
      console.error(`Error reactivando mobiliario ${id}:`, error)
      throw error
    }
  },

  // ELIMINAR PERMANENTEMENTE
  async deleteMobiliario(id) {
    try {
      console.log(`📤 Eliminando permanentemente mobiliario ${id}`)
      const response = await api.delete(`/mobiliario/${id}/eliminar-permanente`)
      return response.data
    } catch (error) {
      console.error(`Error eliminando mobiliario ${id}:`, error)
      throw error
    }
  },

  // OBTENER CATÁLOGOS
  async getTiposMobiliario() {
    try {
      const response = await api.get('/mobiliario/auxiliares/tipos-mobiliario')
      return response.data
    } catch (error) {
      console.error('Error obteniendo tipos de mobiliario:', error)
      throw error
    }
  },

  async getEstadosMobiliario() {
    try {
      const response = await api.get('/mobiliario/auxiliares/estados-mobiliario')
      return response.data
    } catch (error) {
      console.error('Error obteniendo estados de mobiliario:', error)
      throw error
    }
  },

  // OBTENER ÁREAS (si tienes endpoint)
  async getAreas() {
    try {
      const response = await api.get('/areas')
      return response.data
    } catch (error) {
      console.error('Error obteniendo áreas:', error)
      // Si no hay endpoint de áreas, devolver array vacío
      return []
    }
  }
}