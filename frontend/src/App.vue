<!-- App.vue - Con botones estilizados -->
<template>
  <div id="app">

    <ToastWrapper />
    
    <!-- Contenido principal -->
    <main :class="{ 'with-navbar': showNavbar }">
      <router-view />
    </main>
    
    <!-- Footer opcional -->
    <footer class="app-footer" v-if="showNavbar">
      <p>Sistema de Gestión de Biblioteca VDJ &copy; {{ currentYear }}</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ToastWrapper from '@/components/ToastWrapper.vue'


const route = useRoute()
const authStore = useAuthStore()

// Computed properties
const showNavbar = computed(() => {
  const noNavbarRoutes = ['/login', '/register']
  return !noNavbarRoutes.includes(route.path)
})

const currentYear = new Date().getFullYear()

const shortUserName = computed(() => {
  const name = authStore.userName
  if (name.length > 15) {
    return name.substring(0, 12) + '...'
  }
  return name
})

const userRoleBadge = computed(() => {
  const role = authStore.userRoleName
  const shortRoles = {
    'Usuario Común': 'Usuario',
    'Administrador Básico': 'Admin',
    'Administrador Avanzado': 'Admin+',
    'Super Administrador': 'Super'
  }
  return shortRoles[role] || role
})

// Métodos
const handleLogout = () => {
  authStore.logout()
}
</script>

<style scoped>
/* Estilos generales */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
  background: #f8f9fa;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Barra de navegación */
.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 3px solid rgba(255, 255, 255, 0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Logo/Brand */
.nav-brand .brand-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: white;
  font-size: 1.4rem;
  font-weight: bold;
  transition: all 0.3s ease;
  padding: 0.5rem;
  border-radius: 0.5rem;
}

.nav-brand .brand-link:hover {
  transform: translateY(-2px);
  text-shadow: 0 2px 10px rgba(255, 255, 255, 0.3);
}

.brand-icon {
  font-size: 2rem;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.brand-text {
  font-size: 1.3rem;
  background: linear-gradient(to right, #ffffff, #e6e6e6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Menú de navegación */
.nav-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Estilos base para todos los botones */
.nav-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  font-weight: 600;
  font-size: 0.95rem;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.nav-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.nav-btn:hover::before {
  left: 100%;
}

.nav-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.nav-btn:active {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Botón INICIAR SESIÓN */
.nav-btn-login {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border-color: rgba(255, 255, 255, 0.3);
}

.nav-btn-login:hover {
  background: linear-gradient(135deg, #3a9bed 0%, #00d9e6 100%);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 6px 15px rgba(79, 172, 254, 0.4);
}

/* Botón REGISTRARSE */
.nav-btn-register {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
  border-color: rgba(255, 255, 255, 0.3);
}

.nav-btn-register:hover {
  background: linear-gradient(135deg, #32d46b 0%, #2ce0c6 100%);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 6px 15px rgba(67, 233, 123, 0.4);
}

/* Botón CERRAR SESIÓN */
.nav-btn-logout {
  background: linear-gradient(135deg, #ff6b6b 0%, #ffa8a8 100%);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  font-weight: 600;
}

.nav-btn-logout:hover {
  background: linear-gradient(135deg, #ff5252 0%, #ff9494 100%);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 6px 15px rgba(255, 107, 107, 0.4);
}

/* Iconos de botones */
.btn-icon {
  font-size: 1.1rem;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.2));
  transition: transform 0.3s ease;
}

.nav-btn:hover .btn-icon {
  transform: scale(1.1);
}

/* Texto de botones */
.btn-text {
  letter-spacing: 0.3px;
}

/* Menú de usuario autenticado */
.user-nav {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-greeting {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  min-width: 200px;
}

.user-icon {
  font-size: 1.2rem;
  background: rgba(255, 255, 255, 0.2);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-name {
  font-weight: 600;
  font-size: 0.95rem;
  flex-grow: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-role {
  background: rgba(255, 255, 255, 0.25);
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: bold;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Contenido principal */
main {
  flex: 1;
  padding: 1rem;
}

main.with-navbar {
  padding-top: 1.5rem;
}

/* Footer */
.app-footer {
  background: linear-gradient(135deg, #343a40 0%, #495057 100%);
  color: white;
  text-align: center;
  padding: 1.5rem;
  font-size: 0.9rem;
  margin-top: auto;
  border-top: 3px solid rgba(255, 255, 255, 0.1);
}

.app-footer p {
  opacity: 0.8;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

/* Responsive */
@media (max-width: 768px) {
  .nav-container {
    padding: 0 1rem;
    flex-direction: column;
    gap: 1rem;
  }
  
  .brand-text {
    font-size: 1.1rem;
  }
  
  .user-greeting {
    min-width: auto;
    max-width: 200px;
  }
  
  .nav-btn {
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
  }
  
  .btn-text {
    display: none;
  }
  
  .nav-btn .btn-icon {
    margin-right: 0;
    font-size: 1.2rem;
  }
}

@media (max-width: 480px) {
  .user-nav {
    flex-direction: column;
    width: 100%;
  }
  
  .user-greeting {
    width: 100%;
    justify-content: center;
  }
  
  .nav-links {
    display: flex;
    flex-direction: column;
    width: 100%;
    gap: 0.5rem;
  }
  
  .nav-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>