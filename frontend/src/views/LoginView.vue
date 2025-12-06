<!-- views/Login.vue -->
<template>
  <div class="login-container">
    <div class="login-card">
      <h1>{{ isRegister ? 'Registrarse' : 'Iniciar Sesión' }}</h1>
      
      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label for="codigo_universitario">Código Universitario *</label>
          <input 
            id="codigo_universitario"
            v-model="form.codigo_universitario"
            type="text" 
            required
            placeholder="Ej: U20234567"
            :disabled="isLoading"
            maxlength="20"
          >
          <small class="input-help">Máximo 20 caracteres</small>
        </div>

        <div class="form-group">
          <label for="clave_acceso">Clave de Acceso *</label>
          <input 
            id="clave_acceso"
            v-model="form.clave_acceso"
            type="password" 
            required
            placeholder="••••••••"
            :disabled="isLoading"
            minlength="6"
          >
          <small class="input-help">Mínimo 6 caracteres</small>
        </div>

        <!-- Campos adicionales para registro -->
        <div v-if="isRegister" class="form-group">
          <label for="nombre_completo">Nombre Completo *</label>
          <input 
            id="nombre_completo"
            v-model="form.nombre_completo"
            type="text" 
            required
            placeholder="Ej: Juan Pérez García"
            :disabled="isLoading"
            maxlength="255"
          >
        </div>

        <div v-if="isRegister" class="form-group">
          <label for="relacion_institucional_id">Relación Institucional *</label>
          <select 
            id="relacion_institucional_id"
            v-model="form.relacion_institucional_id"
            required
            :disabled="isLoading"
            class="select-input"
          >
            <option value="">Selecciona una opción</option>
            <option v-for="relacion in relacionesInstitucionales" 
                    :key="relacion.id" 
                    :value="relacion.id">
              {{ relacion.nombre }}
            </option>
          </select>
          <small class="input-help">Selecciona tu relación con la institución</small>
        </div>

        <button 
          type="submit" 
          class="btn btn-primary btn-full"
          :disabled="isLoading || !isFormValid"
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
        <button @click="$router.push('/healthcheck')" class="btn btn-link">
          🔍 Ver Estado del Sistema
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Login',
  data() {
    return {
      isRegister: false,
      isLoading: false,
      errorMessage: '',
      successMessage: '',
      relacionesInstitucionales: [
        { id: 1, nombre: 'Estudiante' },
        { id: 2, nombre: 'Docente' },
        { id: 3, nombre: 'Administrativo' },
        { id: 4, nombre: 'Investigador' },
        { id: 5, nombre: 'Externo' }
      ],
      form: {
        codigo_universitario: '',
        clave_acceso: '',
        nombre_completo: '',
        relacion_institucional_id: null
      }
    }
  },
  computed: {
    isFormValid() {
      if (this.isRegister) {
        return this.form.codigo_universitario && 
               this.form.clave_acceso && 
               this.form.nombre_completo &&
               this.form.relacion_institucional_id &&
               this.form.clave_acceso.length >= 6
      } else {
        return this.form.codigo_universitario && 
               this.form.clave_acceso
      }
    }
  },
  methods: {
    toggleMode() {
      this.isRegister = !this.isRegister
      this.errorMessage = ''
      this.successMessage = ''
      this.form.clave_acceso = ''
      if (!this.isRegister) {
        this.form.nombre_completo = ''
        this.form.relacion_institucional_id = null
      }
    },

    async handleSubmit() {
      this.isLoading = true
      this.errorMessage = ''
      this.successMessage = ''

      try {
        const authStore = useAuthStore()
        let result
        
        if (this.isRegister) {
          // REGISTRO
          const registerData = {
            codigo_universitario: this.form.codigo_universitario.trim(),
            clave_acceso: this.form.clave_acceso,
            nombre_completo: this.form.nombre_completo.trim(),
            relacion_institucional_id: this.form.relacion_institucional_id
          }
          
          result = await authStore.register(registerData)
          
          if (result.success) {
            this.successMessage = '¡Cuenta creada exitosamente! Ya puedes iniciar sesión.'
            setTimeout(() => {
              this.toggleMode()
            }, 2000)
          } else {
            this.errorMessage = result.error
          }
          
        } else {
          // LOGIN
          const loginData = {
            codigo_universitario: this.form.codigo_universitario.trim(),
            clave_acceso: this.form.clave_acceso
          }
          
          result = await authStore.login(loginData)
          
          if (result.success) {
            this.successMessage = `¡Bienvenido ${authStore.userName}!`
            
            // Redirigir basado en el tipo de usuario
            setTimeout(() => {
              this.redirectBasedOnUserType(authStore.userRole)
            }, 1500)
            
          } else {
            this.errorMessage = result.error
          }
        }
        
      } catch (error) {
        console.error('Error inesperado:', error)
        this.errorMessage = 'Error inesperado. Intenta nuevamente.'
      } finally {
        this.isLoading = false
      }
    },

    redirectBasedOnUserType(tipoUsuarioId) {
      const routes = {
        1: '/dashboard',
        2: '/admin/dashboard',
        3: '/admin/advanced',
        4: '/admin/super'
      }
      
      const route = routes[tipoUsuarioId] || '/'
      this.$router.push(route)
    }
  }
}
</script>

<style scoped>
/* Tus estilos aquí (se mantienen igual) */
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

/* ... resto de estilos ... */
</style>