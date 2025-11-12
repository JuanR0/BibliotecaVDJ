import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
from datetime import timedelta

from config.database import get_db, verify_connection, create_tables
from models import Usuario

from schemas.auth import UsuarioLogin, Token
from schemas.users import UsuarioResponse, UsuarioCreate, UsuarioRegister    
from auth import (
    autenticar_usuario, 
    crear_token_acceso, 
    obtener_usuario_actual,
    obtener_hash_clave,
    requerir_admin   
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
    if verify_connection():
        create_tables()
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
async def test_db(db: Session = Depends(get_db)):
    from sqlalchemy import text
    try:
        result = db.execute(text("SELECT 1"))
        return {"database": "connected", "test": "success"}
    except Exception as e:
        return {"database": "disconnected", "error": str(e)}

# Endpoints de autenticación
@app.post("/api/auth/login", response_model=Token)
async def login(usuario_data: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = autenticar_usuario(db, usuario_data.codigo_universitario, usuario_data.clave_acceso)
    
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

     # ✅ Mapeo de tipos de usuario
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
        "user_type": tipo_usuario_map.get(usuario.tipo_usuario_id, "comun"),  # ✅ CORREGIDO
        "user_name": usuario.nombre_completo,
        "user_id": usuario.id
    }

# TEMPORAL - Para pruebas, eliminar después
@app.get("/api/auth/test-me")
async def test_current_user(db: Session = Depends(get_db)):
    """Endpoint temporal para probar sin token"""
    # Buscar el usuario que acabas de crear
    usuario = db.query(Usuario).filter(Usuario.codigo_universitario == "20240001").first()
    if usuario:
        return {
            "id": usuario.id,
            "codigo_universitario": usuario.codigo_universitario,
            "nombre_completo": usuario.nombre_completo,
            "relacion_institucional_id": usuario.relacion_institucional_id,
            "tipo_usuario_id": usuario.tipo_usuario_id,
            "esta_activo": usuario.esta_activo,
            "fecha_registro": usuario.fecha_registro
        }
    else:
        return {"error": "Usuario no encontrado"}

@app.get("/api/auth/debug-me")
async def debug_current_user(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    """Endpoint de debug con autenticación real"""
    return {
        "message": "✅ Autenticación exitosa!",
        "usuario": {
            "id": usuario_actual.id,
            "codigo_universitario": usuario_actual.codigo_universitario,
            "nombre_completo": usuario_actual.nombre_completo,
            "tipo_usuario": usuario_actual.tipo_usuario_id
        }
    }

@app.get("/api/auth/me", response_model=UsuarioResponse)
async def get_current_user(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual

@app.post("/api/auth/register", response_model=UsuarioResponse)
async def register_user(usuario_data: UsuarioRegister, db: Session = Depends(get_db)):
    try:
        logger.info(f"Intentando registrar usuario: {usuario_data.codigo_universitario}")
        
        usuario_existente = db.query(Usuario).filter(
            Usuario.codigo_universitario == usuario_data.codigo_universitario
        ).first()
        
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código universitario ya está registrado"
            )
        
        # Log para debug
        logger.info(f"Creando usuario con relacion_institucional_id: {usuario_data.relacion_institucional_id}")
        
        nuevo_usuario = Usuario(
            codigo_universitario=usuario_data.codigo_universitario,
            clave_acceso=obtener_hash_clave(usuario_data.clave_acceso),
            nombre_completo=usuario_data.nombre_completo,
            relacion_institucional_id=usuario_data.relacion_institucional_id,
            tipo_usuario_id=1,  # Siempre usuario común por defecto
            esta_activo=True
        )
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        logger.info(f"✅ Usuario creado exitosamente: {nuevo_usuario.codigo_universitario}")
        return nuevo_usuario
        
    except Exception as e:
        logger.error(f"❌ Error en registro: {str(e)}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        db.rollback()  # Importante: hacer rollback en caso de error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.post("/api/admin/usuarios", response_model=UsuarioResponse)
async def crear_usuario_admin(
    usuario_data: UsuarioCreate, 
    db: Session = Depends(get_db),
    admin_actual: Usuario = Depends(requerir_admin)  # ← Solo admins pueden usar este endpoint
):
    try:
        logger.info(f"Intentando registrar usuario: {usuario_data.codigo_universitario}")
        """Crear usuario con cualquier rol (solo administradores)"""
        usuario_existente = db.query(Usuario).filter(
            Usuario.codigo_universitario == usuario_data.codigo_universitario
        ).first()
        
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
            tipo_usuario_id=usuario_data.tipo_usuario_id,  # ✅ Respeta el tipo enviado
            usuario_creador_id=admin_actual.id,  # ✅ Registra quién creó el usuario
            esta_activo=True
        )
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
    
        logger.info(f"✅ Usuario creado por admin {admin_actual.codigo_universitario}: {nuevo_usuario.codigo_universitario} (tipo: {nuevo_usuario.tipo_usuario_id})")
        return nuevo_usuario

    except Exception as e:
        logger.error(f"❌ Error en registro: {str(e)}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        db.rollback()  # Importante: hacer rollback en caso de error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)