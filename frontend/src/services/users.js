import { api } from './api'

export const userService = {
  /**
   * Obtener lista de usuarios
   * @param {Object} params - Parámetros de paginación y filtro
   * @returns {Promise}
   */
  async getUsers(params = {}) {
    try {
      const cleanParams = {}
      
      // Limpiar y convertir parámetros
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          if (key === 'pagina' || key === 'por_pagina') {
            cleanParams[key] = parseInt(value)
          } else if (key === 'esta_activo') {
            cleanParams[key] = Boolean(value)
          } else {
            cleanParams[key] = value
          }
        }
      })
      
      console.log('📤 GET /api/usuarios con params:', cleanParams)
      const response = await api.get('/usuarios', { params: cleanParams })
      return response.data
    } catch (error) {
      console.error('❌ Error obteniendo usuarios:', error)
      throw this.handleError(error)
    }
  },

  /**
   * Obtener usuario por ID
   * @param {Number} id - ID del usuario
   * @returns {Promise}
   */
  async getUserById(id) {
    try {
      console.log(`📤 GET /api/usuarios/${id}`)
      const response = await api.get(`/usuarios/${id}`)
      return response.data
    } catch (error) {
      console.error(`❌ Error obteniendo usuario ${id}:`, error)
      throw this.handleError(error)
    }
  },

  /**
   * Crear usuario (solo super admin)
   * @param {Object} userData - Datos del usuario
   * @returns {Promise}
   */
  async createUser(userData) {
    try {
      console.log('📤 POST /api/usuarios con data:', userData)
      const response = await api.post('/usuarios', userData)
      return response.data
    } catch (error) {
      console.error('❌ Error creando usuario:', error)
      throw this.handleError(error)
    }
  },

  /**
   * Actualizar usuario
   * @param {Number} id - ID del usuario
   * @param {Object} userData - Datos a actualizar
   * @returns {Promise}
   */
  async updateUser(id, userData) {
    try {
      console.log(`📤 PUT /api/usuarios/${id} con data:`, userData)
      const response = await api.put(`/usuarios/${id}`, userData)
      return response.data
    } catch (error) {
      console.error(`❌ Error actualizando usuario ${id}:`, error)
      throw this.handleError(error)
    }
  },

  /**
   * Eliminar usuario (soft delete - cambia estado a inactivo)
   * @param {Number} id - ID del usuario
   * @returns {Promise}
   */
  async deleteUser(id) {
    try {
      console.log(`📤 DELETE /api/usuarios/${id}`)
      const response = await api.delete(`/usuarios/${id}`)
      return response.data
    } catch (error) {
      console.error(`❌ Error eliminando usuario ${id}:`, error)
      throw this.handleError(error)
    }
  },

  /**
   * Activar/Desactivar usuario
   * @param {Number} id - ID del usuario
   * @param {Boolean} activo - true para activar, false para desactivar
   * @returns {Promise}
   */
  async changeUserStatus(id, activo = true) {
    try {
      console.log(`📤 PATCH /api/usuarios/${id}/estado con activo:`, activo)
      const response = await api.patch(`/usuarios/${id}/estado`, { 
        esta_activo: activo 
      })
      return response.data
    } catch (error) {
      console.error(`❌ Error cambiando estado usuario ${id}:`, error)
      throw this.handleError(error)
    }
  },

  /**
   * Reactivar usuario (alias para changeUserStatus)
   * @param {Number} id - ID del usuario
   * @returns {Promise}
   */
  async reactivateUser(id) {
    return this.changeUserStatus(id, true)
  },

  /**
   * Desactivar usuario (alias para changeUserStatus)
   * @param {Number} id - ID del usuario
   * @returns {Promise}
   */
  async deactivateUser(id) {
    return this.changeUserStatus(id, false)
  },

  /**
   * Obtener tipos de usuario disponibles
   * @returns {Array} - Array de tipos de usuario
   */
  getUserTypes() {
    return [
      { id: 1, nombre: 'Usuario Común', descripcion: 'Solo puede consultar' },
      { id: 2, nombre: 'Admin Básico', descripcion: 'Puede prestar libros' },
      { id: 3, nombre: 'Admin Avanzado', descripcion: 'Puede gestionar recursos' },
      { id: 4, nombre: 'Super Admin', descripcion: 'Puede gestionar usuarios' }
    ]
  },

  /**
   * Obtener relaciones institucionales disponibles
   * @returns {Array} - Array de relaciones institucionales
   */
  getInstitutionalRelations() {
    return [
      { id: 1, nombre: 'Estudiante' },
      { id: 2, nombre: 'Docente' },
      { id: 3, nombre: 'Directivo' },
      { id: 4, nombre: 'Administrativo' },
      { id: 5, nombre: 'Investigador' },
      { id: 6, nombre: 'Externo' }
    ]
  },

  /**
   * Filtrar usuarios excluyendo super admins (tipo 4)
   * @param {Array} usuarios - Array de usuarios
   * @returns {Array} - Usuarios filtrados
   */
  filterNonSuperAdmins(usuarios) {
    if (!Array.isArray(usuarios)) return []
    return usuarios.filter(user => user.tipo_usuario_id !== 4)
  },

  /**
   * Verificar si usuario puede ser editado
   * @param {Object} user - Objeto usuario
   * @returns {Boolean}
   */
  canEditUser(user) {
    if (!user) return false
    // No se puede editar super admins (tipo 4)
    return user.tipo_usuario_id !== 4
  },

  /**
   * Mapear tipo de usuario a nombre legible
   * @param {Number} tipoId - ID del tipo de usuario
   * @returns {String}
   */
  getTipoUsuarioNombre(tipoId) {
    const tipos = {
      1: 'Usuario Común',
      2: 'Admin Básico',
      3: 'Admin Avanzado',
      4: 'Super Admin'
    }
    return tipos[tipoId] || 'Desconocido'
  },

  /**
   * Formatear fecha para mostrar
   * @param {String} fechaString - Fecha en formato ISO
   * @returns {String}
   */
  formatFecha(fechaString) {
    if (!fechaString) return 'N/A'
    try {
      const fecha = new Date(fechaString)
      return fecha.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    } catch {
      return 'Fecha inválida'
    }
  },

  /**
   * Manejo de errores centralizado
   * @param {Error} error - Error original
   * @returns {Error}
   */
  handleError(error) {
    if (error.response) {
      const { status, data } = error.response
      
      // Errores específicos del backend
      const errorMessages = {
        400: data.detail || 'Datos inválidos',
        401: 'No autorizado',
        403: 'No tienes permisos para esta acción',
        404: 'Usuario no encontrado',
        409: 'El usuario ya existe',
        422: 'Error de validación',
        500: 'Error interno del servidor'
      }
      
      const message = errorMessages[status] || data.detail || `Error ${status}`
      return new Error(message)
    }
    
    return error
  }
}