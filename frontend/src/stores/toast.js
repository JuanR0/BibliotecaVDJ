import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  // Referencia al componente Toast
  const toastRef = ref(null)
  
  // Métodos para mostrar toasts
  const showSuccess = (message, title = 'Éxito') => {
    return toastRef.value?.addToast('success', title, message)
  }
  
  const showError = (message, title = 'Error') => {
    return toastRef.value?.addToast('error', title, message)
  }
  
  const showWarning = (message, title = 'Advertencia') => {
    return toastRef.value?.addToast('warning', title, message)
  }
  
  const showInfo = (message, title = 'Información') => {
    return toastRef.value?.addToast('info', title, message)
  }
  
  // Método para registrar la referencia del componente
  const setToastRef = (ref) => {
    toastRef.value = ref
  }
  
  // Método para limpiar todos los toasts
  const clearAll = () => {
    toastRef.value?.clearAll()
  }
  
  return {
    // Métodos públicos
    showSuccess,
    showError,
    showWarning,
    showInfo,
    setToastRef,
    clearAll
  }
})