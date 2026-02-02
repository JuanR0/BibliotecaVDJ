<template>
  <div class="layout">
    <!-- Sidebar -->
    <Sidebar />
    
    <!-- Contenido principal -->
    <main :class="['main-content', { 'sidebar-collapsed': isCollapsed }]">
      <!-- Header móvil -->
      <header class="mobile-header">
        <button class="menu-toggle" @click="toggleMobileSidebar">
          ☰
        </button>
        <div class="mobile-title">
          {{ currentPageTitle }}
        </div>
        <div class="mobile-user" v-if="auth.user">
          {{ getUserInitials(auth.userName) }}
        </div>
      </header>
      
      <!-- Contenido de la vista -->
      <div class="content-wrapper">
        <slot></slot>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Sidebar from './Sidebar.vue'

const auth = useAuthStore()
const route = useRoute()
const mobileSidebarOpen = ref(false)

// Computed para detectar si sidebar está colapsado
const isCollapsed = computed(() => {
  const savedState = localStorage.getItem('sidebarCollapsed')
  return savedState ? JSON.parse(savedState) : false
})

// Título de página actual
const currentPageTitle = computed(() => {
  return route.meta.title || getTitleFromRoute(route.name)
})

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

const getTitleFromRoute = (routeName) => {
  const titles = {
    'BookCatalog': 'Catálogo de Libros',
    'UserMenu': 'Mi Perfil',
    'EditarLibro': 'Editar Libro',
    'CrearLibro': 'Crear Nuevo Libro',
    'GestionLibros': 'Gestión de Libros',
    'Home': 'Inicio',
    'Login': 'Iniciar Sesión',
    'Register': 'Registro',
    'HealthCheck': 'Estado del Sistema'
  }
  return titles[routeName] || 'Biblioteca Virtual'
}

// Toggle sidebar en móvil
const toggleMobileSidebar = () => {
  mobileSidebarOpen.value = !mobileSidebarOpen.value
  const sidebar = document.querySelector('.sidebar')
  if (sidebar) {
    sidebar.classList.toggle('collapsed', !mobileSidebarOpen.value)
  }
}

// Cerrar sidebar en móvil al cambiar de ruta
watch(() => route.path, () => {
  if (window.innerWidth < 768) {
    mobileSidebarOpen.value = false
    const sidebar = document.querySelector('.sidebar')
    if (sidebar) {
      sidebar.classList.add('collapsed')
    }
  }
})
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background: #f8fafc;
}

.main-content {
  flex: 1;
  margin-left: 250px;
  transition: margin-left 0.3s ease;
  min-height: 100vh;
}

.main-content.sidebar-collapsed {
  margin-left: 70px;
}

/* Header móvil */
.mobile-header {
  display: none;
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}

.menu-toggle {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #4b5563;
  padding: 8px;
  border-radius: 6px;
}

.menu-toggle:hover {
  background: #f3f4f6;
}

.mobile-title {
  flex: 1;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  text-align: center;
  margin: 0 16px;
}

.mobile-user {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 12px;
}

/* Contenido */
.content-wrapper {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* Responsive */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0 !important;
  }
  
  .mobile-header {
    display: flex;
  }
  
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .main-content {
    margin-left: 70px;
  }
}
</style>