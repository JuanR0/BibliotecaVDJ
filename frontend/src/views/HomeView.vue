<!-- views/Home.vue -->
<template>
  <div class="home">
    <header class="hero-section">
      <div class="container">
        <h1 class="title">📚 Biblioteca Digital</h1>
        <p class="subtitle">Gestiona tu biblioteca de manera eficiente</p>
        
        <!-- Usuario NO autenticado -->
        <div class="hero-actions" v-if="!authStore.isAuthenticated">
          <button @click="$router.push('/login')" class="btn btn-primary">
            Iniciar Sesión
          </button>
          <button @click="$router.push('/register')" class="btn btn-secondary">
            Registrarse
          </button>
        </div>

        <!-- Usuario AUTENTICADO -->
        <div class="user-welcome" v-else>
          <!-- Información del Usuario -->
          <div class="user-header">
            <div class="user-avatar">👤</div>
            <div class="user-info">
              <h2>¡Bienvenido, {{ authStore.userName }}!</h2>
              <div class="user-badge" :class="roleClass">
                {{ authStore.userRoleName }}
              </div>
              <p class="user-code">Código: {{ authStore.userCode }}</p>
            </div>
          </div>

          <!-- Permisos del Usuario -->
          <div class="permisos-section">
            <h3>🎯 Tus Permisos</h3>
            <div class="permisos-grid">
              <div class="permiso-card" v-if="authStore.canViewBooks">
                <span class="permiso-icon">📖</span>
                <div>
                  <h4>Ver Libros</h4>
                  <p>Acceso al catálogo completo</p>
                </div>
              </div>
              
              <div class="permiso-card" v-if="authStore.canBorrowBooks">
                <span class="permiso-icon">⏰</span>
                <div>
                  <h4>Prestar Libros</h4>
                  <p>Solicitar préstamos de libros</p>
                </div>
              </div>
              
              <div class="permiso-card" v-if="authStore.canManageUsers">
                <span class="permiso-icon">👥</span>
                <div>
                  <h4>Gestionar Usuarios</h4>
                  <p>Administrar usuarios del sistema</p>
                </div>
              </div>
              
              <div class="permiso-card" v-if="authStore.canManageBooks">
                <span class="permiso-icon">📚</span>
                <div>
                  <h4>Gestionar Libros</h4>
                  <p>Agregar y modificar libros</p>
                </div>
              </div>
              
              <div class="permiso-card" v-if="authStore.canViewReports">
                <span class="permiso-icon">📊</span>
                <div>
                  <h4>Ver Reportes</h4>
                  <p>Acceso a estadísticas y reportes</p>
                </div>
              </div>
              
              <div class="permiso-card" v-if="authStore.canManageSystem">
                <span class="permiso-icon">⚙️</span>
                <div>
                  <h4>Gestionar Sistema</h4>
                  <p>Configuración del sistema</p>
                </div>
              </div>
              
              <div v-if="!hasPermisos" class="permiso-card empty">
                <span class="permiso-icon">🔒</span>
                <div>
                  <h4>Permisos Limitados</h4>
                  <p>Contacta al administrador para más permisos</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Acciones Rápidas -->
          <div class="quick-actions-section">
            <h3>🚀 Acciones Rápidas</h3>
            <div class="quick-actions">
              <button 
                v-if="authStore.canViewBooks"
                class="btn btn-outline" 
                @click="$router.push('/catalog')"
              >
                🔍 Explorar Catálogo
              </button>
              
              <button 
                v-if="authStore.canBorrowBooks"
                class="btn btn-outline" 
                @click="$router.push('/my-loans')"
              >
                📖 Mis Préstamos
              </button>
              
              <button 
                v-if="authStore.canManageUsers"
                class="btn btn-outline" 
                @click="$router.push('/admin/users')"
              >
                👥 Gestionar Usuarios
              </button>
              
              <button 
                v-if="authStore.canManageBooks"
                class="btn btn-outline" 
                @click="$router.push('/admin/books')"
              >
                📚 Gestionar Libros
              </button>
              
              <button 
                v-if="authStore.canViewReports"
                class="btn btn-outline" 
                @click="$router.push('/admin/reports')"
              >
                📊 Ver Reportes
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Sección de Características -->
    <main class="features-section" v-if="!authStore.isAuthenticated">
      <div class="container">
        <h2>Características Principales</h2>
        <div class="features-grid">
          <div class="feature-card">
            <h3>📖 Catálogo Digital</h3>
            <p>Accede a miles de libros organizados por categorías</p>
          </div>
          <div class="feature-card">
            <h3>⏰ Sistema de Préstamos</h3>
            <p>Gestiona préstamos y reservas de manera eficiente</p>
          </div>
          <div class="feature-card">
            <h3>📊 Reportes Avanzados</h3>
            <p>Genera reportes y estadísticas de uso</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ref, computed, onMounted } from 'vue'

const authStore = useAuthStore()
const router = useRouter()
const isLoading = ref(false)

const hasPermisos = computed(() => {
  return authStore.canViewBooks || 
         authStore.canBorrowBooks || 
         authStore.canManageUsers ||
         authStore.canManageBooks ||
         authStore.canViewReports ||
         authStore.canManageSystem
})

const roleClass = computed(() => {
  const classes = {
    1: 'role-user',
    2: 'role-admin',
    3: 'role-advanced',
    4: 'role-super'
  }
  return classes[authStore.userRole] || 'role-user'
})

const handleLogout = async () => {
  try {
    authStore.logout()
    router.push('/')
  } catch (error) {
    console.error('Error al cerrar sesión:', error)
  }
}

// Cargar información del usuario al montar si está autenticado
onMounted(async () => {
  if (authStore.isAuthenticated) {
    try {
      isLoading.value = true
      await authStore.getCurrentUser()
    } catch (error) {
      console.error('Error cargando información del usuario:', error)
    } finally {
      isLoading.value = false
    }
  }
})
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem 0;
  text-align: center;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.title {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

/* Sección de Usuario Autenticado */
.user-welcome {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 2rem;
  margin: 2rem auto;
  max-width: 800px;
  text-align: left;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.user-avatar {
  font-size: 3rem;
  background: rgba(255, 255, 255, 0.2);
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-info h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
}

.user-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.user-badge.role-user {
  background: #17a2b8;
  color: white;
}

.user-badge.role-admin {
  background: #28a745;
  color: white;
}

.user-badge.role-advanced {
  background: #ffc107;
  color: #333;
}

.user-badge.role-super {
  background: #dc3545;
  color: white;
}

.user-code {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
}

/* Sección de Permisos */
.permisos-section {
  margin-bottom: 2rem;
}

.permisos-section h3 {
  margin-bottom: 1rem;
  font-size: 1.25rem;
  color: white;
}

.permisos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.permiso-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.3s ease, background 0.3s ease;
}

.permiso-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.2);
}

.permiso-card.empty {
  opacity: 0.7;
}

.permiso-icon {
  font-size: 1.5rem;
}

.permiso-card h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  color: white;
}

.permiso-card p {
  margin: 0;
  font-size: 0.8rem;
  opacity: 0.8;
}

/* Sección de Acciones Rápidas */
.quick-actions-section {
  padding-top: 1.5rem;
  border-top: 2px solid rgba(255, 255, 255, 0.2);
}

.quick-actions-section h3 {
  margin-bottom: 1rem;
  font-size: 1.25rem;
  color: white;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
}

/* Botones */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary {
  background: #ff6b6b;
  color: white;
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.btn-outline {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.btn-danger {
  background: #dc3545;
  color: white;
  border: none;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Sección de Características (para no autenticados) */
.features-section {
  padding: 4rem 0;
  background: #f8f9fa;
}

.features-section h2 {
  text-align: center;
  margin-bottom: 3rem;
  color: #333;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.feature-card h3 {
  margin-bottom: 1rem;
  color: #333;
}

/* Responsive */
@media (max-width: 768px) {
  .title {
    font-size: 2rem;
  }
  
  .user-header {
    flex-direction: column;
    text-align: center;
  }
  
  .quick-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>