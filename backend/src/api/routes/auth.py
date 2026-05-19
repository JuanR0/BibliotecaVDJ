from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from sqlalchemy import select
from pydantic import BaseModel, Field, field_validator
from typing import Optional

from config.database import get_db
from schemas.auth import UsuarioLogin, Token
from schemas.usuarios import UsuarioResponse, UsuarioRegister
from core.security import (
    autenticar_usuario,
    crear_token_acceso,
    obtener_usuario_actual,
    obtener_hash_clave,
    verificar_clave,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    obtener_permisos_frontend
)
from models import Usuario


# ── Schema cambiar contraseña ──────────────────────────────────────────────
class CambiarPasswordRequest(BaseModel):
    clave_actual:    str = Field(..., min_length=1)
    clave_nueva:     str = Field(..., min_length=8, max_length=100)
    clave_confirmar: str = Field(..., min_length=8, max_length=100)

    @field_validator('clave_nueva')
    @classmethod
    def no_puede_ser_temporal(cls, v):
        if v == 'biblioteca2025':
            raise ValueError('La nueva contraseña no puede ser la contraseña temporal')
        return v

    @field_validator('clave_confirmar')
    @classmethod
    def claves_coinciden(cls, v, info):
        if 'clave_nueva' in info.data and v != info.data['clave_nueva']:
            raise ValueError('Las contraseñas no coinciden')
        return v

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/login", response_model=Token)
async def login(usuario_data: UsuarioLogin, db: AsyncSession = Depends(get_db)):
    """
    Iniciar sesión en el sistema
    """
    usuario = await autenticar_usuario(db, usuario_data.codigo_universitario, usuario_data.clave_acceso)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código universitario o contraseña incorrectos",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_type=tipo_usuario_map.get(usuario.tipo_usuario_id, "comun"),
        user_name=usuario.nombre_completo,
        user_id=usuario.id
    )

@router.get("/me", response_model=UsuarioResponse)
async def get_current_user(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    """
    Obtener información del usuario actualmente autenticado
    """
    return usuario_actual

@router.get("/me/permisos")
async def get_user_permissions(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    """
    Obtener información de permisos para el frontend
    """
    return obtener_permisos_frontend(usuario_actual)

@router.post("/register", response_model=UsuarioResponse)
async def register_user(usuario_data: UsuarioRegister, db: AsyncSession = Depends(get_db)):
    """
    Registro público de usuarios (siempre crea usuarios tipo 'común')
    """
    # Verificar si el código universitario ya existe
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
    
    # Crear nuevo usuario (siempre tipo 1 = común)
    nuevo_usuario = Usuario(
        codigo_universitario=usuario_data.codigo_universitario,
        clave_acceso=obtener_hash_clave(usuario_data.clave_acceso),
        nombre_completo=usuario_data.nombre_completo,
        relacion_institucional_id=usuario_data.relacion_institucional_id,
        tipo_usuario_id=1,  # ✅ Siempre usuario común en registro público
        esta_activo=True
    )
    
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)
    
    return nuevo_usuario


# ══════════════════════════════════════════════════════════════════════════
# CAMBIAR CONTRASEÑA — el usuario cambia su propia contraseña
# ══════════════════════════════════════════════════════════════════════════

@router.patch("/cambiar-password")
async def cambiar_password(
    data: CambiarPasswordRequest,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    El usuario autenticado cambia su propia contraseña.
    Flujo esperado: SuperAdmin resetea a 'biblioteca2025' → usuario entra
    y la cambia aquí por una de su elección.

    Validaciones:
    - La contraseña actual debe ser correcta
    - La nueva no puede ser igual a la actual
    - La nueva no puede ser la contraseña temporal 'biblioteca2025'
    - La confirmación debe coincidir con la nueva (validado en schema)
    """
    # Verificar que la contraseña actual es correcta
    if not verificar_clave(data.clave_actual, usuario_actual.clave_acceso):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )

    # Evitar reusar la misma contraseña
    if verificar_clave(data.clave_nueva, usuario_actual.clave_acceso):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña no puede ser igual a la contraseña actual"
        )

    usuario_actual.clave_acceso = obtener_hash_clave(data.clave_nueva)
    await db.commit()

    return {"mensaje": "Contraseña actualizada correctamente"}