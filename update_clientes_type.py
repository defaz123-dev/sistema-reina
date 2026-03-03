# update_clientes_type.py
import MySQLdb

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',
    'db': 'sistema_reina'
}

def update():
    try:
        db = MySQLdb.connect(**DB_CONFIG)
        cursor = db.cursor()
        print("Añadiendo columna 'tipo_documento' a clientes...")
        try:
            cursor.execute("ALTER TABLE clientes ADD COLUMN tipo_documento ENUM('CEDULA', 'RUC') AFTER cedula_ruc")
            cursor.execute("UPDATE clientes SET tipo_documento = 'CEDULA' WHERE LENGTH(cedula_ruc) = 10")
            cursor.execute("UPDATE clientes SET tipo_documento = 'RUC' WHERE LENGTH(cedula_ruc) = 13")
            db.commit()
            print("✅ Columna añadida y datos actualizados.")
        except:
            print("✅ La columna ya existía.")
        cursor.close()
        db.close()
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update()
