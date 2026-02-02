<template>
  <div class="dashboard-container">
    <!-- Header -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="user-welcome">
          <h1 class="welcome-title">👋 Hola, {{ userName }}</h1>
          <p class="welcome-subtitle">Panel de usuario para usuario tipo: {{ userType }}</p>
        </div>
        <div class="user-info-card">
          <div class="user-avatar">
            <span class="avatar-icon">👨‍💼</span>
          </div>
          <div class="user-details">
            <div class="user-detail-item">
              <span class="detail-label">Código:</span>
              <span class="detail-value">{{ userCode }}</span>
            </div>
            <div class="user-detail-item">
              <span class="detail-label">Rol:</span>
              <span class="detail-value role-badge">Administrador Básico</span>
            </div>
            <div class="user-detail-item">
              <span class="detail-label">Último acceso:</span>
              <span class="detail-value">{{ lastAccess }}</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Contenido Principal -->
    <main class="dashboard-main">
      <!-- Panel de Acciones Rápidas -->
      <section class="quick-actions-section">
        <h2 class="section-title">Acciones Rápidas</h2>
        <div class="actions-grid">
          <button @click="navigateTo('/loan-requests')" class="action-card primary">
            <span class="action-icon">📋</span>
            <span class="action-title">Revisar Solicitudes</span>
            <span class="action-desc">Autorizar préstamos pendientes</span>
          </button>
          
          <button @click="navigateTo('/books')" class="action-card secondary">
            <span class="action-icon">📚</span>
            <span class="action-title">Ver Catálogo</span>
            <span class="action-desc">Explorar libros disponibles</span>
          </button>
          
          <button @click="navigateTo('/my-loans')" class="action-card accent">
            <span class="action-icon">📖</span>
            <span class="action-title">Mis Préstamos</span>
            <span class="action-desc">Ver mis préstamos activos</span>
          </button>
          
          <button @click="refreshData" class="action-card info">
            <span class="action-icon">🔄</span>
            <span class="action-title">Actualizar</span>
            <span class="action-desc">Refrescar información</span>
          </button>
        </div>
      </section>

      <!-- Panel de Estadísticas -->
      <section class="stats-section">
        <h2 class="section-title">📊 Estadísticas del Día</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-header">
              <span class="stat-icon">⏳</span>
              <span class="stat-title">Pendientes</span>
            </div>
            <div class="stat-value">{{ pendingRequests }}</div>
            <div class="stat-desc">Solicitudes por revisar</div>
          </div>
          
          <div class="stat-card">
            <div class="stat-header">
              <span class="stat-icon">✅</span>
              <span class="stat-title">Aprobados</span>
            </div>
            <div class="stat-value">{{ approvedRequests }}</div>
            <div class="stat-desc">Préstamos autorizados</div>
          </div>
          
          <div class="stat-card">
            <div class="stat-header">
              <span class="stat-icon">📚</span>
              <span class="stat-title">Libros Activos</span>
            </div>
            <div class="stat-value">{{ activeBooks }}</div>
            <div class="stat-desc">En préstamo actual</div>
          </div>
          
          <div class="stat-card">
            <div class="stat-header">
              <span class="stat-icon">💻</span>
              <span class="stat-title">Laptops</span>
            </div>
            <div class="stat-value">{{ activeLaptops }}</div>
            <div class="stat-desc">Equipos prestados</div>
          </div>
        </div>
      </section>

      <!-- Recursos Prestados -->
      <section class="resources-section">
        <div class="section-header">
          <h2 class="section-title">📦 Recursos Prestados</h2>
          <div class="section-tabs">
            <button 
              @click="activeTab = 'books'" 
              :class="['tab-btn', { active: activeTab === 'books' }]"
            >
              📚 Libros
            </button>
            <button 
              @click="activeTab = 'areas'" 
              :class="['tab-btn', { active: activeTab === 'areas' }]"
            >
              🏢 Áreas
            </button>
            <button 
              @click="activeTab = 'laptops'" 
              :class="['tab-btn', { active: activeTab === 'laptops' }]"
            >
              💻 Laptops
            </button>
          </div>
        </div>

        <!-- Tabla de Recursos -->
        <div class="resources-table-container">
          <table class="resources-table">
            <thead>
              <tr>
                <th>Recurso</th>
                <th>Tipo</th>
                <th>Fecha Préstamo</th>
                <th>Fecha Devolución</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in filteredResources" :key="item.id">
                <td class="resource-name">
                  <span class="resource-icon">{{ getResourceIcon(item.type) }}</span>
                  {{ item.name }}
                </td>
                <td>
                  <span class="resource-type">{{ getResourceType(item.type) }}</span>
                </td>
                <td>{{ formatDate(item.loanDate) }}</td>
                <td>{{ formatDate(item.returnDate) }}</td>
                <td>
                  <span :class="['status-badge', item.status]">
                    {{ getStatusText(item.status) }}
                  </span>
                </td>
                <td>
                  <button 
                    v-if="item.status === 'pending'"
                    @click="approveResource(item)"
                    class="action-btn approve-btn"
                  >
                    ✅ Autorizar
                  </button>
                  <button 
                    v-if="item.status === 'active'"
                    @click="returnResource(item)"
                    class="action-btn return-btn"
                  >
                    ↩️ Registrar Devolución
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="filteredResources.length === 0" class="empty-state">
            <span class="empty-icon">📭</span>
            <p>No hay recursos prestados en este momento</p>
          </div>
        </div>
      </section>

      <!-- Resumen de Actividad Reciente -->
      <section class="activity-section">
        <h2 class="section-title">📝 Actividad Reciente</h2>
        <div class="activity-list">
          <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
            <div class="activity-icon">
              <span>{{ getActivityIcon(activity.type) }}</span>
            </div>
            <div class="activity-content">
              <p class="activity-text">{{ activity.description }}</p>
              <span class="activity-time">{{ activity.time }}</span>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="dashboard-footer">
      <div class="footer-content">
        <div class="system-info">
          <span class="info-item">🕐 Última actualización: {{ lastUpdate }}</span>
          <span class="info-item">👥 Usuarios en línea: {{ onlineUsers }}</span>
        </div>
        <button @click="logout" class="logout-btn">
          🚪 Cerrar Sesión
        </button>
        <button @click="$router.push('/catalog')" class="floating-catalog-btn">
          <span class="floating-icon">📚</span>
          <span class="floating-text">Catálogo</span>
        </button>
      </div>
    </footer>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'UserMenu',
  
  data() {
    return {
      activeTab: 'books',
      pendingRequests: 5,
      approvedRequests: 12,
      activeBooks: 8,
      activeLaptops: 3,
      onlineUsers: 24,
      recentActivities: [
        { id: 1, type: 'approval', description: 'Autorizaste préstamo de "Cien años de soledad"', time: 'Hace 10 min' },
        { id: 2, type: 'loan', description: 'Usuario solicitó préstamo de laptop', time: 'Hace 25 min' },
        { id: 3, type: 'return', description: 'Devolución registrada de área de estudio', time: 'Hace 1 hora' },
        { id: 4, type: 'system', description: 'Nuevo usuario registrado en el sistema', time: 'Hace 2 horas' }
      ],
      resources: [
        { id: 1, type: 'book', name: 'Cien años de soledad', loanDate: '2024-01-15', returnDate: '2024-01-22', status: 'active' },
        { id: 2, type: 'area', name: 'Sala de estudio A', loanDate: '2024-01-16', returnDate: '2024-01-16', status: 'completed' },
        { id: 3, type: 'laptop', name: 'Laptop HP EliteBook', loanDate: '2024-01-17', returnDate: '2024-01-24', status: 'pending' },
        { id: 4, type: 'book', name: 'El principito', loanDate: '2024-01-14', returnDate: '2024-01-21', status: 'active' },
        { id: 5, type: 'book', name: 'Don Quijote de la Mancha', loanDate: '2024-01-18', returnDate: '2024-01-25', status: 'pending' }
      ]
    }
  },
  
  computed: {
    userName() {
      const authStore = useAuthStore()
      return authStore.userName
    },
    
    userCode() {
      const authStore = useAuthStore()
      return authStore.user?.codigo_universitario || 'N/A'
    },

    userType(){
      const authstore = useAuthStore()
      return authstore.tipoUsuarioId
    },
    
    lastAccess() {
      return new Date().toLocaleDateString('es-ES', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })
    },
    
    lastUpdate() {
      return new Date().toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },
    
    filteredResources() {
      return this.resources.filter(item => {
        if (this.activeTab === 'books') return item.type === 'book'
        if (this.activeTab === 'areas') return item.type === 'area'
        if (this.activeTab === 'laptops') return item.type === 'laptop'
        return true
      })
    }
  },
  
  methods: {
    navigateTo(route) {
      this.$router.push(route)
    },
    
    refreshData() {
      // Aquí iría la lógica para actualizar datos
      console.log('Actualizando datos...')
    },
    
    getResourceIcon(type) {
      const icons = {
        book: '📚',
        area: '🏢',
        laptop: '💻'
      }
      return icons[type] || '📦'
    },
    
    getResourceType(type) {
      const types = {
        book: 'Libro',
        area: 'Área',
        laptop: 'Laptop'
      }
      return types[type] || 'Recurso'
    },
    
    getActivityIcon(type) {
      const icons = {
        approval: '✅',
        loan: '📋',
        return: '↩️',
        system: '⚙️'
      }
      return icons[type] || '📝'
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('es-ES')
    },
    
    getStatusText(status) {
      const statuses = {
        pending: 'Pendiente',
        active: 'Activo',
        completed: 'Completado'
      }
      return statuses[status] || status
    },
    
    approveResource(resource) {
      console.log('Aprobando recurso:', resource)
      // Aquí iría la lógica para aprobar el recurso
    },
    
    returnResource(resource) {
      console.log('Registrando devolución:', resource)
      // Aquí iría la lógica para registrar devolución
    },
    
    logout() {
      const authStore = useAuthStore()
      authStore.logout()
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.floating-catalog-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: linear-gradient(135deg, #4361ee, #3a56d4);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 15px 25px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(67, 97, 238, 0.4);
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
}

.floating-catalog-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 25px rgba(67, 97, 238, 0.5);
}

.dashboard-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.dashboard-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px 40px;
  border-bottom-left-radius: 30px;
  border-bottom-right-radius: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 30px;
}

.user-welcome .welcome-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.user-welcome .welcome-subtitle {
  font-size: 16px;
  opacity: 0.9;
}

.user-info-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  min-width: 300px;
}

.user-avatar .avatar-icon {
  font-size: 40px;
  background: rgba(255, 255, 255, 0.2);
  padding: 15px;
  border-radius: 50%;
  display: block;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-detail-item {
  display: flex;
  gap: 10px;
  font-size: 14px;
}

.detail-label {
  font-weight: 600;
  min-width: 80px;
}

.detail-value {
  opacity: 0.9;
}

.role-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.dashboard-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #2d3436;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.quick-actions-section {
  margin-bottom: 40px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.action-card {
  background: white;
  border: none;
  border-radius: 16px;
  padding: 25px;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
}

.action-card.primary {
  border-left: 5px solid #667eea;
}

.action-card.secondary {
  border-left: 5px solid #764ba2;
}

.action-card.accent {
  border-left: 5px solid #2ecc71;
}

.action-card.info {
  border-left: 5px solid #3498db;
}

.action-icon {
  font-size: 28px;
  margin-bottom: 5px;
}

.action-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d3436;
}

.action-desc {
  font-size: 14px;
  color: #636e72;
}

.stats-section {
  margin-bottom: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 25px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.stat-icon {
  font-size: 24px;
}

.stat-title {
  font-size: 14px;
  font-weight: 600;
  color: #636e72;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #2d3436;
  line-height: 1;
}

.stat-desc {
  font-size: 13px;
  color: #636e72;
  margin-top: 8px;
}

.resources-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 40px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-tabs {
  display: flex;
  gap: 10px;
  background: #f8f9fa;
  padding: 5px;
  border-radius: 12px;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-btn.active {
  background: white;
  color: #667eea;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.resources-table-container {
  overflow-x: auto;
}

.resources-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.resources-table th {
  background: #f8f9fa;
  padding: 15px;
  text-align: left;
  font-weight: 600;
  color: #636e72;
  border-bottom: 2px solid #e9ecef;
}

.resources-table td {
  padding: 15px;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

.resource-name {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
}

.resource-icon {
  font-size: 20px;
}

.resource-type {
  background: #e9ecef;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.active {
  background: #d1ecf1;
  color: #0c5460;
}

.status-badge.completed {
  background: #d4edda;
  color: #155724;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.approve-btn {
  background: #d4edda;
  color: #155724;
}

.approve-btn:hover {
  background: #c3e6cb;
}

.return-btn {
  background: #cce5ff;
  color: #004085;
}

.return-btn:hover {
  background: #b8daff;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #636e72;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
  display: block;
}

.activity-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border-radius: 12px;
  background: #f8f9fa;
  transition: background 0.2s;
}

.activity-item:hover {
  background: #e9ecef;
}

.activity-icon span {
  font-size: 24px;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 14px;
  font-weight: 500;
  color: #2d3436;
  margin-bottom: 5px;
}

.activity-time {
  font-size: 12px;
  color: #636e72;
}

.dashboard-footer {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  border-top: 1px solid #e9ecef;
  margin-top: 40px;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.system-info {
  display: flex;
  gap: 30px;
  color: #636e72;
  font-size: 14px;
}

.logout-btn {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.logout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(231, 76, 60, 0.3);
}

@media (max-width: 768px) {
  .dashboard-header {
    padding: 20px;
    border-radius: 0 0 20px 20px;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .user-info-card {
    width: 100%;
    justify-content: center;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .section-tabs {
    justify-content: center;
  }
  
  .footer-content {
    flex-direction: column;
    text-align: center;
  }
  
  .system-info {
    flex-direction: column;
    gap: 10px;
  }
}
</style>