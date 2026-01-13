// frontend/src/composables/useToast.js
import { useToastStore } from '@/stores/toast'

export function useToast() {
  const toastStore = useToastStore()
  
  return {
    success: (message, title = 'Éxito') => 
      toastStore.showSuccess(message, title),
    
    error: (message, title = 'Error') => 
      toastStore.showError(message, title),
    
    warning: (message, title = 'Advertencia') => 
      toastStore.showWarning(message, title),
    
    info: (message, title = 'Información') => 
      toastStore.showInfo(message, title)
  }
}