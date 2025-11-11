import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging
from dotenv import load_dotenv

load_dotenv()  # ✅ Cargar variables de entorno

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Construir DATABASE_URL desde variables de entorno
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "bibliotecavdj")  # ← Tu base de datos
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Jalisco2025.")  # ← Tu password
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

logger.info(f"🔗 Configurando conexión a PostgreSQL...")

# Crear engine SIN verificar conexión inmediatamente
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verifica conexión antes de usar
    echo=False,
    future=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

Base = declarative_base()

def get_db():
    """
    Dependencia para obtener sesión de base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_connection():
    """
    Verificar conexión manualmente - se llama en startup
    """
    try:
        with engine.connect() as conn:
            logger.info("✅ Conexión a PostgreSQL establecida correctamente")
            return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Error conectando a PostgreSQL: {e}")
        logger.error("💡 Verifica que:")
        logger.error("   - PostgreSQL esté ejecutándose")
        logger.error("   - Las credenciales en .env sean correctas") 
        logger.error("   - La base de datos 'bibliotecavdj' exista")
        return False

def create_tables():
    """
    Crear tablas solo si la conexión es exitosa
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas/verificadas correctamente")
    except SQLAlchemyError as e:
        logger.error(f"❌ Error creando tablas: {e}")
        raise