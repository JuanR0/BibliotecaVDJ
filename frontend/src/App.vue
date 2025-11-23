<template>
  <div id="app">
    <!-- Barra de Navegación -->
    <nav class="navbar">
      <div class="nav-container">
        <h1 class="logo">📚 Biblioteca</h1>
        <div class="nav-links">
          <router-link to="/" class="nav-link">Inicio</router-link>
          <router-link to="/login" class="nav-link">Login</router-link>
          <router-link to="/healthcheck" class="nav-link">Estado</router-link>
        </div>
      </div>
    </nav>

    <!-- Contenido Principal -->
    <main class="main-content">
      <router-view></router-view>
    </main>

    <!-- Pie de Página -->
    <footer class="footer">
      <p>&copy; 2024 Sistema de Biblioteca. Todos los derechos reservados.</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #f5f5f5;
  color: #333;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Barra de Navegación */
.navbar {
  background: linear-gradient(135deg, #2c3e50, #34495e);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
}

.logo {
  font-size: 1.8rem;
  font-weight: bold;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(255,255,255,0.1);
  transform: translateY(-2px);
}

.nav-link.router-link-active {
  background: #42b883;
  color: white;
}

/* Contenido Principal */
.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* Pie de Página */
.footer {
  background: #2c3e50;
  color: white;
  text-align: center;
  padding: 1.5rem;
  margin-top: auto;
}

/* Responsive */
@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav-links {
    gap: 1rem;
  }
  
  .main-content {
    padding: 1rem;
  }
}
</style>