# init_db.py
import MySQLdb
import sys

# Configuración (Igual que en app.py)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '', # Pon tu contraseña si la cambiaste
}

def run_sql_file(filename):
    try:
        # Conexión inicial al servidor (sin especificar DB)
        db = MySQLdb.connect(**DB_CONFIG)
        cursor = db.cursor()

        print(f"--- Ejecutando script: {filename} ---")
        
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Limpiar y unir comandos SQL
        full_sql = ""
        for line in lines:
            if not line.strip().startswith('--'):
                full_sql += line

        commands = full_sql.split(';')
        
        for cmd in commands:
            sql = cmd.strip()
            if sql:
                try:
                    cursor.execute(sql)
                    print(f"✅ OK: {sql[:40]}...")
                except Exception as e:
                    print(f"⚠️ Error en: {sql[:40]}... -> {str(e)}")
        
        db.commit()
        cursor.close()
        db.close()
        print("\n¡Base de datos REINA lista! ✅")

    except Exception as e:
        print(f"\n❌ Error de conexión: {str(e)}")

if __name__ == "__main__":
    run_sql_file('database.sql')
