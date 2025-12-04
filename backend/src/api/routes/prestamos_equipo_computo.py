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
from models.base import EstadoPrestamo
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
    requerir_puede_gestionar_recursos
)

router = APIRouter(prefix="/prestamos-equipos-computo", tags=["Préstamos de Equipos de Cómputo"])

# =============================================
# FUNCIONES AUXILIARES
# =============================================

async def verificar_equipo_disponible(db: AsyncSession, equipo_id: int) -> EquipoComputo:
    """
    Verificar que el equipo existe, está disponible Y es prestable
    """
    result = await db.execute(
        select(EquipoComputo).filter(EquipoComputo.id == equipo_id)
    )
    equipo = result.scalar_one_or_none()
    
    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo de cómputo no encontrado"
        )
    
    if equipo.estado_id != 1:  # No está disponible
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El equipo no está disponible para préstamo (estado no disponible)"
        )
    
    if not equipo.es_prestable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El equipo no es prestable"
        )
    
    return equipo

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

@router.get("/", response_model=List[PrestamoEquipoComputoConRelaciones])
async def listar_prestamos_equipos(
    skip: int = 0,
    limit: int = 100,
    estado_prestamo_id: Optional[int] = Query(None, description="Filtrar por estado de préstamo"),
    equipo_id: Optional[int] = Query(None, description="Filtrar por equipo"),
    usuario_prestado_id: Optional[int] = Query(None, description="Filtrar por usuario prestado"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar todos los préstamos de equipos de cómputo con filtros opcionales
    """
    try:
        # Construir query base con TODAS las relaciones necesarias
        query = select(PrestamoEquipoComputo).options(
            selectinload(PrestamoEquipoComputo.equipo_computo).selectinload(EquipoComputo.marca_equipo),
            selectinload(PrestamoEquipoComputo.equipo_computo).selectinload(EquipoComputo.tipo_equipo),
            selectinload(PrestamoEquipoComputo.usuario_presta),
            selectinload(PrestamoEquipoComputo.usuario_prestado),
            selectinload(PrestamoEquipoComputo.estado_prestamo),
            selectinload(PrestamoEquipoComputo.usuario_ultimo_cambio)
        )
        
        # Aplicar filtros
        if estado_prestamo_id:
            query = query.where(PrestamoEquipoComputo.estado_prestamo_id == estado_prestamo_id)
        if equipo_id:
            query = query.where(PrestamoEquipoComputo.equipos_computo_id == equipo_id)
        if usuario_prestado_id:
            query = query.where(PrestamoEquipoComputo.usuario_prestado_id == usuario_prestado_id)
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        # Ejecutar query
        result = await db.execute(query)
        prestamos = result.scalars().all()
        
        # Construir respuesta con datos relacionados
        resultado = []
        for prestamo in prestamos:
            # Acceder a las relaciones ya cargadas
            marca_nombre = None
            tipo_nombre = None
            numero_serie = None
            modelo = None
            
            if prestamo.equipo_computo:
                numero_serie = prestamo.equipo_computo.numero_serie
                modelo = prestamo.equipo_computo.modelo
                
                # CORRECCIÓN: .marca en lugar de .nombre
                if prestamo.equipo_computo.marca_equipo:
                    marca_nombre = prestamo.equipo_computo.marca_equipo.marca
                
                # CORRECCIÓN: .tipo en lugar de .nombre
                if prestamo.equipo_computo.tipo_equipo:
                    tipo_nombre = prestamo.equipo_computo.tipo_equipo.tipo
            
            resultado.append({
                "id": prestamo.id,
                "equipos_computo_id": prestamo.equipos_computo_id,
                "usuario_presta_id": prestamo.usuario_presta_id,
                "usuario_prestado_id": prestamo.usuario_prestado_id,
                "estado_prestamo_id": prestamo.estado_prestamo_id,
                "fecha_prestamo": prestamo.fecha_prestamo,
                "fecha_devolucion": prestamo.fecha_devolucion,
                "usuario_ultimo_cambio_id": prestamo.usuario_ultimo_cambio_id,
                "fecha_ultimo_cambio_estado": prestamo.fecha_ultimo_cambio_estado,
                "observaciones": prestamo.observaciones,
                "equipo_numero_serie": numero_serie,
                "equipo_marca": marca_nombre,
                "equipo_modelo": modelo,
                "equipo_tipo": tipo_nombre,
                "usuario_presta_nombre": prestamo.usuario_presta.nombre_completo if prestamo.usuario_presta else None,
                "usuario_prestado_nombre": prestamo.usuario_prestado.nombre_completo if prestamo.usuario_prestado else None,
                "estado_prestamo_nombre": prestamo.estado_prestamo.estado if prestamo.estado_prestamo else None
            })
        
        return resultado
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar préstamos de equipos: {str(e)}"
        )

@router.get("/vigentes", response_model=List[PrestamoEquipoComputoConRelaciones])
async def listar_prestamos_equipos_vigentes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar solo préstamos vigentes de equipos (estado_prestamo_id = 1)
    """
    return await listar_prestamos_equipos(
        skip=skip, 
        limit=limit, 
        estado_prestamo_id=1,  # Vigente
        equipo_id=None,        
        usuario_prestado_id=None,
        db=db, 
        usuario_actual=usuario_actual
    )

@router.get("/{prestamo_id}", response_model=PrestamoEquipoComputoConRelaciones)
async def obtener_prestamo_equipo(
    prestamo_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Obtener un préstamo de equipo específico por ID
    """
    result = await db.execute(
        select(PrestamoEquipoComputo)
        .options(
            selectinload(PrestamoEquipoComputo.equipo_computo).selectinload(EquipoComputo.marca_equipo),
            selectinload(PrestamoEquipoComputo.equipo_computo).selectinload(EquipoComputo.tipo_equipo),
            selectinload(PrestamoEquipoComputo.usuario_presta),
            selectinload(PrestamoEquipoComputo.usuario_prestado),
            selectinload(PrestamoEquipoComputo.estado_prestamo),
            selectinload(PrestamoEquipoComputo.usuario_ultimo_cambio)
        )
        .filter(PrestamoEquipoComputo.id == prestamo_id)
    )
    prestamo = result.scalar_one_or_none()
    
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo de equipo no encontrado"
        )
    
    # Obtener datos de relaciones
    marca_nombre = None
    tipo_nombre = None
    numero_serie = None
    modelo = None
    
    if prestamo.equipo_computo:
        numero_serie = prestamo.equipo_computo.numero_serie
        modelo = prestamo.equipo_computo.modelo
        
        if prestamo.equipo_computo.marca_equipo:
            marca_nombre = prestamo.equipo_computo.marca_equipo.marca
        
        if prestamo.equipo_computo.tipo_equipo:
            tipo_nombre = prestamo.equipo_computo.tipo_equipo.tipo
    
    return {
        "id": prestamo.id,
        "equipos_computo_id": prestamo.equipos_computo_id,
        "usuario_presta_id": prestamo.usuario_presta_id,
        "usuario_prestado_id": prestamo.usuario_prestado_id,
        "estado_prestamo_id": prestamo.estado_prestamo_id,
        "fecha_prestamo": prestamo.fecha_prestamo,
        "fecha_devolucion": prestamo.fecha_devolucion,
        "usuario_ultimo_cambio_id": prestamo.usuario_ultimo_cambio_id,
        "fecha_ultimo_cambio_estado": prestamo.fecha_ultimo_cambio_estado,
        "observaciones": prestamo.observaciones,
        "equipo_numero_serie": numero_serie,
        "equipo_marca": marca_nombre,
        "equipo_modelo": modelo,
        "equipo_tipo": tipo_nombre,
        "usuario_presta_nombre": prestamo.usuario_presta.nombre_completo if prestamo.usuario_presta else None,
        "usuario_prestado_nombre": prestamo.usuario_prestado.nombre_completo if prestamo.usuario_prestado else None,
        "estado_prestamo_nombre": prestamo.estado_prestamo.estado if prestamo.estado_prestamo else None
    }

# =============================================
# ENDPOINTS DE CREACIÓN (POST)
# =============================================

@router.post("/", response_model=PrestamoEquipoComputoResponse)
async def crear_prestamo_equipo(
    prestamo_data: PrestamoEquipoComputoCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Crear un nuevo préstamo de equipo de cómputo
    """
    try:
        # 1. Verificar que el equipo existe y está disponible
        equipo = await verificar_equipo_disponible(db, prestamo_data.equipos_computo_id)
        
        # 2. Verificar que el usuario prestado existe y está activo
        usuario_prestado = await verificar_usuario_activo(db, prestamo_data.usuario_prestado_id)
        
        # 3. INICIAR TRANSACCIÓN
        # 3.1 Cambiar estado del equipo a "Prestado" (estado_id = 2)
        equipo.estado_id = 2  # Prestado
        equipo.fecha_ultimo_cambio_estado = datetime.utcnow() - timedelta(hours=6)
        
        # 3.2 Crear el préstamo
        nuevo_prestamo = PrestamoEquipoComputo(
            equipos_computo_id=prestamo_data.equipos_computo_id,
            usuario_presta_id=usuario_actual.id,
            usuario_prestado_id=prestamo_data.usuario_prestado_id,
            estado_prestamo_id=1,  # "Vigente"
            fecha_prestamo=datetime.utcnow() - timedelta(hours=6),
            usuario_ultimo_cambio_id=usuario_actual.id,
            fecha_ultimo_cambio_estado=datetime.utcnow() - timedelta(hours=6),
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear préstamo de equipo: {str(e)}"
        )

# =============================================
# ENDPOINTS DE ACTUALIZACIÓN (PUT/PATCH)
# =============================================

@router.patch("/{prestamo_id}/devolver", response_model=PrestamoEquipoComputoResponse)
async def devolver_prestamo_equipo(
    prestamo_id: int,
    devolucion_data: PrestamoEquipoComputoDevolucion,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Registrar devolución de un préstamo de equipo
    """
    try:
        # 1. Obtener el préstamo
        result = await db.execute(
            select(PrestamoEquipoComputo).filter(PrestamoEquipoComputo.id == prestamo_id)
        )
        prestamo = result.scalar_one_or_none()
        
        if not prestamo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Préstamo de equipo no encontrado"
            )
        
        if prestamo.estado_prestamo_id != 1:  # Si no está vigente
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden devolver préstamos vigentes"
            )
        
        # 2. INICIAR TRANSACCIÓN
        # 2.1 Cambiar estado del equipo a "Disponible"
        result_equipo = await db.execute(
            select(EquipoComputo).filter(EquipoComputo.id == prestamo.equipos_computo_id)
        )
        equipo = result_equipo.scalar_one_or_none()
        
        if equipo:
            equipo.estado_id = 1  # Disponible
            equipo.fecha_ultimo_cambio_estado = datetime.utcnow() - timedelta(hours=6)
        
        # 2.2 Actualizar préstamo
        prestamo.estado_prestamo_id = 3  # Terminado
        prestamo.fecha_devolucion = datetime.utcnow() - timedelta(hours=6)
        prestamo.usuario_ultimo_cambio_id = usuario_actual.id
        prestamo.fecha_ultimo_cambio_estado = datetime.utcnow() - timedelta(hours=6)
        
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
            detail=f"Error al registrar devolución de equipo: {str(e)}"
        )

@router.get("/usuario/{usuario_id}", response_model=List[PrestamoEquipoComputoConRelaciones])
async def listar_prestamos_equipo_usuario(
    usuario_id: int,
    solo_vigentes: bool = Query(True, description="Mostrar solo préstamos vigentes"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar préstamos de equipos de un usuario específico
    """
    query = select(PrestamoEquipoComputo).options(
        selectinload(PrestamoEquipoComputo.equipo_computo).selectinload(EquipoComputo.marca_equipo),
        selectinload(PrestamoEquipoComputo.equipo_computo).selectinload(EquipoComputo.tipo_equipo),
        selectinload(PrestamoEquipoComputo.usuario_presta),
        selectinload(PrestamoEquipoComputo.usuario_prestado),
        selectinload(PrestamoEquipoComputo.estado_prestamo)
    ).filter(PrestamoEquipoComputo.usuario_prestado_id == usuario_id)
    
    if solo_vigentes:
        query = query.where(PrestamoEquipoComputo.estado_prestamo_id == 1)  # Solo vigentes
    
    result = await db.execute(query)
    prestamos = result.scalars().all()
    
    # Construir respuesta con datos relacionados
    resultado = []
    for prestamo in prestamos:
        # Obtener datos de relaciones
        marca_nombre = None
        tipo_nombre = None
        numero_serie = None
        modelo = None
        
        if prestamo.equipo_computo:
            numero_serie = prestamo.equipo_computo.numero_serie
            modelo = prestamo.equipo_computo.modelo
            
            if prestamo.equipo_computo.marca_equipo:
                marca_nombre = prestamo.equipo_computo.marca_equipo.marca
            
            if prestamo.equipo_computo.tipo_equipo:
                tipo_nombre = prestamo.equipo_computo.tipo_equipo.tipo
        
        resultado.append({
            "id": prestamo.id,
            "equipos_computo_id": prestamo.equipos_computo_id,
            "usuario_presta_id": prestamo.usuario_presta_id,
            "usuario_prestado_id": prestamo.usuario_prestado_id,
            "estado_prestamo_id": prestamo.estado_prestamo_id,
            "fecha_prestamo": prestamo.fecha_prestamo,
            "fecha_devolucion": prestamo.fecha_devolucion,
            "usuario_ultimo_cambio_id": prestamo.usuario_ultimo_cambio_id,
            "fecha_ultimo_cambio_estado": prestamo.fecha_ultimo_cambio_estado,
            "observaciones": prestamo.observaciones,
            "equipo_numero_serie": numero_serie,
            "equipo_marca": marca_nombre,
            "equipo_modelo": modelo,
            "equipo_tipo": tipo_nombre,
            "usuario_presta_nombre": prestamo.usuario_presta.nombre_completo if prestamo.usuario_presta else None,
            "usuario_prestado_nombre": prestamo.usuario_prestado.nombre_completo if prestamo.usuario_prestado else None,
            "estado_prestamo_nombre": prestamo.estado_prestamo.estado if prestamo.estado_prestamo else None
        })
    
    return resultado