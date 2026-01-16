import { h, provide } from 'vue'
import ToastComponent from '@/components/Toast.vue'

export const ToastProvider = {
  install(app) {
    const toast = {
      addToast: null,
      removeToast: null
    }
    
    // Crear un componente wrapper que maneje el estado del toast
    const wrapper = {
      setup() {
        const methods = {}
        
        const onMountedCallback = (add, remove) => {
          toast.addToast = add
          toast.removeToast = remove
        }
        
        return () => 
          h(ToastComponent, {
            ref: methods,
            onMounted: onMountedCallback,
            duration: 5000
          })
      }
    }
    
    // Proveer la API del toast
    provide('toast', toast)
    
    // Registrar el componente globalmente
    app.component('ToastWrapper', wrapper)
  }
}