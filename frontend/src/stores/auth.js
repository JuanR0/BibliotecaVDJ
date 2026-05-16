// stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {

  const isInitialized = ref(false)

  // ── State ──────────────────────────────────────────────────────────────────
  const user    = ref(JSON.parse(localStorage.getItem('user'))    || null)
  const token   = ref(localStorage.getItem('token')               || null)
  const permisos = ref(JSON.parse(localStorage.getItem('permisos')) || {})
  const isLoading = ref(false)
  const tieneMultasPendientes = ref(false)

  // ── Auth básica ────────────────────────────────────────────────────────────
  const isAuthenticated = computed(() => !!token.value)
  const userName  = computed(() => user.value?.nombre_completo || 'Usuario')
  const userCode  = computed(() => user.value?.codigo_universitario || '')
  const userId    = computed(() => user.value?.id || user.value?.usuario_id || null)

  // ── Tipo de usuario (rol) ──────────────────────────────────────────────────
  // IMPORTANTE: tipoUsuarioId es el ROL (1,2,3,4) — NO el ID del usuario
  const tipoUsuarioId = computed(() => {
    if (user.value?.tipo_usuario_id)    return user.value.tipo_usuario_id
    if (permisos.value?.tipo_usuario_id) return permisos.value.tipo_usuario_id
    return 1
  })

  // ── Roles ──────────────────────────────────────────────────────────────────
  const esEstudiante    = computed(() => tipoUsuarioId.value === 1)
  const esAdminBasico   = computed(() => tipoUsuarioId.value === 2)
  const esAdminAvanzado = computed(() => tipoUsuarioId.value === 3)
  const esSuperAdmin    = computed(() => tipoUsuarioId.value === 4)
  const esCualquierAdmin = computed(() => tipoUsuarioId.value >= 2)
  // Alias para compatibilidad
  const esUsuarioComun  = esEstudiante

  // ── Permisos por nivel ─────────────────────────────────────────────────────
  // Nivel 1+ (todos los autenticados)
  const puedeConsultar   = computed(() => tipoUsuarioId.value >= 1)
  const puedeVerMultas   = computed(() => tipoUsuarioId.value >= 1)

  // Nivel 2+ (bibliotecarios)
  const puedePrestar          = computed(() => tipoUsuarioId.value >= 2)
  const puedeGestionarMultas  = computed(() => tipoUsuarioId.value >= 2)
  const puedeLiquidarMultas   = computed(() => tipoUsuarioId.value >= 2)
  const puedeCrearMultas      = computed(() => tipoUsuarioId.value >= 2)

  // Nivel 3+ (admin avanzado — gestión de recursos)
  const puedeGestionarRecursos = computed(() => tipoUsuarioId.value >= 3)

  // Libros
  const puedeVerLibrosRetirados = computed(() => tipoUsuarioId.value >= 2)
  const puedeEditarLibros       = computed(() => tipoUsuarioId.value >= 3)
  const puedeEliminarLibros     = computed(() => tipoUsuarioId.value >= 3)
  const puedeReactivarLibros    = computed(() => tipoUsuarioId.value >= 3)
  const puedeCrearLibros        = computed(() => tipoUsuarioId.value >= 3)

  // Mobiliario
  const puedeVerMobiliario       = computed(() => tipoUsuarioId.value >= 3)
  const puedeCrearMobiliario     = computed(() => tipoUsuarioId.value >= 3)
  const puedeEditarMobiliario    = computed(() => tipoUsuarioId.value >= 3)
  const puedeEliminarMobiliario  = computed(() => tipoUsuarioId.value >= 3)
  const puedeReactivarMobiliario = computed(() => tipoUsuarioId.value >= 3)
  const puedeDesactivarMobiliario = computed(() => tipoUsuarioId.value >= 3)

  // Áreas
  const puedeVerAreas       = computed(() => tipoUsuarioId.value >= 3)
  const puedeCrearAreas     = computed(() => tipoUsuarioId.value >= 3)
  const puedeEditarAreas    = computed(() => tipoUsuarioId.value >= 3)
  const puedeEliminarAreas  = computed(() => tipoUsuarioId.value >= 3)
  const puedeReactivarAreas = computed(() => tipoUsuarioId.value >= 3)
  const puedeDesactivarAreas = computed(() => tipoUsuarioId.value >= 3)

  // Nivel 4 (super admin — usuarios)
  const puedeGestionarUsuarios = computed(() => tipoUsuarioId.value === 4)

  // Multas — bloqueo de préstamo si hay multas pendientes
  const puedePedirPrestamo = computed(() => puedePrestar.value && !tieneMultasPendientes.value)

  // ── Mapa de permisos para tienePermiso() ──────────────────────────────────
  const tienePermiso = (permiso) => {
    const mapa = {
      // Catálogo
      'canSeeRetiredBooks':   puedeVerLibrosRetirados.value,
      'canEditBooks':         puedeEditarLibros.value,
      'canDeleteBooks':       puedeEliminarLibros.value,
      'canRecoverBooks':      puedeReactivarLibros.value,
      'canCreateBooks':       puedeCrearLibros.value,
      'canRequestLoans':      puedePrestar.value,

      // Mobiliario
      'canViewFurniture':      puedeVerMobiliario.value,
      'canCreateFurniture':    puedeCrearMobiliario.value,
      'canEditFurniture':      puedeEditarMobiliario.value,
      'canDeleteFurniture':    puedeEliminarMobiliario.value,
      'canReactivatFurniture': puedeReactivarMobiliario.value,
      'canDesactivateFurniture': puedeDesactivarMobiliario.value,

      // Áreas
      'canViewAreas':       puedeVerAreas.value,
      'canCreateAreas':     puedeCrearAreas.value,
      'canEditAreas':       puedeEditarAreas.value,
      'canDeleteAreas':     puedeEliminarAreas.value,
      'canReactivateAreas': puedeReactivarAreas.value,
      'canDesactivateAreas': puedeDesactivarAreas.value,

      // Multas
      'ver_multas':       puedeVerMultas.value,
      'gestionar_multas': puedeGestionarMultas.value,
      'liquidar_multas':  puedeLiquidarMultas.value,
      'crear_multas':     puedeCrearMultas.value,

      // Recursos (general)
      'gestionar_recursos':  puedeGestionarRecursos.value,
      'gestionar_usuarios':  puedeGestionarUsuarios.value,
    }
    return mapa[permiso] ?? permisos.value[permiso] ?? false
  }

  // ── Actions ────────────────────────────────────────────────────────────────
  const login = async (credentials) => {
    isLoading.value = true
    try {
      const response = await api.post('api/auth/login', credentials)
      const { access_token } = response.data

      token.value = access_token
      localStorage.setItem('token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      await fetchCurrentUser()
      return { success: true, user: user.value, token: access_token }
    } catch (error) {
      return { success: false, error: getErrorMessage(error) }
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value    = null
    token.value   = null
    permisos.value = {}
    isLoading.value = false
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    localStorage.removeItem('permisos')
    delete api.defaults.headers.common['Authorization']
  }

  const fetchCurrentUser = async () => {
    try {
      const response = await api.get('api/auth/me')
      const userData = response.data
      user.value = userData
      if (userData.permisos) {
        permisos.value = userData.permisos
      } else {
        await fetchPermisosCompletos()
      }
      localStorage.setItem('user', JSON.stringify(user.value))
      return userData
    } catch (error) {
      logout()
      throw error
    }
  }

  const fetchPermisosCompletos = async () => {
    try {
      const response = await api.get('api/auth/me/permisos')
      permisos.value = response.data
      localStorage.setItem('permisos', JSON.stringify(permisos.value))
      if (response.data.tipo_usuario_id && user.value) {
        user.value.tipo_usuario_id = response.data.tipo_usuario_id
        localStorage.setItem('user', JSON.stringify(user.value))
      }
      return permisos.value
    } catch {
      // Fallback: construir permisos desde tipoUsuarioId
      const tipoId = tipoUsuarioId.value
      permisos.value = {
        puede_consultar:         true,
        puede_prestar:           tipoId >= 2,
        puede_gestionar_recursos: tipoId >= 3,
        puede_gestionar_usuarios: tipoId === 4,
        tipo_usuario_id:         tipoId,
      }
      localStorage.setItem('permisos', JSON.stringify(permisos.value))
      return permisos.value
    }
  }

  const actualizarEstadoMultas = (multas = []) => {
    tieneMultasPendientes.value = multas.some(m => Number(m.estado_multa_id) === 1)
  }

  const initializeAuth = async () => {
    if (isInitialized.value) return
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      token.value = storedToken
      api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
      try { await fetchCurrentUser() }
      catch { logout() }
    }
    isInitialized.value = true
  }

  // Alias para compatibilidad
  const inicializarDesdeStorage = initializeAuth

  const getErrorMessage = (error) => {
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 400: return data.detail || 'Datos inválidos'
        case 401: return data.detail || 'Credenciales incorrectas'
        case 403: return data.detail || 'Sin permisos'
        case 404: return data.detail || 'Recurso no encontrado'
        case 422:
          if (Array.isArray(data.detail))
            return data.detail.map(e => e.msg || e.loc?.join('.')).join(', ')
          return data.detail || 'Error de validación'
        case 500: return 'Error interno del servidor'
        default:  return data.detail || `Error ${status}`
      }
    }
    return error.request ? 'No se pudo conectar con el servidor' : error.message || 'Error desconocido'
  }

  // ── Exports ────────────────────────────────────────────────────────────────
  return {
    // State
    user, token, permisos, isLoading, isInitialized, tieneMultasPendientes,

    // Auth
    isAuthenticated, userName, userCode, userId, tipoUsuarioId,

    // Roles
    esEstudiante, esUsuarioComun, esAdminBasico, esAdminAvanzado,
    esSuperAdmin, esCualquierAdmin,

    // Permisos generales
    puedeConsultar, puedePrestar, puedePedirPrestamo,
    puedeGestionarRecursos, puedeGestionarUsuarios,

    // Libros
    puedeVerLibrosRetirados, puedeCrearLibros, puedeEditarLibros,
    puedeEliminarLibros, puedeReactivarLibros,

    // Mobiliario
    puedeVerMobiliario, puedeCrearMobiliario, puedeEditarMobiliario,
    puedeEliminarMobiliario, puedeReactivarMobiliario, puedeDesactivarMobiliario,

    // Áreas
    puedeVerAreas, puedeCrearAreas, puedeEditarAreas,
    puedeEliminarAreas, puedeReactivarAreas, puedeDesactivarAreas,

    // Multas
    puedeVerMultas, puedeGestionarMultas, puedeLiquidarMultas, puedeCrearMultas,

    // Actions
    login, logout, initializeAuth, inicializarDesdeStorage,
    fetchCurrentUser, fetchPermisosCompletos,
    actualizarEstadoMultas, tienePermiso,
  }
})