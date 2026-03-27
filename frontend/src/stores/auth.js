// stores/auth.js - VERSIÓN OPTIMIZADA Y SINCRONIZADA CON BACKEND
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {

  const isInitialized = ref(false)

  // ========== STATE ==========
  const user = ref(JSON.parse(localStorage.getItem('user')) || null)
  const token = ref(localStorage.getItem('token') || null)
  const permisos = ref(JSON.parse(localStorage.getItem('permisos')) || {})
  const isLoading = ref(false)
  const tieneMultasPendientes = ref(false)


  // ========== GETTERS (COMPUTED) ==========
  const isAuthenticated = computed(() => !!token.value)
  
  const userName = computed(() => 
    user.value?.nombre_completo || user.value?.user_name || 'Usuario'
  )
  
  const userCode = computed(() => 
    user.value?.codigo_universitario || ''
  )

  // TIPO DE USUARIO
  const tipoUsuarioId = computed(() => {
    //Tipo_usuario_id del backend
    if (user.value?.tipo_usuario_id) return user.value.tipo_usuario_id
    
    //Permisos del backend
    if (permisos.value?.tipo_usuario_id) return permisos.value.tipo_usuario_id
    
    //Mapeo user_type string
    const roleMap = {
      'comun': 1,
      'admin_basico': 2,
      'admin_avanzado': 3,
      'super_admin': 4,
      //Definiciones para compatibilidad
      'admin': 2,
      'advanced_admin': 3
    }
    
    const userType = user.value?.user_type
    return roleMap[userType] || 1
  })

  const puedePedirPrestamo = computed(
    () => puedePrestar.value && !tieneMultasPendientes.value
  )

//USER ID
const userId = computed(() => {
  if (user.value?.id) return user.value.id
  if (user.value?.usuario_id) return user.value.usuario_id
  return null
  })

  // PERMISOS DIRECTOS DESDE BACKEND (computed para reactividad automática)
  const puedeConsultar = computed(() => permisos.value?.puede_consultar === true)
  const puedePrestar = computed(() => permisos.value?.puede_prestar === true)
  const puedeGestionarRecursos = computed(() => permisos.value?.puede_gestionar_recursos === true)
  const puedeGestionarUsuarios = computed(() => permisos.value?.puede_gestionar_usuarios === true)

  // PERMISOS ESPECIFICOS PARA COMPONENTES
  const puedeVerLibrosRetirados = computed(() => userId.value >= 2)
  const puedeEditarLibros = computed(() => userId.value >= 2)  // Tipos 2,3,4
  const puedeEliminarLibros = computed(() => userId.value >= 3) // Tipos 3,4
  const puedeReactivarLibros = computed(() => userId.value >= 3) // Tipos 3,4
  const puedeCrearLibros = computed(() => userId.value >= 3)    // Tipos 3,4

  // TIPOS DE USUARIO (Definicion de permisos para ocultar/mostrar informacion de admins)
  const esUsuarioComun = computed(() => userId.value === 1)
  const esAdminBasico = computed(() => userId.value === 2)
  const esAdminAvanzado = computed(() => userId.value === 3)
  const esSuperAdmin = computed(() => userId.value === 4)
  const esCualquierAdmin = computed(() => userId.value >= 2)

  //PERMISOS PARA MOBILIARIO
  const puedeVerMobiliario = computed(() => userId.value >= 3)  // Tipos 2,3,4
  const puedeEditarMobiliario = computed(() => userId.value >= 3)  // Tipos 2,3,4
  const puedeEliminarMobiliario = computed(() => userId.value >= 3) // Tipos 3,4
  const puedeReactivarMobiliario = computed(() => userId.value >= 3) // Tipos 3,4
  const puedeCrearMobiliario = computed(() => userId.value >= 3)    // Tipos 3,4
  const puedeDesactivarMobiliario = computed(() => userId.value >= 3) // Tipos 3,4

  //PERMISOSS PARA AREAS
  const puedeVerAreas = computed(() => userId.value >= 3)  // Tipos 3,4
  const puedeEditarAreas = computed(() => userId.value >= 3)  // Tipos 3,4
  const puedeEliminarAreas = computed(() => userId.value >= 3) // Tipos 3,4
  const puedeReactivarAreas = computed(() => userId.value >= 3) // Tipos 3,4
  const puedeCrearAreas = computed(() => userId.value >= 3)    // Tipos 3,4
  const puedeDesactivarAreas = computed(() => userId.value >= 3) // Tipos 3,4

  //PERMISOS PARA MULTAS
  const puedeVerMultas      = computed(() => tipoUsuarioId.value >= 1)  // todos
  const puedeGestionarMultas = computed(() => tipoUsuarioId.value >= 2) // admins
  const puedeLiquidarMultas  = computed(() => tipoUsuarioId.value >= 2) // admins
  const puedeCrearMultas     = computed(() => tipoUsuarioId.value >= 2) // admins

  // ========== ACTIONS ==========
  const login = async (credentials) => {
    isLoading.value = true
    try {
      console.log('Iniciando sesion:', credentials)
      const response = await api.post('api/auth/login', credentials)
      console.log('Login exitoso:', response.data)
      
      const { access_token } = response.data
      
      // TOKEN (GUARDADO)
      token.value = access_token
      localStorage.setItem('token', access_token)
      
      // Configurar axios (peticiones de HTTP con token de autenticacion)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      //DATOS DE USUARIO
      await fetchCurrentUser()
      
      
      return { success: true, user: user.value, token: access_token }
      
    } catch (error) {
      console.error('Error en login:', error)
      return { 
        success: false, 
        error: getErrorMessage(error)
      }
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    isLoading.value = true
    try {
      console.log('Registrando...', userData)
      const response = await api.post('api/auth/register', userData)
      console.log('Registro exitoso!', response.data)
      
      return { success: true, data: response.data }
      
    } catch (error) {
      console.error('Error en registro:', error)
      return { success: false, error: getErrorMessage(error) }
    } finally {
      isLoading.value = false
    }
  }

  //MULTAS
  const actualizarEstadoMultas = (multas = []) => {
    tieneMultasPendientes.value = multas.some(
    m => Number(m.estado_multa_id) === 1
    )
  }

  // Obteniendo usuario actual con sus permisos
  const fetchCurrentUser = async () => {
    try {
      console.log('Obteniendo usuario actual...')
      
      //Esperando respuesta de auth y guardando
      const response = await api.get('api/auth/me')
      const userData = response.data
  
      if (userData.permisos) {
        user.value = userData
        permisos.value = userData.permisos
      } else {
        user.value = userData
        // Obtener permisos por separado (solo permisos)
        await fetchPermisosCompletos()
      }
      
      localStorage.setItem('user', JSON.stringify(user.value))
      return userData
      
    } catch (error) {
      console.error('Error obteniendo usuario:', error)
      logout()
      throw error
    }
  }

  // Obtener permisos desde security
  const fetchPermisosCompletos = async () => {
    try {
      console.log('Obteniendo permisos del backend...')
      
      const response = await api.get('api/auth/me/permisos')
      const permisosData = response.data
      
      console.log('Permisos recibidos!', permisosData)
      
      // Guardar permisos
      permisos.value = permisosData
      localStorage.setItem('permisos', JSON.stringify(permisosData))
      
      // Actualizar usuario con tipo_usuario_id si viene en permisos
      if (permisosData.tipo_usuario_id && user.value) {
        user.value.tipo_usuario_id = permisosData.tipo_usuario_id
        localStorage.setItem('user', JSON.stringify(user.value))
      }
      
      return permisosData
      
    } catch (error) {
      console.error('No se pudieron obtener permisos:', error)
      
      // Si no hay endpoint de permisos, crear permisos básicos desde user_type (caso de uso excepcional)
      const defaultPermisos = crearPermisosDesdeUserType()
      permisos.value = defaultPermisos
      localStorage.setItem('permisos', JSON.stringify(defaultPermisos))
      
      return defaultPermisos
    }
  }

  // Crear permisos básicos si el endpoint no responde (o existe)
  const crearPermisosDesdeUserType = () => {
    const tipoId = tipoUsuarioId.value
    
    return {
      puede_consultar: true,                  //TODOS
      puede_prestar: tipoId >= 2,
      puede_gestionar_recursos: tipoId >= 3,
      puede_gestionar_usuarios: tipoId === 4,
      
      // Informacion para frontend
      tipo_usuario_id: tipoId,
      es_usuario_comun: tipoId === 1,
      es_admin_basico: tipoId === 2,
      es_admin_avanzado: tipoId === 3,
      es_super_admin: tipoId === 4,
      es_cualquier_admin: tipoId >= 2
    }
  }

  //LOGOUT (CERRAR SESION)
  const logout = () => {
    console.log('Cerrando sesión...')
    
    // Limpiar state
    user.value = null
    token.value = null
    permisos.value = {}
    isLoading.value = false
    
    // Limpiar localStorage
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    localStorage.removeItem('permisos')
    
    // Remover token
    delete api.defaults.headers.common['Authorization']
    
    console.log('Sesión cerrada correctamente!')
  }

  //INICIALIZACION
  const initializeAuth = async () => {
    if (isInitialized.value) return

    const storedToken = localStorage.getItem('token')

    if (!storedToken) {
      isInitialized.value = true
      return
    }

    try {
      token.value = storedToken
      api.defaults.headers.common['Authorization'] =`Bearer ${storedToken}`

      await fetchCurrentUser()

    } catch (error) {
      console.warn('Token inválido')
      logout()
    } finally {
      isInitialized.value = true
    }
  }

  const inicializarDesdeStorage = async () => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      token.value = storedToken
      api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
      
      // Cargar usuario y permisos
      if (localStorage.getItem('user')) {
        try {
          await fetchCurrentUser()
        } catch (error) {
          console.log('Token inválido, limpiando...')
          logout()
        }
      }
    }
  }

  //Verificar permisos (general)
  const tienePermiso = (permiso) => {
    // Permisos directos del backend
    const permisosDirectos = {
      'consultar': puedeConsultar.value,
      'prestar': puedePrestar.value,
      'gestionar_recursos': puedeGestionarRecursos.value,
      'gestionar_usuarios': puedeGestionarUsuarios.value,

      'ver_libros_retirados': puedeVerLibrosRetirados.value,
      'editar_libros': puedeEditarLibros.value,
      'eliminar_libros': puedeEliminarLibros.value,
      'reactivar_libros': puedeReactivarLibros.value,
      'crear_libros': puedeCrearLibros.value,

      // Mobiliario
      'canViewFurniture': puedeVerMobiliario.value,
      'canEditFurniture': puedeEditarMobiliario.value,
      'canDeleteFurniture': puedeEliminarMobiliario.value,
      'canReactivatFurniture': puedeReactivarMobiliario.value,
      'canCreateFurniture': puedeCrearMobiliario.value,
      'canDesactivateFurniture': puedeDesactivarMobiliario.value,

      // Áreas (AGREGAR ESTOS)
      'canViewAreas': puedeVerAreas.value,
      'canEditAreas': puedeEditarAreas.value,
      'canDeleteAreas': puedeEliminarAreas.value,
      'canReactivateAreas': puedeReactivarAreas.value,
      'canCreateAreas': puedeCrearAreas.value,
      'canDesactivateAreas': puedeDesactivarAreas.value,

      //Multas
      'ver_multas':       puedeVerMultas.value,
      'gestionar_multas': puedeGestionarMultas.value,
      'liquidar_multas':  puedeLiquidarMultas.value,
      'crear_multas':     puedeCrearMultas.value
    }
    
    // Permisos del objeto permisos
    const permisosBackend = permisos.value[permiso]
    
    return permisosDirectos[permiso] || permisosBackend || false
  }

  // Guia para errores
  const getErrorMessage = (error) => {
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400: return data.detail || 'Datos inválidos'
        case 401: return data.detail || 'Credenciales incorrectas'
        case 404: return data.detail || 'Recurso no encontrado'
        case 409: return data.detail || 'El recurso ya existe'
        case 422: 
          if (data.detail && Array.isArray(data.detail)) {
            return data.detail.map(err => err.msg || err.loc?.join('.')).join(', ')
          }
          return data.detail || 'Error de validación'
        case 500: return 'Error interno del servidor'
        default: return data.detail || `Error ${status}`
      }
    } else if (error.request) {
      return 'No se pudo conectar con el servidor'
    } else {
      return error.message || 'Error de conexión'
    }
  }

  // ========== EXPORT ==========
  return {
    // State
    user,
    token,
    permisos,
    isLoading,
    tieneMultasPendientes,
    
    // Computed - Autenticación
    isAuthenticated,
    userName,
    userCode,
    tipoUsuarioId,
    
    // Computed - Permisos directos (para uso fácil en templates)
    puedeConsultar,
    puedePrestar,
    puedeGestionarRecursos,
    puedeGestionarUsuarios,
    
    // Computed - Permisos específicos
    puedeVerLibrosRetirados,
    puedeEditarLibros,
    puedeEliminarLibros,
    puedeReactivarLibros,
    puedeCrearLibros,
    
    // Computed - Tipos de usuario
    esUsuarioComun,
    esAdminBasico,
    esAdminAvanzado,
    esSuperAdmin,
    esCualquierAdmin,

    //Computed - Mobiliario
    puedeVerMobiliario,
    puedeEditarMobiliario,
    puedeEliminarMobiliario,
    puedeReactivarMobiliario,
    puedeCrearMobiliario,
    puedeDesactivarMobiliario,
    
    //Computed - Areas
    puedeVerAreas,
    puedeEditarAreas,
    puedeEliminarAreas,
    puedeReactivarAreas,
    puedeCrearAreas,
    puedeDesactivarAreas,

    //Computed - Multas
    puedePedirPrestamo,
    puedeVerMultas,
    puedeGestionarMultas,
    puedeLiquidarMultas,
    puedeCrearMultas,

    // Actions
    login,
    register,
    logout,
    fetchCurrentUser,
    fetchPermisosCompletos,
    inicializarDesdeStorage,
    tienePermiso,
    actualizarEstadoMultas,

    userId,
    isInitialized,
    initializeAuth
  }
})