<template>
  <div class="user-management">

    <!-- ══════════════════════════════════════
         HEADER
    ══════════════════════════════════════ -->
    <header class="page-header">
      <div class="header-inner">
        <div class="header-texto">
          <p class="header-sup">Panel de administración</p>
          <h1 class="header-titulo">Gestión de Usuarios</h1>
          <p class="header-sub">
            {{ authStore.userName }}
            <span class="header-sep">·</span>
            <span class="header-code">{{ authStore.userCode }}</span>
          </p>
        </div>

        <div class="header-acciones">
          <button
            class="btn-toggle-inactivos"
            :class="{ 'btn-toggle-on': showInactiveUsers }"
            @click="toggleShowInactive"
          >
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
            </svg>
            {{ showInactiveUsers ? 'Ocultar inactivos' : 'Mostrar inactivos' }}
          </button>

          <button class="btn-crear" @click="abrirModalCrear">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
            </svg>
            Nuevo Usuario
          </button>
        </div>
      </div>

      <div class="header-stats">
        <div class="hstat">
          <span class="hstat-num">{{ stats.totalActivos }}</span>
          <span class="hstat-lbl">Activos</span>
        </div>
        <div class="hstat">
          <span class="hstat-num">{{ stats.commonUsers }}</span>
          <span class="hstat-lbl">Usuarios comunes</span>
        </div>
        <div class="hstat">
          <span class="hstat-num">{{ stats.adminUsers }}</span>
          <span class="hstat-lbl">Administradores</span>
        </div>
        <div class="hstat hstat-muted" v-if="stats.inactiveUsers > 0">
          <span class="hstat-num">{{ stats.inactiveUsers }}</span>
          <span class="hstat-lbl">Inactivos</span>
        </div>
      </div>
    </header>

    <!-- ══════════════════════════════════════
         TOOLBAR
    ══════════════════════════════════════ -->
    <div class="toolbar">
      <div class="search-wrap">
        <svg class="search-ico" width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input v-model="searchQuery" type="text" placeholder="Buscar por código o nombre..." class="search-input"/>
        <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">×</button>
      </div>

      <select v-model="filters.tipo_usuario_id" class="filter-select">
        <option value="">Todos los tipos</option>
        <option value="1">Usuario Común</option>
        <option value="2">Admin Básico</option>
        <option value="3">Admin Avanzado</option>
      </select>

      <select v-model="sortBy" class="filter-select">
        <option value="nombre">Nombre A-Z</option>
        <option value="codigo">Código A-Z</option>
        <option value="fecha_registro">Más recientes</option>
        <option value="tipo">Tipo</option>
      </select>

      <button class="btn-reset" @click="resetFilters" v-if="hasActiveFilters">
        Limpiar filtros
      </button>
    </div>

    <!-- ══════════════════════════════════════
         TABLA
    ══════════════════════════════════════ -->
    <div class="tabla-section">

      <div v-if="isLoading" class="estado-loading">
        <div class="spinner"></div>
        <p>Cargando usuarios...</p>
      </div>

      <div v-else-if="error" class="estado-error">
        <p>{{ error }}</p>
        <!-- btn-primary viene de buttons.css -->
        <button class="btn-primary" @click="loadUsers">Reintentar</button>
      </div>

      <div v-else class="tabla-wrap">
        <table class="tabla">
          <thead>
            <tr>
              <th style="width:60px">ID</th>
              <th style="width:140px">Código</th>
              <th>Nombre</th>
              <th style="width:150px">Tipo</th>
              <th style="width:100px">Estado</th>
              <th style="width:130px">Registro</th>
              <th style="width:180px">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedUsers" :key="user.id" :class="{ 'fila-inactiva': !user.esta_activo }">
              <td class="td-id">#{{ user.id }}</td>
              <td><span class="td-codigo">{{ user.codigo_universitario }}</span></td>
              <td>
                <div class="td-nombre">{{ user.nombre_completo }}</div>
                <div class="td-relacion">{{ getRelacionNombre(user.relacion_institucional_id) }}</div>
              </td>
              <td>
                <span class="tipo-badge" :class="`tipo-${user.tipo_usuario_id}`">
                  {{ getTipoUsuarioNombre(user.tipo_usuario_id) }}
                </span>
              </td>
              <td>
                <span class="estado-badge" :class="user.esta_activo ? 'estado-activo' : 'estado-inactivo'">
                  {{ user.esta_activo ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="td-fecha">{{ formatFecha(user.fecha_registro) }}</td>
              <td>
                <div class="acciones">
                  <!-- tbl-btn + variantes vienen de buttons.css -->
                  <button v-if="canEditUser(user)" class="tbl-btn tbl-blue" title="Editar usuario" :disabled="isProcessing" @click="abrirModalEditar(user)">
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                    Editar
                  </button>

                  <button v-if="canEditUser(user)" class="tbl-btn tbl-gold" title="Resetear contraseña" :disabled="isProcessing" @click="abrirModalReset(user)">
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
                    </svg>
                    Resetear
                  </button>

                  <button v-if="user.esta_activo && canEditUser(user)" class="tbl-btn tbl-warning" style="padding:.3rem .5rem" title="Desactivar" :disabled="isProcessing" @click="confirmarAccion(user, 'deactivate')">
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                  </button>

                  <button v-else-if="!user.esta_activo" class="tbl-btn tbl-green" style="padding:.3rem .5rem" title="Activar" :disabled="isProcessing" @click="confirmarAccion(user, 'activate')">
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                  </button>

                  <button v-if="!user.esta_activo" class="tbl-btn tbl-danger" style="padding:.3rem .5rem" title="Eliminar permanentemente" :disabled="isProcessing" @click="confirmarAccion(user, 'delete')">
                    <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="filteredUsers.length === 0" class="estado-vacio">
          <svg width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" class="vacio-ico">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          <p class="vacio-titulo">No se encontraron usuarios</p>
          <p class="vacio-desc">Intenta con otros términos o ajusta los filtros</p>
          <button class="btn-outline" @click="resetFilters">Limpiar filtros</button>
        </div>
      </div>

      <div v-if="!isLoading && filteredUsers.length > 0" class="paginacion">
        <span class="pag-info">{{ startItem }}–{{ endItem }} de {{ filteredUsers.length }}</span>
        <div class="pag-controles">
          <button class="pag-btn" :disabled="currentPage === 1" @click="prevPage">← Anterior</button>
          <span v-for="page in visiblePages" :key="page" class="pag-num" :class="{ 'pag-num-active': page === currentPage }" @click="goToPage(page)">{{ page }}</span>
          <button class="pag-btn" :disabled="currentPage === totalPages" @click="nextPage">Siguiente →</button>
        </div>
        <div class="pag-size">
          <label>Mostrar</label>
          <select v-model="itemsPerPage" @change="resetPagination" class="pag-select">
            <option :value="10">10</option>
            <option :value="25">25</option>
            <option :value="50">50</option>
          </select>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════
         MODAL: CREAR USUARIO
    ══════════════════════════════════════ -->
    <div v-if="modalCrear.visible" class="modal-overlay" @click.self="cerrarModalCrear">
      <div class="modal">
        <div class="modal-header">
          <h3>Nuevo Usuario</h3>
          <button class="modal-close" @click="cerrarModalCrear" :disabled="isProcessing">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-field">
              <label class="form-label">Código Universitario <span class="req">*</span></label>
              <input v-model="crearForm.codigo_universitario" type="text" class="form-input" placeholder="U20234567" maxlength="20"/>
            </div>
            <div class="form-field">
              <label class="form-label">Nombre Completo <span class="req">*</span></label>
              <input v-model="crearForm.nombre_completo" type="text" class="form-input" placeholder="Juan Pérez García" maxlength="255"/>
            </div>
            <div class="form-field">
              <label class="form-label">Contraseña inicial <span class="req">*</span></label>
              <input v-model="crearForm.clave_acceso" type="password" class="form-input" placeholder="Mínimo 6 caracteres" minlength="6"/>
              <p class="form-hint">El usuario deberá cambiarla al ingresar</p>
            </div>
            <div class="form-field">
              <label class="form-label">Tipo de Usuario <span class="req">*</span></label>
              <select v-model="crearForm.tipo_usuario_id" class="form-select">
                <option v-for="t in userTypes" :key="t.id" :value="t.id" :disabled="t.id === 4">{{ t.nombre }}</option>
              </select>
            </div>
            <div class="form-field">
              <label class="form-label">Relación Institucional <span class="req">*</span></label>
              <select v-model="crearForm.relacion_institucional_id" class="form-select">
                <option v-for="r in institutionalRelations" :key="r.id" :value="r.id">{{ r.nombre }}</option>
              </select>
            </div>
          </div>
          <div v-if="modalCrear.error" class="form-error">{{ modalCrear.error }}</div>
        </div>
        <div class="modal-footer">
          <!-- btn-modal-cancel y btn-modal-confirm vienen de buttons.css -->
          <button class="btn-modal-cancel" @click="cerrarModalCrear" :disabled="isProcessing">Cancelar</button>
          <button class="btn-modal-confirm" @click="guardarNuevoUsuario" :disabled="isProcessing">
            <span v-if="isProcessing" class="spinner-mini"></span>
            {{ isProcessing ? 'Creando...' : 'Crear Usuario' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════
         MODAL: EDITAR USUARIO
    ══════════════════════════════════════ -->
    <div v-if="modalEditar.visible" class="modal-overlay" @click.self="cerrarModalEditar">
      <div class="modal">
        <div class="modal-header">
          <h3>Editar Usuario</h3>
          <button class="modal-close" @click="cerrarModalEditar" :disabled="isProcessing">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-field">
              <label class="form-label">Código Universitario</label>
              <input :value="editForm.codigo_universitario" type="text" class="form-input" disabled/>
              <p class="form-hint">No modificable</p>
            </div>
            <div class="form-field">
              <label class="form-label">Nombre Completo <span class="req">*</span></label>
              <input v-model="editForm.nombre_completo" type="text" class="form-input" placeholder="Nombre completo"/>
            </div>
            <div class="form-field">
              <label class="form-label">Tipo de Usuario <span class="req">*</span></label>
              <select v-model="editForm.tipo_usuario_id" class="form-select">
                <option v-for="t in userTypes" :key="t.id" :value="t.id" :disabled="t.id === 4">{{ t.nombre }}</option>
              </select>
            </div>
            <div class="form-field">
              <label class="form-label">Relación Institucional</label>
              <select v-model="editForm.relacion_institucional_id" class="form-select">
                <option v-for="r in institutionalRelations" :key="r.id" :value="r.id">{{ r.nombre }}</option>
              </select>
            </div>
            <div class="form-field form-field-full">
              <label class="form-label">Estado</label>
              <div class="estado-toggle">
                <button class="toggle-opt" :class="{ 'toggle-opt-on': editForm.esta_activo }" @click="editForm.esta_activo = true">Activo</button>
                <button class="toggle-opt" :class="{ 'toggle-opt-off': !editForm.esta_activo }" @click="editForm.esta_activo = false">Inactivo</button>
              </div>
            </div>
          </div>
          <div v-if="modalEditar.error" class="form-error">{{ modalEditar.error }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="cerrarModalEditar" :disabled="isProcessing">Cancelar</button>
          <button class="btn-modal-confirm" @click="guardarEdicion" :disabled="isProcessing">
            <span v-if="isProcessing" class="spinner-mini"></span>
            {{ isProcessing ? 'Guardando...' : 'Guardar Cambios' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════
         MODAL: RESET PASSWORD
    ══════════════════════════════════════ -->
    <div v-if="modalReset.visible" class="modal-overlay" @click.self="cerrarModalReset">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>Resetear Contraseña</h3>
          <button class="modal-close" @click="cerrarModalReset" :disabled="isProcessing">×</button>
        </div>
        <div class="modal-body">
          <div class="reset-info">
            <div class="reset-avatar">{{ getUserInitials(modalReset.usuario?.nombre_completo) }}</div>
            <div>
              <p class="reset-nombre">{{ modalReset.usuario?.nombre_completo }}</p>
              <p class="reset-codigo">{{ modalReset.usuario?.codigo_universitario }}</p>
            </div>
          </div>
          <div class="reset-aviso">
            <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <p>La contraseña se reseteará a <strong>biblioteca2025</strong>. El usuario deberá cambiarla al iniciar sesión.</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="cerrarModalReset" :disabled="isProcessing">Cancelar</button>
          <!-- btn-warning viene de buttons.css -->
          <button class="btn-warning" @click="ejecutarReset" :disabled="isProcessing">
            <span v-if="isProcessing" class="spinner-mini"></span>
            {{ isProcessing ? 'Reseteando...' : 'Sí, resetear contraseña' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════
         MODAL: CONFIRMAR ACCIÓN
    ══════════════════════════════════════ -->
    <div v-if="modalConfirm.visible" class="modal-overlay" @click.self="cerrarModalConfirm">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>{{ modalConfirm.titulo }}</h3>
          <button class="modal-close" @click="cerrarModalConfirm" :disabled="isProcessing">×</button>
        </div>
        <div class="modal-body">
          <p class="confirm-msg">{{ modalConfirm.mensaje }}</p>
          <div v-if="modalConfirm.usuario" class="confirm-user">
            <strong>{{ modalConfirm.usuario.nombre_completo }}</strong>
            <span>{{ modalConfirm.usuario.codigo_universitario }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" @click="cerrarModalConfirm" :disabled="isProcessing">Cancelar</button>
          <!-- btn-modal-delete y btn-modal-confirm vienen de buttons.css -->
          <button
            :class="modalConfirm.accion === 'delete' ? 'btn-modal-delete' : 'btn-modal-confirm'"
            @click="ejecutarAccion"
            :disabled="isProcessing"
          >
            <span v-if="isProcessing" class="spinner-mini"></span>
            {{ isProcessing ? 'Procesando...' : modalConfirm.textoBtn }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════
         TOAST
    ══════════════════════════════════════ -->
    <transition name="toast-in">
      <div v-if="toast.visible" class="toast" :class="toast.tipo">
        <span>{{ toast.mensaje }}</span>
        <button class="toast-close" @click="toast.visible = false">×</button>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { userService } from '@/services/users'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

// ── Import centralizado de botones ─────────────────────────────────────────
import '@/styles/buttons.css'

const authStore = useAuthStore()

if (authStore.tipoUsuarioId !== 4) {
  useRouter().push('/')
}

// ── State ──────────────────────────────────────────────────────────────────
const users             = ref([])
const isLoading         = ref(false)
const error             = ref(null)
const isProcessing      = ref(false)
const showInactiveUsers = ref(false)
const currentPage       = ref(1)
const itemsPerPage      = ref(10)
const searchQuery       = ref('')
const sortBy            = ref('')
const filters           = ref({ tipo_usuario_id: '' })

// ── Modales ────────────────────────────────────────────────────────────────
const modalCrear   = ref({ visible: false, error: '' })
const modalEditar  = ref({ visible: false, error: '' })
const modalReset   = ref({ visible: false, usuario: null })
const modalConfirm = ref({ visible: false, titulo: '', mensaje: '', textoBtn: '', accion: '', usuario: null })

// ── Formularios ────────────────────────────────────────────────────────────
const crearForm = ref({ codigo_universitario: '', nombre_completo: '', clave_acceso: '', tipo_usuario_id: 1, relacion_institucional_id: 1 })
const editForm  = ref({ id: null, codigo_universitario: '', nombre_completo: '', tipo_usuario_id: 1, relacion_institucional_id: 1, esta_activo: true })

// ── Toast ──────────────────────────────────────────────────────────────────
const toast = ref({ visible: false, mensaje: '', tipo: '' })
const mostrarToast = (mensaje, tipo = 'toast-success') => {
  toast.value = { visible: true, mensaje, tipo }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

// ── Catálogos ──────────────────────────────────────────────────────────────
const userTypes              = computed(() => userService.getUserTypes())
const institutionalRelations = computed(() => userService.getInstitutionalRelations())

// ── Computed ───────────────────────────────────────────────────────────────
const filteredUsers = computed(() => {
  let result = userService.filterNonSuperAdmins(users.value)

  if (!showInactiveUsers.value) result = result.filter(u => u.esta_activo)
  if (filters.value.tipo_usuario_id) result = result.filter(u => u.tipo_usuario_id === parseInt(filters.value.tipo_usuario_id))

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    result = result.filter(u =>
      u.codigo_universitario?.toLowerCase().includes(q) ||
      u.nombre_completo?.toLowerCase().includes(q)
    )
  }

  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'nombre':         return a.nombre_completo?.localeCompare(b.nombre_completo)
      case 'codigo':         return a.codigo_universitario?.localeCompare(b.codigo_universitario)
      case 'fecha_registro': return new Date(b.fecha_registro) - new Date(a.fecha_registro)
      case 'tipo':           return a.tipo_usuario_id - b.tipo_usuario_id
      default:               return a.id - b.id
    }
  })
  return result
})

const stats = computed(() => {
  const all = userService.filterNonSuperAdmins(users.value)
  return {
    totalActivos:  all.filter(u => u.esta_activo).length,
    commonUsers:   all.filter(u => u.tipo_usuario_id === 1).length,
    adminUsers:    all.filter(u => u.tipo_usuario_id >= 2 && u.tipo_usuario_id <= 3).length,
    inactiveUsers: all.filter(u => !u.esta_activo).length
  }
})

const totalPages     = computed(() => Math.ceil(filteredUsers.value.length / itemsPerPage.value) || 1)
const startItem      = computed(() => (currentPage.value - 1) * itemsPerPage.value + 1)
const endItem        = computed(() => Math.min(currentPage.value * itemsPerPage.value, filteredUsers.value.length))
const paginatedUsers = computed(() => {
  const s = (currentPage.value - 1) * itemsPerPage.value
  return filteredUsers.value.slice(s, s + itemsPerPage.value)
})
const visiblePages = computed(() => {
  const max = 5, total = totalPages.value
  if (total <= max) return Array.from({ length: total }, (_, i) => i + 1)
  let start = Math.max(1, currentPage.value - 2)
  const end = Math.min(total, start + max - 1)
  if (end - start + 1 < max) start = end - max + 1
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})
const hasActiveFilters = computed(() => searchQuery.value.trim() !== '' || filters.value.tipo_usuario_id !== '')

// ── Carga ──────────────────────────────────────────────────────────────────
const loadUsers = async () => {
  isLoading.value = true; error.value = null
  try {
    const response = await userService.getUsers({ pagina: 1, por_pagina: 100, activos_only: false })
    users.value = (Array.isArray(response) ? response : (response.usuarios ?? [])).sort((a, b) => a.id - b.id)
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

// ── Modal crear ────────────────────────────────────────────────────────────
const abrirModalCrear = () => {
  crearForm.value = { codigo_universitario: '', nombre_completo: '', clave_acceso: '', tipo_usuario_id: 1, relacion_institucional_id: 1 }
  modalCrear.value = { visible: true, error: '' }
}
const cerrarModalCrear = () => { if (!isProcessing.value) modalCrear.value.visible = false }

const guardarNuevoUsuario = async () => {
  const { codigo_universitario, nombre_completo, clave_acceso, tipo_usuario_id, relacion_institucional_id } = crearForm.value
  if (!codigo_universitario || !nombre_completo || !clave_acceso) { modalCrear.value.error = 'Completa todos los campos obligatorios'; return }
  if (clave_acceso.length < 6) { modalCrear.value.error = 'La contraseña debe tener al menos 6 caracteres'; return }
  isProcessing.value = true
  try {
    const nuevo = await userService.createUser({ codigo_universitario, nombre_completo, clave_acceso, tipo_usuario_id, relacion_institucional_id })
    users.value.unshift(nuevo)
    cerrarModalCrear()
    modalCrear.value.visible = false
    mostrarToast(`Usuario ${nombre_completo} creado correctamente`)
  } 
  catch (err) {
    modalCrear.value.error = err.message || 'Error al crear el usuario'
  } finally { isProcessing.value = false }
}

// ── Modal editar ───────────────────────────────────────────────────────────
const abrirModalEditar = (user) => {
  editForm.value = { id: user.id, codigo_universitario: user.codigo_universitario, nombre_completo: user.nombre_completo, tipo_usuario_id: user.tipo_usuario_id, relacion_institucional_id: user.relacion_institucional_id, esta_activo: user.esta_activo }
  modalEditar.value = { visible: true, error: '' }
}
const cerrarModalEditar = () => { if (!isProcessing.value) modalEditar.value.visible = false }

const guardarEdicion = async () => {
  if (!editForm.value.nombre_completo.trim()) {
    modalEditar.value.error = 'El nombre es obligatorio'
    return
  }
  isProcessing.value = true
  try {
    await userService.updateUser(editForm.value.id, {
      nombre_completo:           editForm.value.nombre_completo,
      tipo_usuario_id:           editForm.value.tipo_usuario_id,
      relacion_institucional_id: editForm.value.relacion_institucional_id,
      esta_activo:               editForm.value.esta_activo
    })
    modalEditar.value.visible = false
    await loadUsers()
    mostrarToast('Usuario actualizado correctamente')
  } catch (err) {
    modalEditar.value.error = err.message || 'Error al actualizar'
  } finally {
    isProcessing.value = false
  }
}

// ── Modal reset ────────────────────────────────────────────────────────────
const abrirModalReset = (user) => { modalReset.value = { visible: true, usuario: user } }

const cerrarModalReset = () => { if (!isProcessing.value) modalReset.value.visible = false }

const ejecutarReset = async () => {
  if (!modalReset.value.usuario) return
  isProcessing.value = true
  try {
    await api.patch(`/api/usuarios/${modalReset.value.usuario.id}/reset-password`)
    cerrarModalReset()
    mostrarToast(`Contraseña de ${modalReset.value.usuario.nombre_completo} reseteada a 'biblioteca2025'`)
  } catch (err) {
    mostrarToast(err.response?.data?.detail || 'Error al resetear contraseña', 'toast-error')
  } finally { isProcessing.value = false }
}

// ── Modal confirmar ────────────────────────────────────────────────────────
const confirmarAccion = (user, accion) => {
  const config = {
    activate:   { titulo: 'Activar Usuario',   mensaje: `¿Activar a ${user.nombre_completo}?`,    textoBtn: 'Sí, activar' },
    deactivate: { titulo: 'Desactivar Usuario', mensaje: `¿Desactivar a ${user.nombre_completo}?`, textoBtn: 'Sí, desactivar' },
    delete:     { titulo: 'Eliminar Usuario',   mensaje: `¿Eliminar permanentemente a ${user.nombre_completo}? Esta acción no se puede deshacer.`, textoBtn: 'Sí, eliminar' }
  }
  modalConfirm.value = { visible: true, ...config[accion], accion, usuario: user }
}

const cerrarModalConfirm = () => {
  if (!isProcessing.value) modalConfirm.value.visible = false
}

const ejecutarAccion = async () => {
  const { accion, usuario } = modalConfirm.value
  if (!usuario) return
  isProcessing.value = true
  try {
    switch (accion) {
      case 'activate':
        await userService.reactivateUser(usuario.id)
        const ua = users.value.find(u => u.id === usuario.id)
        if (ua) ua.esta_activo = true
        mostrarToast(`${usuario.nombre_completo} activado`)
        break
      case 'deactivate':
        await userService.deactivateUser(usuario.id)
        const ud = users.value.find(u => u.id === usuario.id)
        if (ud) ud.esta_activo = false
        mostrarToast(`${usuario.nombre_completo} desactivado`)
        break
      case 'delete':
        await userService.deleteUser(usuario.id)
        users.value = users.value.filter(u => u.id !== usuario.id)
        mostrarToast(`${usuario.nombre_completo} eliminado`)
        break
    }
    modalConfirm.value.visible = false  // ← cierra directo
  } catch (err) {
    mostrarToast(err.message || 'Error al ejecutar la acción', 'toast-error')
  } finally {
    isProcessing.value = false
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
const canEditUser          = (user) => userService.canEditUser(user)
const getTipoUsuarioNombre = (id)   => userService.getTipoUsuarioNombre(id)
const formatFecha          = (f)    => userService.formatFecha(f)
const getRelacionNombre    = (id)   => { const rel = institutionalRelations.value.find(r => r.id === id); return rel?.nombre || '—' }
const getUserInitials      = (name) => { if (!name) return 'US'; return name.split(' ').map(w => w[0]).join('').toUpperCase().substring(0, 2) }

// ── Paginación ─────────────────────────────────────────────────────────────
const prevPage        = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage        = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const goToPage        = (p) => { if (p >= 1 && p <= totalPages.value) currentPage.value = p }
const resetPagination = () => { currentPage.value = 1 }
const resetFilters    = () => { searchQuery.value = ''; filters.value.tipo_usuario_id = ''; currentPage.value = 1 }
const toggleShowInactive = () => { showInactiveUsers.value = !showInactiveUsers.value; currentPage.value = 1 }

watch([searchQuery, filters, sortBy, showInactiveUsers], () => { currentPage.value = 1 })
onMounted(loadUsers)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

/*
 * NOTA: Los estilos de botones vienen de src/styles/buttons.css
 * importado con: import '@/styles/buttons.css'
 *
 * Clases usadas de buttons.css en esta vista:
 *   .btn-primary      → reintentar error
 *   .btn-outline      → limpiar filtros (vacío)
 *   .btn-warning      → resetear contraseña
 *   .btn-modal-cancel → cancelar en todos los modales
 *   .btn-modal-confirm→ confirmar en crear/editar
 *   .btn-modal-delete → confirmar en eliminar
 *   .tbl-btn          → base de botones de tabla
 *   .tbl-green        → editar / activar
 *   .tbl-gold         → resetear / desactivar
 *   .tbl-red          → eliminar
 *   .spinner-mini     → spinner en botones
 */

:root {
  --green-dark:   #1a4731;
  --green-mid:    #2d6a4f;
  --green-light:  #52b788;
  --green-pale:   #d8f3dc;
  --gold-mid:     #c9900c;
  --gold-light:   #f4c542;
  --gold-pale:    #fef9e7;
  --cream:        #f5f0e8;
  --cream-border: #d4e8da;
  --card-bg:      #fffef9;
  --shadow-sm:    0 2px 12px rgba(26,47,26,.08);
}

.user-management {
  font-family: 'DM Sans', sans-serif; min-height: 100vh;
  background:
    radial-gradient(ellipse 70% 40% at 5% 0%, rgba(82,183,136,.08) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 90% 100%, rgba(201,144,12,.07) 0%, transparent 50%),
    var(--cream);
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.page-header { background: linear-gradient(135deg, #1a4731 0%, #2d6a4f 60%, #3a7d5e 100%); padding: 1.75rem 2rem 1.25rem; position: relative; overflow: hidden; }
.page-header::before { content: ''; position: absolute; inset: 0; pointer-events: none; background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E"); }
.header-inner  { display: flex; justify-content: space-between; align-items: flex-start; gap: 1.5rem; flex-wrap: wrap; position: relative; }
.header-sup    { font-size: .72rem; font-weight: 600; color: rgba(255,255,255,.5); text-transform: uppercase; letter-spacing: .1em; margin-bottom: .2rem; }
.header-titulo { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: #fff; margin-bottom: .3rem; }
.header-sub    { font-size: .8rem; color: rgba(255,255,255,.65); display: flex; align-items: center; gap: .4rem; }
.header-sep    { color: rgba(255,255,255,.3); }
.header-code   { font-family: monospace; font-size: .75rem; }
.header-acciones { display: flex; gap: .75rem; align-items: center; flex-shrink: 0; }

/* Botones del header — específicos de esta vista */
.btn-toggle-inactivos {
  display: flex; align-items: center; gap: .4rem; padding: .5rem 1rem;
  background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.15);
  border-radius: 8px; color: rgba(255,255,255,.75);
  font-family: 'DM Sans', sans-serif; font-size: .8rem; font-weight: 500;
  cursor: pointer; transition: all .2s;
}
.btn-toggle-inactivos:hover, .btn-toggle-on { background: rgba(255,255,255,.18); color: #fff; }

.btn-crear {
  display: flex; align-items: center; gap: .4rem; padding: .5rem 1.1rem;
  background: linear-gradient(135deg, var(--gold-light), var(--gold-mid));
  border: none; border-radius: 8px; color: var(--green-dark);
  font-family: 'DM Sans', sans-serif; font-size: .82rem; font-weight: 700;
  cursor: pointer; box-shadow: 0 4px 14px rgba(244,197,66,.3); transition: all .2s;
}
.btn-crear:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(244,197,66,.4); }

.header-stats { display: flex; gap: .75rem; margin-top: 1.25rem; position: relative; flex-wrap: wrap; }
.hstat {
  display: flex; flex-direction: column; align-items: center;
  background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.1);
  border-radius: 9px; padding: .45rem .875rem; min-width: 80px;
}
.hstat-muted { opacity: .65; }
.hstat-num { font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: #fff; line-height: 1; }
.hstat-lbl { font-size: .64rem; color: rgba(255,255,255,.55); text-transform: uppercase; letter-spacing: .07em; margin-top: 2px; white-space: nowrap; }

/* ── Toolbar ─────────────────────────────────────────────────────────────── */
.toolbar { display: flex; align-items: center; gap: .75rem; padding: 1rem 1.5rem; background: var(--card-bg); border-bottom: 1.5px solid var(--cream-border); flex-wrap: wrap; }
.search-wrap { display: flex; align-items: center; gap: .5rem; flex: 1; min-width: 220px; padding: .5rem .75rem; background: var(--cream); border: 1.5px solid var(--cream-border); border-radius: 9px; color: #9ab5a0; }
.search-ico { flex-shrink: 0; }
.search-input { flex: 1; border: none; background: none; font-family: 'DM Sans', sans-serif; font-size: .875rem; color: #1a2e1a; outline: none; }
.search-input::placeholder { color: #9ab5a0; }
.search-clear { background: none; border: none; color: #9ab5a0; cursor: pointer; font-size: 1rem; padding: 0; line-height: 1; }
.search-clear:hover { color: var(--green-dark); }
.filter-select { padding: .5rem .75rem; background: var(--cream); border: 1.5px solid var(--cream-border); border-radius: 9px; font-family: 'DM Sans', sans-serif; font-size: .82rem; color: #3d5a3d; outline: none; cursor: pointer; }
.filter-select:focus { border-color: var(--green-light); }
.btn-reset { padding: .5rem .875rem; background: none; border: 1.5px solid var(--cream-border); border-radius: 9px; font-family: 'DM Sans', sans-serif; font-size: .8rem; color: #5a7a5a; cursor: pointer; white-space: nowrap; transition: all .18s; }
.btn-reset:hover { background: #111; color: #fff; border-color: #111; }

/* ── Tabla ───────────────────────────────────────────────────────────────── */
.tabla-section { background: var(--card-bg); border: 1.5px solid var(--cream-border); border-radius: 0 0 16px 16px; overflow: hidden; box-shadow: var(--shadow-sm); margin: 0 1.5rem 1.5rem; }
.tabla-wrap { overflow-x: auto; }
.tabla { width: 100%; border-collapse: collapse; font-size: .82rem; }
.tabla thead { background: linear-gradient(135deg, #1a4731, #2d6a4f); }
.tabla thead th { padding: .75rem 1rem; text-align: left; color: rgba(255,255,255,.88); font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; }
.tabla tbody tr { border-bottom: 1px solid #f1f5f0; transition: background .15s; }
.tabla tbody tr:last-child { border-bottom: none; }
.tabla tbody tr:hover { background: #fafef8; }
.tabla tbody tr.fila-inactiva { background: #fff8f8; opacity: .8; }
.tabla tbody tr.fila-inactiva:hover { background: #fff0f0; }
.tabla td { padding: .75rem 1rem; vertical-align: middle; color: #334155; }
.td-id      { font-family: monospace; color: #9ab5a0; font-size: .78rem; }
.td-codigo  { font-family: monospace; font-weight: 700; color: var(--green-dark); font-size: .82rem; }
.td-nombre  { font-weight: 600; color: #1a2e1a; }
.td-relacion{ font-size: .72rem; color: #9ab5a0; margin-top: 2px; }
.td-fecha   { font-size: .78rem; color: #64748b; }

.tipo-badge { display: inline-block; padding: .2rem .6rem; border-radius: 20px; font-size: .7rem; font-weight: 700; white-space: nowrap; }
.tipo-1 { background: #e3f2fd; color: #1565c0; }
.tipo-2 { background: var(--gold-pale); color: var(--gold-mid); border: 1px solid #fde68a; }
.tipo-3 { background: var(--green-pale); color: var(--green-dark); border: 1px solid #b8ddc8; }
.tipo-4 { background: #f3e5f5; color: #7b1fa2; }

.estado-badge { display: inline-block; padding: .2rem .55rem; border-radius: 20px; font-size: .7rem; font-weight: 700; }
.estado-activo   { background: var(--green-pale); color: var(--green-dark); border: 1px solid #b8ddc8; }
.estado-inactivo { background: #fff0f0; color: #b91c1c; border: 1px solid #fca5a5; }

.acciones { display: flex; align-items: center; gap: .35rem; flex-wrap: wrap; }

/* ── Estados ─────────────────────────────────────────────────────────────── */
.estado-loading, .estado-error, .estado-vacio { display: flex; flex-direction: column; align-items: center; padding: 3.5rem 2rem; gap: .75rem; text-align: center; }
.spinner { width: 36px; height: 36px; border: 3px solid var(--green-pale); border-top-color: var(--green-mid); border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.estado-loading p { color: #5a7a5a; font-size: .875rem; }
.estado-error p   { color: #d62828; font-size: .875rem; }
.vacio-ico    { color: #b8ddc8; }
.vacio-titulo { font-weight: 700; color: var(--green-dark); margin: 0; }
.vacio-desc   { font-size: .82rem; color: #5a7a5a; margin: 0; }

/* ── Paginación ──────────────────────────────────────────────────────────── */
.paginacion { display: flex; justify-content: space-between; align-items: center; padding: .875rem 1.25rem; border-top: 1.5px solid #eef5f0; font-size: .8rem; color: #5a7a5a; flex-wrap: wrap; gap: .75rem; }
.pag-controles { display: flex; align-items: center; gap: .5rem; }
.pag-btn { padding: .35rem .75rem; background: #fff; border: 1.5px solid var(--cream-border); border-radius: 7px; font-size: .78rem; font-weight: 600; color: var(--green-mid); cursor: pointer; font-family: 'DM Sans', sans-serif; transition: all .15s; }
.pag-btn:hover:not(:disabled) { background: #111; color: #fff; border-color: #111; }
.pag-btn:disabled { opacity: .4; cursor: not-allowed; }
.pag-num { padding: .3rem .65rem; border-radius: 7px; cursor: pointer; font-size: .8rem; font-weight: 500; color: var(--green-mid); transition: all .15s; }
.pag-num:hover      { background: #111; color: #fff; }
.pag-num-active     { background: var(--green-mid); color: #fff; }
.pag-size { display: flex; align-items: center; gap: .5rem; }
.pag-select { padding: .3rem .55rem; border: 1.5px solid var(--cream-border); border-radius: 7px; font-size: .8rem; color: var(--green-dark); background: #fff; cursor: pointer; }

/* ── Modales ─────────────────────────────────────────────────────────────── */
.modal-overlay { position: fixed; inset: 0; background: rgba(26,47,26,.5); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 2000; }
.modal { background: var(--card-bg); border-radius: 16px; width: 90%; max-width: 540px; border: 1.5px solid var(--cream-border); box-shadow: 0 24px 64px rgba(0,0,0,.2); animation: modalIn .25s cubic-bezier(.22,1,.36,1); max-height: 90vh; overflow-y: auto; }
.modal-sm { max-width: 420px; }
@keyframes modalIn { from { opacity: 0; transform: translateY(-14px) scale(.97); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.1rem 1.375rem .875rem; border-bottom: 1.5px solid #eef5f0; position: sticky; top: 0; background: var(--card-bg); z-index: 1; border-radius: 16px 16px 0 0; }
.modal-header h3 { font-family: 'Playfair Display', serif; font-size: 1.05rem; font-weight: 700; color: var(--green-dark); margin: 0; }
.modal-close { background: none; border: none; font-size: 1.3rem; color: #9ab5a0; cursor: pointer; padding: 0; line-height: 1; transition: color .15s; }
.modal-close:hover { color: var(--green-dark); }
.modal-body { padding: 1.25rem 1.375rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: .625rem; padding: .875rem 1.375rem; border-top: 1.5px solid #eef5f0; position: sticky; bottom: 0; background: var(--card-bg); border-radius: 0 0 16px 16px; }

/* Formulario */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-field { display: flex; flex-direction: column; gap: 5px; }
.form-field-full { grid-column: 1 / -1; }
.form-label { font-size: .72rem; font-weight: 700; color: var(--green-dark); text-transform: uppercase; letter-spacing: .07em; }
.req { color: #d62828; }
.form-input, .form-select { padding: .6rem .75rem; background: #fff; border: 1.5px solid var(--cream-border); border-radius: 9px; font-family: 'DM Sans', sans-serif; font-size: .875rem; color: #1a2e1a; outline: none; transition: border-color .2s; box-sizing: border-box; width: 100%; }
.form-input::placeholder { color: #aabcaa; }
.form-input:focus, .form-select:focus { border-color: var(--green-light); }
.form-input:disabled { background: var(--cream); color: #9ab5a0; cursor: not-allowed; }
.form-hint  { font-size: .7rem; color: #9ab5a0; margin: 0; }
.form-error { margin-top: .75rem; padding: .6rem .875rem; background: #fff3f3; border: 1px solid #f5c0c0; border-radius: 9px; color: #d62828; font-size: .82rem; font-weight: 600; }

/* Toggle estado */
.estado-toggle { display: flex; gap: .5rem; }
.toggle-opt { flex: 1; padding: .5rem; background: #fff; border: 1.5px solid var(--cream-border); border-radius: 9px; font-family: 'DM Sans', sans-serif; font-size: .82rem; font-weight: 600; color: #5a7a5a; cursor: pointer; transition: all .2s; }
.toggle-opt-on  { background: var(--green-pale); color: var(--green-dark); border-color: #b8ddc8; }
.toggle-opt-off { background: #fff0f0; color: #b91c1c; border-color: #fca5a5; }

/* Reset modal */
.reset-info { display: flex; align-items: center; gap: .875rem; padding: .875rem; background: var(--cream); border-radius: 10px; margin-bottom: 1rem; }
.reset-avatar { width: 42px; height: 42px; background: linear-gradient(135deg, var(--green-light), var(--green-mid)); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .9rem; color: #fff; flex-shrink: 0; }
.reset-nombre { font-weight: 700; font-size: .9rem; color: var(--green-dark); margin: 0 0 2px; }
.reset-codigo { font-size: .75rem; color: #9ab5a0; margin: 0; font-family: monospace; }
.reset-aviso  { display: flex; align-items: flex-start; gap: .625rem; padding: .75rem; background: var(--gold-pale); border: 1px solid #fde68a; border-radius: 9px; font-size: .82rem; color: #7a5200; }
.reset-aviso p { margin: 0; line-height: 1.5; }

/* Confirm modal */
.confirm-msg  { font-size: .875rem; color: #334155; margin-bottom: .75rem; }
.confirm-user { display: flex; flex-direction: column; gap: 2px; padding: .75rem; background: var(--cream); border-radius: 9px; border-left: 3px solid var(--green-light); font-size: .82rem; }
.confirm-user strong { color: var(--green-dark); }
.confirm-user span   { color: #9ab5a0; font-family: monospace; }

/* ── Toast ───────────────────────────────────────────────────────────────── */
.toast { position: fixed; bottom: 2rem; right: 2rem; display: flex; align-items: center; gap: .75rem; padding: .75rem 1.1rem; border-radius: 10px; font-size: .82rem; font-weight: 600; color: #fff; z-index: 9999; box-shadow: 0 4px 20px rgba(0,0,0,.15); }
.toast-success { background: #16a34a; }
.toast-error   { background: #d62828; }
.toast-close   { background: none; border: none; color: rgba(255,255,255,.75); font-size: 1.1rem; cursor: pointer; padding: 0; line-height: 1; }
.toast-close:hover { color: #fff; }
.toast-in-enter-active, .toast-in-leave-active { transition: all .3s ease; }
.toast-in-enter-from, .toast-in-leave-to { opacity: 0; transform: translateX(16px); }
</style>