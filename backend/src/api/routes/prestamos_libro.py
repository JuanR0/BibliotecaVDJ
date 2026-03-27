from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
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
    MultaResumenEnDevolucion
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

COSTO_MULTA_POR_DIA = Decimal('10.00')   # $10 MXN por día de retraso
TIPO_PAGO_ID_DEFAULT = 1                  # "Banco" o el primer tipo de pago disponible
TIPO_RECURSO_LIBRO_ID = 1                 # ID del tipo de recurso "Libro" en tipos_recurso_multa

# =============================================
# FUNCIONES AUXILIARES
# =============================================

def to_naive(dt: datetime) -> datetime:
    if dt and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

def calcular_dias_excedidos(fecha_esperada: datetime, fecha_real: datetime) -> int:
    if not fecha_real:
        return 0
    fecha_esperada_date = fecha_esperada.date()
    fecha_real_date = fecha_real.date()
    diferencia = fecha_real_date - fecha_esperada_date
    return max(0, diferencia.days)

async def verificar_libro_disponible(db: AsyncSession, libro_id: int) -> Libro:
    result = await db.execute(select(Libro).filter(Libro.id == libro_id))
    libro = result.scalar_one_or_none()

    if not libro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    if libro.estado_id != 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El libro no está disponible para préstamo")
    if not libro.es_prestable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El libro no es prestable")

    return libro

async def verificar_usuario_activo(db: AsyncSession, usuario_id: int) -> Usuario:
    result = await db.execute(
        select(Usuario).filter(and_(Usuario.id == usuario_id, Usuario.esta_activo == True))
    )
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no válido para préstamo")
    return usuario


# =============================================
# NUEVA FUNCIÓN: Verificar multas pendientes
# Implementa el patrón "Lazy evaluation":
# Se ejecuta al intentar crear un nuevo préstamo.
# =============================================

async def verificar_sin_multas_pendientes(db: AsyncSession, usuario_id: int):
    """
    Verifica que el usuario no tenga multas pendientes (estado_multa_id = 1).
    Si tiene, lanza 403 con detalle claro para el frontend.
    """
    result = await db.execute(
        select(func.count(Multa.id)).where(
            and_(
                Multa.usuario_multado_id == usuario_id,
                Multa.estado_multa_id == 1  # Pendiente
            )
        )
    )
    cantidad = result.scalar() or 0

    if cantidad > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"El usuario tiene {cantidad} multa(s) pendiente(s). "
                   f"Debe liquidarlas antes de solicitar un nuevo préstamo."
        )


# =============================================
# NUEVA FUNCIÓN: Generar multa por devolución tardía
# =============================================

async def generar_multa_por_retraso(
    db: AsyncSession,
    prestamo: PrestamoLibro,
    dias_excedidos: int,
    usuario_admin_id: int
) -> Multa:
    """
    Crea una multa automáticamente cuando se devuelve un libro con retraso.
    Costo = dias_excedidos * COSTO_MULTA_POR_DIA
    """
    costo = Decimal(str(dias_excedidos)) * COSTO_MULTA_POR_DIA

    nueva_multa = Multa(
        usuario_multa_id=usuario_admin_id,
        usuario_multado_id=prestamo.usuario_prestado_id,
        estado_multa_id=1,  # Pendiente
        fecha_multa=datetime.utcnow() - timedelta(hours=6),
        usuario_ultimo_cambio_id=usuario_admin_id,
        fecha_ultimo_cambio_estado=datetime.utcnow() - timedelta(hours=6),
        tipo_pago_id=TIPO_PAGO_ID_DEFAULT,
        tipo_recurso_multa_id=TIPO_RECURSO_LIBRO_ID,
        costo_monetario=costo,
        observaciones=(
            f"Multa generada automáticamente por devolución tardía. "
            f"Préstamo #{prestamo.id} — {dias_excedidos} día(s) de retraso. "
            f"Costo: ${costo} MXN (${COSTO_MULTA_POR_DIA}/día)."
        )
    )

    db.add(nueva_multa)
    return nueva_multa


# =============================================
# ENDPOINTS DE CONSULTA (LISTAR)
# =============================================

@router.get("/", response_model=List[PrestamoLibroConRelaciones])
async def listar_prestamos(
    skip: int = 0,
    limit: int = 100,
    estado_prestamo_id: Optional[int] = Query(None),
    libro_id: Optional[int] = Query(None),
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
            selectinload(PrestamoLibro.usuario_ultimo_cambio)
        )

        if estado_prestamo_id:
            query = query.where(PrestamoLibro.estado_prestamo_id == estado_prestamo_id)
        if libro_id:
            query = query.where(PrestamoLibro.libro_id == libro_id)
        if usuario_prestado_id:
            query = query.where(PrestamoLibro.usuario_prestado_id == usuario_prestado_id)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        prestamos = result.scalars().all()

        return [_serializar_prestamo(p) for p in prestamos]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar préstamos: {str(e)}")


@router.get("/vigentes", response_model=List[PrestamoLibroConRelaciones])
async def listar_prestamos_vigentes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    return await listar_prestamos(
        skip=skip, limit=limit, estado_prestamo_id=1,
        libro_id=None, usuario_prestado_id=None,
        db=db, usuario_actual=usuario_actual
    )


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
        )
        .where(PrestamoLibro.usuario_prestado_id == usuario_actual.id)
    )

    if solo_vigentes:
        query = query.where(PrestamoLibro.estado_prestamo_id == 1)

    result = await db.execute(query)
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
            selectinload(PrestamoLibro.usuario_ultimo_cambio)
        )
        .filter(PrestamoLibro.id == prestamo_id)
    )
    prestamo = result.scalar_one_or_none()

    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    return _serializar_prestamo(prestamo)


# =============================================
# ENDPOINTS DE CREACIÓN (POST)
# =============================================

@router.post("/", response_model=PrestamoLibroResponse)
async def crear_prestamo(
    prestamo_data: PrestamoLibroCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Crear un nuevo préstamo de libro.
    BLOQUEA si el usuario tiene multas pendientes (Lazy evaluation).
    """
    fecha_devolucion = to_naive(prestamo_data.fecha_devolucion_esperada)
    fecha_actual = datetime.utcnow().replace(tzinfo=None) - timedelta(hours=6)

    try:
        # ── NUEVO: Verificar multas pendientes antes de crear préstamo ──
        await verificar_sin_multas_pendientes(db, prestamo_data.usuario_prestado_id)

        libro = await verificar_libro_disponible(db, prestamo_data.libro_id)
        usuario_prestado = await verificar_usuario_activo(db, prestamo_data.usuario_prestado_id)

        libro.estado_id = 2
        libro.fecha_cambio_estado = datetime.utcnow() - timedelta(hours=6)

        nuevo_prestamo = PrestamoLibro(
            libro_id=prestamo_data.libro_id,
            usuario_presta_id=usuario_actual.id,
            usuario_prestado_id=prestamo_data.usuario_prestado_id,
            estado_prestamo_id=1,
            fecha_prestamo=fecha_actual,
            fecha_devolucion_esperada=fecha_devolucion,
            usuario_ultimo_cambio_id=usuario_actual.id,
            fecha_ultimo_cambio_estado=fecha_actual,
            observaciones=prestamo_data.observaciones
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
# ENDPOINTS DE DEVOLUCIÓN (PATCH)
# =============================================

@router.patch("/{prestamo_id}/devolver", response_model=PrestamoDevolucionResponse)
async def devolver_prestamo(
    prestamo_id: int,
    devolucion_data: PrestamoLibroDevolucion,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Registrar devolución de un préstamo.

    NUEVO COMPORTAMIENTO:
    - Si el libro se devuelve con retraso (dias_excedidos > 0),
      se genera automáticamente una multa al usuario.
    - La respuesta siempre incluye el préstamo actualizado.
    - Si hubo multa, la incluye en `multa_generada`.
    """
    try:
        result = await db.execute(
            select(PrestamoLibro).filter(PrestamoLibro.id == prestamo_id)
        )
        prestamo = result.scalar_one_or_none()

        if not prestamo:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")

        if prestamo.estado_prestamo_id != 1:
            raise HTTPException(status_code=400, detail="Solo se pueden devolver préstamos vigentes")

        # ── Actualizar libro a Disponible ──
        result_libro = await db.execute(
            select(Libro).filter(Libro.id == prestamo.libro_id)
        )
        libro = result_libro.scalar_one_or_none()
        if libro:
            libro.estado_id = 1
            libro.fecha_cambio_estado = datetime.utcnow() - timedelta(hours=6)

        # ── Calcular días excedidos ──
        fecha_devolucion_real = datetime.utcnow() - timedelta(hours=6)
        dias_excedidos = calcular_dias_excedidos(
            prestamo.fecha_devolucion_esperada,
            fecha_devolucion_real
        )

        # ── Actualizar préstamo ──
        prestamo.estado_prestamo_id = 3  # Terminado
        prestamo.fecha_devolucion_real = fecha_devolucion_real
        prestamo.usuario_ultimo_cambio_id = usuario_actual.id
        prestamo.fecha_ultimo_cambio_estado = fecha_devolucion_real
        prestamo.dias_excedidos = dias_excedidos

        if devolucion_data.observaciones:
            prestamo.observaciones = devolucion_data.observaciones

        # ── NUEVO: Generar multa si hay retraso ──
        multa_generada = None
        if dias_excedidos > 0:
            multa_generada = await generar_multa_por_retraso(
                db=db,
                prestamo=prestamo,
                dias_excedidos=dias_excedidos,
                usuario_admin_id=usuario_actual.id
            )

        await db.commit()
        await db.refresh(prestamo)
        if multa_generada:
            await db.refresh(multa_generada)

        # ── Construir respuesta ──
        multa_resumen = None
        if multa_generada:
            multa_resumen = MultaResumenEnDevolucion(
                id=multa_generada.id,
                costo_monetario=multa_generada.costo_monetario,
                dias_excedidos=dias_excedidos,
                observaciones=multa_generada.observaciones
            )

        mensaje = (
            f"Devolución registrada. Se generó una multa de "
            f"${multa_generada.costo_monetario} MXN por {dias_excedidos} día(s) de retraso."
            if multa_generada
            else "Devolución registrada correctamente."
        )

        return PrestamoDevolucionResponse(
            prestamo=prestamo,
            multa_generada=multa_resumen,
            mensaje=mensaje
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar devolución: {str(e)}")


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
        query = query.where(PrestamoLibro.estado_prestamo_id == 1)

    result = await db.execute(query)
    prestamos = result.scalars().all()

    return [_serializar_prestamo(p) for p in prestamos]


# =============================================
# HELPER DE SERIALIZACIÓN (evita repetición)
# =============================================

def _serializar_prestamo(prestamo: PrestamoLibro) -> dict:
    return {
        "id": prestamo.id,
        "libro_id": prestamo.libro_id,
        "usuario_presta_id": prestamo.usuario_presta_id,
        "usuario_prestado_id": prestamo.usuario_prestado_id,
        "estado_prestamo_id": prestamo.estado_prestamo_id,
        "fecha_prestamo": prestamo.fecha_prestamo,
        "fecha_devolucion_esperada": prestamo.fecha_devolucion_esperada,
        "fecha_devolucion_real": prestamo.fecha_devolucion_real,
        "usuario_ultimo_cambio_id": prestamo.usuario_ultimo_cambio_id,
        "fecha_ultimo_cambio_estado": prestamo.fecha_ultimo_cambio_estado,
        "observaciones": prestamo.observaciones,
        "dias_excedidos": prestamo.dias_excedidos or 0,
        "libro_titulo": prestamo.libro.titulo if prestamo.libro else None,
        "libro_autor": prestamo.libro.autor if prestamo.libro else None,
        "libro_codigo_decimal": prestamo.libro.codigo_decimal if prestamo.libro else None,
        "usuario_presta_nombre": prestamo.usuario_presta.nombre_completo if prestamo.usuario_presta else None,
        "usuario_prestado_nombre": prestamo.usuario_prestado.nombre_completo if prestamo.usuario_prestado else None,
        "estado_prestamo_nombre": prestamo.estado_prestamo.estado if prestamo.estado_prestamo else None,
    }