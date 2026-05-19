import api from './api'

export const chatService = {
  /**
   * Enviar pregunta al asistente virtual.
   * El backend proxy maneja el session_id automáticamente.
   * @param {string} question
   * @returns {{ answer, confidence, source, entities }}
   */
  async ask(question) {
    const response = await api.post('/chat/ask', { question })
    return response.data
  },

  /**
   * Verificar que el microservicio del chatbot esté disponible
   */
  async healthCheck() {
    try {
      const response = await api.get('/chatbot/health')
      return response.data?.status === 'healthy'
    } catch {
      return false
    }
  }
}