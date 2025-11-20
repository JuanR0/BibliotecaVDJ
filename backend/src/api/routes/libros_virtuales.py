# src/api/routers/libros_virtuales.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from config.database import get_db
from schemas.libros_virtuales import (
    LibroVirtualCreate,
    LibroVirtualResponse,
    LibroVirtualUpdate,
    LibroVirtualListResponse,
    LibroVirtualConRelacionesResponse,
    EstadoVirtualResponse,
    EditorialResponse,
    AreaConocimientoResponse
)
from core.security import (
    obtener_usuario_actual, 
    requerir_puede_consultar,
    requerir_puede_gestionar_recursos
)
from models import LibroVirtual, EstadoVirtual, Usuario, Editorial, AreaConocimiento

router = APIRouter(prefix="/api/libros-virtuales", tags=["libros-virtuales"])

# =============================================
# FUNCIONES AUXILIARES
# =============================================

async def verificar_relaciones_libro_virtual(db: AsyncSession, libro_data: dict):
    """Verifica que existan las relaciones del libro virtual"""
    relaciones = [
        (libro_data.get('editorial_id'), Editorial, "Editorial"),
        (libro_data.get('area_conocimiento_id'), AreaConocimiento, "Área de conocimiento"),
        (libro_data.get('estado_virtual_id'), EstadoVirtual, "Estado virtual")
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

@router.get("/", response_model=LibroVirtualListResponse)
async def listar_libros_virtuales(
    pagina: int = Query(1, ge=1, description="Página actual"),
    por_pagina: int = Query(10, ge=1, le=100, description="Elementos por página"),
    titulo: Optional[str] = Query(None, description="Filtrar por título"),
    autor: Optional[str] = Query(None, description="Filtrar por autor"),
    editorial_id: Optional[int] = Query(None, description="Filtrar por editorial"),
    area_conocimiento_id: Optional[int] = Query(None, description="Filtrar por área de conocimiento"),
    estado_virtual_id: Optional[int] = Query(None, description="Filtrar por estado"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Listar libros virtuales (todos los usuarios autenticados)
    """
    from sqlalchemy.orm import selectinload
    
    # ✅ CORREGIDO: Usar selectinload como en libros
    query = select(LibroVirtual).options(
        selectinload(LibroVirtual.editorial),
        selectinload(LibroVirtual.area_conocimiento),
        selectinload(LibroVirtual.estado_virtual),
        selectinload(LibroVirtual.usuario_subio)
    )
    
    # Aplicar filtros
    if titulo:
        query = query.filter(LibroVirtual.titulo.ilike(f"%{titulo}%"))
    if autor:
        query = query.filter(LibroVirtual.autor.ilike(f"%{autor}%"))
    if editorial_id:
        query = query.filter(LibroVirtual.editorial_id == editorial_id)
    if area_conocimiento_id:
        query = query.filter(LibroVirtual.area_conocimiento_id == area_conocimiento_id)
    if estado_virtual_id:
        query = query.filter(LibroVirtual.estado_virtual_id == estado_virtual_id)
    
    # Contar total (sin relaciones para eficiencia)
    total_query = select(func.count()).select_from(LibroVirtual)
    
    # Aplicar mismos filtros al count
    if titulo:
        total_query = total_query.filter(LibroVirtual.titulo.ilike(f"%{titulo}%"))
    if autor:
        total_query = total_query.filter(LibroVirtual.autor.ilike(f"%{autor}%"))
    if editorial_id:
        total_query = total_query.filter(LibroVirtual.editorial_id == editorial_id)
    if area_conocimiento_id:
        total_query = total_query.filter(LibroVirtual.area_conocimiento_id == area_conocimiento_id)
    if estado_virtual_id:
        total_query = total_query.filter(LibroVirtual.estado_virtual_id == estado_virtual_id)
    
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    # Aplicar paginación
    offset = (pagina - 1) * por_pagina
    query = query.offset(offset).limit(por_pagina)
    
    # Ejecutar query
    result = await db.execute(query)
    libros_virtuales = result.scalars().all()
    
    # Construir respuesta con nombres de relaciones
    libros_con_relaciones = []
    for libro in libros_virtuales:
        libro_dict = LibroVirtualConRelacionesResponse.model_validate(libro)
        libro_dict.editorial_nombre = libro.editorial.nombre
        libro_dict.area_conocimiento_nombre = libro.area_conocimiento.nombre
        libro_dict.estado_virtual_nombre = libro.estado_virtual.estado
        libro_dict.usuario_subio_nombre = libro.usuario_subio.nombre_completo
        libros_con_relaciones.append(libro_dict)
    
    return LibroVirtualListResponse(
        libros_virtuales=libros_con_relaciones,
        total=total,
        pagina=pagina,
        por_pagina=por_pagina
    )

@router.get("/{libro_virtual_id}", response_model=LibroVirtualConRelacionesResponse)
async def obtener_libro_virtual(
    libro_virtual_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """
    Obtener información de un libro virtual
    """
    from sqlalchemy.orm import selectinload
    
    # ✅ CORREGIDO: Usar selectinload como en libros
    result = await db.execute(
        select(LibroVirtual)
        .options(
            selectinload(LibroVirtual.editorial),
            selectinload(LibroVirtual.area_conocimiento),
            selectinload(LibroVirtual.estado_virtual),
            selectinload(LibroVirtual.usuario_subio)
        )
        .filter(LibroVirtual.id == libro_virtual_id)
    )
    libro_virtual = result.scalar_one_or_none()
    
    if not libro_virtual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro virtual no encontrado"
        )
    
    # Construir respuesta con nombres
    libro_response = LibroVirtualConRelacionesResponse.model_validate(libro_virtual)
    libro_response.editorial_nombre = libro_virtual.editorial.nombre
    libro_response.area_conocimiento_nombre = libro_virtual.area_conocimiento.nombre
    libro_response.estado_virtual_nombre = libro_virtual.estado_virtual.estado
    libro_response.usuario_subio_nombre = libro_virtual.usuario_subio.nombre_completo
    
    return libro_response

# =============================================
# ENDPOINTS DE GESTIÓN (Solo admin avanzado y super admin)
# =============================================

@router.post("/", response_model=LibroVirtualResponse)
async def crear_libro_virtual(
    libro_data: LibroVirtualCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Crear libro virtual (solo admin avanzado y super admin)
    """
    # Verificar que no exista ya el mismo archivo
    result = await db.execute(
        select(LibroVirtual).filter(LibroVirtual.archivo_digital == libro_data.archivo_digital)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un libro virtual con ese archivo digital"
        )
    
    # Verificar que las relaciones existan
    await verificar_relaciones_libro_virtual(db, libro_data.model_dump())
    
    # Crear libro virtual
    nuevo_libro_virtual = LibroVirtual(
        **libro_data.model_dump(),
        usuario_subio_id=usuario_actual.id
    )
    
    db.add(nuevo_libro_virtual)
    await db.commit()
    await db.refresh(nuevo_libro_virtual)
    
    return nuevo_libro_virtual

@router.put("/{libro_virtual_id}", response_model=LibroVirtualResponse)
async def actualizar_libro_virtual(
    libro_virtual_id: int,
    libro_data: LibroVirtualUpdate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Actualizar libro virtual (solo admin avanzado y super admin)
    """
    result = await db.execute(
        select(LibroVirtual).filter(LibroVirtual.id == libro_virtual_id)
    )
    libro_virtual = result.scalar_one_or_none()
    
    if not libro_virtual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro virtual no encontrado"
        )
    
    update_data = libro_data.model_dump(exclude_unset=True)
    
    # Verificar unicidad del archivo si se está actualizando
    if 'archivo_digital' in update_data:
        result = await db.execute(
            select(LibroVirtual).filter(
                LibroVirtual.archivo_digital == update_data['archivo_digital'],
                LibroVirtual.id != libro_virtual_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro libro virtual con ese archivo digital"
            )
    
    # Verificar relaciones si se están actualizando
    await verificar_relaciones_libro_virtual(db, update_data)
    
    # Actualizar fecha de cambio de estado si se cambia el estado
    if 'estado_virtual_id' in update_data:
        libro_virtual.fecha_ultimo_cambio_estado = datetime.utcnow()
    
    # Actualizar campos
    for field, value in update_data.items():
        setattr(libro_virtual, field, value)
    
    await db.commit()
    await db.refresh(libro_virtual)
    
    return libro_virtual

@router.delete("/{libro_virtual_id}")
async def eliminar_libro_virtual(
    libro_virtual_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Eliminar libro virtual (solo admin avanzado y super admin)
    """
    result = await db.execute(
        select(LibroVirtual).filter(LibroVirtual.id == libro_virtual_id)
    )
    libro_virtual = result.scalar_one_or_none()
    
    if not libro_virtual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro virtual no encontrado"
        )
    if libro_virtual.estado_virtual_id == 2:  # No disponible
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El libro virtual no esta disponible"
        )

    libro_virtual.estado_virtual_id = 2
    libro_virtual.fecha_cambio_estado = datetime.utcnow()
    await db.commit()
    
    return {"message": "Libro virtual eliminado exitosamente"}

@router.patch("/{libro_virtual_id}/reactivar", response_model=LibroVirtualResponse)
async def reactivar_libro_virtual(
    libro_virtual_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_recursos)
):
    """
    Reactivar libro virtual retirado - cambia estado a "Disponible" (1)
    """
    result = await db.execute(select(LibroVirtual).filter(LibroVirtual.id == libro_virtual_id))
    libroVitual = result.scalar_one_or_none()
    
    if not libroVitual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro virtual no encontrado"
        )
    
    if libroVitual.estado_virtual_id != 2:  # No está retirado
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El libro virtual no está retirado"
        )
     
    # Cambiar estado a "Disponible" (1)
    libroVitual.estado_virtual_id = 1
    libroVitual.fecha_cambio_estado = datetime.utcnow()
    
    await db.commit()
    await db.refresh(libroVitual)

    return libroVitual

# =============================================
# ENDPOINTS AUXILIARES
# =============================================

@router.get("/auxiliares/estados-virtual", response_model=List[EstadoVirtualResponse])
async def listar_estados_virtual(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """Listar todos los estados virtuales"""
    result = await db.execute(select(EstadoVirtual).order_by(EstadoVirtual.estado))
    estados = result.scalars().all()
    return estados

@router.get("/auxiliares/editoriales", response_model=List[EditorialResponse])
async def listar_editoriales(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """Listar todas las editoriales"""
    result = await db.execute(select(Editorial).order_by(Editorial.nombre))
    editoriales = result.scalars().all()
    return editoriales

@router.get("/auxiliares/areas-conocimiento", response_model=List[AreaConocimientoResponse])
async def listar_areas_conocimiento(
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_consultar)
):
    """Listar todas las áreas de conocimiento"""
    result = await db.execute(select(AreaConocimiento).order_by(AreaConocimiento.nombre))
    areas = result.scalars().all()
    return areas