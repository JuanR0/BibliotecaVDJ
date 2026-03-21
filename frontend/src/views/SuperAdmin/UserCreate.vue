<template>
  <div class="user-create">
    <!-- Header -->
    <div class="create-header">
      <div class="header-content">
        <h1>👤 Crear Nuevo Usuario</h1>
        <p class="subtitle">Registra un nuevo usuario en el sistema bibliotecario</p>
        
        <div class="breadcrumb">
          <router-link to="/admin/usuarios" class="breadcrumb-link">
            ← Volver a Gestión de Usuarios
          </router-link>
        </div>
      </div>
    </div>

    <!-- Formulario principal -->
    <div class="form-container">
      <form @submit.prevent="submitForm" class="user-form">
        <!-- Información básica -->
        <div class="form-section">
          <h3 class="section-title">📝 Información Básica</h3>
          
          <div class="form-row">
            <div class="form-group">
              <label for="codigo_universitario" class="required">
                Código Universitario
              </label>
              <input
                id="codigo_universitario"
                v-model="form.codigo_universitario"
                type="text"
                placeholder="Ej: 215686936"
                :class="{ 'error': errors.codigo_universitario }"
                @blur="validateField('codigo_universitario')"
              />
              <div v-if="errors.codigo_universitario" class="error-message">
                {{ errors.codigo_universitario }}
              </div>
              <div class="form-hint">
                Identificador único del usuario en el sistema
              </div>
            </div>
            
            <div class="form-group">
              <label for="nombre_completo" class="required">
                Nombre Completo
              </label>
              <input
                id="nombre_completo"
                v-model="form.nombre_completo"
                type="text"
                placeholder="Ej: Juan Pérez González"
                :class="{ 'error': errors.nombre_completo }"
                @blur="validateField('nombre_completo')"
              />
              <div v-if="errors.nombre_completo" class="error-message">
                {{ errors.nombre_completo }}
              </div>
            </div>
          </div>
        </div>

        <!-- Credenciales -->
        <div class="form-section">
          <h3 class="section-title">🔐 Credenciales de Acceso</h3>
          
          <div class="form-row">
            <div class="form-group">
              <label for="clave_acceso" class="required">
                Contraseña
              </label>
              <div class="password-input">
                <input
                  id="clave_acceso"
                  v-model="form.clave_acceso"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Mínimo 6 caracteres"
                  :class="{ 'error': errors.clave_acceso }"
                  @blur="validateField('clave_acceso')"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showPassword = !showPassword"
                >
                  {{ showPassword ? '🙈' : '👁️' }}
                </button>
              </div>
              <div v-if="errors.clave_acceso" class="error-message">
                {{ errors.clave_acceso }}
              </div>
            </div>
            
            <div class="form-group">
              <label for="confirmar_clave" class="required">
                Confirmar Contraseña
              </label>
              <div class="password-input">
                <input
                  id="confirmar_clave"
                  v-model="form.confirmar_clave"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="Repite la contraseña"
                  :class="{ 'error': errors.confirmar_clave }"
                  @blur="validatePasswordMatch"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  {{ showConfirmPassword ? '🙈' : '👁️' }}
                </button>
              </div>
              <div v-if="errors.confirmar_clave" class="error-message">
                {{ errors.confirmar_clave }}
              </div>
            </div>
          </div>
          
          <div class="password-strength" v-if="form.clave_acceso">
            <div class="strength-label">Seguridad de la contraseña:</div>
            <div class="strength-bar" :class="passwordStrength.class">
              <div class="strength-fill" :style="{ width: passwordStrength.percentage + '%' }"></div>
            </div>
            <div class="strength-text">{{ passwordStrength.text }}</div>
          </div>
        </div>

        <!-- Configuración del usuario -->
        <div class="form-section">
          <h3 class="section-title">⚙️ Configuración del Usuario</h3>
          
          <div class="form-row">
            <div class="form-group">
              <label for="tipo_usuario_id" class="required">
                Tipo de Usuario
              </label>
              <select
                id="tipo_usuario_id"
                v-model="form.tipo_usuario_id"
                :class="{ 'error': errors.tipo_usuario_id }"
              >
                <option value="" disabled>Selecciona un tipo</option>
                <option
                  v-for="type in userTypes.filter(t => t.id !== 4)"
                  :key="type.id"
                  :value="type.id"
                >
                  {{ type.nombre }} - {{ type.descripcion }}
                </option>
              </select>
              <div v-if="errors.tipo_usuario_id" class="error-message">
                {{ errors.tipo_usuario_id }}
              </div>
            </div>
            
            <div class="form-group">
              <label for="relacion_institucional_id" class="required">
                Relación Institucional
              </label>
              <select
                id="relacion_institucional_id"
                v-model="form.relacion_institucional_id"
                :class="{ 'error': errors.relacion_institucional_id }"
              >
                <option value="" disabled>Selecciona una relación</option>
                <option
                  v-for="rel in institutionalRelations"
                  :key="rel.id"
                  :value="rel.id"
                >
                  {{ rel.nombre }}
                </option>
              </select>
              <div v-if="errors.relacion_institucional_id" class="error-message">
                {{ errors.relacion_institucional_id }}
              </div>
            </div>
          </div>
          
          <!-- Estado inicial (siempre activo para nuevos) -->
          <div class="form-group">
            <label>Estado Inicial</label>
            <div class="status-display">
              <span class="status-badge active">✅ Activo</span>
              <div class="form-hint">
                Los nuevos usuarios se crean en estado activo por defecto
              </div>
            </div>
          </div>
        </div>

        <!-- Resumen del usuario -->
        <div class="form-section preview-section">
          <h3 class="section-title">👁️ Vista Previa</h3>
          <div class="user-preview">
            <div class="preview-header">
              <div class="preview-avatar">👤</div>
              <div class="preview-info">
                <div class="preview-name">{{ form.nombre_completo || 'Nombre del usuario' }}</div>
                <div class="preview-code">{{ form.codigo_universitario || 'Código universitario' }}</div>
              </div>
            </div>
            <div class="preview-details">
              <div class="preview-item">
                <span class="preview-label">Tipo:</span>
                <span class="preview-value" v-if="form.tipo_usuario_id">
                  {{ getTipoNombre(form.tipo_usuario_id) }}
                </span>
                <span class="preview-placeholder" v-else>No seleccionado</span>
              </div>
              <div class="preview-item">
                <span class="preview-label">Relación:</span>
                <span class="preview-value" v-if="form.relacion_institucional_id">
                  {{ getRelacionNombre(form.relacion_institucional_id) }}
                </span>
                <span class="preview-placeholder" v-else>No seleccionado</span>
              </div>
              <div class="preview-item">
                <span class="preview-label">Estado:</span>
                <span class="preview-value">
                  <span class="status-badge active">✅ Activo</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Acciones del formulario -->
        <div class="form-actions">
          <button type="button" @click="cancel" class="btn btn-secondary" :disabled="isSubmitting"> Cancelar</button>
          
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting || !isFormValid">
            <span v-if="isSubmitting" class="spinner-small"></span>
            {{ isSubmitting ? 'Creando Usuario...' : 'Crear Usuario' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Toast de éxito -->
    <div v-if="showSuccessToast" class="toast success">
      <div class="toast-icon">✅</div>
      <div class="toast-content">
        <strong>¡Usuario creado exitosamente!</strong>
        <p>El usuario {{ createdUserName }} ha sido registrado en el sistema.</p>
      </div>
      <button @click="showSuccessToast = false" class="toast-close">×</button>
    </div>

    <!-- Modal de error -->
    <div v-if="showErrorModal" class="modal-overlay">
      <div class="modal-content error-modal">
        <div class="modal-header">
          <h3>❌ Error al crear usuario</h3>
          <button @click="closeErrorModal" class="modal-close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <p>{{ errorMessage }}</p>
          <div v-if="errorDetails" class="error-details">
            <pre>{{ errorDetails }}</pre>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeErrorModal" class="btn btn-primary">
            Entendido
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userService } from '@/services/users'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Verificar permisos - solo tipo 4 puede acceder
if (authStore.tipoUsuarioId !== 4) {
  router.push('/')
}

// State
const form = ref({
  codigo_universitario: '',
  nombre_completo: '',
  clave_acceso: '',
  confirmar_clave: '',
  tipo_usuario_id: 1, // Por defecto usuario común
  relacion_institucional_id: 1, // Por defecto estudiante
  esta_activo: true
})

const errors = ref({})
const isSubmitting = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const showSuccessToast = ref(false)
const showErrorModal = ref(false)
const errorMessage = ref('')
const errorDetails = ref('')
const createdUserName = ref('')

// Computed
const userTypes = computed(() => userService.getUserTypes())
const institutionalRelations = computed(() => userService.getInstitutionalRelations())

const isFormValid = computed(() => {
  return (
    form.value.codigo_universitario.trim() &&
    form.value.nombre_completo.trim() &&
    form.value.clave_acceso &&
    form.value.confirmar_clave &&
    form.value.tipo_usuario_id &&
    form.value.relacion_institucional_id &&
    !Object.values(errors.value).some(error => error)
  )
})

const passwordStrength = computed(() => {
  const password = form.value.clave_acceso
  if (!password) return { class: 'weak', text: 'Ingresa una contraseña', percentage: 0 }
  
  let score = 0
  if (password.length >= 6) score += 25
  if (password.length >= 8) score += 25
  if (/[A-Z]/.test(password)) score += 25
  if (/[0-9]/.test(password)) score += 25
  
  if (score >= 75) return { class: 'strong', text: 'Fuerte', percentage: 100 }
  if (score >= 50) return { class: 'medium', text: 'Media', percentage: 66 }
  if (score >= 25) return { class: 'weak', text: 'Débil', percentage: 33 }
  return { class: 'very-weak', text: 'Muy débil', percentage: 0 }
})

// Métodos
const getTipoNombre = (tipoId) => {
  const tipo = userTypes.value.find(t => t.id === tipoId)
  return tipo ? tipo.nombre : 'Desconocido'
}

const getRelacionNombre = (relacionId) => {
  const rel = institutionalRelations.value.find(r => r.id === relacionId)
  return rel ? rel.nombre : 'Desconocida'
}

const validateField = (fieldName) => {
  const value = form.value[fieldName]
  errors.value[fieldName] = ''
  
  switch (fieldName) {
    case 'codigo_universitario':
      if (!value.trim()) {
        errors.value[fieldName] = 'El código universitario es requerido'
      } else if (value.trim().length < 3) {
        errors.value[fieldName] = 'El código debe tener al menos 3 caracteres'
      }
      break
      
    case 'nombre_completo':
      if (!value.trim()) {
        errors.value[fieldName] = 'El nombre completo es requerido'
      } else if (value.trim().length < 3) {
        errors.value[fieldName] = 'El nombre debe tener al menos 3 caracteres'
      }
      break
      
    case 'clave_acceso':
      if (!value) {
        errors.value[fieldName] = 'La contraseña es requerida'
      } else if (value.length < 6) {
        errors.value[fieldName] = 'La contraseña debe tener al menos 6 caracteres'
      }
      break
      
    case 'confirmar_clave':
      validatePasswordMatch()
      break
      
    case 'tipo_usuario_id':
      if (!value) {
        errors.value[fieldName] = 'El tipo de usuario es requerido'
      } else if (value === 4) {
        errors.value[fieldName] = 'No se puede crear usuarios Super Admin desde aquí'
      }
      break
      
    case 'relacion_institucional_id':
      if (!value) {
        errors.value[fieldName] = 'La relación institucional es requerida'
      }
      break
  }
}

const validatePasswordMatch = () => {
  if (form.value.clave_acceso !== form.value.confirmar_clave) {
    errors.value.confirmar_clave = 'Las contraseñas no coinciden'
  } else {
    errors.value.confirmar_clave = ''
  }
}

const validateForm = () => {
  // Validar todos los campos
  Object.keys(form.value).forEach(field => {
    if (field !== 'esta_activo') { // No validar estado
      validateField(field)
    }
  })
  
  // Retornar si hay errores
  return !Object.values(errors.value).some(error => error)
}

const submitForm = async () => {
  // Validar formulario
  if (!validateForm()) {
    alert('Por favor corrige los errores en el formulario')
    return
  }
  
  isSubmitting.value = true
  
  try {
    // Preparar datos para enviar (excluir confirmar_clave)
    const userData = {
      codigo_universitario: form.value.codigo_universitario.trim(),
      nombre_completo: form.value.nombre_completo.trim(),
      clave_acceso: form.value.clave_acceso,
      tipo_usuario_id: form.value.tipo_usuario_id,
      relacion_institucional_id: form.value.relacion_institucional_id,
      esta_activo: true // Siempre activo al crear
    }
    
    console.log('📤 Enviando datos:', userData)
    
    // Crear usuario
    const response = await userService.createUser(userData)
    console.log('✅ Usuario creado:', response)
    
    // Guardar nombre para el toast
    createdUserName.value = userData.nombre_completo
    
    // Mostrar toast de éxito
    showSuccessToast.value = true
    
    // Redirigir después de 2 segundos
    setTimeout(() => {
      router.push('/SuperAdmin/usuarios/')
    }, 2000)
    
  } catch (error) {
    console.error('❌ Error creando usuario:', error)
    
    // Manejar errores específicos
    if (error.message.includes('ya existe') || error.message.includes('duplicado')) {
      errorMessage.value = 'El código universitario ya está registrado'
      errorDetails.value = 'Por favor, utiliza un código diferente'
    } else if (error.message.includes('No autorizado') || error.message.includes('403')) {
      errorMessage.value = 'No tienes permisos para crear usuarios'
      errorDetails.value = 'Solo los Super Admins pueden crear usuarios'
    } else {
      errorMessage.value = error.message || 'Error desconocido al crear el usuario'
      errorDetails.value = error.toString()
    }
    
    showErrorModal.value = true
    
  } finally {
    isSubmitting.value = false
  }
}

const cancel = () => {
  if (confirm('¿Estás seguro de que deseas cancelar? Los datos no guardados se perderán.')) {
    router.push('/SuperAdmin/usuarios/')
  }
}

const closeErrorModal = () => {
  showErrorModal.value = false
  errorMessage.value = ''
  errorDetails.value = ''
}

// Ciclo de vida
onMounted(() => {
  console.log('UserCreate.vue montado')
  console.log('Usuario actual:', authStore.userName)
  console.log('Tipo usuario:', authStore.tipoUsuarioId)
})
</script>

<style scoped>
.user-create {
  padding: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
}

/* Header */
.create-header {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 12px;
  color: white;
}

.create-header h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 1rem;
}

.breadcrumb {
  margin-top: 1rem;
}

.breadcrumb-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: white;
  text-decoration: underline;
}

/* Formulario */
.form-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid #f1f5f9;
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-title {
  font-size: 1.25rem;
  color: #334155;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #475569;
}

.form-group label.required::after {
  content: ' *';
  color: #ef4444;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-group input.error,
.form-group select.error {
  border-color: #ef4444;
}

.password-input {
  position: relative;
}

.password-input input {
  padding-right: 3rem;
}

.password-toggle {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  color: #64748b;
}

.password-toggle:hover {
  background: #f1f5f9;
  color: #334155;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.form-hint {
  color: #64748b;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

/* Password strength */
.password-strength {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.5rem;
}

.strength-label {
  font-weight: 500;
  color: #475569;
  margin-bottom: 0.5rem;
}

.strength-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.strength-fill {
  height: 100%;
  background: #10b981;
  transition: width 0.3s;
}

.strength-bar.weak .strength-fill {
  background: #ef4444;
}

.strength-bar.medium .strength-fill {
  background: #f59e0b;
}

.strength-bar.strong .strength-fill {
  background: #10b981;
}

.strength-text {
  font-size: 0.875rem;
  color: #64748b;
  text-align: right;
}

/* Vista previa */
.preview-section {
  background: #f8fafc;
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.user-preview {
  background: white;
  border-radius: 0.5rem;
  border: 2px solid #e2e8f0;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: #f1f5f9;
}

.preview-avatar {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  background: #10b981;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-info {
  flex: 1;
}

.preview-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.preview-code {
  font-family: 'Courier New', monospace;
  color: #64748b;
}

.preview-details {
  padding: 1.5rem;
}

.preview-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.preview-label {
  font-weight: 500;
  color: #475569;
  width: 100px;
  flex-shrink: 0;
}

.preview-value {
  color: #1e293b;
}

.preview-placeholder {
  color: #94a3b8;
  font-style: italic;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

/* Acciones */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #f1f5f9;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #10b981;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
}

.spinner-small {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Toast */
.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  max-width: 350px;
  z-index: 3000;
  animation: toastSlideIn 0.3s ease-out;
  border-left: 4px solid #10b981;
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.toast-icon {
  font-size: 1.8rem;
}

.toast-content {
  flex: 1;
}

.toast-content strong {
  display: block;
  margin-bottom: 0.25rem;
  color: #1e293b;
}

.toast-content p {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
}

.toast-close {
  background: none;
  border: none;
  color: #64748b;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-close:hover {
  background: #f1f5f9;
}

/* Modal de error */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-modal {
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  color: #1e293b;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close-btn:hover {
  background: #f1f5f9;
}

.modal-body {
  padding: 1.5rem;
}

.modal-body p {
  margin: 0 0 1rem;
  color: #475569;
}

.error-details {
  margin-top: 1rem;
  padding: 1rem;
  background: #fef2f2;
  border-radius: 0.5rem;
  border-left: 4px solid #ef4444;
}

.error-details pre {
  margin: 0;
  font-size: 0.875rem;
  color: #b91c1c;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
}
</style>