<!-- views/admin/LoanApprovalView.vue -->
<template>
  <div class="loan-approval-view">
    <h1>⏰ Autorización de Préstamos</h1>
    
    <!-- Filtros -->
    <div class="filters-section">
      <div class="filter-group">
        <label>Estado:</label>
        <select v-model="filterStatus" class="filter-select">
          <option value="pending">⏳ Pendientes</option>
          <option value="approved">✅ Aprobados</option>
          <option value="rejected">❌ Rechazados</option>
          <option value="all">📋 Todos</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Fecha:</label>
        <input v-model="filterDate" type="date" class="filter-input">
      </div>
      
      <button @click="clearFilters" class="btn btn-outline">
        🔄 Limpiar
      </button>
    </div>

    <!-- Lista de solicitudes -->
    <div class="requests-list">
      <div v-for="request in filteredRequests" :key="request.id" class="request-card">
        <div class="request-header">
          <h3>{{ request.book_title }}</h3>
          <span class="request-status" :class="request.status">
            {{ getStatusText(request.status) }}
          </span>
        </div>
        
        <div class="request-details">
          <p><strong>👤 Usuario:</strong> {{ request.user_name }}</p>
          <p><strong>📅 Fecha solicitud:</strong> {{ formatDate(request.request_date) }}</p>
          <p><strong>📚 Libro:</strong> {{ request.book_author }} - {{ request.book_isbn }}</p>
          <p><strong>⏱️ Duración:</strong> {{ request.duration_days }} días</p>
          <p v-if="request.reason"><strong>📝 Motivo:</strong> {{ request.reason }}</p>
        </div>
        
        <div v-if="request.status === 'pending'" class="request-actions">
          <button @click="approveRequest(request.id)" class="btn btn-success">
            ✅ Aprobar
          </button>
          <button @click="rejectRequest(request.id)" class="btn btn-danger">
            ❌ Rechazar
          </button>
          <button @click="viewUserDetails(request.user_id)" class="btn btn-info">
            👤 Ver Usuario
          </button>
          <button @click="viewBookDetails(request.book_id)" class="btn btn-outline">
            📖 Ver Libro
          </button>
        </div>
        
        <div v-if="request.status !== 'pending'" class="request-resolution">
          <p><strong>Resolución:</strong> {{ request.resolution_notes || 'Sin comentarios' }}</p>
          <p><strong>Resuelto por:</strong> {{ request.resolved_by }}</p>
          <p><strong>Fecha:</strong> {{ formatDate(request.resolution_date) }}</p>
        </div>
      </div>
      
      <div v-if="filteredRequests.length === 0" class="empty-state">
        <p>📭 No hay solicitudes que coincidan con los filtros</p>
      </div>
    </div>
    
    <!-- Estadísticas -->
    <div class="stats-section">
      <div class="stat-card">
        <h4>📊 Estadísticas</h4>
        <p>Pendientes: {{ pendingCount }}</p>
        <p>Aprobados hoy: {{ approvedToday }}</p>
        <p>Tasa aprobación: {{ approvalRate }}%</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Datos de ejemplo
const loanRequests = ref([
  {
    id: 1,
    user_id: 101,
    user_name: 'Juan Pérez',
    book_id: 1,
    book_title: 'Cien años de soledad',
    book_author: 'Gabriel García Márquez',
    book_isbn: '978-1234567890',
    request_date: '2024-01-15',
    duration_days: 14,
    status: 'pending',
    reason: 'Para investigación académica'
  },
  // ... más solicitudes
])

const filterStatus = ref('pending')
const filterDate = ref('')

// Filtros
const filteredRequests = computed(() => {
  return loanRequests.value.filter(request => {
    const matchesStatus = filterStatus.value === 'all' || request.status === filterStatus.value
    const matchesDate = !filterDate.value || request.request_date === filterDate.value
    return matchesStatus && matchesDate
  })
})

// Estadísticas
const pendingCount = computed(() => {
  return loanRequests.value.filter(r => r.status === 'pending').length
})

// Métodos
const getStatusText = (status) => {
  const texts = {
    pending: '⏳ Pendiente',
    approved: '✅ Aprobado',
    rejected: '❌ Rechazado'
  }
  return texts[status] || status
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('es-ES')
}

const approveRequest = async (requestId) => {
  console.log('Aprobando solicitud:', requestId)
  // Llamar al endpoint de aprobación
}

const rejectRequest = async (requestId) => {
  console.log('Rechazando solicitud:', requestId)
  // Llamar al endpoint de rechazo
}

const clearFilters = () => {
  filterStatus.value = 'pending'
  filterDate.value = ''
}

onMounted(() => {
  // Cargar solicitudes del API
})
</script>

<style scoped>
.loan-approval-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.filters-section {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-select, .filter-input {
  padding: 0.5rem;
  border: 2px solid #ddd;
  border-radius: 0.5rem;
}

.requests-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.request-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border-left: 4px solid #007bff;
}

.request-card .request-status.pending {
  border-left-color: #ffc107;
}

.request-card .request-status.approved {
  border-left-color: #28a745;
}

.request-card .request-status.rejected {
  border-left-color: #dc3545;
}

.request-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.request-status {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: bold;
}

.request-status.pending {
  background: #fff3cd;
  color: #856404;
}

.request-status.approved {
  background: #d4edda;
  color: #155724;
}

.request-status.rejected {
  background: #f8d7da;
  color: #721c24;
}

.request-details p {
  margin: 0.25rem 0;
}

.request-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.request-resolution {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  font-size: 0.9rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.stats-section {
  margin-top: 2rem;
}

.stat-card {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
  max-width: 300px;
}
</style>