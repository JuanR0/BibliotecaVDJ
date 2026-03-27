// services/PrestamoLibro.js
import api from '@/services/api'

export const prestamoLibroService = {

  // ==============================
  // LISTAR TODOS LOS PRÉSTAMOS
  // ==============================
  async getPrestamos(params = {}) {
    const response = await api.get('/prestamos-libros/', { params })
    return response.data
  },

  // ==============================
  // OBTENER PRÉSTAMO POR ID
  // ==============================
  async getPrestamoById(id) {
    const response = await api.get(`/prestamos-libros/${id}`)
    return response.data
  },

  // ==============================
  // CREAR PRÉSTAMO
  // El backend rechaza con 403 si el usuario tiene multas pendientes.
  // ==============================
  async crearPrestamo(prestamoData) {
    const response = await api.post('/prestamos-libros/', prestamoData)
    return response.data
  },

  // ==============================
  // DEVOLVER PRÉSTAMO
  // Respuesta: { prestamo, multa_generada, mensaje }
  // multa_generada es null si no hubo retraso,
  // o { id, costo_monetario, dias_excedidos, observaciones } si hubo multa.
  // ==============================
  async devolverPrestamo(prestamoId, observaciones = null) {
    const response = await api.patch(
      `/prestamos-libros/${prestamoId}/devolver`,
      { observaciones }
    )
    return response.data  // { prestamo, multa_generada, mensaje }
  },

  // ==============================
  // LISTAR PRÉSTAMOS VIGENTES
  // ==============================
  async getPrestamosVigentes(params = {}) {
    const response = await api.get('/prestamos-libros/vigentes', { params })
    return response.data
  },

  // ==============================
  // LISTAR PRÉSTAMOS DEL USUARIO ACTUAL
  // Retorna array con formato para la tabla de UserMenu
  // ==============================
  async getPrestamosUsuario(soloVigentes = false) {
    const response = await api.get('/prestamos-libros/mis-prestamos', {
      params: { solo_vigentes: soloVigentes }
    })

    const hoy = new Date()
    hoy.setHours(0, 0, 0, 0)

    return response.data.map(p => {
      const fechaDevolucion = new Date(p.fecha_devolucion_esperada)
      fechaDevolucion.setHours(0, 0, 0, 0)

      const diffMs = fechaDevolucion - hoy
      const diffDias = Math.ceil(diffMs / (1000 * 60 * 60 * 24))

      let status = 'active'
      if (diffDias < 0) {
        status = 'overdue'          // Vencido
      } else if (diffDias <= 7) {
        status = 'warning'          // Por vencer (próximos 7 días)
      }

      // Si el préstamo ya fue devuelto, siempre "completed"
      if (p.estado_prestamo_id !== 1) {
        status = 'completed'
      }

      return {
        id: p.id,
        type: 'book',
        name: p.libro_titulo,
        loanDate: p.fecha_prestamo,
        returnDate: p.fecha_devolucion_esperada,
        status,
        diasRestantes: diffDias,
        diasExcedidos: p.dias_excedidos || 0
      }
    })
  }
}