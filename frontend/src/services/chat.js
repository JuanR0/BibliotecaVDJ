import api from './api'

export const chatService = {
  async ask(question) {
    const response = await api.post('/chat/ask', { question })
    return response.data
  }
}