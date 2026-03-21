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

import MobiliarioManagementView from '@/views/admin//FurnitureManagement.vue'
import MobiliarioCreateView from '@/views/admin/FurnitureCreate.vue'
import MobiliarioEditView from '@/views/admin/EditFurniture.vue'

import AreasManagement from '@/views/admin/AreasManagement.vue'

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

  {
    path: '/admin/areas',
    name: 'AreasManagement',
    component: AreasManagement,
    meta: {
      requiresAuth: true,
      requiredPermission: 'canViewAreas'
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

  if (to.meta.title) {
    document.title = `${to.meta.title} | BiblioSys`
  }
  
  // RUTAS PUBLICAS
  if (to.meta.public === true) {
    next()
    return
  }
  
  // VERFICACION DE AUTENTICACION
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    //Usuario no autenficado se envia a login
    console.warn('Acceso no autorizado - Redirigiendo a login')
    next({ 
      name: 'Login',
      query: { redirect: to.fullPath }
    })
    return
  }
  
  // SI ESTA AUTENTICADO Y SE ENVIO A LOGIN O REGISTER, SE ENVIA A HOME
  if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    next('/')
    return
  }
  
  //VERIFICACION DE PERMISOS DEL USUARIO
  if (to.meta.requiresAuth && authStore.isAuthenticated) {
    const userTipoId = authStore.tipoUsuarioId
    
    //REDIRECCION SI USUARIO NO ES TIPO 4
    if (to.meta.requiresSuperAdmin && userTipoId !== 4) {
      console.warn(`Usuario tipo ${userTipoId} intentó acceder a ruta Super Admin`)
      showPermissionError()
      next('/')
      return
    }
    
    //REDIRECCION A USUARIOS MENORES A TIPO 3
    if (to.meta.requiresAdminAdvanced && userTipoId < 3) {
      console.warn(`Usuario tipo ${userTipoId} intentó acceder a ruta Admin Avanzado`)
      showPermissionError('Se requieren permisos de administrador avanzado')
      next('/')
      return
    }
    
    //REDIRECCION A USUARIOS QUE NO SEAN AL MENOS TIPO 2
    if (to.meta.requiresAnyAdmin && userTipoId < 2) {
      console.warn(`Usuario tipo ${userTipoId} intentó acceder a ruta Admin`)
      showPermissionError('Se requieren permisos de administrador')
      next('/')
      return
    }
  }
  
  //PERMITIR NAVEGACION
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