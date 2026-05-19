<template>
  <div class="gestion-prestamos">

    <!-- ══ HEADER ══ -->
    <header class="page-header">
      <div class="header-inner">
        <div class="header-texto">
          <p class="header-sup">Panel — Bibliotecario</p>
          <h1 class="header-titulo">Préstamos de Libros</h1>
          <p class="header-sub">Gestiona préstamos activos e historial del CID</p>
        </div>
        <button class="btn-nuevo" @click="abrirModalCrear">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
          </svg>
          Nuevo Préstamo
        </button>
      </div>
    </header>

    <!-- ══ TABS + BÚSQUEDA ══ -->
    <div class="toolbar">
      <div class="tabs">
        <button
          v-for="tab in tabs" :key="tab.id"
          class="tab-btn" :class="{ 'tab-active': activeTab === tab.id }"
          @click="cambiarTab(tab.id)"
        >
          {{ tab.label }}
          <span v-if="tab.count > 0" class="tab-badge" :class="tab.badgeClass">{{ tab.count }}</span>
        </button>
      </div>

      <div class="search-wrap">
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input v-model="busqueda" type="text" class="search-input" placeholder="Buscar por estudiante, título, código..."/>
        <button v-if="busqueda" class="search-clear" @click="busqueda = ''">×</button>
      </div>
    </div>

    <!-- ══ TABLA ══ -->
    <div class="tabla-section">
      <div v-if="isLoading" class="estado-c"><div class="spinner"></div><p>Cargando préstamos...</p></div>
      <div v-else-if="errorMsg" class="estado-e"><p>{{ errorMsg }}</p><button class="btn-retry" @click="cargar">Reintentar</button></div>

      <div v-else-if="filtrados.length === 0" class="estado-v">
        <svg width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" class="vacio-ico">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
        </svg>
        <p class="vacio-titulo">
          {{ busqueda ? 'Sin resultados' : activeTab === 'vigentes' ? 'No hay préstamos vigentes' : activeTab === 'vencidos' ? 'No hay préstamos vencidos' : 'Sin historial' }}
        </p>
      </div>

      <div v-else class="tabla-wrap">
        <table class="tabla">
          <thead>
            <tr>
              <th style="width:55px">ID</th>
              <th>Libro</th>
              <th style="width:180px">Estudiante</th>
              <th style="width:110px">Prestado</th>
              <th style="width:140px">{{ activeTab === 'historial' ? 'Devuelto' : 'Devolver para' }}</th>
              <th style="width:130px">Estado</th>
              <th v-if="activeTab !== 'historial'" style="width:130px">Acciones</th>
              <th v-else style="width:90px">Retraso</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in paginados" :key="p.id" :class="{ 'fila-vencida': estadoVisual(p) === 'vencido' }">
              <td class="td-id">#{{ p.id }}</td>
              <td>
                <div class="td-titulo">{{ p.libro_titulo }}</div>
                <div class="td-sub">{{ p.libro_autor }}</div>
                <div class="td-sub mono" v-if="p.libro_codigo_decimal">{{ p.libro_codigo_decimal }}</div>
              </td>
              <td>
                <div class="td-nombre">{{ p.usuario_prestado_nombre }}</div>
                <div class="td-sub">Por: {{ p.usuario_presta_nombre }}</div>
              </td>
              <td class="td-fecha">{{ fmt(p.fecha_prestamo) }}</td>
              <td>
                <div class="td-fecha">
                  {{ activeTab === 'historial' ? fmt(p.fecha_devolucion_real) : fmt(p.fecha_devolucion_esperada) }}
                </div>
                <div v-if="activeTab !== 'historial'">
                  <span v-if="estadoVisual(p) === 'vencido'" class="dias-vencido">+{{ Math.abs(calcDias(p)) }} día(s)</span>
                  <span v-else-if="estadoVisual(p) === 'por_vencer'" class="dias-alerta">{{ calcDias(p) }} día(s)</span>
                </div>
              </td>
              <td><span class="estado-badge" :class="getBadgeClass(p)">{{ getBadgeText(p) }}</span></td>
              <td v-if="activeTab !== 'historial'">
                <div class="acciones">
                  <button class="tbl-btn tbl-green" @click="abrirModalDevolver(p)">
                    <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/>
                    </svg>
                    Devolver
                  </button>
                </div>
              </td>
              <td v-else>
                <span v-if="p.dias_excedidos > 0" class="dias-vencido">+{{ p.dias_excedidos }}d</span>
                <span v-else class="dias-ok">A tiempo</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginación -->
      <div v-if="!isLoading && filtrados.length > 0" class="paginacion">
        <span class="pag-info">{{ desde }}–{{ hasta }} de {{ filtrados.length }}</span>
        <div class="pag-controles">
          <button class="pag-btn" :disabled="pagina === 1" @click="pagina--">← Anterior</button>
          <span v-for="pg in paginas" :key="pg" class="pag-num" :class="{ 'pag-num-active': pg === pagina }" @click="pagina = pg">{{ pg }}</span>
          <button class="pag-btn" :disabled="pagina === totalPaginas" @click="pagina++">Siguiente →</button>
        </div>
        <div class="pag-size">
          <select v-model="porPagina" @change="pagina = 1" class="pag-select">
            <option :value="15">15</option><option :value="30">30</option><option :value="50">50</option>
          </select>
        </div>
      </div>
    </div>

    <!-- ══ MODAL: NUEVO PRÉSTAMO ══ -->
    <div v-if="modalCrear.visible" class="modal-overlay" @click.self="cerrarModalCrear">
      <div class="modal">
        <div class="modal-header">
          <h3>Registrar Préstamo</h3>
          <button class="modal-close" @click="cerrarModalCrear" :disabled="procesando">×</button>
        </div>
        <div class="modal-body">

          <!-- Libro -->
          <div class="form-field">
            <label class="form-label">Libro <span class="req">*</span></label>
            <div v-if="!crearForm.libroSeleccionado">
              <input
                v-model="crearForm.busquedaLibro"
                type="text" class="form-input"
                placeholder="Buscar por título o autor..."
                @input="buscarLibros"
              />
              <div v-if="buscandoLibros" class="sug-cargando">Buscando...</div>
              <div v-else-if="librosSug.length" class="sugerencias">
                <div v-for="libro in librosSug" :key="libro.id" class="sug-item" @click="selLibro(libro)">
                  <div class="sug-titulo">{{ libro.titulo }}</div>
                  <div class="sug-sub">{{ libro.autor }} · {{ libro.codigo_decimal }}</div>
                </div>
              </div>
              <div v-else-if="crearForm.busquedaLibro.length >= 2" class="sug-vacio">Sin resultados</div>
            </div>
            <div v-else class="seleccionado">
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" style="flex-shrink:0;color:var(--green-mid)">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
              <div class="sel-info">
                <div class="sel-titulo">{{ crearForm.libroSeleccionado.titulo }}</div>
                <div class="sel-sub">{{ crearForm.libroSeleccionado.autor }} · {{ crearForm.libroSeleccionado.codigo_decimal }}</div>
              </div>
              <button class="sel-quitar" @click="crearForm.libroSeleccionado = null; crearForm.busquedaLibro = ''">×</button>
            </div>
          </div>

          <!-- Estudiante -->
          <div class="form-field">
            <label class="form-label">Estudiante <span class="req">*</span></label>
            <div v-if="!crearForm.usuarioSeleccionado">
              <input
                v-model="crearForm.busquedaUsuario"
                type="text" class="form-input"
                placeholder="Buscar por nombre o código universitario..."
                @input="buscarUsuarios"
              />
              <div v-if="buscandoUsuarios" class="sug-cargando">Buscando...</div>
              <div v-else-if="usuariosSug.length" class="sugerencias">
                <div v-for="u in usuariosSug" :key="u.id" class="sug-item" @click="selUsuario(u)">
                  <div class="sug-titulo">{{ u.nombre_completo }}</div>
                  <div class="sug-sub">{{ u.codigo_universitario }}</div>
                </div>
              </div>
              <div v-else-if="crearForm.busquedaUsuario.length >= 2" class="sug-vacio">Sin resultados</div>
            </div>
            <div v-else class="seleccionado">
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" style="flex-shrink:0;color:var(--green-mid)">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              <div class="sel-info">
                <div class="sel-titulo">{{ crearForm.usuarioSeleccionado.nombre_completo }}</div>
                <div class="sel-sub">{{ crearForm.usuarioSeleccionado.codigo_universitario }}</div>
              </div>
              <button class="sel-quitar" @click="crearForm.usuarioSeleccionado = null; crearForm.busquedaUsuario = ''">×</button>
            </div>
          </div>

          <!-- Fecha — solo día, sin hora -->
          <div class="form-field">
            <label class="form-label">Fecha de devolución esperada <span class="req">*</span></label>
            <input type="date" v-model="crearForm.fecha_devolucion" class="form-input" :min="fechaMinimaDate"/>
          </div>

          <!-- Observaciones -->
          <div class="form-field">
            <label class="form-label">Observaciones</label>
            <textarea v-model="crearForm.observaciones" class="form-input form-textarea" rows="2" placeholder="Condición del libro, notas..."></textarea>
          </div>

          <div v-if="modalCrear.error" class="form-error">{{ modalCrear.error }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="cerrarModalCrear" :disabled="procesando">Cancelar</button>
          <button class="btn-modal-confirm" @click="guardarPrestamo" :disabled="procesando">
            <span v-if="procesando" class="spinner-mini"></span>
            {{ procesando ? 'Registrando...' : 'Registrar Préstamo' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══ MODAL: DEVOLUCIÓN ══ -->
    <div v-if="modalDevolver.visible" class="modal-overlay" @click.self="cerrarModalDevolver">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>Registrar Devolución</h3>
          <button class="modal-close" @click="cerrarModalDevolver" :disabled="procesando">×</button>
        </div>
        <div class="modal-body">
          <div class="resumen-prestamo">
            <div class="rp-row"><span class="rp-lbl">Libro</span><span class="rp-val">{{ modalDevolver.prestamo?.libro_titulo }}</span></div>
            <div class="rp-row"><span class="rp-lbl">Autor</span><span class="rp-val">{{ modalDevolver.prestamo?.libro_autor }}</span></div>
            <div class="rp-row"><span class="rp-lbl">Estudiante</span><span class="rp-val">{{ modalDevolver.prestamo?.usuario_prestado_nombre }}</span></div>
            <div class="rp-row"><span class="rp-lbl">Debía devolver</span><span class="rp-val">{{ fmt(modalDevolver.prestamo?.fecha_devolucion_esperada) }}</span></div>
          </div>

          <div v-if="modalDevolver.prestamo && estadoVisual(modalDevolver.prestamo) === 'vencido'" class="alerta-multa">
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="flex-shrink:0;color:#dc2626;margin-top:1px">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <div>
              <p class="alerta-titulo">Vencido — {{ Math.abs(calcDias(modalDevolver.prestamo)) }} día(s) de retraso</p>
              <p class="alerta-desc">Multa automática: <strong>${{ Math.abs(calcDias(modalDevolver.prestamo)) * 5 }} MXN</strong> ($5/día)</p>
            </div>
          </div>

          <div class="form-field">
            <label class="form-label">Observaciones</label>
            <textarea v-model="modalDevolver.observaciones" class="form-input form-textarea" rows="2" placeholder="Condición del libro al devolver..."></textarea>
          </div>
          <div v-if="modalDevolver.error" class="form-error">{{ modalDevolver.error }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="cerrarModalDevolver" :disabled="procesando">Cancelar</button>
          <button class="btn-modal-confirm" @click="confirmarDevolucion" :disabled="procesando">
            <span v-if="procesando" class="spinner-mini"></span>
            {{ procesando ? 'Registrando...' : 'Confirmar Devolución' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══ MODAL: RESULTADO DEVOLUCIÓN ══ -->
    <div v-if="modalResultado.visible" class="modal-overlay" @click.self="modalResultado.visible = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>Devolución Registrada</h3>
          <button class="modal-close" @click="modalResultado.visible = false">×</button>
        </div>
        <div class="modal-body">
          <div class="resultado-ok">
            <div class="resultado-check">✓</div>
            <p>{{ modalResultado.mensaje }}</p>
          </div>
          <div v-if="modalResultado.multa" class="multa-generada">
            <p class="multa-etiqueta">Multa generada automáticamente</p>
            <p class="multa-monto">${{ modalResultado.multa.costo_monetario }} MXN</p>
            <p class="multa-detalle">{{ modalResultado.multa.dias_excedidos }} día(s) × $5.00/día</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-confirm" @click="modalResultado.visible = false">Aceptar</button>
        </div>
      </div>
    </div>

    <!-- ══ TOAST ══ -->
    <transition name="toast-in">
      <div v-if="toast.visible" class="toast" :class="toast.tipo">
        {{ toast.msg }}
        <button class="toast-close" @click="toast.visible = false">×</button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { prestamoLibroService, calcularEstadoVisual, calcularDiasRestantes } from '@/services/PrestamoLibro'
import api from '@/services/api'
import '@/styles/buttons.css'

// ── State ──────────────────────────────────────────────────────────────────
const prestamos  = ref([])
const isLoading  = ref(false)
const errorMsg   = ref(null)
const procesando = ref(false)
const busqueda   = ref('')
const activeTab  = ref('vigentes')
const pagina     = ref(1)
const porPagina  = ref(15)

// Modales
const modalCrear    = ref({ visible: false, error: '' })
const modalDevolver = ref({ visible: false, prestamo: null, observaciones: '', error: '' })
const modalResultado = ref({ visible: false, mensaje: '', multa: null })
const toast         = ref({ visible: false, msg: '', tipo: 'toast-success' })

// Formulario crear
const crearForm = ref({
  busquedaLibro: '', libroSeleccionado: null,
  busquedaUsuario: '', usuarioSeleccionado: null,
  fecha_devolucion: '', observaciones: ''
})
const librosSug        = ref([])
const usuariosSug      = ref([])
const buscandoLibros   = ref(false)
const buscandoUsuarios = ref(false)

// ── Tabs ───────────────────────────────────────────────────────────────────
const tabs = computed(() => {
  const hoy = new Date(); hoy.setHours(0,0,0,0)
  const vigentes = prestamos.value.filter(p => p.estado_prestamo_id === 1)
  const vencidos = vigentes.filter(p => new Date(p.fecha_devolucion_esperada) < hoy)
  return [
    { id: 'vigentes',  label: 'Vigentes',  count: vigentes.length - vencidos.length, badgeClass: 'badge-green' },
    { id: 'vencidos',  label: 'Vencidos',  count: vencidos.length, badgeClass: 'badge-red' },
    { id: 'historial', label: 'Historial', count: 0, badgeClass: '' },
  ]
})

// ── Computed ───────────────────────────────────────────────────────────────
const filtrados = computed(() => {
  let r = [...prestamos.value]
  if      (activeTab.value === 'vigentes') r = r.filter(p => estadoVisual(p) !== 'vencido')
  else if (activeTab.value === 'vencidos') r = r.filter(p => estadoVisual(p) === 'vencido')

  if (busqueda.value.trim()) {
    const q = busqueda.value.toLowerCase()
    r = r.filter(p =>
      p.libro_titulo?.toLowerCase().includes(q)            ||
      p.libro_autor?.toLowerCase().includes(q)             ||
      p.usuario_prestado_nombre?.toLowerCase().includes(q) ||
      p.libro_codigo_decimal?.toLowerCase().includes(q)
    )
  }
  return r
})

const totalPaginas = computed(() => Math.ceil(filtrados.value.length / porPagina.value) || 1)
const paginados    = computed(() => filtrados.value.slice((pagina.value - 1) * porPagina.value, pagina.value * porPagina.value))
const desde        = computed(() => (pagina.value - 1) * porPagina.value + 1)
const hasta        = computed(() => Math.min(pagina.value * porPagina.value, filtrados.value.length))
const paginas      = computed(() => {
  const max = 5, tot = totalPaginas.value
  if (tot <= max) return Array.from({ length: tot }, (_, i) => i + 1)
  let s = Math.max(1, pagina.value - 2)
  const e = Math.min(tot, s + max - 1)
  if (e - s + 1 < max) s = e - max + 1
  return Array.from({ length: e - s + 1 }, (_, i) => s + i)
})

// Fecha mínima para el date picker — solo formato YYYY-MM-DD
const fechaMinimaDate = computed(() => new Date().toISOString().split('T')[0])

// ── Helpers ────────────────────────────────────────────────────────────────
const estadoVisual = (p) => calcularEstadoVisual(p)
const calcDias     = (p) => calcularDiasRestantes(p)
const fmt = (d) => d ? new Date(d).toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'

const getBadgeClass = (p) => ({
  'badge-vigente':    estadoVisual(p) === 'vigente',
  'badge-por-vencer': estadoVisual(p) === 'por_vencer',
  'badge-vencido':    estadoVisual(p) === 'vencido',
  'badge-terminado':  estadoVisual(p) === 'terminado',
})
const getBadgeText = (p) => {
  const ev = estadoVisual(p)
  if (ev === 'vencido')    return `Vencido +${Math.abs(calcDias(p))}d`
  if (ev === 'por_vencer') return `Vence en ${calcDias(p)}d`
  if (ev === 'terminado')  return 'Terminado'
  return 'Vigente'
}

const mostrarToast = (msg, tipo = 'toast-success') => {
  toast.value = { visible: true, msg, tipo }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

// ── Carga ──────────────────────────────────────────────────────────────────
const cargar = async () => {
  isLoading.value = true; errorMsg.value = null
  try {
    prestamos.value = await (
      activeTab.value === 'historial'
        ? prestamoLibroService.getHistorial()
        : prestamoLibroService.getVigentes()
    )
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || 'Error cargando préstamos'
  } finally {
    isLoading.value = false
  }
}

const cambiarTab = async (tab) => { activeTab.value = tab; pagina.value = 1; await cargar() }

// ── Autocomplete libros — usa params del backend ────────────────────────────
// Backend acepta: titulo, autor, estado_id=1, es_prestable=true
let timerL, timerU

const buscarLibros = () => {
  clearTimeout(timerL)
  librosSug.value = []
  const q = crearForm.value.busquedaLibro.trim()
  if (q.length < 2) return
  buscandoLibros.value = true
  timerL = setTimeout(async () => {
    try {
      const r = await api.get('/api/libros/', {
        params: {
          titulo:     q,
          estado_id:  1,          // solo disponibles
          es_prestable: true,
          por_pagina: 8,
          pagina:     1,
        }
      })
      let libros = r.data?.libros ?? (Array.isArray(r.data) ? r.data : [])
      // Si no hay resultados por título, intentar por autor
      if (!libros.length) {
        const r2 = await api.get('/api/libros/', {
          params: { autor: q, estado_id: 1, es_prestable: true, por_pagina: 8, pagina: 1 }
        })
        libros = r2.data?.libros ?? []
      }
      librosSug.value = libros
    } catch { librosSug.value = [] }
    finally { buscandoLibros.value = false }
  }, 350)
}

// ── Autocomplete usuarios — usa params del backend ──────────────────────────
// Backend acepta: nombre_filter, codigo_filter, activos_only
const buscarUsuarios = () => {
  clearTimeout(timerU); usuariosSug.value = []
  const q = crearForm.value.busquedaUsuario.trim()
  if (q.length < 2) return
  buscandoUsuarios.value = true
  timerU = setTimeout(async () => {
    try {
      const r = await api.get('/api/usuarios/buscar', { params: { q } })
      usuariosSug.value = r.data
    } catch { usuariosSug.value = [] }
    finally { buscandoUsuarios.value = false }
  }, 350)
}

const selLibro   = (l) => { crearForm.value.libroSeleccionado = l;   crearForm.value.busquedaLibro = '';   librosSug.value = [] }
const selUsuario = (u) => { crearForm.value.usuarioSeleccionado = u; crearForm.value.busquedaUsuario = ''; usuariosSug.value = [] }

// ── Modal crear ────────────────────────────────────────────────────────────
const abrirModalCrear = () => {
  crearForm.value = { busquedaLibro: '', libroSeleccionado: null, busquedaUsuario: '', usuarioSeleccionado: null, fecha_devolucion: '', observaciones: '' }
  librosSug.value = []; usuariosSug.value = []
  modalCrear.value = { visible: true, error: '' }
}
const cerrarModalCrear = () => { if (!procesando.value) modalCrear.value.visible = false }

const guardarPrestamo = async () => {
  if (!crearForm.value.libroSeleccionado)   { modalCrear.value.error = 'Selecciona un libro'; return }
  if (!crearForm.value.usuarioSeleccionado) { modalCrear.value.error = 'Selecciona un estudiante'; return }
  if (!crearForm.value.fecha_devolucion)    { modalCrear.value.error = 'Indica la fecha de devolución'; return }

  procesando.value = true
  try {
    // Convertir fecha YYYY-MM-DD a datetime ISO para el backend
    const fechaISO = `${crearForm.value.fecha_devolucion}T23:59:00`
    const nuevo = await prestamoLibroService.crearPrestamo({
      libro_id:                  crearForm.value.libroSeleccionado.id,
      usuario_prestado_id:       crearForm.value.usuarioSeleccionado.id,
      fecha_devolucion_esperada: fechaISO,
      observaciones:             crearForm.value.observaciones || null
    })
    if (activeTab.value !== 'historial') prestamos.value.unshift(nuevo)
    modalCrear.value.visible = false
    mostrarToast(`Préstamo de "${crearForm.value.libroSeleccionado.titulo}" registrado`)
  } catch (e) {
    modalCrear.value.error = e.response?.data?.detail || 'Error al registrar el préstamo'
  } finally {
    procesando.value = false
  }
}

// ── Modal devolver ─────────────────────────────────────────────────────────
const abrirModalDevolver  = (p) => { modalDevolver.value = { visible: true, prestamo: p, observaciones: '', error: '' } }
const cerrarModalDevolver = () => { if (!procesando.value) modalDevolver.value.visible = false }

const confirmarDevolucion = async () => {
  const p = modalDevolver.value.prestamo
  if (!p) return
  procesando.value = true
  try {
    const resultado = await prestamoLibroService.registrarDevolucion(p.id, modalDevolver.value.observaciones || null)
    prestamos.value = prestamos.value.filter(x => x.id !== p.id)
    modalDevolver.value.visible = false
    modalResultado.value = { visible: true, mensaje: resultado.mensaje, multa: resultado.multa_generada }
  } catch (e) {
    modalDevolver.value.error = e.response?.data?.detail || 'Error al registrar la devolución'
  } finally {
    procesando.value = false
  }
}

watch([busqueda], () => { pagina.value = 1 })
onMounted(cargar)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

:root {
  --green-dark:   #1a4731; --green-mid:    #2d6a4f;
  --green-light:  #52b788; --green-pale:   #d8f3dc;
  --gold-mid:     #c9900c; --gold-light:   #f4c542;
  --cream:        #f5f0e8; --cream-border: #d4e8da;
  --card-bg:      #fffef9; --shadow-sm:    0 2px 12px rgba(26,47,26,.08);
}

.gestion-prestamos { font-family:'DM Sans',sans-serif; min-height:100vh; background:radial-gradient(ellipse 70% 40% at 5% 0%,rgba(82,183,136,.08) 0%,transparent 55%),radial-gradient(ellipse 50% 40% at 90% 100%,rgba(201,144,12,.07) 0%,transparent 50%),var(--cream); }

/* ── Header ──────────────────────────────────────────────────────────────── */
.page-header { background:linear-gradient(135deg,#1a4731 0%,#2d6a4f 60%,#3a7d5e 100%); padding:1.75rem 2rem; position:relative; overflow:hidden; }
.page-header::before { content:''; position:absolute; inset:0; pointer-events:none; background:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E"); }
.header-inner { display:flex; justify-content:space-between; align-items:center; gap:1.5rem; flex-wrap:wrap; position:relative; }
.header-sup   { font-size:.72rem; font-weight:600; color:rgba(255,255,255,.5); text-transform:uppercase; letter-spacing:.1em; margin-bottom:.2rem; }
.header-titulo{ font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700; color:#fff; margin-bottom:.3rem; }
.header-sub   { font-size:.8rem; color:rgba(255,255,255,.65); margin:0; }
.btn-nuevo { display:flex; align-items:center; gap:.4rem; padding:.55rem 1.25rem; background:linear-gradient(135deg,var(--gold-light),var(--gold-mid)); border:none; border-radius:8px; color:var(--green-dark); font-family:'DM Sans',sans-serif; font-size:.85rem; font-weight:700; cursor:pointer; box-shadow:0 4px 14px rgba(244,197,66,.3); transition:all .2s; flex-shrink:0; }
.btn-nuevo:hover { transform:translateY(-1px); box-shadow:0 6px 20px rgba(244,197,66,.4); }

/* ── Toolbar ─────────────────────────────────────────────────────────────── */
.toolbar { display:flex; align-items:center; gap:1rem; padding:.875rem 1.5rem; background:var(--card-bg); border-bottom:1.5px solid var(--cream-border); flex-wrap:wrap; }
.tabs { display:flex; gap:.375rem; flex-shrink:0; }
.tab-btn { display:flex; align-items:center; gap:.5rem; padding:.45rem .875rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:600; color:#5a7a5a; cursor:pointer; transition:all .18s; }
.tab-btn:hover { background:#111; color:#fff; border-color:#111; }
.tab-active { background:var(--green-mid) !important; color:#fff !important; border-color:var(--green-mid) !important; }
.tab-badge { font-size:.68rem; font-weight:700; padding:.1rem .4rem; border-radius:20px; }
.badge-green { background:rgba(255,255,255,.25); color:#fff; }
.badge-red   { background:rgba(239,68,68,.25); color:#fca5a5; }
.search-wrap { display:flex; align-items:center; gap:.5rem; flex:1; min-width:200px; padding:.5rem .75rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:9px; color:#9ab5a0; }
.search-input { flex:1; border:none; background:none; font-family:'DM Sans',sans-serif; font-size:.875rem; color:#1a2e1a; outline:none; }
.search-input::placeholder { color:#9ab5a0; }
.search-clear { background:none; border:none; color:#9ab5a0; cursor:pointer; font-size:1rem; padding:0; }

/* ── Tabla ───────────────────────────────────────────────────────────────── */
.tabla-section { background:var(--card-bg); border:1.5px solid var(--cream-border); border-radius:0 0 16px 16px; overflow:hidden; box-shadow:var(--shadow-sm); margin:0 1.5rem 1.5rem; }
.tabla-wrap { overflow-x:auto; }
.tabla { width:100%; border-collapse:collapse; font-size:.82rem; }
.tabla thead { background:linear-gradient(135deg,#1a4731,#2d6a4f); }
.tabla thead th { padding:.75rem 1rem; text-align:left; color:rgba(255,255,255,.88); font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.06em; }
.tabla tbody tr { border-bottom:1px solid #f1f5f0; transition:background .15s; }
.tabla tbody tr:last-child { border-bottom:none; }
.tabla tbody tr:hover { background:#fafef8; }
.tabla tbody tr.fila-vencida { background:#fff5f5; }
.tabla tbody tr.fila-vencida:hover { background:#fff0f0; }
.tabla td { padding:.75rem 1rem; vertical-align:middle; color:#334155; }
.td-id     { font-family:monospace; color:#9ab5a0; font-size:.78rem; }
.td-titulo { font-weight:600; color:#1a2e1a; }
.td-sub    { font-size:.72rem; color:#9ab5a0; margin-top:2px; }
.td-nombre { font-weight:500; color:#334155; }
.td-fecha  { font-size:.8rem; color:#64748b; }
.mono      { font-family:monospace; }
.acciones  { display:flex; gap:.35rem; }
.dias-vencido { font-size:.7rem; font-weight:700; color:#dc2626; }
.dias-alerta  { font-size:.7rem; font-weight:600; color:#d97706; }
.dias-ok      { font-size:.7rem; color:#9ab5a0; }
.estado-badge { display:inline-block; padding:.25rem .65rem; border-radius:20px; font-size:.7rem; font-weight:700; white-space:nowrap; }
.badge-vigente    { background:var(--green-pale); color:var(--green-dark); border:1px solid #b8ddc8; }
.badge-por-vencer { background:#fef3c7; color:#92400e; border:1px solid #fcd34d; }
.badge-vencido    { background:#fff0f0; color:#b91c1c; border:1px solid #fca5a5; }
.badge-terminado  { background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; }

/* ── Estados ─────────────────────────────────────────────────────────────── */
.estado-c,.estado-e,.estado-v { display:flex; flex-direction:column; align-items:center; padding:3.5rem 2rem; gap:.75rem; text-align:center; }
.spinner { width:32px; height:32px; border:3px solid var(--green-pale); border-top-color:var(--green-mid); border-radius:50%; animation:spin .7s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }
.estado-c p,.estado-e p { color:#5a7a5a; font-size:.875rem; margin:0; }
.estado-e p { color:#d62828; }
.vacio-ico   { color:#b8ddc8; }
.vacio-titulo{ font-weight:700; color:var(--green-dark); margin:0; }
.btn-retry   { padding:.5rem 1.1rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-size:.82rem; font-weight:700; cursor:pointer; }

/* ── Paginación ──────────────────────────────────────────────────────────── */
.paginacion { display:flex; justify-content:space-between; align-items:center; padding:.875rem 1.25rem; border-top:1.5px solid #eef5f0; font-size:.8rem; color:#5a7a5a; flex-wrap:wrap; gap:.75rem; }
.pag-controles { display:flex; align-items:center; gap:.5rem; }
.pag-btn { padding:.35rem .75rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:7px; font-size:.78rem; font-weight:600; color:var(--green-mid); cursor:pointer; font-family:'DM Sans',sans-serif; transition:all .15s; }
.pag-btn:hover:not(:disabled) { background:#111; color:#fff; border-color:#111; }
.pag-btn:disabled { opacity:.4; cursor:not-allowed; }
.pag-num { padding:.3rem .65rem; border-radius:7px; cursor:pointer; font-size:.8rem; font-weight:500; color:var(--green-mid); transition:all .15s; }
.pag-num:hover { background:#111; color:#fff; }
.pag-num-active { background:var(--green-mid); color:#fff; }
.pag-select { padding:.3rem .55rem; border:1.5px solid var(--cream-border); border-radius:7px; font-size:.8rem; color:var(--green-dark); background:#fff; cursor:pointer; }

/* ── Modales ─────────────────────────────────────────────────────────────── */
.modal-overlay { position:fixed; inset:0; background:transparent; display:flex; align-items:center; justify-content:center; z-index:2000; }
.modal-overlay::before { content:''; position:fixed; inset:0; background:rgba(26,47,26,.55); backdrop-filter:blur(8px); z-index:-1; }
.modal { background:var(--card-bg); border-radius:16px; width:90%; max-width:500px; border:1.5px solid var(--cream-border); box-shadow:0 24px 64px rgba(0,0,0,.2); animation:modalIn .25s cubic-bezier(.22,1,.36,1); position:relative; z-index:1; max-height:90vh; overflow-y:auto; }
.modal-sm { max-width:420px; }
@keyframes modalIn { from { opacity:0; transform:translateY(-14px) scale(.97); } to { opacity:1; transform:translateY(0) scale(1); } }
.modal-header { display:flex; justify-content:space-between; align-items:center; padding:1.1rem 1.375rem .875rem; border-bottom:1.5px solid #eef5f0; position:sticky; top:0; background:var(--card-bg); z-index:1; border-radius:16px 16px 0 0; }
.modal-header h3 { font-family:'Playfair Display',serif; font-size:1.05rem; font-weight:700; color:var(--green-dark); margin:0; }
.modal-close { background:none; border:none; font-size:1.3rem; color:#9ab5a0; cursor:pointer; padding:0; }
.modal-close:hover { color:var(--green-dark); }
.modal-body { padding:1.25rem 1.375rem; display:flex; flex-direction:column; gap:.875rem; }
.modal-footer { display:flex; justify-content:flex-end; gap:.625rem; padding:.875rem 1.375rem; border-top:1.5px solid #eef5f0; position:sticky; bottom:0; background:var(--card-bg); border-radius:0 0 16px 16px; }

.form-field { display:flex; flex-direction:column; gap:5px; }
.form-label { font-size:.72rem; font-weight:700; color:var(--green-dark); text-transform:uppercase; letter-spacing:.07em; }
.req { color:#d62828; }
.form-input { padding:.6rem .75rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.875rem; color:#1a2e1a; outline:none; transition:border-color .2s; box-sizing:border-box; width:100%; }
.form-input:focus { border-color:var(--green-light); }
.form-textarea { resize:vertical; min-height:60px; }
.form-error { padding:.6rem .875rem; background:#fff3f3; border:1px solid #f5c0c0; border-radius:9px; color:#d62828; font-size:.82rem; font-weight:600; }

.sugerencias { background:#fff; border:1.5px solid var(--cream-border); border-radius:10px; box-shadow:var(--shadow-sm); overflow:hidden; margin-top:.3rem; max-height:220px; overflow-y:auto; }
.sug-item { padding:.625rem .875rem; cursor:pointer; border-bottom:1px solid #f5f5f5; transition:background .15s; }
.sug-item:last-child { border-bottom:none; }
.sug-item:hover { background:var(--green-pale); }
.sug-titulo { font-size:.82rem; font-weight:600; color:#1a2e1a; }
.sug-sub    { font-size:.72rem; color:#9ab5a0; margin-top:1px; }
.sug-vacio  { font-size:.78rem; color:#9ab5a0; padding:.5rem .875rem; }
.sug-cargando { font-size:.78rem; color:#9ab5a0; padding:.5rem .875rem; font-style:italic; }

.seleccionado { display:flex; align-items:center; gap:.75rem; padding:.75rem; background:var(--green-pale); border:1px solid #b8ddc8; border-radius:9px; margin-top:.3rem; }
.sel-info { flex:1; min-width:0; }
.sel-titulo { font-size:.82rem; font-weight:600; color:var(--green-dark); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.sel-sub    { font-size:.72rem; color:#5a7a5a; }
.sel-quitar { background:none; border:none; color:#9ab5a0; cursor:pointer; font-size:1.1rem; flex-shrink:0; padding:0; }
.sel-quitar:hover { color:#d62828; }

.resumen-prestamo { display:flex; flex-direction:column; gap:.3rem; padding:.875rem; background:var(--cream); border-radius:10px; }
.rp-row { display:flex; gap:.75rem; font-size:.82rem; }
.rp-lbl { color:#9ab5a0; font-weight:600; min-width:110px; flex-shrink:0; }
.rp-val { color:#1a2e1a; font-weight:500; }

.alerta-multa { display:flex; gap:.625rem; padding:.75rem; background:#fff5f5; border:1px solid #fca5a5; border-radius:9px; align-items:flex-start; }
.alerta-titulo { font-size:.82rem; font-weight:700; color:#7f1d1d; margin:0 0 3px; }
.alerta-desc   { font-size:.78rem; color:#7f1d1d; margin:0; line-height:1.5; opacity:.85; }

.resultado-ok { display:flex; align-items:center; gap:1rem; padding:.875rem; background:var(--green-pale); border-radius:10px; }
.resultado-check { width:36px; height:36px; background:var(--green-mid); border-radius:50%; display:flex; align-items:center; justify-content:center; color:#fff; font-size:1rem; font-weight:700; flex-shrink:0; }
.resultado-ok p { font-size:.82rem; color:var(--green-dark); margin:0; line-height:1.5; }
.multa-generada { padding:.875rem; background:#fff5f5; border:1px solid #fca5a5; border-radius:10px; text-align:center; }
.multa-etiqueta { font-size:.72rem; font-weight:700; color:#7f1d1d; text-transform:uppercase; letter-spacing:.07em; margin:0 0 .25rem; }
.multa-monto    { font-family:'Playfair Display',serif; font-size:1.8rem; font-weight:700; color:#dc2626; line-height:1; margin:0; }
.multa-detalle  { font-size:.72rem; color:#9ab5a0; margin:.25rem 0 0; }

.btn-modal-cancel  { padding:.5rem 1rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:600; color:#5a7a5a; cursor:pointer; }
.btn-modal-cancel:hover { background:#f8fafc; }
.btn-modal-cancel:disabled { opacity:.5; cursor:not-allowed; }
.btn-modal-confirm { padding:.5rem 1.1rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:.4rem; transition:background .2s; }
.btn-modal-confirm:hover:not(:disabled) { background:#111; }
.btn-modal-confirm:disabled { opacity:.5; cursor:not-allowed; }
.spinner-mini { width:12px; height:12px; border:2px solid rgba(255,255,255,.3); border-top-color:#fff; border-radius:50%; animation:spin .6s linear infinite; }

.toast { position:fixed; bottom:2rem; right:2rem; display:flex; align-items:center; gap:.75rem; padding:.75rem 1.1rem; border-radius:10px; font-size:.82rem; font-weight:600; color:#fff; z-index:9999; box-shadow:0 4px 20px rgba(0,0,0,.15); }
.toast-success { background:#16a34a; }
.toast-error   { background:#d62828; }
.toast-close   { background:none; border:none; color:rgba(255,255,255,.75); font-size:1.1rem; cursor:pointer; padding:0; margin-left:auto; }
.toast-in-enter-active,.toast-in-leave-active { transition:all .3s ease; }
.toast-in-enter-from,.toast-in-leave-to { opacity:0; transform:translateX(16px); }
</style>