from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta

from config.database import get_db
from models.prestamos_equipo_computo import PrestamoEquipoComputo
from models.equipos_computo import EquipoComputo
from models.usuarios import Usuario
from schemas.prestamos_equipo_computo import (
    PrestamoEquipoComputoCreate,
    PrestamoEquipoComputoResponse,
    PrestamoEquipoComputoConRelaciones,
    PrestamoEquipoComputoUpdate,
    PrestamoEquipoComputoDevolucion
)
from core.security import (
    obtener_usuario_actual,
    requerir_puede_consultar,
    requerir_puede_prestar,           # nivel 2+ — bibliotecario
    requerir_puede_gestionar_recursos  # nivel 3+ — admin avanzado
)

router = APIRouter(prefix="/prestamos-equipos-computo", tags=["Préstamos de Equipos de Cómputo"])

ESTADO_VIGENTE   = 1
ESTADO_TERMINADO = 3

def _ahora():
    return datetime.utcnow() - timedelta(hours=6)

def _serializar(prestamo: PrestamoEquipoComputo) -> dict:
    marca_nombre = None
    tipo_nombre  = None
    numero_serie = None
    modelo       = None

    if prestamo.equipo_computo:
        numero_serie = prestamo.equipo_computo.numero_serie
        modelo       = prestamo.equipo_computo.modelo
        if prestamo.equipo_computo.marca_equipo:
            marca_nombre = prestamo.equipo_computo.marca_equipo.marca
        if prestamo.equipo_computo.tipo_equipo:
            tipo_nombre = prestamo.equipo_computo.tipo_equipo.tipo

    return {
        "id":                         prestamo.id,
        "equipos_computo_id":         prestamo.equipos_computo_id,
        "usuario_presta_id":          prestamo.usuario_presta_id,
        "usuario_prestado_id":        prestamo.usuario_prestado_id,
        "estado_prestamo_id":         prestamo.estado_prestamo_id,
        "fecha_prestamo":             prestamo.fecha_prestamo,
        "fecha_devolucion":           prestamo.fecha_devolucion,
        "usuario_ultimo_cambio_id":   prestamo.usuario_ultimo_cambio_id,
        "fecha_ultimo_cambio_estado": prestamo.fecha_ultimo_cambio_estado,
        "observaciones":              prestamo.observaciones,
        "equipo_numero_serie":        numero_serie,
        "equipo_marca":               marca_nombre,
        "equipo_modelo":              modelo,
        "equipo_tipo":                tipo_nombre,
        "usuario_presta_nombre":      prestamo.usuario_presta.nombre_completo   if prestamo.usuario_presta   else None,
        "usuario_prestado_nombre":    prestamo.usuario_prestado.nombre_completo if prestamo.usuario_prestado else None,
        "estado_prestamo_nombre":     prestamo.estado_prestamo.estado           if prestamo.estado_prestamo  else None,
    }

def _opts():
    return [
        selectinload(PrestamoEquipoComputo.equipo_computo).selectinload(EquipoComputo.marca_equipo),
        selectinload(PrestamoEquipoComputo.equipo_computo).selectinload(EquipoComputo.tipo_equipo),
        selectinload(PrestamoEquipoComputo.usuario_presta),
        selectinload(PrestamoEquipoComputo.usuario_prestado),
        selectinload(PrestamoEquipoComputo.estado_prestamo),
        selectinload(PrestamoEquipoComputo.usuario_ultimo_cambio),
    ]

async def _get_o_404(db, prestamo_id):
    result = await db.execute(
        select(PrestamoEquipoComputo).options(*_opts()).filter(PrestamoEquipoComputo.id == prestamo_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Préstamo de equipo no encontrado")
    return p

# ══════════════════════════════════════════════════════════════════════════
# CONSULTAS
# ══════════════════════════════════════════════════════════════════════════

@router.get("/vigentes")
async def listar_vigentes(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(requerir_puede_prestar)
):
    """Préstamos vigentes de equipos. El frontend calcula el tiempo restante."""
    result = await db.execute(
        select(PrestamoEquipoComputo).options(*_opts())
        .where(PrestamoEquipoComputo.estado_prestamo_id == ESTADO_VIGENTE)
        .order_by(PrestamoEquipoComputo.fecha_devolucion.asc())
    )
    return [_serializar(p) for p in result.scalars().all()]


@router.get("/historial")
async def listar_historial(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(requerir_puede_prestar)
):
    """Historial de préstamos terminados."""
    result = await db.execute(
        select(PrestamoEquipoComputo).options(*_opts())
        .where(PrestamoEquipoComputo.estado_prestamo_id == ESTADO_TERMINADO)
        .order_by(PrestamoEquipoComputo.fecha_devolucion.desc())
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
# ══════════════════════════════════════════════════════════════════════════

@router.post("/", status_code=201)
async def crear_prestamo_equipo(
    data: PrestamoEquipoComputoCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_prestar)  # nivel 2+
):
    """
    El bibliotecario registra el préstamo cuando el estudiante recibe el equipo.
    - Equipo → Prestado (estado 2)
    - Préstamo → Vigente (estado 1)
    - fecha_devolucion indica cuándo debe regresar (en horas)
    """
    try:
        # Verificar equipo disponible y prestable
        equipo_result = await db.execute(select(EquipoComputo).filter(EquipoComputo.id == data.equipos_computo_id))
        equipo = equipo_result.scalar_one_or_none()
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        if equipo.estado_id != 1:
            raise HTTPException(status_code=400, detail="El equipo no está disponible")
        if not equipo.es_prestable:
            raise HTTPException(status_code=400, detail="El equipo no es prestable")

        # Verificar usuario activo
        usuario_result = await db.execute(
            select(Usuario).filter(and_(Usuario.id == data.usuario_prestado_id, Usuario.esta_activo == True))
        )
        if not usuario_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Usuario no válido")

        fecha = _ahora()
        equipo.estado_id                  = 2  # Prestado
        equipo.fecha_ultimo_cambio_estado = fecha

        nuevo = PrestamoEquipoComputo(
            equipos_computo_id         = data.equipos_computo_id,
            usuario_presta_id          = usuario_actual.id,
            usuario_prestado_id        = data.usuario_prestado_id,
            estado_prestamo_id         = ESTADO_VIGENTE,
            fecha_prestamo             = fecha,
            fecha_devolucion           = data.fecha_devolucion,
            usuario_ultimo_cambio_id   = usuario_actual.id,
            fecha_ultimo_cambio_estado = fecha,
            observaciones              = data.observaciones,
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
async def devolver_prestamo_equipo(
    prestamo_id: int,
    data: PrestamoEquipoComputoDevolucion,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_prestar)
):
    """
    El bibliotecario registra la devolución del equipo.
    No genera multa — el exceso de tiempo queda registrado en el historial.
    """
    try:
        prestamo = await _get_o_404(db, prestamo_id)
        if prestamo.estado_prestamo_id != ESTADO_VIGENTE:
            raise HTTPException(status_code=400, detail="Solo préstamos vigentes pueden devolverse")

        fecha = _ahora()

        # Equipo → Disponible
        equipo_result = await db.execute(select(EquipoComputo).filter(EquipoComputo.id == prestamo.equipos_computo_id))
        equipo = equipo_result.scalar_one_or_none()
        if equipo:
            equipo.estado_id                  = 1
            equipo.fecha_ultimo_cambio_estado = fecha

        prestamo.estado_prestamo_id         = ESTADO_TERMINADO
        prestamo.fecha_devolucion           = fecha   # sobreescribe con hora real
        prestamo.usuario_ultimo_cambio_id   = usuario_actual.id
        prestamo.fecha_ultimo_cambio_estado = fecha
        if data and data.observaciones:
            prestamo.observaciones = data.observaciones

        await db.commit()
        return _serializar(await _get_o_404(db, prestamo_id))

    except HTTPException:
        await db.rollback(); raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al devolver equipo: {str(e)}")
    

##############################################################
# HELPER PARA MOSTRAR PRESTAMOS DE EQUIPO ACTIVOS EN USUARIO #
##############################################################

@router.get("/usuario/{usuario_id}")
async def prestamos_por_usuario_equipo(
    usuario_id: int,
    solo_vigentes: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(requerir_puede_consultar)
):
    query = (
        select(PrestamoEquipoComputo).options(*_opts())
        .where(PrestamoEquipoComputo.usuario_prestado_id == usuario_id)
    )
    if solo_vigentes:
        query = query.where(PrestamoEquipoComputo.estado_prestamo_id == ESTADO_VIGENTE)
    result = await db.execute(query)
    return [_serializar(p) for p in result.scalars().all()]    