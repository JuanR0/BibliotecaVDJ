// main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

const pinia = createPinia()


const app = createApp(App)

app.use(pinia)

const authStore = useAuthStore()

await authStore.initializeAuth()

app.use(router)

app.mount('#app')