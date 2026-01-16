import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

//IMPORTACION DE VISTAS (TESTING)
import UserManagement from '@/views/SuperAdmin/UserManagement.vue'
import UserCreate from '@/views/SuperAdmin/UserCreate.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/login', 
    name: 'Login',
    component: () => import('../views/auth/LoginView.vue')
  },
  {
    path: '/healthcheck',
    name: 'HealthCheck', 
    component: () => import('../views/HealthCheckView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/RegisterView.vue'),
    meta: { public: true }
  },
  {
    path: '/userMenu',
    name: 'UserMenu',
    component: () => import('../views/user/UserMenu.vue'),
    meta: { public: true }
  },
  {
  path: '/catalog',
  name: 'BookCatalog',
  component: () => import('../views/user/BookCatalog.vue')
  },
  {
  path: '/admin/libros/editar/:id',
  name: 'BookEdit',
  component: () => import('../views/admin/BookEdit.vue'),
  meta: {
    title: 'Editar Libro',
    requiresAuth: true,
    roles: ['admin', 'advanced_admin', 'super_admin'],
    layout: 'admin'
    }
  },

  {
  path: '/admin/libros/crear',
  name: 'BookCreate',
  component: () => import('../views/admin/CrearLibro.vue'),
  meta: {
    title: 'Crear Nuevo Libro',
    requiresAuth: true,
    roles: [3, 4],
    layout: 'admin'
    },
  },
  {
    path: '/SuperAdmin/usuarios',
    name: 'UserManagement',
    component: UserManagement,
    meta: { 
      requiresAuth: true,
      requiresSuperAdmin: true 
    }
  },
  {
    path: '/SuperAdmin/usuarios/crear',
    name: 'UserCreate',
    component: UserCreate,
    meta: { 
      requiresAuth: true,
      requiresSuperAdmin: true 
    }
  }
  
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

//GUARD PARA NAVEGACION GLOBAL
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Verificar autenticación
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // Verificar super admin para rutas protegidas
  if (to.meta.requiresSuperAdmin && authStore.tipoUsuarioId !== 4) {
    alert('No tienes permisos para acceder a esta sección')
    next('/')
    return
  }
  
  next()
})

export default router