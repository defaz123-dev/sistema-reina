import MySQLdb
import os

def setup_rbac():
    try:
        conn = MySQLdb.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            passwd=os.environ.get('MYSQL_PASSWORD', ''),
            db=os.environ.get('MYSQL_DB', 'sistema_reina')
        )
        cur = conn.cursor()
        
        # 1. Crear tabla de Menús
        cur.execute("""
            CREATE TABLE IF NOT EXISTS menus (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                url VARCHAR(100) NOT NULL,
                icono VARCHAR(50),
                categoria VARCHAR(50), -- Operativo, Abastecimiento, Administrativo, etc.
                orden INT DEFAULT 0
            )
        """)
        
        # 2. Crear tabla de Permisos (Rol - Menú)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rol_menus (
                id INT AUTO_INCREMENT PRIMARY KEY,
                rol_id INT,
                menu_id INT,
                FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
                FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE,
                UNIQUE KEY unique_rol_menu (rol_id, menu_id)
            )
        """)

        # 3. Insertar los Menús actuales si no existen
        menus_data = [
            # Nombre, URL, Icono, Categoria, Orden
            ('Nueva Orden', 'pos', 'fas fa-cash-register', 'OPERATIVO', 1),
            ('Egresos', 'listar_egresos', 'fas fa-hand-holding-usd', 'OPERATIVO', 2),
            ('Turno Caja', 'sesion_caja', 'fas fa-lock', 'OPERATIVO', 3),
            ('Cierre Día', 'cierre_diario', 'fas fa-calendar-check', 'OPERATIVO', 4),
            ('Ventas', 'historial_ventas', 'fas fa-receipt', 'OPERATIVO', 5),
            ('Clientes', 'clientes', 'fas fa-address-book', 'OPERATIVO', 6),
            
            ('Compras', 'compras', 'fas fa-shopping-cart', 'ABASTECIMIENTO', 7),
            ('Proveedores', 'proveedores', 'fas fa-truck', 'ABASTECIMIENTO', 8),
            
            ('Usuarios', 'usuarios', 'fas fa-user-shield', 'ADMINISTRATIVO', 9),
            ('Inventario', 'inventario', 'fas fa-boxes', 'ADMINISTRATIVO', 10),
            ('Producto', 'productos', 'fas fa-hamburger', 'ADMINISTRATIVO', 11),
            ('Sucursales', 'sucursales', 'fas fa-store', 'ADMINISTRATIVO', 12),
            ('Categorías', 'categorias', 'fas fa-list', 'ADMINISTRATIVO', 13),
            ('Empresa', 'configuracion_empresa', 'fas fa-building', 'ADMINISTRATIVO', 14),
            ('Auditoría', 'ver_auditoria', 'fas fa-history', 'ADMINISTRATIVO', 15),
            ('Reportes', 'reportes', 'fas fa-chart-pie', 'ADMINISTRATIVO', 16)
        ]
        
        for nom, url, ico, cat, ord in menus_data:
            cur.execute("INSERT IGNORE INTO menus (nombre, url, icono, categoria, orden) VALUES (%s, %s, %s, %s, %s)", 
                        (nom, url, ico, cat, ord))

        # 4. Asignar Permisos por Defecto
        # Obtener IDs de roles
        cur.execute("SELECT id FROM roles WHERE nombre = 'ADMINISTRADOR'")
        admin_id = cur.fetchone()[0]
        cur.execute("SELECT id FROM roles WHERE nombre = 'CAJERO'")
        cajero_id = cur.fetchone()[0]
        
        # Admin tiene TODO
        cur.execute("SELECT id FROM menus")
        all_menus = cur.fetchall()
        for m in all_menus:
            cur.execute("INSERT IGNORE INTO rol_menus (rol_id, menu_id) VALUES (%s, %s)", (admin_id, m[0]))
            
        # Cajero solo Operativo (menos Cierre Día)
        cur.execute("SELECT id FROM menus WHERE categoria = 'OPERATIVO' AND nombre != 'Cierre Día'")
        cajero_menus = cur.fetchall()
        for m in cajero_menus:
            cur.execute("INSERT IGNORE INTO rol_menus (rol_id, menu_id) VALUES (%s, %s)", (cajero_id, m[0]))

        conn.commit()
        cur.close()
        conn.close()
        print("Sistema RBAC (Roles y Menús) inicializado con éxito.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    setup_rbac()
