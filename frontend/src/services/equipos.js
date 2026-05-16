import api from '@/services/api'

export const equiposService = {

  async getEquipos(params = {}) {
    const response = await api.get('/api/equipos-computo/', { params })
    return response.data
  },

  async createEquipo(data) {
    const response = await api.post('/api/equipos-computo/', data)
    return response.data
  },

  async updateEquipo(id, data) {
    const response = await api.put(`/api/equipos-computo/${id}`, data)
    return response.data
  },

  async retirarEquipo(id) {
    const response = await api.patch(`/api/equipos-computo/${id}/desactivar`) // ← tu endpoint
    return response.data
  },

  async reactivarEquipo(id) {
    const response = await api.patch(`/api/equipos-computo/${id}/reactivar`)
    return response.data
  },

  async getEstados() {
    const response = await api.get('/api/equipos-computo/auxiliares/estados-equipo')
    return response.data
  },

  async getTipos() {
    const response = await api.get('/api/equipos-computo/auxiliares/tipos-equipo')
    return response.data
  },

  async getMarcas() {
    const response = await api.get('/api/equipos-computo/auxiliares/marcas')
    return response.data
  },
}