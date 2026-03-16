
import MySQLdb
import os
import sys

# Configuración (Igual que en app.py)
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'passwd': os.environ.get('MYSQL_PASSWORD', ''),
    'port': int(os.environ.get('MYSQL_PORT', 3306)),
}

def execute_sql_file(cursor, filename):
    print(f"--- Ejecutando: {filename} ---")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        # Limpiar comentarios simples y manejar bloques SQL
        statements = sql_content.split(';')
        for statement in statements:
            clean_stmt = statement.strip()
            if clean_stmt:
                try:
                    cursor.execute(clean_stmt)
                except Exception as e:
                    # Ignorar errores menores en DROP TABLE si no existe
                    if "Drop table" not in clean_stmt:
                        print(f"Error en statement: {clean_stmt[:50]}... \nDetalle: {e}")
    except Exception as e:
        print(f"Error al leer/procesar {filename}: {e}")

def init_all():
    try:
        db = MySQLdb.connect(**DB_CONFIG)
        cursor = db.cursor()

        print("--- Preparando Base de Datos 'sistema_reina' ---")
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_reina;")
        cursor.execute("USE sistema_reina;")

        # 1. Esquema (Borrar y crear tablas)
        execute_sql_file(cursor, 'database.sql')
        
        # 2. Datos Maestros (Usuarios, Productos, etc.)
        if os.path.exists('seed_data.sql'):
            execute_sql_file(cursor, 'seed_data.sql')
        else:
            print("⚠️ Advertencia: seed_data.sql no encontrado.")

        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
        db.commit()
        cursor.close()
        db.close()
        print("\n¡Base de datos REINICIADA y DATOS RESTAURADOS con éxito! ✅")

    except Exception as e:
        print(f"\n❌ Error Crítico: {e}")

if __name__ == "__main__":
    init_all()
