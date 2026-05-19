from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta

from config.database import get_db
from models.prestamos_area import PrestamoArea
from models.areas import Area
from models.usuarios import Usuario
from schemas.prestamos_area import (
    PrestamoAreaCreate,
    PrestamoAreaResponse,
    PrestamoAreaConRelaciones,
    PrestamoAreaDevolucion
)
from core.security import (
    obtener_usuario_actual,
    requerir_puede_consultar,
    requerir_puede_prestar,
    requerir_puede_gestionar_recursos
)

router = APIRouter(prefix="/prestamos-areas", tags=["Préstamos de Áreas"])

ESTADO_PRESTAMO_VIGENTE  = 1
ESTADO_PRESTAMO_TERMINADO = 3
ESTADO_AREA_DISPONIBLE   = 1
ESTADO_AREA_OCUPADA      = 2

def _ahora():
    return datetime.utcnow() - timedelta(hours=6)

def calcular_tiempo_excedido(fecha_esperada: datetime, fecha_real: datetime) -> timedelta:
    if not fecha_real:
        return timedelta(0)
    diff = fecha_real - fecha_esperada
    return timedelta(0) if diff <= timedelta(0) else diff

def _serializar(p: PrestamoArea) -> dict:
    te = p.tiempo_excedido
    return {
        "id":                         p.id,
        "area_id":                    p.area_id,
        "usuario_presta_id":          p.usuario_presta_id,
        "usuario_prestado_id":        p.usuario_prestado_id,
        "estado_prestamo_id":         p.estado_prestamo_id,
        "fecha_prestamo":             p.fecha_prestamo,
        "fecha_devolucion_esperada":  p.fecha_devolucion_esperada,
        "fecha_devolucion_real":      p.fecha_devolucion_real,
        "usuario_ultimo_cambio_id":   p.usuario_ultimo_cambio_id,
        "fecha_ultimo_cambio_estado": p.fecha_ultimo_cambio_estado,
        "observaciones":              p.observaciones,
        "tiempo_excedido":            te,
        "horas_excedidas":            round(te.total_seconds() / 3600, 2) if te else 0.0,
        "area_nombre":                p.area.nombre    if p.area           else None,
        "area_capacidad":             p.area.capacidad if p.area           else None,
        "usuario_presta_nombre":      p.usuario_presta.nombre_completo   if p.usuario_presta   else None,
        "usuario_prestado_nombre":    p.usuario_prestado.nombre_completo if p.usuario_prestado else None,
        "usuario_ultimo_cambio_nombre": p.usuario_ultimo_cambio.nombre_completo if p.usuario_ultimo_cambio else None,
        "estado_prestamo_nombre":     p.estado_prestamo.estado if p.estado_prestamo else None,
    }

def _opts():
    return [
        selectinload(PrestamoArea.area),
        selectinload(PrestamoArea.usuario_presta),
        selectinload(PrestamoArea.usuario_prestado),
        selectinload(PrestamoArea.estado_prestamo),
        selectinload(PrestamoArea.usuario_ultimo_cambio),
    ]

async def _get_o_404(db, prestamo_id):
    result = await db.execute(
        select(PrestamoArea).options(*_opts()).filter(PrestamoArea.id == prestamo_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Préstamo de área no encontrado")
    return p

# ══════════════════════════════════════════════════════════════════════════
# CONSULTAS
# ══════════════════════════════════════════════════════════════════════════

@router.get("/vigentes")
async def listar_vigentes(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(requerir_puede_prestar)
):
    """Préstamos vigentes de áreas. El frontend calcula tiempo restante."""
    result = await db.execute(
        select(PrestamoArea).options(*_opts())
        .where(PrestamoArea.estado_prestamo_id == ESTADO_PRESTAMO_VIGENTE)
        .order_by(PrestamoArea.fecha_devolucion_esperada.asc())
    )
    return [_serializar(p) for p in result.scalars().all()]


@router.get("/historial")
async def listar_historial(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(requerir_puede_prestar)
):
    """Historial completo de préstamos terminados."""
    result = await db.execute(
        select(PrestamoArea).options(*_opts())
        .where(PrestamoArea.estado_prestamo_id == ESTADO_PRESTAMO_TERMINADO)
        .order_by(PrestamoArea.fecha_devolucion_real.desc())
        .offset(skip).limit(limit)
    )
    return [_serializar(p) for p in result.scalars().all()]


@router.get("/{prestamo_id}")
async def obtener_prestamo(
    prestamo_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(requerir_puede_consultar)
):
    return _serializar(await _get_o_404(db, prestamo_id))


# ══════════════════════════════════════════════════════════════════════════
# CREAR — bibliotecario registra presencialmente (nivel 2+)
# Directo a Vigente — sin flujo pendiente/aprobación
# ══════════════════════════════════════════════════════════════════════════

@router.post("/", status_code=201)
async def crear_prestamo_area(
    data: PrestamoAreaCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_prestar)
):
    """
    El bibliotecario registra el préstamo cuando el estudiante ocupa el área.
    - Área → Ocupada (estado 2)
    - Préstamo → Vigente (estado 1) directamente, sin aprobación
    """
    try:
        # Verificar área disponible y prestable
        area_result = await db.execute(select(Area).filter(Area.id == data.area_id))
        area = area_result.scalar_one_or_none()
        if not area:
            raise HTTPException(status_code=404, detail="Área no encontrada")
        if area.estado_id != ESTADO_AREA_DISPONIBLE:
            raise HTTPException(status_code=400, detail="El área no está disponible")
        if not area.es_prestable:
            raise HTTPException(status_code=400, detail="El área no es prestable")

        # Verificar que el área no tenga préstamos vigentes
        existe = await db.scalar(
            select(func.count(PrestamoArea.id)).where(
                and_(
                    PrestamoArea.area_id == data.area_id,
                    PrestamoArea.estado_prestamo_id == ESTADO_PRESTAMO_VIGENTE
                )
            )
        )
        if (existe or 0) > 0:
            raise HTTPException(status_code=400, detail="El área ya tiene un préstamo activo")

        # Verificar usuario activo
        usuario_result = await db.execute(
            select(Usuario).filter(and_(Usuario.id == data.usuario_prestado_id, Usuario.esta_activo == True))
        )
        if not usuario_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Usuario no válido")

        fecha = _ahora()
        area.estado_id                  = ESTADO_AREA_OCUPADA
        area.fecha_ultimo_cambio_estado = fecha

        nuevo = PrestamoArea(
            area_id                    = data.area_id,
            usuario_presta_id          = usuario_actual.id,
            usuario_prestado_id        = data.usuario_prestado_id,
            estado_prestamo_id         = ESTADO_PRESTAMO_VIGENTE,
            fecha_prestamo             = fecha,
            fecha_devolucion_esperada  = data.fecha_devolucion_esperada,
            usuario_ultimo_cambio_id   = usuario_actual.id,
            fecha_ultimo_cambio_estado = fecha,
            observaciones              = data.observaciones,
            tiempo_excedido            = None,
        )
        db.add(nuevo)
        await db.commit()
        await db.refresh(nuevo)
        return _serializar(await _get_o_404(db, nuevo.id))

    except HTTPException:
        await db.rollback(); raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear préstamo: {str(e)}")


# ══════════════════════════════════════════════════════════════════════════
# DEVOLVER — bibliotecario registra la devolución (nivel 2+)
# ══════════════════════════════════════════════════════════════════════════

@router.patch("/{prestamo_id}/devolver")
async def devolver_prestamo_area(
    prestamo_id: int,
    data: PrestamoAreaDevolucion,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_prestar)
):
    """
    El bibliotecario registra la devolución del área.
    Calcula tiempo excedido si aplica (sin multa).
    """
    try:
        prestamo = await _get_o_404(db, prestamo_id)
        if prestamo.estado_prestamo_id != ESTADO_PRESTAMO_VIGENTE:
            raise HTTPException(status_code=400, detail="Solo préstamos vigentes pueden devolverse")

        fecha = _ahora()

        # Área → Disponible
        area_result = await db.execute(select(Area).filter(Area.id == prestamo.area_id))
        area = area_result.scalar_one_or_none()
        if area:
            area.estado_id                  = ESTADO_AREA_DISPONIBLE
            area.fecha_ultimo_cambio_estado = fecha

        prestamo.estado_prestamo_id         = ESTADO_PRESTAMO_TERMINADO
        prestamo.fecha_devolucion_real       = fecha
        prestamo.usuario_ultimo_cambio_id    = usuario_actual.id
        prestamo.fecha_ultimo_cambio_estado  = fecha
        prestamo.tiempo_excedido            = calcular_tiempo_excedido(
            prestamo.fecha_devolucion_esperada, fecha
        )
        if data and data.observaciones:
            prestamo.observaciones = data.observaciones

        await db.commit()
        return _serializar(await _get_o_404(db, prestamo_id))

    except HTTPException:
        await db.rollback(); raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al devolver área: {str(e)}")

##############################################################
# HELPER PARA MOSTRAR PRESTAMOS DE AREA   ACTIVOS EN USUARIO #
##############################################################

@router.get("/usuario/{usuario_id}")
async def prestamos_por_usuario_area(
    usuario_id: int,
    solo_vigentes: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(requerir_puede_consultar)
):
    query = (
        select(PrestamoArea).options(*_opts())
        .where(PrestamoArea.usuario_prestado_id == usuario_id)
    )
    if solo_vigentes:
        query = query.where(PrestamoArea.estado_prestamo_id == ESTADO_PRESTAMO_VIGENTE)
    result = await db.execute(query)
    return [_serializar(p) for p in result.scalars().all()]

# ══════════════════════════════════════════════════════════════════════════
# ENDPOINTS COMENTADOS — FLUJO VIEJO (solicitar/aprobar/rechazar)
# Preservados como referencia hasta decidir eliminarlos
# ══════════════════════════════════════════════════════════════════════════

# @router.get("/pendientes")
# async def listar_pendientes(...):
#     """FLUJO VIEJO: Lista áreas en estado Pendiente (2) esperando aprobación del admin."""
#     ...

# @router.patch("/{prestamo_id}/aprobar")
# async def aprobar_solicitud_area(...):
#     """
#     FLUJO VIEJO: El admin aprueba la solicitud.
#     Área: Reservada (4) → Ocupada (2). Préstamo: Pendiente (2) → Vigente (1).
#     """
#     ...

# @router.patch("/{prestamo_id}/rechazar")
# async def rechazar_solicitud_area(...):
#     """
#     FLUJO VIEJO: El admin rechaza la solicitud.
#     Área: Reservada (4) → Disponible (1). Préstamo: Pendiente (2) → Terminado (3).
#     """
#     ...