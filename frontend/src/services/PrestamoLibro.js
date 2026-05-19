// services/PrestamoLibro.js
import api from '@/services/api'

// ── Helpers de estado visual ───────────────────────────────────────────────
// El estado "Vencido" se calcula en el frontend.
// En BD un préstamo es siempre Vigente (1) hasta que el bibliotecario lo devuelve.

export function calcularEstadoVisual(prestamo) {
  if (prestamo.estado_prestamo_id === 3) return 'terminado'

  const hoy      = new Date(); hoy.setHours(0, 0, 0, 0)
  const devolver = new Date(prestamo.fecha_devolucion_esperada); devolver.setHours(0, 0, 0, 0)
  const diff     = Math.ceil((devolver - hoy) / 86400000)

  if (diff < 0)  return 'vencido'
  if (diff <= 3) return 'por_vencer'
  return 'vigente'
}

export function calcularDiasRestantes(prestamo) {
  const hoy      = new Date(); hoy.setHours(0, 0, 0, 0)
  const devolver = new Date(prestamo.fecha_devolucion_esperada); devolver.setHours(0, 0, 0, 0)
  return Math.ceil((devolver - hoy) / 86400000)
}

// ── Servicio ───────────────────────────────────────────────────────────────
export const prestamoLibroService = {

  // Contadores para el header de GestionPrestamos
  async getStats() {
    const r = await api.get('/prestamos-libros/stats')
    return r.data
  },

  // Préstamos vigentes (incluye vencidos — el frontend los separa por fecha)
  async getVigentes(params = {}) {
    const r = await api.get('/prestamos-libros/vigentes', { params })
    return r.data
  },

  // Historial — préstamos terminados
  async getHistorial(params = {}) {
    const r = await api.get('/prestamos-libros/historial', { params })
    return r.data
  },

  // Mis préstamos — para Mi Perfil (nivel 1)
  // Enriquece cada préstamo con estado visual calculado en el cliente
  async getPrestamosUsuario(soloVigentes = true) {
    const r = await api.get('/prestamos-libros/mis-prestamos', {
      params: { solo_vigentes: soloVigentes }
    })
    return r.data.map(p => ({
      ...p,
      estadoVisual:  calcularEstadoVisual(p),
      diasRestantes: calcularDiasRestantes(p),
      // Aliases para compatibilidad con UserMenu existente
      type:         'book',
      name:          p.libro_titulo,
      loanDate:      p.fecha_prestamo,
      returnDate:    p.fecha_devolucion_esperada,
      status:        calcularEstadoVisual(p) === 'vencido'    ? 'overdue'
                   : calcularEstadoVisual(p) === 'por_vencer' ? 'warning'
                   : calcularEstadoVisual(p) === 'terminado'  ? 'completed'
                   : 'active',
    }))
  },

  // Crear préstamo — el bibliotecario lo registra presencialmente
  async crearPrestamo(data) {
    const r = await api.post('/prestamos-libros/', data)
    return r.data
  },

  // Registrar devolución — el bibliotecario confirma que el libro fue devuelto
  async registrarDevolucion(prestamoId, observaciones = null) {
    const r = await api.patch(`/prestamos-libros/${prestamoId}/devolver`, { observaciones })
    return r.data
  },

  // Editar fecha de devolución esperada u observaciones
  async editarPrestamo(prestamoId, data) {
    const r = await api.patch(`/prestamos-libros/${prestamoId}/editar`, data)
    return r.data
  },

  // Obtener préstamo por ID
  async getPrestamoById(id) {
    const r = await api.get(`/prestamos-libros/${id}`)
    return r.data
  },
}