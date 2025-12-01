import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config.database import verify_connection, create_tables
from api.routes import auth, usuarios, libros, libros_virtuales, areas, equipos_computo, mobiliario, tesis, prestamos_libro, prestamos_area, prestamos_equipo_computo

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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # ← AGREGAR 5173
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
app.include_router(prestamos_libro.router)
app.include_router(prestamos_area.router)
app.include_router(prestamos_equipo_computo.router)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)