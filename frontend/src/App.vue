<!-- App.vue -->
<template>
  <Layout v-if="usarLayout">
    <router-view />
  </Layout>
  <router-view v-else />

  <!-- Chat persistente — visible en Landing y vistas de estudiante (nivel 1) -->
  <ChatWidget v-if="mostrarChat" />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Layout from '@/components/Layout.vue'
import ChatWidget from '@/components/ChatWidget.vue'

const route     = useRoute()
const authStore = useAuthStore()

// Rutas que NUNCA usan Layout aunque el usuario esté autenticado
const rutasSinLayout = ['Landing', 'Login', 'HealthCheck', 'NotFound']

const usarLayout = computed(() =>
  authStore.isAuthenticated &&
  !rutasSinLayout.includes(route.name)
)

// Rutas donde el chat es visible
const rutasConChat = [
  'Landing',       // pública
  'BookCatalog',   // catálogo de libros
  'AreasEstudio',  // cubículos
  'LaptopsView',   // laptops
  'MisMultas',     // mis multas
  'UserMenu',      // mi perfil
]

const mostrarChat = computed(() => {
  // En Landing siempre visible (usuario no autenticado)
  if (route.name === 'Landing') return true

  // En vistas de estudiante solo si está autenticado y es nivel 1
  return (
    authStore.isAuthenticated &&
    rutasConChat.includes(route.name)
  )
})
</script>