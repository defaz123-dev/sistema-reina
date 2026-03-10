from app import app, mysql

def upgrade_db():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Alterar tabla ventas
        try:
            cur.execute("ALTER TABLE ventas ADD COLUMN intentos_envio INT DEFAULT 0;")
            cur.execute("ALTER TABLE ventas ADD COLUMN proximo_reintento DATETIME DEFAULT CURRENT_TIMESTAMP;")
            print("Tabla ventas actualizada.")
        except Exception as e:
            print("Error en ventas (posiblemente ya existen):", e)
            
        # Alterar tabla anulaciones_factura
        try:
            cur.execute("ALTER TABLE anulaciones_factura ADD COLUMN intentos_envio INT DEFAULT 0;")
            cur.execute("ALTER TABLE anulaciones_factura ADD COLUMN proximo_reintento DATETIME DEFAULT CURRENT_TIMESTAMP;")
            print("Tabla anulaciones_factura actualizada.")
        except Exception as e:
            print("Error en anulaciones_factura (posiblemente ya existen):", e)

        mysql.connection.commit()
        cur.close()
        print("Migración de contingencia SRI completada.")

if __name__ == "__main__":
    upgrade_db()
