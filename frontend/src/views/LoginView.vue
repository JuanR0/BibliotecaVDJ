<!-- views/LoginView.vue -->
<template>
  <div class="login-container">
    <div class="login-card">
      <h1>{{ isRegister ? 'Registro' : 'Iniciar Sesión' }}</h1>
      
      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label>Email</label>
          <input 
            v-model="form.email"
            type="email" 
            required
            placeholder="tu@email.com"
          >
        </div>

        <div class="form-group">
          <label>Contraseña</label>
          <input 
            v-model="form.password"
            type="password" 
            required
            placeholder="••••••••"
          >
        </div>

        <div v-if="isRegister" class="form-group">
          <label>Nombre Completo</label>
          <input 
            v-model="form.name"
            type="text" 
            required
            placeholder="Tu nombre completo"
          >
        </div>

        <button 
          type="submit" 
          class="btn btn-primary btn-full"
          :disabled="authStore.isLoading"
        >
          {{ authStore.isLoading ? 'Procesando...' : (isRegister ? 'Registrarse' : 'Iniciar Sesión') }}
        </button>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
      </form>

      <div class="switch-mode">
        <p>
          {{ isRegister ? '¿Ya tienes cuenta?' : '¿No tienes cuenta?' }}
          <a href="#" @click.prevent="toggleMode">
            {{ isRegister ? 'Inicia Sesión' : 'Regístrate' }}
          </a>
        </p>
      </div>

      <div class="additional-actions">
        <button @click="$router.push('/')" class="btn btn-link">
          ← Volver al Inicio
        </button>
        <button @click="$router.push('/healthcheck')" class="btn btn-link">
          🔍 Ver Estado del Sistema
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isRegister = ref(false)
const errorMessage = ref('')

const form = reactive({
  email: '',
  password: '',
  name: ''
})

const toggleMode = () => {
  isRegister.value = !isRegister.value
  errorMessage.value = ''
}

const handleSubmit = async () => {
  errorMessage.value = ''

  const result = isRegister.value 
    ? await authStore.register(form)
    : await authStore.login(form)

  if (result.success) {
    router.push('/')
  } else {
    errorMessage.value = result.error
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.login-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  width: 100%;
  max-width: 400px;
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.login-form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e1e5e9;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

.btn-full {
  width: 100%;
  margin-top: 1rem;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 0.75rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
  text-align: center;
}

.switch-mode {
  text-align: center;
  margin-bottom: 1.5rem;
}

.switch-mode a {
  color: #667eea;
  text-decoration: none;
}

.additional-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.btn-link {
  background: transparent;
  color: #667eea;
  border: none;
  text-decoration: underline;
}
</style>