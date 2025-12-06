import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Construir DATABASE_URL async
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "BibliotecaVDJ")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "josue326")
DB_PORT = os.getenv("DB_PORT", "5432")

# ✅ CAMBIO: postgresql+asyncpg en lugar de postgresql
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

logger.info(f"🔗 Configurando conexión ASINCRONA a PostgreSQL...")

# Crear engine async
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # ✅ Útil para debug durante migración
    future=True,
    pool_size=10,
    max_overflow=20,
)

# Session async
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()

# Dependencia async
async def get_db():
    """
    Dependencia async para obtener sesión de base de datos.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error de base de datos: {e}")
            raise
        finally:
            await session.close()

# Funciones async para verificación
async def verify_connection():
    """
    Verificar conexión manualmente - async
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("✅ Conexión ASINCRONA a PostgreSQL establecida correctamente")
            return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Error conectando a PostgreSQL: {e}")
        return False

async def create_tables():
    """
    Crear tablas async
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Tablas creadas/verificadas correctamente")
    except SQLAlchemyError as e:
        logger.error(f"❌ Error creando tablas: {e}")
        raise