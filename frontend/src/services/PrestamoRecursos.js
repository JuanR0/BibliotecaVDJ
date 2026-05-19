import api from '@/services/api'

// ── Helpers de estado visual por tiempo ───────────────────────────────────
// Para préstamos por horas usamos fecha_devolucion (equipos) o
// fecha_devolucion_esperada (áreas)

export function calcularEstadoTiempo(fechaDevolucion) {
  if (!fechaDevolucion) return 'sin_fecha'
  const ahora    = new Date()
  const devolver = new Date(fechaDevolucion)
  const diffMs   = devolver - ahora          // positivo = queda tiempo
  const diffMin  = diffMs / 60000

  if (diffMin < 0)   return 'excedido'       // ya pasó
  if (diffMin <= 10) return 'peligro'        // ≤ 10 min
  if (diffMin <= 30) return 'advertencia'    // ≤ 30 min
  return 'vigente'                           // más de 30 min
}

export function minutosRestantes(fechaDevolucion) {
  if (!fechaDevolucion) return 0
  const diffMs = new Date(fechaDevolucion) - new Date()
  return Math.ceil(diffMs / 60000)
}

export function formatTiempo(fechaDevolucion) {
  const min = minutosRestantes(fechaDevolucion)
  if (min < 0) {
    const abs = Math.abs(min)
    return abs >= 60
      ? `+${Math.floor(abs/60)}h ${abs%60}m excedido`
      : `+${abs}m excedido`
  }
  return min >= 60
    ? `${Math.floor(min/60)}h ${min%60}m restantes`
    : `${min}m restantes`
}

// ── Servicio Equipos ───────────────────────────────────────────────────────
export const prestamoEquipoService = {

  async getVigentes() {
    const r = await api.get('/prestamos-equipos-computo/vigentes')
    return r.data
  },

  async getHistorial(params = {}) {
    const r = await api.get('/prestamos-equipos-computo/historial', { params })
    return r.data
  },

  async crearPrestamo(data) {
    const r = await api.post('/prestamos-equipos-computo/', data)
    return r.data
  },

  async registrarDevolucion(prestamoId, observaciones = null) {
    const r = await api.patch(`/prestamos-equipos-computo/${prestamoId}/devolver`, { observaciones })
    return r.data
  },
}


// ── Servicio Áreas ─────────────────────────────────────────────────────────
export const prestamoAreaService = {

  async getVigentes() {
    const r = await api.get('/prestamos-areas/vigentes')
    return r.data
  },

  async getHistorial(params = {}) {
    const r = await api.get('/prestamos-areas/historial', { params })
    return r.data
  },

  async crearPrestamo(data) {
    const r = await api.post('/prestamos-areas/', data)
    return r.data
  },

  async registrarDevolucion(prestamoId, observaciones = null) {
    const r = await api.patch(`/prestamos-areas/${prestamoId}/devolver`, { observaciones })
    return r.data
  },
}