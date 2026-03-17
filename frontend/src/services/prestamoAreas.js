import api from '@/services/api'

export const prestamoAreasService = {
    async crearPrestamo(data){
        const response = await api.post('/prestamos-areas/', data)
        return response.data
    },

    async devolverPrestamo(id){
        const response = await api.patch(
            `/prestamos-areas/${id}/devolver`,
            {} // ⚠️ enviar body vacío
        )

        return response.data
    },

    async getPrestamosVigentes(){
        const response = await api.get('/prestamos-areas/vigentes')
        return response.data
    }
}