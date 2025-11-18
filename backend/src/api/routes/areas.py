# src/api/routers/areas.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from config.database import get_db
from schemas.areas import (
    AreaCreate,
    AreaResponse,
    AreaUpdate,
    AreaListResponse,
    AreaConRelacionesResponse,
    EstadoAreaResponse
)
from core.security import (
    obtener_usuario_actual, 
    requerir_puede_consultar,
    requerir_puede_gestionar_recursos
)
from models import Area, EstadoArea, Usuario, EquipoComputo, Mobiliario

router = APIRouter(prefix="/api/areas", tags=["areas"])

# =============================================
# CONSTANTES
# =============================================
ESTADO_DISPONIBLE = 1
ESTADO_ELIMINADO = 5

# =============================================
# FUNCIONES AUXILIARES
# =============================================

async def verificar_relaciones_area(db: AsyncSession, area_data: dict):
    """Verifica que existan las relaciones del área"""
    if area_data.get('estado_id') is not None:
        result = await db.execute(
            select(EstadoArea).filter(EstadoArea.id == area_data.get('estado_id'))
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estado de área no encontrado"
            )

async def verificar_nombre_area_unico(
    db: AsyncSession,
    nombre: str,
    area_id: Optional[int] = None
) -> bool:
    """
    Verifica que no exista otra área DISPONIBLE con el mismo nombre
    """
    query = select(Area).filter(
        Area.nombre == nombre,
        Area.estado_id == ESTADO_DISPONIBLE
    )
    
    if area_id:
        query = query.filter(Area.id != area_id)
    
    result = await db.execute(query)
    area_existente = result.scalar_one_or_none()
    
    if area_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un área disponible con ese nombre"
        )
    
    return True

async def verificar_area_sin_recursos_activos(
    db: AsyncSession,
    area_id: int
) -> bool:
    """
    Verifica que el área no tenga equipos o mobiliario activos asociados
    """
    # Verificar equipos de cómputo activos en esta área
    result_equipos = await db.execute(
        select(EquipoComputo).filter(
            EquipoComputo.area_id == area_id,
            EquipoComputo.estado_id == 1  # Equipos disponibles
        )
    )
    equipos_activos = result_equipos.scalars().first()
    
    if equipos_activos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede desactivar el área porque tiene equipos de cómputo activos asociados"
        )
    
    # Verificar mobiliario activo en esta área
    result_mobiliario = await db.execute(
        select(Mobiliario).filter(
            Mobiliario.area_id == area_id,
            Mobiliario.estado_id == 1  # Mobiliario disponible
        )
    )
    mobiliario_activo = result_mobiliario.scalars().first()
    
    if mobiliario_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede desactivar el área porque tiene mobiliario activo asociado"
        )
    
    return True

# =============================================
# ENDPOINTS DE CONSULTA (Todos los usuarios autenticados)
# =============================================

@router.get("/", response_model=AreaListResponse)
async def listar_areas(
    pagina: int = Query(1, ge=1, description="Página actual"),
    por_pagina: int = Query(10, ge=1, le=100, description="Elementos por página"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre"),
    estado_id: Optional[int] = Query(None, ge=1, le=5, description="Filtrar por estado"),
    es_prestable: Optional[bool] = Query(None, description="Filtrar por prestable"),
    incluir_eliminadas: bool = Query(False, description="Incluir áreas eliminadas (estado 5)"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar áreas con filtros (por defecto excluye áreas eliminadas)
    """
    from sqlalchemy.orm import selectinload
    
    # ✅ CORREGIDO: Usar selectinload como en libros y libros virtuales
    query = select(Area).options(
        selectinload(Area.estado),
        selectinload(Area.usuario_registro)
    )
    
    # Excluir áreas eliminadas por defecto
    if not incluir_eliminadas:
        query = query.filter(Area.estado_id != ESTADO_ELIMINADO)
    
    # Aplicar filtros adicionales
    if nombre:
        query = query.filter(Area.nombre.ilike(f"%{nombre}%"))
    if estado_id:
        query = query.filter(Area.estado_id == estado_id)
    if es_prestable is not None:
        query = query.filter(Area.es_prestable == es_prestable)

    # Contar total (sin relaciones para eficiencia)
    total_query = select(func.count()).select_from(Area)
    
    # Aplicar mismos filtros al count
    if not incluir_eliminadas:
        total_query = total_query.filter(Area.estado_id != ESTADO_ELIMINADO)
    if nombre:
        total_query = total_query.filter(Area.nombre.ilike(f"%{nombre}%"))
    if estado_id:
        total_query = total_query.filter(Area.estado_id == estado_id)
    if es_prestable is not None:
        total_query = total_query.filter(Area.es_prestable == es_prestable)
    
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    # Aplicar paginación
    offset = (pagina - 1) * por_pagina
    query = query.offset(offset).limit(por_pagina)
    
    # Ejecutar query
    result = await db.execute(query)
    areas = result.scalars().all()
    
    # Construir respuesta con nombres de relaciones
    areas_con_relaciones = []
    for area in areas:
        area_dict = AreaConRelacionesResponse.model_validate(area)
        # ✅ Ahora las relaciones están cargadas por selectinload
        area_dict.estado_nombre = area.estado.estado
        area_dict.usuario_registro_nombre = area.usuario_registro.nombre_completo
        areas_con_relaciones.append(area_dict)
    
    return AreaListResponse(
        areas=areas_con_relaciones,
        total=total,
        pagina=pagina,
        por_pagina=por_pagina
    )

@router.get("/{area_id}", response_model=AreaConRelacionesResponse)
async def obtener_area(
    area_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Obtener información detallada de un área (solo si está disponible)
    """
    from sqlalchemy.orm import selectinload
    
    # ✅ CORREGIDO: Usar selectinload como en libros y libros virtuales
    result = await db.execute(
        select(Area)
        .options(
            selectinload(Area.estado),
            selectinload(Area.usuario_registro)
        )
        .filter(
            Area.id == area_id,
            Area.estado_id == ESTADO_DISPONIBLE
        )
    )
    area = result.scalar_one_or_none()
    
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área no encontrada o no disponible"
        )
    
    # Construir respuesta con nombres
    area_response = AreaConRelacionesResponse.model_validate(area)
    area_response.estado_nombre = area.estado.estado
    area_response.usuario_registro_nombre = area.usuario_registro.nombre_completo
    
    return area_response

# =============================================
# ENDPOINTS DE GESTIÓN (Solo admin avanzado y super admin)
# =============================================

@router.post("/", response_model=AreaResponse)
async def crear_area(
    area_data: AreaCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Crear una nueva área (solo admin avanzado y super admin)
    """
    # Validar que no se cree directamente como eliminada
    if area_data.estado_id == ESTADO_ELIMINADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede crear un área directamente como eliminada"
        )
    
    # Verificar que el nombre sea único entre áreas disponibles
    await verificar_nombre_area_unico(db, area_data.nombre)
    
    # Verificar que las relaciones existan
    await verificar_relaciones_area(db, area_data.model_dump())
    
    # Crear nueva área
    nueva_area = Area(
        **area_data.model_dump(),
        usuario_registro_id=usuario_actual.id
    )
    
    db.add(nueva_area)
    await db.commit()
    await db.refresh(nueva_area)
    
    return nueva_area

@router.put("/{area_id}", response_model=AreaResponse)
async def actualizar_area(
    area_id: int,
    area_data: AreaUpdate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Actualizar información de área (solo si está disponible)
    """
    result = await db.execute(
        select(Area).filter(
            Area.id == area_id,
            Area.estado_id == ESTADO_DISPONIBLE
        )
    )
    area = result.scalar_one_or_none()
    
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área no encontrada o no disponible"
        )
    
    update_data = area_data.model_dump(exclude_unset=True)
    
    # Validar que no se actualice a estado eliminado (usar endpoint específico)
    if 'estado_id' in update_data and update_data['estado_id'] == ESTADO_ELIMINADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use el endpoint /desactivar para eliminar el área"
        )
    
    # Verificar nombre único si se está actualizando
    if 'nombre' in update_data:
        await verificar_nombre_area_unico(db, update_data['nombre'], area_id)
    
    # Verificar relaciones si se están actualizando
    await verificar_relaciones_area(db, update_data)
    
    # Actualizar fecha de cambio de estado si se cambia el estado
    if 'estado_id' in update_data:
        area.fecha_ultimo_cambio_estado = datetime.utcnow()
    
    # Actualizar campos
    for field, value in update_data.items():
        setattr(area, field, value)
    
    await db.commit()
    await db.refresh(area)
    
    return area

@router.patch("/{area_id}/desactivar", response_model=AreaResponse)
async def desactivar_area(
    area_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Soft delete - Cambiar área a estado "No disponible" (5)
    """
    result = await db.execute(
        select(Area).filter(
            Area.id == area_id,
            Area.estado_id == ESTADO_DISPONIBLE
        )
    )
    area = result.scalar_one_or_none()
    
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área no encontrada o ya no disponible"
        )
    
    # Verificar que no tenga recursos activos asociados
    await verificar_area_sin_recursos_activos(db, area_id)
    
    # SOFT DELETE: Cambiar a estado 5
    area.estado_id = ESTADO_ELIMINADO
    area.fecha_ultimo_cambio_estado = datetime.utcnow()
    
    await db.commit()
    await db.refresh(area)
    
    return area

@router.patch("/{area_id}/reactivar", response_model=AreaResponse)
async def reactivar_area(
    area_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Reactivar área - Cambiar de estado "No disponible" (5) a "Disponible" (1)
    """
    # Buscar área en estado 5
    result = await db.execute(
        select(Area).filter(
            Area.id == area_id,
            Area.estado_id == ESTADO_ELIMINADO
        )
    )
    area = result.scalar_one_or_none()
    
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área no encontrada o ya está disponible"
        )
    
    # Verificar que el nombre sea único al reactivar
    await verificar_nombre_area_unico(db, area.nombre, area_id)
    
    # REACTIVAR: Cambiar a estado 1
    area.estado_id = ESTADO_DISPONIBLE
    area.fecha_ultimo_cambio_estado = datetime.utcnow()
    
    await db.commit()
    await db.refresh(area)
    
    return area

# =============================================
# ENDPOINTS PARA DATOS AUXILIARES
# =============================================

@router.get("/auxiliares/estados-area", response_model=List[EstadoAreaResponse])
async def listar_estados_area(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """Listar todos los estados de área"""
    result = await db.execute(select(EstadoArea).order_by(EstadoArea.estado))
    estados = result.scalars().all()
    return estados