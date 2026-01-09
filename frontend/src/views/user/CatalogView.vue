<template>
  <div class="catalog-container">
    <!-- Header del Catálogo -->
    <header class="catalog-header">
      <div class="header-content">
        <h1 class="page-title">
          <span class="title-icon">📚</span>
          Catálogo de Libros
        </h1>
        <p class="page-subtitle">
          <span v-if="totalLibros > 0">Explora nuestra colección de {{ totalLibros }} libros</span>
          <span v-else>Cargando catálogo...</span>
        </p>
        
        <!-- Estadísticas rápidas -->
        <div class="stats-bar">
          <div class="stat-item">
            <span class="stat-icon">📖</span>
            <span class="stat-count">{{ librosDisponibles }}</span>
            <span class="stat-label">Disponibles</span>
          </div>
          <div class="stat-item">
            <span class="stat-icon">📊</span>
            <span class="stat-count">{{ totalLibros }}</span>
            <span class="stat-label">Total</span>
          </div>
          <div class="stat-item">
            <span class="stat-icon">🔢</span>
            <span class="stat-count">{{ ultimaPagina }}</span>
            <span class="stat-label">Páginas</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Panel de Búsqueda y Filtros -->
    <div class="search-panel">
      <div class="search-container">
        <div class="search-input-wrapper">
          <span class="search-icon">🔍</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por título, autor, editorial, ISBN..."
            class="search-input"
            @input="onSearchInput"
            @keyup.enter="buscarLibros"
          />
          <button
            v-if="searchQuery"
            @click="limpiarBusqueda"
            class="clear-search-btn"
            title="Limpiar búsqueda"
          >
            ✕
          </button>
          <button @click="buscarLibros" class="search-action-btn" title="Buscar">
            Buscar
          </button>
        </div>

        <!-- Filtros Avanzados -->
        <div class="filters-section">
          <div class="filter-group">
            <label class="filter-label">Estado:</label>
            <select v-model="estadoFiltro" @change="aplicarFiltros" class="filter-select">
              <option value="">Todos los estados</option>
              <option v-for="estado in estadosUnicos" :key="estado" :value="estado">
                {{ estado }}
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label class="filter-label">Área:</label>
            <select v-model="areaFiltro" @change="aplicarFiltros" class="filter-select">
              <option value="">Todas las áreas</option>
              <option v-for="area in areasUnicas" :key="area" :value="area">
                {{ area }}
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label class="filter-label">Prestable:</label>
            <select v-model="prestableFiltro" @change="aplicarFiltros" class="filter-select">
              <option value="">Todos</option>
              <option value="true">✅ Prestable</option>
              <option value="false">❌ No prestable</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label class="filter-label">Ordenar por:</label>
            <select v-model="ordenarPor" @change="aplicarFiltros" class="filter-select">
              <option value="titulo">Título (A-Z)</option>
              <option value="autor">Autor (A-Z)</option>
              <option value="editorial">Editorial (A-Z)</option>
              <option value="fecha_adquisicion">Fecha adquisición (nuevos)</option>
            </select>
          </div>

          <div class="filter-actions">
            <button @click="limpiarFiltros" class="btn btn-secondary btn-sm">
              <span class="btn-icon">🔄</span>
              Limpiar filtros
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Estado de carga/error -->
    <div v-if="cargando" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando catálogo...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <span class="error-icon">⚠️</span>
      <p>{{ error }}</p>
      <button @click="cargarLibros" class="btn btn-outline">Reintentar</button>
    </div>

    <!-- Contenido Principal -->
    <main v-else class="catalog-main">
      <!-- Vista de cuadrícula/tabla -->
      <div class="view-controls">
        <div class="view-toggle">
          <button 
            @click="modoVista = 'grid'"
            :class="['view-btn', { active: modoVista === 'grid' }]"
            title="Vista de cuadrícula"
          >
            <span class="view-icon">⏹️</span>
          </button>
          <button 
            @click="modoVista = 'list'"
            :class="['view-btn', { active: modoVista === 'list' }]"
            title="Vista de lista"
          >
            <span class="view-icon">📋</span>
          </button>
        </div>
        
        <div class="results-info">
          Mostrando {{ inicioItem }}-{{ finItem }} de {{ totalLibros }} libros
        </div>
      </div>

      <!-- Mensaje de resultados vacíos -->
      <div v-if="libros.length === 0" class="empty-state">
        <span class="empty-icon">📭</span>
        <h3>No se encontraron libros</h3>
        <p>Intenta con otros términos de búsqueda o filtros</p>
        <button @click="limpiarFiltros" class="btn btn-primary">Mostrar todos los libros</button>
      </div>

      <!-- Vista de Cuadrícula -->
      <div v-else-if="modoVista === 'grid'" class="books-grid">
        <div 
          v-for="libro in libros" 
          :key="libro.id" 
          class="book-card"
          @click="verDetallesLibro(libro)"
        >
          <div class="book-card-inner">
            <!-- Portada del libro -->
            <div class="book-cover-container">
              <div class="book-cover">
                <span class="default-cover">
                  📖
                </span>
                <div class="book-badges">
                  <span v-if="libro.es_prestable" class="badge prestable-badge">📚</span>
                  <span class="badge ejemplar-badge">#{{ libro.numero_ejemplar }}</span>
                </div>
              </div>
            </div>
            
            <!-- Información del libro -->
            <div class="book-info">
              <div class="book-header">
                <h3 class="book-title" :title="libro.titulo">{{ truncarTexto(libro.titulo, 40) }}</h3>
                <span class="book-code" :title="libro.codigo_decimal">
                  {{ libro.codigo_decimal || 'Sin código' }}
                </span>
              </div>
              
              <p class="book-author">
                <span class="info-icon">✍️</span>
                {{ libro.autor || 'Autor desconocido' }}
              </p>
              
              <div class="book-meta">
                <span class="meta-item" v-if="libro.editorial_nombre">
                  <span class="meta-icon">🏢</span>
                  {{ truncarTexto(libro.editorial_nombre, 20) }}
                </span>
                <span class="meta-item">
                  <span class="meta-icon">🔢</span>
                  ISBN: {{ libro.isbn || 'N/A' }}
                </span>
                <span class="meta-item" v-if="libro.edicion">
                  <span class="meta-icon">📅</span>
                  Ed. {{ libro.edicion }}
                </span>
              </div>
              
              <!-- Estado y disponibilidad -->
              <div class="book-status-section">
                <div :class="['status-badge', getEstadoClase(libro.estado_nombre)]">
                  {{ libro.estado_nombre || 'Desconocido' }}
                </div>
                
                <div class="prestable-info">
                  <span class="prestable-icon" :class="{ prestable: libro.es_prestable }">
                    {{ libro.es_prestable ? '✅' : '❌' }}
                  </span>
                  {{ libro.es_prestable ? 'Prestable' : 'No prestable' }}
                </div>
              </div>
              
              <!-- Información adicional -->
              <div class="book-details">
                <span class="detail-item" v-if="libro.area_conocimiento_nombre">
                  <span class="detail-icon">📚</span>
                  {{ libro.area_conocimiento_nombre }}
                </span>
                <span class="detail-item" v-if="libro.numero_paginas">
                  <span class="detail-icon">📄</span>
                  {{ libro.numero_paginas }} págs.
                </span>
                <span class="detail-item">
                  <span class="detail-icon">👤</span>
                  {{ libro.usuario_registro_nombre || 'Sistema' }}
                </span>
              </div>
              
              <!-- Acciones -->
              <div class="book-actions">
                <button 
                  v-if="libro.es_prestable && libro.estado_nombre?.toLowerCase() === 'disponible' && authStore.userRole >= 1"
                  @click.stop="solicitarPrestamo(libro)"
                  class="action-btn loan-btn"
                  title="Solicitar préstamo"
                >
                  <span class="action-icon">📥</span>
                  Solicitar Préstamo
                </button>
                
                <button 
                  @click.stop="verDetallesLibro(libro)"
                  class="action-btn details-btn"
                  title="Ver detalles completos"
                >
                  <span class="action-icon">🔍</span>
                  Ver Detalles
                </button>
                
                <button 
                  v-if="authStore.userRole >= 3"
                  @click.stop="editarLibro(libro)"
                  class="action-btn edit-btn"
                  title="Editar libro"
                >
                  <span class="action-icon">✏️</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Vista de Lista -->
      <div v-else class="books-list">
        <div class="table-container">
          <table class="books-table">
            <thead>
              <tr>
                <th @click="ordenarPorCampo('titulo')" class="sortable">
                  Título 
                  <span v-if="ordenCampo === 'titulo'" class="sort-icon">
                    {{ ordenDireccion === 'asc' ? '↑' : '↓' }}
                  </span>
                </th>
                <th @click="ordenarPorCampo('autor')" class="sortable">
                  Autor
                  <span v-if="ordenCampo === 'autor'" class="sort-icon">
                    {{ ordenDireccion === 'asc' ? '↑' : '↓' }}
                  </span>
                </th>
                <th>Editorial</th>
                <th>Estado</th>
                <th>Código</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="libro in libros" :key="libro.id">
                <td class="book-title-cell">
                  <div class="title-wrapper">
                    <div class="book-icon-small">
                      {{ libro.es_prestable ? '📚' : '📖' }}
                    </div>
                    <div>
                      <strong>{{ truncarTexto(libro.titulo, 50) }}</strong>
                      <div class="book-meta-row">
                        <span class="meta-tag">ISBN: {{ libro.isbn || 'N/A' }}</span>
                        <span v-if="libro.edicion" class="meta-tag">Ed. {{ libro.edicion }}</span>
                      </div>
                    </div>
                  </div>
                </td>
                <td>{{ libro.autor || 'N/A' }}</td>
                <td>{{ truncarTexto(libro.editorial_nombre, 25) }}</td>
                <td>
                  <span :class="['status-indicator', getEstadoClase(libro.estado_nombre)]">
                    {{ libro.estado_nombre || 'N/A' }}
                  </span>
                </td>
                <td>
                  <code class="book-code-small">{{ libro.codigo_decimal || 'N/A' }}</code>
                </td>
                <td>
                  <div class="table-actions">
                    <button 
                      v-if="libro.es_prestable && libro.estado_nombre?.toLowerCase() === 'disponible'"
                      @click="solicitarPrestamo(libro)"
                      class="table-btn loan"
                      title="Solicitar préstamo"
                    >
                      📥
                    </button>
                    <button 
                      @click="verDetallesLibro(libro)"
                      class="table-btn view"
                      title="Ver detalles"
                    >
                      🔍
                    </button>
                    <button 
                      v-if="authStore.userRole >= 3"
                      @click="editarLibro(libro)"
                      class="table-btn edit"
                      title="Editar"
                    >
                      ✏️
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Paginación -->
      <div v-if="totalPaginas > 1" class="pagination-section">
        <div class="pagination-controls">
          <button 
            @click="paginaAnterior" 
            :disabled="paginaActual === 1"
            class="pagination-btn prev"
          >
            ← Anterior
          </button>
          
          <div class="page-numbers">
            <button 
              v-for="pagina in paginasVisibles" 
              :key="pagina"
              @click="irAPagina(pagina)"
              :class="['page-btn', { active: pagina === paginaActual }]"
            >
              {{ pagina }}
            </button>
            <span v-if="mostrarElipsis" class="page-ellipsis">...</span>
          </div>
          
          <button 
            @click="paginaSiguiente" 
            :disabled="paginaActual === totalPaginas"
            class="pagination-btn next"
          >
            Siguiente →
          </button>
        </div>
        
        <div class="page-size-selector">
          <label>Mostrar por página:</label>
          <select v-model="porPagina" @change="cambiarPorPagina" class="page-size-select">
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { debounce } from 'lodash-es'

export default {
  name: 'CatalogView',
  
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    // Estado reactivo
    const libros = ref([])
    const cargando = ref(true)
    const error = ref(null)
    const searchQuery = ref('')
    const estadoFiltro = ref('')
    const areaFiltro = ref('')
    const prestableFiltro = ref('')
    const ordenarPor = ref('titulo')
    const modoVista = ref('grid')
    const paginaActual = ref(1)
    const porPagina = ref(20)
    
    // Datos de paginación del servidor
    const totalLibros = ref(0)
    const totalPaginas = ref(1)
    
    // Computed properties
    const estadosUnicos = computed(() => {
      const estados = libros.value.map(libro => libro.estado_nombre).filter(Boolean)
      return [...new Set(estados)].sort()
    })
    
    const areasUnicas = computed(() => {
      const areas = libros.value.map(libro => libro.area_conocimiento_nombre).filter(Boolean)
      return [...new Set(areas)].sort()
    })
    
    const librosDisponibles = computed(() => {
      return libros.value.filter(libro => 
        libro.es_prestable && 
        libro.estado_nombre?.toLowerCase() === 'disponible'
      ).length
    })
    
    const ultimaPagina = computed(() => totalPaginas.value)
    
    // Métodos para manejar la API
    const cargarLibros = async () => {
      cargando.value = true
      error.value = null
      
      try {
        // Construir parámetros de consulta
        const params = {
          pagina: paginaActual.value,
          por_pagina: porPagina.value,
          busqueda: searchQuery.value || undefined,
          estado: estadoFiltro.value || undefined,
          area_conocimiento: areaFiltro.value || undefined,
          es_prestable: prestableFiltro.value || undefined,
          ordenar_por: ordenarPor.value
        }
        
        // Eliminar parámetros undefined
        Object.keys(params).forEach(key => {
          if (params[key] === undefined) {
            delete params[key]
          }
        })
        
        // Llamar al endpoint de libros
        const response = await api.get('/api/libros', { params })
        
        if (response.data) {
          libros.value = response.data.libros || []
          totalLibros.value = response.data.total || 0
          totalPaginas.value = response.data.total_paginas || Math.ceil(totalLibros.value / porPagina.value)
          
          // Si no hay paginación en la respuesta, calcularla
          if (!response.data.total_paginas && totalLibros.value > 0) {
            totalPaginas.value = Math.ceil(totalLibros.value / porPagina.value)
          }
        }
      } catch (err) {
        console.error('Error cargando libros:', err)
        error.value = 'No se pudo cargar el catálogo. ' + (err.response?.data?.detail || err.message)
        
        // Datos de ejemplo para desarrollo
        if (process.env.NODE_ENV === 'development') {
          libros.value = obtenerLibrosEjemplo()
          totalLibros.value = libros.value.length
          totalPaginas.value = Math.ceil(totalLibros.value / porPagina.value)
        }
      } finally {
        cargando.value = false
      }
    }
    
    const buscarLibros = () => {
      paginaActual.value = 1
      cargarLibros()
    }
    
    const onSearchInput = debounce(() => {
      buscarLibros()
    }, 500)
    
    const solicitarPrestamo = async (libro) => {
      try {
        if (!authStore.isAuthenticated) {
          router.push({ 
            name: 'Login', 
            query: { redirect: router.currentRoute.value.fullPath } 
          })
          return
        }
        
        // Endpoint para solicitar préstamo
        const response = await api.post('/api/prestamos/solicitar', {
          libro_id: libro.id,
          usuario_id: authStore.userId,
          ejemplar_numero: libro.numero_ejemplar
        })
        
        if (response.data && response.data.success) {
          alert('✅ Solicitud de préstamo enviada exitosamente')
          // Actualizar el estado del libro
          libro.estado_nombre = 'Reservado'
        } else {
          alert('❌ ' + (response.data?.error || 'Error al solicitar préstamo'))
        }
      } catch (err) {
        console.error('Error solicitando préstamo:', err)
        alert('❌ Error al solicitar préstamo: ' + (err.response?.data?.detail || err.message))
      }
    }
    
    // Métodos auxiliares
    const truncarTexto = (texto, maxLength) => {
      if (!texto) return ''
      if (texto.length <= maxLength) return texto
      return texto.substring(0, maxLength) + '...'
    }
    
    const getEstadoClase = (estado) => {
      if (!estado) return 'desconocido'
      
      const estadoLower = estado.toLowerCase()
      if (estadoLower.includes('disponible')) return 'disponible'
      if (estadoLower.includes('prestado')) return 'prestado'
      if (estadoLower.includes('reservado')) return 'reservado'
      if (estadoLower.includes('mantenimiento')) return 'mantenimiento'
      return 'desconocido'
    }
    
    const limpiarBusqueda = () => {
      searchQuery.value = ''
      paginaActual.value = 1
      cargarLibros()
    }
    
    const limpiarFiltros = () => {
      searchQuery.value = ''
      estadoFiltro.value = ''
      areaFiltro.value = ''
      prestableFiltro.value = ''
      ordenarPor.value = 'titulo'
      paginaActual.value = 1
      cargarLibros()
    }
    
    const aplicarFiltros = () => {
      paginaActual.value = 1
      cargarLibros()
    }
    
    const ordenarPorCampo = (campo) => {
      ordenarPor.value = campo
      cargarLibros()
    }
    
    const verDetallesLibro = (libro) => {
      // Navegar a vista de detalles
      router.push({ name: 'BookDetails', params: { id: libro.id } })
    }
    
    const editarLibro = (libro) => {
      if (authStore.userRole >= 3) {
        router.push({ name: 'EditBook', params: { id: libro.id } })
      }
    }
    
    // Paginación
    const paginaSiguiente = () => {
      if (paginaActual.value < totalPaginas.value) {
        paginaActual.value++
        cargarLibros()
      }
    }
    
    const paginaAnterior = () => {
      if (paginaActual.value > 1) {
        paginaActual.value--
        cargarLibros()
      }
    }
    
    const irAPagina = (pagina) => {
      paginaActual.value = pagina
      cargarLibros()
    }
    
    const cambiarPorPagina = () => {
      paginaActual.value = 1
      cargarLibros()
    }
    
    const inicioItem = computed(() => {
      return (paginaActual.value - 1) * porPagina.value + 1
    })
    
    const finItem = computed(() => {
      return Math.min(paginaActual.value * porPagina.value, totalLibros.value)
    })
    
    const paginasVisibles = computed(() => {
      const paginas = []
      const maxVisible = 5
      let start = Math.max(1, paginaActual.value - Math.floor(maxVisible / 2))
      let end = start + maxVisible - 1
      
      if (end > totalPaginas.value) {
        end = totalPaginas.value
        start = Math.max(1, end - maxVisible + 1)
      }
      
      for (let i = start; i <= end; i++) {
        paginas.push(i)
      }
      
      return paginas
    })
    
    const mostrarElipsis = computed(() => {
      return totalPaginas.value > paginasVisibles.value.length
    })
    
    const ordenCampo = computed(() => {
      return ordenarPor.value
    })
    
    const ordenDireccion = computed(() => {
      // Por ahora asumimos ascendente, puedes añadir lógica para cambiar dirección
      return 'asc'
    })
    
    // Datos de ejemplo para desarrollo
    const obtenerLibrosEjemplo = () => {
      return [
        {
          id: 1,
          codigo_decimal: "821.111(73)",
          etiqueta: "FIC HEM",
          numero_ejemplar: 1,
          isbn: "9788497592208",
          titulo: "Cien años de soledad",
          autor: "Gabriel García Márquez",
          editorial_id: 1,
          editorial_nombre: "Sudamericana",
          edicion: 1,
          numero_paginas: 471,
          area_conocimiento_id: 1,
          area_conocimiento_nombre: "Literatura",
          metodo_adquisicion_id: 1,
          metodo_adquisicion_nombre: "Compra",
          proveedor_nombre: "Librería Nacional",
          precio: "25.99",
          es_prestable: true,
          estado_id: 1,
          estado_nombre: "Disponible",
          fecha_adquisicion: "2024-01-15",
          fecha_cambio_estado: "2024-01-15",
          usuario_registro_id: 1,
          usuario_registro_nombre: "Admin Sistema"
        },
        {
          id: 2,
          codigo_decimal: "813.54",
          etiqueta: "FIC KIN",
          numero_ejemplar: 1,
          isbn: "9781501180989",
          titulo: "It",
          autor: "Stephen King",
          editorial_id: 2,
          editorial_nombre: "Viking Press",
          edicion: 2,
          numero_paginas: 1138,
          area_conocimiento_id: 2,
          area_conocimiento_nombre: "Terror",
          metodo_adquisicion_id: 1,
          metodo_adquisicion_nombre: "Donación",
          proveedor_nombre: "Donante Particular",
          precio: "0.00",
          es_prestable: true,
          estado_id: 2,
          estado_nombre: "Prestado",
          fecha_adquisicion: "2024-02-20",
          fecha_cambio_estado: "2024-03-10",
          usuario_registro_id: 1,
          usuario_registro_nombre: "Admin Sistema"
        },
        {
          id: 3,
          codigo_decimal: "821.134.2",
          etiqueta: "POE CER",
          numero_ejemplar: 1,
          isbn: "9788420639132",
          titulo: "Poesía completa",
          autor: "Miguel de Cervantes",
          editorial_id: 3,
          editorial_nombre: "Alianza Editorial",
          edicion: 3,
          numero_paginas: 320,
          area_conocimiento_id: 1,
          area_conocimiento_nombre: "Literatura",
          metodo_adquisicion_id: 1,
          metodo_adquisicion_nombre: "Compra",
          proveedor_nombre: "Librería Cervantes",
          precio: "18.50",
          es_prestable: false,
          estado_id: 1,
          estado_nombre: "Disponible",
          fecha_adquisicion: "2024-03-05",
          fecha_cambio_estado: "2024-03-05",
          usuario_registro_id: 2,
          usuario_registro_nombre: "Bibliotecario"
        }
      ]
    }
    
    // Lifecycle hooks
    onMounted(() => {
      cargarLibros()
    })
    
    watch([paginaActual, porPagina], cargarLibros)
    
    return {
      // Estado
      libros,
      cargando,
      error,
      searchQuery,
      estadoFiltro,
      areaFiltro,
      prestableFiltro,
      ordenarPor,
      modoVista,
      paginaActual,
      porPagina,
      totalLibros,
      totalPaginas,
      
      // Computed
      estadosUnicos,
      areasUnicas,
      librosDisponibles,
      ultimaPagina,
      inicioItem,
      finItem,
      paginasVisibles,
      mostrarElipsis,
      ordenCampo,
      ordenDireccion,
      
      // Store
      authStore,
      
      // Métodos
      cargarLibros,
      buscarLibros,
      onSearchInput,
      solicitarPrestamo,
      truncarTexto,
      getEstadoClase,
      limpiarBusqueda,
      limpiarFiltros,
      aplicarFiltros,
      ordenarPorCampo,
      verDetallesLibro,
      editarLibro,
      paginaSiguiente,
      paginaAnterior,
      irAPagina,
      cambiarPorPagina
    }
  }
}
</script>

<style scoped>
/* Estilos generales */
.catalog-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

/* Header */
.catalog-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.title-icon {
  font-size: 2.8rem;
}

.page-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 25px;
}

.stats-bar {
  display: flex;
  gap: 30px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.15);
  padding: 12px 20px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.stat-icon {
  font-size: 1.5rem;
}

.stat-count {
  font-size: 1.8rem;
  font-weight: 700;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

/* Panel de búsqueda */
.search-panel {
  background: white;
  border-radius: 20px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
}

.search-container {
  max-width: 1200px;
  margin: 0 auto;
}

.search-input-wrapper {
  position: relative;
  margin-bottom: 25px;
}

.search-icon {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
  color: #667eea;
}

.search-input {
  width: 100%;
  padding: 18px 60px 18px 50px;
  border: 2px solid #e0e6ff;
  border-radius: 15px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f8f9ff;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  background: white;
}

.clear-search-btn {
  position: absolute;
  right: 120px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #999;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-search-btn:hover {
  background: #f0f0f0;
  color: #666;
}

.search-action-btn {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s ease;
}

.search-action-btn:hover {
  background: #5a6fd8;
}

/* Filtros */
.filters-section {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 180px;
  flex: 1;
}

.filter-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
}

.filter-select {
  padding: 10px 15px;
  border: 2px solid #e0e6ff;
  border-radius: 10px;
  background: white;
  font-size: 0.9rem;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
}

.filter-actions {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 0.9rem;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5a6fd8;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #f0f4ff;
  color: #667eea;
  border: 2px solid #e0e6ff;
}

.btn-secondary:hover {
  background: #e0e6ff;
}

.btn-outline {
  background: transparent;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-outline:hover {
  background: #667eea;
  color: white;
}

.btn-icon {
  font-size: 1rem;
}

/* Estados de carga/error */
.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 20px;
  margin: 30px 0;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f0f0f0;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error