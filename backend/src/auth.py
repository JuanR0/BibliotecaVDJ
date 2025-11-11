from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
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
    print("⚠️  ADVERTENCIA: Usando SECRET_KEY por defecto. Esto es INSECURO para producción.")

# Configuración de bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 para FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def obtener_hash_clave(clave: str) -> str:
    """
    Genera un hash bcrypt para una clave.
    Versión compatible con bcrypt 4.0+
    """
    # La validación de longitud ya se hizo en el schema
    # Si llegamos aquí, la contraseña es válida
    return pwd_context.hash(clave)

def verificar_clave(clave_plana: str, clave_hash: str) -> bool:
    """Verifica si una clave plana coincide con un hash bcrypt."""
    return pwd_context.verify(clave_plana, clave_hash)

def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verificar_token(token: str) -> Optional[dict]:
    """
    Verifica y decodifica un token JWT.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
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
        
        if codigo_universitario is None or user_id is None:
            raise credenciales_exception
        
        # Buscar usuario en la base de datos
        usuario = db.query(Usuario).filter(
            Usuario.codigo_universitario == codigo_universitario,
            Usuario.id == user_id,
            Usuario.esta_activo == True
        ).first()
        
        if usuario is None:
            raise credenciales_exception
        
        return usuario
        
    except JWTError:
        raise credenciales_exception

async def obtener_usuario_actual_optcional(
    db: Session = Depends(get_db),
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

def requerir_admin(usuario_actual: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    """
    Dependencia para requerir permisos de administrador.
    """
    if usuario_actual.tipo_usuario_id not in [2, 3, 4]:  # 2=Admin, 3=SuperAdmin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return usuario_actual

def requerir_super_admin(usuario_actual: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    """
    Dependencia para requerir permisos de super administrador.
    """
    if usuario_actual.tipo_usuario_id != 4:  # 4=SuperAdmin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de super administrador"
        )
    return usuario_actual

def autenticar_usuario(
    db: Session, 
    codigo_universitario: str, 
    clave_acceso: str
) -> Optional[Usuario]:
    """
    Autentica un usuario con código universitario y clave.
    """
    usuario = db.query(Usuario).filter(
        Usuario.codigo_universitario == codigo_universitario,
        Usuario.esta_activo == True
    ).first()
    
    if not usuario:
        return None
    
    if not verificar_clave(clave_acceso, usuario.clave_acceso):
        return None
    
    return usuario