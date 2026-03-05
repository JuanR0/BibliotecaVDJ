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

    <div v-if="notification" class="notification">
      {{ notification }}
    </div>

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
          <h2 class="section-title">Recursos Prestados</h2>
          <div class="section-tabs">
            <button @click="activeTab = 'books'" :class="['tab-btn', { active: activeTab === 'books' }]">📚 Libros</button>

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
                <!-- BOTONES DE ACCION EN LIBRO -->
                <td>
                  <button v-if="item.status === 'pending'" @click="approveResource(item)" class="action-btn approve-btn"> Autorizar </button>

                  <button v-if="item.status === 'active'" @click="returnResource(item)" :disabled="returningLoanId === item.id" class="action-btn return-btn">
                    <span v-if="returningLoanId === item.id">Procesando...</span>
                    <span v-else>Registrar Devolución</span>
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
      </div>
    </footer>
  </div>
</template>


<script>

//IMPORTACION DE ICONOS
import {
  RESOURCE_ICONS,
  STATUS_TEXT,
  RESOURCE_TYPE,
  ACTIVITY_ICONS
} from '@/utils/resourseHelper'

import { useAuthStore } from '@/stores/auth'
import { prestamoLibroService } from '@/services/PrestamoLibro'

export default {
  name: 'UserMenu',
  
  data() {
    return {
      prestamos: [],
      loadingPrestamos: false,
      returningLoanId: null,
      notification: null,
      activeTab: 'books',
      activeLaptops: 0,
      onlineUsers: 24,

      recentActivities: [
        { id: 1, type: 'approval', description: 'Autorizaste préstamo de "Cien años de soledad"', time: 'Hace 10 min' },
        { id: 2, type: 'loan', description: 'Usuario solicitó préstamo de laptop', time: 'Hace 25 min' },
        { id: 3, type: 'return', description: 'Devolución registrada de área de estudio', time: 'Hace 1 hora' },
        { id: 4, type: 'system', description: 'Nuevo usuario registrado en el sistema', time: 'Hace 2 horas' }
      ],
    }
  },
  
  //INICIALIZACION DE AUTHSTORE
  setup(){
    const authStore = useAuthStore()

    return { authStore }
  },
  
  computed: {
    userName() {
      return this.authStore.userName
    },
    
    userCode() {
      return this.authStore.userCode
    },

    userType(){
      return this.authStore.tipoUsuarioId
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
      if (this.activeTab === 'books') {
        return this.prestamos
      }

      // Por ahora solo libros
      return []
    },

    //ACTUALIZACION DE ESTADISTICAS
    activeBooks() {
      return this.prestamos.filter(
        p => p.status === 'active'
      ).length
    },

    approvedRequests() {
      return this.prestamos.length
    },

    pendingRequests() {
      return this.prestamos.filter(
        p => p.status === 'pending'
      ).length
    }
  },

  //CARGA DE PAGINA
  mounted(){
    this.loadPrestamos()
  },
  
  //METODOS
  methods: {
    //CARGA DE PRESTAMOS
    async loadPrestamos() {
      try {
        this.loadingPrestamos = true

        const data = await prestamoLibroService.getPrestamosUsuario()

        console.log("📦 Préstamos backend:", data)

        // FORMATO DE TABLA
        this.prestamos = await prestamoLibroService.getPrestamosUsuario()
        //DEBUGGING DATOS EN TABLA
        console.table(this.prestamos)

      } catch (error) {
        console.error("Error cargando préstamos:", error)
      } finally {
        this.loadingPrestamos = false
      }
    },
    
    //ESTADO DE LOS PRESTAMOS (FECHA)
    getLoanStatus(prestamo) {
      const hoy = new Date()
      const fechaDevolucion = new Date(prestamo.fecha_devolucion_esperada)

      const diffDias =
        (fechaDevolucion - hoy) / (1000 * 60 * 60 * 24)

      if (diffDias < 0) return 'overdue'
      if (diffDias <= 2) return 'warning'

      return 'active'
    },

    
    
    //NOTIFICACIONES
    showNotification(message) {
      this.notification = message

      setTimeout(() => {
        this.notification = null
      }, 3000)
    },

    navigateTo(route) {
      this.$router.push(route)
    },
    
    refreshData() {
      // PENDIENTE
      console.log('Actualizando datos...')
    },

    
    getStatusText(type){
      return STATUS_TEXT[type] || '📦'
    },
    getResourceIcon(type) { 
      return RESOURCE_ICONS[type] || '📦'
    }, 
    getResourceType(type) 
    { 
      return RESOURCE_TYPE[type] || 'Recurso' 
    }, 
    getActivityIcon(type)
    {
       return ACTIVITY_ICONS[type] || '📝' 
    },
    
    //FORMATEO DE FECHA
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('es-ES')
    },
    
    //ESTATUS
    getStatusText(status) {
      const statuses = {
        active: 'Activo',
        warning: 'Por vencer',
        overdue: 'Vencido',
        completed: 'Devuelto'
      }

      return statuses[status] || status
    },
    
    //ARPOVACION DE PRESTAMO
    approveResource(resource) {
      //PENDIENTE
      console.log('Aprobando recurso:', resource)
    },
    
    //RETORNAR LIBRO
    async returnResource(resource) {
      try {
        this.returningLoanId = resource.id

        await prestamoLibroService.devolverPrestamo(resource.id)

        await this.loadPrestamos()

        this.showNotification("Devolución registrada correctamente!")

      } catch (error) {
        console.error("Error registrando devolución:", error)
        this.showNotification("Error al registrar devolución!")
      } finally {
        this.returningLoanId = null
      }
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

/*ESTILO DE NOTIFICACION*/
  .notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #2ecc71;
    color: white;
    padding: 15px 20px;
    border-radius: 10px;
    font-weight: 600;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    z-index: 2000;
    animation: fadeIn 0.3s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }
}
</style>