<template>
  <div class="user-menu">

    <!-- ══ HEADER ══ -->
    <header class="page-header">
      <div class="header-inner">
        <div class="header-saludo">
          <p class="saludo-label">Bienvenido de vuelta</p>
          <h1 class="saludo-nombre">{{ userName }}</h1>
          <p class="saludo-meta">
            <span class="meta-chip">{{ getRoleName(userType) }}</span>
            <span class="meta-sep">·</span>
            <span class="meta-codigo">{{ userCode }}</span>
          </p>
        </div>
        <div class="header-stats">
          <div class="hstat" :class="{ 'hstat-danger': vencidos > 0 }">
            <span class="hstat-num">{{ activeBooks }}</span>
            <span class="hstat-lbl">Libros</span>
          </div>
          <div class="hstat hstat-warn" v-if="porVencer > 0">
            <span class="hstat-num">{{ porVencer }}</span>
            <span class="hstat-lbl">Por vencer</span>
          </div>
          <div class="hstat hstat-danger" v-if="vencidos > 0">
            <span class="hstat-num">{{ vencidos }}</span>
            <span class="hstat-lbl">Vencidos</span>
          </div>
          <div class="hstat hstat-blue" v-if="equiposActivos.length > 0">
            <span class="hstat-num">{{ equiposActivos.length }}</span>
            <span class="hstat-lbl">Equipos</span>
          </div>
          <div class="hstat hstat-purple" v-if="areasActivas.length > 0">
            <span class="hstat-num">{{ areasActivas.length }}</span>
            <span class="hstat-lbl">Cubículos</span>
          </div>
          <button class="btn-refresh" @click="refreshData" title="Actualizar">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </button>
          <button class="btn-cambiar-pass" @click="abrirModalPassword" title="Cambiar contraseña">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- ══ BANNER MULTAS ══ -->
    <div v-if="tieneMultasPendientes" class="banner-multas">
      <div class="banner-ico">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
      </div>
      <div class="banner-body">
        <strong>Tienes multas pendientes</strong>
        <p>No puedes solicitar nuevos préstamos hasta liquidarlas.</p>
      </div>
      <button class="banner-cta" @click="$router.push('/mis-multas')">Ver multas →</button>
    </div>

    <div class="page-body">

      <!-- ══ PRÉSTAMOS DE LIBROS ══ -->
      <section class="section-card">
        <div class="section-head">
          <div class="section-title-wrap">
            <div class="section-ico section-ico-libro">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
            </div>
            <h2 class="section-title">Mis Préstamos</h2>
            <span class="section-count">{{ prestamosActivos.length }}</span>
          </div>
        </div>

        <div v-if="loadingPrestamos" class="estado-loading">
          <div class="spinner"></div><p>Cargando préstamos...</p>
        </div>
        <div v-else-if="prestamosActivos.length === 0" class="estado-vacio">
          <div class="vacio-ico">
            <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
          </div>
          <p class="vacio-titulo">Sin préstamos activos</p>
          <p class="vacio-desc">Consulta el catálogo para ver libros disponibles</p>
          <button class="btn-catalogo" @click="$router.push('/catalogo')">Ver catálogo →</button>
        </div>
        <div v-else class="prestamos-lista">
          <div
            v-for="item in prestamosActivos" :key="item.id"
            class="prestamo-card"
            :class="{ 'prestamo-overdue': item.status === 'overdue', 'prestamo-warning': item.status === 'warning' }"
          >
            <div class="prestamo-indicator"></div>
            <div class="prestamo-body">
              <div class="prestamo-top">
                <div class="prestamo-info">
                  <p class="prestamo-nombre">{{ item.name }}</p>
                  <div class="prestamo-meta">
                    <span class="prestamo-fecha-lbl">Prestado</span>
                    <span class="prestamo-fecha">{{ formatDate(item.loanDate) }}</span>
                  </div>
                </div>
                <span class="status-badge" :class="`badge-${item.status}`">{{ getStatusText(item.status) }}</span>
              </div>
              <div class="prestamo-devolucion">
                <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                <span class="dev-label">Devolución:</span>
                <span class="dev-fecha">{{ formatDate(item.returnDate) }}</span>
                <span v-if="item.status === 'warning'" class="dev-urgencia dev-warn">
                  {{ item.diasRestantes === 0 ? 'Vence hoy' : `${item.diasRestantes}d restantes` }}
                </span>
                <span v-if="item.status === 'overdue'" class="dev-urgencia dev-overdue">
                  {{ Math.abs(item.diasRestantes) }}d vencido
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ══ EQUIPO EN USO ══ -->
      <section class="section-card">
        <div class="section-head">
          <div class="section-title-wrap">
            <div class="section-ico section-ico-equipo">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <h2 class="section-title">Equipo en Uso</h2>
            <span class="section-count">{{ equiposActivos.length }}</span>
          </div>
        </div>

        <div v-if="loadingEquipos" class="estado-loading">
          <div class="spinner"></div><p>Cargando equipos...</p>
        </div>
        <div v-else-if="equiposActivos.length === 0" class="estado-vacio">
          <div class="vacio-ico">
            <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
          </div>
          <p class="vacio-titulo">Sin equipos en uso</p>
          <p class="vacio-desc">No tienes laptops o computadoras prestadas</p>
        </div>
        <div v-else class="prestamos-lista">
          <div
            v-for="eq in equiposActivos" :key="eq.id"
            class="prestamo-card"
            :class="getTiempoCardClass(eq.fecha_devolucion)"
          >
            <div class="prestamo-indicator"></div>
            <div class="prestamo-body">
              <div class="prestamo-top">
                <div class="prestamo-info">
                  <p class="prestamo-nombre">{{ eq.equipo_modelo }} — {{ eq.equipo_marca }}</p>
                  <div class="prestamo-meta">
                    <span class="prestamo-fecha-lbl">Serie</span>
                    <span class="prestamo-fecha mono">{{ eq.equipo_numero_serie }}</span>
                  </div>
                </div>
                <span class="status-badge" :class="getTiempoBadgeClass(eq.fecha_devolucion)">
                  {{ getTiempoBadgeText(eq.fecha_devolucion) }}
                </span>
              </div>
              <div class="prestamo-devolucion">
                <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <span class="dev-label">Devolver a las:</span>
                <span class="dev-fecha">{{ formatHora(eq.fecha_devolucion) }}</span>
                <span v-if="calcularEstadoTiempo(eq.fecha_devolucion) !== 'vigente'" class="dev-urgencia" :class="getTiempoUrgenciaClass(eq.fecha_devolucion)">
                  {{ formatTiempoRestante(eq.fecha_devolucion) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ══ CUBÍCULO EN USO ══ -->
      <section class="section-card">
        <div class="section-head">
          <div class="section-title-wrap">
            <div class="section-ico section-ico-area">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
            </div>
            <h2 class="section-title">Cubículo en Uso</h2>
            <span class="section-count">{{ areasActivas.length }}</span>
          </div>
        </div>

        <div v-if="loadingAreas" class="estado-loading">
          <div class="spinner"></div><p>Cargando cubículos...</p>
        </div>
        <div v-else-if="areasActivas.length === 0" class="estado-vacio">
          <div class="vacio-ico">
            <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <p class="vacio-titulo">Sin cubículos en uso</p>
          <p class="vacio-desc">No tienes áreas de estudio reservadas</p>
        </div>
        <div v-else class="prestamos-lista">
          <div
            v-for="area in areasActivas" :key="area.id"
            class="prestamo-card"
            :class="getTiempoCardClass(area.fecha_devolucion_esperada)"
          >
            <div class="prestamo-indicator"></div>
            <div class="prestamo-body">
              <div class="prestamo-top">
                <div class="prestamo-info">
                  <p class="prestamo-nombre">{{ area.area_nombre }}</p>
                  <div class="prestamo-meta" v-if="area.area_capacidad">
                    <span class="prestamo-fecha-lbl">Capacidad</span>
                    <span class="prestamo-fecha">{{ area.area_capacidad }} personas</span>
                  </div>
                </div>
                <span class="status-badge" :class="getTiempoBadgeClass(area.fecha_devolucion_esperada)">
                  {{ getTiempoBadgeText(area.fecha_devolucion_esperada) }}
                </span>
              </div>
              <div class="prestamo-devolucion">
                <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <span class="dev-label">Devolver a las:</span>
                <span class="dev-fecha">{{ formatHora(area.fecha_devolucion_esperada) }}</span>
                <span v-if="calcularEstadoTiempo(area.fecha_devolucion_esperada) !== 'vigente'" class="dev-urgencia" :class="getTiempoUrgenciaClass(area.fecha_devolucion_esperada)">
                  {{ formatTiempoRestante(area.fecha_devolucion_esperada) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ══ HISTORIAL DE LIBROS ══ -->
      <section class="section-card section-historial">
        <button class="historial-toggle" @click="historialAbierto = !historialAbierto">
          <div class="section-title-wrap">
            <h2 class="section-title">Historial de préstamos</h2>
            <span class="section-count">{{ prestamosHistorial.length }}</span>
          </div>
          <svg class="toggle-chevron" :class="{ 'chevron-open': historialAbierto }"
            width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
          </svg>
        </button>
        <transition name="historial-slide">
          <div v-if="historialAbierto" class="historial-body">
            <div class="historial-search">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
              <input v-model="busquedaHistorial" type="text" placeholder="Buscar en historial..." class="historial-input"/>
            </div>
            <div v-if="historialFiltrado.length === 0" class="estado-vacio estado-vacio-sm">
              <p>{{ busquedaHistorial ? 'Sin resultados' : 'Sin historial registrado' }}</p>
            </div>
            <div v-else class="historial-lista">
              <div v-for="item in historialPaginado" :key="item.id" class="historial-item">
                <div class="historial-item-ico">
                  <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                  </svg>
                </div>
                <div class="historial-item-info">
                  <p class="historial-item-nombre">{{ item.name }}</p>
                  <p class="historial-item-fechas">{{ formatDate(item.loanDate) }} → {{ formatDate(item.returnDate) }}</p>
                </div>
                <span class="historial-badge">Devuelto</span>
              </div>
            </div>
            <div v-if="totalPaginasHistorial > 1" class="historial-paginacion">
              <button class="pag-btn" :disabled="paginaHistorial === 1" @click="paginaHistorial--">← Anterior</button>
              <span class="pag-info">{{ paginaHistorial }} / {{ totalPaginasHistorial }}</span>
              <button class="pag-btn" :disabled="paginaHistorial === totalPaginasHistorial" @click="paginaHistorial++">Siguiente →</button>
            </div>
          </div>
        </transition>
      </section>
    </div>

    <!-- ══ TOAST ══ -->
    <transition name="toast-in">
      <div v-if="toast.visible" class="toast" :class="toast.tipo">
        <span>{{ toast.titulo }}</span>
        <p v-if="toast.descripcion" class="toast-desc">{{ toast.descripcion }}</p>
        <button class="toast-close" @click="toast.visible = false">×</button>
      </div>
    </transition>

    <!-- ══ MODAL: CAMBIAR CONTRASEÑA ══ -->
    <div v-if="modalPassword.visible" class="modal-overlay" @click.self="cerrarModalPassword">
      <div class="modal-pass">
        <div class="modal-pass-header">
          <div class="modal-pass-ico">
            <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
            </svg>
          </div>
          <div class="modal-pass-titulo-wrap">
            <h3 class="modal-pass-titulo">Cambiar Contraseña</h3>
            <p class="modal-pass-sub">Elige una contraseña segura de al menos 8 caracteres</p>
          </div>
          <button class="modal-pass-close" @click="cerrarModalPassword" :disabled="procesandoPassword">×</button>
        </div>

        <div class="modal-pass-body">
          <!-- Contraseña actual -->
          <div class="pass-field">
            <label class="pass-label">Contraseña actual <span class="req">*</span></label>
            <div class="pass-input-wrap">
              <input
                :type="mostrarActual ? 'text' : 'password'"
                v-model="passwordForm.actual"
                class="pass-input"
                placeholder="Tu contraseña actual"
                autocomplete="current-password"
              />
              <button class="pass-eye" @click="mostrarActual = !mostrarActual" type="button">
                <svg v-if="!mostrarActual" width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Nueva contraseña -->
          <div class="pass-field">
            <label class="pass-label">Nueva contraseña <span class="req">*</span></label>
            <div class="pass-input-wrap">
              <input
                :type="mostrarNueva ? 'text' : 'password'"
                v-model="passwordForm.nueva"
                class="pass-input"
                placeholder="Mínimo 8 caracteres"
                autocomplete="new-password"
              />
              <button class="pass-eye" @click="mostrarNueva = !mostrarNueva" type="button">
                <svg v-if="!mostrarNueva" width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              </button>
            </div>
            <!-- Indicador de fortaleza -->
            <div v-if="passwordForm.nueva" class="pass-strength">
              <div class="strength-bar">
                <div class="strength-fill" :class="fortalezaClass" :style="{ width: fortalezaPct + '%' }"></div>
              </div>
              <span class="strength-label" :class="fortalezaClass">{{ fortalezaLabel }}</span>
            </div>
          </div>

          <!-- Confirmar -->
          <div class="pass-field">
            <label class="pass-label">Confirmar contraseña <span class="req">*</span></label>
            <div class="pass-input-wrap">
              <input
                :type="mostrarConfirmar ? 'text' : 'password'"
                v-model="passwordForm.confirmar"
                class="pass-input"
                :class="{ 'pass-input-error': passwordForm.confirmar && passwordForm.nueva !== passwordForm.confirmar }"
                placeholder="Repite la nueva contraseña"
                autocomplete="new-password"
              />
              <button class="pass-eye" @click="mostrarConfirmar = !mostrarConfirmar" type="button">
                <svg v-if="!mostrarConfirmar" width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              </button>
            </div>
            <p v-if="passwordForm.confirmar && passwordForm.nueva !== passwordForm.confirmar" class="pass-mismatch">
              Las contraseñas no coinciden
            </p>
          </div>

          <div v-if="modalPassword.error" class="pass-error-box">{{ modalPassword.error }}</div>
        </div>

        <div class="modal-pass-footer">
          <button class="btn-pass-cancel" @click="cerrarModalPassword" :disabled="procesandoPassword">Cancelar</button>
          <button class="btn-pass-confirm" @click="guardarPassword" :disabled="procesandoPassword || !passwordFormValido">
            <span v-if="procesandoPassword" class="spinner-mini-dark"></span>
            {{ procesandoPassword ? 'Guardando...' : 'Cambiar Contraseña' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { prestamoLibroService } from '@/services/PrestamoLibro'
import { multasService } from '@/services/multas'
import api from '@/services/api'

export default {
  name: 'UserMenu',

  data() {
    return {
      prestamos:        [],
      loadingPrestamos: false,
      equipos:          [],
      loadingEquipos:   false,
      areas:            [],
      loadingAreas:     false,
      tieneMultasPendientes: false,
      historialAbierto:  false,
      busquedaHistorial: '',
      paginaHistorial:   1,
      itemsPorPagina:    8,
      toast: { visible: false, tipo: '', titulo: '', descripcion: '' },
      // ── Cambiar contraseña ─────────────────────────────────────────────
      modalPassword:     { visible: false, error: '' },
      procesandoPassword: false,
      mostrarActual:     false,
      mostrarNueva:      false,
      mostrarConfirmar:  false,
      passwordForm:      { actual: '', nueva: '', confirmar: '' }
    }
  },

  setup() {
    return { authStore: useAuthStore() }
  },

  computed: {
    userName() { return this.authStore.userName },
    userCode() { return this.authStore.userCode },
    userType() { return this.authStore.tipoUsuarioId },

    prestamosActivos() {
      return this.prestamos.filter(p => ['active','warning','overdue'].includes(p.status))
    },
    prestamosHistorial() {
      return this.prestamos.filter(p => p.status === 'completed')
    },
    historialFiltrado() {
      if (!this.busquedaHistorial.trim()) return this.prestamosHistorial
      const q = this.busquedaHistorial.toLowerCase()
      return this.prestamosHistorial.filter(p => p.name?.toLowerCase().includes(q))
    },
    totalPaginasHistorial() {
      return Math.ceil(this.historialFiltrado.length / this.itemsPorPagina) || 1
    },
    historialPaginado() {
      const s = (this.paginaHistorial - 1) * this.itemsPorPagina
      return this.historialFiltrado.slice(s, s + this.itemsPorPagina)
    },
    activeBooks() { return this.prestamos.filter(p => ['active','warning','overdue'].includes(p.status)).length },
    porVencer()   { return this.prestamos.filter(p => p.status === 'warning').length },
    vencidos()    { return this.prestamos.filter(p => p.status === 'overdue').length },
    equiposActivos() { return this.equipos.filter(e => e.estado_prestamo_id === 1) },
    areasActivas()   { return this.areas.filter(a => a.estado_prestamo_id === 1) },

    // ── Fortaleza de contraseña ────────────────────────────────────────────
    fortalezaPct() {
      const p = this.passwordForm.nueva
      if (!p) return 0
      let score = 0
      if (p.length >= 8)  score += 25
      if (p.length >= 12) score += 15
      if (/[A-Z]/.test(p)) score += 20
      if (/[0-9]/.test(p)) score += 20
      if (/[^A-Za-z0-9]/.test(p)) score += 20
      return Math.min(score, 100)
    },
    fortalezaClass() {
      const pct = this.fortalezaPct
      if (pct < 40) return 'strength-weak'
      if (pct < 70) return 'strength-medium'
      return 'strength-strong'
    },
    fortalezaLabel() {
      const pct = this.fortalezaPct
      if (pct < 40) return 'Débil'
      if (pct < 70) return 'Regular'
      return 'Fuerte'
    },
    passwordFormValido() {
      return (
        this.passwordForm.actual.length > 0 &&
        this.passwordForm.nueva.length >= 8 &&
        this.passwordForm.nueva === this.passwordForm.confirmar
      )
    },
  },

  watch: {
    busquedaHistorial() { this.paginaHistorial = 1 }
  },

  mounted() {
    this.loadPrestamos()
    this.loadEquipos()
    this.loadAreas()
    this.verificarMultasPendientes()
  },

  methods: {
    async loadPrestamos() {
      try {
        this.loadingPrestamos = true
        this.prestamos = await prestamoLibroService.getPrestamosUsuario(false)
      } catch {
        this.mostrarToast('error', 'Error', 'No se pudieron cargar los préstamos')
      } finally { this.loadingPrestamos = false }
    },

    async loadEquipos() {
      try {
        this.loadingEquipos = true
        const userId = this.authStore.userId
        if (!userId) return
        const r = await api.get(`/prestamos-equipos-computo/usuario/${userId}`, { params: { solo_vigentes: true } })
        this.equipos = Array.isArray(r.data) ? r.data : []
      } catch { this.equipos = [] }
      finally { this.loadingEquipos = false }
    },

    async loadAreas() {
      try {
        this.loadingAreas = true
        const userId = this.authStore.userId
        if (!userId) return
        const r = await api.get(`/prestamos-areas/usuario/${userId}`, { params: { solo_vigentes: true } })
        this.areas = Array.isArray(r.data) ? r.data : []
      } catch { this.areas = [] }
      finally { this.loadingAreas = false }
    },

    async verificarMultasPendientes() {
      try {
        const userId = this.authStore.userId
        if (!userId) return
        const multas = await multasService.getMultasByUsuario(userId)
        this.tieneMultasPendientes = Array.isArray(multas) && multas.length > 0
        if (this.authStore.actualizarEstadoMultas) this.authStore.actualizarEstadoMultas(multas)
      } catch { /* silencioso */ }
    },

    refreshData() {
      this.loadPrestamos()
      this.loadEquipos()
      this.loadAreas()
      this.verificarMultasPendientes()
    },

    // ── Tiempo para equipos y áreas ─────────────────────────────────────
    calcularEstadoTiempo(fecha) {
      if (!fecha) return 'sin_fecha'
      const diffMin = (new Date(fecha) - new Date()) / 60000
      if (diffMin < 0)   return 'excedido'
      if (diffMin <= 10) return 'peligro'
      if (diffMin <= 30) return 'advertencia'
      return 'vigente'
    },
    getTiempoBadgeClass(fecha) {
      return {
        vigente:     'badge-active',
        advertencia: 'badge-warning',
        peligro:     'badge-overdue',
        excedido:    'badge-excedido',
      }[this.calcularEstadoTiempo(fecha)] || 'badge-active'
    },
    getTiempoBadgeText(fecha) {
      return { vigente:'Al corriente', advertencia:'⚠ Advertencia', peligro:'🔴 Peligro', excedido:'Excedió tiempo' }[this.calcularEstadoTiempo(fecha)] || '—'
    },
    getTiempoCardClass(fecha) {
      return { advertencia:'prestamo-warning', peligro:'prestamo-overdue', excedido:'prestamo-overdue' }[this.calcularEstadoTiempo(fecha)] || ''
    },
    getTiempoUrgenciaClass(fecha) {
      return { advertencia:'dev-warn', peligro:'dev-overdue', excedido:'dev-overdue' }[this.calcularEstadoTiempo(fecha)] || ''
    },
    formatTiempoRestante(fecha) {
      if (!fecha) return ''
      const diffMin = Math.ceil((new Date(fecha) - new Date()) / 60000)
      if (diffMin < 0) {
        const abs = Math.abs(diffMin)
        return abs >= 60 ? `+${Math.floor(abs/60)}h ${abs%60}m excedido` : `+${abs}m excedido`
      }
      return diffMin >= 60 ? `${Math.floor(diffMin/60)}h ${diffMin%60}m restantes` : `${diffMin}m restantes`
    },

    // ── Helpers generales ───────────────────────────────────────────────
    getRoleName(tipoId) {
      return { 1:'Estudiante', 2:'Bibliotecario', 3:'Admin Avanzado', 4:'Super Admin' }[tipoId] || 'Usuario'
    },
    formatDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString('es-MX', { day:'2-digit', month:'short', year:'numeric' })
    },
    formatHora(d) {
      if (!d) return '—'
      return new Date(d).toLocaleString('es-MX', { day:'2-digit', month:'short', hour:'2-digit', minute:'2-digit' })
    },
    getStatusText(status) {
      return { active:'Activo', warning:'Por vencer', overdue:'Vencido', completed:'Devuelto' }[status] || status
    },
    // ── Cambiar contraseña ─────────────────────────────────────────────────
    abrirModalPassword() {
      this.passwordForm   = { actual: '', nueva: '', confirmar: '' }
      this.mostrarActual  = false
      this.mostrarNueva   = false
      this.mostrarConfirmar = false
      this.modalPassword  = { visible: true, error: '' }
    },
    cerrarModalPassword() {
      if (!this.procesandoPassword) this.modalPassword.visible = false
    },
    async guardarPassword() {
      if (!this.passwordFormValido || this.procesandoPassword) return
      this.procesandoPassword     = true
      this.modalPassword.error    = ''
      try {
        await api.patch('/api/auth/cambiar-password', {
          clave_actual:    this.passwordForm.actual,
          clave_nueva:     this.passwordForm.nueva,
          clave_confirmar: this.passwordForm.confirmar,
        })
        this.modalPassword.visible = false
        this.mostrarToast('success', '¡Contraseña actualizada!', 'Tu nueva contraseña ya está activa')
      } catch (e) {
        this.modalPassword.error = e.response?.data?.detail || 'Error al cambiar la contraseña'
      } finally {
        this.procesandoPassword = false
      }
    },

    mostrarToast(tipo, titulo, descripcion = '') {
      this.toast = { visible:true, tipo:`toast-${tipo}`, titulo, descripcion }
      setTimeout(() => { this.toast.visible = false }, 4000)
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

:root {
  --green-dark:#1a4731; --green-mid:#2d6a4f; --green-light:#52b788;
  --green-pale:#d8f3dc; --gold-mid:#c9900c; --gold-light:#f4c542;
  --gold-pale:#fef9e7; --cream:#f5f0e8; --cream-border:#d4e8da;
  --card-bg:#fffef9; --shadow-sm:0 2px 12px rgba(26,47,26,.08);
}

.user-menu { min-height:100vh; font-family:'DM Sans',sans-serif; background:radial-gradient(ellipse 70% 40% at 5% 0%,rgba(82,183,136,.1) 0%,transparent 55%),radial-gradient(ellipse 50% 40% at 90% 100%,rgba(201,144,12,.08) 0%,transparent 50%),var(--cream); }

.page-header { background:linear-gradient(135deg,#1a4731 0%,#2d6a4f 60%,#3a7d5e 100%); padding:2rem 2rem 1.75rem; position:relative; overflow:hidden; }
.page-header::before { content:''; position:absolute; inset:0; pointer-events:none; background:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E"); }
.header-inner { position:relative; display:flex; justify-content:space-between; align-items:flex-end; gap:1.5rem; flex-wrap:wrap; }
.saludo-label  { font-size:.72rem; font-weight:600; color:rgba(255,255,255,.5); text-transform:uppercase; letter-spacing:.1em; margin-bottom:.2rem; }
.saludo-nombre { font-family:'Playfair Display',serif; font-size:1.75rem; font-weight:700; color:#fff; margin-bottom:.4rem; }
.saludo-meta   { display:flex; align-items:center; gap:.5rem; font-size:.8rem; }
.meta-chip     { background:rgba(244,197,66,.18); color:var(--gold-light); border:1px solid rgba(244,197,66,.25); padding:.15rem .55rem; border-radius:20px; font-weight:600; font-size:.72rem; text-transform:uppercase; }
.meta-sep      { color:rgba(255,255,255,.3); }
.meta-codigo   { color:rgba(255,255,255,.6); font-family:monospace; font-size:.78rem; }
.header-stats  { display:flex; align-items:center; gap:.625rem; flex-shrink:0; flex-wrap:wrap; }
.hstat         { display:flex; flex-direction:column; align-items:center; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.12); border-radius:10px; padding:.45rem .875rem; min-width:60px; }
.hstat-warn    { background:rgba(244,197,66,.15); border-color:rgba(244,197,66,.2); }
.hstat-danger  { background:rgba(214,40,40,.18);  border-color:rgba(214,40,40,.25); }
.hstat-blue    { background:rgba(96,165,250,.15);  border-color:rgba(96,165,250,.25); }
.hstat-purple  { background:rgba(167,139,250,.15); border-color:rgba(167,139,250,.25); }
.hstat-num     { font-family:'Playfair Display',serif; font-size:1.2rem; font-weight:700; color:#fff; line-height:1; }
.hstat-lbl     { font-size:.63rem; color:rgba(255,255,255,.55); text-transform:uppercase; letter-spacing:.07em; margin-top:2px; white-space:nowrap; }
.btn-refresh   { width:34px; height:34px; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.12); border-radius:8px; color:rgba(255,255,255,.7); cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all .2s; }
.btn-refresh:hover { background:rgba(255,255,255,.18); color:#fff; }

.banner-multas { display:flex; align-items:center; gap:1rem; margin:1.25rem 1.5rem 0; padding:.875rem 1.25rem; background:#fff3f3; border:1.5px solid #f5c0c0; border-left:4px solid #d62828; border-radius:12px; }
.banner-ico    { color:#d62828; flex-shrink:0; display:flex; }
.banner-body   { flex:1; }
.banner-body strong { display:block; font-size:.875rem; color:#d62828; margin-bottom:2px; }
.banner-body p { font-size:.78rem; color:#6b3333; margin:0; }
.banner-cta    { background:#d62828; color:#fff; border:none; border-radius:8px; padding:.4rem .9rem; font-size:.8rem; font-weight:700; cursor:pointer; white-space:nowrap; flex-shrink:0; transition:background .2s; }
.banner-cta:hover { background:#b91c1c; }

.page-body { padding:1.5rem; display:flex; flex-direction:column; gap:1.25rem; }

.section-card { background:var(--card-bg); border:1.5px solid var(--cream-border); border-radius:16px; box-shadow:var(--shadow-sm); overflow:hidden; }
.section-head { padding:1.1rem 1.375rem .875rem; border-bottom:1.5px solid #eef5f0; }
.section-title-wrap { display:flex; align-items:center; gap:.625rem; }
.section-ico   { width:26px; height:26px; border-radius:7px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.section-ico-libro  { background:var(--green-pale); color:var(--green-mid); }
.section-ico-equipo { background:#dbeafe; color:#1e40af; }
.section-ico-area   { background:#ede9fe; color:#5b21b6; }
.section-title { font-family:'Playfair Display',serif; font-size:1.05rem; font-weight:700; color:var(--green-dark); margin:0; }
.section-count { background:var(--green-pale); color:var(--green-dark); font-size:.72rem; font-weight:700; padding:.15rem .5rem; border-radius:20px; border:1px solid var(--cream-border); }

.estado-loading { display:flex; align-items:center; gap:.75rem; padding:1.5rem 1.375rem; color:#9ab5a0; font-size:.82rem; }
.spinner { width:20px; height:20px; border:2.5px solid var(--green-pale); border-top-color:var(--green-mid); border-radius:50%; animation:spin .7s linear infinite; flex-shrink:0; }
@keyframes spin { to{transform:rotate(360deg)} }
.estado-vacio { display:flex; flex-direction:column; align-items:center; gap:.5rem; padding:2rem 1.375rem; text-align:center; }
.estado-vacio-sm { padding:1rem 1.375rem; }
.vacio-ico     { color:#b8ddc8; }
.vacio-titulo  { font-size:.875rem; font-weight:700; color:var(--green-dark); margin:0; }
.vacio-desc    { font-size:.78rem; color:#9ab5a0; margin:0; }
.btn-catalogo  { margin-top:.25rem; padding:.45rem 1rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-size:.8rem; font-weight:700; cursor:pointer; transition:background .2s; }
.btn-catalogo:hover { background:#111; }

.prestamos-lista { display:flex; flex-direction:column; }
.prestamo-card { display:flex; border-bottom:1px solid #f1f5f0; transition:background .15s; }
.prestamo-card:last-child { border-bottom:none; }
.prestamo-card:hover { background:#fafef8; }
.prestamo-warning .prestamo-indicator { background:var(--gold-light); }
.prestamo-warning { background:#fffbeb; }
.prestamo-overdue .prestamo-indicator { background:#d62828; }
.prestamo-overdue { background:#fff5f5; }
.prestamo-indicator { width:4px; flex-shrink:0; background:#b8ddc8; }
.prestamo-body   { flex:1; padding:.875rem 1.25rem; display:flex; flex-direction:column; gap:.375rem; }
.prestamo-top    { display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; flex-wrap:wrap; }
.prestamo-nombre { font-weight:700; font-size:.9rem; color:#1a2e1a; margin:0; }
.prestamo-meta   { display:flex; gap:.4rem; align-items:center; margin-top:2px; }
.prestamo-fecha-lbl { font-size:.7rem; color:#9ab5a0; text-transform:uppercase; letter-spacing:.05em; }
.prestamo-fecha     { font-size:.75rem; color:#5a7a5a; }
.prestamo-devolucion { display:flex; align-items:center; gap:.4rem; font-size:.75rem; color:#5a7a5a; }
.dev-label   { color:#9ab5a0; }
.dev-fecha   { color:#3d5a3d; }
.dev-urgencia { font-weight:700; font-size:.7rem; padding:.1rem .45rem; border-radius:20px; }
.dev-warn    { background:var(--gold-pale); color:var(--gold-mid); }
.dev-overdue { background:#fff0f0; color:#b91c1c; }
.mono { font-family:monospace; }

.status-badge { font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.06em; padding:.2rem .55rem; border-radius:20px; white-space:nowrap; flex-shrink:0; }
.badge-active   { background:var(--green-pale); color:var(--green-dark); border:1px solid #b8ddc8; }
.badge-warning  { background:var(--gold-pale);  color:var(--gold-mid);   border:1px solid #fde68a; }
.badge-overdue  { background:#fff0f0; color:#b91c1c; border:1px solid #fca5a5; }
.badge-excedido { background:#fee2e2; color:#991b1b; border:1px solid #f87171; font-style:italic; }

.section-historial { overflow:visible; }
.historial-toggle { width:100%; padding:1.1rem 1.375rem .875rem; display:flex; justify-content:space-between; align-items:center; background:none; border:none; cursor:pointer; text-align:left; transition:background .15s; }
.historial-toggle:hover { background:#fafef8; }
.toggle-chevron { color:#9ab5a0; flex-shrink:0; transition:transform .28s cubic-bezier(.4,0,.2,1); }
.chevron-open   { transform:rotate(180deg); }
.historial-slide-enter-active { transition:all .3s cubic-bezier(.4,0,.2,1); }
.historial-slide-leave-active { transition:all .2s ease-in; }
.historial-slide-enter-from, .historial-slide-leave-to { opacity:0; transform:translateY(-8px); }
.historial-body   { border-top:1.5px solid #eef5f0; padding:.875rem 1.375rem 1.1rem; display:flex; flex-direction:column; gap:.875rem; }
.historial-search { display:flex; align-items:center; gap:.5rem; padding:.5rem .75rem; background:var(--cream); border:1.5px solid var(--cream-border); border-radius:8px; color:#9ab5a0; }
.historial-input  { flex:1; border:none; background:none; font-family:'DM Sans',sans-serif; font-size:.82rem; color:#1a2e1a; outline:none; }
.historial-input::placeholder { color:#9ab5a0; }
.historial-lista  { display:flex; flex-direction:column; gap:.375rem; }
.historial-item   { display:flex; align-items:center; gap:.75rem; padding:.625rem .75rem; border-radius:9px; background:#f8fdf9; border:1px solid #eef5f0; }
.historial-item:hover { background:#f0faf3; }
.historial-item-ico   { width:28px; height:28px; background:var(--green-pale); border-radius:7px; display:flex; align-items:center; justify-content:center; color:var(--green-mid); flex-shrink:0; }
.historial-item-info  { flex:1; min-width:0; }
.historial-item-nombre { font-size:.82rem; font-weight:600; color:#1a2e1a; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin:0; }
.historial-item-fechas { font-size:.72rem; color:#9ab5a0; margin:1px 0 0; }
.historial-badge { font-size:.65rem; font-weight:700; text-transform:uppercase; padding:.15rem .5rem; border-radius:20px; background:var(--green-pale); color:var(--green-dark); border:1px solid #b8ddc8; flex-shrink:0; }
.historial-paginacion { display:flex; justify-content:center; align-items:center; gap:.75rem; padding-top:.5rem; border-top:1px solid #eef5f0; }
.pag-btn { padding:.35rem .75rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:7px; font-size:.78rem; font-weight:600; color:var(--green-mid); cursor:pointer; font-family:'DM Sans',sans-serif; transition:all .15s; }
.pag-btn:hover:not(:disabled) { background:#111; color:#fff; border-color:#111; }
.pag-btn:disabled { opacity:.4; cursor:not-allowed; }
.pag-info { font-size:.78rem; color:#5a7a5a; }

.toast { position:fixed; bottom:2rem; right:2rem; display:flex; align-items:flex-start; gap:.75rem; padding:.875rem 1.1rem; border-radius:12px; max-width:340px; z-index:9999; box-shadow:0 8px 30px rgba(0,0,0,.15); color:#fff; font-size:.82rem; font-weight:600; }
.toast-success { background:#16a34a; }
.toast-error   { background:#d62828; }
.toast-desc    { margin:.2rem 0 0; opacity:.9; font-size:.78rem; font-weight:400; }
.toast-close   { background:none; border:none; color:rgba(255,255,255,.7); font-size:1.1rem; cursor:pointer; margin-left:auto; padding:0; }
.toast-in-enter-active,.toast-in-leave-active { transition:all .3s ease; }
.toast-in-enter-from,.toast-in-leave-to { opacity:0; transform:translateX(16px); }

@media (max-width:600px) {
  .page-header  { padding:1.5rem 1.25rem 1.25rem; }
  .header-inner { flex-direction:column; align-items:flex-start; gap:1rem; }
  .header-stats { width:100%; }
  .saludo-nombre { font-size:1.4rem; }
  .page-body    { padding:1rem; }
  .banner-multas { margin:1rem 1rem 0; flex-direction:column; text-align:center; }
  .prestamo-top  { flex-direction:column; }
  .toast { left:1rem; right:1rem; bottom:1rem; max-width:none; }
}

/* ── Botón cambiar contraseña en header ─────────────────────────────────── */
.btn-cambiar-pass { width:34px; height:34px; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.12); border-radius:8px; color:rgba(255,255,255,.7); cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all .2s; }
.btn-cambiar-pass:hover { background:rgba(255,255,255,.2); color:#fff; }

/* ── Modal contraseña ────────────────────────────────────────────────────── */
.modal-overlay { position:fixed; inset:0; background:rgba(26,47,26,.55); backdrop-filter:blur(8px); display:flex; align-items:center; justify-content:center; z-index:3000; }
.modal-pass { background:var(--card-bg); border-radius:16px; width:90%; max-width:420px; border:1.5px solid var(--cream-border); box-shadow:0 24px 64px rgba(0,0,0,.2); animation:modalIn .25s cubic-bezier(.22,1,.36,1); overflow:hidden; }
@keyframes modalIn { from{opacity:0;transform:translateY(-14px) scale(.97)} to{opacity:1;transform:translateY(0) scale(1)} }

.modal-pass-header { display:flex; align-items:center; gap:.875rem; padding:1.25rem 1.375rem 1rem; border-bottom:1.5px solid #eef5f0; background:linear-gradient(135deg,#1a4731,#2d6a4f); }
.modal-pass-ico { width:38px; height:38px; background:rgba(255,255,255,.15); border-radius:10px; display:flex; align-items:center; justify-content:center; color:#fff; flex-shrink:0; }
.modal-pass-titulo-wrap { flex:1; }
.modal-pass-titulo { font-family:'Playfair Display',serif; font-size:1rem; font-weight:700; color:#fff; margin:0 0 2px; }
.modal-pass-sub    { font-size:.72rem; color:rgba(255,255,255,.65); margin:0; }
.modal-pass-close  { background:rgba(255,255,255,.15); border:none; border-radius:7px; width:28px; height:28px; color:rgba(255,255,255,.8); cursor:pointer; font-size:1.1rem; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.modal-pass-close:hover { background:rgba(255,255,255,.25); }

.modal-pass-body   { padding:1.25rem 1.375rem; display:flex; flex-direction:column; gap:.875rem; }
.modal-pass-footer { display:flex; justify-content:flex-end; gap:.625rem; padding:.875rem 1.375rem; border-top:1.5px solid #eef5f0; }

/* Campos */
.pass-field     { display:flex; flex-direction:column; gap:5px; }
.pass-label     { font-size:.72rem; font-weight:700; color:var(--green-dark); text-transform:uppercase; letter-spacing:.07em; }
.req            { color:#d62828; }
.pass-input-wrap{ position:relative; display:flex; align-items:center; }
.pass-input     { width:100%; padding:.6rem 2.5rem .6rem .75rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:9px; font-family:'DM Sans',sans-serif; font-size:.875rem; color:#1a2e1a; outline:none; transition:border-color .2s; box-sizing:border-box; }
.pass-input:focus { border-color:var(--green-light); }
.pass-input-error { border-color:#fca5a5 !important; }
.pass-eye       { position:absolute; right:.625rem; background:none; border:none; color:#9ab5a0; cursor:pointer; padding:0; display:flex; }
.pass-eye:hover { color:var(--green-mid); }

/* Fortaleza */
.pass-strength  { display:flex; align-items:center; gap:.5rem; margin-top:4px; }
.strength-bar   { flex:1; height:4px; background:#eef5f0; border-radius:4px; overflow:hidden; }
.strength-fill  { height:100%; border-radius:4px; transition:width .3s ease, background .3s ease; }
.strength-weak   { background:#ef4444; color:#b91c1c; }
.strength-medium { background:#f59e0b; color:#92400e; }
.strength-strong { background:#16a34a; color:#15803d; }
.strength-label  { font-size:.7rem; font-weight:700; white-space:nowrap; }

/* Errores */
.pass-mismatch  { font-size:.75rem; color:#dc2626; margin:2px 0 0; }
.pass-error-box { padding:.6rem .875rem; background:#fff3f3; border:1px solid #f5c0c0; border-radius:9px; color:#d62828; font-size:.82rem; font-weight:600; }

/* Botones footer */
.btn-pass-cancel  { padding:.5rem 1rem; background:#fff; border:1.5px solid var(--cream-border); border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:600; color:#5a7a5a; cursor:pointer; }
.btn-pass-cancel:disabled { opacity:.5; cursor:not-allowed; }
.btn-pass-confirm { padding:.5rem 1.1rem; background:var(--green-mid); color:#fff; border:none; border-radius:8px; font-family:'DM Sans',sans-serif; font-size:.82rem; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:.4rem; transition:background .2s; }
.btn-pass-confirm:hover:not(:disabled) { background:#111; }
.btn-pass-confirm:disabled { opacity:.45; cursor:not-allowed; }
.spinner-mini-dark { width:12px; height:12px; border:2px solid rgba(255,255,255,.3); border-top-color:#fff; border-radius:50%; animation:spin .6s linear infinite; }
</style>