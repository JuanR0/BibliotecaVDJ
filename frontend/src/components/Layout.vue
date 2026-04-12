<template>
  <div class="layout">

    <!-- Sidebar -->
    <Sidebar ref="sidebarRef" />

    <!-- Contenido principal -->
    <main
      class="main-content"
      :class="{ 'sidebar-collapsed': isCollapsed }"
    >

      <!-- ══ Header móvil con hamburguesa ══ -->
      <header class="mobile-header">
        <button
          class="hamburger"
          @click="openSidebar"
          aria-label="Abrir menú"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <div class="mobile-brand">
          <span class="mobile-brand-letter">B</span>
          <span class="mobile-brand-name">Biblioteca VDJ</span>
        </div>

        <div class="mobile-avatar" v-if="auth.user">
          {{ getUserInitials(auth.userName) }}
        </div>
      </header>

      <!-- ══ Vista actual ══ -->
      <div class="content-wrapper">
        <slot></slot>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Sidebar from './Sidebar.vue'

const auth     = useAuthStore()
const route    = useRoute()
const sidebarRef = ref(null)

// Lee el estado colapsado del sidebar desde localStorage
const isCollapsed = computed(() => {
  const saved = localStorage.getItem('sidebarCollapsed')
  return saved ? JSON.parse(saved) : false
})

// Abre el drawer en móvil
const openSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.mobileOpen = true
  }
}

const getUserInitials = name => {
  if (!name) return 'US'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().substring(0, 2)
}

// Cerrar drawer al cambiar ruta en móvil
watch(() => route.path, () => {
  if (window.innerWidth < 768 && sidebarRef.value) {
    sidebarRef.value.mobileOpen = false
  }
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@500;600&display=swap');

/* ── Layout base ─────────────────────────────────────────────────────────── */
.layout {
  display: flex;
  min-height: 100vh;
  background:
    radial-gradient(ellipse 70% 40% at 10% 0%, rgba(82,183,136,.08) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 90% 100%, rgba(201,144,12,.07) 0%, transparent 50%),
    #f5f0e8;
}

/* ── Contenido principal ─────────────────────────────────────────────────── */
.main-content {
  flex: 1;
  margin-left: 252px;
  transition: margin-left .28s cubic-bezier(.4,0,.2,1);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content.sidebar-collapsed {
  margin-left: 68px;
}

/* ── Mobile header ───────────────────────────────────────────────────────── */
.mobile-header {
  display: none;
  align-items: center;
  gap: .75rem;
  padding: .875rem 1.25rem;
  background: linear-gradient(135deg, #1a4731 0%, #2d6a4f 100%);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 12px rgba(26,71,49,.2);
}

/* Hamburguesa — tres líneas animadas */
.hamburger {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
  width: 36px; height: 36px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 8px;
  cursor: pointer;
  padding: 0 9px;
  flex-shrink: 0;
  transition: background .2s;
}
.hamburger:hover { background: rgba(255,255,255,0.18); }
.hamburger span {
  display: block;
  height: 2px;
  background: rgba(255,255,255,0.9);
  border-radius: 2px;
  transition: transform .2s;
}

/* Brand en móvil */
.mobile-brand {
  flex: 1;
  display: flex;
  align-items: center;
  gap: .5rem;
}
.mobile-brand-letter {
  width: 28px; height: 28px;
  background: linear-gradient(135deg, #f4c542, #c9900c);
  border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Playfair Display', serif;
  font-size: .95rem; font-weight: 700;
  color: #1a4731;
  flex-shrink: 0;
}
.mobile-brand-name {
  font-family: 'Playfair Display', serif;
  font-size: .95rem; font-weight: 700;
  color: #fff;
  white-space: nowrap;
}

/* Avatar móvil */
.mobile-avatar {
  width: 32px; height: 32px;
  background: linear-gradient(135deg, #52b788, #2d6a4f);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: 'DM Sans', sans-serif;
  font-size: .7rem; font-weight: 700;
  color: #fff;
  border: 2px solid rgba(255,255,255,0.2);
  flex-shrink: 0;
}

/* ── Content wrapper ─────────────────────────────────────────────────────── */
.content-wrapper {
  flex: 1;
  padding: 1.5rem;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

/* ══════════════════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════════════════ */

/* Tablet — sidebar colapsa automáticamente */
@media (min-width: 769px) and (max-width: 1024px) {
  .main-content {
    margin-left: 68px !important;
  }
}

/* Móvil — sidebar es drawer, main ocupa todo */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0 !important;
  }

  .mobile-header {
    display: flex;
  }

  .content-wrapper {
    padding: 1rem;
  }
}

@media (max-width: 420px) {
  .content-wrapper {
    padding: .75rem;
  }
  .mobile-brand-name {
    font-size: .85rem;
  }
}
</style>