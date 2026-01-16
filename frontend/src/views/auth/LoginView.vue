<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Login',
  data() {
    return {
      isRegister: false,
      isLoading: false,
      showPassword: false,
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
        1: '/UserMenu',
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


<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-branding">
        <div class="brand-content">
          <div class="logo">
            <span class="logo-icon">📚</span>
            <h1 class="logo-text">Biblioteca<br>Virtual</h1>
          </div>
          <div class="brand-message">
            <h2>Accede a miles de libros digitales</h2>
            <p>Gestiona tus préstamos, explora el catálogo y disfruta de la lectura</p>
          </div>
        </div>
      </div>

      <div class="login-form-container">
        <div class="form-header">
          <div class="mode-switcher">
            <button
              @click="toggleMode"
              class="mode-btn"
              :class="{ active: !isRegister }"
            >
              Iniciar Sesión
            </button>
            <button
              @click="toggleMode"
              class="mode-btn"
              :class="{ active: isRegister }"
            >
              Registrarse
            </button>
          </div>
        </div>

        <form @submit.prevent="handleSubmit" class="login-form">
          <div class="input-group">
            <label for="codigo_universitario" class="input-label">
              Código Universitario
            </label>
            <input
              id="codigo_universitario"
              v-model="form.codigo_universitario"
              type="text"
              required
              placeholder="U20234567"
              :disabled="isLoading"
              maxlength="20"
              class="input-field"
            >
          </div>

          <div class="input-group">
            <label for="clave_acceso" class="input-label">
              Contraseña
            </label>
            <div class="password-wrapper">
              <input
                id="clave_acceso"
                v-model="form.clave_acceso"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="••••••••"
                :disabled="isLoading"
                minlength="6"
                class="input-field"
              >
              <button
                type="button"
                class="password-toggle"
                @click="showPassword = !showPassword"
              >
                {{ showPassword ? '👁️' : '👁️‍🗨️' }}
              </button>
            </div>
          </div>

          <div v-if="isRegister" class="register-fields">
            <div class="input-group">
              <label for="nombre_completo" class="input-label">
                Nombre Completo
              </label>
              <input
                id="nombre_completo"
                v-model="form.nombre_completo"
                type="text"
                required
                placeholder="Juan Pérez García"
                :disabled="isLoading"
                maxlength="255"
                class="input-field"
              >
            </div>

            <div class="input-group">
              <label for="relacion_institucional_id" class="input-label">
                Relación Institucional
              </label>
              <select
                id="relacion_institucional_id"
                v-model="form.relacion_institucional_id"
                required
                :disabled="isLoading"
                class="select-field"
              >
                <option value="" disabled selected>Selecciona tu perfil</option>
                <option
                  v-for="relacion in relacionesInstitucionales"
                  :key="relacion.id"
                  :value="relacion.id"
                >
                  {{ relacion.nombre }}
                </option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            class="submit-btn"
            :disabled="isLoading || !isFormValid"
          >
            <span v-if="isLoading" class="btn-loading">
              Procesando...
            </span>
            <span v-else>
              {{ isRegister ? 'Crear Cuenta' : 'Ingresar' }}
            </span>
          </button>

          <div v-if="errorMessage" class="message error-message">
            {{ errorMessage }}
          </div>

          <div v-if="successMessage" class="message success-message">
            {{ successMessage }}
          </div>
        </form>

        <div class="form-footer">
          <button @click="$router.push('/')" class="footer-link">
            ← Volver al Inicio
          </button>
        </div>
      </div>
    </div>
  </div>
</template>


<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-wrapper {
  display: flex;
  max-width: 900px;
  width: 100%;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.login-branding {
  flex: 1;
  background: linear-gradient(135deg, #4361ee, #7209b7);
  color: white;
  padding: 40px;
  display: flex;
  align-items: center;
}

.brand-content {
  text-align: center;
}

.logo {
  margin-bottom: 30px;
}

.logo-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 10px;
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
}

.brand-message h2 {
  font-size: 20px;
  margin-bottom: 10px;
  font-weight: 600;
}

.brand-message p {
  font-size: 14px;
  opacity: 0.9;
}

.login-form-container {
  flex: 1;
  padding: 40px;
}

.form-header {
  margin-bottom: 30px;
}

.mode-switcher {
  display: flex;
  background: #f1f3f9;
  border-radius: 8px;
  padding: 4px;
}

.mode-btn {
  flex: 1;
  padding: 12px;
  border: none;
  background: transparent;
  color: #6c757d;
  font-weight: 600;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.mode-btn.active {
  background: white;
  color: #4361ee;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.input-field {
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
  width: 100%;
}

.input-field:focus {
  outline: none;
  border-color: #4361ee;
}

.input-field:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.password-wrapper {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #6c757d;
  padding: 4px;
}

.select-field {
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  width: 100%;
}

.select-field:focus {
  outline: none;
  border-color: #4361ee;
}

.submit-btn {
  padding: 14px;
  background: #4361ee;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 10px;
}

.submit-btn:hover:not(:disabled) {
  background: #3a56d4;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.message {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
}

.error-message {
  background: #fee;
  color: #dc3545;
  border: 1px solid #f5c6cb;
}

.success-message {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.form-footer {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
  text-align: center;
}

.footer-link {
  background: none;
  border: none;
  color: #6c757d;
  font-size: 14px;
  cursor: pointer;
  text-decoration: underline;
  padding: 8px 16px;
}

.footer-link:hover {
  color: #4361ee;
}

@media (max-width: 768px) {
  .login-wrapper {
    flex-direction: column;
  }
  
  .login-branding {
    padding: 30px;
  }
  
  .login-form-container {
    padding: 30px;
  }
}
</style>