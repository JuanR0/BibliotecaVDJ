import api from '@/services/api'

export const prestamoLibroService = {

  // ==============================
  // LISTAR TODOS LOS PRÉSTAMOS
  // ==============================
  async getPrestamos(params = {}) {
    try {
      const response = await api.get('/prestamos-libros/', { params })
      return response.data
    } catch (error) {
      console.error('Error obteniendo préstamos:', error)
      throw error
    }
  },

  // ==============================
  // OBTENER PRÉSTAMO POR ID
  // ==============================
  async getPrestamoById(id) {
    try {
      const response = await api.get(`/prestamos-libros/${id}`)
      return response.data
    } catch (error) {
      console.error(`Error obteniendo préstamo ${id}:`, error)
      throw error
    }
  },

  // ==============================
  // CREAR PRÉSTAMO
  // ==============================
  async crearPrestamo(prestamoData) {
    try {
      console.log('📤 Creando préstamo con:', prestamoData)
      const response = await api.post('/prestamos-libros/', prestamoData)
      return response.data
    } catch (error) {
      console.error('Error creando préstamo:', error)
      throw error
    }
  },

  // ==============================
  // DEVOLVER PRÉSTAMO
  // ==============================
  async devolverPrestamo(prestamoId, observaciones = null) {
    try {
      const response = await api.patch(
        `/prestamos-libros/${prestamoId}/devolver`,
        { observaciones }
      )
      return response.data
    } catch (error) {
      console.error(`Error devolviendo préstamo ${prestamoId}:`, error)
      throw error
    }
  },

  // ==============================
  // LISTAR PRÉSTAMOS VIGENTES
  // ==============================
  async getPrestamosVigentes(params = {}) {
    try {
      const response = await api.get('/prestamos-libros/vigentes', { params })
      return response.data
    } catch (error) {
      console.error('Error obteniendo préstamos vigentes:', error)
      throw error
    }
  },

  // ==============================
  // LISTAR PRÉSTAMOS DE UN USUARIO
  // ==============================
  async getPrestamosUsuario(usuarioId, soloVigentes = true) {
    try {
      const response = await api.get(
        '/prestamos-libros/mis-prestamos',
        { params: { solo_vigentes: soloVigentes } }
      )
      
    return response.data.map(p => ({
      id: p.id,
      type: 'book',
      name: p.libro_titulo,
      loanDate: p.fecha_prestamo,
      returnDate: p.fecha_devolucion_esperada,
      status: p.estado_prestamo_id === 1
        ? 'active'
        : 'completed'
    }))
    
    } catch (error) {
      console.error(`Error obteniendo préstamos del usuario ${usuarioId}:`, error)
      throw error
    }
  }
}
