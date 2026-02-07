<template>
  <div class="areas-management">
    <!-- Header simplificado -->
    <div class="management-header">
      <div class="header-content">
        <h1>🏢 Gestión de Áreas</h1>
        <p class="subtitle">Administra las áreas y cubículos</p>
      </div>
      
      <div class="header-actions">
        <button 
          v-if="puedeCrearAreas"
          @click="openCreateModal" 
          class="btn-create-area"
        >
          ➕ Nueva Área
        </button>
        
        <!-- Botón para recargar datos -->
        <button 
          @click="forceReload" 
          class="btn-reload"
          title="Recargar datos"
        >
          🔄
        </button>
      </div>
    </div>

    <!-- Pestañas simplificadas -->
    <div class="tabs-simple">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="{ 'active': activeTab === tab.id }"
        class="tab-simple-btn"
      >
        {{ tab.icon }} {{ tab.label }}
        <span class="tab-count">{{ getTabCount(tab.id) }}</span>
      </button>
    </div>

    <!-- Contenido principal -->
    <div class="content-container">
      <!-- Estado de carga -->
      <div v-if="isLoading" class="loading-simple">
        <div class="spinner"></div>
        <p>Cargando áreas...</p>
      </div>

      <!-- Estado de error -->
      <div v-else-if="error" class="error-simple">
        <p>❌ {{ error }}</p>
        <button @click="loadData" class="btn-retry">Reintentar</button>
      </div>

      <!-- Contenido de la pestaña activa -->
      <template v-else>
        <!-- Vista de tarjetas para prestables -->
        <div v-if="activeTab === 'prestables'" class="cards-view">
          <div 
            v-for="area in areasPrestables" 
            :key="area.id" 
            class="area-card-simple"
          >
            <div class="card-header">
              <h3>{{ area.nombre }}</h3>
              <span :class="`status-${area.estado_id}`" class="status-dot"></span>
            </div>
            
            <div class="card-body">
              <p><strong>Capacidad:</strong> {{ area.capacidad || 'N/A' }}</p>
              <p><strong>Estado:</strong> {{ area.estado_nombre || 'Desconocido' }}</p>
              <p><strong>Creado por:</strong> {{ area.usuario_registro_nombre }}</p>
            </div>
            
            <div class="card-actions">
              <button 
                @click="handleEdit(area)"
                class="btn-action btn-edit"
                title="Editar"
              >
                ✏️
              </button>
              
              <button 
                v-if="area.estado_id !== 4"
                @click="handleDesactivate(area)"
                class="btn-action btn-warn"
                title="Desactivar"
              >
                ⚠️
              </button>
              
              <button 
                v-if="area.estado_id === 4"
                @click="handleReactivate(area)"
                class="btn-action btn-success"
                title="Reactivar"
              >
                🔄
              </button>
            </div>
          </div>
          
          <!-- Sin áreas -->
          <div v-if="areasPrestables.length === 0" class="empty-state">
            <p>No hay áreas prestables</p>
            <button 
              v-if="puedeCrearAreas"
              @click="openCreateModal" 
              class="btn-create"
            >
              Crear primera área
            </button>
          </div>
        </div>

        <!-- Vista de tabla para internas/todas -->
        <div v-else class="table-view">
          <table class="simple-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Tipo</th>
                <th>Capacidad</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="area in currentTabAreas" :key="area.id">
                <td>{{ area.nombre }}</td>
                <td>
                  <span class="type-badge" :class="area.es_prestable ? 'prestable' : 'interna'">
                    {{ area.es_prestable ? '🎓' : '🏢' }}
                  </span>
                </td>
                <td>{{ area.capacidad || 'N/A' }}</td>
                <td>
                  <span class="state-badge" :class="`state-${area.estado_id}`">
                    {{ area.estado_nombre || 'Desconocido' }}
                  </span>
                </td>
                <td>
                  <div class="table-actions">
                    <button @click="handleEdit(area)" class="table-btn" title="Editar">
                      ✏️
                    </button>
                    <button 
                      v-if="area.estado_id !== 4"
                      @click="handleDesactivate(area)" 
                      class="table-btn table-btn-warn"
                      title="Desactivar"
                    >
                      ⚠️
                    </button>
                    <button 
                      v-if="area.estado_id === 4"
                      @click="handleReactivate(area)" 
                      class="table-btn table-btn-success"
                      title="Reactivar"
                    >
                      🔄
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <!-- Modal simple de edición -->
    <div v-if="showModal" class="modal-simple">
      <div class="modal-content">
        <h3>{{ isEditing ? 'Editar Área' : 'Nueva Área' }}</h3>
        
        <form @submit.prevent="handleSave">
          <div class="form-group">
            <label>Nombre:</label>
            <input 
              v-model="formData.nombre" 
              type="text" 
              required
              placeholder="Nombre del área"
            />
          </div>
          
          <div class="form-group">
            <label>Tipo:</label>
            <div class="type-select">
              <label>
                <input 
                  type="radio" 
                  v-model="formData.es_prestable" 
                  :value="true"
                />
                🎓 Prestable
              </label>
              <label>
                <input 
                  type="radio" 
                  v-model="formData.es_prestable" 
                  :value="false"
                />
                🏢 Interna
              </label>
            </div>
          </div>
          
          <div class="form-group" v-if="formData.es_prestable">
            <label>Capacidad:</label>
            <input 
              v-model.number="formData.capacidad" 
              type="number" 
              min="1"
              required
              placeholder="Ej: 8"
            />
          </div>
          
          <div class="form-group" v-else>
            <label>Capacidad (opcional):</label>
            <input 
              v-model.number="formData.capacidad" 
              type="number" 
              min="0"
              placeholder="Ej: 50"
            />
          </div>
          
          <div class="form-group" v-if="isEditing">
            <label>Estado:</label>
            <select v-model="formData.estado_id">
              <option v-for="estado in estadosArea" :key="estado.id" :value="estado.id">
                {{ estado.estado }}
              </option>
            </select>
          </div>
          
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-cancel">
              Cancelar
            </button>
            <button type="submit" class="btn-save" :disabled="isSaving">
              {{ isSaving ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal de confirmación -->
    <div v-if="showConfirmModal" class="modal-simple">
      <div class="modal-content">
        <h3>{{ confirmTitle }}</h3>
        <p>{{ confirmMessage }}</p>
        
        <div class="modal-actions">
          <button @click="closeConfirmModal" class="btn-cancel">
            Cancelar
          </button>
          <button @click="executeConfirmedAction" class="btn-confirm" :disabled="isSaving">
            {{ isSaving ? 'Procesando...' : 'Confirmar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast simple -->
    <div v-if="showToast" class="toast-simple" :class="toastType">
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAreas } from '@/composables/useAreas'

const authStore = useAuthStore()
const {
  areas,
  estadosArea,
  isLoading,
  error,
  cargarAreas,
  cargarEstados,
  crearArea,
  actualizarArea,
  desactivarArea,
  reactivarArea,
  refrescarArea
} = useAreas()

// ========== STATE SIMPLIFICADO ==========
const activeTab = ref('prestables')
const showModal = ref(false)
const showConfirmModal = ref(false)
const showToast = ref(false)
const isSaving = ref(false)

// Datos del formulario
const formData = ref({
  id: null,
  nombre: '',
  capacidad: null,
  es_prestable: true,
  estado_id: 1
})

// Confirmación
const confirmAction = ref(null)
const confirmArea = ref(null)
const confirmTitle = ref('')
const confirmMessage = ref('')

// Toast
const toastMessage = ref('')
const toastType = ref('success')

// ========== COMPUTED SIMPLIFICADOS ==========
const puedeCrearAreas = computed(() => authStore.puedeCrearAreas)
const puedeEditarAreas = computed(() => authStore.puedeEditarAreas)
const puedeDesactivarAreas = computed(() => authStore.puedeDesactivarAreas)
const puedeReactivarAreas = computed(() => authStore.puedeReactivarAreas)

const tabs = [
  { id: 'prestables', label: 'Prestables', icon: '🎓' },
  { id: 'internas', label: 'Internas', icon: '🏢' },
  { id: 'todas', label: 'Todas', icon: '📋' }
]

const areasPrestables = computed(() => 
  areas.value.filter(a => a.es_prestable && a.estado_id !== 4)
)

const areasInternas = computed(() => 
  areas.value.filter(a => !a.es_prestable && a.estado_id !== 4)
)

const todasLasAreas = computed(() => 
  areas.value.filter(a => a.estado_id !== 4)
)

const currentTabAreas = computed(() => {
  switch (activeTab.value) {
    case 'prestables': return areasPrestables.value
    case 'internas': return areasInternas.value
    case 'todas': return todasLasAreas.value
    default: return []
  }
})

const getTabCount = (tabId) => {
  switch (tabId) {
    case 'prestables': return areasPrestables.value.length
    case 'internas': return areasInternas.value.length
    case 'todas': return todasLasAreas.value.length
    default: return 0
  }
}

const isEditing = computed(() => !!formData.value.id)

// ========== MÉTODOS SIMPLIFICADOS ==========
const loadData = async () => {
  try {
    await cargarAreas()
    await cargarEstados()
  } catch (err) {
    console.error('Error cargando datos:', err)
  }
}

const forceReload = () => {
  loadData()
  showToastMessage('Datos recargados', 'success')
}

// Modal de creación/edición
const openCreateModal = () => {
  formData.value = {
    id: null,
    nombre: '',
    capacidad: null,
    es_prestable: true,
    estado_id: 1
  }
  showModal.value = true
}

const handleEdit = (area) => {
  if (!puedeEditarAreas.value) {
    showToastMessage('No tienes permisos para editar', 'error')
    return
  }
  
  formData.value = {
    id: area.id,
    nombre: area.nombre,
    capacidad: area.capacidad,
    es_prestable: area.es_prestable,
    estado_id: area.estado_id
  }
  showModal.value = true
}

const closeModal = () => {
  if (!isSaving.value) {
    showModal.value = false
  }
}

// Guardar área
const handleSave = async () => {
  if (isSaving.value) return
  
  // Validaciones básicas
  if (!formData.value.nombre.trim()) {
    showToastMessage('El nombre es requerido', 'error')
    return
  }
  
  if (formData.value.es_prestable && !formData.value.capacidad) {
    showToastMessage('La capacidad es requerida para áreas prestables', 'error')
    return
  }
  
  isSaving.value = true
  
  try {
    if (isEditing.value) {
      // Actualizar
      await actualizarArea(formData.value.id, {
        nombre: formData.value.nombre,
        capacidad: formData.value.capacidad,
        es_prestable: formData.value.es_prestable,
        estado_id: formData.value.estado_id
      })
      
      showToastMessage('Área actualizada correctamente', 'success')
    } else {
      // Crear
      await crearArea({
        nombre: formData.value.nombre,
        capacidad: formData.value.capacidad,
        es_prestable: formData.value.es_prestable,
        estado_id: formData.value.estado_id
      })
      
      showToastMessage('Área creada correctamente', 'success')
    }
    
    showModal.value = false
    
  } catch (err) {
    console.error('Error guardando área:', err)
    showToastMessage(err.message || 'Error al guardar', 'error')
  } finally {
    isSaving.value = false
  }
}

// Acciones de desactivar/reactivar
const handleDesactivate = (area) => {
  if (!puedeDesactivarAreas.value) {
    showToastMessage('No tienes permisos para desactivar', 'error')
    return
  }
  
  confirmArea.value = area
  confirmAction.value = 'desactivate'
  confirmTitle.value = 'Desactivar Área'
  confirmMessage.value = `¿Desactivar "${area.nombre}"?`
  showConfirmModal.value = true
}

const handleReactivate = (area) => {
  if (!puedeReactivarAreas.value) {
    showToastMessage('No tienes permisos para reactivar', 'error')
    return
  }
  
  confirmArea.value = area
  confirmAction.value = 'reactivate'
  confirmTitle.value = 'Reactivar Área'
  confirmMessage.value = `¿Reactivar "${area.nombre}"?`
  showConfirmModal.value = true
}

const closeConfirmModal = () => {
  if (!isSaving.value) {
    showConfirmModal.value = false
    confirmArea.value = null
    confirmAction.value = null
  }
}

const executeConfirmedAction = async () => {
  if (!confirmArea.value || isSaving.value) return
  
  isSaving.value = true
  
  try {
    if (confirmAction.value === 'desactivate') {
      await desactivarArea(confirmArea.value.id)
      showToastMessage('Área desactivada', 'success')
    } else if (confirmAction.value === 'reactivate') {
      await reactivarArea(confirmArea.value.id)
      showToastMessage('Área reactivada', 'success')
    }
    
    closeConfirmModal()
    
  } catch (err) {
    console.error('Error en acción confirmada:', err)
    showToastMessage(err.message || 'Error en la acción', 'error')
  } finally {
    isSaving.value = false
  }
}

// Toast helper
const showToastMessage = (message, type = 'success') => {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// ========== LIFECYCLE ==========
onMounted(() => {
  loadData()
})
</script>

<style scoped>
/* Estilos simplificados */
.areas-management {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #64B5F6 0%, #1976D2 100%);
  border-radius: 10px;
  color: white;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
}

.subtitle {
  margin: 5px 0 0;
  opacity: 0.9;
}

.btn-create-area {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.btn-reload {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  margin-left: 10px;
}

.tabs-simple {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tab-simple-btn {
  flex: 1;
  padding: 12px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.tab-simple-btn.active {
  background: #1976D2;
  color: white;
  border-color: #1976D2;
}

.tab-count {
  background: #e0e0e0;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.tab-simple-btn.active .tab-count {
  background: rgba(255, 255, 255, 0.3);
}

/* Tarjetas */
.cards-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.area-card-simple {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border: 1px solid #e0e0e0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-1 { background: #4CAF50; }
.status-2 { background: #FF9800; }
.status-3 { background: #2196F3; }
.status-4 { background: #9E9E9E; }
.status-5 { background: #607D8B; }

.card-body p {
  margin: 8px 0;
  color: #555;
}

.card-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.btn-action {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}

.btn-edit {
  background: #e3f2fd;
  color: #1976D2;
}

.btn-warn {
  background: #fff3cd;
  color: #856404;
}

.btn-success {
  background: #d4edda;
  color: #155724;
}

/* Tabla */
.simple-table {
  width: 100%;
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border-collapse: collapse;
}

.simple-table th {
  background: #f5f5f5;
  padding: 15px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
}

.simple-table td {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.type-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 14px;
}

.type-badge.prestable {
  background: #e3f2fd;
  color: #1976D2;
}

.type-badge.interna {
  background: #f3e5f5;
  color: #7B1FA2;
}

.state-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.state-1 { background: #d4edda; color: #155724; }
.state-2 { background: #fff3cd; color: #856404; }
.state-3 { background: #d1ecf1; color: #0c5460; }
.state-4 { background: #f8d7da; color: #721c24; }
.state-5 { background: #e9ecef; color: #495057; }

.table-actions {
  display: flex;
  gap: 8px;
}

.table-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
}

.table-btn:hover {
  background: #f5f5f5;
}

.table-btn-warn:hover {
  background: #fff3cd;
}

.table-btn-success:hover {
  background: #d4edda;
}

/* Modal */
.modal-simple {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 10px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin: 0 0 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
}

.type-select {
  display: flex;
  gap: 20px;
}

.type-select label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.btn-cancel {
  padding: 10px 20px;
  background: #f5f5f5;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #333;
}

.btn-save, .btn-confirm {
  padding: 10px 20px;
  background: #1976D2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-save:hover:not(:disabled),
.btn-confirm:hover:not(:disabled) {
  background: #1565C0;
}

.btn-save:disabled,
.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Toast */
.toast-simple {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 2000;
  animation: slideIn 0.3s ease;
}

.toast-simple.success {
  background: #4CAF50;
}

.toast-simple.error {
  background: #f44336;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Estados */
.loading-simple,
.error-simple,
.empty-state {
  text-align: center;
  padding: 50px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1976D2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.btn-retry, .btn-create {
  padding: 10px 20px;
  background: #1976D2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 15px;
}

/* Responsive */
@media (max-width: 768px) {
  .management-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .tabs-simple {
    flex-direction: column;
  }
  
  .cards-view {
    grid-template-columns: 1fr;
  }
  
  .simple-table {
    display: block;
    overflow-x: auto;
  }
  
  .type-select {
    flex-direction: column;
    gap: 10px;
  }
}
</style>