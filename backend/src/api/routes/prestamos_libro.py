from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from config.database import get_db
from models.prestamos_libro import PrestamoLibro
from models.libros import Libro
from models.usuarios import Usuario
from models.multas import Multa
from models.base import EstadoPrestamo
from schemas.prestamos_libro import (
    PrestamoLibroCreate,
    PrestamoLibroResponse,
    PrestamoLibroConRelaciones,
    PrestamoLibroUpdate,
    PrestamoLibroDevolucion,
    PrestamoDevolucionResponse,
    MultaResumenEnDevolucion,
    SolicitudDevolucionResponse,
    AprobacionDevolucionRequest,
)
from core.security import (
    obtener_usuario_actual,
    requerir_puede_consultar,
    requerir_puede_gestionar_recursos
)

router = APIRouter(prefix="/prestamos-libros", tags=["Préstamos de Libros"])

# =============================================
# CONSTANTES
# =============================================

COSTO_MULTA_POR_DIA   = Decimal('5.00')  # $5 MXN por día de retraso
TIPO_PAGO_ID_DEFAULT  = 1
TIPO_RECURSO_LIBRO_ID = 1

# Estados de préstamo
ESTADO_VIGENTE              = 1
ESTADO_EXPIRADO             = 2
ESTADO_TERMINADO            = 3
ESTADO_PENDIENTE_DEVOLUCION = 5   # Nuevo — esperando aprobación del admin

# =============================================
# FUNCIONES AUXILIARES
# =============================================

def to_naive(dt: datetime) -> datetime:
    if dt and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def calcular_dias_excedidos(fecha_esperada: datetime, fecha_real: datetime) -> int:
    """
    Compara solo fechas (sin horas). Cada día calendario completo = 1 día.
    IMPORTANTE: se usa fecha_solicitud_dev (cuando el usuario solicitó),
    NO la fecha en que el admin aprueba — esto evita que el admin
    retrase la aprobación y cobre más días al usuario.
    """
    if not fecha_real:
        return 0
    diferencia = fecha_real.date() - fecha_esperada.date()
    return max(0, diferencia.days)


def generar_numero_ticket(prestamo_id: int, fecha: datetime) -> int:
    """
    Genera un número de ticket único basado en timestamp + id del préstamo.
    Formato: YYYYMMDDHHmmSS + id (relleno a 3 dígitos)
    Ejemplo: préstamo id=15 del 25/04/2026 14:30:22 → 20260425143022015
    """
    timestamp = fecha.strftime('%Y%m%d%H%M%S')
    return int(f"{timestamp}{prestamo_id:03d}")


async def verificar_libro_disponible(db: AsyncSession, libro_id: int) -> Libro:
    result = await db.execute(select(Libro).filter(Libro.id == libro_id))
    libro  = result.scalar_one_or_none()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    if libro.estado_id != 1:
        raise HTTPException(status_code=400, detail="El libro no está disponible para préstamo")
    if not libro.es_prestable:
        raise HTTPException(status_code=400, detail="El libro no es prestable")
    return libro


async def verificar_usuario_activo(db: AsyncSession, usuario_id: int) -> Usuario:
    result = await db.execute(
        select(Usuario).filter(and_(Usuario.id == usuario_id, Usuario.esta_activo == True))
    )
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario no válido para préstamo")
    return usuario


async def verificar_sin_multas_pendientes(db: AsyncSession, usuario_id: int):
    """Lazy evaluation: bloquea si el usuario tiene multas pendientes."""
    result   = await db.execute(
        select(func.count(Multa.id)).where(
            and_(Multa.usuario_multado_id == usuario_id, Multa.estado_multa_id == 1)
        )
    )
    cantidad = result.scalar() or 0
    if cantidad > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"El usuario tiene {cantidad} multa(s) pendiente(s). "
                   f"Debe liquidarlas antes de solicitar un nuevo préstamo."
        )


async def generar_multa_por_retraso(
    db: AsyncSession,
    prestamo: PrestamoLibro,
    dias_excedidos: int,
    usuario_admin_id: int
) -> Multa:
    """Genera multa automática. Usa fecha_solicitud_dev para el cálculo."""
    costo = Decimal(str(dias_excedidos)) * COSTO_MULTA_POR_DIA

    nueva_multa = Multa(
        usuario_multa_id           = usuario_admin_id,
        usuario_multado_id         = prestamo.usuario_prestado_id,
        estado_multa_id            = 1,
        fecha_multa                = datetime.utcnow() - timedelta(hours=6),
        usuario_ultimo_cambio_id   = usuario_admin_id,
        fecha_ultimo_cambio_estado = datetime.utcnow() - timedelta(hours=6),
        tipo_pago_id               = TIPO_PAGO_ID_DEFAULT,
        tipo_recurso_multa_id      = TIPO_RECURSO_LIBRO_ID,
        costo_monetario            = costo,
        observaciones              = (
            f"Multa automática por devolución tardía. "
            f"Préstamo #{prestamo.id} — {dias_excedidos} día(s) de retraso. "
            f"Cargo: ${COSTO_MULTA_POR_DIA} MXN/día × {dias_excedidos} = ${costo} MXN. "
            f"Fecha solicitud devolución: {prestamo.fecha_solicitud_dev.strftime('%d/%m/%Y %H:%M') if prestamo.fecha_solicitud_dev else 'N/A'}."
        )
    )
    db.add(nueva_multa)
    return nueva_multa


# =============================================
# ENDPOINTS DE CONSULTA
# =============================================

@router.get("/", response_model=List[PrestamoLibroConRelaciones])
async def listar_prestamos(
    skip: int = 0,
    limit: int = 100,
    estado_prestamo_id:  Optional[int] = Query(None),
    libro_id:            Optional[int] = Query(None),
    usuario_prestado_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    try:
        query = select(PrestamoLibro).options(
            selectinload(PrestamoLibro.libro),
            selectinload(PrestamoLibro.usuario_presta),
            selectinload(PrestamoLibro.usuario_prestado),
            selectinload(PrestamoLibro.estado_prestamo),
            selectinload(PrestamoLibro.usuario_ultimo_cambio),
            selectinload(PrestamoLibro.aprobado_por)
        )
        if estado_prestamo_id:
            query = query.where(PrestamoLibro.estado_prestamo_id == estado_prestamo_id)
        if libro_id:
            query = query.where(PrestamoLibro.libro_id == libro_id)
        if usuario_prestado_id:
            query = query.where(PrestamoLibro.usuario_prestado_id == usuario_prestado_id)

        query     = query.offset(skip).limit(limit)
        result    = await db.execute(query)
        prestamos = result.scalars().all()
        return [_serializar_prestamo(p) for p in prestamos]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar préstamos: {str(e)}")


@router.get("/vigentes", response_model=List[PrestamoLibroConRelaciones])
async def listar_prestamos_vigentes(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    return await listar_prestamos(
        skip=skip, limit=limit, estado_prestamo_id=ESTADO_VIGENTE,
        libro_id=None, usuario_prestado_id=None,
        db=db, usuario_actual=usuario_actual
    )


@router.get("/pendientes-devolucion", response_model=List[PrestamoLibroConRelaciones])
async def listar_pendientes_devolucion(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Lista todos los préstamos en estado 'Pendiente devolución'.
    Solo accesible para admins. Usado en el panel de aprobaciones.
    """
    try:
        query = select(PrestamoLibro).options(
            selectinload(PrestamoLibro.libro),
            selectinload(PrestamoLibro.usuario_presta),
            selectinload(PrestamoLibro.usuario_prestado),
            selectinload(PrestamoLibro.estado_prestamo),
            selectinload(PrestamoLibro.aprobado_por)
        ).where(
            PrestamoLibro.estado_prestamo_id == ESTADO_PENDIENTE_DEVOLUCION
        ).order_by(PrestamoLibro.fecha_solicitud_dev.asc())

        query     = query.offset(skip).limit(limit)
        result    = await db.execute(query)
        prestamos = result.scalars().all()
        return [_serializar_prestamo(p) for p in prestamos]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/mis-prestamos", response_model=List[PrestamoLibroConRelaciones])
async def mis_prestamos(
    solo_vigentes: bool = True,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    query = (
        select(PrestamoLibro)
        .options(
            selectinload(PrestamoLibro.libro),
            selectinload(PrestamoLibro.estado_prestamo),
            selectinload(PrestamoLibro.usuario_presta),
            selectinload(PrestamoLibro.usuario_prestado),
            selectinload(PrestamoLibro.aprobado_por),       # ← AGREGAR
            selectinload(PrestamoLibro.usuario_ultimo_cambio) # ← AGREGAR
        )
        .where(PrestamoLibro.usuario_prestado_id == usuario_actual.id)
    )

    if solo_vigentes:
        query = query.where(
            PrestamoLibro.estado_prestamo_id.in_(
                [ESTADO_VIGENTE, ESTADO_PENDIENTE_DEVOLUCION]
            )
        )

    result    = await db.execute(query)
    prestamos = result.scalars().all()
    return [_serializar_prestamo(p) for p in prestamos]


@router.get("/{prestamo_id}", response_model=PrestamoLibroConRelaciones)
async def obtener_prestamo(
    prestamo_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    result = await db.execute(
        select(PrestamoLibro)
        .options(
            selectinload(PrestamoLibro.libro),
            selectinload(PrestamoLibro.usuario_presta),
            selectinload(PrestamoLibro.usuario_prestado),
            selectinload(PrestamoLibro.estado_prestamo),
            selectinload(PrestamoLibro.usuario_ultimo_cambio),
            selectinload(PrestamoLibro.aprobado_por)
        )
        .filter(PrestamoLibro.id == prestamo_id)
    )
    prestamo = result.scalar_one_or_none()
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return _serializar_prestamo(prestamo)


# =============================================
# CREAR PRÉSTAMO
# =============================================

@router.post("/", response_model=PrestamoLibroResponse)
async def crear_prestamo(
    prestamo_data: PrestamoLibroCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """Crear préstamo. Bloquea si el usuario tiene multas pendientes."""
    fecha_devolucion = to_naive(prestamo_data.fecha_devolucion_esperada)
    fecha_actual     = datetime.utcnow().replace(tzinfo=None) - timedelta(hours=6)

    try:
        await verificar_sin_multas_pendientes(db, prestamo_data.usuario_prestado_id)
        libro            = await verificar_libro_disponible(db, prestamo_data.libro_id)
        usuario_prestado = await verificar_usuario_activo(db, prestamo_data.usuario_prestado_id)

        libro.estado_id          = 2
        libro.fecha_cambio_estado = fecha_actual

        nuevo_prestamo = PrestamoLibro(
            libro_id                   = prestamo_data.libro_id,
            usuario_presta_id          = usuario_actual.id,
            usuario_prestado_id        = prestamo_data.usuario_prestado_id,
            estado_prestamo_id         = ESTADO_VIGENTE,
            fecha_prestamo             = fecha_actual,
            fecha_devolucion_esperada  = fecha_devolucion,
            usuario_ultimo_cambio_id   = usuario_actual.id,
            fecha_ultimo_cambio_estado = fecha_actual,
            observaciones              = prestamo_data.observaciones
        )

        db.add(nuevo_prestamo)
        await db.commit()
        await db.refresh(nuevo_prestamo)
        return nuevo_prestamo

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear préstamo: {str(e)}")


# =============================================
# NUEVO: SOLICITAR DEVOLUCIÓN (usuario)
# =============================================

@router.patch("/{prestamo_id}/solicitar-devolucion",
              response_model=SolicitudDevolucionResponse)
async def solicitar_devolucion(
    prestamo_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    El usuario solicita devolver su libro.

    - Cambia estado a 'Pendiente devolución' (5)
    - Registra fecha_solicitud_dev — este timestamp se usará para
      calcular días de retraso, no la fecha de aprobación del admin
    - Genera número de ticket único para presentar en el CID
    - El libro sigue en estado 'Prestado' hasta que el admin apruebe
    """
    try:
        result   = await db.execute(
            select(PrestamoLibro)
            .options(selectinload(PrestamoLibro.libro))
            .filter(PrestamoLibro.id == prestamo_id)
        )
        prestamo = result.scalar_one_or_none()

        if not prestamo:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")

        # Solo el dueño del préstamo puede solicitar la devolución
        if prestamo.usuario_prestado_id != usuario_actual.id:
            raise HTTPException(status_code=403,
                                detail="No puedes solicitar la devolución de un préstamo ajeno")

        # Solo préstamos vigentes pueden solicitar devolución
        if prestamo.estado_prestamo_id != ESTADO_VIGENTE:
            estados_msg = {
                ESTADO_PENDIENTE_DEVOLUCION: "Este préstamo ya tiene una solicitud de devolución pendiente",
                ESTADO_TERMINADO:            "Este préstamo ya fue devuelto",
                ESTADO_EXPIRADO:             "Este préstamo está expirado"
            }
            msg = estados_msg.get(prestamo.estado_prestamo_id,
                                  "Este préstamo no puede solicitar devolución")
            raise HTTPException(status_code=400, detail=msg)

        # ── Registrar solicitud ───────────────────────────────────────────
        fecha_solicitud = datetime.utcnow() - timedelta(hours=6)
        ticket          = generar_numero_ticket(prestamo.id, fecha_solicitud)

        prestamo.estado_prestamo_id        = ESTADO_PENDIENTE_DEVOLUCION
        prestamo.fecha_solicitud_dev       = fecha_solicitud
        prestamo.numero_ticket             = ticket
        prestamo.usuario_ultimo_cambio_id  = usuario_actual.id
        prestamo.fecha_ultimo_cambio_estado= fecha_solicitud

        await db.commit()
        await db.refresh(prestamo)

        return SolicitudDevolucionResponse(
            prestamo_id     = prestamo.id,
            numero_ticket   = ticket,
            fecha_solicitud = fecha_solicitud,
            libro_titulo    = prestamo.libro.titulo if prestamo.libro else None,
            mensaje         = (
                f"Solicitud registrada. Presenta el ticket #{ticket} "
                f"en el CID para completar la devolución."
            )
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Error al solicitar devolución: {str(e)}")


# =============================================
# NUEVO: APROBAR DEVOLUCIÓN (admin)
# =============================================

@router.patch("/{prestamo_id}/aprobar-devolucion",
              response_model=PrestamoDevolucionResponse)
async def aprobar_devolucion(
    prestamo_id: int,
    aprobacion_data: AprobacionDevolucionRequest,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    El admin aprueba la devolución de un préstamo.

    - Verifica que exista solicitud pendiente (estado 5)
    - Calcula días de retraso usando fecha_solicitud_dev
      (no la fecha actual — esto protege al usuario de retrasos del admin)
    - Genera multa si aplica ($5/día)
    - Libera el libro (estado → Disponible)
    - Cierra el préstamo (estado → Terminado)
    """
    try:
        result = await db.execute(
            select(PrestamoLibro)
            .options(selectinload(PrestamoLibro.libro))
            .filter(PrestamoLibro.id == prestamo_id)
        )
        prestamo = result.scalar_one_or_none()

        if not prestamo:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")

        if prestamo.estado_prestamo_id != ESTADO_PENDIENTE_DEVOLUCION:
            raise HTTPException(
                status_code=400,
                detail="Solo se pueden aprobar préstamos en estado 'Pendiente devolución'"
            )

        # ── Liberar libro ─────────────────────────────────────────────────
        result_libro = await db.execute(
            select(Libro).filter(Libro.id == prestamo.libro_id)
        )
        libro = result_libro.scalar_one_or_none()
        if libro:
            libro.estado_id           = 1   # Disponible
            libro.fecha_cambio_estado = datetime.utcnow() - timedelta(hours=6)

        # ── Calcular días de retraso ──────────────────────────────────────
        # CLAVE: se usa fecha_solicitud_dev, no datetime.now()
        # Así el admin no puede "cobrar más días" retrasando la aprobación
        fecha_base     = prestamo.fecha_solicitud_dev or (datetime.utcnow() - timedelta(hours=6))
        dias_excedidos = calcular_dias_excedidos(
            prestamo.fecha_devolucion_esperada,
            fecha_base
        )

        # ── Cerrar préstamo ───────────────────────────────────────────────
        fecha_aprobacion                    = datetime.utcnow() - timedelta(hours=6)
        prestamo.estado_prestamo_id         = ESTADO_TERMINADO
        prestamo.fecha_devolucion_real      = fecha_aprobacion
        prestamo.usuario_ultimo_cambio_id   = usuario_actual.id
        prestamo.fecha_ultimo_cambio_estado = fecha_aprobacion
        prestamo.aprobado_por_id            = usuario_actual.id
        prestamo.dias_excedidos             = dias_excedidos

        if aprobacion_data.observaciones:
            prestamo.observaciones = aprobacion_data.observaciones

        # ── Generar multa si hay retraso ──────────────────────────────────
        multa_generada = None
        if dias_excedidos > 0:
            multa_generada = await generar_multa_por_retraso(
                db               = db,
                prestamo         = prestamo,
                dias_excedidos   = dias_excedidos,
                usuario_admin_id = usuario_actual.id
            )

        await db.commit()
        await db.refresh(prestamo)
        if multa_generada:
            await db.refresh(multa_generada)

        multa_resumen = None
        if multa_generada:
            multa_resumen = MultaResumenEnDevolucion(
                id              = multa_generada.id,
                costo_monetario = multa_generada.costo_monetario,
                dias_excedidos  = dias_excedidos,
                observaciones   = multa_generada.observaciones
            )

        mensaje = (
            f"Devolución aprobada. Multa generada: "
            f"${multa_generada.costo_monetario} MXN "
            f"({dias_excedidos} día(s) × $5.00 MXN/día)."
            if multa_generada
            else "Devolución aprobada correctamente. Sin retraso."
        )

        return PrestamoDevolucionResponse(
            prestamo       = prestamo,
            multa_generada = multa_resumen,
            mensaje        = mensaje
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Error al aprobar devolución: {str(e)}")


# =============================================
# BUSCAR POR TICKET (admin)
# =============================================

@router.get("/ticket/{numero_ticket}",
            response_model=PrestamoLibroConRelaciones)
async def buscar_por_ticket(
    numero_ticket: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Busca un préstamo por número de ticket.
    El admin lo usa en el CID cuando el estudiante presenta su ticket.
    """
    result = await db.execute(
        select(PrestamoLibro)
        .options(
            selectinload(PrestamoLibro.libro),
            selectinload(PrestamoLibro.usuario_presta),
            selectinload(PrestamoLibro.usuario_prestado),
            selectinload(PrestamoLibro.estado_prestamo),
            selectinload(PrestamoLibro.aprobado_por)
        )
        .filter(PrestamoLibro.numero_ticket == numero_ticket)
    )
    prestamo = result.scalar_one_or_none()

    if not prestamo:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró ningún préstamo con el ticket #{numero_ticket}"
        )

    return _serializar_prestamo(prestamo)


@router.get("/usuario/{usuario_id}", response_model=List[PrestamoLibroConRelaciones])
async def listar_prestamos_usuario(
    usuario_id: int,
    solo_vigentes: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    query = select(PrestamoLibro).options(
        selectinload(PrestamoLibro.libro),
        selectinload(PrestamoLibro.usuario_presta),
        selectinload(PrestamoLibro.usuario_prestado),
        selectinload(PrestamoLibro.estado_prestamo)
    ).filter(PrestamoLibro.usuario_prestado_id == usuario_id)

    if solo_vigentes:
        query = query.where(
            PrestamoLibro.estado_prestamo_id.in_(
                [ESTADO_VIGENTE, ESTADO_PENDIENTE_DEVOLUCION]
            )
        )

    result    = await db.execute(query)
    prestamos = result.scalars().all()
    return [_serializar_prestamo(p) for p in prestamos]


# =============================================
# HELPER DE SERIALIZACIÓN
# =============================================

def _serializar_prestamo(prestamo: PrestamoLibro) -> dict:
    return {
        "id":                         prestamo.id,
        "libro_id":                   prestamo.libro_id,
        "usuario_presta_id":          prestamo.usuario_presta_id,
        "usuario_prestado_id":        prestamo.usuario_prestado_id,
        "estado_prestamo_id":         prestamo.estado_prestamo_id,
        "fecha_prestamo":             prestamo.fecha_prestamo,
        "fecha_devolucion_esperada":  prestamo.fecha_devolucion_esperada,
        "fecha_devolucion_real":      prestamo.fecha_devolucion_real,
        "usuario_ultimo_cambio_id":   prestamo.usuario_ultimo_cambio_id,
        "fecha_ultimo_cambio_estado": prestamo.fecha_ultimo_cambio_estado,
        "observaciones":              prestamo.observaciones,
        "dias_excedidos":             prestamo.dias_excedidos or 0,
        "numero_ticket":              prestamo.numero_ticket,
        "fecha_solicitud_dev":        prestamo.fecha_solicitud_dev,
        "aprobado_por_id":            prestamo.aprobado_por_id,
        "libro_titulo":               prestamo.libro.titulo         if prestamo.libro           else None,
        "libro_autor":                prestamo.libro.autor          if prestamo.libro           else None,
        "libro_codigo_decimal":       prestamo.libro.codigo_decimal if prestamo.libro           else None,
        "usuario_presta_nombre":      prestamo.usuario_presta.nombre_completo   if prestamo.usuario_presta   else None,
        "usuario_prestado_nombre":    prestamo.usuario_prestado.nombre_completo if prestamo.usuario_prestado else None,
        "estado_prestamo_nombre":     prestamo.estado_prestamo.estado           if prestamo.estado_prestamo  else None,
        "aprobado_por_nombre":        prestamo.aprobado_por.nombre_completo     if prestamo.aprobado_por     else None,
    }