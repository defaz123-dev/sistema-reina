from app import app, mysql

def register_new_menus():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # 1. Verificar si ya existen para no duplicar
        cur.execute("SELECT id FROM menus WHERE url = 'listar_anulaciones'")
        if not cur.fetchone():
            print("Registrando menú de Anulaciones...")
            cur.execute("INSERT INTO menus (nombre, url, icono, categoria, orden) VALUES (%s, %s, %s, %s, %s)", 
                        ('Anulaciones', 'listar_anulaciones', 'fas fa-file-invoice', 'OPERATIVO', 17))
            id_anula = cur.lastrowid
            cur.execute("INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, %s)", (id_anula,))
        
        cur.execute("SELECT id FROM menus WHERE url = 'kardex_movimientos'")
        if not cur.fetchone():
            print("Registrando menú de Kardex...")
            cur.execute("INSERT INTO menus (nombre, url, icono, categoria, orden) VALUES (%s, %s, %s, %s, %s)", 
                        ('Kardex', 'kardex_movimientos', 'fas fa-clipboard-list', 'ADMINISTRATIVO', 18))
            id_kardex = cur.lastrowid
            cur.execute("INSERT INTO rol_menus (rol_id, menu_id) VALUES (1, %s)", (id_kardex,))
            
        mysql.connection.commit()
        cur.close()
        print("Menús actualizados con éxito.")

if __name__ == "__main__":
    register_new_menus()
