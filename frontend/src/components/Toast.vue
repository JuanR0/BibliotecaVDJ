<template>
  <div class="toast-container">
    <TransitionGroup name="toast-list">
      <div 
        v-for="toast in toasts" 
        :key="toast.id"
        :class="['toast', `toast-${toast.type}`]"
        @click="removeToast(toast.id)"
      >
        <div class="toast-icon">
          <span v-if="toast.type === 'success'">✅</span>
          <span v-else-if="toast.type === 'error'">❌</span>
          <span v-else-if="toast.type === 'warning'">⚠️</span>
          <span v-else-if="toast.type === 'info'">ℹ️</span>
        </div>
        <div class="toast-content">
          <div class="toast-title">{{ toast.title }}</div>
          <div class="toast-message">{{ toast.message }}</div>
        </div>
        <button class="toast-close" @click.stop="removeToast(toast.id)">
          ×
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  position: {
    type: String,
    default: 'top-right',
    validator: (value) => ['top-right', 'top-left', 'bottom-right', 'bottom-left'].includes(value)
  },
  duration: {
    type: Number,
    default: 4000
  }
})

const toasts = ref([])
let toastId = 0

// Métodos públicos que se expondrán
const addToast = (type, title, message) => {
  const id = ++toastId
  const toast = {
    id,
    type,
    title,
    message,
    timer: setTimeout(() => {
      removeToast(id)
    }, props.duration)
  }
  
  toasts.value.push(toast)
  return id
}

const removeToast = (id) => {
  const index = toasts.value.findIndex(toast => toast.id === id)
  if (index !== -1) {
    clearTimeout(toasts.value[index].timer)
    toasts.value.splice(index, 1)
  }
}

const clearAll = () => {
  toasts.value.forEach(toast => clearTimeout(toast.timer))
  toasts.value = []
}

// Exponer métodos para usar desde fuera
defineExpose({
  addToast,
  removeToast,
  clearAll
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  z-index: 9999;
  max-width: 350px;
  pointer-events: none;
}

/* Posiciones */
.top-right {
  top: 20px;
  right: 20px;
}

.top-left {
  top: 20px;
  left: 20px;
}

.bottom-right {
  bottom: 20px;
  right: 20px;
}

.bottom-left {
  bottom: 20px;
  left: 20px;
}

/* Toast individual */
.toast {
  display: flex;
  align-items: flex-start;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background: white;
  pointer-events: auto;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: slideIn 0.3s ease-out;
}

.toast:hover {
  transform: translateX(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

/* Colores según tipo */
.toast-success {
  border-left: 4px solid #10b981;
  background: #f0fdf4;
}

.toast-error {
  border-left: 4px solid #ef4444;
  background: #fef2f2;
}

.toast-warning {
  border-left: 4px solid #f59e0b;
  background: #fffbeb;
}

.toast-info {
  border-left: 4px solid #3b82f6;
  background: #eff6ff;
}

/* Icono */
.toast-icon {
  font-size: 20px;
  margin-right: 12px;
  flex-shrink: 0;
}

/* Contenido */
.toast-content {
  flex-grow: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
  color: #1f2937;
}

.toast-message {
  font-size: 13px;
  line-height: 1.4;
  color: #6b7280;
}

/* Botón cerrar */
.toast-close {
  background: none;
  border: none;
  font-size: 24px;
  line-height: 1;
  color: #9ca3af;
  cursor: pointer;
  padding: 0;
  margin-left: 10px;
  flex-shrink: 0;
  transition: color 0.2s;
}

.toast-close:hover {
  color: #374151;
}

/* Animaciones */
.toast-list-enter-active,
.toast-list-leave-active {
  transition: all 0.4s ease;
}

.toast-list-enter-from,
.toast-list-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-list-move {
  transition: transform 0.4s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Responsive */
@media (max-width: 640px) {
  .toast-container {
    max-width: calc(100% - 40px);
    left: 20px;
    right: 20px;
  }
  
  .toast {
    padding: 12px;
  }
}
</style>