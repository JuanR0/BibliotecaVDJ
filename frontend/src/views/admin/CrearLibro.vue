<!-- src/views/admin/CrearLibro.vue -->
<template>
  <div class="crear-libro-container">
    <!-- Header -->
    <div class="create-header">
      <div class="header-content">
        <button @click="goBack" class="btn-back">
          ← Volver al Catálogo
        </button>
        <h1>➕ Agregar Nuevo Libro</h1>
        <p class="subtitle">Complete todos los campos para registrar un nuevo libro en la biblioteca</p>
      </div>
      
      <div class="header-steps">
        <div class="step-indicator active">
          <span class="step-number">1</span>
          <span class="step-label">Información Básica</span>
        </div>
        <div class="step-indicator">
          <span class="step-number">2</span>
          <span class="step-label">Detalles del Libro</span>
        </div>
        <div class="step-indicator">
          <span class="step-number">3</span>
          <span class="step-label">Revisar y Crear</span>
        </div>
      </div>
    </div>

    <!-- Formulario -->
    <form @submit.prevent="submitForm" class="create-book-form">
      
      <!-- SECCIÓN 1: INFORMACIÓN DE IDENTIFICACIÓN -->
      <div class="form-section">
        <div class="section-header">
          <h2>🏷️ Información de Identificación</h2>
          <div class="section-required">Todos los campos son obligatorios</div>
        </div>
        
        <div class="form-grid">
          <div class="form-group">
            <label for="codigo_decimal" class="required-label">
              Código Decimal
              <span class="required-asterisk">*</span>
            </label>
            <input
              v-model="form.codigo_decimal"
              type="text"
              id="codigo_decimal"
              required
              class="form-input"
              :class="{ 'is-invalid': errors.codigo_decimal }"
              placeholder="Ej: 823.5"
              maxlength="20"
              @input="validateCodigoDecimal"
            />
            <div v-if="errors.codigo_decimal" class="invalid-feedback">
              {{ errors.codigo_decimal }}
            </div>
            <small class="form-help">
              Formato: números y puntos. Máx. 20 caracteres.
              <span v-if="form.codigo_decimal" class="char-count">
                {{ form.codigo_decimal.length }}/20
              </span>
            </small>
          </div>

          <div class="form-group">
            <label for="etiqueta" class="required-label">
              Etiqueta
              <span class="required-asterisk">*</span>
            </label>
            <input
              v-model="form.etiqueta"
              type="text"
              id="etiqueta"
              required
              class="form-input"
              :class="{ 'is-invalid': errors.etiqueta }"
              placeholder="Ej: LIT"
              maxlength="3"
              @input="form.etiqueta = form.etiqueta.toUpperCase()"
            />
            <div v-if="errors.etiqueta" class="invalid-feedback">
              {{ errors.etiqueta }}
            </div>
            <small class="form-help">
              Exactamente 3 letras mayúsculas.
              <span class="char-count">
                {{ form.etiqueta.length }}/3
              </span>
            </small>
          </div>

          <div class="form-group">
            <label for="numero_ejemplar" class="required-label">
              Número de Ejemplar
              <span class="required-asterisk">*</span>
            </label>
            <input
              v-model="form.numero_ejemplar"
              type="number"
              id="numero_ejemplar"
              required
              min="1"
              class="form-input"
              :class="{ 'is-invalid': errors.numero_ejemplar }"
              placeholder="Ej: 1"
            />
            <div v-if="errors.numero_ejemplar" class="invalid-feedback">
              {{ errors.numero_ejemplar }}
            </div>
            <small class="form-help">
              Número secuencial del ejemplar. Mínimo 1.
            </small>
          </div>
        </div>
      </div>

      <!-- SECCIÓN 2: INFORMACIÓN BÁSICA DEL LIBRO -->
      <div class="form-section">
        <div class="section-header">
          <h2>📖 Información Básica del Libro</h2>
          <div class="section-required">Campos marcados con * son obligatorios</div>
        </div>
        
        <div class="form-grid">
          <div class="form-group">
            <label for="titulo" class="required-label">
              Título
              <span class="required-asterisk">*</span>
            </label>
            <input
              v-model="form.titulo"
              type="text"
              id="titulo"
              required
              class="form-input"
              :class="{ 'is-invalid': errors.titulo }"
              placeholder="Ej: Dune"
              maxlength="255"
            />
            <div v-if="errors.titulo" class="invalid-feedback">
              {{ errors.titulo }}
            </div>
            <small class="form-help">
              Título completo del libro.
              <span v-if="form.titulo" class="char-count">
                {{ form.titulo.length }}/255
              </span>
            </small>
          </div>

          <div class="form-group">
            <label for="autor" class="required-label">
              Autor
              <span class="required-asterisk">*</span>
            </label>
            <input
              v-model="form.autor"
              type="text"
              id="autor"
              required
              class="form-input"
              :class="{ 'is-invalid': errors.autor }"
              placeholder="Ej: Frank Herbert"
              maxlength="255"
            />
            <div v-if="errors.autor" class="invalid-feedback">
              {{ errors.autor }}
            </div>
            <small class="form-help">
              Nombre completo del autor.
              <span v-if="form.autor" class="char-count">
                {{ form.autor.length }}/255
              </span>
            </small>
          </div>

          <div class="form-group">
            <label for="isbn">ISBN</label>
            <input
              v-model="form.isbn"
              type="text"
              id="isbn"
              class="form-input"
              :class="{ 'is-invalid': errors.isbn }"
              placeholder="Ej: 978-84-9759-324-9"
              maxlength="20"
            />
            <div v-if="errors.isbn" class="invalid-feedback">
              {{ errors.isbn }}
            </div>
            <small class="form-help">
              ISBN del libro (opcional).
              <span v-if="form.isbn" class="char-count">
                {{ form.isbn.length }}/20
              </span>
            </small>
          </div>
        </div>
      </div>

      <!-- SECCIÓN 3: DETALLES DEL LIBRO -->
      <div class="form-section">
        <div class="section-header">
          <h2>📚 Detalles del Libro</h2>
          <div class="section-optional">Campos opcionales</div>
        </div>
        
        <div class="form-grid">
          <div class="form-group">
            <label for="editorial_id" class="required-label">
              Editorial
              <span class="required-asterisk">*</span>
            </label>
            <select
              v-model="form.editorial_id"
              id="editorial_id"
              required
              class="form-select"
              :class="{ 'is-invalid': errors.editorial_id }"
            >
              <option value="">Seleccionar editorial</option>
              <option v-for="editorial in editoriales" :key="editorial.id" :value="editorial.id">
                {{ editorial.nombre }}
              </option>
            </select>
            <div v-if="errors.editorial_id" class="invalid-feedback">
              {{ errors.editorial_id }}
            </div>
            <small class="form-help">
              Seleccione la editorial del libro.
            </small>
          </div>

          <div class="form-group">
            <label for="area_conocimiento_id" class="required-label">
              Área de Conocimiento
              <span class="required-asterisk">*</span>
            </label>
            <select
              v-model="form.area_conocimiento_id"
              id="area_conocimiento_id"
              required
              class="form-select"
              :class="{ 'is-invalid': errors.area_conocimiento_id }"
            >
              <option value="">Seleccionar área</option>
              <option v-for="area in areasConocimiento" :key="area.id" :value="area.id">
                {{ area.nombre }}
              </option>
            </select>
            <div v-if="errors.area_conocimiento_id" class="invalid-feedback">
              {{ errors.area_conocimiento_id }}
            </div>
            <small class="form-help">
              Categoría principal del libro.
            </small>
          </div>

          <div class="form-group">
            <label for="edicion">Edición</label>
            <input
              v-model="form.edicion"
              type="number"
              id="edicion"
              min="1"
              class="form-input"
              :class="{ 'is-invalid': errors.edicion }"
              placeholder="Ej: 1"
            />
            <div v-if="errors.edicion" class="invalid-feedback">
              {{ errors.edicion }}
            </div>
            <small class="form-help">
              Número de edición (opcional).
            </small>
          </div>

          <div class="form-group">
            <label for="numero_paginas">Número de Páginas</label>
            <input
              v-model="form.numero_paginas"
              type="number"
              id="numero_paginas"
              min="1"
              class="form-input"
              :class="{ 'is-invalid': errors.numero_paginas }"
              placeholder="Ej: 784"
            />
            <div v-if="errors.numero_paginas" class="invalid-feedback">
              {{ errors.numero_paginas }}
            </div>
            <small class="form-help">
              Total de páginas (opcional).
            </small>
          </div>
        </div>
      </div>

      <!-- SECCIÓN 4: INFORMACIÓN DE ADQUISICIÓN -->
      <div class="form-section">
        <div class="section-header">
          <h2>💰 Información de Adquisición</h2>
          <div class="section-required">Campos marcados con * son obligatorios</div>
        </div>
        
        <div class="form-grid">
          <div class="form-group">
            <label for="metodo_adquisicion_id" class="required-label">
              Método de Adquisición
              <span class="required-asterisk">*</span>
            </label>
            <select
              v-model="form.metodo_adquisicion_id"
              id="metodo_adquisicion_id"
              required
              class="form-select"
              :class="{ 'is-invalid': errors.metodo_adquisicion_id }"
            >
              <option value="">Seleccionar método</option>
              <option value="1">📦 Compra</option>
              <option value="2">🎁 Donación</option>
              <option value="3">🔄 Canje</option>
            </select>
            <div v-if="errors.metodo_adquisicion_id" class="invalid-feedback">
              {{ errors.metodo_adquisicion_id }}
            </div>
            <small class="form-help">
              Cómo se obtuvo el libro.
            </small>
          </div>

          <div class="form-group">
            <label for="proveedor_nombre">Proveedor / Donante</label>
            <input
              v-model="form.proveedor_nombre"
              type="text"
              id="proveedor_nombre"
              class="form-input"
              :class="{ 'is-invalid': errors.proveedor_nombre }"
              placeholder="Ej: Librería El Sótano"
              maxlength="255"
            />
            <div v-if="errors.proveedor_nombre" class="invalid-feedback">
              {{ errors.proveedor_nombre }}
            </div>
            <small class="form-help">
              Nombre del proveedor o donante.
              <span v-if="form.proveedor_nombre" class="char-count">
                {{ form.proveedor_nombre.length }}/255
              </span>
            </small>
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
              :class="{ 'is-invalid': errors.precio }"
              placeholder="Ej: 480.00"
              @blur="formatPrecio"
            />
            <div v-if="errors.precio" class="invalid-feedback">
              {{ errors.precio }}
            </div>
            <small class="form-help">
              Precio en dólares. Usar punto para decimales.
            </small>
          </div>
        </div>
      </div>

      <!-- SECCIÓN 5: ESTADO Y DISPONIBILIDAD -->
      <div class="form-section">
        <div class="section-header">
          <h2>⚙️ Estado y Disponibilidad</h2>
        </div>
        
        <div class="form-grid">
          <div class="form-group">
            <label for="estado_id" class="required-label">
              Estado del Libro
              <span class="required-asterisk">*</span>
            </label>
            <select
              v-model="form.estado_id"
              id="estado_id"
              required
              class="form-select"
              :class="{ 'is-invalid': errors.estado_id }"
            >
              <option value="">Seleccionar estado</option>
              <option value="1">✅ Disponible</option>
              <option value="2">⏳ Prestado</option>
              <option value="3">🔧 En reparación</option>
              <option value="4">❌ Retirado</option>
            </select>
            <div v-if="errors.estado_id" class="invalid-feedback">
              {{ errors.estado_id }}
            </div>
            <small class="form-help">
              Estado actual del libro.
            </small>
          </div>

          <div class="form-group">
            <label for="es_prestable">¿Es prestable?</label>
            <select
              v-model="form.es_prestable"
              id="es_prestable"
              class="form-select"
              :class="{ 'is-invalid': errors.es_prestable }"
            >
              <option :value="true">✅ Sí, puede ser prestado</option>
              <option :value="false">❌ No, solo consulta en sala</option>
            </select>
            <div v-if="errors.es_prestable" class="invalid-feedback">
              {{ errors.es_prestable }}
            </div>
            <small class="form-help">
              Determina si el libro puede ser prestado a usuarios.
            </small>
          </div>
        </div>
      </div>

      <!-- Botones de acción -->
      <div class="form-actions">
        <div class="action-left">
          <button type="button" @click="goBack" class="btn btn-secondary btn-lg">Cancelar</button>
        </div>
        
        <div class="action-right">
          <button 
            type="button" 
            @click="resetForm" 
            class="btn btn-outline btn-lg"
            :disabled="isSubmitting"
          >
            🔄 Limpiar Formulario
          </button>
          
          <button 
            type="submit" 
            class="btn btn-success btn-lg"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="spinner-small"></span>
            <span v-else>✅ Crear Libro</span>
          </button>
        </div>
      </div>

      <!-- Resumen de validación -->
      <div v-if="Object.keys(errors).length > 0" class="validation-summary">
        <div class="validation-header">
          <span class="validation-icon">⚠️</span>
          <h3>Corrija los siguientes errores:</h3>
        </div>
        <ul class="validation-errors">
          <li v-for="(error, field) in errors" :key="field">
            <strong>{{ getFieldLabel(field) }}:</strong> {{ error }}
          </li>
        </ul>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { bookService } from '@/services/books'

const router = useRouter()

// Estado
const loading = ref(false)
const isSubmitting = ref(false)

// Listas para selects (ejemplo - reemplaza con tus endpoints)
const editoriales = ref([
  { id: 1, nombre: 'Debolsillo' },
  { id: 2, nombre: 'Alfaguara' },
  { id: 3, nombre: 'Planeta' },
  { id: 4, nombre: 'Penguin Random House' },
  { id: 5, nombre: 'Editorial Norma' }
])

const areasConocimiento = ref([
  { id: 1, nombre: 'Literatura' },
  { id: 2, nombre: 'Ciencia' },
  { id: 3, nombre: 'Historia' },
  { id: 4, nombre: 'Arte' },
  { id: 5, nombre: 'Ciencia Ficción' },
  { id: 6, nombre: 'Filosofía' },
  { id: 7, nombre: 'Matemáticas' },
  { id: 8, nombre: 'Tecnología' }
])

// Formulario con valores iniciales
const form = reactive({
  // Identificación (obligatorios)
  codigo_decimal: '',
  etiqueta: '',
  numero_ejemplar: 1,
  
  // Información básica
  isbn: '',
  titulo: '',
  autor: '',
  editorial_id: '',
  edicion: 1,
  numero_paginas: '',
  area_conocimiento_id: '',
  
  // Adquisición
  metodo_adquisicion_id: '',
  proveedor_nombre: '',
  precio: '',
  es_prestable: true,
  
  // Estado
  estado_id: '1'
})

// Errores
const errors = reactive({})

// Métodos
const validateCodigoDecimal = () => {
  const value = form.codigo_decimal
  if (value && !/^[\d.]+$/.test(value)) {
    errors.codigo_decimal = 'Solo números y puntos permitidos'
  } else if (errors.codigo_decimal === 'Solo números y puntos permitidos') {
    delete errors.codigo_decimal
  }
}

const formatPrecio = () => {
  if (form.precio) {
    // Formatear a 2 decimales
    form.precio = parseFloat(form.precio).toFixed(2)
  }
}

const getFieldLabel = (field) => {
  const labels = {
    codigo_decimal: 'Código Decimal',
    etiqueta: 'Etiqueta',
    numero_ejemplar: 'Número de Ejemplar',
    titulo: 'Título',
    autor: 'Autor',
    editorial_id: 'Editorial',
    area_conocimiento_id: 'Área de Conocimiento',
    metodo_adquisicion_id: 'Método de Adquisición',
    estado_id: 'Estado del Libro'
  }
  return labels[field] || field
}

const validateForm = () => {
  // Limpiar errores anteriores
  Object.keys(errors).forEach(key => delete errors[key])
  
  let isValid = true
  
  // Validar campos obligatorios
  const requiredFields = [
    'codigo_decimal',
    'etiqueta', 
    'numero_ejemplar',
    'titulo',
    'autor',
    'editorial_id',
    'area_conocimiento_id',
    'metodo_adquisicion_id',
    'estado_id'
  ]
  
  requiredFields.forEach(field => {
    if (!form[field] || (typeof form[field] === 'string' && form[field].trim() === '')) {
      errors[field] = 'Este campo es obligatorio'
      isValid = false
    }
  })
  
  // Validaciones específicas
  if (form.etiqueta && form.etiqueta.length !== 3) {
    errors.etiqueta = 'La etiqueta debe tener exactamente 3 caracteres'
    isValid = false
  }
  
  if (form.codigo_decimal && !/^[\d.]+$/.test(form.codigo_decimal)) {
    errors.codigo_decimal = 'Solo números y puntos permitidos'
    isValid = false
  }
  
  if (form.codigo_decimal && form.codigo_decimal.length > 20) {
    errors.codigo_decimal = 'Máximo 20 caracteres'
    isValid = false
  }
  
  if (form.numero_ejemplar && form.numero_ejemplar < 1) {
    errors.numero_ejemplar = 'Debe ser mayor o igual a 1'
    isValid = false
  }
  
  if (form.edicion && form.edicion < 1) {
    errors.edicion = 'La edición debe ser mayor o igual a 1'
    isValid = false
  }
  
  if (form.numero_paginas && form.numero_paginas < 1) {
    errors.numero_paginas = 'El número de páginas debe ser mayor o igual a 1'
    isValid = false
  }
  
  if (form.precio && parseFloat(form.precio) < 0) {
    errors.precio = 'El precio no puede ser negativo'
    isValid = false
  }
  
  return isValid
}

const submitForm = async () => {
  console.log('Validando formulario...')
  
  if (!validateForm()) {
    console.log('Errores de validación:', errors)
    return
  }
  
  isSubmitting.value = true
  
  try {
    // Preparar datos exactamente como espera el backend
    const bookData = {
      codigo_decimal: form.codigo_decimal.trim(),
      etiqueta: form.etiqueta.trim().toUpperCase(),
      numero_ejemplar: parseInt(form.numero_ejemplar),
      isbn: form.isbn.trim() || null,
      titulo: form.titulo.trim(),
      autor: form.autor.trim(),
      editorial_id: parseInt(form.editorial_id),
      edicion: form.edicion ? parseInt(form.edicion) : null,
      numero_paginas: form.numero_paginas ? parseInt(form.numero_paginas) : null,
      area_conocimiento_id: parseInt(form.area_conocimiento_id),
      metodo_adquisicion_id: parseInt(form.metodo_adquisicion_id),
      proveedor_nombre: form.proveedor_nombre.trim() || null,
      precio: form.precio ? parseFloat(form.precio) : null,
      es_prestable: form.es_prestable,
      estado_id: parseInt(form.estado_id)
    }
    
    console.log('Enviando datos al servidor:', bookData)
    
    // Llamar al endpoint POST /api/libros
    const result = await bookService.createBook(bookData)
    console.log('Libro creado exitosamente:', result)
    
    // Mostrar mensaje de éxito
    alert(`✅ Libro "${form.titulo}" creado exitosamente`)
    
    // Redirigir al catálogo
    router.push('/catalog')
    
  } catch (error) {
    console.error('Error creando libro:', error)
    console.error('Response data:', error.response?.data)
    
    // Manejar errores del backend
    if (error.response?.status === 422) {
      // Errores de validación de Pydantic
      const validationErrors = error.response.data.detail
      if (Array.isArray(validationErrors)) {
        validationErrors.forEach(validationError => {
          const field = validationError.loc[validationError.loc.length - 1]
          errors[field] = validationError.msg
        })
      } else if (typeof validationErrors === 'string') {
        alert(`❌ Error: ${validationErrors}`)
      }
    } else if (error.response?.status === 400) {
      alert(`❌ Error: ${error.response.data.detail || 'Datos inválidos'}`)
    } else {
      alert('❌ Error al crear el libro. Por favor, intente nuevamente.')
    }
    
  } finally {
    isSubmitting.value = false
  }
}

const resetForm = () => {
  Object.assign(form, {
    codigo_decimal: '',
    etiqueta: '',
    numero_ejemplar: 1,
    isbn: '',
    titulo: '',
    autor: '',
    editorial_id: '',
    edicion: 1,
    numero_paginas: '',
    area_conocimiento_id: '',
    metodo_adquisicion_id: '',
    proveedor_nombre: '',
    precio: '',
    es_prestable: true,
    estado_id: '1'
  })
  
  Object.keys(errors).forEach(key => delete errors[key])
}

const goBack = () => {
  router.push('/catalog')
}

// Cargar datos iniciales
onMounted(() => {
  // Aquí podrías cargar editoriales y áreas de conocimiento desde la API
  console.log('Componente CrearLibro montado')
})
</script>

<style scoped>
.crear-libro-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.create-header {
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 3px solid #667eea;
}

.header-content {
  margin-bottom: 2rem;
}

.btn-back {
  background: none;
  border: none;
  color: #667eea;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.5rem 0;
  margin-bottom: 1rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-back:hover {
  text-decoration: underline;
}

.create-header h1 {
  font-size: 2.5rem;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
  margin: 0;
}

/* Steps indicator */
.header-steps {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
  max-width: 600px;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  position: relative;
}

.step-indicator::after {
  content: '';
  position: absolute;
  top: 12px;
  left: 50%;
  right: -50%;
  height: 2px;
  background: #e0e0e0;
  z-index: -1;
}

.step-indicator:last-child::after {
  display: none;
}

.step-indicator.active .step-number {
  background: #667eea;
  color: white;
}

.step-indicator.active .step-label {
  color: #667eea;
  font-weight: 600;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e0e0e0;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 600;
}

.step-label {
  font-size: 0.85rem;
  color: #666;
  white-space: nowrap;
}

/* Formulario */
.create-book-form {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #f0f0f0;
}

.section-header h2 {
  font-size: 1.4rem;
  color: #444;
  margin: 0;
}

.section-required, .section-optional {
  font-size: 0.85rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-weight: 500;
}

.section-required {
  background: #d4edda;
  color: #155724;
}

.section-optional {
  background: #e2e3e5;
  color: #383d41;
}

/* Form grid */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.required-label {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.required-asterisk {
  color: #dc3545;
}

.form-input, .form-select {
  padding: 0.75rem 1rem;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-input:focus, .form-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input.is-invalid, .form-select.is-invalid {
  border-color: #dc3545;
}

.form-input.is-invalid:focus, .form-select.is-invalid:focus {
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
}

.invalid-feedback {
  color: #dc3545;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.form-help {
  color: #6c757d;
  font-size: 0.85rem;
  margin-top: 0.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.char-count {
  font-family: monospace;
  font-size: 0.8rem;
  color: #999;
}

/* Botones */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 2px solid #f0f0f0;
}

.action-left, .action-right {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.btn-lg {
  padding: 0.875rem 1.75rem;
  font-size: 1.05rem;
}

.btn-success {
  background: linear-gradient(135deg, #28a745 0%, #218838 100%);
  color: white;
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4);
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

.btn-outline:hover:not(:disabled) {
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Validación */
.validation-summary {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  color: #856404;
}

.validation-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.validation-icon {
  font-size: 1.5rem;
}

.validation-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.validation-errors {
  margin: 0;
  padding-left: 1.5rem;
}

.validation-errors li {
  margin-bottom: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .crear-libro-container {
    padding: 1rem;
  }
  
  .create-header h1 {
    font-size: 2rem;
  }
  
  .header-steps {
    flex-direction: column;
    gap: 1rem;
  }
  
  .step-indicator {
    flex-direction: row;
    gap: 1rem;
  }
  
  .step-indicator::after {
    display: none;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 1rem;
  }
  
  .action-left, .action-right {
    width: 100%;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>