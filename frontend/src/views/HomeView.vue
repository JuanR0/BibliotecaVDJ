<template>
  <div class="home">
    <h1>Library Management System</h1>
    <p>{{ message }}</p>
    <p v-if="loading">Loading...</p>
    <p v-else>Frontend is working! 🎉</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: '',
      loading: true
    }
  },
  async mounted() {
    try {
      const response = await fetch('http://localhost:8000/api/health')
      const data = await response.json()
      this.message = `Backend status: ${data.status}`
    } catch (error) {
      this.message = 'Failed to connect to backend'
    } finally {
      this.loading = false
    }
  }
}
</script>