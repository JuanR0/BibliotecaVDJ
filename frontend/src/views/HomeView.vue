<!-- views/HomeView.vue -->
<template>
  <div class="home">
    <header class="hero-section">
      <div class="container">
        <h1 class="title">📚 Biblioteca Digital</h1>
        <p class="subtitle">Gestiona tu biblioteca de manera eficiente</p>
        
        <div class="hero-actions" v-if="!authStore.isAuthenticated">
          <button @click="$router.push('/login')" class="btn btn-primary">
            Iniciar Sesión
          </button>
          <button @click="router.push('/register')" class="btn btn-secondary">
            Registrarse
          </button>
        </div>

        <div class="user-welcome" v-else>
          <h2>¡Bienvenido, {{ authStore.userName }}! 👋</h2>
          <p>¿Qué te gustaría hacer hoy?</p>
          <div class="quick-actions">
            <button class="btn btn-outline" @click="$router.push('/catalog')">
              🔍 Explorar Catálogo
            </button>
            <button class="btn btn-outline" @click="$router.push('/my-loans')">
              📖 Mis Préstamos
            </button>
            <button class="btn btn-danger" @click="handleLogout">
              🚪 Cerrar Sesión
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="features-section">
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const showRegister = ref(false)

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4rem 0;
  text-align: center;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.title {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.5rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.hero-actions, .quick-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
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

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

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
</style>