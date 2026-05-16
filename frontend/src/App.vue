<!-- App.vue -->
<template>
  <Layout v-if="usarLayout">
    <router-view />
  </Layout>
  <router-view v-else />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Layout from '@/components/Layout.vue'

const route     = useRoute()
const authStore = useAuthStore()

// Rutas que NUNCA usan Layout aunque el usuario esté autenticado
const rutasSinLayout = ['Landing', 'Login', 'HealthCheck', 'NotFound']

const usarLayout = computed(() =>
  authStore.isAuthenticated &&
  !rutasSinLayout.includes(route.name)
)
</script>