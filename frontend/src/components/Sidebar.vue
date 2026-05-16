<template>
  <!-- Overlay móvil -->
  <div v-if="mobileOpen" class="sidebar-overlay" @click="mobileOpen = false"></div>

  <aside :class="['sidebar', { 'collapsed': collapsed, 'mobile-open': mobileOpen }]">

    <!-- ══ HEADER ══ -->
    <div class="sidebar-header">
      <div class="logo" @click="!collapsed && irInicio()">
        <div class="logo-mark">
          <span class="logo-letter">B</span>
        </div>
        <transition name="fade-text">
          <div v-if="!collapsed" class="logo-text-wrap">
            <span class="logo-name">Biblioteca</span>
            <span class="logo-sub">VDJ</span>
          </div>
        </transition>
      </div>
      <button class="toggle-btn" @click="toggleCollapse" :title="collapsed ? 'Expandir' : 'Colapsar'">
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path v-if="!collapsed" stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
          <path v-else stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
        </svg>
      </button>
    </div>

    <!-- ══ PERFIL ══ -->
    <div v-if="auth.user" class="user-profile">
      <div class="avatar" :title="auth.userName">{{ getUserInitials(auth.userName) }}</div>
      <transition name="fade-text">
        <div v-if="!collapsed" class="user-info">
          <div class="user-name">{{ auth.userName }}</div>
          <div class="user-role">
            <span class="role-dot" :class="`dot-nivel-${auth.tipoUsuarioId}`"></span>
            {{ getRoleName(auth.tipoUsuarioId) }}
          </div>
        </div>
      </transition>
    </div>

    <!-- ══ NAV ══ -->
    <nav class="sidebar-nav" role="navigation">

      <!-- NIVEL 1+: Recursos -->
      <SectionLabel :collapsed="collapsed" label="Recursos" />
      <div class="nav-group">
        <NavItem to="/catalogo" :collapsed="collapsed" @click="handleNavClick">
          <template #icon>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
          </template>
          Catálogo de Libros
        </NavItem>

        <NavItem to="/areas-estudio" :collapsed="collapsed" @click="handleNavClick">
          <template #icon>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </template>
          Cubículos
        </NavItem>

        <NavItem to="/laptops" :collapsed="collapsed" @click="handleNavClick">
          <template #icon>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
          </template>
          Laptops
        </NavItem>
      </div>

      <!-- NIVEL 1+: Mi cuenta -->
      <SectionLabel :collapsed="collapsed" label="Mi cuenta" />
      <div class="nav-group">
        <NavItem to="/perfil" :collapsed="collapsed" @click="handleNavClick">
          <template #icon>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
          </template>
          Mi Perfil
        </NavItem>

        <NavItem to="/mis-multas" :collapsed="collapsed" @click="handleNavClick">
          <template #icon>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
            </svg>
          </template>
          Mis Multas
        </NavItem>
      </div>

      <!-- NIVEL 2+: Préstamos (Bibliotecarios) -->
      <template v-if="auth.esCualquierAdmin">
        <SectionLabel :collapsed="collapsed" label="Préstamos" />
        <div class="nav-group">
          <NavItem to="/admin/devoluciones-pendientes" :collapsed="collapsed" @click="handleNavClick">
            <template #icon>
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/>
              </svg>
            </template>
            Devoluciones
          </NavItem>

          <NavItem to="/admin/multas" :collapsed="collapsed" @click="handleNavClick">
            <template #icon>
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
            </template>
            Multas
          </NavItem>
        </div>
      </template>

      <!-- NIVEL 3+: Administración de recursos -->
      <template v-if="auth.puedeGestionarRecursos">
        <SectionLabel :collapsed="collapsed" label="Administración" />
        <div class="nav-group">
          <NavItem to="/admin/libros/crear" :collapsed="collapsed" @click="handleNavClick">
            <template #icon>
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
              </svg>
            </template>
            Nuevo Libro
          </NavItem>

          <NavItem to="/admin/mobiliario" :collapsed="collapsed" @click="handleNavClick">
            <template #icon>
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
              </svg>
            </template>
            Mobiliario
          </NavItem>

          <NavItem to="/admin/areas" :collapsed="collapsed" @click="handleNavClick">
            <template #icon>
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
            </template>
            Gestión de Áreas
          </NavItem>

          <NavItem to="/admin/solicitudes-areas" :collapsed="collapsed" @click="handleNavClick">
            <template #icon>
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
              </svg>
            </template>
            Solicitudes Áreas
          </NavItem>
        </div>
      </template>

      <!-- NIVEL 4: Super Admin -->
      <template v-if="auth.esSuperAdmin">
        <SectionLabel :collapsed="collapsed" label="Super Admin" />
        <div class="nav-group">
          <NavItem to="/admin/usuarios" :collapsed="collapsed" @click="handleNavClick">
            <template #icon>
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </template>
            Usuarios
          </NavItem>
        </div>
      </template>

    </nav>

    <!-- ══ LOGOUT ══ -->
    <div class="sidebar-bottom">
      <button v-if="auth.isAuthenticated" class="logout-btn" @click="logout" :title="collapsed ? 'Cerrar Sesión' : ''">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
        </svg>
        <transition name="fade-text">
          <span v-if="!collapsed" class="logout-text">Cerrar Sesión</span>
        </transition>
      </button>
      <transition name="fade-text">
        <div v-if="!collapsed" class="sidebar-version">v1.0.0</div>
      </transition>
    </div>

  </aside>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth   = useAuthStore()
const router = useRouter()
const route  = useRoute()

const collapsed  = ref(false)
const mobileOpen = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('sidebarCollapsed')
  if (saved !== null) collapsed.value = JSON.parse(saved)
})
watch(collapsed, val => localStorage.setItem('sidebarCollapsed', JSON.stringify(val)))
watch(() => route.path, () => { mobileOpen.value = false })

defineExpose({ mobileOpen })

const toggleCollapse = () => { collapsed.value = !collapsed.value }
const handleNavClick = () => { if (window.innerWidth < 768) mobileOpen.value = false }

const irInicio = () => {
  const nivel = auth.tipoUsuarioId
  router.push(nivel >= 1 ? '/catalogo' : '/')
}

const logout = () => { auth.logout(); router.push('/login') }

const getUserInitials = (name) => {
  if (!name) return 'US'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().substring(0, 2)
}

const getRoleName = (tipo) => ({
  1: 'Estudiante',
  2: 'Bibliotecario',
  3: 'Admin. Avanzado',
  4: 'Super Admin'
}[tipo] || 'Usuario')
</script>

<script>
import { defineComponent, h, resolveComponent } from 'vue'

export const NavItem = defineComponent({
  name: 'NavItem',
  props: { to: { type: String, required: true }, collapsed: { type: Boolean, default: false } },
  emits: ['click'],
  setup(props, { slots, emit }) {
    return () => h(
      resolveComponent('RouterLink'),
      { to: props.to, class: 'nav-link', activeClass: 'nav-link-active', onClick: () => emit('click') },
      () => [
        h('span', { class: 'nav-item-icon' }, slots.icon?.()),
        !props.collapsed ? h('span', { class: 'nav-item-text' }, slots.default?.()) : null
      ]
    )
  }
})

export const SectionLabel = defineComponent({
  name: 'SectionLabel',
  props: { label: { type: String, required: true }, collapsed: { type: Boolean, default: false } },
  setup(props) {
    return () => h(
      'div',
      { class: ['nav-section', { 'nav-section-collapsed': props.collapsed }] },
      props.collapsed ? h('div', { class: 'section-line' }) : h('span', { class: 'section-label' }, props.label)
    )
  }
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

:root {
  --green-dark:  #1a4731; --green-mid:   #2d6a4f;
  --green-light: #52b788; --gold-mid:    #c9900c;
  --gold-light:  #f4c542; --sidebar-w:   252px;
  --sidebar-col: 68px;
}

.sidebar {
  width: var(--sidebar-w); height: 100vh;
  position: fixed; left: 0; top: 0; z-index: 1000;
  display: flex; flex-direction: column;
  transition: width .28s cubic-bezier(.4,0,.2,1);
  font-family: 'DM Sans', sans-serif;
  background-image:
    url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E"),
    linear-gradient(175deg, #1a4731 0%, #162d23 60%, #0f1f18 100%);
  border-right: 1px solid rgba(255,255,255,.07);
  box-shadow: 4px 0 24px rgba(0,0,0,.25);
  overflow: hidden;
}
.sidebar.collapsed { width: var(--sidebar-col); }

.sidebar-overlay {
  position: fixed; inset: 0;
  background: rgba(26,47,26,.55); backdrop-filter: blur(3px); z-index: 999;
}

.sidebar-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.25rem 1rem 1rem;
  border-bottom: 1px solid rgba(255,255,255,.07); flex-shrink: 0;
}
.logo { display: flex; align-items: center; gap: .625rem; cursor: pointer; overflow: hidden; min-width: 0; }
.logo-mark { width: 34px; height: 34px; background: linear-gradient(135deg, var(--gold-light), var(--gold-mid)); border-radius: 9px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(244,197,66,.3); flex-shrink: 0; }
.logo-letter { font-family: 'Playfair Display', serif; font-size: 1.1rem; font-weight: 700; color: #1a4731; line-height: 1; }
.logo-text-wrap { display: flex; flex-direction: column; overflow: hidden; }
.logo-name { font-family: 'Playfair Display', serif; font-size: .95rem; font-weight: 700; color: #fff; line-height: 1.1; white-space: nowrap; }
.logo-sub  { font-size: .6rem; font-weight: 600; color: var(--gold-light); letter-spacing: .18em; text-transform: uppercase; }
.toggle-btn { width: 28px; height: 28px; background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.1); border-radius: 7px; color: rgba(255,255,255,.6); cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: background .2s, color .2s; }
.toggle-btn:hover { background: rgba(255,255,255,.14); color: #fff; }

.user-profile { display: flex; align-items: center; gap: .75rem; padding: .875rem 1rem; border-bottom: 1px solid rgba(255,255,255,.07); flex-shrink: 0; overflow: hidden; }
.avatar { width: 34px; height: 34px; background: linear-gradient(135deg, var(--green-light), var(--green-mid)); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: .75rem; font-weight: 700; color: #fff; flex-shrink: 0; border: 2px solid rgba(255,255,255,.12); }
.user-info { overflow: hidden; min-width: 0; }
.user-name { font-size: .82rem; font-weight: 600; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { display: flex; align-items: center; gap: .35rem; font-size: .7rem; color: rgba(255,255,255,.5); white-space: nowrap; }
.role-dot    { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
.dot-nivel-1 { background: var(--green-light); }
.dot-nivel-2 { background: #60a5fa; }
.dot-nivel-3 { background: var(--gold-light); }
.dot-nivel-4 { background: #f87171; }

.sidebar-nav { flex: 1; overflow-y: auto; overflow-x: hidden; padding: .75rem 0; }
.sidebar-nav::-webkit-scrollbar { width: 3px; }
.sidebar-nav::-webkit-scrollbar-track { background: transparent; }
.sidebar-nav::-webkit-scrollbar-thumb { background: rgba(255,255,255,.12); border-radius: 2px; }
.nav-group { padding: 0 .625rem; margin-bottom: .25rem; }

:deep(.nav-link) { display: flex; align-items: center; gap: .625rem; padding: .55rem .75rem; color: rgba(255,255,255,.62); text-decoration: none; border-radius: 9px; font-size: .82rem; font-weight: 500; transition: background .18s, color .18s; white-space: nowrap; overflow: hidden; }
:deep(.nav-link:hover) { background: rgba(255,255,255,.08); color: #fff; }
:deep(.nav-link-active) { background: rgba(244,197,66,.12); color: var(--gold-light) !important; border-left: 2px solid var(--gold-light); padding-left: calc(.75rem - 2px); }
:deep(.nav-link-active .nav-item-icon) { color: var(--gold-light); }
:deep(.nav-item-icon) { display: flex; flex-shrink: 0; color: rgba(255,255,255,.5); transition: color .18s; width: 16px; }
:deep(.nav-link:hover .nav-item-icon) { color: rgba(255,255,255,.9); }
:deep(.nav-item-text) { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
:deep(.nav-section) { padding: .875rem .625rem .3rem 1.25rem; }
:deep(.section-label) { font-size: .67rem; font-weight: 700; color: rgba(255,255,255,.28); text-transform: uppercase; letter-spacing: .1em; white-space: nowrap; }
:deep(.nav-section-collapsed) { padding: .5rem .625rem; }
:deep(.section-line) { height: 1px; background: rgba(255,255,255,.08); border-radius: 1px; }

.sidebar-bottom { padding: .75rem .625rem; border-top: 1px solid rgba(255,255,255,.07); flex-shrink: 0; display: flex; align-items: center; justify-content: space-between; gap: .5rem; }
.logout-btn { display: flex; align-items: center; gap: .625rem; padding: .55rem .75rem; background: none; border: none; border-radius: 9px; color: rgba(248,113,113,.75); font-family: 'DM Sans', sans-serif; font-size: .82rem; font-weight: 500; cursor: pointer; transition: background .18s, color .18s; white-space: nowrap; overflow: hidden; flex: 1; }
.logout-btn:hover { background: rgba(248,113,113,.1); color: #f87171; }
.logout-text { overflow: hidden; text-overflow: ellipsis; }
.sidebar-version { font-size: .65rem; color: rgba(255,255,255,.2); font-family: monospace; flex-shrink: 0; white-space: nowrap; }

.fade-text-enter-active { transition: opacity .18s ease, width .28s ease; }
.fade-text-leave-active { transition: opacity .1s ease, width .28s ease; }
.fade-text-enter-from, .fade-text-leave-to { opacity: 0; }

@media (max-width: 768px) {
  .sidebar { width: 280px !important; transform: translateX(-100%); transition: transform .28s cubic-bezier(.4,0,.2,1); }
  .sidebar.mobile-open { transform: translateX(0); }
  .toggle-btn { display: none; }
}
</style>