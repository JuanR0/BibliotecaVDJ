<!-- views/Register.vue -->
<template>
  <div class="register-container">
    <div class="register-card">
      <!-- Header -->
      <div class="register-header">
        <h1>📝 Registro de Usuario</h1>
        <p>Crea tu cuenta en la Biblioteca VDJ</p>
      </div>

      <!-- Formulario de Registro -->
      <form @submit.prevent="handleRegister" class="register-form">
        <!-- Información Personal -->
        <div class="form-section">
          <h3>👤 Información Personal</h3>
          
          <div class="form-group">
            <label for="nombre_completo">Nombre Completo *</label>
            <input 
              id="nombre_completo"
              v-model="form.nombre_completo"
              type="text" 
              required
              placeholder="Ej: María González López"
              :disabled="isLoading"
              maxlength="255"
              @input="validateName"
            >
            <small class="input-help">Nombre completo tal como aparece en documentos oficiales</small>
            <span v-if="nameError" class="error-text">{{ nameError }}</span>
          </div>

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
              @input="validateCode"
            >
            <small class="input-help">Máximo 20 caracteres</small>
            <span v-if="codeError" class="error-text">{{ codeError }}</span>
          </div>
        </div>

        <!-- Información Institucional -->
        <div class="form-section">
          <h3>🏫 Información Institucional</h3>
          
          <div class="form-group">
            <label for="relacion_institucional_id">Relación con la Institución *</label>
            <select 
              id="relacion_institucional_id"
              v-model="form.relacion_institucional_id"
              required
              :disabled="isLoading"
              class="select-input"
              @change="validateRelacion"
            >
              <option value="">Selecciona tu relación</option>
              <option v-for="relacion in relacionesInstitucionales" 
                      :key="relacion.id" 
                      :value="relacion.id">
                {{ relacion.nombre }}
              </option>
            </select>
            <small class="input-help">Selecciona tu relación actual con la universidad</small>
            <span v-if="relacionError" class="error-text">{{ relacionError }}</span>
          </div>
        </div>

        <!-- Seguridad -->
        <div class="form-section">
          <h3>🔒 Seguridad</h3>
          
          <div class="form-group">
            <label for="clave_acceso">Contraseña *</label>
            <div class="password-input-container">
              <input 
                id="clave_acceso"
                v-model="form.clave_acceso"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="••••••••"
                :disabled="isLoading"
                minlength="6"
                @input="validatePassword"
              >
              <button 
                type="button" 
                class="password-toggle"
                @click="showPassword = !showPassword"
                :disabled="isLoading"
              >
                {{ showPassword ? '👁️' : '👁️‍🗨️' }}
              </button>
            </div>
            <small class="input-help">Mínimo 6 caracteres</small>
            <div class="password-strength" :class="passwordStrength">
              Seguridad: {{ passwordStrengthText }}
            </div>
            <span v-if="passwordError" class="error-text">{{ passwordError }}</span>
          </div>

          <div class="form-group">
            <label for="confirmar_clave">Confirmar Contraseña *</label>
            <div class="password-input-container">
              <input 
                id="confirmar_clave"
                v-model="confirmarClave"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                placeholder="••••••••"
                :disabled="isLoading"
                @input="validatePasswordMatch"
              >
              <button 
                type="button" 
                class="password-toggle"
                @click="showConfirmPassword = !showConfirmPassword"
                :disabled="isLoading"
              >
                {{ showConfirmPassword ? '👁️' : '👁️‍🗨️' }}
              </button>
            </div>
            <small class="input-help">Repite tu contraseña para confirmar</small>
            <span v-if="passwordMatchError" class="error-text">{{ passwordMatchError }}</span>
          </div>
        </div>

        <!-- Términos y Condiciones -->
        <div class="form-section">
          <div class="checkbox-group">
            <input 
              id="accept_terms"
              v-model="acceptTerms"
              type="checkbox"
              required
              :disabled="isLoading"
            >
            <label for="accept_terms">
              Acepto los <a href="#" @click.prevent="showTerms = true">términos y condiciones</a> 
              y la <a href="#" @click.prevent="showPrivacy = true">política de privacidad</a>
            </label>
            <span v-if="termsError" class="error-text">{{ termsError }}</span>
          </div>
        </div>

        <!-- Botón de Registro -->
        <button 
          type="submit" 
          class="btn btn-primary btn-full"
          :disabled="isLoading || !isFormValid"
        >
          <span v-if="isLoading">
            <span class="spinner"></span> Creando cuenta...
          </span>
          <span v-else>🎉 Crear Mi Cuenta</span>
        </button>

        <!-- Mensajes de Estado -->
        <div v-if="errorMessage" class="error-message">
          <h4>❌ Error en el Registro</h4>
          <p>{{ errorMessage }}</p>
          <div v-if="validationErrors.length > 0" class="validation-errors">
            <ul>
              <li v-for="error in validationErrors" :key="error">{{ error }}</li>
            </ul>
          </div>
        </div>

        <div v-if="successMessage" class="success-message">
          <h4>✅ ¡Registro Exitoso!</h4>
          <p>{{ successMessage }}</p>
        </div>
      </form>

      <!-- Enlaces de Navegación -->
      <div class="register-footer">
        <p>¿Ya tienes una cuenta? 
          <router-link to="/login" class="link">Inicia sesión aquí</router-link>
        </p>
        <router-link to="/" class="btn btn-link">
          ← Volver al Inicio
        </router-link>
      </div>
    </div>

    <!-- Modal de Términos y Condiciones -->
    <div v-if="showTerms" class="modal-overlay" @click="showTerms = false">
      <div class="modal-content" @click.stop>
        <h3>📄 Términos y Condiciones</h3>
        <div class="modal-body">
          <p>Al registrarte en la Biblioteca VDJ, aceptas:</p>
          <ul>
            <li>Utilizar el sistema únicamente para fines académicos</li>
            <li>Respetar los derechos de autor y propiedad intelectual</li>
            <li>Mantener la confidencialidad de tus credenciales</li>
            <li>No realizar actividades fraudulentas o malintencionadas</li>
            <li>Cumplir con el reglamento interno de la biblioteca</li>
          </ul>
          <p>El incumplimiento de estos términos puede resultar en la suspensión de tu cuenta.</p>
        </div>
        <button @click="showTerms = false" class="btn btn-primary">Entendido</button>
      </div>
    </div>

    <!-- Modal de Política de Privacidad -->
    <div v-if="showPrivacy" class="modal-overlay" @click="showPrivacy = false">
      <div class="modal-content" @click.stop>
        <h3>🔒 Política de Privacidad</h3>
        <div class="modal-body">
          <p>En Biblioteca VDJ protegemos tu información personal:</p>
          <ul>
            <li>Tus datos personales se utilizan únicamente para gestionar servicios de biblioteca</li>
            <li>No compartimos tu información con terceros sin tu consentimiento</li>
            <li>Implementamos medidas de seguridad para proteger tus datos</li>
            <li>Puedes solicitar la eliminación de tu cuenta en cualquier momento</li>
            <li>Cumplimos con la legislación de protección de datos aplicable</li>
          </ul>
        </div>
        <button @click="showPrivacy = false" class="btn btn-primary">Entendido</button>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '@/services/api'

export default {
  name: 'Register',
  data() {
    return {
      isLoading: false,
      errorMessage: '',
      successMessage: '',
      validationErrors: [],
      showPassword: false,
      showConfirmPassword: false,
      showTerms: false,
      showPrivacy: false,
      acceptTerms: false,
      
      // Errores de validación
      nameError: '',
      codeError: '',
      relacionError: '',
      passwordError: '',
      passwordMatchError: '',
      termsError: '',
      
      // Confirmación de contraseña
      confirmarClave: '',
      
      // Relaciones institucionales
      relacionesInstitucionales: [
        { id: 1, nombre: '🎓 Estudiante' },
        { id: 2, nombre: '👨‍🏫 Docente' },
        { id: 3, nombre: '💼 Administrativo' },
        { id: 4, nombre: '🔬 Investigador' },
        { id: 5, nombre: '🌐 Usuario Externo' }
      ],
      
      // Formulario
      form: {
        nombre_completo: '',
        codigo_universitario: '',
        clave_acceso: '',
        relacion_institucional_id: null
      }
    }
  },
  computed: {
    isFormValid() {
      return this.form.nombre_completo &&
             this.form.codigo_universitario &&
             this.form.clave_acceso &&
             this.form.relacion_institucional_id &&
             this.confirmarClave &&
             this.acceptTerms &&
             this.form.clave_acceso.length >= 6 &&
             this.form.clave_acceso === this.confirmarClave &&
             !this.nameError &&
             !this.codeError &&
             !this.relacionError &&
             !this.passwordError &&
             !this.passwordMatchError &&
             !this.termsError
    },
    
    passwordStrength() {
      const password = this.form.clave_acceso
      if (password.length === 0) return 'empty'
      if (password.length < 6) return 'weak'
      if (password.length < 8) return 'medium'
      if (/[A-Z]/.test(password) && /[0-9]/.test(password)) return 'strong'
      return 'medium'
    },
    
    passwordStrengthText() {
      const strengths = {
        'empty': 'No establecida',
        'weak': 'Débil',
        'medium': 'Media', 
        'strong': 'Fuerte'
      }
      return strengths[this.passwordStrength]
    }
  },
  methods: {
    validateName() {
      const name = this.form.nombre_completo.trim()
      if (!name) {
        this.nameError = 'El nombre completo es requerido'
      } else if (name.length < 2) {
        this.nameError = 'El nombre debe tener al menos 2 caracteres'
      } else if (name.length > 255) {
        this.nameError = 'El nombre no puede exceder 255 caracteres'
      } else {
        this.nameError = ''
      }
    },
    
    validateCode() {
      const code = this.form.codigo_universitario.trim()
      if (!code) {
        this.codeError = 'El código universitario es requerido'
      } else if (code.length > 20) {
        this.codeError = 'Máximo 20 caracteres permitidos'
      } else {
        this.codeError = ''
      }
    },
    
    validateRelacion() {
      if (!this.form.relacion_institucional_id) {
        this.relacionError = 'Debes seleccionar una relación institucional'
      } else {
        this.relacionError = ''
      }
    },
    
    validatePassword() {
      const password = this.form.clave_acceso
      
      if (!password) {
        this.passwordError = 'La contraseña es requerida'
      } else if (password.length < 6) {
        this.passwordError = 'La contraseña debe tener al menos 6 caracteres'
      } else if (password.length > 72) {
        // Límite de bcrypt
        this.passwordError = 'La contraseña no puede exceder 72 caracteres'
      } else {
        this.passwordError = ''
      }
      
      // Validar coincidencia si ya hay confirmación
      if (this.confirmarClave) {
        this.validatePasswordMatch()
      }
    },
    
    validatePasswordMatch() {
      if (this.confirmarClave && this.form.clave_acceso !== this.confirmarClave) {
        this.passwordMatchError = 'Las contraseñas no coinciden'
      } else {
        this.passwordMatchError = ''
      }
    },
    
    async handleRegister() {
      // Resetear mensajes
      this.isLoading = true
      this.errorMessage = ''
      this.successMessage = ''
      this.validationErrors = []
      
      // Validar todos los campos
      this.validateName()
      this.validateCode()
      this.validateRelacion()
      this.validatePassword()
      this.validatePasswordMatch()
      
      if (!this.acceptTerms) {
        this.termsError = 'Debes aceptar los términos y condiciones'
      } else {
        this.termsError = ''
      }
      
      // Si hay errores de validación, detener
      if (this.nameError || this.codeError || this.relacionError || 
          this.passwordError || this.passwordMatchError || this.termsError) {
        this.isLoading = false
        this.errorMessage = 'Por favor, corrige los errores en el formulario'
        return
      }
      
      try {
        console.log('📝 Enviando datos de registro...')
        
        // Preparar datos para enviar
        const registerData = {
          codigo_universitario: this.form.codigo_universitario.trim(),
          clave_acceso: this.form.clave_acceso,
          nombre_completo: this.form.nombre_completo.trim(),
          relacion_institucional_id: this.form.relacion_institucional_id
        }
        
        console.log('📤 Datos a enviar:', registerData)
        
        // Hacer la petición POST al endpoint de registro
        const response = await api.post('/auth/register', registerData)
        
        console.log('✅ Respuesta del servidor:', response.data)
        
        // Éxito
        this.successMessage = `¡Cuenta creada exitosamente! 
        Tu código universitario es: ${registerData.codigo_universitario}
        Serás redirigido al login en 5 segundos...`
        
        // Limpiar formulario
        this.form = {
          nombre_completo: '',
          codigo_universitario: '',
          clave_acceso: '',
          relacion_institucional_id: null
        }
        this.confirmarClave = ''
        this.acceptTerms = false
        
        // Redirigir al login después de 5 segundos
        setTimeout(() => {
          this.$router.push('/login')
        }, 5000)
        
      } catch (error) {
        console.error('❌ Error en registro:', error)
        
        // Manejar diferentes tipos de errores
        if (error.response) {
          const { status, data } = error.response
          
          console.log('📋 Detalles del error:', data)
          
          switch (status) {
            case 400:
              this.errorMessage = data.detail || 'Datos inválidos enviados al servidor'
              break
            case 409:
              this.errorMessage = 'Este código universitario ya está registrado'
              break
            case 422:
              // Error de validación del backend
              this.errorMessage = 'Errores de validación:'
              if (data.detail && Array.isArray(data.detail)) {
                this.validationErrors = data.detail.map(err => {
                  const field = err.loc?.join('.') || 'campo'
                  const msg = err.msg || 'Error de validación'
                  return `${field}: ${msg}`
                })
              } else if (data.detail) {
                this.validationErrors = [data.detail]
              }
              break
            case 500:
              this.errorMessage = 'Error interno del servidor. Por favor, intenta más tarde.'
              break
            default:
              this.errorMessage = `Error ${status}: ${data.detail || 'Error desconocido'}`
          }
        } else if (error.request) {
          // No se recibió respuesta
          this.errorMessage = 'No se pudo conectar con el servidor. Verifica tu conexión a internet.'
        } else {
          // Error en la configuración
          this.errorMessage = `Error de configuración: ${error.message}`
        }
      } finally {
        this.isLoading = false
      }
    }
  },
  mounted() {
    // Limpiar cualquier estado previo al cargar la vista
    console.log('🔄 Vista de registro cargada')
  }
}
</script>

<style scoped>
/* Tus estilos anteriores se mantienen, agrego solo los nuevos */
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 1rem;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.register-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 500px;
}

/* ... (mantén todos tus estilos anteriores) ... */

.error-message {
  background: #fee;
  color: #721c24;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
  border-left: 4px solid #dc3545;
}

.error-message h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.validation-errors {
  margin-top: 0.5rem;
  padding-left: 1.5rem;
}

.validation-errors ul {
  margin: 0.5rem 0;
}

.validation-errors li {
  margin: 0.25rem 0;
  font-size: 0.9rem;
}

.success-message {
  background: #d1edff;
  color: #155724;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
  border-left: 4px solid #28a745;
}

.success-message h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.success-message p {
  margin: 0;
  white-space: pre-line;
}

/* Spinner para loading */
.spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>