import api from '@/services/api'

export const multasService = {

  // ========== CONSULTAS ==========

  /**
   * Obtener todas las multas (admin)
   */
  getMultas: async () => {
    const response = await api.get('/multas/')
    return response.data
  },

  /**
   * Obtener multas pendientes (admin)
   */
  getMultasPendientes: async () => {
    const response = await api.get('/multas/pendientes')
    return response.data
  },

  /**
   * Obtener multas liquidadas (admin)
   */
  getMultasLiquidadas: async () => {
    const response = await api.get('/multas/liquidadas')
    return response.data
  },

  /**
   * Obtener multa por ID
   */
  getMultaById: async (multaId) => {
    const response = await api.get(`/multas/${multaId}`)
    return response.data
  },

  /**
   * Obtener multas de un usuario específico
   */
  getMultasByUsuario: async (usuarioId) => {
    const response = await api.get(`/multas/usuario/${usuarioId}`)
    return response.data
  },

  /**
   * Obtener resumen y estadísticas de multas (admin)
   */
  getResumenMultas: async () => {
    const response = await api.get('/multas/resumen/estadisticas')
    return response.data
  },

  // ========== ACCIONES ADMIN ==========

  /**
   * Crear una nueva multa manualmente (admin)
   */
  crearMulta: async (multaData) => {
    const response = await api.post('/multas/', multaData)
    return response.data
  },

  /**
   * Actualizar datos de una multa (admin)
   */
  actualizarMulta: async (multaId, multaData) => {
    const response = await api.patch(`/multas/${multaId}`, multaData)
    return response.data
  },

  /**
   * Liquidar una multa — marca como pagada (admin)
   */
  liquidarMulta: async (multaId, pagoData) => {
    const response = await api.patch(`/multas/${multaId}/liquidar`, pagoData)
    return response.data
  },

  /**
   * Cambiar estado de una multa (admin)
   */
  cambiarEstadoMulta: async (multaId, estadoData) => {
    const response = await api.patch(`/multas/${multaId}/cambiar-estado`, estadoData)
    return response.data
  }
}