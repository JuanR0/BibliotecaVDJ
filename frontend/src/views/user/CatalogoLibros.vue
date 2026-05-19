<template>
  <div class="book-catalog">

    <!-- ══ HEADER ══ -->
    <div class="catalog-header">
      <div class="header-content">
        <p class="header-sup">Biblioteca Universitaria</p>
        <h1 class="header-titulo">Catálogo de Libros</h1>
        <p class="header-sub">{{ esAdmin ? 'Gestión del acervo bibliográfico' : 'Consulta la disponibilidad del acervo' }}</p>
      </div>
      <div class="catalog-stats">
        <div class="stat-pill">
          <span class="stat-num">{{ stats.totalBooks }}</span>
          <span class="stat-lbl">Total</span>
        </div>
        <div class="stat-pill stat-pill-green">
          <span class="stat-num">{{ stats.availableBooks }}</span>
          <span class="stat-lbl">Disponibles</span>
        </div>
        <div class="stat-pill stat-pill-gold" v-if="esAdmin">
          <span class="stat-num">{{ stats.prestableBooks }}</span>
          <span class="stat-lbl">Prestables</span>
        </div>
      </div>
    </div>

    <!-- ══ BARRA DE BÚSQUEDA ══ -->
    <div class="search-section">
      <div class="search-bar">
        <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="search-icon-inner">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar por título, autor, editorial..."
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button v-if="esAdmin" @click="showAdvancedFilters = !showAdvancedFilters" class="btn-filter">
          {{ showAdvancedFilters ? '▲' : '▼' }} Filtros
        </button>
        <button @click="handleSearch" class="btn-search">Buscar</button>
        <!-- Botón nuevo libro — solo admin -->
        <button v-if="esAdmin" @click="abrirModalCrear" class="btn-nuevo-libro">
          <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
          </svg>
          Nuevo
        </button>
      </div>

      <!-- Filtros avanzados — solo admin -->
      <div v-if="esAdmin && showAdvancedFilters" class="advanced-filters">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Estado:</label>
            <select v-model="filters.estado_id" class="filter-select">
              <option value="">Todos</option>
              <option value="1">Disponible</option>
              <option value="2">Prestado</option>
              <option value="3">En reparación</option>
              <option value="4">Retirados</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Prestable:</label>
            <select v-model="filters.es_prestable" class="filter-select">
              <option value="">Todos</option>
              <option value="true">Solo prestables</option>
              <option value="false">No prestables</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Editorial:</label>
            <select v-model="filters.editorial_id" class="filter-select">
              <option value="">Todas</option>
              <option v-for="e in editoriales" :key="e.id" :value="e.id">{{ e.nombre }}</option>
            </select>
          </div>
        </div>
        <div class="filter-actions">
          <button @click="currentPage = 1" class="btn btn-primary">Aplicar</button>
          <button @click="resetFilters" class="btn btn-outline">Limpiar</button>
        </div>
      </div>
    </div>

    <!-- ══ CONTROLES DE VISTA ══ -->
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
            <option value="edicion">Edición</option>
          </select>
        </div>
      </div>

      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando catálogo...</p>
      </div>
      <div v-if="error" class="error-state">
        <p>{{ error }}</p>
        <button @click="loadBooks" class="btn btn-primary">Reintentar</button>
      </div>

      <!-- ── CUADRÍCULA ── -->
      <div v-if="viewMode === 'grid' && !isLoading && !error" class="books-grid">
        <div v-for="book in paginatedBooks" :key="book.id" class="book-card">

          <div class="book-card-top" :class="getCardColorClass(book.id)">
            <span class="book-icon-lg">📖</span>
            <div class="badge-status" :class="getStatusClass(book)">{{ getStatusText(book) }}</div>
            <div class="card-code-badge">{{ book.codigo_decimal || 'N/A' }}</div>
            <div v-if="book.es_prestable" class="badge-prestable">Prestable</div>
          </div>

          <div class="book-body">
            <h3 class="book-title">{{ book.titulo }}</h3>
            <p class="book-author">✍️ {{ book.autor }}</p>
            <div class="book-details">
              <!-- ISBN solo para admin -->
              <p v-if="esAdmin"><strong>ISBN:</strong> {{ book.isbn || '—' }}</p>
              <p><strong>Etiqueta:</strong> {{ book.etiqueta }}</p>
              <p><strong>Edición:</strong> {{ book.edicion || '—' }}</p>
              <p v-if="book.editorial_nombre"><strong>Editorial:</strong> {{ book.editorial_nombre }}</p>
              <p v-if="book.area_conocimiento_nombre"><strong>Área:</strong> {{ book.area_conocimiento_nombre }}</p>
            </div>
          </div>

          <div class="book-actions">
            <!-- Detalles — todos los niveles -->
            <button @click="abrirModalDetalles(book)" class="btn-detail">Detalles</button>

            <!-- Solicitar préstamo — nivel 2 (bibliotecario, desde catálogo no aplica el self-service) -->
            <!-- El préstamo lo gestiona GestionPrestamos, no el catálogo -->

            <!-- Acciones admin — nivel 3+ -->
            <template v-if="esAdmin">
              <button @click="abrirModalEditarLibro(book)" class="btn-editar">Editar</button>
              <button
                v-if="book.estado_id !== 4"
                @click="confirmarRetirar(book)"
                class="btn-eliminar"
                :disabled="book.estado_id === 2"
                :title="book.estado_id === 2 ? 'No se puede retirar: está prestado' : 'Retirar libro'"
              >Retirar</button>
              <button v-if="book.estado_id === 4" @click="reactivarLibro(book)" class="btn-recuperar">Recuperar</button>
            </template>
          </div>
        </div>

        <!-- Modal eliminar (retirar) -->
        <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeModal">
          <div class="modal-content">
            <div class="modal-header">
              <h3>Confirmar Retiro</h3>
              <button @click="closeModal" class="modal-close-btn" :disabled="isDeleting">×</button>
            </div>
            <div class="modal-body">
              <p>¿Retirar el siguiente libro del catálogo?</p>
              <div class="book-to-delete">
                <div class="book-info-modal">
                  <h4>{{ bookToDelete?.titulo }}</h4>
                  <p><strong>Autor:</strong> {{ bookToDelete?.autor }}</p>
                  <p><strong>Código:</strong> {{ bookToDelete?.codigo_decimal }} — Ej. {{ bookToDelete?.numero_ejemplar }}</p>
                </div>
                <div class="warning-message">
                  <div class="warning-icon">⚠️</div>
                  <p>El libro pasará a estado <strong>Retirado</strong> (soft delete).</p>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button @click="closeModal" class="btn-modal-cancel" :disabled="isDeleting">Cancelar</button>
              <button @click="deleteBook" class="btn-modal-delete" :disabled="isDeleting">
                <span v-if="isDeleting" class="spinner-small"></span>
                {{ isDeleting ? 'Retirando...' : 'Sí, Retirar' }}
              </button>
            </div>
          </div>
        </div>
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
                  <div class="td-sub">{{ book.etiqueta }}</div>
                </td>
                <td>
                  <div class="td-title">{{ book.titulo }}</div>
                  <div class="td-sub" v-if="book.edicion">Ed. {{ book.edicion }}</div>
                </td>
                <td class="td-author">{{ book.autor }}</td>
                <td><div class="td-sub">{{ book.editorial_nombre || '—' }}</div></td>
                <td>
                  <span :class="getStatusClass(book)" class="status-pill">{{ getStatusText(book) }}</span>
                  <div class="td-sub" v-if="book.es_prestable" style="margin-top:.25rem">🔄 Prestable</div>
                </td>
                <td>
                  <div class="td-actions">
                    <button @click="abrirModalDetalles(book)" class="tbl-btn" title="Detalles">🔍</button>
                    <template v-if="esAdmin">
                      <button @click="abrirModalEditarLibro(book)" class="tbl-btn tbl-gold" title="Editar">✏️</button>
                      <button
                        v-if="book.estado_id !== 4"
                        @click="confirmarRetirar(book)"
                        class="tbl-btn tbl-red"
                        :disabled="book.estado_id === 2"
                        title="Retirar"
                      >🗑️</button>
                      <button v-if="book.estado_id === 4" @click="reactivarLibro(book)" class="tbl-btn tbl-green" title="Recuperar">♻️</button>
                    </template>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Toasts -->
      <div v-if="showSuccessToast" class="toast">
        <span class="toast-icon">✅</span>
        <div class="toast-content">
          <strong>{{ toastMsg }}</strong>
        </div>
        <button @click="showSuccessToast = false" class="toast-close">×</button>
      </div>

      <!-- Paginación -->
      <div v-if="!isLoading && !error && filteredBooks.length > 0" class="pagination-section">
        <div class="pagination-info">
          Mostrando {{ startItem }}–{{ endItem }} de {{ filteredBooks.length }} libros
        </div>
        <div class="pagination-controls">
          <button @click="prevPage" :disabled="currentPage === 1" class="pbtn">← Anterior</button>
          <div class="page-numbers">
            <span v-for="page in visiblePages" :key="page" @click="goToPage(page)" :class="{ active: page === currentPage }" class="page-number">{{ page }}</span>
          </div>
          <button @click="nextPage" :disabled="currentPage === totalPages" class="pbtn">Siguiente →</button>
        </div>
        <div class="items-per-page">
          <label>Mostrar:</label>
          <select v-model="itemsPerPage" @change="currentPage = 1" class="page-select">
            <option :value="12">12</option><option :value="24">24</option><option :value="48">48</option>
          </select>
        </div>
      </div>

      <div v-if="!isLoading && !error && filteredBooks.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>No se encontraron libros</h3>
        <p>Intenta con otros términos o ajusta los filtros.</p>
        <button @click="resetFilters" class="btn-loan" style="margin-top:1rem">🔄 Mostrar todos</button>
      </div>
    </div>


    <!-- ══════════════════════════════════════════════
         MODAL: DETALLES + EJEMPLARES
    ══════════════════════════════════════════════ -->
    <div v-if="modalDetalles.visible" class="modal-overlay" @click.self="cerrarModalDetalles">
      <div class="modal-content modal-detalles">
        <div class="modal-header">
          <h3>Detalles del Libro</h3>
          <button @click="cerrarModalDetalles" class="modal-close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="detalles-grid">
            <!-- Info del libro -->
            <div class="detalles-info">
              <div class="detalle-titulo-wrap">
                <h4 class="detalle-titulo">{{ modalDetalles.libro?.titulo }}</h4>
                <span class="detalle-autor">{{ modalDetalles.libro?.autor }}</span>
              </div>
              <div class="detalle-ficha">
                <div class="ficha-row"><span class="ficha-lbl">Código</span><span class="ficha-val mono">{{ modalDetalles.libro?.codigo_decimal }} — {{ modalDetalles.libro?.etiqueta }}</span></div>
                <div class="ficha-row"><span class="ficha-lbl">Edición</span><span class="ficha-val">{{ modalDetalles.libro?.edicion || '—' }}</span></div>
                <div class="ficha-row"><span class="ficha-lbl">Editorial</span><span class="ficha-val">{{ modalDetalles.libro?.editorial_nombre || '—' }}</span></div>
                <div class="ficha-row"><span class="ficha-lbl">Área</span><span class="ficha-val">{{ modalDetalles.libro?.area_conocimiento_nombre || '—' }}</span></div>
                <div class="ficha-row"><span class="ficha-lbl">Páginas</span><span class="ficha-val">{{ modalDetalles.libro?.numero_paginas || '—' }}</span></div>
                <div class="ficha-row" v-if="esAdmin"><span class="ficha-lbl">ISBN</span><span class="ficha-val mono">{{ modalDetalles.libro?.isbn || '—' }}</span></div>
                <div class="ficha-row" v-if="esAdmin"><span class="ficha-lbl">Prestable</span><span class="ficha-val">{{ modalDetalles.libro?.es_prestable ? 'Sí' : 'No' }}</span></div>
              </div>
            </div>

            <!-- Ejemplares -->
            <div class="detalles-ejemplares">
              <h5 class="ejemplares-titulo">Ejemplares</h5>
              <div v-if="modalDetalles.cargandoEjemplares" class="ejemplares-loading">
                <div class="spinner-sm"></div>
                <span>Cargando ejemplares...</span>
              </div>
              <div v-else-if="modalDetalles.ejemplares.length === 0" class="ejemplares-vacio">
                Sin ejemplares registrados
              </div>
              <div v-else class="ejemplares-lista">
                <div
                  v-for="ej in modalDetalles.ejemplares"
                  :key="ej.id"
                  class="ejemplar-badge"
                  :class="getEjemplarBadgeClass(ej)"
                >
                  <span class="ejemplar-num">Ejemplar {{ ej.numero_ejemplar }}</span>
                  <span class="ejemplar-estado">{{ getEjemplarEstadoText(ej) }}</span>
                </div>
              </div>
              <p class="ejemplares-resumen" v-if="modalDetalles.ejemplares.length > 0">
                {{ modalDetalles.ejemplares.filter(e => e.estado_id === 1).length }} disponible(s) de {{ modalDetalles.ejemplares.length }}
              </p>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="cerrarModalDetalles" class="btn-modal-cancel">Cerrar</button>
          <!-- Botón crear otro ejemplar — solo admin -->
          <button v-if="esAdmin" @click="abrirModalEjemplarExtra(modalDetalles.libro)" class="btn-modal-confirm">
            + Agregar ejemplar
          </button>
        </div>
      </div>
    </div>


    <!-- ══════════════════════════════════════════════
         MODAL: CREAR LIBRO (individual o múltiple)
    ══════════════════════════════════════════════ -->
    <div v-if="modalCrear.visible" class="modal-overlay" @click.self="cerrarModalCrear">
      <div class="modal-content modal-crear">
        <div class="modal-header">
          <h3>{{ modalCrear.modo === 'multiple' ? 'Crear Múltiples Ejemplares' : 'Nuevo Libro' }}</h3>
          <button @click="cerrarModalCrear" class="modal-close-btn" :disabled="procesandoCrear">×</button>
        </div>
        <div class="modal-body">

          <!-- Toggle modo -->
          <div class="modo-toggle">
            <button :class="{ 'modo-active': modalCrear.modo === 'individual' }" @click="modalCrear.modo = 'individual'" class="modo-btn">Individual</button>
            <button :class="{ 'modo-active': modalCrear.modo === 'multiple' }" @click="modalCrear.modo = 'multiple'" class="modo-btn">Múltiples ejemplares</button>
          </div>

          <div class="crear-grid">
            <div class="form-field">
              <label class="form-label">Título <span class="req">*</span></label>
              <input v-model="crearForm.titulo" type="text" class="form-input" placeholder="Título del libro"/>
            </div>
            <div class="form-field">
              <label class="form-label">Autor <span class="req">*</span></label>
              <input v-model="crearForm.autor" type="text" class="form-input" placeholder="Nombre del autor"/>
            </div>
            <div class="form-field">
              <label class="form-label">Código Decimal <span class="req">*</span></label>
              <input v-model="crearForm.codigo_decimal" type="text" class="form-input" placeholder="Ej: 540.1"/>
            </div>
            <div class="form-field">
              <label class="form-label">Etiqueta <span class="req">*</span></label>
              <input v-model="crearForm.etiqueta" type="text" class="form-input" maxlength="3" placeholder="3 letras"/>
            </div>
            <div class="form-field" v-if="modalCrear.modo === 'individual'">
              <label class="form-label">Nº Ejemplar <span class="req">*</span></label>
              <input v-model.number="crearForm.numero_ejemplar" type="number" class="form-input" min="1" placeholder="1"/>
            </div>
            <template v-if="modalCrear.modo === 'multiple'">
              <div class="form-field">
                <label class="form-label">Cantidad de ejemplares <span class="req">*</span></label>
                <input v-model.number="crearForm.cantidad_ejemplares" type="number" class="form-input" min="1" max="50" placeholder="Ej: 3"/>
              </div>
              <div class="form-field">
                <label class="form-label">Nº ejemplar inicial</label>
                <input v-model.number="crearForm.numero_ejemplar_inicial" type="number" class="form-input" min="1" placeholder="1"/>
              </div>
            </template>
            <div class="form-field">
              <label class="form-label">ISBN</label>
              <input v-model="crearForm.isbn" type="text" class="form-input" placeholder="Opcional"/>
            </div>
            <div class="form-field">
              <label class="form-label">Editorial <span class="req">*</span></label>
              <select v-model.number="crearForm.editorial_id" class="form-input">
                <option value="">Seleccionar...</option>
                <option v-for="e in catalogosAux.editoriales" :key="e.id" :value="e.id">{{ e.nombre }}</option>
              </select>
            </div>
            <div class="form-field">
              <label class="form-label">Área de conocimiento <span class="req">*</span></label>
              <select v-model.number="crearForm.area_conocimiento_id" class="form-input">
                <option value="">Seleccionar...</option>
                <option v-for="a in catalogosAux.areas" :key="a.id" :value="a.id">{{ a.nombre }}</option>
              </select>
            </div>
            <div class="form-field">
              <label class="form-label">Estado <span class="req">*</span></label>
              <select v-model.number="crearForm.estado_id" class="form-input">
                <option value="">Seleccionar...</option>
                <option v-for="e in catalogosAux.estados.filter(s => s.id !== 4)" :key="e.id" :value="e.id">{{ e.estado }}</option>
              </select>
            </div>
            <div class="form-field">
              <label class="form-label">Método adquisición <span class="req">*</span></label>
              <select v-model.number="crearForm.metodo_adquisicion_id" class="form-input">
                <option value="">Seleccionar...</option>
                <option v-for="m in catalogosAux.metodos" :key="m.id" :value="m.id">{{ m.tipo }}</option>
              </select>
            </div>
            <div class="form-field">
              <label class="form-label">Edición</label>
              <input v-model.number="crearForm.edicion" type="number" class="form-input" min="1" placeholder="Opcional"/>
            </div>
            <div class="form-field">
              <label class="form-label">Páginas</label>
              <input v-model.number="crearForm.numero_paginas" type="number" class="form-input" min="1" placeholder="Opcional"/>
            </div>
            <div class="form-field">
              <label class="form-label">Precio</label>
              <input v-model.number="crearForm.precio" type="number" class="form-input" min="0" step="0.01" placeholder="Opcional"/>
            </div>
            <div class="form-field">
              <label class="form-label">Proveedor</label>
              <input v-model="crearForm.proveedor_nombre" type="text" class="form-input" placeholder="Opcional"/>
            </div>
            <div class="form-field form-field-check">
              <label class="form-label-check">
                <input type="checkbox" v-model="crearForm.es_prestable"/>
                Es prestable
              </label>
            </div>
          </div>

          <div v-if="modalCrear.error" class="form-error">{{ modalCrear.error }}</div>
          <div v-if="modalCrear.advertencia" class="form-warning">{{ modalCrear.advertencia }}</div>
        </div>
        <div class="modal-footer">
          <button @click="cerrarModalCrear" class="btn-modal-cancel" :disabled="procesandoCrear">Cancelar</button>
          <button @click="guardarLibro" class="btn-modal-confirm" :disabled="procesandoCrear">
            <span v-if="procesandoCrear" class="spinner-small"></span>
            {{ procesandoCrear ? 'Guardando...' : modalCrear.modo === 'multiple' ? 'Crear Ejemplares' : 'Crear Libro' }}
          </button>
        </div>
      </div>
    </div>


    <!-- ══════════════════════════════════════════════
         MODAL: EDITAR LIBRO
    ══════════════════════════════════════════════ -->
    <div v-if="modalEditar.visible" class="modal-overlay" @click.self="cerrarModalEditar">
      <div class="modal-content modal-crear">
        <div class="modal-header">
          <h3>Editar Libro</h3>
          <button @click="cerrarModalEditar" class="modal-close-btn" :disabled="procesandoEditar">×</button>
        </div>
        <div class="modal-body">
          <div class="crear-grid">
            <div class="form-field">
              <label class="form-label">Título</label>
              <input v-model="editarForm.titulo" type="text" class="form-input"/>
            </div>
            <div class="form-field">
              <label class="form-label">Autor</label>
              <input v-model="editarForm.autor" type="text" class="form-input"/>
            </div>
            <div class="form-field">
              <label class="form-label">ISBN</label>
              <input v-model="editarForm.isbn" type="text" class="form-input"/>
            </div>
            <div class="form-field">
              <label class="form-label">Editorial</label>
              <select v-model.number="editarForm.editorial_id" class="form-input">
                <option v-for="e in catalogosAux.editoriales" :key="e.id" :value="e.id">{{ e.nombre }}</option>
              </select>
            </div>
            <div class="form-field">
              <label class="form-label">Estado</label>
              <select v-model.number="editarForm.estado_id" class="form-input">
                <option v-for="e in catalogosAux.estados.filter(s => s.id !== 4)" :key="e.id" :value="e.id">{{ e.estado }}</option>
              </select>
            </div>
            <div class="form-field">
              <label class="form-label">Edición</label>
              <input v-model.number="editarForm.edicion" type="number" class="form-input" min="1"/>
            </div>
            <div class="form-field">
              <label class="form-label">Páginas</label>
              <input v-model.number="editarForm.numero_paginas" type="number" class="form-input" min="1"/>
            </div>
            <div class="form-field">
              <label class="form-label">Precio</label>
              <input v-model.number="editarForm.precio" type="number" class="form-input" min="0" step="0.01"/>
            </div>
            <div class="form-field form-field-check">
              <label class="form-label-check">
                <input type="checkbox" v-model="editarForm.es_prestable"/>
                Es prestable
              </label>
            </div>
          </div>
          <div v-if="modalEditar.error" class="form-error">{{ modalEditar.error }}</div>
        </div>
        <div class="modal-footer">
          <button @click="cerrarModalEditar" class="btn-modal-cancel" :disabled="procesandoEditar">Cancelar</button>
          <button @click="guardarEdicion" class="btn-modal-confirm" :disabled="procesandoEditar">
            <span v-if="procesandoEditar" class="spinner-small"></span>
            {{ procesandoEditar ? 'Guardando...' : 'Guardar Cambios' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>


<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { bookService } from '@/services/books'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import '@/styles/buttons.css'

const authStore = useAuthStore()

// ── Permisos ───────────────────────────────────────────────────────────────
const nivel  = computed(() => authStore.tipoUsuarioId)
const esAdmin = computed(() => nivel.value >= 3)

// ── Estado UI ──────────────────────────────────────────────────────────────
const searchQuery         = ref('')
const showAdvancedFilters = ref(false)
const viewMode            = ref('grid')
const sortBy              = ref('titulo')
const isLoading           = ref(false)
const error               = ref(null)
const currentPage         = ref(1)
const itemsPerPage        = ref(12)
const showSuccessToast    = ref(false)
const toastMsg            = ref('')
const isDeleting          = ref(false)
const showDeleteModal     = ref(false)
const bookToDelete        = ref(null)
const procesandoCrear     = ref(false)
const procesandoEditar    = ref(false)

const books       = ref([])
const editoriales = ref([])
const stats       = ref({ totalBooks: 0, availableBooks: 0, prestableBooks: 0 })

const filters = ref({ estado_id: '', es_prestable: '', editorial_id: '' })

// ── Catálogos auxiliares (admin) ────────────────────────────────────────────
const catalogosAux = ref({ editoriales: [], areas: [], estados: [], metodos: [] })

// ── Modal detalles ─────────────────────────────────────────────────────────
const modalDetalles = ref({
  visible: false, libro: null,
  ejemplares: [], cargandoEjemplares: false
})

// ── Modal crear ────────────────────────────────────────────────────────────
const modalCrear = ref({ visible: false, modo: 'individual', error: '', advertencia: '' })
const crearFormInicial = () => ({
  titulo: '', autor: '', codigo_decimal: '', etiqueta: '', numero_ejemplar: 1,
  isbn: '', editorial_id: '', area_conocimiento_id: '', estado_id: '',
  metodo_adquisicion_id: '', edicion: null, numero_paginas: null,
  precio: null, proveedor_nombre: '', es_prestable: true,
  cantidad_ejemplares: 1, numero_ejemplar_inicial: 1
})
const crearForm = ref(crearFormInicial())

// ── Modal editar ────────────────────────────────────────────────────────────
const modalEditar = ref({ visible: false, libroId: null, error: '' })
const editarForm  = ref({})

// ── Computed ───────────────────────────────────────────────────────────────
const filteredBooks = computed(() => {
  let r = books.value

  // Nivel 1: solo ver ejemplar 1 de cada libro (los demás ejemplares se ven en el modal)
  if (nivel.value === 1) r = r.filter(b => b.numero_ejemplar === 1)

  if (filters.value.estado_id)    r = r.filter(b => b.estado_id === parseInt(filters.value.estado_id))
  if (filters.value.es_prestable !== '') r = r.filter(b => b.es_prestable === (filters.value.es_prestable === 'true'))
  if (filters.value.editorial_id) r = r.filter(b => b.editorial_id === parseInt(filters.value.editorial_id))

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    r = r.filter(b =>
      b.titulo?.toLowerCase().includes(q) ||
      b.autor?.toLowerCase().includes(q)  ||
      b.editorial_nombre?.toLowerCase().includes(q) ||
      b.codigo_decimal?.toLowerCase().includes(q)
    )
  }

  return [...r].sort((a, b) => {
    if (sortBy.value === 'autor')   return (a.autor||'').localeCompare(b.autor||'')
    if (sortBy.value === 'edicion') return (b.edicion||0) - (a.edicion||0)
    return (a.titulo||'').localeCompare(b.titulo||'')
  })
})

const totalPages     = computed(() => Math.ceil(filteredBooks.value.length / itemsPerPage.value) || 1)
const paginatedBooks = computed(() => filteredBooks.value.slice((currentPage.value-1)*itemsPerPage.value, currentPage.value*itemsPerPage.value))
const startItem      = computed(() => (currentPage.value-1)*itemsPerPage.value + 1)
const endItem        = computed(() => Math.min(currentPage.value*itemsPerPage.value, filteredBooks.value.length))
const visiblePages   = computed(() => {
  const max = 5, total = totalPages.value
  if (total <= max) return Array.from({length:total}, (_,i) => i+1)
  let s = Math.max(1, currentPage.value-2)
  const e = Math.min(total, s+max-1)
  if (e-s+1 < max) s = e-max+1
  return Array.from({length:e-s+1}, (_,i) => s+i)
})

// ── Carga de datos ─────────────────────────────────────────────────────────
const loadBooks = async () => {
  isLoading.value = true; error.value = null
  try {
    const params = esAdmin.value ? { por_pagina: 200 } : { por_pagina: 200 }
    const response = await bookService.getBooks(params)
    books.value = response?.libros ?? (Array.isArray(response) ? response : [])
    calculateStats()
    extractEditoriales()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error cargando el catálogo'
  } finally { isLoading.value = false }
}

const calculateStats = () => {
  stats.value = {
    totalBooks:     books.value.filter(b => b.numero_ejemplar === 1).length,
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

const cargarCatalogosAux = async () => {
  try {
    const [eds, areas, estados, metodos] = await Promise.all([
      api.get('/api/libros/auxiliares/editoriales'),
      api.get('/api/libros/auxiliares/areas-conocimiento'),
      api.get('/api/libros/auxiliares/estados-libro'),
      api.get('/api/libros/auxiliares/metodos-adquisicion'),
    ])
    catalogosAux.value = {
      editoriales: eds.data,
      areas:       areas.data,
      estados:     estados.data,
      metodos:     metodos.data,
    }
  } catch { /* silencioso */ }
}

const handleSearch = () => { currentPage.value = 1 }

const resetFilters = () => {
  searchQuery.value = ''
  filters.value = { estado_id: '', es_prestable: '', editorial_id: '' }
  currentPage.value = 1
}

// ── Helpers visuales ────────────────────────────────────────────────────────
const CARD_COLORS = ['card-c1','card-c2','card-c3']
const getCardColorClass = (id) => CARD_COLORS[id % CARD_COLORS.length]
const STATUS_CLASS = { 1:'status-available', 2:'status-borrowed', 3:'status-repair', 4:'status-lost' }
const STATUS_TEXT  = { 1:'✅ Disponible', 2:'⏳ Prestado', 3:'🔧 En reparación', 4:'❌ Retirado' }
const getStatusClass = (book) => STATUS_CLASS[book.estado_id] || 'status-unknown'
const getStatusText  = (book) => STATUS_TEXT[book.estado_id]  || book.estado_nombre || 'Desconocido'

const getEjemplarBadgeClass = (ej) => ({
  'ejemplar-disponible':    ej.estado_id === 1,
  'ejemplar-prestado':      ej.estado_id === 2,
  'ejemplar-reparacion':    ej.estado_id === 3,
  'ejemplar-retirado':      ej.estado_id === 4,
})
const getEjemplarEstadoText = (ej) => ({
  1: 'Disponible', 2: 'Prestado', 3: 'En reparación', 4: 'Retirado'
})[ej.estado_id] || '—'

// ── Modal detalles ─────────────────────────────────────────────────────────
const abrirModalDetalles = async (book) => {
  modalDetalles.value = { visible: true, libro: book, ejemplares: [], cargandoEjemplares: true }
  try {
    const r = await api.get('/api/libros/', {
      params: {
        codigo_decimal_exacto: book.codigo_decimal,
        por_pagina: 100
      }
    })
    const todos = r.data?.libros ?? []
    // Filtrar por misma etiqueta para no mezclar libros distintos con el mismo código
    modalDetalles.value.ejemplares = todos
      .filter(l => l.etiqueta === book.etiqueta)
      .sort((a, b) => a.numero_ejemplar - b.numero_ejemplar)
  } catch {
    modalDetalles.value.ejemplares = []
  } finally {
    modalDetalles.value.cargandoEjemplares = false
  }
}
const cerrarModalDetalles = () => { modalDetalles.value.visible = false }

// Desde modal detalles → abrir crear con datos pre-rellenados
const abrirModalEjemplarExtra = (libro) => {
  cerrarModalDetalles()
  // Calcular el siguiente número de ejemplar
  const maxEj = modalDetalles.value.ejemplares.length
    ? Math.max(...modalDetalles.value.ejemplares.map(e => e.numero_ejemplar))
    : 1
  crearForm.value = {
    ...crearFormInicial(),
    titulo:                libro.titulo,
    autor:                 libro.autor,
    codigo_decimal:        libro.codigo_decimal,
    etiqueta:              libro.etiqueta,
    isbn:                  libro.isbn || '',
    editorial_id:          libro.editorial_id,
    area_conocimiento_id:  libro.area_conocimiento_id,
    estado_id:             1,
    metodo_adquisicion_id: libro.metodo_adquisicion_id,
    edicion:               libro.edicion,
    numero_paginas:        libro.numero_paginas,
    es_prestable:          libro.es_prestable,
    numero_ejemplar:       maxEj + 1,
    numero_ejemplar_inicial: maxEj + 1,
  }
  modalCrear.value = { visible: true, modo: 'individual', error: '', advertencia: '' }
}

// ── Modal crear ─────────────────────────────────────────────────────────────
const abrirModalCrear = () => {
  crearForm.value = crearFormInicial()
  modalCrear.value = { visible: true, modo: 'individual', error: '', advertencia: '' }
}
const cerrarModalCrear = () => { if (!procesandoCrear.value) modalCrear.value.visible = false }

const guardarLibro = async () => {
  const f = crearForm.value
  if (!f.titulo || !f.autor || !f.codigo_decimal || !f.etiqueta || !f.editorial_id || !f.area_conocimiento_id || !f.estado_id || !f.metodo_adquisicion_id) {
    modalCrear.value.error = 'Completa los campos obligatorios (*)'; return
  }
  procesandoCrear.value = true
  modalCrear.value.error = ''; modalCrear.value.advertencia = ''
  try {
    if (modalCrear.value.modo === 'multiple') {
      const payload = {
        titulo: f.titulo, autor: f.autor, codigo_decimal: f.codigo_decimal,
        etiqueta: f.etiqueta.toUpperCase(), isbn: f.isbn || null,
        editorial_id: f.editorial_id, area_conocimiento_id: f.area_conocimiento_id,
        estado_id: f.estado_id, metodo_adquisicion_id: f.metodo_adquisicion_id,
        edicion: f.edicion || null, numero_paginas: f.numero_paginas || null,
        precio: f.precio || null, proveedor_nombre: f.proveedor_nombre || null,
        es_prestable: f.es_prestable,
        cantidad_ejemplares: f.cantidad_ejemplares,
        numero_ejemplar_inicial: f.numero_ejemplar_inicial,
      }
      const r = await api.post('/api/libros/multiple', payload)
      const creados = Array.isArray(r.data) ? r.data : (r.data?.libros_creados ?? [])
      if (r.data?.advertencia) modalCrear.value.advertencia = r.data.advertencia.message
      mostrarToast(`${creados.length} ejemplar(es) creado(s) correctamente`)
    } else {
      const payload = {
        titulo: f.titulo, autor: f.autor, codigo_decimal: f.codigo_decimal,
        etiqueta: f.etiqueta.toUpperCase(), numero_ejemplar: f.numero_ejemplar,
        isbn: f.isbn || null, editorial_id: f.editorial_id,
        area_conocimiento_id: f.area_conocimiento_id, estado_id: f.estado_id,
        metodo_adquisicion_id: f.metodo_adquisicion_id,
        edicion: f.edicion || null, numero_paginas: f.numero_paginas || null,
        precio: f.precio || null, proveedor_nombre: f.proveedor_nombre || null,
        es_prestable: f.es_prestable,
      }
      await api.post('/api/libros/', payload)
      mostrarToast('Libro creado correctamente')
    }
    if (!modalCrear.value.advertencia) modalCrear.value.visible = false
    await loadBooks()
  } catch (e) {
    modalCrear.value.error = e.response?.data?.detail || 'Error al crear el libro'
  } finally { procesandoCrear.value = false }
}

// ── Modal editar ────────────────────────────────────────────────────────────
const abrirModalEditarLibro = (book) => {
  editarForm.value = {
    titulo:        book.titulo,
    autor:         book.autor,
    isbn:          book.isbn || '',
    editorial_id:  book.editorial_id,
    estado_id:     book.estado_id,
    edicion:       book.edicion,
    numero_paginas: book.numero_paginas,
    precio:        book.precio,
    es_prestable:  book.es_prestable,
  }
  modalEditar.value = { visible: true, libroId: book.id, error: '' }
}
const cerrarModalEditar = () => { if (!procesandoEditar.value) modalEditar.value.visible = false }

const guardarEdicion = async () => {
  procesandoEditar.value = true
  try {
    await api.put(`/api/libros/${modalEditar.value.libroId}`, editarForm.value)
    const idx = books.value.findIndex(b => b.id === modalEditar.value.libroId)
    if (idx !== -1) Object.assign(books.value[idx], editarForm.value)
    modalEditar.value.visible = false
    mostrarToast('Libro actualizado correctamente')
  } catch (e) {
    modalEditar.value.error = e.response?.data?.detail || 'Error al guardar cambios'
  } finally { procesandoEditar.value = false }
}

// ── Retirar / Recuperar ────────────────────────────────────────────────────
const confirmarRetirar = (book) => { bookToDelete.value = book; showDeleteModal.value = true }
const closeModal       = () => { if (!isDeleting.value) { showDeleteModal.value = false; bookToDelete.value = null } }

const deleteBook = async () => {
  if (!bookToDelete.value?.id || isDeleting.value) return
  isDeleting.value = true
  try {
    await bookService.deleteBook(bookToDelete.value.id)
    books.value = books.value.filter(b => b.id !== bookToDelete.value.id)
    showDeleteModal.value = false
    mostrarToast('Libro retirado correctamente')
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al retirar el libro')
  } finally { isDeleting.value = false; bookToDelete.value = null }
}

const reactivarLibro = async (book) => {
  try {
    await bookService.reactivateBook(book.id)
    const t = books.value.find(b => b.id === book.id)
    if (t) { t.estado_id = 1; t.estado_nombre = 'Disponible' }
    mostrarToast(`"${book.titulo}" recuperado correctamente`)
  } catch { alert('Error al recuperar el libro') }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const mostrarToast = (msg) => {
  toastMsg.value = msg; showSuccessToast.value = true
  setTimeout(() => { showSuccessToast.value = false }, 3500)
}

const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const goToPage = (p)  => { if (p >= 1 && p <= totalPages.value) currentPage.value = p }

watch(searchQuery, () => { currentPage.value = 1 })
watch(filters, () => { currentPage.value = 1 }, { deep: true })

onMounted(async () => {
  await loadBooks()
  if (esAdmin.value) await cargarCatalogosAux()
})
</script>


<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');
/*
 * Botones: btn-detail, btn-loan, btn-editar, btn-eliminar, btn-recuperar,
 * btn-primary, btn-outline, tbl-btn → src/styles/buttons.css
 */
:root {
  --green-dark:#1a4731; --green-mid:#2d6a4f; --green-light:#52b788;
  --green-pale:#d8f3dc; --gold-mid:#c9900c; --gold-light:#f4c542;
  --gold-pale:#fef9e7; --cream:#f5f0e8; --cream-border:#d4e8da;
  --card-bg:#fffef9; --shadow-sm:0 2px 12px rgba(26,47,26,.10);
  --shadow-md:0 8px 24px rgba(26,71,49,.15);
}

.book-catalog { font-family:'DM Sans',sans-serif; padding:1.5rem; max-width:1400px; margin:0 auto; background:radial-gradient(ellipse 80% 40% at 10% 0%,rgba(82,183,136,.13) 0%,transparent 60%),radial-gradient(ellipse 60% 50% at 90% 100%,rgba(201,144,12,.10) 0%,transparent 55%),#f5f0e8; min-height:100vh; }

/* ── Header ─────────────────────────────────────────────────────────────── */
.catalog-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; padding:1.5rem 2rem; background:linear-gradient(135deg,#1a4731 0%,#2d6a4f 60%,#3a7d5e 100%); border-radius:16px; position:relative; overflow:hidden; }
.catalog-header::before { content:''; position:absolute; inset:0; background:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23fff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E"); pointer-events:none; }
.header-sup   { font-size:.72rem; font-weight:600; color:rgba(255,255,255,.5); text-transform:uppercase; letter-spacing:.1em; margin-bottom:.2rem; position:relative; }
.header-titulo{ font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700; color:#fff; margin-bottom:.2rem; position:relative; }
.header-sub   { font-size:.8rem; color:rgba(255,255,255,.6); margin:0; position:relative; }
.catalog-stats { display:flex; gap:.75rem; position:relative; }
.stat-pill { display:flex; flex-direction:column; align-items:center; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.15); border-radius:10px; padding:.5rem .875rem; min-width:65px; }
.stat-pill-green { background:rgba(82,183,136,.2); border-color:rgba(82,183,136,.3); }
.stat-pill-gold  { background:rgba(244,197,66,.15); border-color:rgba(244,197,66,.2); }
.stat-num { font-family:'Playfair Display',serif; font-size:1.2rem; font-weight:700; color:#fff; line-height:1; }
.stat-lbl { font-size:.62rem; color:rgba(255,255,255,.55); text-transform:uppercase; letter-spacing:.07em; margin-top:2px; white-space:nowrap; }

/* ── Búsqueda ────────────────────────────────────────────────────────────── */
.search-section { margin-bottom:1.25rem; }
.search-bar { display:flex; align-items:center; gap:.5rem; background:var(--card-bg); border:1.5px solid var(--cream-border); border-radius:12px; padding:.5rem .875rem; box-shadow:var(--shadow-sm); }
.search-icon-inner { color:#9ab5a0; flex-shrink:0; }
.search-input { flex:1; border:none; background:none; font-family:'DM Sans',sans-serif; font-size:.9rem; color:#1a2e1a; outline:none; }
.search-input::placeholder { color:#9ab5a0; }
.btn-filter { padding:.35rem .75rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:8px; font-size:.78rem; font-weight:600; color:#5a7a5a; cursor:pointer; white-space:nowrap; transition:all .18s; }
.btn-filter:hover { background:#111; color:#fff; border-color:#111; }
.btn-search { padding:.35rem .875rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-size:.82rem; font-weight:700; cursor:pointer; white-space:nowrap; transition:background .2s; }
.btn-search:hover { background:#111; }
.btn-nuevo-libro { display:flex; align-items:center; gap:.35rem; padding:.35rem .875rem; background:linear-gradient(135deg,var(--gold-light),var(--gold-mid)); border:none; border-radius:8px; color:var(--green-dark); font-size:.82rem; font-weight:700; cursor:pointer; white-space:nowrap; transition:all .2s; }
.btn-nuevo-libro:hover { transform:translateY(-1px); }
.advanced-filters { background:var(--card-bg); border:1.5px solid var(--cream-border); border-radius:12px; padding:1rem 1.25rem; margin-top:.625rem; }
.filters-grid { display:flex; gap:1rem; flex-wrap:wrap; }
.filter-group { display:flex; flex-direction:column; gap:4px; min-width:160px; }
.filter-group label { font-size:.72rem; font-weight:700; color:var(--green-dark); text-transform:uppercase; letter-spacing:.07em; }
.filter-select,.filter-input { padding:.45rem .625rem; border:1.5px solid var(--cream-border); border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; color:#1a2e1a; background:#fff; outline:none; }
.filter-actions { display:flex; gap:.5rem; margin-top:.75rem; }

/* ── Controles ───────────────────────────────────────────────────────────── */
.results-section { }
.view-controls { display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:.75rem; }
.view-options { display:flex; gap:.375rem; }
.view-btn { padding:.35rem .75rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:8px; font-size:.8rem; font-weight:600; color:#5a7a5a; cursor:pointer; transition:all .18s; }
.view-btn.active,.view-btn:hover { background:#111; color:#fff; border-color:#111; }
.sort-options { display:flex; align-items:center; gap:.5rem; font-size:.8rem; color:#5a7a5a; }
.sort-select { padding:.35rem .625rem; border:1.5px solid var(--cream-border); border-radius:8px; font-size:.8rem; background:#fff; color:#1a2e1a; cursor:pointer; }

/* ── Estado carga ────────────────────────────────────────────────────────── */
.loading-state,.error-state { display:flex; flex-direction:column; align-items:center; padding:4rem 2rem; gap:.75rem; text-align:center; background:var(--card-bg); border-radius:14px; }
.spinner { width:32px; height:32px; border:3px solid var(--green-pale); border-top-color:var(--green-mid); border-radius:50%; animation:spin .7s linear infinite; }
@keyframes spin { to{transform:rotate(360deg)} }

/* ── Grid de libros ──────────────────────────────────────────────────────── */
.books-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:1.25rem; }
.book-card { background:var(--card-bg); border:1.5px solid var(--cream-border); border-radius:14px; overflow:hidden; box-shadow:var(--shadow-sm); display:flex; flex-direction:column; transition:box-shadow .2s,transform .18s; }
.book-card:hover { box-shadow:var(--shadow-md); transform:translateY(-2px); }
.book-card-top { position:relative; padding:1.25rem 1rem .875rem; display:flex; align-items:flex-start; justify-content:space-between; }
.book-icon-lg  { font-size:1.75rem; }
.card-c1 { background:linear-gradient(135deg,#1a4731,#2d6a4f); }
.card-c2 { background:linear-gradient(135deg,#92650a,#c9900c); }
.card-c3 { background:linear-gradient(135deg,#2c4a6e,#3d6490); }
.badge-status { position:absolute; top:.625rem; right:.625rem; font-size:.65rem; font-weight:700; padding:.2rem .5rem; border-radius:20px; }
.status-available { background:rgba(82,183,136,.25); color:#d8f3dc; border:1px solid rgba(82,183,136,.3); }
.status-borrowed  { background:rgba(244,197,66,.25); color:#fef9e7; border:1px solid rgba(244,197,66,.3); }
.status-repair    { background:rgba(255,165,0,.25);   color:#ffe4b5; border:1px solid rgba(255,165,0,.3); }
.status-lost      { background:rgba(220,38,38,.25);   color:#fecaca; border:1px solid rgba(220,38,38,.3); }
.card-code-badge { position:absolute; bottom:.625rem; left:.625rem; font-size:.65rem; font-family:monospace; background:rgba(0,0,0,.3); color:rgba(255,255,255,.8); padding:.15rem .45rem; border-radius:5px; }
.badge-prestable { position:absolute; bottom:.625rem; right:.625rem; font-size:.6rem; font-weight:700; background:rgba(82,183,136,.3); color:#d8f3dc; padding:.15rem .45rem; border-radius:5px; }
.book-body { flex:1; padding:.875rem 1rem; display:flex; flex-direction:column; gap:.375rem; }
.book-title  { font-family:'Playfair Display',serif; font-size:.925rem; font-weight:700; color:var(--green-dark); margin:0; line-height:1.4; }
.book-author { font-size:.78rem; color:#5a7a5a; margin:0; }
.book-details { font-size:.75rem; color:#64748b; display:flex; flex-direction:column; gap:2px; }
.book-details p { margin:0; }
.book-actions { padding:.625rem .875rem .875rem; display:flex; gap:.375rem; flex-wrap:wrap; border-top:1px solid #eef5f0; margin-top:auto; }

/* ── Lista ───────────────────────────────────────────────────────────────── */
.books-list .table-wrap { overflow-x:auto; }
.table-ui { width:100%; border-collapse:collapse; font-size:.82rem; background:var(--card-bg); border-radius:12px; overflow:hidden; box-shadow:var(--shadow-sm); }
.table-ui thead { background:linear-gradient(135deg,#1a4731,#2d6a4f); }
.table-ui thead th { padding:.75rem 1rem; text-align:left; color:rgba(255,255,255,.88); font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.06em; }
.table-ui tbody tr { border-bottom:1px solid #f1f5f0; transition:background .15s; }
.table-ui tbody tr:hover { background:#fafef8; }
.table-ui td { padding:.75rem 1rem; vertical-align:middle; }
.td-code,.td-title { font-weight:600; color:#1a2e1a; }
.td-sub    { font-size:.72rem; color:#9ab5a0; margin-top:2px; }
.td-author { font-size:.82rem; color:#334155; }
.td-actions { display:flex; gap:.35rem; }
.status-pill { font-size:.7rem; font-weight:700; padding:.2rem .55rem; border-radius:20px; white-space:nowrap; }

/* ── Modal base ──────────────────────────────────────────────────────────── */
.modal-overlay { position:fixed; inset:0; background:rgba(26,47,26,.55); backdrop-filter:blur(8px); display:flex; align-items:center; justify-content:center; z-index:2000; }
.modal-content { background:var(--card-bg); border-radius:16px; width:90%; max-width:520px; border:1.5px solid var(--cream-border); box-shadow:0 24px 64px rgba(0,0,0,.2); animation:modalIn .25s cubic-bezier(.22,1,.36,1); max-height:90vh; overflow-y:auto; }
.modal-detalles { max-width:640px; }
.modal-crear    { max-width:680px; }
@keyframes modalIn { from{opacity:0;transform:translateY(-14px) scale(.97)} to{opacity:1;transform:translateY(0) scale(1)} }
.modal-header { display:flex; justify-content:space-between; align-items:center; padding:1.1rem 1.375rem .875rem; border-bottom:1.5px solid #eef5f0; position:sticky; top:0; background:var(--card-bg); z-index:1; }
.modal-header h3 { font-family:'Playfair Display',serif; font-size:1.05rem; font-weight:700; color:var(--green-dark); margin:0; }
.modal-close-btn { background:none; border:none; font-size:1.3rem; color:#9ab5a0; cursor:pointer; }
.modal-body   { padding:1.25rem 1.375rem; display:flex; flex-direction:column; gap:.875rem; }
.modal-footer { display:flex; justify-content:flex-end; gap:.625rem; padding:.875rem 1.375rem; border-top:1.5px solid #eef5f0; position:sticky; bottom:0; background:var(--card-bg); }
.btn-modal-cancel  { padding:.5rem 1rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:600; color:#5a7a5a; cursor:pointer; }
.btn-modal-confirm { padding:.5rem 1.1rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:.4rem; }
.btn-modal-confirm:hover { background:#111; }
.btn-modal-delete  { padding:.5rem 1.1rem; background:#dc2626; color:#fff; border:none; border-radius:8px; font-size:.82rem; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:.4rem; }

/* ── Modal Detalles ──────────────────────────────────────────────────────── */
.detalles-grid { display:grid; grid-template-columns:1fr 1fr; gap:1.25rem; }
@media (max-width:540px) { .detalles-grid { grid-template-columns:1fr; } }
.detalle-titulo { font-family:'Playfair Display',serif; font-size:1.05rem; font-weight:700; color:var(--green-dark); margin:0 0 .25rem; }
.detalle-autor  { font-size:.82rem; color:#5a7a5a; }
.detalle-ficha  { display:flex; flex-direction:column; gap:.375rem; margin-top:.75rem; }
.ficha-row  { display:flex; gap:.5rem; font-size:.8rem; }
.ficha-lbl  { color:#9ab5a0; font-weight:700; min-width:70px; flex-shrink:0; font-size:.72rem; text-transform:uppercase; letter-spacing:.05em; }
.ficha-val  { color:#1a2e1a; font-weight:500; }
.mono       { font-family:monospace; }
.ejemplares-titulo { font-family:'Playfair Display',serif; font-size:.95rem; font-weight:700; color:var(--green-dark); margin:0 0 .75rem; }
.ejemplares-loading { display:flex; align-items:center; gap:.5rem; font-size:.8rem; color:#9ab5a0; }
.spinner-sm { width:16px; height:16px; border:2px solid var(--green-pale); border-top-color:var(--green-mid); border-radius:50%; animation:spin .7s linear infinite; }
.ejemplares-vacio { font-size:.8rem; color:#9ab5a0; font-style:italic; }
.ejemplares-lista { display:flex; flex-direction:column; gap:.5rem; }
.ejemplar-badge { display:flex; justify-content:space-between; align-items:center; padding:.5rem .75rem; border-radius:9px; font-size:.8rem; font-weight:600; border:1.5px solid; }
.ejemplar-disponible { background:var(--green-pale); color:var(--green-dark); border-color:#b8ddc8; }
.ejemplar-prestado   { background:#fff0f0; color:#b91c1c; border-color:#fca5a5; }
.ejemplar-reparacion { background:#fef3c7; color:#92400e; border-color:#fcd34d; }
.ejemplar-retirado   { background:#f1f5f9; color:#64748b; border-color:#cbd5e1; }
.ejemplar-num   { font-weight:700; }
.ejemplar-estado{ font-size:.72rem; opacity:.85; }
.ejemplares-resumen { font-size:.75rem; color:#9ab5a0; margin:.625rem 0 0; text-align:right; }

/* ── Modal Crear ─────────────────────────────────────────────────────────── */
.modo-toggle { display:flex; gap:.375rem; margin-bottom:.5rem; }
.modo-btn { padding:.4rem .875rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:8px; font-size:.8rem; font-weight:600; color:#5a7a5a; cursor:pointer; transition:all .18s; }
.modo-active { background:var(--green-mid); color:#fff; border-color:var(--green-mid); }
.crear-grid { display:grid; grid-template-columns:1fr 1fr; gap:.875rem; }
@media (max-width:480px) { .crear-grid { grid-template-columns:1fr; } }
.form-field { display:flex; flex-direction:column; gap:4px; }
.form-field-check { flex-direction:row; align-items:center; gap:.5rem; margin-top:.25rem; }
.form-label { font-size:.72rem; font-weight:700; color:var(--green-dark); text-transform:uppercase; letter-spacing:.07em; }
.form-label-check { font-size:.82rem; color:#1a2e1a; font-weight:500; cursor:pointer; display:flex; align-items:center; gap:.4rem; }
.form-input { padding:.55rem .75rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.875rem; color:#1a2e1a; outline:none; transition:border-color .2s; }
.form-input:focus { border-color:var(--green-light); }
.req { color:#d62828; }
.form-error   { padding:.6rem .875rem; background:#fff3f3; border:1px solid #f5c0c0; border-radius:9px; color:#d62828; font-size:.82rem; font-weight:600; }
.form-warning { padding:.6rem .875rem; background:#fef3c7; border:1px solid #fcd34d; border-radius:9px; color:#92400e; font-size:.82rem; font-weight:600; }

/* ── Modal Eliminar ──────────────────────────────────────────────────────── */
.book-to-delete { display:flex; flex-direction:column; gap:.875rem; }
.book-info-modal h4 { margin:0 0 .375rem; font-family:'Playfair Display',serif; color:var(--green-dark); }
.book-info-modal p  { font-size:.82rem; margin:.2rem 0; color:#334155; }
.warning-message { display:flex; align-items:flex-start; gap:.625rem; padding:.75rem; background:#fff5f5; border:1px solid #fca5a5; border-radius:9px; }
.warning-icon { font-size:1.25rem; }
.warning-message p { font-size:.82rem; margin:0; color:#7f1d1d; }
.spinner-small { width:12px; height:12px; border:2px solid rgba(255,255,255,.3); border-top-color:#fff; border-radius:50%; animation:spin .6s linear infinite; display:inline-block; }

/* ── Toast ───────────────────────────────────────────────────────────────── */
.toast { position:fixed; bottom:2rem; right:2rem; display:flex; align-items:center; gap:.75rem; padding:.875rem 1.1rem; background:#16a34a; border-radius:12px; color:#fff; font-size:.82rem; font-weight:600; z-index:9999; box-shadow:0 8px 30px rgba(0,0,0,.15); animation:slideIn .3s ease; }
.toast-icon    { font-size:1.1rem; }
.toast-content { flex:1; }
.toast-close   { background:none; border:none; color:rgba(255,255,255,.7); font-size:1.1rem; cursor:pointer; }
@keyframes slideIn { from{opacity:0;transform:translateX(20px)} to{opacity:1;transform:translateX(0)} }

/* ── Empty / Pagination ──────────────────────────────────────────────────── */
.empty-state { display:flex; flex-direction:column; align-items:center; padding:4rem 2rem; gap:.75rem; text-align:center; background:var(--card-bg); border-radius:14px; }
.empty-icon  { font-size:3rem; }
.empty-state h3 { font-family:'Playfair Display',serif; color:var(--green-dark); margin:0; }
.empty-state p  { color:#5a7a5a; margin:0; font-size:.875rem; }
.pagination-section { display:flex; justify-content:space-between; align-items:center; margin-top:1.25rem; flex-wrap:wrap; gap:.75rem; font-size:.8rem; color:#5a7a5a; }
.pagination-controls { display:flex; align-items:center; gap:.5rem; }
.page-numbers { display:flex; gap:.35rem; }
.page-number  { padding:.3rem .65rem; border-radius:7px; cursor:pointer; font-size:.8rem; font-weight:500; color:var(--green-mid); transition:all .15s; }
.page-number:hover,.page-number.active { background:var(--green-mid); color:#fff; }
.pbtn { padding:.35rem .75rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:7px; font-size:.78rem; font-weight:600; color:var(--green-mid); cursor:pointer; transition:all .15s; }
.pbtn:hover:not(:disabled) { background:#111; color:#fff; border-color:#111; }
.pbtn:disabled { opacity:.4; cursor:not-allowed; }
.items-per-page { display:flex; align-items:center; gap:.5rem; }
.page-select { padding:.3rem .55rem; border:1.5px solid var(--cream-border); border-radius:7px; font-size:.8rem; color:var(--green-dark); background:#fff; cursor:pointer; }
</style>