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
    requerir_puede_prestar,
    requerir_puede_gestionar_recursos
)

router = APIRouter(prefix="/prestamos-libros", tags=["Préstamos de Libros"])

# =============================================
# CONSTANTES
# =============================================

COSTO_MULTA_POR_DIA   = Decimal('5.00')
TIPO_PAGO_ID_DEFAULT  = 1
TIPO_RECURSO_LIBRO_ID = 1

ESTADO_VIGENTE              = 1
ESTADO_EXPIRADO             = 2   # obsoleto en el nuevo flujo
ESTADO_TERMINADO            = 3
ESTADO_PENDIENTE_DEVOLUCION = 5   # flujo viejo — usuario solicita, admin aprueba


# =============================================
# FUNCIONES AUXILIARES
# =============================================

def _ahora():
    return datetime.utcnow() - timedelta(hours=6)

def to_naive(dt: datetime) -> datetime:
    if dt and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

def calcular_dias_excedidos(fecha_esperada: datetime, fecha_real: datetime) -> int:
    if not fecha_real:
        return 0
    return max(0, (fecha_real.date() - fecha_esperada.date()).days)

def generar_numero_ticket(prestamo_id: int, fecha: datetime) -> int:
    timestamp = fecha.strftime('%Y%m%d%H%M%S')
    return int(f"{timestamp}{prestamo_id:03d}")

def _opts():
    return [
        selectinload(PrestamoLibro.libro),
        selectinload(PrestamoLibro.usuario_presta),
        selectinload(PrestamoLibro.usuario_prestado),
        selectinload(PrestamoLibro.estado_prestamo),
        selectinload(PrestamoLibro.usuario_ultimo_cambio),
        selectinload(PrestamoLibro.aprobado_por),
    ]

def _serializar_prestamo(p: PrestamoLibro) -> dict:
    return {
        "id":                         p.id,
        "libro_id":                   p.libro_id,
        "usuario_presta_id":          p.usuario_presta_id,
        "usuario_prestado_id":        p.usuario_prestado_id,
        "estado_prestamo_id":         p.estado_prestamo_id,
        "fecha_prestamo":             p.fecha_prestamo,
        "fecha_devolucion_esperada":  p.fecha_devolucion_esperada,
        "fecha_devolucion_real":      p.fecha_devolucion_real,
        "usuario_ultimo_cambio_id":   p.usuario_ultimo_cambio_id,
        "fecha_ultimo_cambio_estado": p.fecha_ultimo_cambio_estado,
        "observaciones":              p.observaciones,
        "dias_excedidos":             p.dias_excedidos or 0,
        "numero_ticket":              p.numero_ticket,
        "fecha_solicitud_dev":        p.fecha_solicitud_dev,
        "aprobado_por_id":            p.aprobado_por_id,
        "libro_titulo":         p.libro.titulo         if p.libro           else None,
        "libro_autor":          p.libro.autor          if p.libro           else None,
        "libro_codigo_decimal": p.libro.codigo_decimal if p.libro           else None,
        "usuario_presta_nombre":   p.usuario_presta.nombre_completo   if p.usuario_presta   else None,
        "usuario_prestado_nombre": p.usuario_prestado.nombre_completo if p.usuario_prestado else None,
        "estado_prestamo_nombre":  p.estado_prestamo.estado           if p.estado_prestamo  else None,
        "aprobado_por_nombre":     p.aprobado_por.nombre_completo     if p.aprobado_por     else None,
    }

async def _get_o_404(db, prestamo_id):
    result = await db.execute(
        select(PrestamoLibro).options(*_opts()).filter(PrestamoLibro.id == prestamo_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return p

async def verificar_libro_disponible(db, libro_id):
    result = await db.execute(select(Libro).filter(Libro.id == libro_id))
    libro  = result.scalar_one_or_none()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    if libro.estado_id != 1:
        raise HTTPException(status_code=400, detail="El libro no está disponible para préstamo")
    if not libro.es_prestable:
        raise HTTPException(status_code=400, detail="El libro no es prestable")
    return libro

async def verificar_usuario_activo(db, usuario_id):
    result = await db.execute(
        select(Usuario).filter(and_(Usuario.id == usuario_id, Usuario.esta_activo == True))
    )
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario no válido para préstamo")
    return usuario

async def verificar_sin_multas_pendientes(db, usuario_id):
    cantidad = await db.scalar(
        select(func.count(Multa.id)).where(
            and_(Multa.usuario_multado_id == usuario_id, Multa.estado_multa_id == 1)
        )
    )
    if (cantidad or 0) > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"El usuario tiene {cantidad} multa(s) pendiente(s)."
        )

async def generar_multa_por_retraso(db, prestamo, dias_excedidos, usuario_admin_id):
    costo = Decimal(str(dias_excedidos)) * COSTO_MULTA_POR_DIA
    multa = Multa(
        usuario_multa_id           = usuario_admin_id,
        usuario_multado_id         = prestamo.usuario_prestado_id,
        estado_multa_id            = 1,
        fecha_multa                = _ahora(),
        usuario_ultimo_cambio_id   = usuario_admin_id,
        fecha_ultimo_cambio_estado = _ahora(),
        tipo_pago_id               = TIPO_PAGO_ID_DEFAULT,
        tipo_recurso_multa_id      = TIPO_RECURSO_LIBRO_ID,
        costo_monetario            = costo,
        observaciones              = (
            f"Multa automática — Préstamo #{prestamo.id}. "
            f"{dias_excedidos} día(s) × ${COSTO_MULTA_POR_DIA}/día = ${costo} MXN."
        )
    )
    db.add(multa)
    return multa


# ══════════════════════════════════════════════════════════════════════════
# ENDPOINTS ACTIVOS — NUEVO FLUJO (bibliotecario gestiona todo)
# ══════════════════════════════════════════════════════════════════════════

@router.get("/vigentes")
async def listar_vigentes(
    usuario_prestado_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(requerir_puede_prestar)
):
    """Préstamos vigentes. Incluye los vencidos — el frontend los diferencia por fecha."""
    query = (
        select(PrestamoLibro).options(*_opts())
        .where(PrestamoLibro.estado_prestamo_id == ESTADO_VIGENTE)
        .order_by(PrestamoLibro.fecha_devolucion_esperada.asc())
    )
    if usuario_prestado_id:
        query = query.where(PrestamoLibro.usuario_prestado_id == usuario_prestado_id)
    result = await db.execute(query)
    return [_serializar_prestamo(p) for p in result.scalars().all()]


@router.get("/historial")
async def listar_historial(
    skip: int = 0, limit: int = 100,
    usuario_prestado_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(requerir_puede_prestar)
):
    """Préstamos terminados — historial completo."""
    query = (
        select(PrestamoLibro).options(*_opts())
        .where(PrestamoLibro.estado_prestamo_id == ESTADO_TERMINADO)
        .order_by(PrestamoLibro.fecha_devolucion_real.desc())
        .offset(skip).limit(limit)
    )
    if usuario_prestado_id:
        query = query.where(PrestamoLibro.usuario_prestado_id == usuario_prestado_id)
    result = await db.execute(query)
    return [_serializar_prestamo(p) for p in result.scalars().all()]


@router.get("/mis-prestamos")
async def mis_prestamos(
    solo_vigentes: bool = True,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Préstamos del usuario autenticado — para Mi Perfil."""
    query = (
        select(PrestamoLibro).options(*_opts())
        .where(PrestamoLibro.usuario_prestado_id == usuario_actual.id)
    )
    if solo_vigentes:
        query = query.where(PrestamoLibro.estado_prestamo_id == ESTADO_VIGENTE)
    result = await db.execute(query)
    return [_serializar_prestamo(p) for p in result.scalars().all()]


@router.get("/{prestamo_id}")
async def obtener_prestamo(
    prestamo_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(requerir_puede_consultar)
):
    return _serializar_prestamo(await _get_o_404(db, prestamo_id))


@router.post("/", status_code=201)
async def crear_prestamo(
    data: PrestamoLibroCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_prestar)
):
    """
    NUEVO FLUJO: El bibliotecario registra el préstamo presencialmente.
    El estudiante entrega su credencial, el bibliotecario crea el préstamo.
    Libro → Prestado, Préstamo → Vigente directamente.
    """
    try:
        libro   = await verificar_libro_disponible(db, data.libro_id)
        usuario = await verificar_usuario_activo(db, data.usuario_prestado_id)
        await verificar_sin_multas_pendientes(db, data.usuario_prestado_id)

        fecha = _ahora()
        libro.estado_id = 2

        nuevo = PrestamoLibro(
            libro_id                   = data.libro_id,
            usuario_presta_id          = usuario_actual.id,
            usuario_prestado_id        = data.usuario_prestado_id,
            estado_prestamo_id         = ESTADO_VIGENTE,
            fecha_prestamo             = fecha,
            fecha_devolucion_esperada  = to_naive(data.fecha_devolucion_esperada),
            usuario_ultimo_cambio_id   = usuario_actual.id,
            fecha_ultimo_cambio_estado = fecha,
            observaciones              = data.observaciones,
            dias_excedidos             = 0
        )
        db.add(nuevo)
        await db.commit()
        await db.refresh(nuevo)
        return _serializar_prestamo(await _get_o_404(db, nuevo.id))

    except HTTPException:
        await db.rollback(); raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear préstamo: {str(e)}")


@router.patch("/{prestamo_id}/devolver")
async def registrar_devolucion(
    prestamo_id: int,
    data: PrestamoLibroDevolucion = None,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_prestar)
):
    """
    NUEVO FLUJO: El bibliotecario registra la devolución cuando el estudiante
    regresa el libro físicamente al CID.
    - Calcula días de retraso automáticamente
    - Genera multa automática si aplica ($5/día)
    - Libro → Disponible, Préstamo → Terminado
    """
    try:
        prestamo = await _get_o_404(db, prestamo_id)
        if prestamo.estado_prestamo_id != ESTADO_VIGENTE:
            raise HTTPException(status_code=400, detail="Solo préstamos vigentes pueden devolverse")

        fecha = _ahora()
        dias  = calcular_dias_excedidos(prestamo.fecha_devolucion_esperada, fecha)

        libro = (await db.execute(select(Libro).filter(Libro.id == prestamo.libro_id))).scalar_one_or_none()
        if libro:
            libro.estado_id = 1

        prestamo.estado_prestamo_id         = ESTADO_TERMINADO
        prestamo.fecha_devolucion_real       = fecha
        prestamo.usuario_ultimo_cambio_id    = usuario_actual.id
        prestamo.fecha_ultimo_cambio_estado  = fecha
        prestamo.dias_excedidos              = dias
        if data and data.observaciones:
            prestamo.observaciones = data.observaciones

        multa = None
        if dias > 0:
            multa = await generar_multa_por_retraso(db, prestamo, dias, usuario_actual.id)

        await db.commit()
        if multa:
            await db.refresh(multa)

        return {
            "prestamo":       _serializar_prestamo(await _get_o_404(db, prestamo_id)),
            "multa_generada": {"id": multa.id, "costo_monetario": float(multa.costo_monetario), "dias_excedidos": dias} if multa else None,
            "mensaje":        f"Devolución registrada. Multa: ${multa.costo_monetario} MXN ({dias} día(s))." if multa else "Devolución registrada sin retraso."
        }

    except HTTPException:
        await db.rollback(); raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar devolución: {str(e)}")


# ══════════════════════════════════════════════════════════════════════════
# ENDPOINTS COMENTADOS — FLUJO VIEJO (usuario solicita, admin aprueba)
# Se conservan como referencia. No están activos.
# Discutir antes de eliminar definitivamente.
# ══════════════════════════════════════════════════════════════════════════

# @router.get("/", response_model=List[PrestamoLibroConRelaciones])
# async def listar_prestamos(
#     skip: int = 0, limit: int = 100,
#     estado_prestamo_id: Optional[int] = Query(None),
#     libro_id: Optional[int] = Query(None),
#     usuario_prestado_id: Optional[int] = Query(None),
#     db: AsyncSession = Depends(get_db),
#     usuario_actual: Usuario = Depends(requerir_puede_consultar)
# ):
#     """Lista todos los préstamos con filtros opcionales."""
#     try:
#         query = select(PrestamoLibro).options(*_opts())
#         if estado_prestamo_id:
#             query = query.where(PrestamoLibro.estado_prestamo_id == estado_prestamo_id)
#         if libro_id:
#             query = query.where(PrestamoLibro.libro_id == libro_id)
#         if usuario_prestado_id:
#             query = query.where(PrestamoLibro.usuario_prestado_id == usuario_prestado_id)
#         query  = query.offset(skip).limit(limit)
#         result = await db.execute(query)
#         return [_serializar_prestamo(p) for p in result.scalars().all()]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error al listar préstamos: {str(e)}")


# @router.get("/pendientes-devolucion", response_model=List[PrestamoLibroConRelaciones])
# async def listar_pendientes_devolucion(
#     skip: int = 0, limit: int = 100,
#     db: AsyncSession = Depends(get_db),
#     usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
# ):
#     """
#     FLUJO VIEJO: Lista préstamos en estado 'Pendiente devolución' (5).
#     El admin los aprueba uno a uno desde el panel de devoluciones.
#     """
#     try:
#         query = (
#             select(PrestamoLibro).options(*_opts())
#             .where(PrestamoLibro.estado_prestamo_id == ESTADO_PENDIENTE_DEVOLUCION)
#             .order_by(PrestamoLibro.fecha_solicitud_dev.asc())
#             .offset(skip).limit(limit)
#         )
#         result = await db.execute(query)
#         return [_serializar_prestamo(p) for p in result.scalars().all()]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# @router.patch("/{prestamo_id}/solicitar-devolucion",
#               response_model=SolicitudDevolucionResponse)
# async def solicitar_devolucion(
#     prestamo_id: int,
#     db: AsyncSession = Depends(get_db),
#     usuario_actual: Usuario = Depends(obtener_usuario_actual)
# ):
#     """
#     FLUJO VIEJO: El usuario solicita devolver su libro desde la app.
#     - Genera número de ticket único (YYYYMMDDHHMMSS + id)
#     - Cambia estado a 'Pendiente devolución' (5)
#     - Registra fecha_solicitud_dev — se usa para calcular retraso,
#       no la fecha en que el admin aprueba (protección al usuario)
#     - El libro sigue en estado Prestado hasta que el admin apruebe
#     """
#     try:
#         result   = await db.execute(
#             select(PrestamoLibro).options(selectinload(PrestamoLibro.libro))
#             .filter(PrestamoLibro.id == prestamo_id)
#         )
#         prestamo = result.scalar_one_or_none()
#         if not prestamo:
#             raise HTTPException(status_code=404, detail="Préstamo no encontrado")
#         if prestamo.usuario_prestado_id != usuario_actual.id:
#             raise HTTPException(status_code=403, detail="No puedes solicitar la devolución de un préstamo ajeno")
#         if prestamo.estado_prestamo_id != ESTADO_VIGENTE:
#             estados_msg = {
#                 ESTADO_PENDIENTE_DEVOLUCION: "Este préstamo ya tiene una solicitud pendiente",
#                 ESTADO_TERMINADO:            "Este préstamo ya fue devuelto",
#                 ESTADO_EXPIRADO:             "Este préstamo está expirado"
#             }
#             raise HTTPException(status_code=400,
#                 detail=estados_msg.get(prestamo.estado_prestamo_id, "No puede solicitar devolución"))
#
#         fecha_solicitud = _ahora()
#         ticket          = generar_numero_ticket(prestamo.id, fecha_solicitud)
#
#         prestamo.estado_prestamo_id         = ESTADO_PENDIENTE_DEVOLUCION
#         prestamo.fecha_solicitud_dev        = fecha_solicitud
#         prestamo.numero_ticket              = ticket
#         prestamo.usuario_ultimo_cambio_id   = usuario_actual.id
#         prestamo.fecha_ultimo_cambio_estado = fecha_solicitud
#
#         await db.commit()
#         await db.refresh(prestamo)
#
#         return SolicitudDevolucionResponse(
#             prestamo_id     = prestamo.id,
#             numero_ticket   = ticket,
#             fecha_solicitud = fecha_solicitud,
#             libro_titulo    = prestamo.libro.titulo if prestamo.libro else None,
#             mensaje         = f"Solicitud registrada. Presenta el ticket #{ticket} en el CID."
#         )
#     except HTTPException:
#         await db.rollback(); raise
#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(status_code=500, detail=f"Error al solicitar devolución: {str(e)}")


# @router.patch("/{prestamo_id}/aprobar-devolucion",
#               response_model=PrestamoDevolucionResponse)
# async def aprobar_devolucion(
#     prestamo_id: int,
#     aprobacion_data: AprobacionDevolucionRequest,
#     db: AsyncSession = Depends(get_db),
#     usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
# ):
#     """
#     FLUJO VIEJO: El admin aprueba la devolución de un préstamo en estado 5.
#     - Calcula días usando fecha_solicitud_dev (no la fecha actual)
#       → el admin no puede "cobrar más días" retrasando la aprobación
#     - Genera multa automática si hay retraso ($5/día)
#     - Libro → Disponible, Préstamo → Terminado
#     """
#     try:
#         result   = await db.execute(
#             select(PrestamoLibro).options(selectinload(PrestamoLibro.libro))
#             .filter(PrestamoLibro.id == prestamo_id)
#         )
#         prestamo = result.scalar_one_or_none()
#         if not prestamo:
#             raise HTTPException(status_code=404, detail="Préstamo no encontrado")
#         if prestamo.estado_prestamo_id != ESTADO_PENDIENTE_DEVOLUCION:
#             raise HTTPException(status_code=400,
#                 detail="Solo préstamos en estado 'Pendiente devolución' pueden aprobarse")
#
#         libro_result = await db.execute(select(Libro).filter(Libro.id == prestamo.libro_id))
#         libro = libro_result.scalar_one_or_none()
#         if libro:
#             libro.estado_id = 1
#
#         # CLAVE: usar fecha_solicitud_dev, no ahora()
#         fecha_base     = prestamo.fecha_solicitud_dev or _ahora()
#         dias_excedidos = calcular_dias_excedidos(prestamo.fecha_devolucion_esperada, fecha_base)
#
#         fecha_aprobacion                    = _ahora()
#         prestamo.estado_prestamo_id         = ESTADO_TERMINADO
#         prestamo.fecha_devolucion_real       = fecha_aprobacion
#         prestamo.usuario_ultimo_cambio_id    = usuario_actual.id
#         prestamo.fecha_ultimo_cambio_estado  = fecha_aprobacion
#         prestamo.aprobado_por_id             = usuario_actual.id
#         prestamo.dias_excedidos              = dias_excedidos
#         if aprobacion_data.observaciones:
#             prestamo.observaciones = aprobacion_data.observaciones
#
#         multa_generada = None
#         if dias_excedidos > 0:
#             multa_generada = await generar_multa_por_retraso(db, prestamo, dias_excedidos, usuario_actual.id)
#
#         await db.commit()
#         await db.refresh(prestamo)
#         if multa_generada:
#             await db.refresh(multa_generada)
#
#         multa_resumen = None
#         if multa_generada:
#             multa_resumen = MultaResumenEnDevolucion(
#                 id=multa_generada.id,
#                 costo_monetario=multa_generada.costo_monetario,
#                 dias_excedidos=dias_excedidos,
#                 observaciones=multa_generada.observaciones
#             )
#
#         return PrestamoDevolucionResponse(
#             prestamo       = prestamo,
#             multa_generada = multa_resumen,
#             mensaje        = f"Devolución aprobada. Multa: ${multa_generada.costo_monetario} MXN ({dias_excedidos}d)."
#                              if multa_generada else "Devolución aprobada. Sin retraso."
#         )
#     except HTTPException:
#         await db.rollback(); raise
#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(status_code=500, detail=f"Error al aprobar devolución: {str(e)}")


# @router.get("/ticket/{numero_ticket}", response_model=PrestamoLibroConRelaciones)
# async def buscar_por_ticket(
#     numero_ticket: int,
#     db: AsyncSession = Depends(get_db),
#     usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
# ):
#     """
#     FLUJO VIEJO: El admin busca un préstamo por número de ticket.
#     El estudiante presenta su ticket en el CID y el admin lo busca aquí.
#     """
#     result = await db.execute(
#         select(PrestamoLibro).options(*_opts())
#         .filter(PrestamoLibro.numero_ticket == numero_ticket)
#     )
#     prestamo = result.scalar_one_or_none()
#     if not prestamo:
#         raise HTTPException(status_code=404,
#             detail=f"No se encontró ningún préstamo con el ticket #{numero_ticket}")
#     return _serializar_prestamo(prestamo)


# @router.get("/usuario/{usuario_id}", response_model=List[PrestamoLibroConRelaciones])
# async def listar_prestamos_usuario(
#     usuario_id: int,
#     solo_vigentes: bool = Query(True),
#     db: AsyncSession = Depends(get_db),
#     usuario_actual: Usuario = Depends(requerir_puede_consultar)
# ):
#     """FLUJO VIEJO: Lista préstamos de un usuario específico por su ID."""
#     query = select(PrestamoLibro).options(*_opts()).filter(
#         PrestamoLibro.usuario_prestado_id == usuario_id
#     )
#     if solo_vigentes:
#         query = query.where(
#             PrestamoLibro.estado_prestamo_id.in_([ESTADO_VIGENTE, ESTADO_PENDIENTE_DEVOLUCION])
#         )
#     result = await db.execute(query)
#     return [_serializar_prestamo(p) for p in result.scalars().all()]