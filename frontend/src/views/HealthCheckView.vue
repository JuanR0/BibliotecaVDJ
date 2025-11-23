<!-- views/HealthCheck.vue -->
<template>
  <div class="healthcheck">
    <h1>🔍 Health Check</h1>
    <div class="status" :class="status">
      {{ message }}
    </div>
    <button @click="testBackend">Probar Backend</button>
    <button @click="$router.push('/')">Volver al Home</button>
  </div>
</template>

<script>
export default {
  name: 'HealthCheck',
  data() {
    return {
      status: 'loading',
      message: 'Cargando...'
    }
  },
  methods: {
    async testBackend() {
      this.status = 'testing'
      this.message = 'Probando conexión...'
      
      try {
        const response = await fetch('http://localhost:8000/api/health')
        const data = await response.json()
        this.status = 'success'
        this.message = `✅ Backend conectado: ${data.status}`
      } catch (error) {
        this.status = 'error'
        this.message = '❌ Error conectando al backend'
        console.error('Error:', error)
      }
    }
  },
  mounted() {
    this.testBackend()
  }
}
</script>

<style scoped>
.healthcheck {
  padding: 2rem;
  text-align: center;
}

.status {
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 0.5rem;
}

.status.loading {
  background: #fff3cd;
  color: #856404;
}

.status.success {
  background: #d1edff;
  color: #155724;
}

.status.error {
  background: #f8d7da;
  color: #721c24;
}

.status.testing {
  background: #fff3cd;
  color: #856404;
}

button {
  margin: 0 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}
</style>