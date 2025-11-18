# src/api/routers/tesis.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from config.database import get_db
from schemas.tesis import (
    TesisCreate,
    TesisResponse,
    TesisUpdate,
    TesisListResponse,
    TesisConRelacionesResponse,
    TesisSubirVirtual
)
from core.security import (
    obtener_usuario_actual, 
    requerir_puede_consultar,
    requerir_puede_gestionar_recursos
)
from models import Tesis, EstadoLibro, EstadoVirtual, Usuario

router = APIRouter(prefix="/api/tesis", tags=["tesis"])

# =============================================
# CONSTANTES
# =============================================
# Estados físicos (estados_libro)
ESTADO_FISICO_DISPONIBLE = 1
ESTADO_FISICO_RETIRADO = 4

# Estados virtuales (estados_virtual)  
ESTADO_VIRTUAL_DISPONIBLE = 1
ESTADO_VIRTUAL_NO_DISPONIBLE = 2

# =============================================
# FUNCIONES AUXILIARES
# =============================================

async def verificar_relaciones_tesis(db: AsyncSession, tesis_data: dict):
    """Verifica que existan las relaciones de la tesis"""
    relaciones = [
        (tesis_data.get('estado_fisico_id'), EstadoLibro, "Estado físico"),
        (tesis_data.get('estado_virtual_id'), EstadoVirtual, "Estado virtual")
    ]
    
    for valor, modelo, nombre in relaciones:
        if valor is not None:
            result = await db.execute(select(modelo).filter(modelo.id == valor))
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{nombre} no encontrado"
                )

async def verificar_codigo_decimal_unico(
    db: AsyncSession,
    codigo_decimal: str,
    tesis_id: Optional[int] = None
) -> bool:
    """
    Verifica que no exista otra tesis con el mismo código decimal
    """
    query = select(Tesis).filter(Tesis.codigo_decimal == codigo_decimal)
    
    if tesis_id:
        query = query.filter(Tesis.id != tesis_id)
    
    result = await db.execute(query)
    tesis_existente = result.scalar_one_or_none()
    
    if tesis_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una tesis con ese código decimal"
        )
    
    return True

# =============================================
# ENDPOINTS DE CONSULTA (Todos los usuarios autenticados)
# =============================================

@router.get("/", response_model=TesisListResponse)
async def listar_tesis(
    pagina: int = Query(1, ge=1, description="Página actual"),
    por_pagina: int = Query(10, ge=1, le=100, description="Elementos por página"),
    titulo: Optional[str] = Query(None, description="Filtrar por título"),
    nombre_autor: Optional[str] = Query(None, description="Filtrar por nombre del autor"),
    carrera: Optional[str] = Query(None, description="Filtrar por carrera"),
    codigo_decimal: Optional[str] = Query(None, description="Filtrar por código decimal"),
    estado_fisico_id: Optional[int] = Query(None, description="Filtrar por estado físico"),
    estado_virtual_id: Optional[int] = Query(None, description="Filtrar por estado virtual"),
    incluir_retiradas: bool = Query(False, description="Incluir tesis retiradas físicamente"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar tesis con filtros
    """
    from sqlalchemy.orm import selectinload
    
    query = select(Tesis).options(
        selectinload(Tesis.estado_fisico),
        selectinload(Tesis.estado_virtual),
        selectinload(Tesis.usuario_ingreso),
        selectinload(Tesis.usuario_subio_virtual)
    )
    
    # Excluir tesis retiradas físicamente por defecto
    if not incluir_retiradas:
        query = query.filter(Tesis.estado_fisico_id != ESTADO_FISICO_RETIRADO)
    
    # Aplicar filtros
    if titulo:
        query = query.filter(Tesis.titulo.ilike(f"%{titulo}%"))
    if nombre_autor:
        query = query.filter(Tesis.nombre_autor.ilike(f"%{nombre_autor}%"))
    if carrera:
        query = query.filter(Tesis.carrera.ilike(f"%{carrera}%"))
    if codigo_decimal:
        query = query.filter(Tesis.codigo_decimal.ilike(f"%{codigo_decimal}%"))
    if estado_fisico_id:
        query = query.filter(Tesis.estado_fisico_id == estado_fisico_id)
    if estado_virtual_id:
        query = query.filter(Tesis.estado_virtual_id == estado_virtual_id)

    # Contar total
    total_query = select(func.count()).select_from(Tesis)
    
    # Aplicar mismos filtros al count
    if not incluir_retiradas:
        total_query = total_query.filter(Tesis.estado_fisico_id != ESTADO_FISICO_RETIRADO)
    if titulo:
        total_query = total_query.filter(Tesis.titulo.ilike(f"%{titulo}%"))
    if nombre_autor:
        total_query = total_query.filter(Tesis.nombre_autor.ilike(f"%{nombre_autor}%"))
    if carrera:
        total_query = total_query.filter(Tesis.carrera.ilike(f"%{carrera}%"))
    if codigo_decimal:
        total_query = total_query.filter(Tesis.codigo_decimal.ilike(f"%{codigo_decimal}%"))
    if estado_fisico_id:
        total_query = total_query.filter(Tesis.estado_fisico_id == estado_fisico_id)
    if estado_virtual_id:
        total_query = total_query.filter(Tesis.estado_virtual_id == estado_virtual_id)
    
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    # Aplicar paginación
    offset = (pagina - 1) * por_pagina
    query = query.offset(offset).limit(por_pagina)
    
    # Ejecutar query
    result = await db.execute(query)
    tesis_list = result.scalars().all()
    
    # Construir respuesta con nombres de relaciones
    tesis_con_relaciones = []
    for tesis in tesis_list:
        tesis_dict = TesisConRelacionesResponse.model_validate(tesis)
        tesis_dict.estado_fisico_nombre = tesis.estado_fisico.estado
        tesis_dict.estado_virtual_nombre = tesis.estado_virtual.estado
        tesis_dict.usuario_ingreso_nombre = tesis.usuario_ingreso.nombre_completo
        if tesis.usuario_subio_virtual:
            tesis_dict.usuario_subio_virtual_nombre = tesis.usuario_subio_virtual.nombre_completo
        tesis_con_relaciones.append(tesis_dict)
    
    return TesisListResponse(
        tesis=tesis_con_relaciones,
        total=total,
        pagina=pagina,
        por_pagina=por_pagina
    )

@router.get("/{tesis_id}", response_model=TesisConRelacionesResponse)
async def obtener_tesis(
    tesis_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Obtener información detallada de una tesis
    """
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Tesis)
        .options(
            selectinload(Tesis.estado_fisico),
            selectinload(Tesis.estado_virtual),
            selectinload(Tesis.usuario_ingreso),
            selectinload(Tesis.usuario_subio_virtual)
        )
        .filter(Tesis.id == tesis_id)
    )
    tesis = result.scalar_one_or_none()
    
    if not tesis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tesis no encontrada"
        )
    
    # Construir respuesta con nombres
    tesis_response = TesisConRelacionesResponse.model_validate(tesis)
    tesis_response.estado_fisico_nombre = tesis.estado_fisico.estado
    tesis_response.estado_virtual_nombre = tesis.estado_virtual.estado
    tesis_response.usuario_ingreso_nombre = tesis.usuario_ingreso.nombre_completo
    if tesis.usuario_subio_virtual:
        tesis_response.usuario_subio_virtual_nombre = tesis.usuario_subio_virtual.nombre_completo
    
    return tesis_response

# =============================================
# ENDPOINTS DE GESTIÓN (Solo admin avanzado y super admin)
# =============================================

@router.post("/", response_model=TesisResponse)
async def crear_tesis(
    tesis_data: TesisCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Crear nueva tesis
    """
    # Verificar que el código decimal sea único
    await verificar_codigo_decimal_unico(db, tesis_data.codigo_decimal)
    
    # Verificar que las relaciones existan
    await verificar_relaciones_tesis(db, tesis_data.model_dump())
    
    # Crear nueva tesis
    nueva_tesis = Tesis(
        **tesis_data.model_dump(),
        usuario_ingreso_id=usuario_actual.id
    )
    
    db.add(nueva_tesis)
    await db.commit()
    await db.refresh(nueva_tesis)
    
    return nueva_tesis

@router.put("/{tesis_id}", response_model=TesisResponse)
async def actualizar_tesis(
    tesis_id: int,
    tesis_data: TesisUpdate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Actualizar información de tesis
    """
    result = await db.execute(select(Tesis).filter(Tesis.id == tesis_id))
    tesis = result.scalar_one_or_none()
    
    if not tesis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tesis no encontrada"
        )
    
    update_data = tesis_data.model_dump(exclude_unset=True)
    
    # Verificar código decimal único si se está actualizando
    if 'codigo_decimal' in update_data:
        await verificar_codigo_decimal_unico(db, update_data['codigo_decimal'], tesis_id)
    
    # Verificar relaciones si se están actualizando
    await verificar_relaciones_tesis(db, update_data)
    
    # Actualizar fechas de cambio de estado si se cambian los estados
    if 'estado_fisico_id' in update_data:
        tesis.fecha_ultimo_cambio_estado_fisico = datetime.utcnow()
    
    if 'estado_virtual_id' in update_data:
        tesis.fecha_ultimo_cambio_estado_virtual = datetime.utcnow()
    
    # Actualizar campos
    for field, value in update_data.items():
        setattr(tesis, field, value)
    
    await db.commit()
    await db.refresh(tesis)
    
    return tesis

# =============================================
# ENDPOINTS ESPECIALES PARA ESTADOS
# =============================================

@router.patch("/{tesis_id}/retirar-fisico", response_model=TesisResponse)
async def retirar_tesis_fisico(
    tesis_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Retirar tesis físicamente (soft delete físico)
    """
    result = await db.execute(
        select(Tesis).filter(
            Tesis.id == tesis_id,
            Tesis.estado_fisico_id != ESTADO_FISICO_RETIRADO
        )
    )
    tesis = result.scalar_one_or_none()
    
    if not tesis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tesis no encontrada o ya retirada físicamente"
        )
    
    # SOFT DELETE FÍSICO: Cambiar a estado "Retirado" (4)
    tesis.estado_fisico_id = ESTADO_FISICO_RETIRADO
    tesis.fecha_ultimo_cambio_estado_fisico = datetime.utcnow()
    
    await db.commit()
    await db.refresh(tesis)
    
    return tesis

@router.patch("/{tesis_id}/reactivar-fisico", response_model=TesisResponse)
async def reactivar_tesis_fisico(
    tesis_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Reactivar tesis físicamente
    """
    result = await db.execute(
        select(Tesis).filter(
            Tesis.id == tesis_id,
            Tesis.estado_fisico_id == ESTADO_FISICO_RETIRADO
        )
    )
    tesis = result.scalar_one_or_none()
    
    if not tesis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tesis no encontrada o ya está activa físicamente"
        )
    
    # REACTIVAR FÍSICO: Cambiar a estado "Disponible" (1)
    tesis.estado_fisico_id = ESTADO_FISICO_DISPONIBLE
    tesis.fecha_ultimo_cambio_estado_fisico = datetime.utcnow()
    
    await db.commit()
    await db.refresh(tesis)
    
    return tesis

@router.patch("/{tesis_id}/desactivar-virtual", response_model=TesisResponse)
async def desactivar_tesis_virtual(
    tesis_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Desactivar tesis virtualmente
    """
    result = await db.execute(
        select(Tesis).filter(
            Tesis.id == tesis_id,
            Tesis.estado_virtual_id != ESTADO_VIRTUAL_NO_DISPONIBLE
        )
    )
    tesis = result.scalar_one_or_none()
    
    if not tesis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tesis no encontrada o ya desactivada virtualmente"
        )
    
    # DESACTIVAR VIRTUAL: Cambiar a estado "No disponible" (2)
    tesis.estado_virtual_id = ESTADO_VIRTUAL_NO_DISPONIBLE
    tesis.fecha_ultimo_cambio_estado_virtual = datetime.utcnow()
    
    await db.commit()
    await db.refresh(tesis)
    
    return tesis

@router.patch("/{tesis_id}/activar-virtual", response_model=TesisResponse)
async def activar_tesis_virtual(
    tesis_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Activar tesis virtualmente
    """
    result = await db.execute(
        select(Tesis).filter(
            Tesis.id == tesis_id,
            Tesis.estado_virtual_id == ESTADO_VIRTUAL_NO_DISPONIBLE
        )
    )
    tesis = result.scalar_one_or_none()
    
    if not tesis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tesis no encontrada o ya está activa virtualmente"
        )
    
    # ACTIVAR VIRTUAL: Cambiar a estado "Disponible" (1)
    tesis.estado_virtual_id = ESTADO_VIRTUAL_DISPONIBLE
    tesis.fecha_ultimo_cambio_estado_virtual = datetime.utcnow()
    
    await db.commit()
    await db.refresh(tesis)
    
    return tesis

@router.patch("/{tesis_id}/subir-virtual", response_model=TesisResponse)
async def subir_tesis_virtual(
    tesis_id: int,
    virtual_data: TesisSubirVirtual,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Subir/actualizar archivo virtual de tesis
    """
    result = await db.execute(select(Tesis).filter(Tesis.id == tesis_id))
    tesis = result.scalar_one_or_none()
    
    if not tesis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tesis no encontrada"
        )
    
    # Actualizar información virtual
    tesis.link_copia_virtual = virtual_data.link_copia_virtual
    tesis.usuario_subio_virtual_id = usuario_actual.id
    tesis.fecha_subida_virtual = datetime.utcnow()
    tesis.estado_virtual_id = ESTADO_VIRTUAL_DISPONIBLE
    tesis.fecha_ultimo_cambio_estado_virtual = datetime.utcnow()
    
    await db.commit()
    await db.refresh(tesis)
    
    return tesis