import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// ── Vistas públicas ────────────────────────────────────────────────────────
import LandingPage  from '@/views/LandingPage.vue'
import LoginView    from '@/views/auth/LoginView.vue'
import HealthCheck  from '@/views/HealthCheckView.vue'
import NotFound     from '@/views/NotFoundView.vue'

// ── Nivel 1: Estudiante ───────────────────────────────────────────────────
import BookCatalog  from '@/views/user/CatalogoLibros.vue'
import AreasEstudio from '@/views/user/AreasEstudio.vue'
import LaptopsView  from '@/views/user/Laptops.vue'
import MisMultas    from '@/views/user/MisMultas.vue'
import UserMenu     from '@/views/user/UserMenu.vue'

// ── Nivel 2: Bibliotecario ────────────────────────────────────────────────
import MultasPendientes       from '@/views/admin/MultasPendientes.vue'
import GestionPrestamos       from '@/views/admin/PrestamoLibros.vue'
import PrestamoEquiposComputo from '@/views/admin/PrestamoEquiposComputo.vue'
import PrestamoAreas          from '@/views/admin/PrestamoAreas.vue'

// ── Nivel 3: Admin Avanzado ───────────────────────────────────────────────
import FurnitureManagement from '@/views/admin/FurnitureManagement.vue'
import AreasManagement    from '@/views/admin/AreasManagement.vue'

// ── Nivel 4: Super Admin ──────────────────────────────────────────────────
import UserManagement from '@/views/SuperAdmin/UserManagement.vue'

// ══════════════════════════════════════════════════════════════════════════
// RUTAS
// Meta flags:
//   public: true          → sin autenticación
//   minLevel: N           → requiere tipoUsuarioId >= N
//   exactLevel: N         → requiere tipoUsuarioId === N
// ══════════════════════════════════════════════════════════════════════════
const routes = [

  // ── Públicas ─────────────────────────────────────────────────────────────
  {
    path: '/',
    name: 'Landing',
    component: LandingPage,
    meta: { public: true, title: 'Bienvenido — BiblioVDJ' }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { public: true, title: 'Iniciar Sesión' }
  },
  {
    path: '/health',
    name: 'HealthCheck',
    component: HealthCheck,
    meta: { public: true }
  },

  // ── Nivel 1: Estudiante ───────────────────────────────────────────────────
  {
    path: '/catalogo',
    name: 'BookCatalog',
    component: BookCatalog,
    meta: { minLevel: 1, title: 'Catálogo de Libros' }
  },
  {
    path: '/areas-estudio',
    name: 'AreasEstudio',
    component: AreasEstudio,
    meta: { minLevel: 1, title: 'Áreas de Estudio' }
  },
  {
    path: '/laptops',
    name: 'LaptopsView',
    component: LaptopsView,
    meta: { minLevel: 1, title: 'Laptops Disponibles' }
  },
  {
    path: '/mis-multas',
    name: 'MisMultas',
    component: MisMultas,
    meta: { minLevel: 1, title: 'Mis Multas' }
  },
  {
    path: '/perfil',
    name: 'UserMenu',
    component: UserMenu,
    meta: { minLevel: 1, title: 'Mi Perfil' }
  },

  // ── Nivel 2: Bibliotecario ────────────────────────────────────────────────

  // router
  { 
    path: '/admin/prestamos', 
    name: 'GestionPrestamos', 
    component: GestionPrestamos, 
    meta: { minLevel: 2, title: 'Gestión de Préstamos' } 
  
  },

  {
    path: '/admin/multas',
    name: 'MultasPendientes',
    component: MultasPendientes,
    meta: { minLevel: 2, title: 'Gestión de Multas' }
  },
  { 
    path: '/admin/prestamos/equipos', 
    name: 'GestionPrestamosEquipos', 
    component: PrestamoEquiposComputo, 
    meta: { minLevel: 2 } 
  },
  
  { 
    path: '/admin/prestamos/areas',   
    name: 'GestionPrestamosAreas',   
    component: PrestamoAreas,   
    meta: { minLevel: 2 } 
  },

  // ── Nivel 3: Admin Avanzado ───────────────────────────────────────────────
  {
    path: '/admin/mobiliario',
    name: 'FurnitureManagement',
    component: FurnitureManagement,
    meta: { minLevel: 3, title: 'Gestión de Mobiliario' }
  },
  {
    path: '/admin/areas',
    name: 'AreasManagement',
    component: AreasManagement,
    meta: { minLevel: 3, title: 'Gestión de Áreas' }
  },

  // ── Nivel 4: Super Admin ──────────────────────────────────────────────────
  {
    path: '/admin/usuarios',
    name: 'UserManagement',
    component: UserManagement,
    meta: { minLevel: 4, title: 'Gestión de Usuarios' }
  },

  // ── 404 ───────────────────────────────────────────────────────────────────
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { public: true, title: 'Página no encontrada' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  }
})

// ══════════════════════════════════════════════════════════════════════════
// GUARD GLOBAL — lógica centralizada y simple
// ══════════════════════════════════════════════════════════════════════════
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // Inicializar una sola vez
  if (!auth.isInitialized) await auth.initializeAuth()

  // Title
  document.title = to.meta.title ? `${to.meta.title} | BiblioVDJ` : 'BiblioVDJ'

  // 1. Ruta pública → siempre pasar
  if (to.meta.public) return next()

  // 2. Evitar que usuario autenticado vaya a login
  if (to.name === 'Login' && auth.isAuthenticated) return next('/catalogo')

  // 3. Ruta protegida sin sesión → login
  if (!auth.isAuthenticated) return next({ name: 'Login', query: { redirect: to.fullPath } })

  // 4. Verificar nivel mínimo requerido
  if (to.meta.minLevel && auth.tipoUsuarioId < to.meta.minLevel) {
    console.warn(`Nivel requerido: ${to.meta.minLevel}, nivel actual: ${auth.tipoUsuarioId}`)
    return next(getRutaHome(auth.tipoUsuarioId))
  }

  // 5. Verificar nivel exacto
  if (to.meta.exactLevel && auth.tipoUsuarioId !== to.meta.exactLevel) {
    return next(getRutaHome(auth.tipoUsuarioId))
  }

  next()
})

// Ruta de inicio según nivel del usuario
function getRutaHome(nivel) {
  switch (nivel) {
    case 1:  return '/catalogo'
    case 2:  return '/admin/devoluciones-pendientes'
    case 3:  return '/admin/areas'
    case 4:  return '/admin/usuarios'
    default: return '/login'
  }
}

export default router