import MySQLdb

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',
    'db': 'sistema_reina'
}

def insert_menus():
    try:
        db = MySQLdb.connect(**DB_CONFIG)
        cursor = db.cursor()

        # Check and insert Anulaciones
        cursor.execute("SELECT id FROM menus WHERE url = 'listar_anulaciones'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO menus (id, nombre, url, icono, categoria, orden) 
                VALUES (17, 'Anulaciones', 'listar_anulaciones', 'fas fa-ban', 'OPERATIVO', 17)
            """)
            print("Menu 'Anulaciones' inserted.")
        
        # Check and insert Kardex
        cursor.execute("SELECT id FROM menus WHERE url = 'kardex_movimientos'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO menus (id, nombre, url, icono, categoria, orden) 
                VALUES (18, 'Kardex', 'kardex_movimientos', 'fas fa-exchange-alt', 'ADMINISTRATIVO', 18)
            """)
            print("Menu 'Kardex' inserted.")

        # Assign to Admin (rol_id = 1)
        # Check and assign Anulaciones (menu_id = 17)
        cursor.execute("SELECT id FROM rol_menus WHERE rol_id = 1 AND menu_id = 17")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 17)")
            print("Menu 'Anulaciones' assigned to Admin.")

        # Check and assign Kardex (menu_id = 18)
        cursor.execute("SELECT id FROM rol_menus WHERE rol_id = 1 AND menu_id = 18")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, 18)")
            print("Menu 'Kardex' assigned to Admin.")

        db.commit()
        print("Done successfully.")
        db.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    insert_menus()