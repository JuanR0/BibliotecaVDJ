<template>
  <div class="landing">

    <!-- ══ NAVBAR ══ -->
    <nav class="navbar">
      <div class="nav-brand">
        <div class="brand-mark">B</div>
        <div class="brand-text">
          <span class="brand-name">Biblioteca</span>
          <span class="brand-sub">VDJ · CID</span>
        </div>
      </div>
    </nav>

    <!-- ══ HERO ══ -->
    <section class="hero">
      <!-- Imagen de fondo: estanterías Unsplash NIJuEQw0RKg -->
      <div class="hero-bg" :style="{ backgroundImage: `url(${bgUrl})` }"></div>
      <div class="hero-overlay"></div>

      <div class="hero-content">
        <!-- Chip institucional -->
        <div class="hero-chip">
          <span class="chip-dot"></span>
          Centro Integral de Documentación
        </div>

        <!-- Título -->
        <h1 class="hero-titulo">
          Biblioteca<br>
          <span class="titulo-accent">Universitaria</span><br>
          <span class="titulo-light">VDJ</span>
        </h1>

        <p class="hero-desc">
          Consulta nuestro acervo bibliográfico, verifica la disponibilidad de cubículos
          y laptops, o inicia sesión para acceder a todos los recursos del CID.
        </p>

        <!-- Stats rápidos -->
        <!-- REEMPLAZA hero-stats por esto -->
        <div class="hero-cta-unico">
          <router-link to="/catalogo" class="cta-primary">
            <svg width="17" height="17" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
            Ver catálogo
          </router-link>
        </div>

        <div class="hero-stats">
          <div class="hero-stat"><span class="hs-num">{{ stats.libros }}</span><span class="hs-lbl">Títulos</span></div>
          <div class="hs-sep"></div>
          <div class="hero-stat"><span class="hs-num">{{ stats.cubiculos }}</span><span class="hs-lbl">Cubículos</span></div>
          <div class="hs-sep"></div>
          <div class="hero-stat"><span class="hs-num">{{ stats.laptops }}</span><span class="hs-lbl">Laptops</span></div>
        </div>
      </div>

      <!-- Decorativo — scroll hint -->
      <div class="scroll-hint">
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
      </div>
    </section>

    <!-- ══ FEATURES ══ -->
    <section class="features">
      <div class="features-inner">
        <div class="feature-card">
          <div class="feature-ico">
            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
          </div>
          <h3>Catálogo digital</h3>
          <p>Consulta el acervo completo de la biblioteca sin necesidad de iniciar sesión.</p>
        </div>

        <div class="feature-card">
          <div class="feature-ico">
            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <h3>Cubículos</h3>
          <p>Verifica en tiempo real la disponibilidad de espacios de estudio individual y grupal.</p>
        </div>

        <div class="feature-card">
          <div class="feature-ico">
            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
          </div>
          <h3>Laptops</h3>
          <p>Consulta qué laptops están disponibles para préstamo en el CID.</p>
        </div>
      </div>
    </section>

    <!-- ══ FOOTER ══ -->
    <footer class="footer">
      <span>© {{ new Date().getFullYear() }} Biblioteca VDJ · Centro Integral de Documentación</span>
    </footer>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { bookService } from '@/services/books'

// URL directa de Unsplash (foto: NIJuEQw0RKg — estanterías de libros)
const bgUrl = 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1800&q=80&fit=crop'

const stats = ref({ libros: '—', cubiculos: '—', laptops: '—' })

// Carga stats básicos sin autenticación si el backend lo permite
// Si el endpoint requiere auth, simplemente muestra valores decorativos
const cargarStats = async () => {
  try {
    const r = await bookService.getBooks()
    const libros = r?.libros ?? (Array.isArray(r) ? r : [])
    stats.value.libros     = libros.length || '+'
    stats.value.cubiculos  = 8   // estático por ahora — ajusta cuando tengas endpoint público
    stats.value.laptops    = 15  // estático por ahora
  } catch {
    // Si no hay endpoint público, mostrar valores decorativos
    stats.value = { libros: '+500', cubiculos: 8, laptops: 15 }
  }
}

onMounted(cargarStats)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=DM+Sans:wght@400;500;600&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

.landing {
  font-family: 'DM Sans', sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0f1f18;
}

/* ── Navbar ──────────────────────────────────────────────────────────────── */
.navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 2.5rem;
  background: rgba(15, 31, 24, 0.75);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255,255,255,.07);
}

.nav-brand { display: flex; align-items: center; gap: .75rem; }
.brand-mark {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, #f4c542, #c9900c);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem; font-weight: 700; color: #1a4731;
}
.brand-name { display: block; font-family: 'Playfair Display', serif; font-size: 1rem; font-weight: 700; color: #fff; line-height: 1.1; }
.brand-sub  { display: block; font-size: .65rem; color: rgba(255,255,255,.4); letter-spacing: .12em; text-transform: uppercase; }

.nav-actions { display: flex; align-items: center; gap: .75rem; }

.btn-catalogo {
  display: flex; align-items: center; gap: .4rem;
  padding: .45rem 1rem;
  background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.12);
  border-radius: 8px; color: rgba(255,255,255,.75);
  font-family: 'DM Sans', sans-serif; font-size: .82rem; font-weight: 500;
  text-decoration: none; transition: all .2s;
}
.btn-catalogo:hover { background: rgba(255,255,255,.14); color: #fff; }

.btn-login {
  display: flex; align-items: center; gap: .4rem;
  padding: .45rem 1.1rem;
  background: linear-gradient(135deg, #f4c542, #c9900c);
  border: none; border-radius: 8px;
  color: #1a4731; font-family: 'DM Sans', sans-serif;
  font-size: .82rem; font-weight: 700;
  text-decoration: none; transition: all .2s;
  box-shadow: 0 4px 14px rgba(244,197,66,.25);
}
.btn-login:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(244,197,66,.4); }

/* ── Hero ────────────────────────────────────────────────────────────────── */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute; inset: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  transform: scale(1.05);
  transition: transform 8s ease;
}
.hero:hover .hero-bg { transform: scale(1.0); }

/* Overlay verde oscuro semitransparente */
.hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(
    135deg,
    rgba(15, 31, 24, 0.88) 0%,
    rgba(26, 71, 49, 0.80) 50%,
    rgba(15, 31, 24, 0.70) 100%
  );
}

.hero-content {
  position: relative; z-index: 1;
  max-width: 680px;
  padding: 2rem;
  text-align: left;
  margin-left: 8vw;
}

.hero-chip {
  display: inline-flex; align-items: center; gap: .5rem;
  padding: .35rem .875rem;
  background: rgba(82, 183, 136, .15);
  border: 1px solid rgba(82, 183, 136, .25);
  border-radius: 20px;
  font-size: .75rem; font-weight: 600; color: #52b788;
  letter-spacing: .08em; text-transform: uppercase;
  margin-bottom: 1.5rem;
}
.chip-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #52b788;
  box-shadow: 0 0 6px rgba(82,183,136,.6);
  animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: .4; } }

.hero-titulo {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.8rem, 6vw, 5rem);
  font-weight: 700;
  color: #fff;
  line-height: 1.05;
  margin-bottom: 1.25rem;
}
.titulo-accent { color: #f4c542; }
.titulo-light  { font-weight: 600; font-style: italic; color: rgba(255,255,255,.65); }

.hero-desc {
  font-size: 1rem; line-height: 1.7;
  color: rgba(255,255,255,.65);
  margin-bottom: 2rem;
  max-width: 480px;
}

.hero-ctas {
  display: flex; gap: 1rem; flex-wrap: wrap;
  margin-bottom: 2.5rem;
}

.cta-primary {
  display: inline-flex; align-items: center; gap: .5rem;
  padding: .875rem 2rem;
  background: linear-gradient(135deg, #f4c542, #c9900c);
  border: none; border-radius: 12px;
  color: #1a4731; font-family: 'DM Sans', sans-serif;
  font-size: .95rem; font-weight: 700;
  text-decoration: none;
  box-shadow: 0 8px 24px rgba(244,197,66,.3);
  transition: all .2s;
}
.cta-primary:hover { transform: translateY(-2px); box-shadow: 0 12px 32px rgba(244,197,66,.45); }

.cta-secondary {
  display: inline-flex; align-items: center; gap: .5rem;
  padding: .875rem 2rem;
  background: rgba(255,255,255,.08);
  border: 1.5px solid rgba(255,255,255,.2);
  border-radius: 12px;
  color: #fff; font-family: 'DM Sans', sans-serif;
  font-size: .95rem; font-weight: 600;
  text-decoration: none; transition: all .2s;
}
.cta-secondary:hover { background: rgba(255,255,255,.14); border-color: rgba(255,255,255,.35); }

/* Stats */
.hero-stats {
  display: flex; align-items: center; gap: 1.5rem;
}
.hero-stat { display: flex; flex-direction: column; }
.hs-num { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: #fff; line-height: 1; }
.hs-lbl { font-size: .72rem; color: rgba(255,255,255,.45); text-transform: uppercase; letter-spacing: .08em; margin-top: 2px; }
.hs-sep { width: 1px; height: 36px; background: rgba(255,255,255,.15); }

/* Scroll hint */
.scroll-hint {
  position: absolute; bottom: 2rem; left: 50%;
  transform: translateX(-50%);
  color: rgba(255,255,255,.3);
  animation: bounce 2s infinite;
}
@keyframes bounce { 0%,100% { transform: translateX(-50%) translateY(0); } 50% { transform: translateX(-50%) translateY(6px); } }

/* ── Features ────────────────────────────────────────────────────────────── */
.features {
  background: #f5f0e8;
  padding: 5rem 2rem;
}

.features-inner {
  max-width: 960px; margin: 0 auto;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  background: #fffef9;
  border: 1.5px solid #d4e8da;
  border-radius: 16px;
  padding: 1.875rem;
  box-shadow: 0 2px 12px rgba(26,47,26,.07);
  transition: transform .2s, box-shadow .2s;
}
.feature-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(26,71,49,.12); }

.feature-ico {
  width: 48px; height: 48px;
  background: #d8f3dc;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #2d6a4f; margin-bottom: 1rem;
}

.feature-card h3 {
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem; font-weight: 700;
  color: #1a4731; margin-bottom: .5rem;
}
.feature-card p {
  font-size: .875rem; line-height: 1.6; color: #5a7a5a;
}

/* ── Footer ──────────────────────────────────────────────────────────────── */
.footer {
  background: #0f1f18;
  padding: 1.25rem 2.5rem;
  text-align: center;
  font-size: .78rem;
  color: rgba(255,255,255,.3);
}

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .navbar { padding: .875rem 1.25rem; }
  .btn-catalogo { display: none; }
  .hero-content { margin-left: 0; text-align: center; align-items: center; display: flex; flex-direction: column; }
  .hero-ctas    { justify-content: center; }
  .hero-stats   { justify-content: center; }
  .hero-desc    { text-align: center; }
  .features     { padding: 3rem 1.25rem; }
}

.hero-cta-unico {
  margin-bottom: 2rem;
}
</style>