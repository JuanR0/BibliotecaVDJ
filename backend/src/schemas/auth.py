from pydantic import BaseModel, Field, field_validator
from typing import Optional

class UsuarioLogin(BaseModel):
    """Esquema para login de usuario"""
    codigo_universitario: str = Field(..., min_length=1, max_length=20)
    clave_acceso: str = Field(..., min_length=1)

    @field_validator('codigo_universitario')
    @classmethod
    def codigo_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('El código universitario no puede estar vacío')
        return v.strip()

    @field_validator('clave_acceso')
    @classmethod
    def clave_no_vacia(cls, v: str) -> str:
        if not v:
            raise ValueError('La clave de acceso no puede estar vacía')
        return v

class Token(BaseModel):
    """Esquema para respuesta de token JWT"""
    access_token: str
    token_type: str
    user_type: str
    user_name: str
    user_id: int

class TokenData(BaseModel):
    """Esquema para datos dentro del token JWT"""
    codigo_universitario: Optional[str] = None
    user_id: Optional[int] = None
    tipo_usuario_id: Optional[int] = None