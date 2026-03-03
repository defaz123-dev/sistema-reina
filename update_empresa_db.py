# update_empresa_db.py
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
        print("Creando tabla 'empresa' para configuración SRI...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS empresa (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ruc VARCHAR(13) NOT NULL,
            razon_social VARCHAR(255) NOT NULL,
            nombre_comercial VARCHAR(255),
            direccion_matriz VARCHAR(255) NOT NULL,
            obligado_contabilidad VARCHAR(2) DEFAULT 'NO',
            ambiente INT DEFAULT 1 -- 1: Pruebas, 2: Producción
        )
        """)
        
        # Insertar registro por defecto si está vacía
        cursor.execute("SELECT COUNT(*) FROM empresa")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            INSERT INTO empresa (ruc, razon_social, nombre_comercial, direccion_matriz, obligado_contabilidad, ambiente) 
            VALUES ('1790000000001', 'EMPRESA DE PRUEBA S.A.', 'SANDUCHES LA REINA', 'Av. Principal y Secundaria', 'SI', 1)
            """)
            
        db.commit()
        print("✅ Tabla empresa creada e inicializada.")
        
        # Añadir clave de acceso y estado SRI a ventas
        print("Añadiendo campos SRI a ventas...")
        try:
            cursor.execute("ALTER TABLE ventas ADD COLUMN clave_acceso_sri VARCHAR(49) AFTER total")
            cursor.execute("ALTER TABLE ventas ADD COLUMN estado_sri VARCHAR(50) DEFAULT 'CREADA' AFTER clave_acceso_sri")
            db.commit()
            print("✅ Campos SRI añadidos a ventas.")
        except:
            print("✅ Campos SRI ya existían en ventas.")
            
        cursor.close()
        db.close()
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update()
