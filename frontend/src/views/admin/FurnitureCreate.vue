<template>
  <div class="mobiliario-create-view">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>➕ Agregar Nuevo Mobiliario</h1>
        <p class="subtitle">Registra nuevo mobiliario en el inventario de la biblioteca</p>
      </div>
      
      <div class="header-actions">
        <router-link to="/admin/mobiliario" class="btn btn-outline">
          ← Volver al Inventario
        </router-link>
      </div>
    </div>

    <!-- Formulario -->
    <div class="form-container">
      <div class="form-card">
        <!-- Estado de carga -->
        <div v-if="isLoadingCatalogos" class="loading-catalogos">
          <div class="spinner"></div>
          <p>Cargando catálogos...</p>
        </div>

        <!-- Error general -->
        <div v-if="error" class="alert alert-danger">
          <strong>❌ Error:</strong> {{ error }}
          <button @click="loadCatalogos" class="btn btn-sm btn-outline-danger ms-2">
            Reintentar
          </button>
        </div>

        <!-- Formulario principal -->
        <form @submit.prevent="submitForm" v-if="!isLoadingCatalogos && !error">
          <div class="form-grid">
            <!-- Descripción -->
            <div class="form-group full-width">
              <label for="descripcion" class="form-label required">
                📝 Descripción del Mobiliario
              </label>
              <textarea
                id="descripcion"
                v-model="formData.descripcion"
                class="form-control"
                rows="3"
                placeholder="Ej: Mesa de lectura rectangular, 4 sillas ergonómicas, estantería metálica..."
                required
                :maxlength="255"
                :disabled="isSubmitting"
              ></textarea>
              <div class="form-text">
                Describe claramente el mobiliario. Máximo 255 caracteres.
                <span class="char-counter">{{ formData.descripcion?.length || 0 }}/255</span>
              </div>
              <div v-if="validationErrors.descripcion" class="invalid-feedback">
                {{ validationErrors.descripcion }}
              </div>
            </div>

            <!-- Tipo de Mobiliario -->
            <div class="form-group">
              <label for="tipo_mobiliario_id" class="form-label required">Tipo de Mobiliario</label>
              <select id="tipo_mobiliario_id" v-model="formData.tipo_mobiliario_id" class="form-select" required:disabled="isSubmitting || tiposMobiliario.length === 0">
                <option value="" disabled selected>Selecciona un tipo</option>
                <option v-for="tipo in tiposMobiliario" :key="tipo.id" :value="tipo.id">{{ tipo.nombre }}</option>
              </select>
              <div v-if="tiposMobiliario.length === 0" class="form-text text-warning">
                No hay tipos de mobiliario disponibles. Contacta al administrador.
              </div>
              <div v-if="validationErrors.tipo_mobiliario_id" class="invalid-feedback">
                {{ validationErrors.tipo_mobiliario_id }}
              </div>
            </div>

            <!-- Estado -->
            <div class="form-group">
              <label for="estado_id" class="form-label required">
                📋 Estado
              </label>
              <select
                id="estado_id"
                v-model="formData.estado_id"
                class="form-select"
                required
                :disabled="isSubmitting || estadosMobiliario.length === 0"
              >
                <option value="" disabled selected>Selecciona un estado</option>
                <option 
                  v-for="estado in estadosMobiliario" 
                  :key="estado.id" 
                  :value="estado.id"
                >
                  {{ estado.nombre }}
                </option>
              </select>
              <div class="form-text">
                Estado inicial del mobiliario. Generalmente "Activo".
              </div>
              <div v-if="validationErrors.estado_id" class="invalid-feedback">
                {{ validationErrors.estado_id }}
              </div>
            </div>

            <!-- Área -->
            <div class="form-group">
              <label for="area_id" class="form-label">
                📍 Área / Ubicación
              </label>
              <select
                id="area_id"
                v-model="formData.area_id"
                class="form-select"
                :disabled="isSubmitting"
                v-if="areas.length > 0"
              >
                <option value="" selected>Sin área asignada</option>
                <option 
                  v-for="area in areas" 
                  :key="area.id" 
                  :value="area.id"
                >
                  {{ area.nombre }}
                </option>
              </select>
              <input
                v-else
                id="area_id"
                v-model.number="formData.area_id"
                type="number"
                class="form-control"
                placeholder="ID del área"
                :disabled="isSubmitting"
                min="1"
              />
              <div class="form-text">
                Área física donde se ubicará el mobiliario.
                <span v-if="areas.length === 0" class="text-warning">
                  Usa el ID numérico del área.
                </span>
              </div>
              <div v-if="validationErrors.area_id" class="invalid-feedback">
                {{ validationErrors.area_id }}
              </div>
            </div>

            <!-- Notas adicionales -->
            <div class="form-group full-width">
              <label for="notas" class="form-label">
                📄 Notas Adicionales (Opcional)
              </label>
              <textarea
                id="notas"
                v-model="formData.notas"
                class="form-control"
                rows="2"
                placeholder="Observaciones, características especiales, número de serie, etc."
                :disabled="isSubmitting"
                :maxlength="500"
              ></textarea>
              <div class="form-text">
                Información adicional relevante. Máximo 500 caracteres.
                <span class="char-counter">{{ formData.notas?.length || 0 }}/500</span>
              </div>
            </div>
          </div>

          <!-- Información de auditoría -->
          <div class="audit-info">
            <h4>📋 Información de Registro</h4>
            <div class="audit-grid">
              <div class="audit-item">
                <span class="audit-label">Registrado por:</span>
                <span class="audit-value">{{ currentUser?.nombre_completo || 'Usuario actual' }}</span>
              </div>
              <div class="audit-item">
                <span class="audit-label">Fecha de registro:</span>
                <span class="audit-value">{{ currentDate }}</span>
              </div>
              <div class="audit-item">
                <span class="audit-label">Estado inicial:</span>
                <span class="audit-value">
                  {{ getEstadoNombre(formData.estado_id) || 'No seleccionado' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Botones de acción -->
          <div class="form-actions">
            <button 
              type="button" 
              @click="cancelForm" 
              class="btn btn-secondary"
              :disabled="isSubmitting"
            >
              Cancelar
            </button>
            
            <div class="action-group">
              <button 
                type="button" 
                @click="resetForm" 
                class="btn btn-outline"
                :disabled="isSubmitting"
              >
                🔄 Limpiar Formulario
              </button>
              
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="isSubmitting || !isFormValid"
              >
                <span v-if="isSubmitting" class="spinner-small"></span>
                {{ isSubmitting ? 'Guardando...' : '➕ Guardar Mobiliario' }}
              </button>
            </div>
          </div>
        </form>
      </div>

      <!-- Panel de ayuda -->
      <div class="help-panel">
        <h3>💡 Guía para Registrar Mobiliario</h3>
        
        <div class="help-section">
          <h4>📝 Descripción:</h4>
          <ul>
            <li>Describe claramente el tipo de mueble</li>
            <li>Incluye características principales</li>
            <li>Ej: "Silla ergonómica con respaldo ajustable"</li>
          </ul>
        </div>

        <div class="help-section">
          <h4>🪑 Tipos de Mobiliario:</h4>
          <ul>
            <li><strong>Mesas:</strong> Para lectura, estudio o reuniones</li>
            <li><strong>Sillas:</strong> Individuales, ergonómicas o básicas</li>
            <li><strong>Estanterías:</strong> Para libros, revistas o materiales</li>
            <li><strong>Armarios:</strong> Para almacenamiento seguro</li>
            <li><strong>Otros:</strong> Mobiliario especializado</li>
          </ul>
        </div>

        <div class="help-section">
          <h4>📋 Estados:</h4>
          <ul>
            <li><strong>✅ Activo:</strong> En uso normal</li>
            <li><strong>⚠️ En uso:</strong> Actualmente ocupado</li>
            <li><strong>🔧 En reparación:</strong> Requiere mantenimiento</li>
            <li><strong>❌ Desactivado:</strong> Retirado temporalmente</li>
          </ul>
        </div>

        <div class="help-section">
          <h4>📍 Áreas comunes:</h4>
          <ul>
            <li>Sala de lectura principal</li>
            <li>Área de estudio grupal</li>
            <li>Sección de referencia</li>
            <li>Oficina administrativa</li>
            <li>Almacén o bodega</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Toast de éxito/error -->
    <div v-if="showToast" class="toast" :class="toastType">
      <div class="toast-icon">{{ toastIcon }}</div>
      <div class="toast-content">
        <strong>{{ toastTitle }}</strong>
        <p>{{ toastMessage }}</p>
      </div>
      <button @click="showToast = false" class="toast-close">×</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { mobiliarioService } from '@/services/mobiliario'
import { useAuthStore } from '@/stores/auth'
import { useMobiliario } from '@/composables/useFurniture'

const router = useRouter()
const authStore = useAuthStore()

// Estado del formulario
const formData = ref({
  descripcion: '',
  tipo_mobiliario_id: '',
  estado_id: '',
  area_id: '',
  notas: ''
})

// Validación
const validationErrors = ref({})

// Estados de UI
const isSubmitting = ref(false)

// Toast
const showToast = ref(false)
const toastTitle = ref('')
const toastMessage = ref('')
const toastType = ref('success')
const toastIcon = ref('✅')

// Computed
const currentUser = computed(() => authStore.user)
const currentDate = computed(() => {
  return new Date().toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const isFormValid = computed(() => {
  return (
    formData.value.descripcion?.trim() &&
    formData.value.tipo_mobiliario_id &&
    formData.value.estado_id
  )
})

// Métodos
//CARGA DE MOBILIARIO Y UTILIZACION DE COMPOSABLE PARA LOGICA EN EDIT, CREAR Y LISTAR
const { 
  ormData,
  tiposMobiliario,
  estadosMobiliario,
  areas,
  isLoadingCatalogos,
  error,
  initialize
} = useMobiliario()

const getEstadoNombre = (estadoId) => {
  if (!estadoId) return ''
  const estado = estadosMobiliario.value.find(e => e.id == estadoId)
  return estado?.nombre || ''
}

const validateForm = () => {
  validationErrors.value = {}
  let isValid = true

  // Validar descripción
  if (!formData.value.descripcion?.trim()) {
    validationErrors.value.descripcion = 'La descripción es requerida'
    isValid = false
  } else if (formData.value.descripcion.trim().length > 255) {
    validationErrors.value.descripcion = 'Máximo 255 caracteres'
    isValid = false
  }

  // Validar tipo
  if (!formData.value.tipo_mobiliario_id) {
    validationErrors.value.tipo_mobiliario_id = 'Selecciona un tipo de mobiliario'
    isValid = false
  }

  // Validar estado
  if (!formData.value.estado_id) {
    validationErrors.value.estado_id = 'Selecciona un estado'
    isValid = false
  }

  // Validar área (si se proporciona)
  if (formData.value.area_id && formData.value.area_id < 1) {
    validationErrors.value.area_id = 'El ID del área debe ser positivo'
    isValid = false
  }

  return isValid
}

const submitForm = async () => {
  if (!validateForm()) {
    showToastMessage(
      'Formulario incompleto',
      'Por favor, corrige los errores en el formulario',
      'error',
      '❌'
    )
    return
  }

  isSubmitting.value = true
  
  try {
    // Preparar datos para enviar
    const datosEnviar = {
      descripcion: formData.value.descripcion.trim(),
      tipo_mobiliario_id: parseInt(formData.value.tipo_mobiliario_id),
      estado_id: parseInt(formData.value.estado_id),
      area_id: formData.value.area_id ? parseInt(formData.value.area_id) : null
    }
    
    // Agregar notas si existen
    if (formData.value.notas?.trim()) {
      // Nota: Si tu backend acepta un campo "notas", ajústalo aquí
      console.log('Notas:', formData.value.notas.trim())
      // datosEnviar.notas = formData.value.notas.trim()
    }
    
    console.log('📤 Enviando datos:', datosEnviar)
    
    const response = await mobiliarioService.createMobiliario(datosEnviar)
    
    console.log('✅ Mobiliario creado:', response)
    
    showToastMessage(
      '¡Éxito!',
      'El mobiliario ha sido registrado correctamente en el inventario',
      'success',
      '✅'
    )
    
    // Redirigir después de 1.5 segundos
    setTimeout(() => {
      router.push('/admin/mobiliario')
    }, 1500)
    
  } catch (err) {
    console.error('❌ Error creando mobiliario:', err)
    
    let errorMessage = 'Error al registrar el mobiliario'
    
    if (err.response?.data?.detail) {
      errorMessage = err.response.data.detail
    } else if (err.response?.data) {
      // Manejar errores de validación del backend
      const backendErrors = err.response.data
      if (typeof backendErrors === 'object') {
        Object.keys(backendErrors).forEach(key => {
          validationErrors.value[key] = backendErrors[key]
        })
        errorMessage = 'Por favor, corrige los errores en el formulario'
      }
    }
    
    showToastMessage(
      'Error',
      errorMessage,
      'error',
      '❌'
    )
    
  } finally {
    isSubmitting.value = false
  }
}

const resetForm = () => {
  formData.value = {
    descripcion: '',
    tipo_mobiliario_id: '',
    estado_id: estadosMobiliario.value.find(e => 
      e.nombre.toLowerCase().includes('activo')
    )?.id || '',
    area_id: '',
    notas: ''
  }
  validationErrors.value = {}
  
  showToastMessage(
    'Formulario limpiado',
    'Todos los campos han sido restablecidos',
    'info',
    '🔄'
  )
}

const cancelForm = () => {
  if (isSubmitting.value) return
  
  const hasData = Object.values(formData.value).some(value => 
    value !== '' && value !== null && value !== undefined
  )
  
  if (hasData && !confirm('¿Seguro que quieres cancelar? Se perderán los datos no guardados.')) {
    return
  }
  
  router.push('/admin/mobiliario')
}

const showToastMessage = (title, message, type = 'success', icon = '✅') => {
  toastTitle.value = title
  toastMessage.value = message
  toastType.value = type
  toastIcon.value = icon
  showToast.value = true
  
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// Ciclo de vida
onMounted(async () => {
  try {
    // Solo cargar catálogos para creación
    await initialize({
      loadCatalogos: true,
      loadMobiliarioData: false
    })
  } catch (err) {
    console.error('Error inicializando:', err)
  }
})

</script>

<style scoped>
.mobiliario-create-view {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #e9ecef;
}

.header-content h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
}

/* Contenedor del formulario */
.form-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

@media (max-width: 992px) {
  .form-container {
    grid-template-columns: 1fr;
  }
}

/* Tarjeta del formulario */
.form-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* Grid del formulario */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

/* Etiquetas y controles */
.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
}

.form-label.required::after {
  content: ' *';
  color: #dc3545;
}

.form-control,
.form-select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #dee2e6;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: white;
}

.form-control:focus,
.form-select:focus {
  border-color: #4CAF50;
  box-shadow: 0 0 0 0.2rem rgba(76, 175, 80, 0.25);
  outline: none;
}

.form-control:disabled,
.form-select:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
  opacity: 0.7;
}

textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

/* Texto de ayuda */
.form-text {
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.char-counter {
  float: right;
  font-weight: 500;
}

/* Validación */
.invalid-feedback {
  display: block;
  width: 100%;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #dc3545;
}

.alert {
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

.alert-danger {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

/* Información de auditoría */
.audit-info {
  background: #f8f9fa;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin: 2rem 0;
  border-left: 4px solid #4CAF50;
}

.audit-info h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2E7D32;
}

.audit-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.audit-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.audit-label {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
}

.audit-value {
  font-weight: 600;
  color: #495057;
}

/* Botones de acción */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
}

.action-group {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #43A047 0%, #1B5E20 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
  transform: translateY(-2px);
}

.btn-outline {
  background: white;
  color: #4CAF50;
  border: 2px solid #4CAF50;
}

.btn-outline:hover:not(:disabled) {
  background: #f8f9fa;
  transform: translateY(-2px);
}

/* Spinner */
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

.loading-catalogos {
  text-align: center;
  padding: 3rem;
}

.loading-catalogos .spinner {
  width: 50px;
  height: 50px;
  border: 3px solid #e9ecef;
  border-top: 3px solid #4CAF50;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Panel de ayuda */
.help-panel {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  align-self: start;
  position: sticky;
  top: 1rem;
}

.help-panel h3 {
  margin-top: 0;
  color: #2E7D32;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
}

.help-section {
  margin-bottom: 1.5rem;
}

.help-section h4 {
  color: #495057;
  margin-bottom: 0.75rem;
  font-size: 1rem;
}

.help-section ul {
  margin: 0;
  padding-left: 1.5rem;
  color: #6c757d;
}

.help-section li {
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
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
  border-left: 4px solid;
}

.toast.success {
  border-left-color: #28a745;
}

.toast.error {
  border-left-color: #dc3545;
}

.toast.info {
  border-left-color: #17a2b8;
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
  color: #212529;
}

.toast-content p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.toast-close {
  background: none;
  border: none;
  color: #6c757d;
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
  background: #f8f9fa;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .action-group {
    width: 100%;
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  .toast {
    left: 20px;
    right: 20px;
    max-width: none;
  }
}

.text-warning {
  color: #ffc107;
  font-weight: 500;
}
</style>