import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession  # ✅ Import AsyncSession
from sqlalchemy import select  # ✅ IMPORTAR SELECT
import logging
from datetime import timedelta

from config.database import get_db, verify_connection, create_tables
from models import Usuario

from schemas.auth import UsuarioLogin, Token
from schemas.users import UsuarioResponse, UsuarioCreate
from auth import (
    autenticar_usuario, 
    crear_token_acceso, 
    obtener_usuario_actual,
    obtener_hash_clave
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sistema de Biblioteca VDJ")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Iniciando aplicación Biblioteca VDJ...")
    if await verify_connection():
        await create_tables()
        logger.info("✅ Aplicación iniciada correctamente")
    else:
        logger.warning("⚠️  Aplicación iniciada SIN conexión a base de datos")

@app.get("/")
async def root():
    return {"message": "🚀 Biblioteca VDJ API funcionando!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "biblioteca-vdj-api"}

@app.get("/api/test-db")
async def test_db(db: AsyncSession = Depends(get_db)):  # ✅ AsyncSession
    from sqlalchemy import text
    try:
        result = await db.execute(text("SELECT 1"))
        return {"database": "connected", "test": "success"}
    except Exception as e:
        return {"database": "disconnected", "error": str(e)}

# Endpoints de autenticación
@app.post("/api/auth/login", response_model=Token)
async def login(usuario_data: UsuarioLogin, db: AsyncSession = Depends(get_db)):  # ✅ AsyncSession
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
    
    logger.info(f"✅ Login exitoso: {usuario.codigo_universitario}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer", 
        "user_type": tipo_usuario_map.get(usuario.tipo_usuario_id, "comun"),
        "user_name": usuario.nombre_completo,
        "user_id": usuario.id
    }

@app.get("/api/auth/me", response_model=UsuarioResponse)
async def get_current_user(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual

@app.post("/api/auth/register", response_model=UsuarioResponse)
async def register_user(usuario_data: UsuarioCreate, db: AsyncSession = Depends(get_db)):  # ✅ AsyncSession
    # ✅ CORREGIDO: Usar select en lugar de query
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
    await db.commit()  # ✅ CORREGIDO: await commit
    await db.refresh(nuevo_usuario)  # ✅ CORREGIDO: await refresh
    
    logger.info(f"✅ Usuario creado: {nuevo_usuario.codigo_universitario}")
    return nuevo_usuario

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)