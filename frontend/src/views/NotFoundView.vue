<template>
  <div class="not-found">
    <div class="container">
      <h1>404</h1>
      <h2>Página no encontrada</h2>
      <p>La página que buscas no existe o no tienes permisos para acceder.</p>
      <router-link to="/" class="btn btn-primary">
        ← Volver al Inicio
      </router-link>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  text-align: center;
  padding: 2rem;
}

.container {
  max-width: 500px;
}

h1 {
  font-size: 6rem;
  color: #dc3545;
  margin: 0;
  line-height: 1;
}

h2 {
  margin: 1rem 0;
  color: #333;
}

p {
  color: #666;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

.btn {
  padding: 0.75rem 2rem;
  font-size: 1rem;
}
</style>