<!-- views/admin/BookManagementView.vue -->
<template>
  <div class="book-management-view">
    <!-- Tabs -->
    <div class="tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="{ 'active': activeTab === tab.id }"
        class="tab-btn"
      >
        {{ tab.icon }} {{ tab.name }}
      </button>
    </div>

    <!-- Contenido de pestañas -->
    <div class="tab-content">
      <!-- Gestión de Libros -->
      <div v-if="activeTab === 'books'">
        <h2>📚 Gestión de Libros</h2>
        <button @click="showAddBookModal = true" class="btn btn-primary">
          ➕ Agregar Nuevo Libro
        </button>
        <!-- Lista de libros con opciones editar/eliminar -->
      </div>

      <!-- Gestión de Áreas -->
      <div v-if="activeTab === 'areas'">
        <h2>📍 Áreas de Préstamo</h2>
        <!-- CRUD de áreas -->
      </div>

      <!-- Categorías -->
      <div v-if="activeTab === 'categories'">
        <h2>🏷️ Categorías y Géneros</h2>
        <!-- CRUD de categorías -->
      </div>
    </div>

    <!-- Modal para agregar libro -->
    <div v-if="showAddBookModal" class="modal-overlay">
      <div class="modal-content">
        <h3>📖 Agregar Nuevo Libro</h3>
        <form @submit.prevent="submitNewBook">
          <!-- Formulario de libro -->
        </form>
      </div>
    </div>
  </div>
</template>