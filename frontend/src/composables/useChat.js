import { ref } from 'vue'
import { chatService } from '@/services/chat'

export function useChat() {
  const messages = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function sendMessage(question) {
    if (!question.trim() || loading.value) return

    // Agrega el mensaje del usuario
    messages.value.push({
      role: 'user',
      content: question,
      timestamp: new Date()
    })

    loading.value = true
    error.value = null

    try {
      const data = await chatService.ask(question)

      // Agrega la respuesta del bot
      messages.value.push({
        role: 'bot',
        content: data.answer,
        confidence: data.confidence,
        source: data.source,
        entities: data.entities || {},
        timestamp: new Date()
      })
    } catch (err) {
      const msg = err.response?.data?.detail || 'Error al contactar al asistente'
      error.value = msg

      messages.value.push({
        role: 'bot',
        content: msg,
        isError: true,
        timestamp: new Date()
      })
    } finally {
      loading.value = false
    }
  }

  function clearChat() {
    messages.value = []
    error.value = null
  }

  return { messages, loading, error, sendMessage, clearChat }
}