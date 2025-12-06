// router/index.js - Versión simplificada
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/login', 
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/healthcheck',
    name: 'HealthCheck', 
    component: () => import('../views/HealthCheckView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
    meta: { public: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router