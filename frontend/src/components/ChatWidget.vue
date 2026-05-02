<template>
  <div class="chat-container">

    <!-- BOTÓN FLOTANTE -->
    <div v-if="showBubble" class="chat-bubble" @click="toggle">
        💬
    </div>

    <!-- VENTANA DE CHAT -->
    <Transition name="chat" @after-leave="onAfterLeave">
        <div v-if="chat.isOpen" class="chat-window">
            <div class="chat-header">
            <span>Asistente</span>
                <button @click="toggle">—</button>
                <button @click="chat.clearChat()">🗑</button>
            </div>

            <div class="chat-body" ref="chatBody">
                <TransitionGroup name="msg">
                    <div v-for="(msg, index) in chat.messages" :key="index" :class="msg.from">
                        <div :class="{ thinking: msg.text === 'Pensando' }">
                            {{ msg.text }}
                        </div>
                    </div>
                </TransitionGroup>
            </div>

            <div class="chat-footer">
            <input
                v-model="input"
                @keyup.enter="sendMessage"
                placeholder="Escribe un mensaje..."
            />
            <button @click="sendMessage">Enviar</button>
            </div>
        </div>
    </Transition>


  </div>
</template>

<script setup>
//IMPORTS
import { useChatStore } from '@/stores/chat'
import { ref } from 'vue'
import { nextTick, watch } from 'vue'
import { chatService } from '@/services/chat'


//CONST
const input = ref('')
const chat = useChatStore()
const showBubble = ref(true)
const chatBody = ref(null)


//METODOS
chat.clearChat()

const scrollToBottom = async () => {
  await nextTick()

  if (chatBody.value) {
    chatBody.value.scrollTo({
      top: chatBody.value.scrollHeight,
      behavior: 'smooth'
    })
  }
}


const toggle = () => {
  if (chat.isOpen) {
    // Se va a cerrar → ocultar burbuja por ahora
    showBubble.value = false
    chat.toggle()
  } else {
    // Se va a abrir → ocultar burbuja inmediatamente
    showBubble.value = false
    chat.toggle()
  }
}

const onAfterLeave = () => {
  showBubble.value = true
}

//FUNCION DE ENVIO DE MENSAJE conectado al backend para respuesta del microservicio!
const sendMessage = async () => {
    if (!input.value.trim()) return

    const userText = input.value

    chat.addMessage({
        from: 'user',
        text: userText
    })

    input.value = ''

    const thinkingIndex = chat.messages.length
    chat.addMessage({
        from: 'bot',
        text: 'Pensando...'
    })

    try {
        const data = await chatService.ask(userText)
        chat.messages[thinkingIndex].text = data.answer
    } catch (err) {
        const errorMsg = err.response?.data?.detail || 'No se pudo contactar al asistente'
        chat.messages[thinkingIndex].text = errorMsg
    }
}

watch(
  () => chat.messages.length,
  () => {
    scrollToBottom()
  }
)

watch(
  () => chat.isOpen,
  (open) => {
    if (open) {
      scrollToBottom()
    }
  }
)


</script>



<style scoped>
.chat-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
}

/* BURBUJA */
.chat-bubble {
  width: 60px;
  height: 60px;
  background: #2563eb;
  color: white;
  font-size: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

/* VENTANA */
.chat-window {
  width: 420px;
  height: 520px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
}

/* HEADER */
.chat-header {
  background: #2563eb;
  color: white;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  font-weight: bold;
}

/* BODY */
.chat-body {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}

.user,
.bot {
  display: flex;
  margin: 6px 0;
}

.user {
  justify-content: flex-end;
}

.bot {
  justify-content: flex-start;
}

.user div,
.bot div {
  max-width: 75%;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 14px;
  word-break: break-word;
}

/* MENSAJE USUARIO (VERDE) */
.user div {
  background: #dcfce7;
  border: 1px solid #22c55e;
  color: #065f46;
}

/* MENSAJE BOT (AZUL) */
.bot div {
  background: #dbeafe;
  border: 1px solid #3b82f6;
  color: #1e3a8a;
}


/* FOOTER */
.chat-footer {
  display: flex;
  border-top: 1px solid #ddd;
}

.chat-footer input {
  flex: 1;
  border: none;
  padding: 10px;
}

.chat-footer button {
  background: #2563eb;
  color: white;
  border: none;
  padding: 10px;
  cursor: pointer;
}

.chat-bubble {
  transition: transform 0.2s ease;
}

.chat-bubble:hover {
  transform: scale(1.1);
}

/* ANIMACIÓN GENERAL */
.chat-enter-active,
.chat-leave-active {
  transition: all 0.25s ease;
}

/* Estado inicial (cuando aparece) */
.chat-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}

/* Estado final */
.chat-enter-to {
  opacity: 1;
  transform: scale(1) translateY(0);
}

/* Cuando se va */
.chat-leave-from {
  opacity: 1;
  transform: scale(1);
}

.chat-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}

.thinking {
  font-style: italic;
  opacity: 0.7;
}

.thinking::after {
  content: '...';
  animation: dots 1s steps(3, end) infinite;
}

@keyframes dots {
  0%   { content: '.'; }
  33%  { content: '..'; }
  66%  { content: '...'; }
}


</style>
