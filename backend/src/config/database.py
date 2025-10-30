import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """
    Establece conexión con la base de datos PostgreSQL
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "library_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            port=os.getenv("DB_PORT", "5432")
        )
        return connection
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        raise

# Función de utilidad para ejecutar queries
def execute_query(query, params=None, fetch=False):
    """
    Ejecuta una query y opcionalmente retorna resultados
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
                return result
            connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()