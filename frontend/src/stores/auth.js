// stores/auth.js
import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    permisos: JSON.parse(localStorage.getItem('permisos')) || {},
    isLoading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token, // Verificacion de token
    userName: (state) => state.user?.nombre_completo || state.user?.user_name || 'Usuario',
    userRole: (state) => {
      // Mapear user_type string a número para compatibilidad
      const roleMap = {
        'comun': 1,
        'admin': 2,
        'advanced_admin': 3,
        'super_admin': 4
      }
      return roleMap[state.user?.user_type] || state.user?.tipo_usuario_id || 1
    },

    //EDIT BOOKS PERMISSION
    canEditBooks: (state) => {
      // Solo verifica el tipo de usuario
      const userType = state.user?.user_type
      const tipoId = state.user?.tipo_usuario_id
      
      // Si es admin, advanced_admin o super_admin (por string)
      if (userType && ['admin', 'advanced_admin', 'super_admin'].includes(userType)) {
        return true
      }
      
      // Si es 2, 3 o 4 (por número)
      if (tipoId && [2, 3, 4].includes(tipoId)) {
        return true
      }
      
      return false
    },
    
    userCode: (state) => state.user?.codigo_universitario || '',
    isAdmin: (state) => this.userRole >= 2,
    isSuperAdmin: (state) => this.userRole === 4,
    
    //Getters para otros permisos mas especificos
    canViewBooks: (state) => state.permisos?.view_books === true,
    canBorrowBooks: (state) => state.permisos?.borrow_books === true,
    canManageUsers: (state) => state.permisos?.manage_users === true,
    canManageBooks: (state) => state.permisos?.manage_books === true,
    canManageSystem: (state) => state.permisos?.manage_system === true,
    canViewReports: (state) => state.permisos?.view_reports === true,

    // Getters para tipos de usuario
    isCommonUser: (state) => state.permisos?.es_usuario_comun === true,
    isBasicAdmin: (state) => state.permisos?.es_admin_basico === true,
    isAdvancedAdmin: (state) => state.permisos?.es_admin_avanzado === true,
    isSuperAdmin: (state) => state.permisos?.es_super_admin === true,
    isAnyAdmin: (state) => state.permisos?.es_cualquier_admin === true,

    // Para compatibilidad
    isAdmin: (state) => state.permisos?.es_cualquier_admin === true,
    
    can: (state) => {
      return (permission) => {
        const permissionMap = {
          'view_books': 'puede_consultar',
          'borrow_books': 'puede_prestar',
          'manage_books': 'puede_gestionar_recursos',
          'manage_users': 'puede_gestionar_usuarios'
        }
        const spanishPermission = permissionMap[permission] || permission
        return state.permisos?.[spanishPermission] === true
      }
    }

  },

  actions: {
      logout() {
            console.log('🚪 Cerrando sesión...')
            
            // Limpiar estado local
            this.user = null
            this.token = null
            this.isLoading = false
            
            // Limpiar localStorage
            localStorage.removeItem('user')
            localStorage.removeItem('token')
            
            // Remover token de los headers de axios
            delete api.defaults.headers.common['Authorization']
            
            console.log('✅ Sesión cerrada correctamente')
          },

    async login(credentials) {
      this.isLoading = true
      try {
        
      
        console.log('🔐 Enviando credenciales a /auth/login:', credentials)
        
        const response = await api.post('/auth/login', credentials)
        console.log('✅ Respuesta del login:', response.data)
        
        //Response data
        const { access_token, token_type, user_type, user_name, user_id } = response.data
        
        // Guardar token
        this.token = access_token
        localStorage.setItem('token', access_token)
        
        // Crear objeto usuario con la información del token
        const userData = {
          id: user_id,
          nombre_completo: user_name,
          user_type: user_type,
          tipo_usuario_id: this.mapUserTypeToId(user_type),
          codigo_universitario: credentials.codigo_universitario
        }
        
        // Guardar usuario
        this.user = userData
        localStorage.setItem('user', JSON.stringify(userData))
        
        
        
        // Configurar el token en axios para futuras requests
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        
        return { 
          success: true,
          user: userData,
          token: access_token
        }
        
      } catch (error) {
        console.error('❌ Error en login:', error)
        return { 
          success: false, 
          error: this.getErrorMessage(error)
        }
      } finally {
        this.isLoading = false
      }
    },

    async register(userData) {
      this.isLoading = true
      try {
        console.log('Enviando registro:', userData)
        const response = await api.post('/auth/register', userData)
        console.log('Registro exitoso:', response.data)
        
        return { 
          success: true, 
          data: response.data 
        }
        
      } catch (error) {
        console.error('Error en registro:', error)
        return {
          success: false,
          error: this.getErrorMessage(error)
        }
      } finally {
        this.isLoading = false
      }
    },

    async getCurrentUser() {
      try {
        // Obtener información completa del usuario autenticado
        const response = await api.get('/auth/me')
        const userData = response.data
        
        // Actualizar información del usuario
        this.user = { ...this.user, ...userData }
        localStorage.setItem('user', JSON.stringify(this.user))
        
        return userData
      } catch (error) {
        console.error('Error obteniendo usuario actual:', error)
        this.logout()
        throw error
      }
    },

    async fetchPermisos() {
      try {
        console.log('Obteniendo permisos del usuario...')
        const response = await api.get('/auth/me/permisos')
        console.log('Permisos obtenidos:', response.data)
        
        // Guardar permisos
        this.permisos = response.data
        localStorage.setItem('permisos', JSON.stringify(response.data))
        
        return response.data
      } catch (error) {
        console.error('Error obteniendo permisos:', error)
        this.permisos = {}
        localStorage.removeItem('permisos')
        return {}
      }
    },

    logout() {
      //Seteando informacion a vacio
      this.user = null
      this.token = null
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
      console.log('Usuario cerró sesión')
    },

    // Método auxiliar para mapear user_type string a ID numérico
    mapUserTypeToId(userType) {
      const roleMap = {
        'comun': 1,
        'admin_basico': 2,
        'admin_avanzado': 3,
        'super_admin': 4
      }
      return roleMap[userType] || 1
    },

    // Método auxiliar para manejar errores
    getErrorMessage(error) {
      if (error.response) {
        const { status, data } = error.response
        
        switch (status) {
          case 400:
            return data.detail || 'Datos inválidos'
          case 401:
            return data.detail || 'Credenciales incorrectas'
          case 404:
            return data.detail || 'Usuario no encontrado'
          case 409:
            return data.detail || 'El usuario ya existe'
          case 422:
            if (data.detail && Array.isArray(data.detail)) {
              const errors = data.detail.map(err => {
                return err.msg || (err.loc ? err.loc.join('.') : JSON.stringify(err))
              }).join(', ')
              return `Errores de validación: ${errors}`
            }
            return data.detail || 'Error de validación'
          case 500:
            return 'Error interno del servidor'
          default:
            return data.detail || `Error ${status}: ${data.message || 'Error desconocido'}`
        }
      } else if (error.request) {
        return 'No se pudo conectar con el servidor'
      } else {
        return error.message || 'Error de conexión'
      }
    },

    // Método para verificar permisos
    can(permission) {
      const permissions = {
        1: ['view_books', 'borrow_books', 'view_profile'],
        2: ['manage_users', 'view_reports'],
        3: ['manage_books', 'manage_categories'],
        4: ['manage_admins', 'system_config']
      }
      
      const userPermissions = permissions[this.userRole] || []
      return userPermissions.includes(permission)
    }
  }
})