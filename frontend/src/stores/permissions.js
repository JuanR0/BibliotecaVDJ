import { defineStore } from 'pinia'
import { computed } from 'vue'
import { useAuthStore } from './auth'

export const usePermissionsStore = defineStore('permissions', () => {
  const authStore = useAuthStore()
  
  // Computed para reactividad
  const usuario = computed(() => authStore.user)
  const tipoUsuarioId = computed(() => usuario.value?.tipo_usuario_id || 1)
  const estaActivo = computed(() => usuario.value?.esta_activo !== false)
  
  // PERMISOS BASE
  const puedeConsultar = computed(() => estaActivo.value)
  const puedePrestar = computed(() => estaActivo.value && tipoUsuarioId.value >= 2)
  const puedeGestionarRecursos = computed(() => estaActivo.value && tipoUsuarioId.value >= 3)
  const puedeGestionarUsuarios = computed(() => estaActivo.value && tipoUsuarioId.value === 4)
  
  // PERMISOS ESPECÍFICOS
  // Para BookCatalog
  const puedeVerLibrosRetirados = computed(() => tipoUsuarioId.value >= 2)
  const puedeEditarLibros = computed(() => tipoUsuarioId.value >= 2)  // Tipos 2,3,4
  const puedeEliminarLibros = computed(() => tipoUsuarioId.value >= 3) // Tipos 3,4
  const puedeReactivarLibros = computed(() => tipoUsuarioId.value >= 3) // Tipos 3,4
  
  // Para vistas admin
  const puedeAccederAdmin = computed(() => tipoUsuarioId.value >= 2)
  const puedeCrearLibros = computed(() => tipoUsuarioId.value >= 3)
  const puedeGestionarPrestamos = computed(() => tipoUsuarioId.value >= 2)
  
  // TIPOS DE USUARIO
  const esUsuarioComun = computed(() => tipoUsuarioId.value === 1)
  const esAdminBasico = computed(() => tipoUsuarioId.value === 2)
  const esAdminAvanzado = computed(() => tipoUsuarioId.value === 3)
  const esSuperAdmin = computed(() => tipoUsuarioId.value === 4)
  
  // Método para verificar cualquier permiso
  const tienePermiso = (permiso) => {
    const permisosMap = {
      // Base
      'consultar': puedeConsultar.value,
      'prestar': puedePrestar.value,
      'gestionar_recursos': puedeGestionarRecursos.value,
      'gestionar_usuarios': puedeGestionarUsuarios.value,
      
      // Libros
      'ver_libros_retirados': puedeVerLibrosRetirados.value,
      'editar_libros': puedeEditarLibros.value,
      'eliminar_libros': puedeEliminarLibros.value,
      'reactivar_libros': puedeReactivarLibros.value,
      'crear_libros': puedeCrearLibros.value,
      
      // Admin
      'acceder_admin': puedeAccederAdmin.value,
      'gestionar_prestamos': puedeGestionarPrestamos.value
    }
    
    return permisosMap[permiso] || false
  }
  
  return {
    // Permisos base
    puedeConsultar,
    puedePrestar,
    puedeGestionarRecursos,
    puedeGestionarUsuarios,
    
    // Permisos específicos
    puedeVerLibrosRetirados,
    puedeEditarLibros,
    puedeEliminarLibros,
    puedeReactivarLibros,
    puedeCrearLibros,
    puedeAccederAdmin,
    puedeGestionarPrestamos,
    
    // Tipos de usuario
    esUsuarioComun,
    esAdminBasico,
    esAdminAvanzado,
    esSuperAdmin,
    tipoUsuarioId,
    
    // Métodos
    tienePermiso
  }
})