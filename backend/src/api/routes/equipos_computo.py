# src/api/routers/equipos_computo.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from config.database import get_db
from schemas.equipos_computo import (
    EquipoComputoCreate,
    EquipoComputoResponse,
    EquipoComputoUpdate,
    EquipoComputoListResponse,
    EquipoComputoConRelacionesResponse,
    MarcaEquipoComputoResponse,
    TipoEquipoComputoResponse,
    EstadoEquipoResponse
)
from core.security import (
    obtener_usuario_actual, 
    requerir_puede_consultar,
    requerir_puede_gestionar_recursos
)
from models import EquipoComputo, MarcaEquipoComputo, TipoEquipoComputo, EstadoEquipo, Usuario, Area

router = APIRouter(prefix="/api/equipos-computo", tags=["equipos-computo"])

# =============================================
# CONSTANTES
# =============================================
ESTADO_DISPONIBLE = 1
ESTADO_ELIMINADO = 5  # Asumiendo que estados_equipo tiene estado 5 para eliminado

# =============================================
# FUNCIONES AUXILIARES
# =============================================

async def verificar_relaciones_equipo_computo(db: AsyncSession, equipo_data: dict):
    """Verifica que existan las relaciones del equipo de cómputo"""
    relaciones = [
        (equipo_data.get('marca_id'), MarcaEquipoComputo, "Marca"),
        (equipo_data.get('tipo_equipo_id'), TipoEquipoComputo, "Tipo de equipo"),
        (equipo_data.get('area_id'), Area, "Área"),
        (equipo_data.get('estado_id'), EstadoEquipo, "Estado")
    ]
    
    for valor, modelo, nombre in relaciones:
        if valor is not None:
            result = await db.execute(select(modelo).filter(modelo.id == valor))
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{nombre} no encontrado"
                )

async def verificar_numero_serie_unico(
    db: AsyncSession,
    numero_serie: str,
    equipo_id: Optional[int] = None
) -> bool:
    """
    Verifica que no exista otro equipo con el mismo número de serie
    """
    query = select(EquipoComputo).filter(EquipoComputo.numero_serie == numero_serie)
    
    if equipo_id:
        query = query.filter(EquipoComputo.id != equipo_id)
    
    result = await db.execute(query)
    equipo_existente = result.scalar_one_or_none()
    
    if equipo_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un equipo con ese número de serie"
        )
    
    return True

# =============================================
# ENDPOINTS DE CONSULTA (Todos los usuarios autenticados)
# =============================================

@router.get("/", response_model=EquipoComputoListResponse)
async def listar_equipos_computo(
    pagina: int = Query(1, ge=1, description="Página actual"),
    por_pagina: int = Query(10, ge=1, le=100, description="Elementos por página"),
    numero_serie: Optional[str] = Query(None, description="Filtrar por número de serie"),
    modelo: Optional[str] = Query(None, description="Filtrar por modelo"),
    marca_id: Optional[int] = Query(None, description="Filtrar por marca"),
    tipo_equipo_id: Optional[int] = Query(None, description="Filtrar por tipo de equipo"),
    area_id: Optional[int] = Query(None, description="Filtrar por área"),
    estado_id: Optional[int] = Query(None, description="Filtrar por estado"),
    es_prestable: Optional[bool] = Query(None, description="Filtrar por prestable"),
    incluir_eliminados: bool = Query(False, description="Incluir equipos eliminados"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar equipos de cómputo con filtros
    """
    from sqlalchemy.orm import selectinload
    
    query = select(EquipoComputo).options(
        selectinload(EquipoComputo.marca_equipo),
        selectinload(EquipoComputo.tipo_equipo),
        selectinload(EquipoComputo.area),
        selectinload(EquipoComputo.estado),
        selectinload(EquipoComputo.usuario_registro)
    )
    
    # Excluir equipos eliminados por defecto
    if not incluir_eliminados:
        query = query.filter(EquipoComputo.estado_id != ESTADO_ELIMINADO)
    
    # Aplicar filtros
    if numero_serie:
        query = query.filter(EquipoComputo.numero_serie.ilike(f"%{numero_serie}%"))
    if modelo:
        query = query.filter(EquipoComputo.modelo.ilike(f"%{modelo}%"))
    if marca_id:
        query = query.filter(EquipoComputo.marca_id == marca_id)
    if tipo_equipo_id:
        query = query.filter(EquipoComputo.tipo_equipo_id == tipo_equipo_id)
    if area_id:
        query = query.filter(EquipoComputo.area_id == area_id)
    if estado_id:
        query = query.filter(EquipoComputo.estado_id == estado_id)
    if es_prestable is not None:
        query = query.filter(EquipoComputo.es_prestable == es_prestable)

    # Contar total
    total_query = select(func.count()).select_from(EquipoComputo)
    
    # Aplicar mismos filtros al count
    if not incluir_eliminados:
        total_query = total_query.filter(EquipoComputo.estado_id != ESTADO_ELIMINADO)
    if numero_serie:
        total_query = total_query.filter(EquipoComputo.numero_serie.ilike(f"%{numero_serie}%"))
    if modelo:
        total_query = total_query.filter(EquipoComputo.modelo.ilike(f"%{modelo}%"))
    if marca_id:
        total_query = total_query.filter(EquipoComputo.marca_id == marca_id)
    if tipo_equipo_id:
        total_query = total_query.filter(EquipoComputo.tipo_equipo_id == tipo_equipo_id)
    if area_id:
        total_query = total_query.filter(EquipoComputo.area_id == area_id)
    if estado_id:
        total_query = total_query.filter(EquipoComputo.estado_id == estado_id)
    if es_prestable is not None:
        total_query = total_query.filter(EquipoComputo.es_prestable == es_prestable)
    
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    # Aplicar paginación
    offset = (pagina - 1) * por_pagina
    query = query.offset(offset).limit(por_pagina)
    
    # Ejecutar query
    result = await db.execute(query)
    equipos = result.scalars().all()
    
    # Construir respuesta con nombres de relaciones
    equipos_con_relaciones = []
    for equipo in equipos:
        equipo_dict = EquipoComputoConRelacionesResponse.model_validate(equipo)
        equipo_dict.marca_nombre = equipo.marca_equipo.marca
        equipo_dict.tipo_equipo_nombre = equipo.tipo_equipo.tipo
        equipo_dict.area_nombre = equipo.area.nombre
        equipo_dict.estado_nombre = equipo.estado.estado
        equipo_dict.usuario_registro_nombre = equipo.usuario_registro.nombre_completo
        equipos_con_relaciones.append(equipo_dict)
    
    return EquipoComputoListResponse(
        equipos=equipos_con_relaciones,
        total=total,
        pagina=pagina,
        por_pagina=por_pagina
    )

@router.get("/{equipo_id}", response_model=EquipoComputoConRelacionesResponse)
async def obtener_equipo_computo(
    equipo_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Obtener información detallada de un equipo de cómputo
    """
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(EquipoComputo)
        .options(
            selectinload(EquipoComputo.marca_equipo),
            selectinload(EquipoComputo.tipo_equipo),
            selectinload(EquipoComputo.area),
            selectinload(EquipoComputo.estado),
            selectinload(EquipoComputo.usuario_registro)
        )
        .filter(EquipoComputo.id == equipo_id)
    )
    equipo = result.scalar_one_or_none()
    
    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo de cómputo no encontrado"
        )
    
    # Construir respuesta con nombres
    equipo_response = EquipoComputoConRelacionesResponse.model_validate(equipo)
    equipo_response.marca_nombre = equipo.marca_equipo.marca
    equipo_response.tipo_equipo_nombre = equipo.tipo_equipo.tipo
    equipo_response.area_nombre = equipo.area.nombre
    equipo_response.estado_nombre = equipo.estado.estado
    equipo_response.usuario_registro_nombre = equipo.usuario_registro.nombre_completo
    
    return equipo_response

# =============================================
# ENDPOINTS DE GESTIÓN (Solo admin avanzado y super admin)
# =============================================

@router.post("/", response_model=EquipoComputoResponse)
async def crear_equipo_computo(
    equipo_data: EquipoComputoCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Crear un nuevo equipo de cómputo
    """
    # Verificar que el número de serie sea único
    await verificar_numero_serie_unico(db, equipo_data.numero_serie)
    
    # Verificar que las relaciones existan
    await verificar_relaciones_equipo_computo(db, equipo_data.model_dump())
    
    # Crear nuevo equipo
    nuevo_equipo = EquipoComputo(
        **equipo_data.model_dump(),
        usuario_registro_id=usuario_actual.id
    )
    
    db.add(nuevo_equipo)
    await db.commit()
    await db.refresh(nuevo_equipo)
    
    return nuevo_equipo

@router.put("/{equipo_id}", response_model=EquipoComputoResponse)
async def actualizar_equipo_computo(
    equipo_id: int,
    equipo_data: EquipoComputoUpdate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Actualizar información de equipo de cómputo
    """
    result = await db.execute(select(EquipoComputo).filter(EquipoComputo.id == equipo_id))
    equipo = result.scalar_one_or_none()
    
    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo de cómputo no encontrado"
        )
    
    update_data = equipo_data.model_dump(exclude_unset=True)
    
    # Verificar número de serie único si se está actualizando
    if 'numero_serie' in update_data:
        await verificar_numero_serie_unico(db, update_data['numero_serie'], equipo_id)
    
    # Verificar relaciones si se están actualizando
    await verificar_relaciones_equipo_computo(db, update_data)
    
    # Actualizar fecha de cambio de estado si se cambia el estado
    if 'estado_id' in update_data:
        equipo.fecha_ultimo_cambio_estado = datetime.utcnow()
    
    # Actualizar campos
    for field, value in update_data.items():
        setattr(equipo, field, value)
    
    await db.commit()
    await db.refresh(equipo)
    
    return equipo

@router.patch("/{equipo_id}/desactivar", response_model=EquipoComputoResponse)
async def desactivar_equipo_computo(
    equipo_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Soft delete - Cambiar equipo a estado "No disponible"
    """
    result = await db.execute(
        select(EquipoComputo).filter(
            EquipoComputo.id == equipo_id,
            EquipoComputo.estado_id != ESTADO_ELIMINADO
        )
    )
    equipo = result.scalar_one_or_none()
    
    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo de cómputo no encontrado o ya eliminado"
        )
    
    # SOFT DELETE: Cambiar a estado 5
    equipo.estado_id = ESTADO_ELIMINADO
    equipo.fecha_ultimo_cambio_estado = datetime.utcnow()
    
    await db.commit()
    await db.refresh(equipo)
    
    return equipo

@router.patch("/{equipo_id}/reactivar", response_model=EquipoComputoResponse)
async def reactivar_equipo_computo(
    equipo_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Reactivar equipo - Cambiar de estado "No disponible" a "Disponible"
    """
    result = await db.execute(
        select(EquipoComputo).filter(
            EquipoComputo.id == equipo_id,
            EquipoComputo.estado_id == ESTADO_ELIMINADO
        )
    )
    equipo = result.scalar_one_or_none()
    
    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo de cómputo no encontrado o ya está activo"
        )
    
    # REACTIVAR: Cambiar a estado 1
    equipo.estado_id = ESTADO_DISPONIBLE
    equipo.fecha_ultimo_cambio_estado = datetime.utcnow()
    
    await db.commit()
    await db.refresh(equipo)
    
    return equipo

# =============================================
# ENDPOINTS PARA DATOS AUXILIARES
# =============================================

@router.get("/auxiliares/marcas", response_model=List[MarcaEquipoComputoResponse])
async def listar_marcas_equipo_computo(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """Listar todas las marcas de equipo de cómputo"""
    result = await db.execute(select(MarcaEquipoComputo).order_by(MarcaEquipoComputo.marca))
    marcas = result.scalars().all()
    return marcas

@router.get("/auxiliares/tipos-equipo", response_model=List[TipoEquipoComputoResponse])
async def listar_tipos_equipo_computo(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """Listar todos los tipos de equipo de cómputo"""
    result = await db.execute(select(TipoEquipoComputo).order_by(TipoEquipoComputo.tipo))
    tipos = result.scalars().all()
    return tipos

@router.get("/auxiliares/estados-equipo", response_model=List[EstadoEquipoResponse])
async def listar_estados_equipo(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """Listar todos los estados de equipo"""
    result = await db.execute(select(EstadoEquipo).order_by(EstadoEquipo.estado))
    estados = result.scalars().all()
    return estados