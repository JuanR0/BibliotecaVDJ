<template>
  <div class="book-catalog">
    <!-- Header -->
    <div class="catalog-header">
      <div class="header-content">
        <h1>Catálogo de la Biblioteca</h1>
        <p class="subtitle">Libros pertenecientes a la biblioteca</p>
      </div>
      
      <!-- Estadísticas rápidas -->
      <div class="catalog-stats">
        <div class="stat-item">
          <span class="stat-icon">📖</span>
          <div>
            <span class="stat-value">{{ stats.totalBooks || 0 }}</span>
            <span class="stat-label">Libros totales</span>
          </div>
        </div>
        <div class="stat-item">
          <span class="stat-icon">✅</span>
          <div>
            <span class="stat-value">{{ stats.availableBooks || 0 }}</span>
            <span class="stat-label">Disponibles</span>
          </div>
        </div>
        <div class="stat-item">
          <span class="stat-icon">🔄</span>
          <div>
            <span class="stat-value">{{ stats.es_prestable || 0 }}</span>
            <span class="stat-label">Prestables</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Sistema de Búsqueda Avanzado -->
    <div class="search-section">
      <div class="search-container">
        <div class="search-bar-wrapper">
          <div class="search-icon">🔍</div>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por título, autor, ISBN, editorial..."
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <button @click="handleSearch" class="search-button">
            Buscar
          </button>
          <button @click="toggleAdvancedFilters" class="filter-toggle">
            {{ showAdvancedFilters ? '▲' : '▼' }} Filtros Avanzados
          </button>
        </div>

        <!-- FILTROS AVANZADOS -->
        <div v-if="showAdvancedFilters" class="advanced-filters">
          <div class="filters-grid">
            <div class="filter-group">
              <label>Estado:</label>
              <select v-model="filters.estado_id" class="filter-select">
                <option value="">Todos los estados</option>
                <option value="1">Disponible</option>
                <option value="2">Prestado</option>
                <option value="3">En reparación</option>

                <option v-if="canSeeRetiredBooks" value="4">Retirados</option>
              </select>

              <div v-if="filters.estado_id === '1'" class="filter-hint">
                Estado por defecto: Disponible
              </div>
            </div>

            <div class="filter-group">
              <label>Es prestable:</label>
              <select v-model="filters.es_prestable" class="filter-select">
                <option value="">Todos</option>
                <option value="true">Solo prestables</option>
                <option value="false">No prestables</option>
              </select>
            </div>

            <div class="filter-group">
              <label>Año de adquisición:</label>
              <input v-model="filters.ano_adquisicion" type="number" placeholder="Ej: 2023" class="filter-input" min="1900" :max="new Date().getFullYear()"/>
            </div>

            <div class="filter-group">
              <label>Editorial:</label>
              <select v-model="filters.editorial_id" class="filter-select">
                <option value="">Todas las editoriales</option>
                <option v-for="editorial in editoriales" :key="editorial.id" :value="editorial.id">
                  {{ editorial.nombre }}
                </option>
              </select>
            </div>

          </div>

          <div class="filter-actions">
            <button @click="applyFilters" class="btn btn-primary">Aplicar Filtros</button>
            <button @click="resetFilters" class="btn btn-outline">Limpiar Filtros</button>
          </div>

        </div>
      </div>
    </div>

    <!-- RESULTADOS -->
    <div class="results-section">
      <!-- CONTROLES -->
      <div class="view-controls">
        <div class="view-options">
          <!--TIPOS DE VISTA-->
          <button @click="viewMode = 'grid'" :class="{ 'active': viewMode === 'grid' }" class="view-btn">Cuadrícula</button>
          <button @click="viewMode = 'list'" :class="{ 'active': viewMode === 'list' }" class="view-btn">Lista</button>
        </div>
        
        <div class="sort-options">
          <label>Ordenar por:</label>
          <select v-model="sortBy" @change="sortBooks" class="sort-select">
            <option value="titulo">Título (A-Z)</option>
            <option value="autor">Autor (A-Z)</option>
            <option value="edicion">Edición (Más reciente)</option>
            <option value="fecha_adquisicion">Fecha adquisición</option>
          </select>
        </div>
      </div>

      <!-- ESTADO CARGA/ERROR-->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando catálogo...</p>
      </div>

      <div v-if="error" class="error-state">
        <p>Error: {{ error }}</p>
        <button @click="loadBooks" class="btn btn-primary">Reintentar</button>
      </div>

      <!-- VISTA CUADRICULA -->
      <div v-if="viewMode === 'grid' && !isLoading && !error" class="books-grid">
        <div v-for="book in paginatedBooks" :key="book.id" class="book-card">
          <div class="book-card-header">
            <div class="book-status" :class="getStatusClass(book)"> {{ getStatusText(book) }}</div>
            <div class="book-code">{{ book.codigo_decimal || 'N/A' }}</div>
          </div>
          
          <!-- PRESTABLE -->
          <div class="book-cover">
            <div class="cover-placeholder">
              <span class="book-icon">📖</span>
              <div class="book-badge" v-if="book.es_prestable && book.edicion != 1">🔄 Prestable</div>
            </div>
          </div>
          
          <div class="book-info">
            <h3 class="book-title">{{ book.titulo }}</h3>
            <p class="book-author">✍️ {{ book.autor }}</p>
            
            <div class="book-details">
              <p><strong>ISBN:</strong> {{ book.isbn || 'No disponible' }}</p>
              <p><strong>Etiqueta:</strong> {{ book.etiqueta }}</p>
              <p><strong>Ejemplar:</strong> {{ book.numero_ejemplar }}</p>
              <p><strong>Edición:</strong> {{ book.edicion }}</p>
              <p><strong>Páginas:</strong> {{ book.numero_paginas }}</p>
              <p v-if="book.editorial_nombre">
                <strong>Editorial:</strong> {{ book.editorial_nombre }}
              </p>
              <p v-if="book.area_conocimiento_nombre">
                <strong>Área:</strong> {{ book.area_conocimiento_nombre }}
              </p>
            </div>
            
            <div class="book-metadata">
              <span class="metadata-item">ID:{{ book.id }}</span>
              <!-- COSTO DE LIBRO NO NECESARIO PARA USUARIO -->
              <!-- <span class="metadata-item" v-if="book.precio">${{ formatPrecio(book.precio) }}</span> -->
              <!-- <span class="metadata-item" v-if="book.fecha_adquisicion">{{ formatFecha(book.fecha_adquisicion) }}</span> -->
            </div>
          </div>
          

          <!-- ACCIONES DE LIBRO -->
          <div class="book-actions">
            <button @click="viewBookDetails(book.id)" class="btn btn-outline btn-small btn-details-books">Detalles..</button>
            <button v-if="book.es_prestable && book.edicion != 1" @click="requestLoan(book.id)" class="btn btn-loan-books btn-smal" :disabled="isProcessingLoan">Solicitar Préstamo </button>
            <button v-if="canEditBooks" @click="goToEditPage(book.id)" class="btn btn-edit-books" :title="`Editar libro: ${book.titulo}`">Editar</button>
            
            <button v-if="canDelete" @click="confirmDelete(book)" class="btn btn-danger btn-delete-books" :title="`Eliminar: ${book.titulo}`" :disabled="isDeleting">
              <span v-if="isDeleting && deletingBookId === book.id" class="spinner-mini"></span>
              <span v-else>Eliminar</span>
            </button>
            <button v-if="canRecoverBooks && book.estado_id == 4" @click="recoverBook(book)" class="btn btn-warning btn-recover-books" title="Ver y recuperar libros retirados">
              <span class="btn-icon">♻️</span>
              <span class="btn-text">Recuperar Libros</span>
            </button>

            <!-- <button v-if="book.metodo_adquisicion_nombre" class="btn btn-secondary btn-small" title="Método de adquisición">🏷️ {{ book.metodo_adquisicion_nombre }} </button> -->

          </div>
        </div>

        <!--MODAL DELETE-->
        <div v-if="showDeleteModal" class="modal-overlay">
            <div class="modal-content">
              <div class="modal-header">
                <h3>Confirmar Eliminación</h3>
                <button @click="closeModal" class="modal-close-btn">×</button>
              </div>
              
              <div class="modal-body">
                <p>¿Estás seguro de que deseas eliminar el siguiente libro?</p>
                <div class="book-to-delete">
                  <div class="book-info">
                    <h4>{{ bookToDelete?.titulo }}</h4>
                    <p><strong>Autor:</strong> {{ bookToDelete?.autor }}</p>
                    <p><strong>Código:</strong> {{ bookToDelete?.codigo_decimal }}</p>
                    <p><strong>Edicion:</strong> {{ bookToDelete?.edicion }}</p>
                  </div>
                  <div class="warning-message">
                    <div class="warning-icon">⚠️</div>
                    <p>El libro será retirado.</p>
                  </div>
                </div>
              </div>
              
              <div class="modal-footer">
                <button @click="closeModal" class="btn btn-secondary" :disabled="isDeleting">
                  Cancelar
                </button>
                <button @click="deleteBook" class="btn btn-danger" :disabled="isDeleting">
                  <span v-if="isDeleting" class="spinner-small"></span>
                  {{ isDeleting ? 'Eliminando...' : 'Sí, Eliminar' }}
                </button>
              </div>
            </div>
          </div>

      </div>
      
      <div v-if="showSuccessToast" class="toast success">
        <div class="toast-icon">✅</div>
        <div class="toast-content">
          <strong>Libro eliminado correctamente</strong>
          <p>El libro ha sido eliminado del sistema</p>
        </div>
        <button @click="showSuccessToast = false" class="toast-close">×</button>
      </div>      
      
      <!-- List mode view -->
      <div v-if="viewMode === 'list' && !isLoading && !error" class="books-list">
        <table class="books-table">
          
          <!-- Table data -->
          
          <thead>
            <tr>
              <th>Código</th>
              <th>Seccion</th>
              <th>Título</th>
              <th>Autor</th>
              <th>Editorial</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>

            <tr v-for="book in paginatedBooks" :key="book.id">
              <td>
                <div class="book-code-cell">
                  <div>{{ book.codigo_decimal || 'N/A' }}</div>
                </div>
              </td>
              
              <td>
                <div class="small-text">{{ book.etiqueta }}-{{ book.numero_ejemplar }}</div>
              </td>

              <td>
                <strong>{{ book.titulo }}</strong>
                <div class="small-text">
                  Ed. {{ book.edicion }}
                </div>
              </td>

              <td>{{ book.autor }}</td>
              <td>{{ book.editorial_nombre || 'N/A' }}</td>
              <td>
                <span :class="getStatusClass(book)" class="status-badge">
                  {{ getStatusText(book) }}
                </span>
                <div class="small-text" v-if="book.es_prestable">
                  🔄 Prestable
                </div>
              </td>
              <td>
                <button @click="viewBookDetails(book.id)" class="btn-action" title="Ver detalles"> 🔍</button>
                <button v-if="book.es_prestable && book.estado_id === 1" @click="requestLoan(book.id)" class="btn-action" title="Solicitar préstamo" :disabled="isProcessingLoan">📥</button>
              </td>
            </tr>

          </tbody>
        </table>
      </div>

      <!-- Paginación -->
      <div v-if="!isLoading && !error && books.length > 0" class="pagination-section">
        <div class="pagination-info">
          Mostrando {{ startItem }}-{{ endItem }} de {{ filteredBooks.length }} libros
          <span v-if="searchQuery || hasActiveFilters" class="filtered-info">
            (Filtrado de {{ books.length }} total)
          </span>
        </div>
        
        <div class="pagination-controls">
          <button @click="prevPage" :disabled="currentPage === 1" class="pagination-btn">← Anterior</button>
          
          <div class="page-numbers">
            <span v-for="page in visiblePages" :key="page" @click="goToPage(page)" :class="{ 'active': page === currentPage }" class="page-number"> {{ page }} </span>
            <span v-if="hasMorePages" class="page-ellipsis">...</span>
          </div>
          
          <button @click="nextPage" :disabled="currentPage === totalPages" class="pagination-btn">Siguiente →</button>
        </div>
        
        <div class="items-per-page">
          <label>Mostrar:</label>
          <select v-model="itemsPerPage" @change="resetPagination" class="page-select">
            <option value="12">12</option>
            <option value="24">24</option>
            <option value="48">48</option>
            <option value="100">100</option>
          </select>
        </div>
      </div>

      <!-- Sin resultados -->
      <div v-if="!isLoading && !error && filteredBooks.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>No se encontraron libros</h3>

        <p v-if="searchQuery || hasActiveFilters"> No hay resultados para tu búsqueda. Intenta con otros términos o ajusta los filtros. </p>
        <p v-else>
          No hay libros disponibles en el catálogo.
        </p>

        <button @click="resetFilters" class="btn btn-primary">🔄 Mostrar todos los libros</button>
      </div>


    </div>
  </div>
</template>


<!-- SCRIPT -->
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { bookService } from '@/services/books'
import { useAuthStore } from '@/stores/auth'
import { usePermissions } from '@/composables/usePermissions'


const router = useRouter()
const { hasPermission } = usePermissions()

// State
const searchQuery = ref('')
const showAdvancedFilters = ref(false)
const viewMode = ref('grid')
const sortBy = ref('titulo')
const isLoading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const itemsPerPage = ref(12)
const isProcessingLoan = ref(false)
const authStore = useAuthStore()

// Eliminacion de libro
const isDeleting = ref(false)
const deletingBookId = ref(null)
const showDeleteModal = ref(false)
const bookToDelete = ref(null)
const showSuccessToast = ref(false)

// Data
const books = ref([])
const stats = ref({
  totalBooks: 0,
  availableBooks: 0,
  prestableBooks: 0
})
const editoriales = ref([])

// Filter
const filters = ref({
  //ESTADO 1 DISPONIBLE SE ELIGE POR DEFECTO PARA LISTAR LIBROS DISPONIBLES SOLAMENTE DE FORMA PREDETERMINADA
  estado_id: '1',
  es_prestable: '',
  ano_adquisicion: '',
  editorial_id: ''
})


//========================================== PERMISOS ======================================================
const canCreateBooks = computed(() => hasPermission('canCreateBooks'))
const canEditBooks = computed(() => hasPermission('canEditBooks'))
const canDelete = computed(() => hasPermission('canDeleteBooks'))
const canRecoverBooks = computed(() => hasPermission('canRecoverBooks'))
const canSeeRetiredBooks = computed(() => hasPermission('canSeeRetiredBooks'))
const userCanRequestLoans = computed(() => hasPermission('canRequestLoans'))



//========================================== FUNCIONES ======================================================

//ELIMINACION DE LIBRO (SOFT DELETE)
const deleteBook = async () => {
  if (!bookToDelete.value?.id || isDeleting.value) return
  
  isDeleting.value = true
  deletingBookId.value = bookToDelete.value.id
  
  try {
    console.log(`Eliminando libro ID: ${bookToDelete.value.id}`)
    
    // Llamar al endpoint DELETE
    await bookService.deleteBook(bookToDelete.value.id)
    
    console.log('✅ Libro eliminado exitosamente')
    
    // Mostrar toast de éxito
    showSuccessToast.value = true
    
    // Cerrar modal
    showDeleteModal.value = false
    
    // Actualizar lista de libros (quitar el libro eliminado)
    books.value = books.value.filter(book => book.id !== bookToDelete.value.id)
    
    // Auto-ocultar toast después de 3 segundos
    setTimeout(() => {
      showSuccessToast.value = false
    }, 3000)
    
  } catch (error) {
    console.error('❌ Error eliminando libro:', error)
    
    // Mostrar error al usuario
    alert(`Error al eliminar el libro: ${error.response?.data?.detail || error.message}`)
    
  } finally {
    isDeleting.value = false
    deletingBookId.value = null
    bookToDelete.value = null
  }
}

//RECUPERACION DE LIBRO
const recoverBook = async (book) => {
  if (!canRecoverBooks.value) {
    alert('No tienes permisos para recuperar libros')
    return
  }
  
  if (!confirm(`¿Recuperar el libro "${book.titulo}"?\n\nEl libro pasará a estado "Disponible".`)) {
    return
  }
  
  try {
    await bookService.reactivateBook(book.id)
    
    const index = books.value.findIndex(b => b.id === book.id)
    if (index !== -1) {
      books.value[index].estado_id = 1
      books.value[index].estado_nombre = 'Disponible'
    }
    
    alert(`✅ Libro "${book.titulo}" recuperado.`)
  } catch (error) {
    console.error('Error recuperando libro:', error)
    alert('❌ Error al recuperar el libro')
  }
}




//========================================== NAVEGACION ======================================================


 //ENVIAR A EDICION DE LIBRO
 const goToEditPage = (bookId) => {
  console.log(`Redirigiendo a página de edición del libro ID: ${bookId}`)
  router.push(`/admin/libros/editar/${bookId}`)
}

//ENVIAR A DETALLES DE LIBRO
const viewBookDetails = (bookId) => {
  router.push(`/libros/${bookId}`)
}




//========================================== MODAL ======================================================
//CONFIRMACION DE ELIIMINACION PARA USO DE MODAL
const confirmDelete = (book) => {
  if (!canDelete.value) {
    alert('No tienes permisos para eliminar libros')
    return
  }
  
  bookToDelete.value = book
  showDeleteModal.value = true

}

const closeModal = () => {
  if (!isDeleting.value) {
    showDeleteModal.value = false
    bookToDelete.value = null
  }
}



//========================================== FUNCIONES EN LISTADO ===========================================
//FILATRADO DE LIBROS
const filteredBooks = computed(() => {
  let result = [...books.value]
  
  // Aplicar filtros
  if (filters.value.estado_id) {
    result = result.filter(book => book.estado_id === parseInt(filters.value.estado_id))
  }
  
  if (filters.value.es_prestable !== '') {
    const isPrestable = filters.value.es_prestable === 'true'
    result = result.filter(book => book.es_prestable === isPrestable)
  }
  
  if (filters.value.editorial_id) {
    result = result.filter(book => book.editorial_id === parseInt(filters.value.editorial_id))
  }
  
  if (filters.value.ano_adquisicion) {
    const year = parseInt(filters.value.ano_adquisicion)
    result = result.filter(book => {
      if (!book.fecha_adquisicion) return false
      const fecha = new Date(book.fecha_adquisicion)
      return fecha.getFullYear() === year
    })
  }

  //BUSQUEDA POR TEXTO
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(book => 
      book.titulo?.toLowerCase().includes(query) ||
      book.autor?.toLowerCase().includes(query) ||
      (book.isbn && book.isbn.toLowerCase().includes(query)) ||
      book.editorial_nombre?.toLowerCase().includes(query) ||
      book.area_conocimiento_nombre?.toLowerCase().includes(query) ||
      book.codigo_decimal?.toLowerCase().includes(query)
    )
  }
  
  // ORDENAMIENTO
  result.sort((a, b) => {
    if (sortBy.value === 'titulo') {
      return (a.titulo || '').localeCompare(b.titulo || '')
    }
    if (sortBy.value === 'autor') {
      return (a.autor || '').localeCompare(b.autor || '')
    }
    if (sortBy.value === 'edicion') {
      return (b.edicion || 0) - (a.edicion || 0)
    }
    if (sortBy.value === 'fecha_adquisicion') {
      const dateA = a.fecha_adquisicion ? new Date(a.fecha_adquisicion) : new Date(0)
      const dateB = b.fecha_adquisicion ? new Date(b.fecha_adquisicion) : new Date(0)
      return dateB - dateA
    }
    return 0
  })
  
  return result
})

//PAGINACION
const totalPages = computed(() => {
  return Math.ceil(filteredBooks.value.length / itemsPerPage.value) || 1
})

const paginatedBooks = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredBooks.value.slice(start, end)
})

const startItem = computed(() => {
  return (currentPage.value - 1) * itemsPerPage.value + 1
})

const endItem = computed(() => {
  const end = currentPage.value * itemsPerPage.value
  return end > filteredBooks.value.length ? filteredBooks.value.length : end
})

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  
  if (totalPages.value <= maxVisible) {
    for (let i = 1; i <= totalPages.value; i++) pages.push(i)
  } else {
    let start = Math.max(1, currentPage.value - 2)
    let end = Math.min(totalPages.value, start + maxVisible - 1)
    
    if (end - start + 1 < maxVisible) {
      start = end - maxVisible + 1
    }
    
    for (let i = start; i <= end; i++) pages.push(i)
  }
  
  return pages
})

const hasMorePages = computed(() => {
  return currentPage.value < totalPages.value - 2
})

const hasActiveFilters = computed(() => {
  return Object.values(filters.value).some(value => 
    value !== '' && value !== null && value !== undefined
  )
})

// Métodos
const loadBooks = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await bookService.getBooks()
    
    // Data structure:{ libros: [], total: 0, pagina: 0, por_pagina: 0 }
    if (response && response.libros) {
      books.value = response.libros
    } else if (Array.isArray(response)) {
      books.value = response
    } else {
      books.value = []
    }
    
    calculateStats()
    
    extractEditoriales()
    
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error cargando el catálogo'
    console.error('Error cargando libros:', err)
  } finally {
    isLoading.value = false
  }
}

const calculateStats = () => {
  const total = books.value.length
  const available = books.value.filter(book => book.estado_id === 1).length
  const prestable = books.value.filter(book => book.es_prestable).length
  
  stats.value = {
    totalBooks: total,
    availableBooks: available,
    prestableBooks: prestable
  }
}

const extractEditoriales = () => {
  const editorialSet = new Map()
  
  books.value.forEach(book => {
    if (book.editorial_id && book.editorial_nombre) {
      if (!editorialSet.has(book.editorial_id)) {
        editorialSet.set(book.editorial_id, {
          id: book.editorial_id,
          nombre: book.editorial_nombre
        })
      }
    }
  })
  
  editoriales.value = Array.from(editorialSet.values())
}

const handleSearch = async () => {
  if (searchQuery.value.trim()) {
    // Si tu API tiene endpoint de búsqueda específico
    try {
      isLoading.value = true
      const response = await bookService.searchBooks(searchQuery.value, filters.value)
      if (response && response.libros) {
        books.value = response.libros
      }
      calculateStats()
    } catch (err) {
      console.error('Error en búsqueda:', err)
      // Si falla la búsqueda específica, usa filtrado local
    } finally {
      isLoading.value = false
    }
  } else {
    // Si no hay búsqueda, recarga todos los libros
    loadBooks()
  }
  currentPage.value = 1
}


const toggleAdvancedFilters = () => {
  showAdvancedFilters.value = !showAdvancedFilters.value
}

const applyFilters = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  searchQuery.value = ''
  filters.value = {
    estado_id: '',
    es_prestable: '',
    ano_adquisicion: '',
    editorial_id: ''
  }
  currentPage.value = 1
  loadBooks()
}

const getStatusClass = (book) => {
  const classes = {
    1: 'status-available',
    2: 'status-borrowed',
    3: 'status-repair',
    4: 'status-lost'
  }
  return classes[book.estado_id] || 'status-unknown'
}

const getStatusText = (book) => {
  const statusMap = {
    1: '✅ Disponible',
    2: '⏳ Prestado',
    3: '🔧 En reparación',
    4: '❌ Retirado'
  }
  return statusMap[book.estado_id] || book.estado_nombre || 'Desconocido'
}

const formatPrecio = (precio) => {
  if (!precio) return '0.00'
  try {
    const num = parseFloat(precio)
    return isNaN(num) ? '0.00' : num.toLocaleString('es-ES', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  } catch {
    return '0.00'
  }
}

const formatFecha = (fecha) => {
  if (!fecha) return 'N/A'
  try {
    return new Date(fecha).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch {
    return 'Fecha inválida'
  }
}


// Paginación
const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const resetPagination = () => {
  currentPage.value = 1
}

const sortBooks = () => {
  currentPage.value = 1
}

// Watch para búsqueda en tiempo real (opcional)
let searchTimeout
watch(searchQuery, (newQuery) => {
  clearTimeout(searchTimeout)
  if (newQuery.trim()) {
    searchTimeout = setTimeout(() => {
      currentPage.value = 1
    }, 500)
  }
})

// Watch para filtros
watch(filters, () => {
  currentPage.value = 1
}, { deep: true })



// Ciclo de vida
onMounted(() => {
  loadBooks()
  //DEBUG PARA SABER PERMISOS ACTUALES
  console.log('Permisos del usuario:', {
    crear: canCreateBooks.value,
    editar: canEditBooks.value,
    eliminar: canDelete.value,
    recuperar: canRecoverBooks.value,
    verRetirados: canSeeRetiredBooks.value,
    prestar: userCanRequestLoans.value
  })
})







//=========================== PROXIMAMENTE =================================
// PRESTAMOS V1
// const requestLoan = async (bookId) => {
//   isProcessingLoan.value = true
//   try {
//     // Aquí deberías implementar la lógica de préstamo
//     // Por ahora solo muestra un mensaje
//     const book = books.value.find(b => b.id === bookId)
//     if (book) {
//       alert(`Solicitando préstamo de: "${book.titulo}"\nAutor: ${book.autor}`)
//       // Aquí llamarías a tu servicio de préstamos cuando lo implementes
//       // await loanService.requestLoan(bookId)
//     }
//   } catch (err) {
//     console.error('Error solicitando préstamo:', err)
//     alert('Error al solicitar préstamo')
//   } finally {
//     isProcessingLoan.value = false
//   }
// }

// PRESTAMOS
// const requestLoan = async (bookId) => {
//   if (!userCanRequestLoans.value) {
//     alert('No tienes permisos para solicitar préstamos')
//     return
//   }
  
//   isProcessingLoan.value = true
//   try {
//     const book = books.value.find(b => b.id === bookId)
//     if (book) {
//       alert(`Solicitando préstamo de: "${book.titulo}"`)
//     }
//   } catch (err) {
//     console.error('Error solicitando préstamo:', err)
//     alert('Error al solicitar préstamo')
//   } finally {
//     isProcessingLoan.value = false
//   }
// }
// ELIMINACION EN LIBROS PRESTADOS
// const canDeleteThisBook = (book) => {
//   return userCanDelete.value && 
//          book.estado_id !== 2 // No se pueden eliminar libros prestados
// }



</script>





<style scoped>
/* Estilos generales */
.book-catalog {
  padding: 1rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.catalog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #e9ecef;
}

.header-content h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
}

.catalog-stats {
  display: flex;
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  background: #f8f9fa;
  border-radius: 0.75rem;
  border: 1px solid #e9ecef;
}

.stat-icon {
  font-size: 1.5rem;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 0.85rem;
  color: #666;
}

/* Búsqueda */
.search-section {
  margin-bottom: 2rem;
}

.search-container {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  overflow: hidden;
}

.search-bar-wrapper {
  display: flex;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.search-icon {
  display: flex;
  align-items: center;
  padding: 0 1rem;
  color: white;
  font-size: 1.2rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.9);
}

.search-button {
  background: white;
  color: #667eea;
  border: none;
  padding: 0 1.5rem;
  margin-left: 0.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-button:hover {
  background: #f8f9fa;
  transform: translateY(-1px);
}

.filter-toggle {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0 1rem;
  margin-left: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
}

/* Filtros avanzados */
.advanced-filters {
  padding: 1.5rem;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #555;
  font-size: 0.9rem;
}

.filter-select, .filter-input {
  padding: 0.5rem 0.75rem;
  border: 2px solid #dee2e6;
  border-radius: 0.5rem;
  background: white;
  font-size: 0.9rem;
}

.filter-input {
  width: 100%;
}

.filter-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

/* Resultados */
.results-section {
  margin-top: 2rem;
}

.view-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.view-options, .sort-options {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.view-btn {
  padding: 0.5rem 1rem;
  border: 2px solid #dee2e6;
  background: white;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.sort-select {
  padding: 0.5rem;
  border: 2px solid #dee2e6;
  border-radius: 0.5rem;
  background: white;
}

/* Estados */
.loading-state {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 3px solid #e9ecef;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  text-align: center;
  padding: 3rem;
  color: #dc3545;
}

/* Grid de libros */
.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.book-card {
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.book-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.book-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.book-status {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-available {
  background: #d4edda;
  color: #155724;
}

.status-borrowed {
  background: #fff3cd;
  color: #856404;
}

.status-repair {
  background: #d1ecf1;
  color: #0c5460;
}

.status-lost {
  background: #f8d7da;
  color: #721c24;
}

.book-code {
  font-family: monospace;
  font-size: 0.8rem;
  color: #666;
  background: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.book-cover {
  height: 180px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.cover-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: white;
  position: relative;
}

.book-icon {
  font-size: 4rem;
  opacity: 0.8;
}

.book-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.7rem;
  font-weight: bold;
}

.book-info {
  padding: 1.5rem;
  flex: 1;
}

.book-title {
  font-size: 1.1rem;
  margin: 0 0 0.75rem 0;
  color: #333;
  line-height: 1.3;
}

.book-author {
  color: #666;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.book-details {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.85rem;
}

.book-details p {
  margin: 0.25rem 0;
  color: #555;
}

.book-metadata {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #888;
}

.book-actions {
  padding: 1rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-small {
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
}

/* Vista de lista */
.books-table {
  width: 100%;
  background: white;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.books-table th {
  background: #f8f9fa;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #e9ecef;
}

.books-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.book-code-small {
  font-size: 0.8rem;
  color: #666;
  font-family: monospace;
  margin-top: 0.25rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  font-size: 0.8rem;
  font-weight: bold;
}

.btn-action {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  margin: 0 0.25rem;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: background 0.2s;
}

.btn-action:hover {
  background: #f8f9fa;
}

/* Paginación */
.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 2px solid #dee2e6;
  background: white;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 0.5rem;
}

.page-number {
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-number:hover {
  background: #f8f9fa;
}

.page-number.active {
  background: #667eea;
  color: white;
}

.page-ellipsis {
  padding: 0.5rem;
}

.items-per-page {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
}

/* Estado vacío */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.5;
}

.empty-state h3 {
  margin-bottom: 0.5rem;
  color: #333;
}

.empty-state p {
  color: #666;
  margin-bottom: 1.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .catalog-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .catalog-stats {
    width: 100%;
    justify-content: space-between;
  }
  
  .search-bar-wrapper {
    flex-wrap: wrap;
  }
  
  .search-input {
    order: 1;
    flex: 100%;
    margin-bottom: 0.5rem;
  }
  
  .search-button, .filter-toggle {
    order: 2;
    flex: 1;
  }
  
  .view-controls {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .pagination-section {
    flex-direction: column;
    gap: 1rem;
    align-items: center;
  }
}

.filtered-info {
  font-size: 0.85rem;
  color: #666;
  margin-left: 0.5rem;
  font-style: italic;
}

.book-code-cell {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.small-text {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.25rem;
}

.books-table td {
  vertical-align: middle;
}

.btn-action {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  margin: 0 0.25rem;
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.btn-action:hover:not(:disabled) {
  background: #f8f9fa;
  transform: scale(1.1);
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.book-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.7rem;
  font-weight: bold;
}

/*STILE FOR EDIT CARD */
.tooltip-container {
  position: relative;
  display: inline-block;
}

.tooltip-text {
  visibility: hidden;
  width: 120px;
  background-color: #333;
  color: white;
  text-align: center;
  border-radius: 6px;
  padding: 5px;
  position: absolute;
  z-index: 1;
  bottom: 125%;
  left: 50%;
  margin-left: -60px;
  opacity: 0;
  transition: opacity 0.3s;
  font-size: 0.8rem;
}

.tooltip-container:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
}

/* Responsive improvements */
@media (max-width: 768px) {
  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
  
  .book-details {
    font-size: 0.8rem;
  }
  
  .book-details p {
    margin: 0.2rem 0;
  }
  
  .book-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .book-actions .btn {
    width: 100%;
    justify-content: center;
  }
}
.book-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.btn-danger {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  color: white;
  border: none;
}

.btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #c82333 0%, #bd2130 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.spinner-mini {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.6s linear infinite;
  margin-right: 5px;
}

/* Modal de confirmación */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(2px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #dc3545;
  font-size: 1.3rem;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6c757d;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close-btn:hover {
  background: #f8f9fa;
}

.modal-body {
  padding: 1.5rem;
}

.book-to-delete {
  margin: 1.5rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #dc3545;
}

.book-info h4 {
  margin: 0 0 0.5rem 0;
  color: #212529;
}

.book-info p {
  margin: 0.25rem 0;
  color: #6c757d;
  font-size: 0.95rem;
}

.warning-message {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 6px;
  color: #856404;
}

.warning-icon {
  font-size: 1.5rem;
}

.warning-message p {
  margin: 0;
  font-size: 0.9rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e9ecef;
}

/* Toast de éxito */
.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  max-width: 350px;
  z-index: 3000;
  animation: toastSlideIn 0.3s ease-out;
  border-left: 4px solid #28a745;
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.toast.success {
  border-left-color: #28a745;
}

.toast-icon {
  font-size: 1.8rem;
}

.toast-content {
  flex: 1;
}

.toast-content strong {
  display: block;
  margin-bottom: 0.25rem;
  color: #212529;
}

.toast-content p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.toast-close {
  background: none;
  border: none;
  color: #6c757d;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-close:hover {
  background: #f8f9fa;
}

/* Spinner para botón de eliminación */
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

/* Responsive */
@media (max-width: 768px) {
  .book-actions {
    flex-direction: column;
  }
  
  .book-actions .btn {
    width: 100%;
    justify-content: center;
  }
  
  .modal-content {
    width: 95%;
    margin: 1rem;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .modal-footer .btn {
    width: 100%;
  }
  
  .toast {
    left: 20px;
    right: 20px;
    max-width: none;
  }
}

.catalog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.btn-create-book {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-create-book:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.btn-icon {
  font-size: 1.2rem;
}

.btn-text {
  white-space: nowrap;
}

/* Responsive */
@media (max-width: 768px) {
  .catalog-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
    justify-content: flex-end;
  }
  
  .btn-create-book .btn-text {
    display: none;
  }
  
  .btn-create-book {
    padding: 0.75rem;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    justify-content: center;
  }
}

.btn-loan-books {
  background: linear-gradient(135deg, #ebd2ff 0%, #7300f7 100%);
  color: #212529;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

.btn-details-books {
  background: linear-gradient(135deg, #505050 0%, #ffffff 100%);
  color: #212529;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

.btn-edit-books {
  background: linear-gradient(135deg, #f4ff8f 0%, #c4b10b 100%);
  color: #212529;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

.btn-delete-books {
  background: linear-gradient(135deg, #b12f2f 0%, #e06c00 100%);
  color: #212529;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

/*ESTILOS PARA RECUPERAR*/
.btn-recover-books {
  background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%);
  color: #212529;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

.btn-recover-books:hover {
  background: linear-gradient(135deg, #e0a800 0%, #d39e00 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 193, 7, 0.3);
}

.badge-count {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #dc3545;
  color: white;
  font-size: 0.75rem;
  font-weight: bold;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 0.25rem;
}

/* Responsive */
@media (max-width: 768px) {
  .btn-recover-books .btn-text {
    display: none;
  }
  
  .btn-recover-books {
    padding: 0.75rem;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    justify-content: center;
  }
  
  .badge-count {
    top: 0;
    right: 0;
    font-size: 0.7rem;
    min-width: 18px;
    height: 18px;
  }
}

</style>