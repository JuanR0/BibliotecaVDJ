from database import get_db_connection

def test_connection():
    """Prueba básica de conexión a la base de datos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Probamos una consulta simple
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print("✅ Conexión exitosa a PostgreSQL")
        print(f"📊 Versión de PostgreSQL: {db_version[0]}")
        
        # Probamos consultar usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios;")
        user_count = cursor.fetchone()[0]
        print(f"👥 Usuarios en la base de datos: {user_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_connection()