import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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
  name: 'BookEdit',
  component: () => import('../views/admin/CrearLibro.vue'),
  meta: {
    title: 'Crear Nuevo Libro',
    requiresAuth: true,
    roles: [3, 4], // Solo advanced_admin y super_admin
    layout: 'admin'
  }
}
  
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router