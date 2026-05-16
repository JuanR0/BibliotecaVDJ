// composables/usePermissions.js
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export const usePermissions = () => {
  const authStore = useAuthStore()

  const permissions = computed(() => ({
    // ── Libros ──────────────────────────────────────────────────────────────
    canSeeRetiredBooks: authStore.puedeVerLibrosRetirados,
    canCreateBooks:     authStore.puedeCrearLibros,
    canEditBooks:       authStore.puedeEditarLibros,
    canDeleteBooks:     authStore.puedeEliminarLibros,
    canRecoverBooks:    authStore.puedeReactivarLibros,
    canRequestLoans:    authStore.puedePrestar,

    // ── Mobiliario ───────────────────────────────────────────────────────────
    canViewFurniture:       authStore.puedeVerMobiliario,
    canCreateFurniture:     authStore.puedeCrearMobiliario,
    canEditFurniture:       authStore.puedeEditarMobiliario,
    canDeleteFurniture:     authStore.puedeEliminarMobiliario,
    canReactivatFurniture:  authStore.puedeReactivarMobiliario,
    canDesactivateFurniture: authStore.puedeDesactivarMobiliario,

    // ── Áreas ────────────────────────────────────────────────────────────────
    canViewAreas:        authStore.puedeVerAreas,
    canCreateAreas:      authStore.puedeCrearAreas,
    canEditAreas:        authStore.puedeEditarAreas,
    canDeleteAreas:      authStore.puedeEliminarAreas,
    canReactivateAreas:  authStore.puedeReactivarAreas,
    canDesactivateAreas: authStore.puedeDesactivarAreas,

    // ── Multas ───────────────────────────────────────────────────────────────
    canViewFines:    authStore.puedeVerMultas,
    canManageFines:  authStore.puedeGestionarMultas,
    canCreateFines:  authStore.puedeCrearMultas,
    canSettleFines:  authStore.puedeLiquidarMultas,

    // ── Roles (atajos para v-if en templates) ────────────────────────────────
    isStudent:       authStore.esEstudiante,
    isBasicAdmin:    authStore.esAdminBasico,
    isAdvancedAdmin: authStore.esAdminAvanzado,
    isSuperAdmin:    authStore.esSuperAdmin,
    isAnyAdmin:      authStore.esCualquierAdmin,
  }))

  const hasPermission    = (name) => permissions.value[name] === true
  const hasAnyPermission = (list) => list.some(p  => permissions.value[p] === true)
  const hasAllPermissions = (list) => list.every(p => permissions.value[p] === true)

  return { permissions, hasPermission, hasAnyPermission, hasAllPermissions, authStore }
}