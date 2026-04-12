<template>
  <div class="book-catalog">

    <!-- Header -->
    <div class="catalog-header">
      <div class="header-content">
        <h1>📚 Catálogo de la Biblioteca</h1>
        <p class="subtitle">Libros pertenecientes a la biblioteca universitaria</p>
      </div>
      <div class="catalog-stats">
        <div class="stat-pill">
          <span class="stat-num">{{ stats.totalBooks }}</span>
          <span class="stat-lbl">Libros totales</span>
        </div>
        <div class="stat-pill">
          <span class="stat-num">{{ stats.availableBooks }}</span>
          <span class="stat-lbl">Disponibles</span>
        </div>
        <div class="stat-pill">
          <span class="stat-num">{{ stats.prestableBooks }}</span>
          <span class="stat-lbl">Prestables</span>
        </div>
      </div>
    </div>

    <!-- Búsqueda -->
    <div class="search-section">
      <div class="search-bar">
        <span class="search-icon-inner">🔍</span>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar por título, autor, ISBN, editorial..."
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button @click="showAdvancedFilters = !showAdvancedFilters" class="btn-filter">
          {{ showAdvancedFilters ? '▲' : '▼' }} Filtros
        </button>
        <button @click="handleSearch" class="btn-search">Buscar</button>
      </div>

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
            <div v-if="filters.estado_id === '1'" class="filter-hint">Estado por defecto: Disponible</div>
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
            <input v-model="filters.ano_adquisicion" type="number" placeholder="Ej: 2023" class="filter-input" min="1900" :max="new Date().getFullYear()" />
          </div>
          <div class="filter-group">
            <label>Editorial:</label>
            <select v-model="filters.editorial_id" class="filter-select">
              <option value="">Todas las editoriales</option>
              <option v-for="e in editoriales" :key="e.id" :value="e.id">{{ e.nombre }}</option>
            </select>
          </div>
        </div>
        <div class="filter-actions">
          <button @click="currentPage = 1" class="btn btn-primary">Aplicar Filtros</button>
          <button @click="resetFilters" class="btn btn-outline">Limpiar Filtros</button>
        </div>
      </div>
    </div>

    <!-- Resultados -->
    <div class="results-section">

      <div class="view-controls">
        <div class="view-options">
          <button @click="viewMode = 'grid'" :class="{ active: viewMode === 'grid' }" class="view-btn">⊞ Cuadrícula</button>
          <button @click="viewMode = 'list'" :class="{ active: viewMode === 'list' }" class="view-btn">☰ Lista</button>
        </div>
        <div class="sort-options">
          <label>Ordenar por:</label>
          <select v-model="sortBy" @change="currentPage = 1" class="sort-select">
            <option value="titulo">Título (A-Z)</option>
            <option value="autor">Autor (A-Z)</option>
            <option value="edicion">Edición (Más reciente)</option>
            <option value="fecha_adquisicion">Fecha adquisición</option>
          </select>
        </div>
      </div>

      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando catálogo...</p>
      </div>

      <div v-if="error" class="error-state">
        <p>Error: {{ error }}</p>
        <button @click="loadBooks" class="btn btn-primary">Reintentar</button>
      </div>

      <!-- ── CUADRÍCULA ── -->
      <div v-if="viewMode === 'grid' && !isLoading && !error" class="books-grid">
        <div v-for="book in paginatedBooks" :key="book.id" class="book-card">

          <div class="book-card-top" :class="getCardColorClass(book.id)">
            <span class="book-icon-lg">📖</span>
            <div class="badge-status" :class="getStatusClass(book)">{{ getStatusText(book) }}</div>
            <div class="card-code-badge">{{ book.codigo_decimal || 'N/A' }}</div>
            <div v-if="book.es_prestable && book.edicion != 1" class="badge-prestable">Prestable</div>
          </div>

          <div class="book-body">
            <h3 class="book-title">{{ book.titulo }}</h3>
            <p class="book-author">✍️ {{ book.autor }}</p>
            <div class="book-details">
              <p><strong>ISBN:</strong> {{ book.isbn || 'No disponible' }}</p>
              <p><strong>Etiqueta:</strong> {{ book.etiqueta }}</p>
              <p><strong>Ejemplar:</strong> {{ book.numero_ejemplar }}</p>
              <p><strong>Edición:</strong> {{ book.edicion }}</p>
              <p><strong>Páginas:</strong> {{ book.numero_paginas }}</p>
              <p v-if="book.editorial_nombre"><strong>Editorial:</strong> {{ book.editorial_nombre }}</p>
              <p v-if="book.area_conocimiento_nombre"><strong>Área:</strong> {{ book.area_conocimiento_nombre }}</p>
            </div>
            <div class="book-metadata">
              <span class="metadata-item">ID: {{ book.id }}</span>
            </div>
          </div>

          <div class="book-actions">
            <button @click="viewBookDetails(book.id)" class="btn-detail">Detalles...</button>
            <button v-if="book.es_prestable && book.estado_id === 1 && userCanRequestLoans" @click="requestLoanModal(book)" class="btn-loan" :disabled="multasPendientes" :title="multasPendientes ? 'Tienes multas pendientes' : 'Solicitar préstamo'">
              {{ multasPendientes ? '🚫 Bloqueado' : 'Solicitar' }}
            </button>
            <button v-if="userCanRequestLoans && book.estado_id === 2" @click="handleReturn(book)" class="btn-devolver">Devolver</button>
            <button v-if="canEditBooks" @click="goToEditPage(book.id)" class="btn-editar" :title="`Editar: ${book.titulo}`">Editar</button>
            <button
              v-if="canDelete"
              @click="confirmDelete(book)"
              class="btn-eliminar"
              :disabled="isDeleting || book.estado_nombre === 'Prestado'"
              :title="book.estado_nombre === 'Prestado' ? 'No se puede eliminar porque está prestado' : 'Eliminar libro'"
            >
              <span v-if="isDeleting && deletingBookId === book.id" class="spinner-mini"></span>
              <span v-else>Eliminar</span>
            </button>
            <button v-if="canRecoverBooks && book.estado_id === 4" @click="recoverBook(book)" class="btn-recuperar">Recuperar</button>
          </div>
        </div>

        <!-- Modal: Eliminar -->
        <div v-if="showDeleteModal" class="modal-overlay">
          <div class="modal-content">
            <div class="modal-header">
              <h3>Confirmar Eliminación</h3>
              <button @click="closeModal" class="modal-close-btn">×</button>
            </div>
            <div class="modal-body">
              <p>¿Estás seguro de que deseas eliminar el siguiente libro?</p>
              <div class="book-to-delete">
                <div class="book-info-modal">
                  <h4>{{ bookToDelete?.titulo }}</h4>
                  <p><strong>Autor:</strong> {{ bookToDelete?.autor }}</p>
                  <p><strong>Código:</strong> {{ bookToDelete?.codigo_decimal }}</p>
                  <p><strong>Edición:</strong> {{ bookToDelete?.edicion }}</p>
                </div>
                <div class="warning-message">
                  <div class="warning-icon">⚠️</div>
                  <p>El libro será retirado.</p>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button @click="closeModal" class="btn-modal-cancel" :disabled="isDeleting">Cancelar</button>
              <button @click="deleteBook" class="btn-modal-delete" :disabled="isDeleting">
                <span v-if="isDeleting" class="spinner-small"></span>
                {{ isDeleting ? 'Eliminando...' : 'Sí, Eliminar' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal: Préstamo -->
      <div v-if="showLoanModal" class="modal-overlay">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Crear Préstamo</h3>
            <button @click="cerrarLoanModal" class="modal-close-btn">×</button>
          </div>
          <div class="modal-body">
            <p><strong>Libro:</strong> {{ selectedBook?.titulo }}</p>
            <p><strong>Autor:</strong> {{ selectedBook?.autor }}</p>
            <div class="filter-group" style="margin-top:1rem">
              <label>Fecha de devolución:</label>
              <input type="date" v-model="loanDate" class="filter-input" :min="fechaMinima"/><p v-if="loanDate && !fechaEsValida" class="fecha-error">La fecha de devolución no puede ser anterior a hoy.</p>
            </div>
            <div class="filter-group" style="margin-top:.75rem">
              <label>Observaciones:</label>
              <textarea v-model="loanObservaciones" class="filter-input"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="cerrarLoanModal" class="btn-modal-cancel">Cancelar</button>
            <button @click="requestLoan" class="btn-modal-confirm" :disabled="isProcessingLoan">
              {{ isProcessingLoan ? 'Creando...' : 'Confirmar Préstamo' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Toast eliminacion -->
      <div v-if="showSuccessToast" class="toast">
        <span class="toast-icon">✅</span>
        <div class="toast-content">
          <strong>Libro eliminado correctamente</strong>
          <p>El libro ha sido eliminado del sistema</p>
        </div>
        <button @click="showSuccessToast = false" class="toast-close">×</button>
      </div>

      <!-- Toast prestamo -->
      <div v-if="showLoanSuccessToast" class="toast toast-loan-success">
        <span class="toast-icon">📚</span>
        <div class="toast-content">
          <strong>Préstamo creado correctamente</strong>
          <p>Recuerda devolver el libro antes de la fecha límite</p>
        </div>
        <button @click="showLoanSuccessToast = false" class="toast-close">×</button>
      </div>

      <!-- ── LISTA ── -->
      <div v-if="viewMode === 'list' && !isLoading && !error" class="books-list">
        <div class="table-wrap">
          <table class="table-ui">
            <thead>
              <tr>
                <th>Código</th>
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
                  <div class="td-code">{{ book.codigo_decimal || 'N/A' }}</div>
                  <div class="td-sub">{{ book.etiqueta }}-{{ book.numero_ejemplar }}</div>
                </td>
                <td>
                  <div class="td-title">{{ book.titulo }}</div>
                  <div class="td-sub">Ed. {{ book.edicion }}</div>
                </td>
                <td class="td-author">{{ book.autor }}</td>
                <td><div class="td-sub">{{ book.editorial_nombre || 'N/A' }}</div></td>
                <td>
                  <span :class="getStatusClass(book)" class="status-pill">{{ getStatusText(book) }}</span>
                  <div class="td-sub" v-if="book.es_prestable" style="margin-top:.25rem">🔄 Prestable</div>
                </td>
                <td>
                  <div class="td-actions">
                    <button @click="viewBookDetails(book.id)" class="tbl-btn" title="Ver detalles">🔍</button>
                    <button v-if="book.es_prestable && book.estado_id === 1 && userCanRequestLoans" @click="requestLoanModal(book)" class="btn-loan" :disabled="multasPendientes" :title="multasPendientes ? 'Tienes multas pendientes' : 'Solicitar préstamo'">
                      {{ multasPendientes ? '🚫 Bloqueado' : 'Solicitar' }}
                    </button>
                    <button v-if="canEditBooks" @click="goToEditPage(book.id)" class="tbl-btn tbl-gold" title="Editar">✏️</button>
                    <button v-if="canDelete" @click="confirmDelete(book)" class="tbl-btn tbl-red" title="Eliminar" :disabled="book.estado_nombre === 'Prestado'">🗑️</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Paginación -->
      <div v-if="!isLoading && !error && books.length > 0" class="pagination-section">
        <div class="pagination-info">
          Mostrando {{ startItem }}–{{ endItem }} de {{ filteredBooks.length }} libros
          <span v-if="searchQuery || hasActiveFilters" class="filtered-info">(Filtrado de {{ books.length }} total)</span>
        </div>
        <div class="pagination-controls">
          <button @click="prevPage" :disabled="currentPage === 1" class="pbtn">← Anterior</button>
          <div class="page-numbers">
            <span v-for="page in visiblePages" :key="page" @click="goToPage(page)" :class="{ active: page === currentPage }" class="page-number">{{ page }}</span>
            <span v-if="hasMorePages" class="page-ellipsis">...</span>
          </div>
          <button @click="nextPage" :disabled="currentPage === totalPages" class="pbtn">Siguiente →</button>
        </div>
        <div class="items-per-page">
          <label>Mostrar:</label>
          <select v-model="itemsPerPage" @change="currentPage = 1" class="page-select">
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
        <p v-if="searchQuery || hasActiveFilters">No hay resultados. Intenta con otros términos o ajusta los filtros.</p>
        <p v-else>No hay libros disponibles en el catálogo.</p>
        <button @click="resetFilters" class="btn-loan" style="margin-top:1rem">🔄 Mostrar todos los libros</button>
      </div>

    </div>
  </div>
</template>


<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { bookService } from '@/services/books'
import { useAuthStore } from '@/stores/auth'
import { usePermissions } from '@/composables/usePermissions'
import { prestamoLibroService } from '@/services/PrestamoLibro'
import { useMultas } from '@/composables/useMultas'
import { multasService } from '@/services/multas'

import '@/styles/buttons.css'

const router = useRouter()
const authStore = useAuthStore()

const { hasPermission } = usePermissions()
const {tieneMultasPendientes} = useMultas()

// ── Estado UI ──────────────────────────────────────────────────────────────
const searchQuery         = ref('')
const showAdvancedFilters = ref(false)
const viewMode            = ref('grid')
const sortBy              = ref('titulo')
const isLoading           = ref(false)
const error               = ref(null)
const currentPage         = ref(1)
const itemsPerPage        = ref(12)

// ── Estado préstamo ────────────────────────────────────────────────────────
const isProcessingLoan    = ref(false)
const showLoanModal       = ref(false)
const selectedBook        = ref(null)
const loanDate            = ref('')
const loanObservaciones   = ref('')

// ── Estado multas ────────────────────────────────────────────────────────
const multasPendientes = ref(false)

// ── Estado eliminación ─────────────────────────────────────────────────────
const isDeleting          = ref(false)
const deletingBookId      = ref(null)
const showDeleteModal     = ref(false)
const bookToDelete        = ref(null)
const showSuccessToast    = ref(false)

const showLoanSuccessToast = ref(false)

// ── Datos ──────────────────────────────────────────────────────────────────
const books       = ref([])
const editoriales = ref([])
const stats       = ref({ totalBooks: 0, availableBooks: 0, prestableBooks: 0 })

const filters = ref({
  estado_id:       '1',
  es_prestable:    '',
  ano_adquisicion: '',
  editorial_id:    ''
})

// ── Permisos ───────────────────────────────────────────────────────────────
const canEditBooks        = computed(() => hasPermission('canEditBooks'))
const canDelete           = computed(() => hasPermission('canDeleteBooks'))
const canRecoverBooks     = computed(() => hasPermission('canRecoverBooks'))
const canSeeRetiredBooks  = computed(() => hasPermission('canSeeRetiredBooks'))
const userCanRequestLoans = computed(() => hasPermission('canRequestLoans'))

// ── Computed ───────────────────────────────────────────────────────────────
const filteredBooks = computed(() => {
  let result = books.value

  if (filters.value.estado_id)
    result = result.filter(b => b.estado_id === parseInt(filters.value.estado_id))

  if (filters.value.es_prestable !== '')
    result = result.filter(b => b.es_prestable === (filters.value.es_prestable === 'true'))

  if (filters.value.editorial_id)
    result = result.filter(b => b.editorial_id === parseInt(filters.value.editorial_id))

  if (filters.value.ano_adquisicion) {
    const year = parseInt(filters.value.ano_adquisicion)
    result = result.filter(b => b.fecha_adquisicion && new Date(b.fecha_adquisicion).getFullYear() === year)
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    result = result.filter(b =>
      b.titulo?.toLowerCase().includes(q) ||
      b.autor?.toLowerCase().includes(q) ||
      b.isbn?.toLowerCase().includes(q) ||
      b.editorial_nombre?.toLowerCase().includes(q) ||
      b.area_conocimiento_nombre?.toLowerCase().includes(q) ||
      b.codigo_decimal?.toLowerCase().includes(q)
    )
  }

  return [...result].sort((a, b) => {
    switch (sortBy.value) {
      case 'autor':             return (a.autor || '').localeCompare(b.autor || '')
      case 'edicion':           return (b.edicion || 0) - (a.edicion || 0)
      case 'fecha_adquisicion': {
        const da = a.fecha_adquisicion ? new Date(a.fecha_adquisicion) : new Date(0)
        const db = b.fecha_adquisicion ? new Date(b.fecha_adquisicion) : new Date(0)
        return db - da
      }
      default: return (a.titulo || '').localeCompare(b.titulo || '')
    }
  })
})

const totalPages   = computed(() => Math.ceil(filteredBooks.value.length / itemsPerPage.value) || 1)
const paginatedBooks = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return filteredBooks.value.slice(start, start + itemsPerPage.value)
})
const startItem    = computed(() => (currentPage.value - 1) * itemsPerPage.value + 1)
const endItem      = computed(() => Math.min(currentPage.value * itemsPerPage.value, filteredBooks.value.length))
const visiblePages = computed(() => {
  const max = 5, total = totalPages.value
  if (total <= max) return Array.from({ length: total }, (_, i) => i + 1)
  let start = Math.max(1, currentPage.value - 2)
  const end = Math.min(total, start + max - 1)
  if (end - start + 1 < max) start = end - max + 1
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})
const hasMorePages    = computed(() => currentPage.value < totalPages.value - 2)
const hasActiveFilters = computed(() => Object.values(filters.value).some(v => v !== '' && v != null))

// ── Carga de datos ─────────────────────────────────────────────────────────
const loadBooks = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await bookService.getBooks()
    books.value = response?.libros ?? (Array.isArray(response) ? response : [])
    calculateStats()
    extractEditoriales()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error cargando el catálogo'
  } finally {
    isLoading.value = false
  }
}

const calculateStats = () => {
  stats.value = {
    totalBooks:     books.value.length,
    availableBooks: books.value.filter(b => b.estado_id === 1).length,
    prestableBooks: books.value.filter(b => b.es_prestable).length
  }
}

const extractEditoriales = () => {
  const map = new Map()
  books.value.forEach(b => {
    if (b.editorial_id && b.editorial_nombre && !map.has(b.editorial_id))
      map.set(b.editorial_id, { id: b.editorial_id, nombre: b.editorial_nombre })
  })
  editoriales.value = Array.from(map.values())
}

// ── Búsqueda ───────────────────────────────────────────────────────────────
const handleSearch = async () => {
  currentPage.value = 1
  if (!searchQuery.value.trim()) { loadBooks(); return }
  try {
    isLoading.value = true
    const response = await bookService.searchBooks(searchQuery.value, filters.value)
    if (response?.libros) books.value = response.libros
    calculateStats()
  } catch {
    // fallback: filteredBooks aplica searchQuery localmente
  } finally {
    isLoading.value = false
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  filters.value = { estado_id: '', es_prestable: '', ano_adquisicion: '', editorial_id: '' }
  currentPage.value = 1
  loadBooks()
}


//VERIFICACION DE MULTAS
const verificarMultas = async () => {
  try {
    const userId = authStore.userId
    if (!userId) return
    const multas = await multasService.getMultasByUsuario(userId)
    multasPendientes.value = Array.isArray(multas) && multas.length > 0
    if (authStore.actualizarEstadoMultas) authStore.actualizarEstadoMultas(multas)
  } catch { /* silencioso */ }
}

//VALIDACION DE FECHAS
const fechaMinima = computed(() => {
  const hoy = new Date()
  return hoy.toISOString().split('T')[0]
})

const fechaEsValida = computed(() => {
  if (!loanDate.value) return false
  return loanDate.value >= fechaMinima.value
})

// ── Helpers ────────────────────────────────────────────────────────────────
const CARD_COLORS = ['card-c1', 'card-c2', 'card-c3']
const getCardColorClass = (id) => CARD_COLORS[id % CARD_COLORS.length]

const STATUS_CLASS = { 1: 'status-available', 2: 'status-borrowed', 3: 'status-repair', 4: 'status-lost' }
const STATUS_TEXT  = { 1: '✅ Disponible', 2: '⏳ Prestado', 3: '🔧 En reparación', 4: '❌ Retirado' }
const getStatusClass = (book) => STATUS_CLASS[book.estado_id] || 'status-unknown'
const getStatusText  = (book) => STATUS_TEXT[book.estado_id]  || book.estado_nombre || 'Desconocido'

// ── Navegación ─────────────────────────────────────────────────────────────
const goToEditPage    = (id) => router.push(`/admin/libros/editar/${id}`)
const viewBookDetails = (id) => router.push(`/libros/${id}`)

// ── Paginación ─────────────────────────────────────────────────────────────
const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const goToPage = (page) => { if (page >= 1 && page <= totalPages.value) currentPage.value = page }

// ── Modales ────────────────────────────────────────────────────────────────
const requestLoanModal = (book) => {
  if (!userCanRequestLoans.value) { alert('No tienes permisos para crear préstamos'); return }
  selectedBook.value = book
  loanDate.value = ''
  loanObservaciones.value = ''
  showLoanModal.value = true
}
const cerrarLoanModal = () => { showLoanModal.value = false; selectedBook.value = null }

const confirmDelete = (book) => {
  if (!canDelete.value) { alert('No tienes permisos para eliminar libros'); return }
  bookToDelete.value = book
  showDeleteModal.value = true
}
const closeModal = () => {
  if (isDeleting.value) return
  showDeleteModal.value = false
  bookToDelete.value = null
}

// ── CRUD ───────────────────────────────────────────────────────────────────
const deleteBook = async () => {
  if (!bookToDelete.value?.id || isDeleting.value) return
  isDeleting.value = true
  deletingBookId.value = bookToDelete.value.id
  try {
    await bookService.deleteBook(bookToDelete.value.id)
    books.value = books.value.filter(b => b.id !== bookToDelete.value.id)
    showDeleteModal.value = false
    showSuccessToast.value = true
    setTimeout(() => { showSuccessToast.value = false }, 3000)
  } catch (err) {
    alert(`Error al eliminar: ${err.response?.data?.detail || err.message}`)
  } finally {
    isDeleting.value = false
    deletingBookId.value = null
    bookToDelete.value = null
  }
}

const recoverBook = async (book) => {
  if (!canRecoverBooks.value) { alert('No tienes permisos para recuperar libros'); return }
  if (!confirm(`¿Recuperar el libro "${book.titulo}"?\nEl libro pasará a estado "Disponible".`)) return
  try {
    await bookService.reactivateBook(book.id)
    const target = books.value.find(b => b.id === book.id)
    if (target) { target.estado_id = 1; target.estado_nombre = 'Disponible' }
    alert(`✅ Libro "${book.titulo}" recuperado.`)
  } catch {
    alert('❌ Error al recuperar el libro')
  }
}

//PRESTAMO

const requestLoan = async () => {
  if (!selectedBook.value) return
 
  if (!loanDate.value) {
    alert('Debes seleccionar una fecha de devolución')
    return
  }
 
  if (loanDate.value < fechaMinima.value) {
    alert('La fecha de devolución no puede ser anterior a hoy')
    return
  }
 
  // Bloquear si tiene multas pendientes
  if (multasPendientes.value) {
    alert('No puedes solicitar préstamos con multas pendientes. Liquida tus multas en la biblioteca.')
    return
  }
 
  isProcessingLoan.value = true
  try {
    await prestamoLibroService.crearPrestamo({
      libro_id:                  selectedBook.value.id,
      usuario_prestado_id:       authStore.user?.id,
      // Enviar como string ISO sin conversión que causa desfase de zona horaria
      fecha_devolucion_esperada: `${loanDate.value}T12:00:00`,
      observaciones:             loanObservaciones.value
    })
 
    const target = books.value.find(b => b.id === selectedBook.value.id)
    if (target) { target.estado_id = 2; target.estado_nombre = 'Prestado' }
 
    cerrarLoanModal()
 
    // Toast en lugar de alert
    showLoanSuccessToast.value = true
    setTimeout(() => { showLoanSuccessToast.value = false }, 3500)
 
  } catch (err) {
    const detail = err.response?.data?.detail || 'Error al crear préstamo'
 
    // Si el error es por multas (403), mostrar mensaje claro
    if (err.response?.status === 403) {
      alert(`⚠️ ${detail}`)
    } else {
      alert(detail)
    }
  } finally {
    isProcessingLoan.value = false
  }
}

const handleReturn = async (book) => {
  isProcessingLoan.value = true
  try {
    const prestamos = await prestamoLibroService.getPrestamos({ libro_id: book.id, solo_vigentes: true })
    if (!prestamos.length) { alert('No se encontró préstamo vigente para este libro'); return }
    await prestamoLibroService.devolverPrestamo(prestamos[0].id, 'Devuelto desde catálogo')
    book.estado_id = 1
    book.estado_nombre = 'Disponible'
    alert(`Libro "${book.titulo}" devuelto correctamente`)
  } catch (err) {
    alert(err.response?.data?.detail || 'Error al devolver libro')
  } finally {
    isProcessingLoan.value = false
  }
}

// ── Watchers ───────────────────────────────────────────────────────────────
let searchTimeout
watch(searchQuery, (val) => {
  clearTimeout(searchTimeout)
  if (val.trim()) searchTimeout = setTimeout(() => { currentPage.value = 1 }, 500)
})
watch(filters, () => { currentPage.value = 1 }, { deep: true })


onMounted(() => { loadBooks(); verificarMultas() })


</script>


<style scoped>
/* ── Fuentes ────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

/* ── Variables ─────────────────────────────────────────────────────────── */
:root {
  --green-dark:   #1a4731;
  --green-mid:    #2d6a4f;
  --green-light:  #52b788;
  --green-pale:   #d8f3dc;
  --gold-dark:    #92650a;
  --gold-mid:     #c9900c;
  --gold-light:   #f4c542;
  --gold-pale:    #fef9e7;
  --cream:        #f5f0e8;
  --cream-border: #d4e8da;
  --card-bg:      #fffef9;
  --shadow-sm:    0 2px 12px rgba(26,47,26,.10);
  --shadow-md:    0 8px 24px rgba(26,71,49,.15);
}

/* ── Layout ─────────────────────────────────────────────────────────────── */
.book-catalog {
  font-family: 'DM Sans', sans-serif;
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  background:
    radial-gradient(ellipse 80% 40% at 10% 0%,  rgba(82,183,136,.13) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 90% 100%, rgba(201,144,12,.10) 0%, transparent 55%),
    #f5f0e8;
  min-height: 100vh;
}

/* ── Header ─────────────────────────────────────────────────────────────── */
.catalog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #1a4731 0%, #2d6a4f 60%, #3a7d5e 100%);
  border-radius: 16px;
  color: white;
  position: relative;
  overflow: hidden;
}
.catalog-header::before {
  content: '';
  position: absolute; inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E");
  pointer-events: none;
}
.header-content { position: relative; }
.header-content h1 {
  font-family: 'Playfair Display', serif;
  font-size: 1.8rem; font-weight: 700;
  color: #fff; margin-bottom: .25rem;
}
.subtitle { font-size: .9rem; color: rgba(255,255,255,.75); }

.catalog-stats { display: flex; gap: 1rem; position: relative; }
.stat-pill {
  background: rgba(255,255,255,.12);
  border: 1px solid rgba(255,255,255,.2);
  border-radius: 12px;
  padding: .65rem 1.1rem;
  text-align: center;
}
.stat-num { display: block; font-size: 1.4rem; font-weight: 700; color: #f4c542; }
.stat-lbl { font-size: .72rem; color: rgba(255,255,255,.78); white-space: nowrap; }

/* ── Búsqueda ────────────────────────────────────────────────────────────── */
.search-section { margin-bottom: 1.25rem; }

.search-bar {
  display: flex;
  align-items: center;
  gap: .5rem;
  padding: .6rem .85rem;
  background: #ffffff;
  border: 1.5px solid var(--cream-border);
  border-radius: 14px;
  box-shadow: var(--shadow-sm);
}
.search-icon-inner { font-size: 1rem; color: #9ab5a0; }
.search-input {
  flex: 1; border: none; outline: none;
  font-size: .95rem; font-family: 'DM Sans', sans-serif;
  background: transparent; color: #1a2e1a;
}
.search-input::placeholder { color: #9ab5a0; }

.btn-search {
  background: var(--green-mid); color: #fff;
  border: none; border-radius: 10px;
  padding: .45rem 1.1rem; font-size: .85rem; font-weight: 600;
  cursor: pointer; font-family: 'DM Sans', sans-serif;
  transition: background .2s, color .2s;
}
.btn-search:hover { background: #111; color: #fff; }

.btn-filter {
  background: var(--gold-pale); color: var(--gold-dark);
  border: 1.5px solid var(--gold-light); border-radius: 10px;
  padding: .45rem .9rem; font-size: .83rem; font-weight: 500;
  cursor: pointer; font-family: 'DM Sans', sans-serif;
  transition: background .2s, color .2s, border-color .2s;
}
.btn-filter:hover { background: #111; color: #fff; border-color: #111; }

/* Filtros avanzados */
.advanced-filters {
  margin-top: .75rem;
  padding: 1.25rem 1.5rem;
  background: var(--card-bg);
  border: 1.5px solid var(--cream-border);
  border-radius: 14px;
  box-shadow: var(--shadow-sm);
}
.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem; margin-bottom: 1rem;
}
.filter-group { display: flex; flex-direction: column; gap: .4rem; }
.filter-group label { font-size: .83rem; font-weight: 600; color: var(--green-dark); }
.filter-select, .filter-input {
  padding: .45rem .75rem;
  border: 1.5px solid var(--cream-border);
  border-radius: 8px; background: #fff;
  font-size: .88rem; font-family: 'DM Sans', sans-serif;
  color: #1a2e1a; outline: none; width: 100%;
  transition: border-color .2s;
}
.filter-select:focus, .filter-input:focus { border-color: var(--green-light); }
.filter-hint { font-size: .75rem; color: #9ab5a0; font-style: italic; }
.filter-actions { display: flex; gap: .75rem; justify-content: flex-end; }

/* ── Controles de vista ──────────────────────────────────────────────────── */
.results-section { margin-top: .5rem; }
.view-controls {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1rem; padding: .75rem 1rem;
  background: var(--card-bg);
  border: 1.5px solid var(--cream-border);
  border-radius: 12px; box-shadow: var(--shadow-sm);
}
.view-options, .sort-options { display: flex; align-items: center; gap: .5rem; }
.sort-options label { font-size: .83rem; color: #5a7a5a; }

.view-btn {
  background: #fff; color: var(--green-mid);
  border: 1.5px solid var(--cream-border);
  border-radius: 8px; padding: .38rem .9rem;
  font-size: .82rem; font-weight: 500; cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: all .2s;
}
.view-btn:hover { background: #111; color: #fff; border-color: #111; }
.view-btn.active { background: var(--green-mid); color: #000000; border-color: var(--green-mid); }
.view-btn.active:hover { background: #fffbfb; border-color: #111; }

.sort-select {
  border: 1.5px solid var(--cream-border); border-radius: 8px;
  padding: .35rem .65rem; font-size: .82rem;
  font-family: 'DM Sans', sans-serif; color: var(--green-dark);
  background: #fff; outline: none; cursor: pointer;
}

/* ── Estados ─────────────────────────────────────────────────────────────── */
.loading-state { text-align: center; padding: 3rem; }
.spinner {
  width: 44px; height: 44px;
  border: 3px solid var(--green-pale);
  border-top-color: var(--green-mid);
  border-radius: 50%; margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}
.error-state { text-align: center; padding: 3rem; color: #b91c1c; }

/* ── Grid ────────────────────────────────────────────────────────────────── */
.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.25rem; margin-bottom: 1.5rem;
}
.book-card {
  background: var(--card-bg);
  border: 1.5px solid var(--cream-border);
  border-radius: 14px; overflow: hidden;
  box-shadow: var(--shadow-sm);
  display: flex; flex-direction: column;
  transition: transform .2s, box-shadow .2s;
}
.book-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); }

.book-card-top {
  height: 110px; display: flex; align-items: center; justify-content: center;
  position: relative;
}
.card-c1 { background: linear-gradient(135deg, #1a4731, #3a7d5e); }
.card-c2 { background: linear-gradient(135deg, #92650a, #c9900c); }
.card-c3 { background: linear-gradient(135deg, #1a4731, #c9900c 130%); }

.book-icon-lg { font-size: 2.8rem; opacity: .85; }
.badge-status {
  position: absolute; top: .55rem; left: .55rem;
  padding: .2rem .6rem; border-radius: 20px;
  font-size: .7rem; font-weight: 700;
}
.card-code-badge {
  position: absolute; top: .55rem; right: .55rem;
  background: rgba(0,0,0,.28); color: rgba(255,255,255,.9);
  padding: .15rem .45rem; border-radius: 6px;
  font-size: .68rem; font-family: monospace;
}
.badge-prestable {
  position: absolute; bottom: .55rem; right: .55rem;
  background: rgba(255,255,255,.88); color: var(--green-mid);
  padding: .18rem .5rem; border-radius: 20px;
  font-size: .68rem; font-weight: 700;
}

.status-available { background: rgba(255,255,255,.9); color: #1a4731; }
.status-borrowed  { background: rgba(244,197,66,.9);  color: #5a3a00; }
.status-repair    { background: rgba(219,234,254,.9); color: #1e3a5f; }
.status-lost      { background: rgba(254,226,226,.9); color: #7f1d1d; }

.book-body { padding: 1.1rem 1.1rem .75rem; flex: 1; }
.book-title {
  font-family: 'Playfair Display', serif;
  font-size: 1rem; font-weight: 600;
  color: #1a2e1a; line-height: 1.35; margin-bottom: .3rem;
}
.book-author { font-size: .78rem; color: #5a7a5a; margin-bottom: .75rem; }
.book-details {
  background: #f3faf5; padding: .75rem;
  border-radius: 8px; margin-bottom: .65rem;
  font-size: .78rem;
}
.book-details p { margin: .2rem 0; color: #3d5a3d; }
.book-details strong { color: var(--green-dark); }
.book-metadata { font-size: .72rem; color: #9ab5a0; }

/* ── Botones de acción en cards ──────────────────────────────────────────── */
.book-actions {
  padding: .75rem 1rem;
  border-top: 1.5px solid #eef5f0;
  display: flex; gap: .4rem; flex-wrap: wrap;
}

/* BASE compartida */
.btn-detail, .btn-loan, .btn-devolver,
.btn-editar, .btn-eliminar, .btn-recuperar {
  border-radius: 8px; padding: .38rem .8rem;
  font-size: .76rem; font-weight: 600; cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: background .18s, color .18s, border-color .18s, transform .15s;
  display: inline-flex; align-items: center; gap: .3rem;
  border: 1.5px solid transparent;
}
.btn-detail, .btn-loan, .btn-devolver,
.btn-editar, .btn-eliminar, .btn-recuperar {
  transform: translateY(0);
}
.btn-detail:hover, .btn-loan:hover, .btn-devolver:hover,
.btn-editar:hover, .btn-eliminar:hover, .btn-recuperar:hover {
  background: #111 !important;
  color: #fff !important;
  border-color: #111 !important;
  transform: translateY(-1px);
}
.btn-detail:disabled, .btn-eliminar:disabled {
  opacity: .45; cursor: not-allowed; transform: none !important;
}

.btn-detail   { background: #f0f7f2; color: var(--green-mid);  border-color: #b8ddc8; }
.btn-loan     { background: var(--green-mid); color: #000000; border-color: var(--green-mid); box-shadow: 0 2px 8px rgba(45,106,79,.25); }
.btn-devolver { background: #fef9e7; color: var(--gold-dark); border-color: var(--gold-light); }
.btn-editar   { background: #fef3cc; color: #7a5200; border-color: var(--gold-light); }
.btn-eliminar { background: #fff0f0; color: #b91c1c; border-color: #fca5a5; }
.btn-recuperar{ background: linear-gradient(135deg, #fef9e7, #fde68a); color: #7a5200; border-color: var(--gold-mid); }

/* Botones genéricos (filtros) */
.btn { border-radius: 8px; padding: .45rem 1rem; font-size: .85rem; font-weight: 600; cursor: pointer; font-family: 'DM Sans', sans-serif; transition: all .18s; border: 1.5px solid transparent; }
.btn-primary { background: var(--green-mid); color: #fff; border-color: var(--green-mid); }
.btn-primary:hover { background: #111; border-color: #111; }
.btn-outline { background: #fff; color: var(--green-mid); border-color: var(--cream-border); }
.btn-outline:hover { background: #111; color: #fff; border-color: #111; }

/* ── Tabla ───────────────────────────────────────────────────────────────── */
.books-list { margin-bottom: 1.5rem; }
.table-wrap {
  background: var(--card-bg);
  border: 1.5px solid var(--cream-border);
  border-radius: 14px; overflow: hidden;
  box-shadow: var(--shadow-sm);
}
.table-ui { width: 100%; border-collapse: collapse; font-size: .83rem; }

.table-ui thead { background: linear-gradient(135deg, #1a4731, #2d6a4f); }
.table-ui thead th {
  padding: .8rem 1rem; text-align: left;
  color: rgba(255,255,255,.92); font-weight: 600;
  font-size: .76rem; letter-spacing: .05em; text-transform: uppercase;
}
.table-ui tbody tr {
  border-bottom: 1px solid #eef5f0;
  transition: background .15s;
}
.table-ui tbody tr:last-child { border-bottom: none; }
.table-ui tbody tr:hover { background: #f0f9f4; }
.table-ui tbody tr:nth-child(even) { background: #fafef8; }
.table-ui tbody tr:nth-child(even):hover { background: #edf7f1; }
.table-ui td { padding: .72rem 1rem; vertical-align: middle; color: #1a2e1a; }

.td-code { font-family: monospace; font-size: .82rem; color: var(--green-mid); font-weight: 700; }
.td-sub  { font-size: .72rem; color: #7a9a7a; margin-top: .1rem; }
.td-title { font-weight: 600; color: #1a2e1a; }
.td-author { color: #3d5a3d; }

.status-pill {
  display: inline-flex; align-items: center; gap: .3rem;
  padding: .25rem .65rem; border-radius: 20px;
  font-size: .72rem; font-weight: 700; white-space: nowrap;
}
.status-available { background: #d8f3dc; color: #1a4731; }
.status-borrowed  { background: #fef3cd; color: #7a5200; }
.status-repair    { background: #dbeafe; color: #1e3a5f; }
.status-lost      { background: #fee2e2; color: #7f1d1d; }

.td-actions { display: flex; gap: .35rem; align-items: center; }

.tbl-btn {
  background: #f0f7f2; border: 1.5px solid var(--cream-border);
  border-radius: 7px; padding: .3rem .6rem;
  font-size: .78rem; cursor: pointer;
  font-family: 'DM Sans', sans-serif; color: var(--green-mid); font-weight: 500;
  transition: all .15s;
}
.tbl-btn:hover        { background: #111; color: #fff; border-color: #111; }
.tbl-btn:disabled     { opacity: .4; cursor: not-allowed; }
.tbl-btn.tbl-gold     { background: #fef9e7; color: var(--gold-dark); border-color: var(--gold-light); }
.tbl-btn.tbl-gold:hover { background: #111; color: #fff; border-color: #111; }
.tbl-btn.tbl-red      { background: #fff0f0; color: #b91c1c; border-color: #fca5a5; }
.tbl-btn.tbl-red:hover  { background: #111; color: #fff; border-color: #111; }
.tbl-btn.tbl-green    { background: #d8f3dc; color: var(--green-dark); border-color: #b8ddc8; }
.tbl-btn.tbl-green:hover { background: #111; color: #fff; border-color: #111; }

/* ── Paginación ──────────────────────────────────────────────────────────── */
.pagination-section {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 1rem; padding: .85rem 1.25rem;
  background: var(--card-bg);
  border: 1.5px solid var(--cream-border);
  border-radius: 12px; box-shadow: var(--shadow-sm);
  font-size: .82rem; color: #5a7a5a;
}
.pagination-controls { display: flex; align-items: center; gap: .75rem; }
.page-numbers { display: flex; gap: .3rem; }
.page-number {
  padding: .35rem .7rem; border-radius: 7px; cursor: pointer;
  font-size: .82rem; font-weight: 500; color: var(--green-mid);
  transition: all .15s;
}
.page-number:hover  { background: #111; color: #fff; }
.page-number.active { background: var(--green-mid); color: #fff; }
.page-ellipsis { padding: .35rem .3rem; color: #9ab5a0; }

.pbtn {
  background: #fff; border: 1.5px solid var(--cream-border);
  border-radius: 8px; padding: .38rem .85rem;
  font-size: .82rem; font-weight: 500; cursor: pointer;
  color: var(--green-mid); font-family: 'DM Sans', sans-serif;
  transition: all .15s;
}
.pbtn:hover    { background: #111; color: #fff; border-color: #111; }
.pbtn:disabled { opacity: .4; cursor: not-allowed; }

.items-per-page { display: flex; align-items: center; gap: .5rem; }
.page-select {
  padding: .3rem .55rem; border: 1.5px solid var(--cream-border);
  border-radius: 7px; font-size: .8rem; font-family: 'DM Sans', sans-serif;
  color: var(--green-dark); background: #fff; cursor: pointer;
}
.filtered-info { font-size: .8rem; color: #9ab5a0; margin-left: .4rem; font-style: italic; }

/* ── Empty state ─────────────────────────────────────────────────────────── */
.empty-state {
  text-align: center; padding: 4rem 2rem;
  background: var(--card-bg);
  border: 1.5px solid var(--cream-border);
  border-radius: 14px; box-shadow: var(--shadow-sm);
}
.empty-icon { font-size: 3.5rem; margin-bottom: 1rem; opacity: .5; }
.empty-state h3 { color: var(--green-dark); margin-bottom: .5rem; font-family: 'Playfair Display', serif; }
.empty-state p  { color: #5a7a5a; margin-bottom: .5rem; }

/* ── Modal ───────────────────────────────────────────────────────────────── */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(26, 47, 26, 0.45); /* verde oscuro suave en lugar de negro */
  display: flex; align-items: center; justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(6px); /* el blur hace el trabajo pesado */
}

.modal-content {
  background: var(--card-bg);
  border-radius: 16px;
  width: 90%;
  max-width: 480px;
  border: 1.5px solid var(--cream-border);
  box-shadow: 0 20px 60px rgba(0,0,0,.2);
  animation: modalIn .25s ease-out;
  position: relative;  /* ← agregar esto */
  z-index: 1;          /* ← agregar esto */
}

@keyframes modalIn {
  from { opacity: 0; transform: translateY(-16px); }
  to   { opacity: 1; transform: translateY(0); }
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1.25rem 1.5rem 1rem;
  border-bottom: 1.5px solid #eef5f0;
}
.modal-header h3 { margin: 0; color: var(--green-dark); font-family: 'Playfair Display', serif; font-size: 1.2rem; }
.modal-close-btn {
  background: none; border: none; font-size: 1.4rem; color: #000000;
  cursor: pointer; width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s;
}
.modal-close-btn:hover { background: #f0f9f4; color: var(--green-dark); }
.modal-body { padding: 1.25rem 1.5rem; font-size: .88rem; color: #060f03; line-height: 1.6; }

.book-to-delete {
  margin: 1rem 0; padding: 1rem;
  background: #f3faf5; border-radius: 10px;
  border-left: 4px solid var(--green-light);
}
.book-info-modal h4 { margin: 0 0 .4rem; color: #1a2e1a; }
.book-info-modal p  { margin: .2rem 0; color: #5a7a5a; font-size: .85rem; }
.warning-message {
  display: flex; gap: .65rem; margin-top: .85rem;
  padding: .65rem; background: #fef9e7;
  border: 1px solid #fde68a; border-radius: 8px; color: #7a5200;
}
.warning-icon { font-size: 1.25rem; }
.warning-message p { margin: 0; font-size: .83rem; }

.modal-footer {
  display: flex; justify-content: flex-end; gap: .75rem;
  padding: 1rem 1.5rem;
  border-top: 1.5px solid #eef5f0;
}
.btn-modal-cancel {
  background: #fff; color: #5a7a5a;
  border: 1.5px solid var(--cream-border); border-radius: 8px;
  padding: .45rem 1rem; font-size: .85rem; font-weight: 600;
  cursor: pointer; font-family: 'DM Sans', sans-serif; transition: all .18s;
}
.btn-modal-cancel:hover { background: #ff4f4f; color: #fff; border-color: #111; }
.btn-modal-delete, .btn-modal-confirm {
  background: var(--green-mid); color: #fff;
  border: none; border-radius: 8px;
  padding: .45rem 1.1rem; font-size: .85rem; font-weight: 600;
  cursor: pointer; font-family: 'DM Sans', sans-serif; transition: all .18s;
  display: inline-flex; align-items: center; gap: .4rem;
}
.btn-modal-delete { background: #000; }
.btn-modal-delete:hover, .btn-modal-confirm:hover { background: #2c7709; }
.btn-modal-delete:disabled, .btn-modal-confirm:disabled { opacity: .55; cursor: not-allowed; }

/* ── Toast ───────────────────────────────────────────────────────────────── */
.toast {
  position: fixed; bottom: 24px; right: 24px;
  background: #52b788;
  border: 1.5px solid #b8ddc8;
  border-radius: 12px;
  box-shadow: 0 6px 24px rgba(0,0,0,.12);
  display: flex; align-items: center; gap: 1rem;
  padding: 1rem 1.25rem; max-width: 340px; z-index: 3000;
  width: 500px;
  animation: toastIn .3s ease-out;
  border-left: 4px solid var(--green-light);
}
@keyframes toastIn {
  from { opacity: 0; transform: translateX(100%); }
  to   { opacity: 1; transform: translateX(0); }
}
.toast-icon { font-size: 1.5rem; }
.toast-content strong { display: block; color: var(--green-dark); margin-bottom: .2rem; font-size: .9rem; }
.toast-content p      { margin: 0; color: #5a7a5a; font-size: .8rem; }
.toast-close {
  background: none; border: none; color: #9ab5a0;
  font-size: 1.1rem; cursor: pointer; padding: 0;
  width: 22px; height: 22px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s;
}
.toast-close:hover { background: #f0f9f4; }

/* Toast prestamo estilo */
.toast-loan-success {
border-left: 4px solid var(--green-mid);
background: #f0fdf4;
}
.toast-loan-success .toast-content strong { color: var(--green-dark); }
.toast-loan-success .toast-content p { color: #5a7a5a; }

/* ── Spinners ────────────────────────────────────────────────────────────── */
.spinner-mini {
  display: inline-block; width: 11px; height: 11px;
  border: 2px solid rgba(255,255,255,.3);
  border-top-color: white; border-radius: 50%;
  animation: spin .6s linear infinite;
}
.spinner-small {
  display: inline-block; width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,.3);
  border-top-color: white; border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }


/* ── Responsive ──────────────────────────────────────────────────────────── */
/* Tablet */
@media (max-width: 900px) {
  .catalog-header     { flex-direction: column; gap: 1rem; align-items: flex-start; padding: 1.25rem 1.5rem; }
  .catalog-stats      { width: 100%; justify-content: space-between; }
  .books-grid         { grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
  .pagination-section { flex-direction: column; align-items: flex-start; gap: .75rem; }
  .pagination-controls{ width: 100%; justify-content: center; }
}
 
/* Móvil */
@media (max-width: 600px) {
  .book-catalog       { padding: .75rem; }
  .header-content h1  { font-size: 1.3rem; }
  .catalog-stats      { flex-direction: column; gap: .5rem; }
  .stat-pill          { display: flex; align-items: center; gap: .75rem; text-align: left; padding: .5rem .85rem; }
  .stat-num           { font-size: 1.1rem; }
 
  .search-bar         { flex-wrap: wrap; gap: .4rem; }
  .search-input       { order: 1; flex: 100%; }
  .btn-filter         { order: 2; flex: 1; }
  .btn-search         { order: 2; flex: 1; }
 
  .filters-grid       { grid-template-columns: 1fr; }
  .filter-actions     { justify-content: stretch; }
  .filter-actions .btn{ flex: 1; text-align: center; }
 
  .view-controls      { flex-direction: column; align-items: flex-start; gap: .65rem; }
  .books-grid         { grid-template-columns: 1fr; }
 
  .book-actions       { flex-direction: column; }
  .book-actions > *   { width: 100%; justify-content: center; }
 
  .table-ui thead th,
  .table-ui td        { padding: .55rem .65rem; }
 
  .pagination-section { padding: .75rem; }
  .pagination-info    { font-size: .76rem; }
  .pbtn               { padding: .35rem .65rem; font-size: .78rem; }
 
  .modal-content      { border-radius: 12px; }
  .modal-footer       { flex-direction: column; }
  .modal-footer > *   { width: 100%; justify-content: center; }
 
  /* Toast full-width en móvil */
  .toast              { left: 16px; right: 16px; bottom: 16px; width: auto; max-width: none; }
}
</style>