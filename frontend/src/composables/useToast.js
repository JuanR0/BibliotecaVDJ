// src/composables/useToast.js
import { useToastStore } from '@/stores/toast'

export const useToast = () => {
  const toastStore = useToastStore()
  
  return {
    showSuccess: (message, title = 'Éxito') => 
      toastStore.showSuccess(message, title),
    
    showError: (message, title = 'Error') => 
      toastStore.showError(message, title),
    
    showWarning: (message, title = 'Advertencia') => 
      toastStore.showWarning(message, title),
    
    showInfo: (message, title = 'Información') => 
      toastStore.showInfo(message, title),
    
    clearAll: () => toastStore.clearAll()
  }
}