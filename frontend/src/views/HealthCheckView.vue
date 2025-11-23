<!-- views/HealthCheck.vue -->
<template>
  <div class="healthcheck">
    <div class="container">
      <h1>🔍 Estado del Sistema - Biblioteca VDJ</h1>
      
      <!-- Tarjeta de Estado General -->
      <div class="overview-card" :class="overallStatus">
        <h2>Resumen del Sistema</h2>
        <div class="overview-grid">
          <div class="overview-item">
            <span class="status-icon">🌐</span>
            <div>
              <h3>Frontend Vue.js</h3>
              <p>✅ Operativo</p>
            </div>
          </div>
          <div class="overview-item">
            <span class="status-icon">🚀</span>
            <div>
              <h3>Backend FastAPI</h3>
              <p>{{ backendStatus.message }}</p>
            </div>
          </div>
          <div class="overview-item">
            <span class="status-icon">💾</span>
            <div>
              <h3>Base de Datos</h3>
              <p>{{ databaseStatus.message }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tarjetas Detalladas -->
      <div class="status-cards">
        <!-- Backend Status -->
        <div class="status-card" :class="backendStatus.class">
          <h3>Backend FastAPI</h3>
          <div class="status-indicator">
            <span class="dot" :class="backendStatus.class"></span>
            {{ backendStatus.message }}
          </div>
          <div class="status-details">
            <p><strong>URL:</strong> http://localhost:8000</p>
            <p><strong>Endpoint:</strong> /api/health</p>
            <p v-if="backendStatus.responseTime"><strong>Tiempo respuesta:</strong> {{ backendStatus.responseTime }}ms</p>
            <p v-if="backendStatus.data"><strong>Respuesta:</strong> {{ backendStatus.data }}</p>
          </div>
        </div>

        <!-- Database Status -->
        <div class="status-card" :class="databaseStatus.class">
          <h3>Base de Datos</h3>
          <div class="status-indicator">
            <span class="dot" :class="databaseStatus.class"></span>
            {{ databaseStatus.message }}
          </div>
          <div class="status-details">
            <p><strong>Estado:</strong> {{ databaseStatus.details || 'Verificando...' }}</p>
            <p v-if="databaseStatus.responseTime"><strong>Tiempo respuesta:</strong> {{ databaseStatus.responseTime }}ms</p>
            <p v-if="databaseStatus.error"><strong>Error:</strong> {{ databaseStatus.error }}</p>
          </div>
        </div>

        <!-- Información del Sistema -->
        <div class="status-card info-card">
          <h3>Información del Sistema</h3>
          <div class="system-info">
            <p><strong>Servicio:</strong> Biblioteca VDJ</p>
            <p><strong>Frontend:</strong> Vue.js 3 + Vite</p>
            <p><strong>Backend:</strong> FastAPI</p>
            <p><strong>Última verificación:</strong> {{ lastCheck }}</p>
            <p><strong>Tiempo total:</strong> {{ totalResponseTime }}ms</p>
          </div>
        </div>
      </div>

      <!-- Acciones -->
      <div class="actions">
        <button 
          @click="checkAllSystems" 
          class="btn btn-primary"
          :disabled="isChecking"
        >
          {{ isChecking ? '🔍 Verificando...' : '🔄 Verificar Todo' }}
        </button>
        <button @click="checkBackendOnly" class="btn btn-outline">
          🌐 Solo Backend
        </button>
        <button @click="checkDatabaseOnly" class="btn btn-outline">
          💾 Solo Base de Datos
        </button>
        <button @click="$router.push('/')" class="btn btn-secondary">
          ← Volver al Inicio
        </button>
      </div>

      <!-- Log de Eventos -->
      <div class="event-log" v-if="eventLog.length > 0">
        <h3>Log de Eventos</h3>
        <div class="log-entries">
          <div 
            v-for="(event, index) in eventLog" 
            :key="index" 
            class="log-entry"
            :class="event.type"
          >
            <span class="log-time">{{ event.time }}</span>
            <span class="log-message">{{ event.message }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '@/services/api'

export default {
  name: 'HealthCheck',
  data() {
    return {
      isChecking: false,
      lastCheck: 'Nunca',
      totalResponseTime: 0,
      eventLog: [],
      
      backendStatus: {
        class: 'checking',
        message: 'Verificando...',
        responseTime: null,
        data: null
      },
      
      databaseStatus: {
        class: 'checking',
        message: 'Verificando...',
        responseTime: null,
        details: null,
        error: null
      }
    }
  },
  computed: {
    overallStatus() {
      if (this.backendStatus.class === 'healthy' && this.databaseStatus.class === 'healthy') {
        return 'healthy'
      } else if (this.backendStatus.class === 'error' || this.databaseStatus.class === 'error') {
        return 'error'
      }
      return 'checking'
    }
  },
  methods: {
    addLog(message, type = 'info') {
      this.eventLog.unshift({
        time: new Date().toLocaleTimeString(),
        message,
        type
      })
      // Mantener solo los últimos 10 logs
      if (this.eventLog.length > 10) {
        this.eventLog.pop()
      }
    },

    async checkAllSystems() {
      this.isChecking = true
      this.addLog('Iniciando verificación completa del sistema...', 'info')
      const startTime = Date.now()

      await Promise.all([
        this.checkBackendStatus(),
        this.checkDatabaseStatus()
      ])

      this.totalResponseTime = Date.now() - startTime
      this.lastCheck = new Date().toLocaleTimeString()
      this.isChecking = false
      this.addLog('Verificación completa finalizada', 'info')
    },

    async checkBackendOnly() {
      this.addLog('Verificando solo el backend...', 'info')
      await this.checkBackendStatus()
    },

    async checkDatabaseOnly() {
      this.addLog('Verificando solo la base de datos...', 'info')
      await this.checkDatabaseStatus()
    },

    async checkBackendStatus() {
      const startTime = Date.now()
      
      try {
        this.backendStatus.class = 'checking'
        this.backendStatus.message = 'Verificando...'
        
        const response = await api.get('/api/health', { timeout: 5000 })
        const responseTime = Date.now() - startTime
        
        this.backendStatus = {
          class: 'healthy',
          message: '✅ Backend operativo',
          responseTime,
          data: JSON.stringify(response.data)
        }
        
        this.addLog(`Backend respondió en ${responseTime}ms`, 'success')
        
      } catch (error) {
        const responseTime = Date.now() - startTime
        let errorMessage = 'Error desconocido'
        
        if (error.code === 'ECONNREFUSED') {
          errorMessage = 'Conexión rechazada - Servidor no disponible'
        } else if (error.response) {
          errorMessage = `HTTP ${error.response.status}: ${error.response.statusText}`
        } else if (error.request) {
          errorMessage = 'No se recibió respuesta del servidor'
        } else {
          errorMessage = error.message
        }
        
        this.backendStatus = {
          class: 'error',
          message: '❌ Error en backend',
          responseTime,
          data: null
        }
        
        this.addLog(`Error en backend: ${errorMessage}`, 'error')
      }
    },

    async checkDatabaseStatus() {
      const startTime = Date.now()
      
      try {
        this.databaseStatus.class = 'checking'
        this.databaseStatus.message = 'Verificando conexión...'
        
        // Intentar diferentes métodos para verificar la BD
        let dbResponse
        let dbCheckMethod = 'health endpoint'
        
        try {
          // Método 1: Endpoint específico de health de BD si existe
          dbResponse = await api.get('/api/health/db', { timeout: 3000 })
        } catch (error) {
          // Método 2: Si no existe, probar con un endpoint simple de la API
          dbCheckMethod = 'users endpoint'
          dbResponse = await api.get('/api/usuarios', { 
            timeout: 3000,
            params: { limit: 1 } // Solo pedir 1 registro para probar
          })
        }
        
        const responseTime = Date.now() - startTime
        
        this.databaseStatus = {
          class: 'healthy',
          message: '✅ Base de datos conectada',
          responseTime,
          details: `Verificado via ${dbCheckMethod}`,
          error: null
        }
        
        this.addLog(`Base de datos respondió en ${responseTime}ms (${dbCheckMethod})`, 'success')
        
      } catch (error) {
        const responseTime = Date.now() - startTime
        let errorDetails = 'Error verificando conexión'
        
        if (error.response?.status === 500) {
          errorDetails = 'Error interno del servidor - Posible problema de BD'
        } else if (error.response?.status === 422) {
          errorDetails = 'Error de validación - BD podría estar funcionando'
        } else if (error.code === 'ECONNREFUSED') {
          errorDetails = 'Backend no disponible - No se puede verificar BD'
        } else {
          errorDetails = error.message
        }
        
        this.databaseStatus = {
          class: 'error',
          message: '❌ Error en base de datos',
          responseTime,
          details: 'No se pudo establecer conexión',
          error: errorDetails
        }
        
        this.addLog(`Error en base de datos: ${errorDetails}`, 'error')
      }
    }
  },
  mounted() {
    this.addLog('Sistema de health check inicializado', 'info')
    this.checkAllSystems()
  }
}
</script>

<style scoped>
.healthcheck {
  min-height: 100vh;
  background: #f8f9fa;
  padding: 2rem 1rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
}

.overview-card {
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.overview-card.healthy {
  border-left: 6px solid #28a745;
}

.overview-card.error {
  border-left: 6px solid #dc3545;
}

.overview-card.checking {
  border-left: 6px solid #ffc107;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.overview-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
}

.status-icon {
  font-size: 2rem;
}

.overview-item h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  color: #333;
}

.overview-item p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.status-card {
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.status-card.healthy {
  border-left: 4px solid #28a745;
}

.status-card.error {
  border-left: 4px solid #dc3545;
}

.status-card.checking {
  border-left: 4px solid #ffc107;
}

.info-card {
  border-left: 4px solid #17a2b8;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: bold;
  margin: 1rem 0;
  font-size: 1.1rem;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot.healthy {
  background: #28a745;
}

.dot.error {
  background: #dc3545;
}

.dot.checking {
  background: #ffc107;
}

.status-details {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.status-details p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  word-break: break-word;
}

.system-info p {
  margin: 0.5rem 0;
  color: #555;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
  min-width: 140px;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-outline {
  background: transparent;
  color: #007bff;
  border: 2px solid #007bff;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.event-log {
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.log-entries {
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.log-entry {
  display: flex;
  gap: 1rem;
  padding: 0.5rem;
  border-bottom: 1px solid #eee;
}

.log-entry:last-child {
  border-bottom: none;
}

.log-entry.success {
  color: #28a745;
}

.log-entry.error {
  color: #dc3545;
}

.log-entry.info {
  color: #17a2b8;
}

.log-time {
  color: #666;
  min-width: 80px;
}

.log-message {
  flex: 1;
}
</style>