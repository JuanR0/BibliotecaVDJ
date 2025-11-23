<!-- views/Login.vue -->
<template>
  <div class="login-container">
    <div class="login-card">
      <h1>{{ isRegister ? 'Registrarse' : 'Iniciar Sesión' }}</h1>
      
      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label for="codigo_universitario">Código Universitario</label>
          <input 
            id="codigo_universitario"
            v-model="form.codigo_universitario"
            type="text" 
            required
            placeholder="Ej: U20234567"
            :disabled="isLoading"
          >
        </div>

        <div class="form-group">
          <label for="clave_acceso">Clave de Acceso</label>
          <input 
            id="clave_acceso"
            v-model="form.clave_acceso"
            type="password" 
            required
            placeholder="••••••••"
            :disabled="isLoading"
          >
        </div>

        <div v-if="isRegister" class="form-group">
          <label for="nombre_completo">Nombre Completo</label>
          <input 
            id="nombre_completo"
            v-model="form.nombre_completo"
            type="text" 
            required
            placeholder="Ej: Juan Pérez García"
            :disabled="isLoading"
          >
        </div>

        <button 
          type="submit" 
          class="btn btn-primary btn-full"
          :disabled="isLoading"
        >
          <span v-if="isLoading">⏳ Procesando...</span>
          <span v-else>{{ isRegister ? 'Crear Cuenta' : 'Ingresar' }}</span>
        </button>

        <div v-if="errorMessage" class="error-message">
          ❌ {{ errorMessage }}
        </div>

        <div v-if="successMessage" class="success-message">
          ✅ {{ successMessage }}
        </div>
      </form>

      <div class="switch-mode">
        <p>
          {{ isRegister ? '¿Ya tienes cuenta?' : '¿No tienes cuenta?' }}
          <a href="#" @click.prevent="toggleMode">
            {{ isRegister ? 'Inicia Sesión' : 'Regístrate aquí' }}
          </a>
        </p>
      </div>

      <div class="additional-actions">
        <button @click="$router.push('/')" class="btn btn-link">
          ← Volver al Inicio
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '@/services/api'

export default {
  name: 'Login',
  data() {
    return {
      isRegister: false,
      isLoading: false,
      errorMessage: '',
      successMessage: '',
      form: {
        codigo_universitario: '',
        clave_acceso: '',
        nombre_completo: ''
      }
    }
  },
  methods: {
    toggleMode() {
      this.isRegister = !this.isRegister
      this.errorMessage = ''
      this.successMessage = ''
      // Limpiar form al cambiar modo
      this.form.clave_acceso = ''
      if (!this.isRegister) {
        this.form.nombre_completo = ''
      }
    },

    async handleSubmit() {
      this.isLoading = true
      this.errorMessage = ''
      this.successMessage = ''

      try {
        let response
        
        if (this.isRegister) {
          // Registro - POST /api/auth/register
          response = await api.post('/auth/register', {
            codigo_universitario: this.form.codigo_universitario,
            clave_acceso: this.form.clave_acceso,
            nombre_completo: this.form.nombre_completo
          })
          
          this.successMessage = '¡Cuenta creada exitosamente! Ya puedes iniciar sesión.'
          this.toggleMode() // Cambiar a login después del registro
          
        } else {
          // Login - POST /api/auth/login
          response = await api.post('/auth/login', {
            codigo_universitario: this.form.codigo_universitario,
            clave_acceso: this.form.clave_acceso
          })
          
          // Guardar datos de usuario (sin token por ahora)
          const userData = response.data
          this.handleLoginSuccess(userData)
        }
        
      } catch (error) {
        this.handleError(error)
      } finally {
        this.isLoading = false
      }
    },

    handleLoginSuccess(userData) {
      console.log('Usuario logueado:', userData)
      
      // Guardar usuario en localStorage temporalmente
      localStorage.setItem('user', JSON.stringify(userData))
      
      this.successMessage = `¡Bienvenido ${userData.nombre_completo}!`
      
      // Redirigir después de login exitoso
      setTimeout(() => {
        this.$router.push('/')
      }, 1500)
    },

    handleError(error) {
      console.error('Error en auth:', error)
      
      if (error.response) {
        // El backend respondió con error HTTP
        const { status, data } = error.response
        
        switch (status) {
          case 400:
            this.errorMessage = data.detail || 'Datos inválidos. Verifica tu código universitario y clave.'
            break
          case 401:
            this.errorMessage = 'Código universitario o clave incorrectos'
            break
          case 409:
            this.errorMessage = 'Este código universitario ya está registrado'
            break
          case 422:
            this.errorMessage = 'Error de validación. Verifica los datos ingresados.'
            break
          case 500:
            this.errorMessage = 'Error interno del servidor. Intenta más tarde.'
            break
          default:
            this.errorMessage = data.detail || `Error ${status}: ${data.message || 'Error desconocido'}`
        }
      } else if (error.request) {
        // No se recibió respuesta
        this.errorMessage = 'No se pudo conectar con el servidor. Verifica tu conexión.'
      } else {
        // Error en la configuración
        this.errorMessage = 'Error de conexión: ' + error.message
      }
    }
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

input:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
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

.success-message {
  background: #efe;
  color: #363;
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
  font-weight: 500;
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
  cursor: pointer;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
</style>