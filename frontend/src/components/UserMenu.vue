<!-- components/UserMenu.vue - VERSIÓN SIMPLIFICADA -->
<template>
  <div class="user-menu">
    <div class="user-info" @click="toggleMenu">
      <span class="user-avatar">👤</span>
      <span class="user-name">{{ authStore.userName }}</span>
      <span class="menu-icon">{{ isMenuOpen ? '▲' : '▼' }}</span>
    </div>
    
    <div v-if="isMenuOpen" class="dropdown-menu">
      <router-link to="/profile" class="menu-item">👤 Mi Perfil</router-link>
      <router-link to="/settings" class="menu-item">⚙️ Configuración</router-link>
      <button @click="logout" class="menu-item logout-btn">🚪 Cerrar Sesión</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const isMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const logout = () => {
  authStore.logout()
  router.push('/')
}

// Cerrar menú al hacer clic fuera
import { onMounted, onUnmounted } from 'vue'

const handleClickOutside = (event) => {
  if (!event.target.closest('.user-menu')) {
    isMenuOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<style scoped>
.user-menu {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  cursor: pointer;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.2);
}

.user-avatar {
  font-size: 1.2rem;
}

.user-name {
  color: white;
  font-weight: 500;
}

.menu-icon {
  font-size: 0.8rem;
  color: white;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  min-width: 180px;
  margin-top: 0.5rem;
  overflow: hidden;
  z-index: 1000;
}

.menu-item {
  display: block;
  padding: 0.75rem 1rem;
  text-decoration: none;
  color: #333;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: background 0.2s;
}

.menu-item:hover {
  background: #f8f9fa;
}

.menu-item.logout-btn {
  color: #dc3545;
  border-top: 1px solid #eee;
}

.menu-item.logout-btn:hover {
  background: #f8d7da;
}
</style>