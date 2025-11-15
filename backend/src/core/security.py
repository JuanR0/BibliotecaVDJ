from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request  
##from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# ✅ Configurar logger
logger = logging.getLogger(__name__)

# Importaciones de tus módulos
from config.database import get_db
from models import Usuario

# Configuración de JWT
SECRET_KEY = os.getenv("SECRET_KEY", "clave_por_defecto_muy_insegura_cambiar")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Verificar que tenemos una SECRET_KEY segura
if SECRET_KEY == "clave_por_defecto_muy_insegura_cambiar":
    logger.warning("⚠️  ADVERTENCIA: Usando SECRET_KEY por defecto. Esto es INSECURO para producción.")

# Configuración de bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 para FastAPI
from fastapi.security import HTTPBearer

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request):
        credentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, 
                    detail="Esquema de autenticación inválido"
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=403, 
                detail="Token de autorización inválido"
            )

# Usar este esquema
oauth2_scheme = JWTBearer()

# =============================================
# FUNCIONES BÁSICAS DE SEGURIDAD
# =============================================

def obtener_hash_clave(clave: str) -> str:
    """Genera un hash bcrypt para una clave."""
    return pwd_context.hash(clave)

def verificar_clave(clave_plana: str, clave_hash: str) -> bool:
    """Verifica si una clave plana coincide con un hash bcrypt."""
    return pwd_context.verify(clave_plana, clave_hash)

def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT de acceso."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verificar_token(token: str) -> Optional[dict]:
    """Verifica y decodifica un token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# =============================================
# AUTENTICACIÓN DE USUARIOS
# =============================================

async def autenticar_usuario(
    db: AsyncSession,
    codigo_universitario: str, 
    clave_acceso: str
) -> Optional[Usuario]:
    """
    Autentica un usuario con código universitario y clave.
    """
    result = await db.execute(
        select(Usuario).filter(
            Usuario.codigo_universitario == codigo_universitario,
            Usuario.esta_activo == True
        )
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        return None
    
    if not verificar_clave(clave_acceso, usuario.clave_acceso):
        return None
    
    return usuario

async def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> Usuario:
    """
    Dependencia de FastAPI para obtener el usuario actual desde el token JWT.
    """
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verificar token
        payload = verificar_token(token)
        if payload is None:
            raise credenciales_exception
        
        # Obtener datos del token
        codigo_universitario: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if codigo_universitario is None:
            raise credenciales_exception
        
        # Consulta corregida
        result = await db.execute(
            select(Usuario).filter(
                Usuario.codigo_universitario == codigo_universitario,
                Usuario.esta_activo == True
            )
        )
        usuario = result.scalar_one_or_none()
        
        if usuario is None:
            raise credenciales_exception
        
        # Verificar que el user_id coincide (seguridad adicional)
        if user_id and usuario.id != user_id:
            raise credenciales_exception
            
        return usuario
        
    except JWTError as e:
        logger.error(f"Error JWT: {e}")
        raise credenciales_exception

async def obtener_usuario_actual_optcional(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[Usuario]:
    """
    Dependencia opcional para obtener usuario actual.
    Devuelve None si no hay token válido en lugar de error.
    """
    if not token:
        return None
    
    try:
        return await obtener_usuario_actual(token, db)
    except HTTPException:
        return None

# =============================================
# SISTEMA SIMPLIFICADO DE PERMISOS
# =============================================

def puede_consultar(usuario: Usuario) -> bool:
    """
    Usuario común puede consultar recursos.
    Todos los usuarios activos pueden consultar.
    """
    return usuario.esta_activo

def puede_prestar(usuario: Usuario) -> bool:
    """
    Admin básico, avanzado y super admin pueden prestar.
    Tipo 2, 3, 4 pueden prestar.
    """
    return usuario.esta_activo and usuario.tipo_usuario_id >= 2

def puede_gestionar_recursos(usuario: Usuario) -> bool:
    """
    Admin avanzado y super admin pueden gestionar recursos.
    Tipo 3, 4 pueden crear/editar/eliminar recursos.
    """
    return usuario.esta_activo and usuario.tipo_usuario_id >= 3

def puede_gestionar_usuarios(usuario: Usuario) -> bool:
    """
    Solo super admin puede gestionar usuarios.
    Solo tipo 4 puede gestionar usuarios.
    """
    return usuario.esta_activo and usuario.tipo_usuario_id == 4

# =============================================
# DEPENDENCIAS DE PERMISOS PARA FASTAPI
# =============================================

def requerir_usuario_activo(usuario_actual: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    """Dependencia básica - requiere usuario activo"""
    if not usuario_actual.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return usuario_actual

def requerir_puede_consultar(usuario_actual: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    """Cualquier usuario activo puede consultar"""
    if not puede_consultar(usuario_actual):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar consultas"
        )
    return usuario_actual

def requerir_puede_prestar(usuario_actual: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    """Solo admins pueden prestar (tipos 2, 3, 4)"""
    if not puede_prestar(usuario_actual):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar préstamos"
        )
    return usuario_actual

def requerir_puede_gestionar_recursos(usuario_actual: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    """Solo admin avanzado y super admin (tipos 3, 4)"""
    if not puede_gestionar_recursos(usuario_actual):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para gestionar recursos"
        )
    return usuario_actual

def requerir_puede_gestionar_usuarios(usuario_actual: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    """Solo super admin (tipo 4)"""
    if not puede_gestionar_usuarios(usuario_actual):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para gestionar usuarios"
        )
    return usuario_actual

# =============================================
# FUNCIONES PARA EL FRONTEND
# =============================================

def obtener_permisos_frontend(usuario: Usuario) -> dict:
    """
    Información que el frontend NECESITA para mostrar/ocultar elementos.
    El frontend llama a /api/auth/me/permisos para obtener esto.
    """
    return {
        # Información básica
        "usuario_id": usuario.id,
        "nombre": usuario.nombre_completo,
        "codigo_universitario": usuario.codigo_universitario,
        "tipo_usuario_id": usuario.tipo_usuario_id,
        "tipo_usuario_nombre": {
            1: "Usuario Común",
            2: "Admin Básico", 
            3: "Admin Avanzado",
            4: "Super Admin"
        }.get(usuario.tipo_usuario_id, "Desconocido"),
        
        # Permisos específicos (para mostrar/ocultar botones)
        "puede_consultar": puede_consultar(usuario),
        "puede_prestar": puede_prestar(usuario),
        "puede_gestionar_recursos": puede_gestionar_recursos(usuario),
        "puede_gestionar_usuarios": puede_gestionar_usuarios(usuario),
        
        # Atajos útiles para el frontend
        "es_usuario_comun": usuario.tipo_usuario_id == 1,
        "es_admin_basico": usuario.tipo_usuario_id == 2,
        "es_admin_avanzado": usuario.tipo_usuario_id == 3,
        "es_super_admin": usuario.tipo_usuario_id == 4,
        "es_cualquier_admin": usuario.tipo_usuario_id >= 2,
    }