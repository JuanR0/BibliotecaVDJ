import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config.database import verify_connection, create_tables
from api.routes import auth, usuarios, libros, libros_virtuales, areas, equipos_computo, mobiliario, tesis


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sistema de Biblioteca VDJ",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080", "http://127.0.0.1:8080"],  # ← AGREGAR 5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],    
)

# Incluir routers
app.include_router(auth.router)
app.include_router(usuarios.router) 
app.include_router(libros.router)
app.include_router(libros_virtuales.router)  
app.include_router(areas.router)
app.include_router(equipos_computo.router)
app.include_router(mobiliario.router)
app.include_router(tesis.router)

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

@app.get("/api/health/db")
async def health_check_db():
    """
    Health check específico para la base de datos
    """
    try:
        # Usar la misma función que usas en startup
        db_connected = await verify_connection()
        
        if db_connected:
            return {
                "status": "healthy",
                "database": "connected",
                "message": "Conexión a la base de datos establecida correctamente",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "unhealthy", 
                "database": "disconnected",
                "message": "No se pudo conectar a la base de datos",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            "status": "error",
            "database": "error",
            "message": f"Error verificando la base de datos: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)