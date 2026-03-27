import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export const usePermissions = () => {
  const authStore = useAuthStore()

  
  
  // Permisos específicos para BookCatalog
  const permissions = computed(() => ({
    // CRUD de libros
    canCreateBooks: authStore.puedeCrearLibros,
    canEditBooks: authStore.puedeEditarLibros,
    canDeleteBooks: authStore.puedeEliminarLibros,
    canRecoverBooks: authStore.puedeReactivarLibros,
    

    // CRUD Mobiliario
    canCreateFurniture: authStore.puedeGestionarRecursos,
    canEditFurniture: authStore.puedeGestionarRecursos,
    canDeleteFurniture: authStore.puedeGestionarRecursos,
    canRecoverFurniture: authStore.puedeGestionarRecursos,
    canDesactivateFurniture: authStore.puedeGestionarRecursos,
    canViewMobiliario: authStore.puedeGestionarRecursos,
    
    // Visualización
    canSeeRetiredBooks: authStore.puedeVerLibrosRetirados,
    
    // Préstamos
    canRequestLoans: authStore.puedePrestar,
    
    // Tipo de usuario
    isCommonUser: authStore.esUsuarioComun,
    isAdmin: authStore.esCualquierAdmin,
    isAdvancedAdmin: authStore.esAdminAvanzado,
    isSuperAdmin: authStore.esSuperAdmin
  }))

  const hasPermission = (permissionName) => {
    return permissions.value[permissionName] === true
  }

  const hasAnyPermission = (permissionsList) => {
    return permissionsList.some(p => permissions.value[p] === true)
  }

  const hasAllPermissions = (permissionsList) => {
    return permissionsList.every(p => permissions.value[p] === true)
}


  
  return {
    permissions,
    hasPermission,
    authStore,
    hasAnyPermission,
    hasAllPermissions
  }
}