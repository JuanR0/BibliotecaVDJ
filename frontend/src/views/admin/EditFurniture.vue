<template>
  <div class="mobiliario-edit-view">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>✏️ Editar Mobiliario</h1>
        <p class="subtitle" v-if="mobiliario">
          Editando: <strong>{{ mobiliario.descripcion }}</strong>
        </p>
        <p class="subtitle" v-else>
          Cargando información del mobiliario...
        </p>
      </div>
      
      <div class="header-actions">
        <router-link to="/admin/mobiliario" class="btn btn-outline">
          ← Volver al Inventario
        </router-link>
      </div>
    </div>

    <!-- Contenido principal -->
    <div class="content-container">
      <!-- Estado de carga -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando información del mobiliario...</p>
      </div>

      <!-- Error de carga -->
      <div v-else-if="loadError" class="error-state">
        <div class="error-card">
          <div class="error-icon">❌</div>
          <h3>Error al cargar el mobiliario</h3>
          <p>{{ loadError }}</p>
          <div class="error-actions">
            <button @click="loadMobiliarioData" class="btn btn-primary">
              Reintentar
            </button>
            <router-link to="/admin/mobiliario" class="btn btn-outline">
              Volver al inventario
            </router-link>
          </div>
        </div>
      </div>

      <!-- Formulario de edición -->
      <div v-else-if="mobiliario" class="form-container">
        <div class="form-card">
          <!-- Información del registro -->
          <div class="record-info">
            <h3>📋 Información del Registro</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">ID:</span>
                <span class="info-value badge bg-secondary">{{ mobiliario.id }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Creado por:</span>
                <span class="info-value">{{ mobiliario.usuario_creador_nombre }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Fecha de ingreso:</span>
                <span class="info-value">{{ formatFecha(mobiliario.fecha_ingreso) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Último cambio de estado:</span>
                <span class="info-value">{{ formatFecha(mobiliario.fecha_ultimo_cambio_estado) }}</span>
              </div>
            </div>
          </div>

          <!-- Formulario -->
          <form @submit.prevent="submitForm">
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
                  placeholder="Describe el mobiliario..."
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
                <label for="tipo_mobiliario_id" class="form-label required">
                  🪑 Tipo de Mobiliario
                </label>
                <select
                  id="tipo_mobiliario_id"
                  v-model="formData.tipo_mobiliario_id"
                  class="form-select"
                  required
                  :disabled="isSubmitting || tiposMobiliario.length === 0"
                >
                  <option value="" disabled>Selecciona un tipo</option>
                  <option 
                    v-for="tipo in tiposMobiliario" 
                    :key="tipo.id" 
                    :value="tipo.id"
                  >
                    {{ tipo.nombre }}
                  </option>
                </select>
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
                  <option value="" disabled>Selecciona un estado</option>
                  <option 
                    v-for="estado in estadosMobiliario" 
                    :key="estado.id" 
                    :value="estado.id"
                  >
                    {{ estado.nombre }}
                  </option>
                </select>
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
                  <option value="">Sin área asignada</option>
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
                <div v-if="validationErrors.area_id" class="invalid-feedback">
                  {{ validationErrors.area_id }}
                </div>
              </div>
            </div>

            <!-- Historial de cambios -->
            <div class="changes-history" v-if="hasChanges">
              <h4>📝 Cambios Pendientes</h4>
              <div class="changes-list">
                <div v-for="change in detectedChanges" :key="change.field" class="change-item">
                  <span class="change-icon">🔄</span>
                  <div class="change-details">
                    <strong>{{ change.label }}:</strong>
                    <span class="change-from">{{ change.from }}</span>
                    <span class="change-arrow">→</span>
                    <span class="change-to">{{ change.to }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Botones de acción -->
            <div class="form-actions">
              <button 
                type="button" 
                @click="cancelEdit" 
                class="btn btn-secondary"
                :disabled="isSubmitting"
              >
                Cancelar
              </button>
              
              <div class="action-group">
                <button 
                  type="button" 
                  @click="resetToOriginal" 
                  class="btn btn-outline"
                  :disabled="isSubmitting || !hasChanges"
                >
                  🔄 Restaurar Original
                </button>
                
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="isSubmitting || !hasChanges"
                >
                  <span v-if="isSubmitting" class="spinner-small"></span>
                  {{ isSubmitting ? 'Guardando...' : '💾 Guardar Cambios' }}
                </button>
              </div>
            </div>
          </form>
        </div>

        <!-- Panel lateral -->
        <div class="side-panel">
          <!-- Estado actual -->
          <div class="status-card">
            <h3>📊 Estado Actual</h3>
            <div class="status-info">
              <div class="status-item">
                <span class="status-label">Estado:</span>
                <span :class="getStatusClass(mobiliario)" class="status-badge">
                  {{ mobiliario.estado_nombre }}
                </span>
              </div>
              <div class="status-item">
                <span class="status-label">Tipo:</span>
                <span class="status-value">{{ mobiliario.tipo_mobiliario_nombre }}</span>
              </div>
              <div class="status-item">
                <span class="status-label">Área:</span>
                <span class="status-value">{{ mobiliario.area_nombre || 'No asignada' }}</span>
              </div>
            </div>
          </div>

          <!-- Acciones rápidas -->
          <div class="quick-actions">
            <h3>⚡ Acciones Rápidas</h3>
            <div class="actions-grid">
              <button 
                v-if="canDesactivate && mobiliario.estado_id !== 4"
                @click="desactivateItem"
                class="btn-action"
                :disabled="isSubmitting"
                title="Desactivar mobiliario"
              >
                <span class="action-icon">⚠️</span>
                <span class="action-text">Desactivar</span>
              </button>
              
              <button 
                v-if="canReactivate && mobiliario.estado_id === 4"
                @click="reactivateItem"
                class="btn-action"
                :disabled="isSubmitting"
                title="Reactivar mobiliario"
              >
                <span class="action-icon">🔄</span>
                <span class="action-text">Reactivar</span>
              </button>
              
              <button 
                v-if="canDelete && mobiliario.estado_id === 4"
                @click="confirmDelete"
                class="btn-action btn-danger"
                :disabled="isSubmitting"
                title="Eliminar permanentemente"
              >
                <span class="action-icon">🗑️</span>
                <span class="action-text">Eliminar</span>
              </button>
              
              <router-link 
                to="/admin/mobiliario" 
                class="btn-action btn-secondary"
                title="Ver en inventario"
              >
                <span class="action-icon">📋</span>
                <span class="action-text">Ver en Lista</span>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modales -->
    <div v-if="showConfirmModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ modalTitle }}</h3>
          <button @click="closeModal" class="modal-close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <p>{{ modalMessage }}</p>
          
          <div class="item-info">
            <h4>{{ mobiliario?.descripcion }}</h4>
            <p><strong>ID:</strong> {{ mobiliario?.id }}</p>
            <p><strong>Tipo:</strong> {{ mobiliario?.tipo_mobiliario_nombre }}</p>
            <p><strong>Estado actual:</strong> {{ mobiliario?.estado_nombre }}</p>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModal" class="btn btn-secondary" :disabled="isProcessing">
            Cancelar
          </button>
          <button @click="executeModalAction" class="btn" :class="modalBtnClass" :disabled="isProcessing">
            <span v-if="isProcessing" class="spinner-small"></span>
            {{ modalButtonText }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast -->
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { mobiliarioService } from '@/services/mobiliario'
import { usePermissions } from '@/composables/usePermissions'
import { useMobiliario } from '@/composables/useFurniture'

const router = useRouter()
const route = useRoute()
const { hasPermission } = usePermissions()

// IDs y datos
const mobiliarioId = ref(parseInt(route.params.id))
const originalData = ref(null)

// Validación
const validationErrors = ref({})

// Modales y Toast
const showConfirmModal = ref(false)
const modalAction = ref('')
const modalTitle = ref('')
const modalMessage = ref('')
const modalButtonText = ref('')
const modalBtnClass = ref('')

const showToast = ref(false)
const toastTitle = ref('')
const toastMessage = ref('')
const toastType = ref('success')
const toastIcon = ref('✅')

// Computed
const canDesactivate = computed(() => hasPermission('canDesactivateMobiliario'))
const canReactivate = computed(() => hasPermission('canReactivateMobiliario'))
const canDelete = computed(() => hasPermission('canDeleteMobiliario'))

// Estados
const isSubmitting = ref(false)


// Computed para cambios
const detectedChanges = computed(() => {
  return getDetectedChanges()
})


const {
  mobiliario,
  formData,
  tiposMobiliario,
  estadosMobiliario,
  areas,
  isLoading,
  isLoadingCatalogos,
  error: loadError,
  initialize,
  setId,
  hasChanges,
  getDetectedChanges
} = useMobiliario(parseInt(route.params.id))

const formatFecha = (fecha) => {
  if (!fecha) return 'N/A'
  try {
    return new Date(fecha).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'Fecha inválida'
  }
}

const getStatusClass = (item) => {
  const classes = {
    1: 'status-available',
    2: 'status-in-use',
    3: 'status-repair',
    4: 'status-inactive'
  }
  return classes[item.estado_id] || 'status-unknown'
}

const validateForm = () => {
  validationErrors.value = {}
  let isValid = true

  if (!formData.value.descripcion?.trim()) {
    validationErrors.value.descripcion = 'La descripción es requerida'
    isValid = false
  }

  if (!formData.value.tipo_mobiliario_id) {
    validationErrors.value.tipo_mobiliario_id = 'Selecciona un tipo de mobiliario'
    isValid = false
  }

  if (!formData.value.estado_id) {
    validationErrors.value.estado_id = 'Selecciona un estado'
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
    const datosEnviar = {
      descripcion: formData.value.descripcion.trim(),
      tipo_mobiliario_id: parseInt(formData.value.tipo_mobiliario_id),
      estado_id: parseInt(formData.value.estado_id)
    }
    
    // Solo enviar área si tiene valor
    if (formData.value.area_id) {
      datosEnviar.area_id = parseInt(formData.value.area_id)
    } else {
      datosEnviar.area_id = null
    }
    
    console.log('📤 Actualizando mobiliario:', datosEnviar)
    
    const response = await mobiliarioService.updateMobiliario(mobiliarioId.value, datosEnviar)
    
    // Actualizar datos locales
    mobiliario.value = { ...mobiliario.value, ...response }
    originalData.value = { ...formData.value }
    
    showToastMessage(
      '¡Actualizado!',
      'Los cambios han sido guardados correctamente',
      'success',
      '✅'
    )
    
  } catch (err) {
    console.error('❌ Error actualizando mobiliario:', err)
    
    let errorMessage = 'Error al guardar los cambios'
    
    if (err.response?.data?.detail) {
      errorMessage = err.response.data.detail
    } else if (err.response?.data) {
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

const resetToOriginal = () => {
  formData.value = { ...originalData.value }
  showToastMessage(
    'Formulario restaurado',
    'Se han restablecido los valores originales',
    'info',
    '🔄'
  )
}

const cancelEdit = () => {
  if (hasChanges.value && !confirm('Tienes cambios sin guardar. ¿Seguro que quieres salir?')) {
    return
  }
  router.push('/admin/mobiliario')
}

// Acciones rápidas
const desactivateItem = () => {
  if (!canDesactivate.value) {
    showToastMessage(
      'Permiso denegado',
      'No tienes permisos para desactivar mobiliario',
      'error',
      '🚫'
    )
    return
  }
  
  modalAction.value = 'desactivate'
  modalTitle.value = '⚠️ Confirmar Desactivación'
  modalMessage.value = '¿Estás seguro de desactivar este mobiliario? Será retirado del inventario activo pero podrás reactivarlo más tarde.'
  modalButtonText.value = 'Sí, Desactivar'
  modalBtnClass.value = 'btn-warning'
  showConfirmModal.value = true
}

const reactivateItem = () => {
  if (!canReactivate.value) {
    showToastMessage(
      'Permiso denegado',
      'No tienes permisos para reactivar mobiliario',
      'error',
      '🚫'
    )
    return
  }
  
  modalAction.value = 'reactivate'
  modalTitle.value = '🔄 Confirmar Reactivación'
  modalMessage.value = '¿Estás seguro de reactivar este mobiliario? Volverá al inventario activo.'
  modalButtonText.value = 'Sí, Reactivar'
  modalBtnClass.value = 'btn-success'
  showConfirmModal.value = true
}

const confirmDelete = () => {
  if (!canDelete.value) {
    showToastMessage(
      'Permiso denegado',
      'No tienes permisos para eliminar mobiliario',
      'error',
      '🚫'
    )
    return
  }
  
  if (mobiliario.value.estado_id !== 4) {
    showToastMessage(
      'Acción no permitida',
      'Solo se puede eliminar mobiliario desactivado',
      'warning',
      '⚠️'
    )
    return
  }
  
  modalAction.value = 'delete'
  modalTitle.value = '🗑️ Confirmar Eliminación Permanente'
  modalMessage.value = '¿Estás seguro de eliminar PERMANENTEMENTE este mobiliario? Esta acción NO se puede deshacer.'
  modalButtonText.value = 'Sí, Eliminar Permanentemente'
  modalBtnClass.value = 'btn-danger'
  showConfirmModal.value = true
}

const executeModalAction = async () => {
  isProcessing.value = true
  
  try {
    let successMessage = ''
    
    switch (modalAction.value) {
      case 'desactivate':
        await mobiliarioService.desactivateMobiliario(mobiliarioId.value)
        mobiliario.value.estado_id = 4
        mobiliario.value.estado_nombre = 'Desactivado'
        formData.value.estado_id = 4
        successMessage = 'Mobiliario desactivado correctamente'
        break
        
      case 'reactivate':
        await mobiliarioService.reactivateMobiliario(mobiliarioId.value)
        mobiliario.value.estado_id = 1
        mobiliario.value.estado_nombre = 'Activo'
        formData.value.estado_id = 1
        successMessage = 'Mobiliario reactivado correctamente'
        break
        
      case 'delete':
        await mobiliarioService.deleteMobiliario(mobiliarioId.value)
        showToastMessage(
          '¡Eliminado!',
          'El mobiliario ha sido eliminado permanentemente',
          'success',
          '✅'
        )
        setTimeout(() => {
          router.push('/admin/mobiliario')
        }, 1500)
        break
    }
    
    if (modalAction.value !== 'delete') {
      showToastMessage(
        '¡Éxito!',
        successMessage,
        'success',
        '✅'
      )
    }
    
    closeModal()
    
  } catch (err) {
    console.error(`Error en ${modalAction.value}:`, err)
    showToastMessage(
      'Error',
      `No se pudo completar la acción: ${err.response?.data?.detail || err.message}`,
      'error',
      '❌'
    )
  } finally {
    isProcessing.value = false
  }
}

const closeModal = () => {
  if (!isProcessing.value) {
    showConfirmModal.value = false
    modalAction.value = ''
  }
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
    // Cargar catálogos Y datos del mobiliario
    await initialize({
      loadCatalogos: true,
      loadMobiliarioData: true
    })
  } catch (err) {
    console.error('Error cargando datos:', err)
  }
})

// Watch para cambios en la ruta
watch(() => route.params.id, (newId) => {
  if (newId) {
    setId(parseInt(newId))
    initialize({
      loadCatalogos: true,
      loadMobiliarioData: true
    })
  }
})  

</script>

<style scoped>
.mobiliario-edit-view {
  padding: 1rem;
  max-width: 1400px;
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

/* Contenedor principal */
.content-container {
  min-height: 400px;
}

/* Estados de carga */
.loading-state {
  text-align: center;
  padding: 4rem;
}

.loading-state .spinner {
  width: 60px;
  height: 60px;
  border: 4px solid #e9ecef;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  margin: 0 auto 1.5rem;
  animation: spin 1s linear infinite;
}

.error-state {
  text-align: center;
  padding: 3rem;
}

.error-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  max-width: 500px;
  margin: 0 auto;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.7;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1.5rem;
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

/* Información del registro */
.record-info {
  background: #f8f9fa;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border-left: 4px solid #4CAF50;
}

.record-info h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2E7D32;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
}

.info-value {
  font-weight: 600;
  color: #495057;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 0.25rem;
}

.bg-secondary {
  background-color: #6c757d;
  color: white;
}

/* Grid del formulario (reutilizado de create) */
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

/* Historial de cambios */
.changes-history {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin: 2rem 0;
}

.changes-history h4 {
  margin-top: 0;
  color: #856404;
  margin-bottom: 1rem;
}

.changes-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.change-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  background: white;
  border-radius: 0.5rem;
  border: 1px solid #e9ecef;
}

.change-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.change-details {
  flex: 1;
  font-size: 0.9rem;
}

.change-from,
.change-to {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  margin: 0 0.25rem;
  border-radius: 0.25rem;
  font-family: monospace;
}

.change-from {
  background: #f8d7da;
  color: #721c24;
  text-decoration: line-through;
}

.change-to {
  background: #d4edda;
  color: #155724;
}

.change-arrow {
  color: #6c757d;
  margin: 0 0.5rem;
}

/* Panel lateral */
.side-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.status-card,
.quick-actions {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.status-card h3,
.quick-actions h3 {
  margin-top: 0;
  color: #2E7D32;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-label {
  font-weight: 500;
  color: #495057;
}

.status-value {
  font-weight: 600;
  color: #2E7D32;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-available {
  background: #d4edda;
  color: #155724;
}

.status-in-use {
  background: #fff3cd;
  color: #856404;
}

.status-repair {
  background: #d1ecf1;
  color: #0c5460;
}

.status-inactive {
  background: #f8d7da;
  color: #721c24;
}

/* Acciones rápidas */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.btn-action {
  background: #f8f9fa;
  border: 2px solid #dee2e6;
  border-radius: 0.75rem;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  color: inherit;
}

.btn-action:hover:not(:disabled) {
  background: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-action.btn-danger {
  border-color: #dc3545;
  color: #dc3545;
}

.btn-action.btn-danger:hover:not(:disabled) {
  background: #f8d7da;
}

.btn-action.btn-secondary {
  border-color: #6c757d;
  color: #6c757d;
}

.action-icon {
  font-size: 1.5rem;
}

.action-text {
  font-size: 0.8rem;
  font-weight: 600;
  text-align: center;
}

/* Modal (reutilizado) */
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
  z-index: 2000;
  backdrop-filter: blur(2px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
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

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6c757d;
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
  background: #f8f9fa;
}

.modal-body {
  padding: 1.5rem;
}

.modal-body .item-info {
  margin: 1.5rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #4CAF50;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e9ecef;
}

.btn-warning {
  background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%);
  color: #212529;
  border: none;
}

.btn-warning:hover:not(:disabled) {
  background: linear-gradient(135deg, #e0a800 0%, #d39e00 100%);
}

.btn-success {
  background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
  color: white;
  border: none;
}

.btn-success:hover:not(:disabled) {
  background: linear-gradient(135deg, #218838 0%, #1c7430 100%);
}

.btn-danger {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  color: white;
  border: none;
}

.btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #c82333 0%, #bd2130 100%);
}

/* Toast (reutilizado) */
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

.toast.warning {
  border-left-color: #ffc107;
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
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .btn,
  .btn-action {
    width: 100%;
    justify-content: center;
  }
  
  .toast {
    left: 20px;
    right: 20px;
    max-width: none;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .modal-footer .btn {
    width: 100%;
  }
}
</style>