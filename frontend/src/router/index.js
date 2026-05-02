import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

//IMPORTACION DE VISTAS
import Home from '@/views/HomeView.vue'
import HealthCheckView from '@/views/HealthCheckView.vue'

import Login from '@/views/auth/LoginView.vue'
import Register from '@/views/auth/RegisterView.vue'

import userMenu from '@/views/user/UserMenu.vue'

import UserManagement from '@/views/SuperAdmin/UserManagement.vue'
import UserCreate from '@/views/SuperAdmin/UserCreate.vue'

import BookManagement from '@/views/user/BookCatalog.vue'
import BookCreate from '@/views/admin/CrearLibro.vue'
import BookEdit from '@/views/admin/BookEdit.vue'

import MobiliarioManagementView from '@/views/admin/FurnitureManagement.vue'
import MobiliarioCreateView from '@/views/admin/FurnitureCreate.vue'
import MobiliarioEditView from '@/views/admin/EditFurniture.vue'

import AreasManagement from '@/views/admin/AreasManagement.vue'
import AreasEstudio from '@/views/user/AreasEstudio.vue'
import SolicitudesArea from '@/views/admin/SolicitudesArea.vue'

import MisMultas from '@/views/user/Multas.vue'
import MultasPendientes from '@/views/admin/MultasPendientes.vue'
import DevolucionesPendientes from '@/views/admin/DevolucionesPendientes.vue'

import Error404 from '@/views/NotFoundView.vue'

const routes = [
  // ========== RUTAS PUBLICAS ==========
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { 
      public:true
    }
  },
  {
    path: '/login', 
    name: 'Login',
    component: Login,
    meta: { 
      public:true
    }
    
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { 
      public:true
    }
  },
  {
    path: '/health',
    name: 'HealthCheck', 
    component:HealthCheckView,
    meta: { 
      public:true
    }
  },
  
// ========== RUTAS DE USUARIO ==========

  {
    path: '/user/menu',
    name: 'UserMenu',
    component: userMenu,
    meta: {
    title: 'User Menu',
    requiresAuth: true,
    requiresAnyAdmin:true
    }
  },

  // ========== RUTAS DE LIBROS ==========

  {
    path: '/admin/libros',
    name: 'BookCatalog',
    component: BookManagement,
    meta: { 
      public:true
    }
  },

  {
  path: '/admin/libros/crear',
  name: 'BookCreate',
  component: BookCreate,
  meta: {
    title: 'Crear libro',
    requiresAuth: true,
    requiresAdminAdvanced:true
    }
  },

  {
  path: '/admin/libros/editar/:id',
  name: 'BookEdit',
  component: BookEdit,
  meta: {
    title: 'Editar Libro',
    requiresAuth: true,
    requiresAdminAdvanced:true
    }
  },
  

  // ========== RUTAS DE USUARIO ==========
  {
    path: '/admin/usuarios',
    name: 'UserManagement',
    component: UserManagement,
    meta: { 
      requiresAuth: true,
      requiresAdminAdvanced: true 
    }
  },
  {
    path: '/admin/usuarios/crear',
    name: 'UserCreate',
    component: UserCreate,
    meta: { 
      requiresAuth: true,
      requiresAdminAdvanced: true 
    }
  },
  // ========== RUTAS DE MOBILIARIO ==========
  {
    path: '/admin/mobiliario',
    name: 'FurnitureManagement',
    component: MobiliarioManagementView,
    meta: {
      title: 'Inventario de Mobiliario',
      requiresAuth: true,
      requiresAdminAdvanced: true
    }
  },
  {
    path: '/admin/mobiliario/crear',
    name: 'FurnitureCreate',
    component: MobiliarioCreateView,
    meta: {
      title: 'Agregar Mobiliario',
      requiresAuth: true,
      requiresAdminAdvanced: true
    }
  },
  {
    path: '/admin/mobiliario/editar/:id',
    name: 'FurnitureEdit',
    component: MobiliarioEditView,
    meta: {
      title: 'Editar Mobiliario',
      requiresAuth: true,
      requiresAdminAdvanced: true,
    },
    props: true
  },

  // ========== RUTAS DE AREAS ==========

  {
    path: '/admin/areas',
    name: 'AreasManagement',
    component: AreasManagement,
    meta: {
      requiresAuth: true,
      requiredPermission: 'canViewAreas'
    }
  },

  {
    path: '/areas-estudio',
    name: 'AreasEstudio',
    component: AreasEstudio,
    meta: { requiresAuth: true }
  },

  { 
    path: '/admin/solicitudes-areas', 
    name: 'SolicitudesAreas', 
    component: SolicitudesArea, 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },


  // ========== RUTAS DE MULTAS ==========
  
  {
    path: '/user/multas',
    name: 'MisMultas',
    component: MisMultas,
    meta:{
      requiresAuth: true
    },
  },

  {
    path: '/admin/multasPendientes',
    name: 'MultasPendientes',
    component: MultasPendientes,
    meta:
    {
      requiresAuth: true,
      requiresAdminAdvanced: true
    }
  },

  {
    path: '/admin/devoluciones-pendientes',
    name: 'DevolucionesPendientes',
    component: DevolucionesPendientes,
    meta: 
    { 
      requiresAuth: true, requiresAdminAdvanced: true 
    }
  },


  // ========== RUTA 404 ==========
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: Error404,
    meta: { title: 'Página no encontrada' }
  }
]


const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// ========== GUARD GLOBAL DE NAVEGACIÓN ==========
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Inicializar autenticación si aún no se ha hecho
  if (!authStore.isInitialized) {
    await authStore.initializeAuth()
  }

  // TITLE DE LA PAGINA
  if (to.meta.title) {
    document.title = `${to.meta.title} | BiblioSys`
  }

  // ==============================
  // RUTAS PUBLICAS
  // ==============================
  if (to.meta.public === true) {
    return next()
  }

  // ==============================
  // VERIFICAR AUTENTICACION
  // ==============================
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.warn('Acceso no autorizado - Redirigiendo a login')

    return next({
      name: 'Login',
      query: { redirect: to.fullPath }
    })
  }

  // ==============================
  // EVITAR QUE USUARIO AUTENTICADO VAYA A LOGIN
  // ==============================
  if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    return next('/')
  }

  // ==============================
  // VALIDAR PERMISOS POR TIPO
  // ==============================
  if (to.meta.requiresAuth) {

    const userTipoId = authStore.tipoUsuarioId

    if (to.meta.requiresSuperAdmin && userTipoId !== 4) {
      showPermissionError('Solo super administradores pueden acceder')
      return next('/')
    }

    if (to.meta.requiresAdminAdvanced && userTipoId < 3) {
      showPermissionError('Se requieren permisos de administrador avanzado')
      return next('/')
    }

    if (to.meta.requiresAnyAdmin && userTipoId < 2) {
      showPermissionError('Se requieren permisos de administrador')
      return next('/')
    }

  }

  // ==============================
  // VALIDAR PERMISOS ESPECIFICOS
  // ==============================
  if (to.meta.requiredPermission) {

    const permission = to.meta.requiredPermission

    if (!authStore.tienePermiso(permission)) {

      console.warn(`Permiso requerido: ${permission}`)

      showPermissionError('No tienes permisos para acceder a esta sección')

      return next('/')
    }

  }

  // ==============================
  // PERMITIR NAVEGACION
  // ==============================
  next()
})


// Función auxiliar para mostrar errores de permisos
function showPermissionError(message = 'No tienes permisos para acceder a esta sección') {
  console.error('Error de permisos:', message)
  
  // Opción 1: Alert básico
  // alert(message)
  
  // Opción 2: Toast (si tienes sistema)
  // useToast().error(message)
  
  // Opción 3: Guardar en store para mostrar en componente
  const authStore = useAuthStore()
  authStore.lastPermissionError = message
}

export default router