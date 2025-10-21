import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def test_postgresql_connection():
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        print(f"Testing connection to: {DATABASE_URL}")
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ PostgreSQL connected! Version: {version}")
            
            # Test if database exists and is accessible
            result = connection.execute(text("SELECT current_database();"))
            db_name = result.scalar()
            print(f"✅ Database accessible: {db_name}")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_postgresql_connection()