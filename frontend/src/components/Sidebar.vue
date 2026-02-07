<template>
  <aside :class="['sidebar', { 'collapsed': collapsed }]">
    <!-- Logo y toggle -->
    <div class="sidebar-header">
      <div class="logo" @click="toggleCollapse">
        <span v-if="!collapsed" class="logo-text">📚 BiblioVDJ</span>
        <span v-else class="logo-icon">📚</span>
      </div>
      <button class="toggle-btn" @click="toggleCollapse">
        {{ collapsed ? '→' : '←' }}
      </button>
    </div>

    <!-- Perfil del usuario -->
    <div v-if="auth.user" class="user-profile">
      <div class="avatar">
        {{ getUserInitials(auth.userName) }}
      </div>
      <div v-if="!collapsed" class="user-info">
        <div class="user-name">{{ auth.userName }}</div>
        <div class="user-role">{{ getUserRoleName(auth.tipoUsuarioId) }}</div>
      </div>
    </div>

    <!-- Menú de navegación -->
    <nav class="sidebar-nav">
      <ul>
        <li v-if="auth.isAuthenticated">
          <router-link to="/user/menu" class="nav-link" active-class="active">
            <span class="nav-icon">👤</span>
            <span v-if="!collapsed" class="nav-text">Mi Perfil</span>
          </router-link>
        </li>

        <!-- ADMINISTRACION (RECURSOS ADMINISTRATIVOS) -->
        <li v-if="auth.esCualquierAdmin" class="nav-section">
          <span v-if="!collapsed" class="section-label">Administración</span>
          <span v-else class="section-icon">⚙️</span>
        </li>

        <li v-if="auth.isAuthenticated">
          <router-link to="/admin/libros" class="nav-link" active-class="active">
            <span class="nav-icon">📚</span>
            <span v-if="!collapsed" class="nav-text">Catálogo</span>
          </router-link>
        </li>

        <!-- RUTAS A LISTADOS -->
        <li v-if="auth.puedeGestionarUsuarios">
          <router-link to="/admin/usuarios" class="nav-link" active-class="active">
            <span class="nav-icon">👥</span>
            <span v-if="!collapsed" class="nav-text">Usuarios</span>
          </router-link>
        </li>

        <li v-if="auth.esAdminAvanzado || auth.esSuperAdmin">
          <router-link to="/admin/mobiliario" class="nav-link">
            <span class="nav-icon">🪑</span>
            <span class="nav-text">Mobiliario</span>
          </router-link>
        </li>

        <li v-if="auth.puedeVerAreas">
          <router-link to="/admin/areas" class="nav-link" :class="{ 'active': isAreasActive }">
            <span class="nav-icon">🏢</span>
            <span v-if="!collapsed" class="nav-text">Gestión de Áreas</span>
          </router-link>
        </li>

        <li v-if="auth.esCualquierAdmin">
          <router-link to="/admin/prestamos" class="nav-link" active-class="active">
            <span class="nav-icon">🔄</span>
            <span v-if="!collapsed" class="nav-text">Préstamos</span>
            <span v-if="!collapsed" class="badge upcoming">Próximo</span>
          </router-link>
        </li>

        <li v-if="auth.esCualquierAdmin">
          <router-link to="/admin/multas" class="nav-link" active-class="active">
            <span class="nav-icon">⚠️</span>
            <span v-if="!collapsed" class="nav-text">Multas</span>
            <span v-if="!collapsed" class="badge upcoming">Próximo</span>
          </router-link>
        </li>

        <!-- RUTAS A CREACION -->
        <li v-if="auth.puedeGestionarRecursos" class="nav-section">
          <span v-if="!collapsed" class="section-label">Administracion libros</span>
          <span v-else class="section-icon">📖</span>
        </li>

        <li v-if="auth.puedeGestionarRecursos">
          <router-link to="/admin/libros/crear" class="nav-link" active-class="active">
            <span class="nav-icon">➕</span>
            <span v-if="!collapsed" class="nav-text">Nuevo Libro</span>
          </router-link>
        </li>
        
        <li v-if="auth.puedeGestionarRecursos" class="nav-section">
          <span v-if="!collapsed" class="section-label">Administracion libros</span>
          <span v-else class="section-icon">👤</span>
        </li>

        <li v-if="auth.puedeGestionarRecursos">
          <router-link to="/admin/usuarios/crear" class="nav-link" active-class="active">
            <span class="nav-icon">➕</span>
            <span v-if="!collapsed" class="nav-text">Nuevo usuario</span>
          </router-link>
        </li>

        <li v-if="auth.puedeGestionarRecursos" class="nav-section">
          <span v-if="!collapsed" class="section-label">Administracion Muebles</span>
          <span v-else class="section-icon">🪑</span>
        </li>

        <li v-if="auth.puedeGestionarRecursos">
          <router-link to="/admin/mobiliario/crear" class="nav-link" active-class="active">
            <span class="nav-icon">➕</span>
            <span v-if="!collapsed" class="nav-text">Nuevo muebles</span>
          </router-link>
        </li>


        <!-- GENERAL -->
        <li class="nav-section">
          <span v-if="!collapsed" class="section-label">General</span>
          <span v-else class="section-icon">🌐</span>
        </li>

        <!-- Rutas públicas -->
        <li>
          <router-link to="/" class="nav-link" active-class="active">
            <span class="nav-icon">🏠</span>
            <span v-if="!collapsed" class="nav-text">Inicio</span>
          </router-link>
        </li>

        <!-- Estado del sistema -->
        <li>
          <router-link to="/Health" class="nav-link" active-class="active">
            <span class="nav-icon">🟢</span>
            <span v-if="!collapsed" class="nav-text">Estado</span>
          </router-link>
        </li>

        <!-- Cerrar sesión -->
        <li v-if="auth.isAuthenticated" class="logout-item">
          <a href="#" class="nav-link" @click.prevent="logout">
            <span class="nav-icon">🚪</span>
            <span v-if="!collapsed" class="nav-text">Cerrar Sesión</span>
          </a>
        </li>
      </ul>
    </nav>

    <!-- Footer de la sidebar -->
    <div v-if="!collapsed" class="sidebar-footer">
      <div class="system-info">
        <div class="version">v1.0.0</div>
        <div class="user-count" v-if="auth.esCualquierAdmin">
          <span class="online-dot"></span>
          Usuarios activos
        </div>
      </div>
    </div>
  </aside>
</template>



<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const collapsed = ref(false)

// Persistir estado en localStorage
onMounted(() => {
  const savedState = localStorage.getItem('sidebarCollapsed')
  if (savedState !== null) {
    collapsed.value = JSON.parse(savedState)
  }
})

watch(collapsed, (newVal) => {
  localStorage.setItem('sidebarCollapsed', JSON.stringify(newVal))
})

// Toggle colapso
const toggleCollapse = () => {
  collapsed.value = !collapsed.value
}

// Helper functions
const getUserInitials = (name) => {
  if (!name) return 'US'
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .substring(0, 2)
}

const isAreasActive = computed(() => {
  return route.path.startsWith('/admin/areas')
})

const getUserRoleName = (tipoId) => {
  const roles = {
    1: 'Usuario Común',
    2: 'Admin Básico',
    3: 'Admin Avanzado',
    4: 'Super Admin'
  }
  return roles[tipoId] || 'Usuario'
}

// Logout
const logout = () => {
  auth.logout()
  router.push('/login')
}

// Cerrar sidebar en móvil al hacer clic en un enlace
const handleNavClick = () => {
  if (window.innerWidth < 768) {
    collapsed.value = true
  }
}



</script>

<style scoped>
.sidebar {
  width: 250px;
  height: 100vh;
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  color: white;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar.collapsed {
  width: 70px;
}

/* Header */
.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: #60a5fa;
}

.logo-icon {
  font-size: 2rem;
}

.toggle-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.toggle-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* User Profile */
.user-profile {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.user-info {
  overflow: hidden;
  transition: opacity 0.3s;
}

.sidebar.collapsed .user-info {
  opacity: 0;
  width: 0;
}

.user-name {
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 12px;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  padding: 20px 0;
  overflow-y: auto;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 10;
}

.sidebar-nav li {
  margin: 4px 12px;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  color: #cbd5e1;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s;
  position: relative;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-link.active {
  background: rgba(59, 130, 246, 0.2);
  color: white;
  border-left: 3px solid #3b82f6;
}

.nav-icon {
  font-size: 18px;
  width: 24px;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

.nav-text {
  margin-left: 12px;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.sidebar.collapsed .nav-text {
  opacity: 0;
  width: 0;
  margin-left: 0;
}

/* Badges */
.badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 600;
  margin-left: auto;
}

.badge.upcoming {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
}

/* Sections */
.nav-section {
  padding: 16px 16px 8px;
  color: #64748b;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-label {
  white-space: nowrap;
}

.section-icon {
  display: block;
  text-align: center;
  font-size: 16px;
}

.sidebar.collapsed .nav-section {
  padding: 16px 0;
  text-align: center;
}

/* Logout item */
.logout-item .nav-link {
  color: #f87171;
}

.logout-item .nav-link:hover {
  background: rgba(248, 113, 113, 0.1);
}

/* Footer */
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 11px;
  color: #64748b;
}

.system-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.version {
  font-family: monospace;
}

.user-count {
  display: flex;
  align-items: center;
  gap: 6px;
}

.online-dot {
  width: 6px;
  height: 6px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    width: 280px;
  }
  
  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .sidebar.collapsed {
    transform: translateX(-100%);
    width: 280px;
  }
  
  .toggle-btn {
    display: none;
  }
}

/* Scrollbar personalizado */
.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>