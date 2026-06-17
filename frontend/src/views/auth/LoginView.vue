<template>
  <div class="login-page">

    <!-- Fondo animado — mismo estilo orgánico que BookCatalog -->
    <div class="bg-layer" aria-hidden="true">
      <div class="bg-orb bg-orb-1"></div>
      <div class="bg-orb bg-orb-2"></div>
      <div class="bg-orb bg-orb-3"></div>
    </div>

    <div class="login-card">

      <!-- ══════════ PANEL IZQUIERDO — Branding ══════════ -->
      <div class="panel-brand">
        <!-- Patrón de puntos idéntico al BookCatalog header -->
        <div class="brand-pattern" aria-hidden="true"></div>

        <div class="brand-inner">
          <!-- Logo -->
          <div class="brand-logo">
            <div class="logo-mark">
              <span class="logo-letter">B</span>
            </div>
            <div class="logo-text-wrap">
              <span class="logo-name">Biblioteca</span>
              <span class="logo-sub">VDJ</span>
            </div>
          </div>

          <!-- Divider dorado -->
          <div class="brand-divider"></div>

          <!-- Tagline tipográfico -->
          <!-- <p class="brand-tagline">
            Gestiona préstamos,<br>
            explora el catálogo<br>
            y disfruta la lectura.
          </p> -->

          <!-- Stats -->
          <!-- <div class="brand-stats">
            <div class="brand-stat">
              <span class="stat-val">∞</span>
              <span class="stat-lbl">Recursos</span>
            </div>
            <div class="brand-stat">
              <span class="stat-val">24/7</span>
              <span class="stat-lbl">Acceso</span>
            </div>
            <div class="brand-stat">
              <span class="stat-val">100%</span>
              <span class="stat-lbl">Digital</span>
            </div>
          </div> -->
        </div>
      </div>

      <!-- ══════════ PANEL DERECHO — Formulario ══════════ -->
      <div class="panel-form">

        <!-- Tabs -->
        <div class="tabs" role="tablist">
          <button
            class="tab"
            :class="{ 'tab-active': !isRegister }"
            @click="!isRegister || toggleMode()"
            role="tab"
          >Iniciar Sesión</button>
          <div class="tab-slider" :class="{ 'tab-slider-right': isRegister }"></div>
        </div>

        <!-- Título -->
        <div class="form-heading">
          <h2>{{ isRegister ? 'Crear cuenta' : 'Bienvenido de vuelta' }}</h2>
          <p>{{ isRegister ? 'Completa los datos para registrarte' : 'Ingresa tus credenciales para continuar' }}</p>
        </div>

        <!-- Formulario -->
        <form @submit.prevent="handleSubmit" class="form" novalidate autocomplete="off">

          <!-- Código universitario -->
          <div class="field">
            <label class="field-label" for="codigo">Código Universitario</label>
            <div class="field-wrap">
              <span class="field-ico">
                <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
              </span>
              <input
                id="codigo"
                v-model="form.codigo_universitario"
                type="text"
                placeholder="U20234567"
                :disabled="isLoading"
                maxlength="20"
                class="field-input"
                autocomplete="username"
              />
            </div>
          </div>

          <!-- Contraseña -->
          <div class="field">
            <label class="field-label" for="clave">Contraseña</label>
            <div class="field-wrap">
              <span class="field-ico">
                <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
              </span>
              <input
                ref="passwordInput"
                id="clave"
                v-model="form.clave_acceso"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Mínimo 6 caracteres"
                :disabled="isLoading"
                minlength="6"
                class="field-input field-input-pw"
                autocomplete="current-password"
              />
              <button
                type="button"
                class="btn-toggle-pw"
                @click="showPassword = !showPassword"
                :title="showPassword ? 'Ocultar' : 'Mostrar'"
              >
                <!-- Ojo abierto -->
                <svg v-if="!showPassword" width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <!-- Ojo tachado -->
                <svg v-else width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Campos extras de registro -->
          <transition name="slide-down">
            <div v-if="isRegister" class="register-extra">

              <div class="field">
                <label class="field-label" for="nombre">Nombre Completo</label>
                <div class="field-wrap">
                  <span class="field-ico">
                    <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0"/>
                    </svg>
                  </span>
                  <input
                    id="nombre"
                    v-model="form.nombre_completo"
                    type="text"
                    placeholder="Juan Pérez García"
                    :disabled="isLoading"
                    maxlength="255"
                    class="field-input"
                  />
                </div>
              </div>

              <div class="field">
                <label class="field-label" for="relacion">Relación Institucional</label>
                <div class="field-wrap">
                  <span class="field-ico">
                    <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                    </svg>
                  </span>
                  <select
                    id="relacion"
                    v-model="form.relacion_institucional_id"
                    :disabled="isLoading"
                    class="field-input field-select"
                  >
                    <option value="" disabled selected>Selecciona tu perfil</option>
                    <option v-for="r in relacionesInstitucionales" :key="r.id" :value="r.id">
                      {{ r.nombre }}
                    </option>
                  </select>
                </div>
              </div>

            </div>
          </transition>

          <!-- Mensajes -->
          <transition name="msg">
            <div v-if="errorMessage" class="msg msg-error" role="alert">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              {{ errorMessage }}
            </div>
          </transition>

          <transition name="msg">
            <div v-if="successMessage" class="msg msg-success" role="status">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
              {{ successMessage }}
            </div>
          </transition>

          <!-- Submit -->
          <button
            type="submit"
            class="btn-submit"
            :disabled="isLoading || !isFormValid"
          >
            <span v-if="isLoading" class="btn-spinner"></span>
            <span v-else class="btn-label">
              {{ isRegister ? 'Crear cuenta' : 'Ingresar' }}
              <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
              </svg>
            </span>
          </button>

        </form>

        <div class="form-footer">
          <button @click="$router.push('/')" class="btn-back">← Volver al inicio</button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Login',
  data() {
    return {
      isRegister: false,
      isLoading: false,
      showPassword: false,
      errorMessage: '',
      successMessage: '',
      relacionesInstitucionales: [
        { id: 1, nombre: 'Estudiante' },
        { id: 2, nombre: 'Docente' },
        { id: 3, nombre: 'Administrativo' },
        { id: 4, nombre: 'Investigador' },
        { id: 5, nombre: 'Externo' }
      ],
      form: {
        codigo_universitario: '',
        clave_acceso: '',
        nombre_completo: '',
        relacion_institucional_id: null
      }
    }
  },
  computed: {
    isFormValid() {
      if (this.isRegister) {
        return this.form.codigo_universitario &&
               this.form.clave_acceso &&
               this.form.nombre_completo &&
               this.form.relacion_institucional_id &&
               this.form.clave_acceso.length >= 6
      }
      return this.form.codigo_universitario && this.form.clave_acceso
    }
  },
  methods: {
    toggleMode() {
      this.isRegister = !this.isRegister
      this.errorMessage = ''
      this.successMessage = ''
      this.form.clave_acceso = ''
      if (!this.isRegister) {
        this.form.nombre_completo = ''
        this.form.relacion_institucional_id = null
      }
    },

    async handleSubmit(event) {
      if (event) event.preventDefault()
      if (this.isLoading) return
      this.isLoading = true
      this.errorMessage = ''
      this.successMessage = ''

      try {
        const authStore = useAuthStore()
        let result

        if (this.isRegister) {
          result = await authStore.register({
            codigo_universitario:      this.form.codigo_universitario.trim(),
            clave_acceso:              this.form.clave_acceso,
            nombre_completo:           this.form.nombre_completo.trim(),
            relacion_institucional_id: this.form.relacion_institucional_id
          })

          if (result.success) {
            this.successMessage = `¡Bienvenido ${authStore.userName}!`
            this.form.codigo_universitario = ''
            this.form.clave_acceso = ''
            setTimeout(() => this.redirectBasedOnUserType(authStore.tipoUsuarioId), 1500)
          } else {
            // Mantener código universitario — solo limpiar contraseña
            this.form.clave_acceso = ''
            this.errorMessage = result.error
          }

        } else {
          result = await authStore.login({
            codigo_universitario: this.form.codigo_universitario.trim(),
            clave_acceso:         this.form.clave_acceso
          })

          if (result.success) {
            this.successMessage = `¡Bienvenido, ${authStore.userName}!`
            this.form.codigo_universitario = ''
            this.form.clave_acceso = ''
            setTimeout(() => this.redirectBasedOnUserType(authStore.tipoUsuarioId), 1500)
          } else {
            // Restaurar código explícitamente + limpiar contraseña + foco
            this.form.clave_acceso = ''
            this.errorMessage = result.error
            this.$nextTick(() => this.$refs.passwordInput?.focus())
          }
        }

      } catch (error) {
        console.error('Error inesperado:', error)
        this.errorMessage = 'Error inesperado. Intenta nuevamente.'
        this.form.clave_acceso = ''
        // codigo_universitario NO se limpia — se mantiene siempre
      } finally {
        this.isLoading = false
      }
    },

    redirectBasedOnUserType(tipoUsuarioId) {
      this.$router.push('/catalogo')
    }
  }
}
</script>



<style scoped>
/* ── Fuentes — idénticas a BookCatalog ──────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

/* ── Variables — paleta BookCatalog ─────────────────────────────────────── */
:root {
  --green-dark:   #1a4731;
  --green-mid:    #2d6a4f;
  --green-light:  #52b788;
  --green-pale:   #d8f3dc;
  --gold-dark:    #92650a;
  --gold-mid:     #c9900c;
  --gold-light:   #f4c542;
  --gold-pale:    #fef9e7;
  --cream:        #f5f0e8;
  --cream-border: #d4e8da;
  --card-bg:      #fffef9;
  --shadow-md:    0 8px 32px rgba(26,71,49,.18);
}

/* ── Page — mismo fondo crema con gradientes orgánicos ──────────────────── */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
  font-family: 'DM Sans', sans-serif;
  background:
    radial-gradient(ellipse 70% 50% at 5%  0%,   rgba(82,183,136,.18) 0%, transparent 55%),
    radial-gradient(ellipse 55% 45% at 95% 100%,  rgba(201,144,12,.14) 0%, transparent 50%),
    radial-gradient(ellipse 40% 60% at 50% 50%,   rgba(26,71,49,.06)   0%, transparent 70%),
    #f5f0e8;
}

/* Orbes animados — misma paleta verde/dorada */
.bg-layer { position: fixed; inset: 0; pointer-events: none; z-index: 0; }

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
}
.bg-orb-1 {
  width: 520px; height: 520px;
  background: rgba(45, 106, 79, 0.22);
  top: -180px; left: -120px;
  animation: orbFloat 14s ease-in-out infinite;
}
.bg-orb-2 {
  width: 380px; height: 380px;
  background: rgba(201, 144, 12, 0.15);
  bottom: -120px; right: -80px;
  animation: orbFloat 18s ease-in-out infinite reverse;
}
.bg-orb-3 {
  width: 260px; height: 260px;
  background: rgba(82, 183, 136, 0.12);
  top: 45%; left: 40%;
  animation: orbFloat 10s ease-in-out infinite 3s;
}

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0); }
  50%       { transform: translate(24px, 18px); }
}

/* ── Card ───────────────────────────────────────────────────────────────── */
.login-card {
  position: relative; z-index: 1;
  display: flex;
  width: 100%;
  max-width: 900px;
  min-height: 560px;
  border-radius: 20px;
  overflow: hidden;
  border: 2px solid #b8d4c0;
  box-shadow:
    0 2px 0 rgba(255,255,255,.9) inset,
    0 12px 48px rgba(26,71,49,.18),
    0 2px 8px rgba(26,71,49,.10),
    0 0 0 1px rgba(26,71,49,.08);
  animation: cardIn .55s cubic-bezier(.22,1,.36,1) both;
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(24px) scale(.975); }
  to   { opacity: 1; transform: translateY(0)    scale(1); }
}

/* ══════════════════════════════════════════════════
   PANEL IZQUIERDO — verde oscuro, igual que el
   header de BookCatalog
══════════════════════════════════════════════════ */
.panel-brand {
  width: 42%;
  background: linear-gradient(145deg, #1a4731 0%, #2d6a4f 60%, #3a7d5e 100%);
  padding: 3rem 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* Patrón SVG idéntico al BookCatalog header */
.brand-pattern {
  position: absolute; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E");
  pointer-events: none;
}

.brand-inner {
  position: relative; z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  animation: brandIn .7s .15s cubic-bezier(.22,1,.36,1) both;
}
@keyframes brandIn {
  from { opacity: 0; transform: translateX(-18px); }
  to   { opacity: 1; transform: translateX(0); }
}

/* Logo */
.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.logo-mark {
  width: 48px; height: 48px;
  background: linear-gradient(135deg, var(--gold-light) 0%, var(--gold-mid) 100%);
  border-radius: 13px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 6px 20px rgba(244,197,66,.35);
  flex-shrink: 0;
}
.logo-letter {
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem; font-weight: 700;
  color: var(--green-dark); line-height: 1;
}

.logo-text-wrap { display: flex; flex-direction: column; }
.logo-name {
  font-family: 'Playfair Display', serif;
  font-size: 1.2rem; font-weight: 700;
  color: #fff; line-height: 1.15;
}
.logo-sub {
  font-size: 0.7rem; font-weight: 600;
  color: var(--gold-light);
  letter-spacing: 0.2em; text-transform: uppercase;
}

/* Divider dorado */
.brand-divider {
  width: 44px; height: 2px;
  background: linear-gradient(90deg, var(--gold-light), transparent);
  border-radius: 2px;
}

/* Tagline */
.brand-tagline {
  font-family: 'Playfair Display', serif;
  font-size: 1.3rem; font-weight: 600;
  color: rgba(255,255,255,.92);
  line-height: 1.65;
  letter-spacing: -.01em;
}

/* Stats */
.brand-stats {
  display: flex; gap: 1.5rem;
  padding-top: .25rem;
}
.brand-stat { display: flex; flex-direction: column; gap: 2px; }
.stat-val {
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem; font-weight: 700;
  color: var(--gold-light);
}
.stat-lbl {
  font-size: .67rem; font-weight: 600;
  color: rgba(255,255,255,.55);
  text-transform: uppercase; letter-spacing: .1em;
}

/* ══════════════════════════════════════════════════
   PANEL DERECHO — fondo crema claro, legible
══════════════════════════════════════════════════ */
.panel-form {
  flex: 1;
  background: var(--card-bg);   /* #fffef9 — crema muy suave, igual que cards */
  padding: 2.5rem 2.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
  border-left: 1.5px solid var(--cream-border);
  animation: formIn .7s .05s cubic-bezier(.22,1,.36,1) both;
}
@keyframes formIn {
  from { opacity: 0; transform: translateX(18px); }
  to   { opacity: 1; transform: translateX(0); }
}

/* ── Tabs ───────────────────────────────────────────────────────────────── */
.tabs {
  position: relative;
  display: flex;
  background: var(--cream);
  border: 1.5px solid var(--cream-border);
  border-radius: 12px;
  padding: 4px;
  gap: 2px;
}

.tab {
  flex: 1; padding: .6rem 1rem;
  background: none; border: none;
  font-family: 'DM Sans', sans-serif;
  font-size: .875rem; font-weight: 600;
  color: #5a7a5a;
  cursor: pointer;
  border-radius: 9px;
  position: relative; z-index: 1;
  transition: color .25s;
}
.tab-active { color: var(--green-dark); }

.tab-slider {
  position: absolute;
  top: 4px; left: 4px;
  width: calc(50% - 4px);
  height: calc(100% - 8px);
  background: #fff;
  border: 1.5px solid var(--cream-border);
  border-radius: 9px;
  box-shadow: 0 2px 8px rgba(26,71,49,.1);
  transition: transform .3s cubic-bezier(.34,1.56,.64,1);
}
.tab-slider-right { transform: translateX(100%); }

/* ── Heading ────────────────────────────────────────────────────────────── */
.form-heading h2 {
  font-family: 'Playfair Display', serif;
  font-size: 1.35rem; font-weight: 700;
  color: var(--green-dark);
  margin: 0 0 3px;
}
.form-heading p {
  font-size: .82rem;
  color: #5a7a5a;
  margin: 0;
}

/* ── Fields ─────────────────────────────────────────────────────────────── */
.form { display: flex; flex-direction: column; gap: .95rem; }

.field { display: flex; flex-direction: column; gap: 5px; }

.field-label {
  font-size: .72rem; font-weight: 700;
  color: var(--green-dark);
  text-transform: uppercase; letter-spacing: .07em;
}

.field-wrap {
  position: relative;
  display: flex; align-items: center;
}

/* Icono izquierdo */
.field-ico {
  position: absolute; left: .875rem;
  color: #9ab5a0;
  display: flex; pointer-events: none;
  transition: color .2s;
}

/* Input base */
.field-input {
  width: 100%;
  padding: .7rem .875rem .7rem 2.6rem;
  background: #fff;
  border: 1.5px solid var(--cream-border);
  border-radius: 10px;
  font-family: 'DM Sans', sans-serif;
  font-size: .9rem;
  color: #1a2e1a;            /* texto oscuro — perfectamente legible */
  outline: none;
  transition: border-color .2s, box-shadow .2s, background .2s;
  box-sizing: border-box;
}
.field-input::placeholder {
  color: #aabcaa;            /* placeholder visible pero suave */
}
.field-input:focus {
  border-color: var(--green-light);
  box-shadow: 0 0 0 3px rgba(82,183,136,.12);
  background: #fff;
}
/* Icono se ilumina al hacer foco */
.field-wrap:focus-within .field-ico { color: var(--green-mid); }

.field-input:disabled {
  background: var(--cream); opacity: .65; cursor: not-allowed;
}

/* Contraseña — espacio derecho para el botón de toggle */
.field-input-pw { padding-right: 2.75rem; }

/* Select */
.field-select {
  appearance: none; cursor: pointer;
  color: #1a2e1a;
}
.field-select option { background: #fff; color: #1a2e1a; }

/* Toggle contraseña */
.btn-toggle-pw {
  position: absolute; right: .875rem;
  background: none; border: none;
  color: #9ab5a0; cursor: pointer;
  display: flex; padding: 4px;
  transition: color .2s;
}
.btn-toggle-pw:hover { color: var(--green-mid); }

/* ── Campos de registro — transición ────────────────────────────────────── */
.register-extra { display: flex; flex-direction: column; gap: .95rem; }
.slide-down-enter-active { transition: all .35s cubic-bezier(.22,1,.36,1); }
.slide-down-leave-active { transition: all .22s ease-in; }
.slide-down-enter-from   { opacity: 0; transform: translateY(-10px); }
.slide-down-leave-to     { opacity: 0; transform: translateY(-6px); }

/* ── Mensajes ────────────────────────────────────────────────────────────── */
.msg {
  display: flex; align-items: center; gap: .45rem;
  padding: .6rem .875rem; border-radius: 10px;
  font-size: .82rem; font-weight: 500; line-height: 1.4;
}
.msg-error {
  background: #fff0f0;
  color: #b91c1c;
  border: 1.5px solid #fca5a5;
}
.msg-success {
  background: var(--green-pale);
  color: var(--green-dark);
  border: 1.5px solid #b8ddc8;
}

.msg-enter-active, .msg-leave-active { transition: all .28s ease; }
.msg-enter-from, .msg-leave-to { opacity: 0; transform: translateY(-5px); }

/* ── Botón submit ────────────────── */
.btn-submit {
  width: 100%;
  padding: .8rem;
  background: var(--green-mid);
  color: #000000;
  border: none; border-radius: 10px;
  font-family: 'DM Sans', sans-serif;
  font-size: .9rem; font-weight: 700;
  cursor: pointer;
  margin-top: .1rem;
  box-shadow: 0 4px 18px rgba(45,106,79,.25);
  transition: background .2s, transform .15s, box-shadow .2s;
}
.btn-submit:hover:not(:disabled) {
  background: #09ff00;
  transform: translateY(-1px);
  box-shadow: 0 8px 28px rgba(0,0,0,.18);
}
.btn-submit:active:not(:disabled) { transform: translateY(0); }
.btn-submit:disabled { opacity: .45; cursor: not-allowed; }

.btn-label {
  display: flex; align-items: center;
  justify-content: center; gap: .45rem;
}

.btn-spinner {
  display: inline-block; width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,.35);
  border-top-color: #fff; border-radius: 50%;
  animation: spin .65s linear infinite; margin: 0 auto;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Footer ──────────────────────────────────────────────────────────────── */
.form-footer {
  margin-top: auto;
  padding-top: .75rem;
  border-top: 1.5px solid var(--cream-border);
}
.btn-back {
  background: none; border: none;
  font-family: 'DM Sans', sans-serif;
  font-size: .8rem; color: #5a7a5a;
  cursor: pointer; padding: 4px 0;
  transition: color .2s;
}
.btn-back:hover { color: var(--green-mid); }

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 700px) {
  .login-card    { flex-direction: column; max-width: 440px; border-radius: 16px; }
  .panel-brand   { width: 100%; padding: 2rem 1.75rem; }
  .brand-tagline { font-size: 1.1rem; }
  .panel-form    { padding: 1.75rem; border-left: none; border-top: 1.5px solid var(--cream-border); }
}

@media (max-width: 420px) {
  .panel-form  { padding: 1.25rem; }
  .panel-brand { padding: 1.5rem; }
}
</style>