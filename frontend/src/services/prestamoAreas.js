// services/prestamoAreas.js
import api from '@/services/api'

export const prestamoAreasService = {

  // ── Usuario solicita un área ───────────────────────────────────────────
  // Área → Reservada, Préstamo → Pendiente (espera aprobación admin)
  async crearPrestamo(data) {
    const response = await api.post('/prestamos-areas/', data)
    return response.data
  },

  // ── Admin aprueba solicitud ────────────────────────────────────────────
  // Área → Ocupada, Préstamo → Vigente
  async aprobarSolicitud(prestamoId) {
    const response = await api.patch(`/prestamos-areas/${prestamoId}/aprobar`)
    return response.data
  },

  // ── Admin rechaza solicitud ────────────────────────────────────────────
  // Área → Disponible, Préstamo → Terminado
  async rechazarSolicitud(prestamoId) {
    const response = await api.patch(`/prestamos-areas/${prestamoId}/rechazar`)
    return response.data
  },

  // ── Devolver área (usuario o admin) ───────────────────────────────────
  // Área → Disponible, Préstamo → Terminado
  async devolverPrestamo(id, observaciones = null) {
    const response = await api.patch(
      `/prestamos-areas/${id}/devolver`,
      { observaciones }
    )
    return response.data
  },

  // ── Listar solicitudes pendientes (admin) ──────────────────────────────
  async getPendientes() {
    const response = await api.get('/prestamos-areas/pendientes')
    return response.data
  },

  // ── Listar vigentes ────────────────────────────────────────────────────
  async getPrestamosVigentes() {
    const response = await api.get('/prestamos-areas/vigentes')
    return response.data
  },

  // ── Mis solicitudes activas (usuario) ─────────────────────────────────
  // Incluye vigentes + pendientes
  async getMisSolicitudes() {
    const response = await api.get('/prestamos-areas/mis-solicitudes')
    return response.data
  },

  // ── Verificar si el usuario ya tiene un área activa ───────────────────
  async usuarioTieneAreaActiva() {
    try {
      const solicitudes = await this.getMisSolicitudes()
      return Array.isArray(solicitudes) && solicitudes.length > 0
    } catch {
      return false
    }
  }
}