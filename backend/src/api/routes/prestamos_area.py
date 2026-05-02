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
from models.base import EstadoPrestamo
from schemas.prestamos_area import (
    PrestamoAreaCreate,
    PrestamoAreaResponse,
    PrestamoAreaConRelaciones,
    PrestamoAreaUpdate,
    PrestamoAreaDevolucion
)
from core.security import (
    obtener_usuario_actual,
    requerir_puede_consultar,
    requerir_puede_gestionar_recursos
)

router = APIRouter(prefix="/prestamos-areas", tags=["Préstamos de Áreas"])

# =============================================
# CONSTANTES DE ESTADO
# =============================================

# Estados de préstamo de área
ESTADO_PRESTAMO_VIGENTE   = 1   # Área ocupada — aprobado por admin
ESTADO_PRESTAMO_PENDIENTE = 2   # Área reservada — esperando aprobación
ESTADO_PRESTAMO_TERMINADO = 3   # Devuelto — área disponible

# Estados del área (estados_area)
ESTADO_AREA_DISPONIBLE  = 1
ESTADO_AREA_OCUPADA     = 2
ESTADO_AREA_RESERVADA   = 4   # Cuando el usuario solicita, antes de aprobación


# =============================================
# FUNCIONES AUXILIARES
# =============================================

def calcular_tiempo_excedido(fecha_esperada: datetime, fecha_real: datetime) -> timedelta:
    if not fecha_real:
        return timedelta(0)
    diferencia = fecha_real - fecha_esperada
    return timedelta(0) if diferencia <= timedelta(0) else diferencia


async def verificar_area_disponible(db: AsyncSession, area_id: int) -> Area:
    result = await db.execute(select(Area).filter(Area.id == area_id))
    area   = result.scalar_one_or_none()

    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")
    if area.estado_id != ESTADO_AREA_DISPONIBLE:
        raise HTTPException(
            status_code=400,
            detail="El área no está disponible para reserva"
        )
    if not area.es_prestable:
        raise HTTPException(status_code=400, detail="El área no es prestable")
    return area


async def verificar_area_sin_solicitudes(db: AsyncSession, area_id: int):
    """Verifica que el área no tenga préstamos vigentes o pendientes."""
    result = await db.execute(
        select(PrestamoArea).filter(
            and_(
                PrestamoArea.area_id == area_id,
                PrestamoArea.estado_prestamo_id.in_(
                    [ESTADO_PRESTAMO_VIGENTE, ESTADO_PRESTAMO_PENDIENTE]
                )
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="El área ya tiene una reserva o está ocupada"
        )


async def verificar_usuario_sin_area_activa(db: AsyncSession, usuario_id: int):
    """
    Bloquea al usuario si ya tiene un préstamo vigente o pendiente de área.
    Un usuario solo puede tener un área a la vez.
    """
    result = await db.execute(
        select(func.count(PrestamoArea.id)).where(
            and_(
                PrestamoArea.usuario_prestado_id == usuario_id,
                PrestamoArea.estado_prestamo_id.in_(
                    [ESTADO_PRESTAMO_VIGENTE, ESTADO_PRESTAMO_PENDIENTE]
                )
            )
        )
    )
    cantidad = result.scalar() or 0

    if cantidad > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Ya tienes un área reservada u ocupada. "
                "Debes devolver el área actual antes de solicitar otra."
            )
        )


async def verificar_usuario_activo(db: AsyncSession, usuario_id: int) -> Usuario:
    result = await db.execute(
        select(Usuario).filter(
            and_(Usuario.id == usuario_id, Usuario.esta_activo == True)
        )
    )
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario no válido para préstamo")
    return usuario


def _serializar_prestamo(prestamo: PrestamoArea) -> dict:
    return {
        "id":                         prestamo.id,
        "area_id":                    prestamo.area_id,
        "usuario_presta_id":          prestamo.usuario_presta_id,
        "usuario_prestado_id":        prestamo.usuario_prestado_id,
        "estado_prestamo_id":         prestamo.estado_prestamo_id,
        "fecha_prestamo":             prestamo.fecha_prestamo,
        "fecha_devolucion_esperada":  prestamo.fecha_devolucion_esperada,
        "fecha_devolucion_real":      prestamo.fecha_devolucion_real,
        "usuario_ultimo_cambio_id":   prestamo.usuario_ultimo_cambio_id,
        "fecha_ultimo_cambio_estado": prestamo.fecha_ultimo_cambio_estado,
        "observaciones":              prestamo.observaciones,
        "tiempo_excedido":            prestamo.tiempo_excedido,
        "horas_excedidas":            round(prestamo.tiempo_excedido.total_seconds() / 3600, 2)
                                      if prestamo.tiempo_excedido else 0.0,
        "area_nombre":                prestamo.area.nombre     if prestamo.area           else None,
        "area_capacidad":             prestamo.area.capacidad  if prestamo.area           else None,
        "usuario_presta_nombre":      prestamo.usuario_presta.nombre_completo   if prestamo.usuario_presta   else None,
        "usuario_prestado_nombre":    prestamo.usuario_prestado.nombre_completo if prestamo.usuario_prestado else None,
        "usuario_ultimo_cambio_nombre": prestamo.usuario_ultimo_cambio.nombre_completo
                                       if prestamo.usuario_ultimo_cambio else None,
        "estado_prestamo_nombre":     prestamo.estado_prestamo.estado if prestamo.estado_prestamo else None,
    }


# =============================================
# ENDPOINTS DE CONSULTA
# =============================================

@router.get("/", response_model=List[PrestamoAreaConRelaciones])
async def listar_prestamos_areas(
    skip: int = 0,
    limit: int = 100,
    estado_prestamo_id:  Optional[int] = Query(None),
    area_id:             Optional[int] = Query(None),
    usuario_prestado_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    try:
        query = select(PrestamoArea).options(
            selectinload(PrestamoArea.area),
            selectinload(PrestamoArea.usuario_presta),
            selectinload(PrestamoArea.usuario_prestado),
            selectinload(PrestamoArea.estado_prestamo),
            selectinload(PrestamoArea.usuario_ultimo_cambio)
        )
        if estado_prestamo_id:
            query = query.where(PrestamoArea.estado_prestamo_id == estado_prestamo_id)
        if area_id:
            query = query.where(PrestamoArea.area_id == area_id)
        if usuario_prestado_id:
            query = query.where(PrestamoArea.usuario_prestado_id == usuario_prestado_id)

        query     = query.offset(skip).limit(limit)
        result    = await db.execute(query)
        prestamos = result.scalars().all()
        return [_serializar_prestamo(p) for p in prestamos]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar préstamos: {str(e)}")


@router.get("/vigentes", response_model=List[PrestamoAreaConRelaciones])
async def listar_prestamos_areas_vigentes(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    return await listar_prestamos_areas(
        skip=skip, limit=limit,
        estado_prestamo_id=ESTADO_PRESTAMO_VIGENTE,
        area_id=None, usuario_prestado_id=None,
        db=db, usuario_actual=usuario_actual
    )


@router.get("/pendientes", response_model=List[PrestamoAreaConRelaciones])
async def listar_solicitudes_pendientes(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Lista todas las solicitudes pendientes de aprobación.
    Solo accesible para admins. Usado en el panel de aprobaciones.
    """
    try:
        query = select(PrestamoArea).options(
            selectinload(PrestamoArea.area),
            selectinload(PrestamoArea.usuario_presta),
            selectinload(PrestamoArea.usuario_prestado),
            selectinload(PrestamoArea.estado_prestamo),
            selectinload(PrestamoArea.usuario_ultimo_cambio)
        ).where(
            PrestamoArea.estado_prestamo_id == ESTADO_PRESTAMO_PENDIENTE
        ).order_by(PrestamoArea.fecha_prestamo.asc())

        query     = query.offset(skip).limit(limit)
        result    = await db.execute(query)
        prestamos = result.scalars().all()
        return [_serializar_prestamo(p) for p in prestamos]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/mis-solicitudes", response_model=List[PrestamoAreaConRelaciones])
async def mis_solicitudes_area(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Devuelve las solicitudes activas del usuario actual
    (vigentes + pendientes de aprobación).
    """
    query = select(PrestamoArea).options(
        selectinload(PrestamoArea.area),
        selectinload(PrestamoArea.estado_prestamo),
        selectinload(PrestamoArea.usuario_presta),
        selectinload(PrestamoArea.usuario_prestado),
    ).where(
        and_(
            PrestamoArea.usuario_prestado_id == usuario_actual.id,
            PrestamoArea.estado_prestamo_id.in_(
                [ESTADO_PRESTAMO_VIGENTE, ESTADO_PRESTAMO_PENDIENTE]
            )
        )
    )
    result    = await db.execute(query)
    prestamos = result.scalars().all()
    return [_serializar_prestamo(p) for p in prestamos]


@router.get("/{prestamo_id}", response_model=PrestamoAreaConRelaciones)
async def obtener_prestamo_area(
    prestamo_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    result = await db.execute(
        select(PrestamoArea)
        .options(
            selectinload(PrestamoArea.area),
            selectinload(PrestamoArea.usuario_presta),
            selectinload(PrestamoArea.usuario_prestado),
            selectinload(PrestamoArea.estado_prestamo),
            selectinload(PrestamoArea.usuario_ultimo_cambio)
        )
        .filter(PrestamoArea.id == prestamo_id)
    )
    prestamo = result.scalar_one_or_none()

    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo de área no encontrado")
    return _serializar_prestamo(prestamo)


# =============================================
# CREAR SOLICITUD (usuario)
# =============================================

@router.post("/", response_model=PrestamoAreaResponse)
async def solicitar_area(
    prestamo_data: PrestamoAreaCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    El usuario solicita reservar un área.

    NUEVO FLUJO:
    - Verifica que el usuario no tenga ya un área activa o pendiente
    - El área pasa a estado 4 (Reservada)
    - El préstamo queda en estado 2 (Pendiente) esperando aprobación del admin
    - El admin aprueba desde /pendientes → área pasa a Ocupada (2)
    """
    try:
        # 1. Bloquear si el usuario ya tiene un área activa o pendiente
        await verificar_usuario_sin_area_activa(db, usuario_actual.id)

        # 2. Verificar que el área existe, está disponible y es prestable
        area = await verificar_area_disponible(db, prestamo_data.area_id)

        # 3. Verificar que el área no tiene solicitudes activas
        await verificar_area_sin_solicitudes(db, prestamo_data.area_id)

        # 4. Verificar usuario prestado (puede ser el mismo usuario)
        usuario_prestado_id = prestamo_data.usuario_prestado_id or usuario_actual.id
        await verificar_usuario_activo(db, usuario_prestado_id)

        fecha_actual = datetime.utcnow() - timedelta(hours=6)

        # 5. Cambiar área a "Reservada" — no "Ocupada" hasta aprobación
        area.estado_id                = ESTADO_AREA_RESERVADA
        area.fecha_ultimo_cambio_estado = fecha_actual

        # 6. Crear préstamo en estado "Pendiente"
        nuevo_prestamo = PrestamoArea(
            area_id                    = prestamo_data.area_id,
            usuario_presta_id          = usuario_actual.id,
            usuario_prestado_id        = usuario_prestado_id,
            estado_prestamo_id         = ESTADO_PRESTAMO_PENDIENTE,
            fecha_prestamo             = fecha_actual,
            fecha_devolucion_esperada  = prestamo_data.fecha_devolucion_esperada,
            usuario_ultimo_cambio_id   = usuario_actual.id,
            fecha_ultimo_cambio_estado = fecha_actual,
            observaciones              = prestamo_data.observaciones,
            tiempo_excedido            = timedelta(0)
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
        raise HTTPException(status_code=500, detail=f"Error al crear solicitud: {str(e)}")


# =============================================
# APROBAR SOLICITUD (admin)
# =============================================

@router.patch("/{prestamo_id}/aprobar", response_model=PrestamoAreaConRelaciones)
async def aprobar_solicitud_area(
    prestamo_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    El admin aprueba una solicitud pendiente.
    - Préstamo pasa de Pendiente (2) → Vigente (1)
    - Área pasa de Reservada (4) → Ocupada (2)
    """
    try:
        result = await db.execute(
            select(PrestamoArea)
            .options(
                selectinload(PrestamoArea.area),
                selectinload(PrestamoArea.usuario_prestado),
                selectinload(PrestamoArea.estado_prestamo)
            )
            .filter(PrestamoArea.id == prestamo_id)
        )
        prestamo = result.scalar_one_or_none()

        if not prestamo:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")

        if prestamo.estado_prestamo_id != ESTADO_PRESTAMO_PENDIENTE:
            raise HTTPException(
                status_code=400,
                detail="Solo se pueden aprobar solicitudes en estado Pendiente"
            )

        fecha_actual = datetime.utcnow() - timedelta(hours=6)

        # Área → Ocupada
        if prestamo.area:
            prestamo.area.estado_id                = ESTADO_AREA_OCUPADA
            prestamo.area.fecha_ultimo_cambio_estado = fecha_actual

        # Préstamo → Vigente
        prestamo.estado_prestamo_id         = ESTADO_PRESTAMO_VIGENTE
        prestamo.usuario_ultimo_cambio_id   = usuario_actual.id
        prestamo.fecha_ultimo_cambio_estado = fecha_actual

        await db.commit()
        await db.refresh(prestamo)
        return _serializar_prestamo(prestamo)

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al aprobar solicitud: {str(e)}")


# =============================================
# RECHAZAR SOLICITUD (admin)
# =============================================

@router.patch("/{prestamo_id}/rechazar", response_model=PrestamoAreaConRelaciones)
async def rechazar_solicitud_area(
    prestamo_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    El admin rechaza una solicitud pendiente.
    - Préstamo pasa a Terminado (3)
    - Área vuelve a Disponible (1)
    """
    try:
        result = await db.execute(
            select(PrestamoArea)
            .options(selectinload(PrestamoArea.area))
            .filter(PrestamoArea.id == prestamo_id)
        )
        prestamo = result.scalar_one_or_none()

        if not prestamo:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")

        if prestamo.estado_prestamo_id != ESTADO_PRESTAMO_PENDIENTE:
            raise HTTPException(
                status_code=400,
                detail="Solo se pueden rechazar solicitudes en estado Pendiente"
            )

        fecha_actual = datetime.utcnow() - timedelta(hours=6)

        # Área → Disponible
        if prestamo.area:
            prestamo.area.estado_id                = ESTADO_AREA_DISPONIBLE
            prestamo.area.fecha_ultimo_cambio_estado = fecha_actual

        # Préstamo → Terminado
        prestamo.estado_prestamo_id         = ESTADO_PRESTAMO_TERMINADO
        prestamo.fecha_devolucion_real       = fecha_actual
        prestamo.usuario_ultimo_cambio_id    = usuario_actual.id
        prestamo.fecha_ultimo_cambio_estado  = fecha_actual
        prestamo.observaciones               = (
            f"[RECHAZADO por admin] {prestamo.observaciones or ''}"
        ).strip()

        await db.commit()
        await db.refresh(prestamo)
        return _serializar_prestamo(prestamo)

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al rechazar solicitud: {str(e)}")


# =============================================
# DEVOLVER ÁREA (admin o usuario)
# =============================================

@router.patch("/{prestamo_id}/devolver", response_model=PrestamoAreaResponse)
async def devolver_prestamo_area(
    prestamo_id: int,
    devolucion_data: PrestamoAreaDevolucion,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Registrar devolución de un área vigente.
    - Puede ejecutarlo el propio usuario o un admin.
    - Área → Disponible, Préstamo → Terminado.
    """
    try:
        result = await db.execute(
            select(PrestamoArea).filter(PrestamoArea.id == prestamo_id)
        )
        prestamo = result.scalar_one_or_none()

        if not prestamo:
            raise HTTPException(status_code=404, detail="Préstamo de área no encontrado")

        if prestamo.estado_prestamo_id != ESTADO_PRESTAMO_VIGENTE:
            raise HTTPException(
                status_code=400,
                detail="Solo se pueden devolver préstamos vigentes"
            )

        # Verificar que el usuario es el dueño o es admin
        es_admin = usuario_actual.tipo_usuario_id >= 2
        if not es_admin and prestamo.usuario_prestado_id != usuario_actual.id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para devolver este préstamo"
            )

        result_area = await db.execute(
            select(Area).filter(Area.id == prestamo.area_id)
        )
        area = result_area.scalar_one_or_none()

        fecha_devolucion = datetime.utcnow() - timedelta(hours=6)

        if area:
            area.estado_id                = ESTADO_AREA_DISPONIBLE
            area.fecha_ultimo_cambio_estado = fecha_devolucion

        prestamo.estado_prestamo_id         = ESTADO_PRESTAMO_TERMINADO
        prestamo.fecha_devolucion_real       = fecha_devolucion
        prestamo.usuario_ultimo_cambio_id    = usuario_actual.id
        prestamo.fecha_ultimo_cambio_estado  = fecha_devolucion
        prestamo.tiempo_excedido             = calcular_tiempo_excedido(
            prestamo.fecha_devolucion_esperada, fecha_devolucion
        )

        if devolucion_data.observaciones:
            prestamo.observaciones = devolucion_data.observaciones

        await db.commit()
        await db.refresh(prestamo)
        return prestamo

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar devolución: {str(e)}")


# =============================================
# LISTAR POR USUARIO
# =============================================

@router.get("/usuario/{usuario_id}", response_model=List[PrestamoAreaConRelaciones])
async def listar_prestamos_areas_usuario(
    usuario_id: int,
    solo_vigentes: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    query = select(PrestamoArea).options(
        selectinload(PrestamoArea.area),
        selectinload(PrestamoArea.usuario_presta),
        selectinload(PrestamoArea.usuario_prestado),
        selectinload(PrestamoArea.estado_prestamo)
    ).filter(PrestamoArea.usuario_prestado_id == usuario_id)

    if solo_vigentes:
        query = query.where(
            PrestamoArea.estado_prestamo_id.in_(
                [ESTADO_PRESTAMO_VIGENTE, ESTADO_PRESTAMO_PENDIENTE]
            )
        )

    result    = await db.execute(query)
    prestamos = result.scalars().all()
    return [_serializar_prestamo(p) for p in prestamos]