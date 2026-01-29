"""
Script para configurar la base de datos en CasaOS
Ejecutar: python setup_database.py
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

# Configuración de CasaOS
DB_HOST = "192.168.100.12"
DB_PORT = "5432"
DB_USER = "casaos"
DB_PASSWORD = "casaos"
DB_NAME = "banco_pichincha"
INITIAL_DB = "casaos"  # Base de datos para conectar inicialmente

def test_connection():
    """Prueba la conexión a PostgreSQL"""
    print(f"\n🔄 Probando conexión a {DB_HOST}:{DB_PORT}...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=10
        )
        conn.close()
        print("✅ Conexión exitosa!")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("\n⚠️  Posibles soluciones:")
        print("   1. Verifica que PostgreSQL esté corriendo en CasaOS")
        print("   2. Verifica que el puerto 5432 esté expuesto en el contenedor")
        print("   3. Verifica que la IP sea correcta (192.168.100.12)")
        print("   4. Revisa la contraseña en CasaOS")
        return False

def create_database():
    """Crea la base de datos si no existe"""
    print(f"\n🔄 Creando base de datos '{DB_NAME}'...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=INITIAL_DB
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Verificar si existe
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(f'CREATE DATABASE {DB_NAME}')
            print(f"✅ Base de datos '{DB_NAME}' creada!")
        else:
            print(f"ℹ️  Base de datos '{DB_NAME}' ya existe")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_schema():
    """Ejecuta el schema.sql"""
    schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
    
    if not os.path.exists(schema_path):
        print(f"❌ No se encontró: {schema_path}")
        return False
    
    print(f"\n🔄 Ejecutando schema.sql...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cur = conn.cursor()
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Schema ejecutado correctamente!")
        return True
    except Exception as e:
        print(f"❌ Error ejecutando schema: {e}")
        return False

def main():
    print("=" * 50)
    print("  BANCO PICHINCHA - Configuración de Base de Datos")
    print("=" * 50)
    
    if not test_connection():
        sys.exit(1)
    
    if not create_database():
        sys.exit(1)
    
    if not run_schema():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("  ✅ BASE DE DATOS CONFIGURADA CORRECTAMENTE")
    print("=" * 50)
    print("\n  Ahora puedes ejecutar: iniciar.bat")
    print()

if __name__ == '__main__':
    main()
