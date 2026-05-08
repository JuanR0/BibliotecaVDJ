# src/api/routers/mobiliario.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from config.database import get_db
from schemas.mobiliario import (
    MobiliarioCreate,
    MobiliarioResponse,
    MobiliarioUpdate,
    MobiliarioListResponse,
    MobiliarioConRelacionesResponse,
    EstadoMobiliarioResponse,
    TipoMobiliarioResponse
)
from core.security import (
    obtener_usuario_actual, 
    requerir_puede_consultar,
    requerir_puede_gestionar_recursos
)
from models import Mobiliario, EstadoMobiliario, Usuario, Area, TipoMobiliario  

router = APIRouter(prefix="/api/mobiliario", tags=["mobiliario"])

# =============================================
# CONSTANTES
# =============================================
ESTADO_DISPONIBLE = 1
ESTADO_DADO_DE_BAJA  = 4  # Asumiendo que estados_mobiliario tiene estado 5 para eliminado

# =============================================
# FUNCIONES AUXILIARES
# =============================================

async def verificar_relaciones_mobiliario(db: AsyncSession, mobiliario_data: dict):
    """Verifica que existan las relaciones del mobiliario"""
    relaciones = [
        (mobiliario_data.get('area_id'), Area, "Área"),
        (mobiliario_data.get('estado_id'), EstadoMobiliario, "Estado"),
        (mobiliario_data.get('tipo_mobiliario_id'), TipoMobiliario, "Tipo de mobiliario") 
    ]
    
    for valor, modelo, nombre in relaciones:
        if valor is not None:
            result = await db.execute(select(modelo).filter(modelo.id == valor))
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{nombre} no encontrado"
                )

# =============================================
# ENDPOINTS DE CONSULTA (Todos los usuarios autenticados)
# =============================================

@router.get("/", response_model=MobiliarioListResponse)
async def listar_mobiliario(
    pagina: int = Query(1, ge=1, description="Página actual"),
    por_pagina: int = Query(10, ge=1, le=100, description="Elementos por página"),
    tipo_mobiliario_id: Optional[int] = Query(None, description="Filtrar por tipo de mobiliario"),  
    area_id: Optional[int] = Query(None, description="Filtrar por área"),
    estado_id: Optional[int] = Query(None, description="Filtrar por estado"),
    incluir_eliminados: bool = Query(False, description="Incluir mobiliario eliminado"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar mobiliario con filtros
    """
    from sqlalchemy.orm import selectinload
    
    query = select(Mobiliario).options(
        selectinload(Mobiliario.tipo_mobiliario),
        selectinload(Mobiliario.area),
        selectinload(Mobiliario.estado),
        selectinload(Mobiliario.usuario_creador)
    )
    
    # Aplicar filtros
    if tipo_mobiliario_id:  # ✅ CAMBIADO: era 'tipo_mobiliario'
        query = query.filter(Mobiliario.tipo_mobiliario_id == tipo_mobiliario_id)
    if area_id:
        query = query.filter(Mobiliario.area_id == area_id)
    if estado_id:
        query = query.filter(Mobiliario.estado_id == estado_id)

    # Contar total
    total_query = select(func.count()).select_from(Mobiliario)
    
    # Aplicar mismos filtros al count
    if not incluir_eliminados:
        total_query = total_query.filter(Mobiliario.estado_id != ESTADO_DADO_DE_BAJA )
    if tipo_mobiliario_id:
        total_query = total_query.filter(Mobiliario.tipo_mobiliario.ilike(f"%{tipo_mobiliario_id}%"))
    if area_id:
        total_query = total_query.filter(Mobiliario.area_id == area_id)
    if estado_id:
        total_query = total_query.filter(Mobiliario.estado_id == estado_id)
    
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    # Aplicar paginación
    offset = (pagina - 1) * por_pagina
    query = query.offset(offset).limit(por_pagina)
    
    # Ejecutar query
    result = await db.execute(query)
    mobiliarios = result.scalars().all()
    
    # Construir respuesta con nombres de relaciones
    mobiliarios_con_relaciones = []
    for mobiliario in mobiliarios:
        mobiliario_dict = MobiliarioConRelacionesResponse.model_validate(mobiliario)
        mobiliario_dict.tipo_mobiliario_nombre = mobiliario.tipo_mobiliario.tipo
        mobiliario_dict.area_nombre = mobiliario.area.nombre
        mobiliario_dict.estado_nombre = mobiliario.estado.estado
        mobiliario_dict.usuario_creador_nombre = mobiliario.usuario_creador.nombre_completo
        mobiliarios_con_relaciones.append(mobiliario_dict)
    
    return MobiliarioListResponse(
        mobiliarios=mobiliarios_con_relaciones,
        total=total,
        pagina=pagina,
        por_pagina=por_pagina
    )

@router.get("/{mobiliario_id}", response_model=MobiliarioConRelacionesResponse)
async def obtener_mobiliario(
    mobiliario_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Obtener información detallada de un mobiliario
    """
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Mobiliario)
        .options(
            selectinload(Mobiliario.tipo_mobiliario), 
            selectinload(Mobiliario.area),
            selectinload(Mobiliario.estado),
            selectinload(Mobiliario.usuario_creador)
        )
        .filter(Mobiliario.id == mobiliario_id)
    )
    mobiliario = result.scalar_one_or_none()
    
    if not mobiliario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mobiliario no encontrado"
        )
    
    # Construir respuesta con nombres
    mobiliario_response = MobiliarioConRelacionesResponse.model_validate(mobiliario)
    mobiliario_response.tipo_mobiliario_nombre = mobiliario.tipo_mobiliario.tipo 
    mobiliario_response.area_nombre = mobiliario.area.nombre
    mobiliario_response.estado_nombre = mobiliario.estado.estado
    mobiliario_response.usuario_creador_nombre = mobiliario.usuario_creador.nombre_completo
    
    return mobiliario_response

# =============================================
# ENDPOINTS DE GESTIÓN (Solo admin avanzado y super admin)
# =============================================

@router.post("/", response_model=MobiliarioResponse)
async def crear_mobiliario(
    mobiliario_data: MobiliarioCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Crear nuevo mobiliario
    """
    # Verificar que las relaciones existan
    await verificar_relaciones_mobiliario(db, mobiliario_data.model_dump())
    
    # Crear nuevo mobiliario
    nuevo_mobiliario = Mobiliario(
        **mobiliario_data.model_dump(),
        usuario_creador_id=usuario_actual.id
    )
    
    db.add(nuevo_mobiliario)
    await db.commit()
    await db.refresh(nuevo_mobiliario)
    
    return nuevo_mobiliario

@router.put("/{mobiliario_id}", response_model=MobiliarioResponse)
async def actualizar_mobiliario(
    mobiliario_id: int,
    mobiliario_data: MobiliarioUpdate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Actualizar información de mobiliario
    """
    result = await db.execute(select(Mobiliario).filter(Mobiliario.id == mobiliario_id))
    mobiliario = result.scalar_one_or_none()
    
    if not mobiliario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mobiliario no encontrado"
        )
    
    update_data = mobiliario_data.model_dump(exclude_unset=True)
    
    # Verificar relaciones si se están actualizando
    await verificar_relaciones_mobiliario(db, update_data)
    
    # Actualizar fecha de cambio de estado si se cambia el estado
    if 'estado_id' in update_data:
        mobiliario.fecha_ultimo_cambio_estado = datetime.utcnow()
    
    # Actualizar campos
    for field, value in update_data.items():
        setattr(mobiliario, field, value)
    
    await db.commit()
    await db.refresh(mobiliario)
    
    return mobiliario

@router.patch("/{mobiliario_id}/desactivar", response_model=MobiliarioResponse)
async def desactivar_mobiliario(
    mobiliario_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Soft delete - Cambiar mobiliario a estado "No disponible"
    """
    result = await db.execute(
        select(Mobiliario).filter(
            Mobiliario.id == mobiliario_id,
            Mobiliario.estado_id != ESTADO_DADO_DE_BAJA 
        )
    )
    mobiliario = result.scalar_one_or_none()
    
    if not mobiliario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mobiliario no encontrado o ya eliminado"
        )
    
    # SOFT DELETE: Cambiar a estado 5
    mobiliario.estado_id = ESTADO_DADO_DE_BAJA 
    mobiliario.fecha_ultimo_cambio_estado = datetime.utcnow()
    
    await db.commit()
    await db.refresh(mobiliario)
    
    return mobiliario

@router.patch("/{mobiliario_id}/reactivar", response_model=MobiliarioResponse)
async def reactivar_mobiliario(
    mobiliario_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Reactivar mobiliario - Cambiar de estado "No disponible" a "Disponible"
    """
    result = await db.execute(
        select(Mobiliario).filter(
            Mobiliario.id == mobiliario_id,
            Mobiliario.estado_id == ESTADO_DADO_DE_BAJA 
        )
    )
    mobiliario = result.scalar_one_or_none()
    
    if not mobiliario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mobiliario no encontrado o ya está activo"
        )
    
    # REACTIVAR: Cambiar a estado 1
    mobiliario.estado_id = ESTADO_DISPONIBLE
    mobiliario.fecha_ultimo_cambio_estado = datetime.utcnow()
    
    await db.commit()
    await db.refresh(mobiliario)
    
    return mobiliario

# =============================================
# ENDPOINTS PARA DATOS AUXILIARES
# =============================================

@router.get("/auxiliares/tipos-mobiliario", response_model=List[TipoMobiliarioResponse])
async def listar_tipos_mobiliario(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """Listar todos los tipos de mobiliario"""
    result = await db.execute(select(TipoMobiliario).order_by(TipoMobiliario.tipo))
    tipos = result.scalars().all()
    return tipos


@router.get("/auxiliares/estados-mobiliario", response_model=List[EstadoMobiliarioResponse])
async def listar_estados_mobiliario(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """Listar todos los estados de mobiliario"""
    result = await db.execute(select(EstadoMobiliario).order_by(EstadoMobiliario.estado))
    estados = result.scalars().all()
    return estados


# =============================================
# ENDPOINT PARA ELIMINAR PERMANENTEMENTE
# =============================================


@router.delete("/{mobiliario_id}", response_model=dict)
async def eliminar_mobiliario_permanente(
    mobiliario_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """Eliminar mobiliario permanentemente. Solo si está dado de baja."""
    result = await db.execute(
        select(Mobiliario).filter(Mobiliario.id == mobiliario_id)
    )
    mobiliario = result.scalar_one_or_none()

    if not mobiliario:
        raise HTTPException(status_code=404, detail="Mobiliario no encontrado")

    if mobiliario.estado_id != ESTADO_DADO_DE_BAJA:
        raise HTTPException(
            status_code=400,
            detail="Solo se puede eliminar mobiliario dado de baja"
        )

    await db.delete(mobiliario)
    await db.commit()

    return {"message": "Mobiliario eliminado permanentemente"}