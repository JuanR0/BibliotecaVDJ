<template>
  <div class="chat-wrapper">

    <!-- ══ BURBUJA FLOTANTE — solo cuando el chat está cerrado ══ -->
    <transition name="bubble">
      <button v-if="!chat.isOpen" class="chat-bubble" @click="chat.toggle()" aria-label="Abrir asistente">
        <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
        </svg>
      </button>
    </transition>

    <!-- ══ VENTANA DE CHAT ══ -->
    <transition name="chat-window">
      <div v-if="chat.isOpen" class="chat-window">

        <!-- Header -->
        <div class="chat-header">
          <div class="header-info">
            <div class="header-avatar">
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
              </svg>
            </div>
            <div class="header-texto">
              <span class="header-nombre">Asistente BiblioVDJ</span>
              <span class="header-estado">
                <span class="estado-dot" :class="{ 'dot-offline': chatOffline }"></span>
                {{ chatOffline ? 'No disponible' : 'En línea' }}
              </span>
            </div>
          </div>
          <div class="header-acciones">
            <button class="header-btn" @click="chat.clearChat()" title="Limpiar conversación">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
            <button class="header-btn header-btn-close" @click="chat.toggle()" title="Minimizar">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Aviso chatbot offline -->
        <div v-if="chatOffline" class="aviso-offline">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
          El asistente no está disponible en este momento
        </div>

        <!-- Cuerpo de mensajes -->
        <div class="chat-body" ref="chatBody">
          <TransitionGroup name="msg" tag="div" class="mensajes-lista">
            <div
              v-for="(msg, index) in chat.messages"
              :key="index"
              class="mensaje-fila"
              :class="msg.from === 'user' ? 'fila-user' : 'fila-bot'"
            >
              <div v-if="msg.from === 'bot'" class="msg-avatar">
                <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
                </svg>
              </div>

              <div
                class="burbuja"
                :class="[
                  msg.from === 'user' ? 'burbuja-user' : 'burbuja-bot',
                  { 'burbuja-error': msg.isError, 'burbuja-ratelimit': msg.isRateLimit }
                ]"
              >
                <span :class="{ thinking: msg.isThinking }">{{ msg.text }}</span>
              </div>
            </div>
          </TransitionGroup>
        </div>

        <!-- Aviso de rate limit activo -->
        <transition name="fade">
          <div v-if="rateLimitActivo" class="aviso-ratelimit">
            <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Espera {{ rateLimitSegundos }}s antes de enviar otra pregunta
          </div>
        </transition>

        <!-- Footer / Input -->
        <div class="chat-footer">
          <input
            v-model="input"
            @keyup.enter="sendMessage"
            placeholder="Escribe un mensaje..."
            class="chat-input"
            :disabled="enviando || rateLimitActivo || chatOffline"
            ref="inputRef"
          />
          <button
            @click="sendMessage"
            class="btn-enviar"
            :disabled="!input.trim() || enviando || rateLimitActivo || chatOffline"
          >
            <svg v-if="!enviando" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
            </svg>
            <div v-else class="spinner-enviar"></div>
          </button>
        </div>

      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'
import { chatService } from '@/services/chat'

const chat         = useChatStore()
const input        = ref('')
const enviando     = ref(false)
const chatBody     = ref(null)
const inputRef     = ref(null)
const chatOffline  = ref(false)

// Rate limit
const rateLimitActivo   = ref(false)
const rateLimitSegundos = ref(0)
let   rateLimitTimer    = null

chat.clearChat()

// ── Scroll al fondo ────────────────────────────────────────────────────────
const scrollToBottom = async () => {
  await nextTick()
  if (chatBody.value) {
    chatBody.value.scrollTo({ top: chatBody.value.scrollHeight, behavior: 'smooth' })
  }
}

// ── Activar bloqueo por rate limit ─────────────────────────────────────────
const activarRateLimit = (segundos = 10) => {
  rateLimitActivo.value   = true
  rateLimitSegundos.value = segundos
  clearInterval(rateLimitTimer)
  rateLimitTimer = setInterval(() => {
    rateLimitSegundos.value--
    if (rateLimitSegundos.value <= 0) {
      rateLimitActivo.value = false
      clearInterval(rateLimitTimer)
    }
  }, 1000)
}

// ── Enviar mensaje ─────────────────────────────────────────────────────────
const sendMessage = async () => {
  const texto = input.value.trim()
  if (!texto || enviando.value || rateLimitActivo.value || chatOffline.value) return

  chat.addMessage({ from: 'user', text: texto })
  input.value   = ''
  enviando.value = true

  // Indicador "Pensando..."
  const thinkingIndex = chat.messages.length
  chat.addMessage({ from: 'bot', text: 'Pensando...', isThinking: true })

  try {
    const data = await chatService.ask(texto)
    // Reemplazar el mensaje de thinking con la respuesta real
    chat.messages[thinkingIndex] = { from: 'bot', text: data.answer }

  } catch (err) {
    const status = err.response?.status
    const detail = err.response?.data?.detail

    if (status === 429) {
      // Rate limit — mensaje amigable + bloqueo temporal
      const waitSeconds = typeof detail === 'object'
        ? (detail.wait_seconds ?? 10)
        : 10

      chat.messages[thinkingIndex] = {
        from:          'bot',
        text:          'Espera un momento antes de enviar otra pregunta 🙏',
        isRateLimit:   true
      }
      activarRateLimit(waitSeconds)

    } else if (status === 503 || status === 504) {
      // Chatbot caído o timeout
      chatOffline.value = true
      chat.messages[thinkingIndex] = {
        from:    'bot',
        text:    'El asistente no está disponible en este momento. Intenta más tarde.',
        isError: true
      }

    } else {
      // Error genérico
      chat.messages[thinkingIndex] = {
        from:    'bot',
        text:    detail?.message ?? detail ?? 'No se pudo obtener una respuesta. Intenta de nuevo.',
        isError: true
      }
    }
  } finally {
    enviando.value = false
  }
}

// ── Watchers ────────────────────────────────────────────────────────────────
watch(() => chat.messages.length, () => scrollToBottom())

watch(() => chat.isOpen, async (open) => {
  if (open) {
    chatOffline.value = false  // reintentar al abrir
    await scrollToBottom()
    await nextTick()
    inputRef.value?.focus()
  }
})
</script>

<style scoped>
/* ── Wrapper — fijo en esquina inferior derecha ─────────────────────────── */
.chat-wrapper {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

/* ── Burbuja flotante ────────────────────────────────────────────────────── */
.chat-bubble {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #1a4731, #2d6a4f);
  color: #fff;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(26, 71, 49, 0.4);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.chat-bubble:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 28px rgba(26, 71, 49, 0.5);
}

/* ── Ventana de chat ─────────────────────────────────────────────────────── */
.chat-window {
  width: 360px;
  height: 500px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.18);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(26, 71, 49, 0.12);
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.chat-header {
  background: linear-gradient(135deg, #1a4731, #2d6a4f);
  padding: 12px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}
.header-info   { display:flex; align-items:center; gap:10px; }
.header-avatar {
  width: 36px; height: 36px;
  background: rgba(255,255,255,.15);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #fff; flex-shrink: 0;
}
.header-texto  { display:flex; flex-direction:column; }
.header-nombre { font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:700; color:#fff; line-height:1.2; }
.header-estado { display:flex; align-items:center; gap:4px; font-size:.68rem; color:rgba(255,255,255,.7); }
.estado-dot    { width:6px; height:6px; background:#4ade80; border-radius:50%; animation:pulse-dot 2s infinite; }
.dot-offline   { background:#f87171; animation:none; }
@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:.4} }
.header-acciones { display:flex; gap:6px; }
.header-btn {
  width:28px; height:28px;
  background:rgba(255,255,255,.15); border:none; border-radius:7px;
  color:rgba(255,255,255,.85); cursor:pointer;
  display:flex; align-items:center; justify-content:center;
  transition:background .18s;
}
.header-btn:hover { background:rgba(255,255,255,.25); }

/* ── Aviso offline ───────────────────────────────────────────────────────── */
.aviso-offline {
  display: flex; align-items: center; gap: .5rem;
  padding: .5rem .875rem;
  background: #fff5f5; border-bottom: 1px solid #fca5a5;
  font-size: .75rem; color: #b91c1c; font-weight: 600;
  flex-shrink: 0;
}

/* ── Cuerpo ──────────────────────────────────────────────────────────────── */
.chat-body {
  flex: 1; overflow-y: auto;
  padding: 14px 12px;
  background: #f8fdf9;
  display: flex; flex-direction: column;
}
.chat-body::-webkit-scrollbar { width:4px; }
.chat-body::-webkit-scrollbar-track { background:transparent; }
.chat-body::-webkit-scrollbar-thumb { background:#d4e8da; border-radius:4px; }
.mensajes-lista {
  display:flex; flex-direction:column; gap:6px;
  min-height:100%; justify-content:flex-end;
}

/* ── Filas ───────────────────────────────────────────────────────────────── */
.mensaje-fila { display:flex; align-items:flex-end; gap:6px; }
.fila-user    { justify-content:flex-end; }
.fila-bot     { justify-content:flex-start; }
.msg-avatar {
  width:26px; height:26px;
  background:linear-gradient(135deg,#1a4731,#2d6a4f);
  border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  color:#fff; flex-shrink:0;
}

/* ── Burbujas ────────────────────────────────────────────────────────────── */
.burbuja {
  max-width:72%; padding:9px 13px; border-radius:18px;
  font-family:'DM Sans',sans-serif; font-size:.84rem;
  line-height:1.45; word-break:break-word;
}
.burbuja-user {
  background:linear-gradient(135deg,#1a4731,#2d6a4f);
  color:#fff; border-bottom-right-radius:4px;
}
.burbuja-bot {
  background:#fff; color:#1a2e1a;
  border:1.5px solid #d4e8da;
  border-bottom-left-radius:4px;
  box-shadow:0 1px 4px rgba(0,0,0,.06);
}
.burbuja-error {
  background:#fff5f5 !important;
  border-color:#fca5a5 !important;
  color:#b91c1c !important;
}
.burbuja-ratelimit {
  background:#fef3c7 !important;
  border-color:#fcd34d !important;
  color:#92400e !important;
}

/* Pensando */
.thinking { font-style:italic; color:#9ab5a0; }
.thinking::after {
  content:'';
  animation:dots 1.2s steps(3,end) infinite;
}
@keyframes dots {
  0%   { content:''; }
  33%  { content:'.'; }
  66%  { content:'..'; }
  100% { content:'...'; }
}

/* ── Aviso rate limit ────────────────────────────────────────────────────── */
.aviso-ratelimit {
  display:flex; align-items:center; gap:.5rem;
  padding:.45rem .875rem;
  background:#fef3c7; border-top:1px solid #fcd34d;
  font-size:.75rem; color:#92400e; font-weight:600;
  flex-shrink:0;
}

/* ── Footer ──────────────────────────────────────────────────────────────── */
.chat-footer {
  display:flex; align-items:center; gap:8px;
  padding:10px 12px;
  border-top:1.5px solid #eef5f0;
  background:#fff; flex-shrink:0;
}
.chat-input {
  flex:1; border:1.5px solid #d4e8da; border-radius:22px;
  padding:8px 14px;
  font-family:'DM Sans',sans-serif; font-size:.84rem; color:#1a2e1a;
  outline:none; background:#f8fdf9;
  transition:border-color .18s;
}
.chat-input:focus       { border-color:#52b788; background:#fff; }
.chat-input::placeholder{ color:#9ab5a0; }
.chat-input:disabled    { opacity:.5; cursor:not-allowed; }
.btn-enviar {
  width:38px; height:38px;
  background:linear-gradient(135deg,#1a4731,#2d6a4f);
  border:none; border-radius:50%; color:#fff; cursor:pointer;
  display:flex; align-items:center; justify-content:center;
  flex-shrink:0; transition:all .2s;
}
.btn-enviar:hover:not(:disabled) { background:#111; transform:scale(1.05); }
.btn-enviar:disabled { opacity:.4; cursor:not-allowed; }
.spinner-enviar {
  width:14px; height:14px;
  border:2px solid rgba(255,255,255,.3);
  border-top-color:#fff; border-radius:50%;
  animation:spin .6s linear infinite;
}
@keyframes spin { to{transform:rotate(360deg)} }

/* ── Animaciones ─────────────────────────────────────────────────────────── */
.bubble-enter-active { transition:all .25s cubic-bezier(.34,1.56,.64,1); }
.bubble-leave-active { transition:all .18s ease-in; }
.bubble-enter-from, .bubble-leave-to { opacity:0; transform:scale(0.5); }

.chat-window-enter-active { transition:all .3s cubic-bezier(.22,1,.36,1); }
.chat-window-leave-active { transition:all .2s ease-in; }
.chat-window-enter-from   { opacity:0; transform:translateY(20px) scale(0.95); }
.chat-window-leave-to     { opacity:0; transform:translateY(16px) scale(0.95); }

.msg-enter-active { transition:all .22s ease-out; }
.msg-enter-from   { opacity:0; transform:translateY(8px); }
.msg-leave-active { transition:none; }

.fade-enter-active, .fade-leave-active { transition:opacity .2s; }
.fade-enter-from,   .fade-leave-to     { opacity:0; }
</style>