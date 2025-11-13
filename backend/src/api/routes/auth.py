from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from sqlalchemy import select

from config.database import get_db
from schemas import UsuarioLogin, Token, UsuarioResponse, UsuarioCreate  # ← Import desde schemas
from core import (  # ← Import desde core
    autenticar_usuario, 
    crear_token_acceso, 
    obtener_usuario_actual,
    obtener_hash_clave
)
from models import Usuario

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(usuario_data: UsuarioLogin, db: AsyncSession = Depends(get_db)):
    usuario = await autenticar_usuario(db, usuario_data.codigo_universitario, usuario_data.clave_acceso)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código universitario o clave incorrectos",
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = crear_token_acceso(
        data={
            "sub": usuario.codigo_universitario,
            "user_id": usuario.id,
            "tipo_usuario_id": usuario.tipo_usuario_id
        },
        expires_delta=access_token_expires
    )

    tipo_usuario_map = {
        1: "comun",
        2: "admin_basico", 
        3: "admin_avanzado",
        4: "super_admin"
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer", 
        "user_type": tipo_usuario_map.get(usuario.tipo_usuario_id, "comun"),
        "user_name": usuario.nombre_completo,
        "user_id": usuario.id
    }

@router.get("/me", response_model=UsuarioResponse)
async def get_current_user(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual

@router.post("/register", response_model=UsuarioResponse)
async def register_user(usuario_data: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Usuario).filter(
            Usuario.codigo_universitario == usuario_data.codigo_universitario
        )
    )
    usuario_existente = result.scalar_one_or_none()
    
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código universitario ya está registrado"
        )
    
    nuevo_usuario = Usuario(
        codigo_universitario=usuario_data.codigo_universitario,
        clave_acceso=obtener_hash_clave(usuario_data.clave_acceso),
        nombre_completo=usuario_data.nombre_completo,
        relacion_institucional_id=usuario_data.relacion_institucional_id,
        tipo_usuario_id=1,
        esta_activo=True
    )
    
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)
    
    return nuevo_usuario