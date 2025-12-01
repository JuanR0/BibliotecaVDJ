from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
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
# FUNCIONES AUXILIARES
# =============================================

def calcular_tiempo_excedido(fecha_esperada: datetime, fecha_real: datetime) -> timedelta:
    """
    Calcula el tiempo excedido entre fecha esperada y fecha real.
    Si es negativo (devolución temprana), retorna timedelta(0).
    """
    if not fecha_real:
        return timedelta(0)
    
    diferencia = fecha_real - fecha_esperada
    
    # Si la devolución fue en la misma fecha o antes, no hay tiempo excedido
    if diferencia <= timedelta(0):
        return timedelta(0)
    
    return diferencia

async def verificar_area_disponible(db: AsyncSession, area_id: int) -> Area:
    """
    Verificar que el área existe, está disponible Y es prestable
    """
    result = await db.execute(
        select(Area).filter(Area.id == area_id)
    )
    area = result.scalar_one_or_none()
    
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área no encontrada"
        )
    
    if area.estado_id != 1:  # No está disponible
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El área no está disponible para préstamo (estado no disponible)"
        )
    
    if not area.es_prestable:  # ✅ VALIDACIÓN DE PRESTABILIDAD
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El área no es prestable"
        )
    
    return area

async def verificar_area_no_ocupada(db: AsyncSession, area_id: int) -> bool:
    """
    Verificar que el área no tiene préstamos vigentes
    """
    result = await db.execute(
        select(PrestamoArea).filter(
            and_(
                PrestamoArea.area_id == area_id,
                PrestamoArea.estado_prestamo_id == 1  # Vigente
            )
        )
    )
    prestamo_vigente = result.scalar_one_or_none()
    
    if prestamo_vigente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El área ya tiene un préstamo vigente"
        )
    
    return True

async def verificar_usuario_activo(db: AsyncSession, usuario_id: int) -> Usuario:
    """
    Verificar que el usuario existe y está activo
    """
    result = await db.execute(
        select(Usuario).filter(
            and_(
                Usuario.id == usuario_id,
                Usuario.esta_activo == True
            )
        )
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no válido para préstamo"
        )
    return usuario

# =============================================
# ENDPOINTS DE CONSULTA (LISTAR)
# =============================================

@router.get("/", response_model=List[PrestamoAreaConRelaciones])
async def listar_prestamos_areas(
    skip: int = 0,
    limit: int = 100,
    estado_prestamo_id: Optional[int] = Query(None, description="Filtrar por estado de préstamo"),
    area_id: Optional[int] = Query(None, description="Filtrar por área"),
    usuario_prestado_id: Optional[int] = Query(None, description="Filtrar por usuario prestado"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar todos los préstamos de áreas con filtros opcionales
    """
    try:
        # Construir query base con joins
        query = select(PrestamoArea).options(
            selectinload(PrestamoArea.area),
            selectinload(PrestamoArea.usuario_presta),
            selectinload(PrestamoArea.usuario_prestado),
            selectinload(PrestamoArea.estado_prestamo),
            selectinload(PrestamoArea.usuario_ultimo_cambio)
        )
        
        # Aplicar filtros
        if estado_prestamo_id:
            query = query.where(PrestamoArea.estado_prestamo_id == estado_prestamo_id)
        if area_id:
            query = query.where(PrestamoArea.area_id == area_id)
        if usuario_prestado_id:
            query = query.where(PrestamoArea.usuario_prestado_id == usuario_prestado_id)
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        # Ejecutar query
        result = await db.execute(query)
        prestamos = result.scalars().all()
        
        # Construir respuesta con datos relacionados
        resultado = []
        for prestamo in prestamos:
            resultado.append({
                "id": prestamo.id,
                "area_id": prestamo.area_id,
                "usuario_presta_id": prestamo.usuario_presta_id,
                "usuario_prestado_id": prestamo.usuario_prestado_id,
                "estado_prestamo_id": prestamo.estado_prestamo_id,
                "fecha_prestamo": prestamo.fecha_prestamo,
                "fecha_devolucion_esperada": prestamo.fecha_devolucion_esperada,
                "fecha_devolucion_real": prestamo.fecha_devolucion_real,
                "usuario_ultimo_cambio_id": prestamo.usuario_ultimo_cambio_id,
                "fecha_ultimo_cambio_estado": prestamo.fecha_ultimo_cambio_estado,
                "observaciones": prestamo.observaciones,
                "tiempo_excedido": prestamo.tiempo_excedido,
                "horas_excedidas": round(prestamo.tiempo_excedido.total_seconds() / 3600, 2) if prestamo.tiempo_excedido else 0.0,
                "area_nombre": prestamo.area.nombre if prestamo.area else None,
                "area_capacidad": prestamo.area.capacidad if prestamo.area else None,
                "usuario_presta_nombre": prestamo.usuario_presta.nombre_completo if prestamo.usuario_presta else None,
                "usuario_prestado_nombre": prestamo.usuario_prestado.nombre_completo if prestamo.usuario_prestado else None,
                "usuario_ultimo_cambio_nombre": prestamo.usuario_ultimo_cambio.nombre_completo if prestamo.usuario_ultimo_cambio else None,
                "estado_prestamo_nombre": prestamo.estado_prestamo.estado if prestamo.estado_prestamo else None
            })
        
        return resultado
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar préstamos de áreas: {str(e)}"
        )

@router.get("/vigentes", response_model=List[PrestamoAreaConRelaciones])
async def listar_prestamos_areas_vigentes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar solo préstamos de áreas vigentes (estado_prestamo_id = 1)
    """
    return await listar_prestamos_areas(
        skip=skip, 
        limit=limit, 
        estado_prestamo_id=1,  # Vigente
        area_id=None,        
        usuario_prestado_id=None,
        db=db, 
        usuario_actual=usuario_actual
    )

@router.get("/{prestamo_id}", response_model=PrestamoAreaConRelaciones)
async def obtener_prestamo_area(
    prestamo_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Obtener un préstamo de área específico por ID
    """
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo de área no encontrado"
        )
    
    return {
        "id": prestamo.id,
        "area_id": prestamo.area_id,
        "usuario_presta_id": prestamo.usuario_presta_id,
        "usuario_prestado_id": prestamo.usuario_prestado_id,
        "estado_prestamo_id": prestamo.estado_prestamo_id,
        "fecha_prestamo": prestamo.fecha_prestamo,
        "fecha_devolucion_esperada": prestamo.fecha_devolucion_esperada,
        "fecha_devolucion_real": prestamo.fecha_devolucion_real,
        "usuario_ultimo_cambio_id": prestamo.usuario_ultimo_cambio_id,
        "fecha_ultimo_cambio_estado": prestamo.fecha_ultimo_cambio_estado,
        "observaciones": prestamo.observaciones,
        "tiempo_excedido": prestamo.tiempo_excedido,
        "horas_excedidas": round(prestamo.tiempo_excedido.total_seconds() / 3600, 2) if prestamo.tiempo_excedido else 0.0,
        "area_nombre": prestamo.area.nombre if prestamo.area else None,
        "area_capacidad": prestamo.area.capacidad if prestamo.area else None,
        "usuario_presta_nombre": prestamo.usuario_presta.nombre_completo if prestamo.usuario_presta else None,
        "usuario_prestado_nombre": prestamo.usuario_prestado.nombre_completo if prestamo.usuario_prestado else None,
        "usuario_ultimo_cambio_nombre": prestamo.usuario_ultimo_cambio.nombre_completo if prestamo.usuario_ultimo_cambio else None,
        "estado_prestamo_nombre": prestamo.estado_prestamo.estado if prestamo.estado_prestamo else None
    }

# =============================================
# ENDPOINTS DE CREACIÓN (POST)
# =============================================

@router.post("/", response_model=PrestamoAreaResponse)
async def crear_prestamo_area(
    prestamo_data: PrestamoAreaCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Crear un nuevo préstamo de área
    """
    try:
        # 1. Verificar que el área existe, está disponible y es prestable
        area = await verificar_area_disponible(db, prestamo_data.area_id)
        
        # 2. Verificar que el área no está ocupada
        await verificar_area_no_ocupada(db, prestamo_data.area_id)
        
        # 3. Verificar que el usuario prestado existe y está activo
        usuario_prestado = await verificar_usuario_activo(db, prestamo_data.usuario_prestado_id)
        
        # 4. INICIAR TRANSACCIÓN
        # 4.1 Cambiar estado del área a "Ocupada" (estado_id = 2)
        area.estado_id = 2  # Ocupada
        area.fecha_ultimo_cambio_estado = datetime.utcnow() - timedelta(hours=6)
        
        # 4.2 Crear el préstamo
        nuevo_prestamo = PrestamoArea(
            area_id=prestamo_data.area_id,
            usuario_presta_id=usuario_actual.id,
            usuario_prestado_id=prestamo_data.usuario_prestado_id,
            estado_prestamo_id=1,  # "Vigente"
            fecha_prestamo=datetime.utcnow() -  timedelta(hours=6),
            fecha_devolucion_esperada=prestamo_data.fecha_devolucion_esperada,
            usuario_ultimo_cambio_id=usuario_actual.id,
            fecha_ultimo_cambio_estado=datetime.utcnow() -  timedelta(hours=6),
            observaciones=prestamo_data.observaciones,
            tiempo_excedido=timedelta(0)  # Inicialmente 0
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear préstamo de área: {str(e)}"
        )

# =============================================
# ENDPOINTS DE ACTUALIZACIÓN (PUT/PATCH)
# =============================================

@router.patch("/{prestamo_id}/devolver", response_model=PrestamoAreaResponse)
async def devolver_prestamo_area(
    prestamo_id: int,
    devolucion_data: PrestamoAreaDevolucion,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Registrar devolución de un préstamo de área
    """
    try:
        # 1. Obtener el préstamo
        result = await db.execute(
            select(PrestamoArea).filter(PrestamoArea.id == prestamo_id)
        )
        prestamo = result.scalar_one_or_none()
        
        if not prestamo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Préstamo de área no encontrado"
            )
        
        if prestamo.estado_prestamo_id != 1:  # Si no está vigente
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden devolver préstamos vigentes"
            )
        
        # 2. INICIAR TRANSACCIÓN
        # 2.1 Cambiar estado del área a "Disponible"
        result_area = await db.execute(
            select(Area).filter(Area.id == prestamo.area_id)
        )
        area = result_area.scalar_one_or_none()
        
        if area:
            area.estado_id = 1  # Disponible
            area.fecha_ultimo_cambio_estado = datetime.utcnow() - timedelta(hours=6)
        
        # 2.2 Actualizar préstamo
        fecha_devolucion = datetime.utcnow() - timedelta(hours=6)
        prestamo.estado_prestamo_id = 3  # Terminado
        prestamo.fecha_devolucion_real = fecha_devolucion
        prestamo.usuario_ultimo_cambio_id = usuario_actual.id
        prestamo.fecha_ultimo_cambio_estado = fecha_devolucion
        
        # ✅ CALCULAR TIEMPO EXCEDIDO (con precisión de horas/minutos)
        prestamo.tiempo_excedido = calcular_tiempo_excedido(
            prestamo.fecha_devolucion_esperada,
            fecha_devolucion
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar devolución: {str(e)}"
        )

@router.get("/usuario/{usuario_id}", response_model=List[PrestamoAreaConRelaciones])
async def listar_prestamos_areas_usuario(
    usuario_id: int,
    solo_vigentes: bool = Query(True, description="Mostrar solo préstamos vigentes"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar préstamos de áreas de un usuario específico
    """
    query = select(PrestamoArea).options(
        selectinload(PrestamoArea.area),
        selectinload(PrestamoArea.usuario_presta),
        selectinload(PrestamoArea.usuario_prestado),
        selectinload(PrestamoArea.estado_prestamo)
    ).filter(PrestamoArea.usuario_prestado_id == usuario_id)
    
    if solo_vigentes:
        query = query.where(PrestamoArea.estado_prestamo_id == 1)  # Solo vigentes
    
    result = await db.execute(query)
    prestamos = result.scalars().all()
    
    # Construir respuesta con datos relacionados
    resultado = []
    for prestamo in prestamos:
        resultado.append({
            "id": prestamo.id,
            "area_id": prestamo.area_id,
            "usuario_presta_id": prestamo.usuario_presta_id,
            "usuario_prestado_id": prestamo.usuario_prestado_id,
            "estado_prestamo_id": prestamo.estado_prestamo_id,
            "fecha_prestamo": prestamo.fecha_prestamo,
            "fecha_devolucion_esperada": prestamo.fecha_devolucion_esperada,
            "fecha_devolucion_real": prestamo.fecha_devolucion_real,
            "usuario_ultimo_cambio_id": prestamo.usuario_ultimo_cambio_id,
            "fecha_ultimo_cambio_estado": prestamo.fecha_ultimo_cambio_estado,
            "observaciones": prestamo.observaciones,
            "tiempo_excedido": prestamo.tiempo_excedido,
            "horas_excedidas": round(prestamo.tiempo_excedido.total_seconds() / 3600, 2) if prestamo.tiempo_excedido else 0.0,
            "area_nombre": prestamo.area.nombre if prestamo.area else None,
            "area_capacidad": prestamo.area.capacidad if prestamo.area else None,
            "usuario_presta_nombre": prestamo.usuario_presta.nombre_completo if prestamo.usuario_presta else None,
            "usuario_prestado_nombre": prestamo.usuario_prestado.nombre_completo if prestamo.usuario_prestado else None,
            "estado_prestamo_nombre": prestamo.estado_prestamo.estado if prestamo.estado_prestamo else None
        })
    
    return resultado