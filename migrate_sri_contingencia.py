from app import app, mysql

def upgrade_db():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # --- TABLA ventas ---
        # intentos_envio
        try:
            cur.execute("ALTER TABLE ventas ADD COLUMN intentos_envio INT DEFAULT 0;")
            print("Columna 'intentos_envio' añadida a 'ventas'.")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("Columna 'intentos_envio' ya existe en 'ventas'.")
            else:
                print("Error al añadir 'intentos_envio' a 'ventas':", e)

        # proximo_reintento
        try:
            cur.execute("ALTER TABLE ventas ADD COLUMN proximo_reintento DATETIME DEFAULT CURRENT_TIMESTAMP;")
            print("Columna 'proximo_reintento' añadida a 'ventas'.")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("Columna 'proximo_reintento' ya existe en 'ventas'.")
            else:
                print("Error al añadir 'proximo_reintento' a 'ventas':", e)

        # --- TABLA anulaciones_factura ---
        # intentos_envio
        try:
            cur.execute("ALTER TABLE anulaciones_factura ADD COLUMN intentos_envio INT DEFAULT 0;")
            print("Columna 'intentos_envio' añadida a 'anulaciones_factura'.")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("Columna 'intentos_envio' ya existe en 'anulaciones_factura'.")
            else:
                print("Error al añadir 'intentos_envio' a 'anulaciones_factura':", e)

        # proximo_reintento
        try:
            cur.execute("ALTER TABLE anulaciones_factura ADD COLUMN proximo_reintento DATETIME DEFAULT CURRENT_TIMESTAMP;")
            print("Columna 'proximo_reintento' añadida a 'anulaciones_factura'.")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("Columna 'proximo_reintento' ya existe en 'anulaciones_factura'.")
            else:
                print("Error al añadir 'proximo_reintento' a 'anulaciones_factura':", e)

        mysql.connection.commit()
        cur.close()
        print("\nMigración de base de datos para SRI completada.")

if __name__ == "__main__":
    upgrade_db()
