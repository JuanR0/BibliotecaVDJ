<!-- src/views/admin/BookEdit.vue -->
<template>
  <div class="book-edit-container">
    <!-- Header -->
    <div class="edit-header">
      <h1>✏️ Editar Libro</h1>
      <button @click="goBack" class="btn-back">
        ← Volver al Catálogo
      </button>
    </div>

    <!-- Contenido -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando información del libro...</p>
    </div>

    <div v-if="error" class="error-state">
      <p>❌ Error: {{ error }}</p>
      <button @click="fetchBook" class="btn btn-primary">Reintentar</button>
    </div>

    <!-- Formulario -->
    <form v-if="book && !loading" @submit.prevent="submitForm" class="book-edit-form">
      <div class="form-section">
        <h2>📋 Información Básica</h2>
        
        <div class="form-group">
          <label for="titulo">Título *</label>
          <input
            v-model="form.titulo"
            type="text"
            id="titulo"
            required
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="autor">Autor *</label>
          <input
            v-model="form.autor"
            type="text"
            id="autor"
            required
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="isbn">ISBN</label>
          <input
            v-model="form.isbn"
            type="text"
            id="isbn"
            class="form-input"
          />
        </div>
      </div>

      <div class="form-section">
        <h2>📖 Detalles</h2>
        
        <div class="form-row">
          <div class="form-group">
            <label for="edicion">Edición</label>
            <input
              v-model="form.edicion"
              type="number"
              id="edicion"
              min="1"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="numero_paginas">Número de páginas</label>
            <input
              v-model="form.numero_paginas"
              type="number"
              id="numero_paginas"
              min="1"
              class="form-input"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="editorial_id">Editorial</label>
          <select v-model="form.editorial_id" id="editorial_id" class="form-select">
            <option value="">Seleccionar editorial</option>
            <option v-for="editorial in editoriales" :key="editorial.id" :value="editorial.id">
              {{ editorial.nombre }}
            </option>
          </select>
        </div>
      </div>

      <div class="form-section">
        <h2>💰 Información de Adquisición</h2>
        
        <div class="form-group">
          <label for="metodo_adquisicion_id">Método de adquisición</label>
          <select v-model="form.metodo_adquisicion_id" id="metodo_adquisicion_id" class="form-select">
            <option value="">Seleccionar método</option>
            <option value="1">Compra</option>
            <option value="2">Donación</option>
            <option value="3">Canje</option>
          </select>
        </div>

        <div class="form-group">
          <label for="proveedor_nombre">Proveedor</label>
          <input
            v-model="form.proveedor_nombre"
            type="text"
            id="proveedor_nombre"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="precio">Precio ($)</label>
          <input
            v-model="form.precio"
            type="number"
            id="precio"
            step="0.01"
            min="0"
            class="form-input"
          />
        </div>
      </div>

      <div class="form-section">
        <h2>⚙️ Estado y Disponibilidad</h2>
        
        <div class="form-row">
          <div class="form-group">
            <label for="estado_id">Estado</label>
            <select v-model="form.estado_id" id="estado_id" class="form-select">
              <option value="1">Disponible</option>
              <option value="2">Prestado</option>
              <option value="3">En reparación</option>
              <option value="4">Extraviado</option>
            </select>
          </div>

          <div class="form-group">
            <label for="es_prestable">¿Es prestable?</label>
            <select v-model="form.es_prestable" id="es_prestable" class="form-select">
              <option :value="true">Sí</option>
              <option :value="false">No</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Información de solo lectura -->
      <div class="form-section readonly">
        <h2>🏷️ Información de Identificación (Solo lectura)</h2>
        
        <div class="form-row">
          <div class="form-group">
            <label>Código Decimal</label>
            <input
              :value="book.codigo_decimal"
              type="text"
              class="form-input readonly"
              readonly
            />
          </div>

          <div class="form-group">
            <label>Etiqueta</label>
            <input
              :value="book.etiqueta"
              type="text"
              class="form-input readonly"
              readonly
            />
          </div>

          <div class="form-group">
            <label>Número de Ejemplar</label>
            <input
              :value="book.numero_ejemplar"
              type="text"
              class="form-input readonly"
              readonly
            />
          </div>
        </div>
      </div>

      <!-- Botones de acción -->
      <div class="form-actions">
        <button type="button" @click="goBack" class="btn btn-secondary">
          Cancelar
        </button>
        
        <button type="submit" :disabled="isSubmitting" class="btn btn-primary">
          <span v-if="isSubmitting" class="spinner-small"></span>
          {{ isSubmitting ? 'Guardando...' : 'Guardar Cambios' }}
        </button>
        
        <button type="button" @click="resetForm" class="btn btn-outline">
          Restablecer
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { bookService } from '@/services/books'

const route = useRoute()
const router = useRouter()

// Estado
const book = ref(null)
const loading = ref(true)
const error = ref(null)
const isSubmitting = ref(false)
const editoriales = ref([])

// Formulario
const form = reactive({
  isbn: '',
  titulo: '',
  autor: '',
  editorial_id: '',
  edicion: '',
  numero_paginas: '',
  metodo_adquisicion_id: '',
  proveedor_nombre: '',
  precio: '',
  es_prestable: true,
  estado_id: '1'
})

// Métodos
const fetchBook = async () => {
  const bookId = route.params.id
  loading.value = true
  error.value = null
  
  try {
    // Obtener libro por ID
    const data = await bookService.getBookById(bookId)
    book.value = data
    
    // Llenar formulario
    Object.keys(form).forEach(key => {
      if (data[key] !== undefined && data[key] !== null) {
        form[key] = data[key]
      }
    })
    
    console.log('Libro cargado:', data)
    
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error cargando el libro'
    console.error('Error:', err)
  } finally {
    loading.value = false
  }
}

const submitForm = async () => {
  isSubmitting.value = true
  
  try {
    const bookId = route.params.id
    const bookData = {
      isbn: form.isbn || null,
      titulo: form.titulo,
      autor: form.autor,
      editorial_id: parseInt(form.editorial_id),
      edicion: form.edicion ? parseInt(form.edicion) : null,
      numero_paginas: form.numero_paginas ? parseInt(form.numero_paginas) : null,
      metodo_adquisicion_id: parseInt(form.metodo_adquisicion_id),
      proveedor_nombre: form.proveedor_nombre || null,
      precio: form.precio ? parseFloat(form.precio) : 0,
      es_prestable: form.es_prestable,
      estado_id: parseInt(form.estado_id)
    }
    
    // Actualizar libro
    await bookService.updateBook(bookId, bookData)
    
    // Mostrar éxito y regresar
    alert('✅ Libro actualizado correctamente')
    router.push('/catalog')
    
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error actualizando el libro'
    console.error('Error:', err)
    alert('❌ Error al actualizar el libro')
  } finally {
    isSubmitting.value = false
  }
}

const resetForm = () => {
  if (book.value) {
    Object.keys(form).forEach(key => {
      if (book.value[key] !== undefined) {
        form[key] = book.value[key]
      }
    })
  }
}

const goBack = () => {
  router.push('/catalog')
}

// Ciclo de vida
onMounted(() => {
  fetchBook()
})
</script>

<style scoped>
.book-edit-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0e0e0;
}

.edit-header h1 {
  font-size: 2rem;
  color: #333;
  margin: 0;
}

.btn-back {
  background: none;
  border: none;
  color: #667eea;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.5rem;
}

.btn-back:hover {
  text-decoration: underline;
}

/* Estados */
.loading-state, .error-state {
  text-align: center;
  padding: 3rem;
  background: #f8f9fa;
  border-radius: 10px;
  margin: 2rem 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e0e0e0;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  background: #ffeaea;
  color: #c53030;
}

/* Formulario */
.book-edit-form {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.form-section {
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.form-section h2 {
  font-size: 1.3rem;
  color: #444;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #667eea;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #555;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.form-input, .form-select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-input:focus, .form-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input.readonly, .form-section.readonly .form-input {
  background: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
  border-color: #e9ecef;
}

/* Botones */
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 1rem;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5a6fd8;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-outline {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-outline:hover {
  background: #667eea;
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.spinner-small {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .book-edit-container {
    padding: 1rem;
  }
  
  .edit-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>