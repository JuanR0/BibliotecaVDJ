from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from config.database import get_db
from schemas.usuarios import (
    UsuarioCreateAdmin, 
    UsuarioResponse, 
    UsuarioUpdate,
    UsuarioListResponse,
    UsuarioStatusChange,
    UsuarioDetailResponse
)
from core.security import (
    obtener_usuario_actual, 
    requerir_puede_gestionar_usuarios,
    obtener_hash_clave
)
from models import Usuario, RelacionInstitucional, TipoUsuario

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])

@router.get("/", response_model=UsuarioListResponse)
async def listar_usuarios(
    pagina: int = Query(1, ge=1, description="Página actual"),
    por_pagina: int = Query(10, ge=1, le=100, description="Elementos por página"),
    activos_only: bool = Query(True, description="Solo usuarios activos"),
    codigo_filter: Optional[str] = Query(None, description="Filtrar por código universitario"),
    nombre_filter: Optional[str] = Query(None, description="Filtrar por nombre"),
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_usuarios)
):
    """
    Listar todos los usuarios (solo super admin)
    """
    # Construir query base
    query = select(Usuario)
    
    # Aplicar filtros
    if activos_only:
        query = query.filter(Usuario.esta_activo == True)
    
    if codigo_filter:
        query = query.filter(Usuario.codigo_universitario.ilike(f"%{codigo_filter}%"))
    
    if nombre_filter:
        query = query.filter(Usuario.nombre_completo.ilike(f"%{nombre_filter}%"))
    
    # Contar total
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    # Aplicar paginación
    offset = (pagina - 1) * por_pagina
    query = query.offset(offset).limit(por_pagina)
    
    # Ejecutar query
    result = await db.execute(query)
    usuarios = result.scalars().all()
    
    return UsuarioListResponse(
        usuarios=usuarios,
        total=total,
        pagina=pagina,
        por_pagina=por_pagina
    )

@router.get("/{usuario_id}", response_model=UsuarioDetailResponse)
async def obtener_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_usuarios)
):
    """
    Obtener información detallada de un usuario (solo super admin)
    """
    result = await db.execute(
        select(Usuario).filter(Usuario.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return usuario

@router.post("/", response_model=UsuarioResponse)
async def crear_usuario_admin(
    usuario_data: UsuarioCreateAdmin,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_usuarios)
):
    """
    Crear nuevo usuario (solo super admin)
    Permite especificar el tipo de usuario
    """
    # Verificar que el código universitario no exista
    result = await db.execute(
        select(Usuario).filter(Usuario.codigo_universitario == usuario_data.codigo_universitario)
    )
    usuario_existente = result.scalar_one_or_none()
    
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código universitario ya está registrado"
        )
    
    # Verificar que el tipo de usuario sea válido (1-4)
    if usuario_data.tipo_usuario_id not in [1, 2, 3, 4]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de usuario inválido"
        )
    
    # Crear nuevo usuario
    nuevo_usuario = Usuario(
        codigo_universitario=usuario_data.codigo_universitario,
        clave_acceso=obtener_hash_clave(usuario_data.clave_acceso),
        nombre_completo=usuario_data.nombre_completo,
        relacion_institucional_id=usuario_data.relacion_institucional_id,
        tipo_usuario_id=usuario_data.tipo_usuario_id,
        usuario_creador_id=usuario_actual.id,  # El admin que crea el usuario
        esta_activo=True
    )
    
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)
    
    return nuevo_usuario

@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_usuarios)
):
    """
    Actualizar información de usuario (solo super admin)
    """
    result = await db.execute(
        select(Usuario).filter(Usuario.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No permitir auto-desactivación
    if usuario.id == usuario_actual.id and usuario_data.esta_activo is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta"
        )
    
    # Actualizar campos proporcionados
    update_data = usuario_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "esta_activo" and value != usuario.esta_activo:
            # Actualizar fecha de cambio de estado
            usuario.fecha_ultimo_cambio_estado = datetime.utcnow()
        setattr(usuario, field, value)
    
    await db.commit()
    await db.refresh(usuario)
    
    return usuario

@router.patch("/{usuario_id}/estado", response_model=UsuarioResponse)
async def cambiar_estado_usuario(
    usuario_id: int,
    estado_data: UsuarioStatusChange,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_usuarios)
):
    """
    Activar/desactivar usuario (solo super admin)
    """
    # No permitir auto-desactivación
    if usuario_id == usuario_actual.id and not estado_data.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta"
        )
    
    result = await db.execute(
        select(Usuario).filter(Usuario.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Solo actualizar si el estado cambió
    if usuario.esta_activo != estado_data.esta_activo:
        usuario.esta_activo = estado_data.esta_activo
        usuario.fecha_ultimo_cambio_estado = datetime.utcnow()
        
        await db.commit()
        await db.refresh(usuario)
    
    return usuario

@router.delete("/{usuario_id}")
async def eliminar_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_puede_gestionar_usuarios)
):
    """
    Eliminar usuario (solo super admin)
    En realidad desactiva el usuario por seguridad
    """
    # No permitir auto-eliminación
    if usuario_id == usuario_actual.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta"
        )
    
    result = await db.execute(
        select(Usuario).filter(Usuario.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # En lugar de eliminar, desactivamos (DELETE lógico)
    usuario.esta_activo = False
    usuario.fecha_ultimo_cambio_estado = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Usuario desactivado exitosamente"}