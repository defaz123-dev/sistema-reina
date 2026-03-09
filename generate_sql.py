import MySQLdb
import os

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',
    'db': 'sistema_reina'
}

def generate_simple_sql():
    try:
        db = MySQLdb.connect(**DB_CONFIG)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Tablas que queremos conservar con DATOS
        tables_with_data = [
            'roles', 'tipos_identificacion', 'tipos_comprobantes', 'unidades_medida',
            'empresa', 'sucursales', 'usuarios', 'categorias', 'productos', 'proveedores', 'insumos'
        ]
        
        # Todas las tablas para la ESTRUCTURA (en orden de dependencia)
        all_tables = [
            'roles', 'tipos_identificacion', 'tipos_comprobantes', 'unidades_medida',
            'sucursales', 'empresa', 'usuarios', 'categorias', 'productos', 'proveedores', 
            'insumos', 'ventas', 'detalles_ventas', 'compras', 'detalles_compras', 
            'egresos', 'flujo_caja', 'sesiones_caja', 'cierres_diarios', 
            'auditoria', 'ajustes_inventario', 'cat_tarjetas', 'plataformas', 'producto_precios', 'recetas'
        ]

        sql_output = "-- SISTEMA REINA - SCRIPT DE RESTAURACION LIMPIA\n"
        sql_output += "SET FOREIGN_KEY_CHECKS = 0;\n\n"

        for table in all_tables:
            # 1. DROP
            sql_output += f"DROP TABLE IF EXISTS `{table}`;\n"
            
            # 2. CREATE
            cursor.execute(f"SHOW CREATE TABLE `{table}`")
            create_stmt = cursor.fetchone()['Create Table']
            sql_output += f"{create_stmt};\n\n"
            
            # 3. INSERT (Solo si está en la lista de datos)
            if table in tables_with_data:
                cursor.execute(f"SELECT * FROM `{table}`")
                rows = cursor.fetchall()
                if rows:
                    sql_output += f"-- Datos para {table}\n"
                    for row in rows:
                        cols = ", ".join([f"`{k}`" for k in row.keys()])
                        vals = []
                        for v in row.values():
                            if v is None: vals.append("NULL")
                            elif isinstance(v, (int, float, complex)): vals.append(str(v))
                            elif isinstance(v, bytes): vals.append(f"0x{v.hex()}") # Manejo de imágenes
                            else: vals.append(f"'{db.escape_string(str(v)).decode()}'")
                        
                        val_str = ", ".join(vals)
                        sql_output += f"INSERT INTO `{table}` ({cols}) VALUES ({val_str});\n"
                    sql_output += "\n"

        sql_output += "SET FOREIGN_KEY_CHECKS = 1;\n"

        # Guardar en ambos archivos
        with open('database.sql', 'w', encoding='utf-8') as f:
            f.write(sql_output)
        with open('database_nube.sql', 'w', encoding='utf-8') as f:
            f.write(sql_output)

        print("✅ Scripts database.sql y database_nube.sql generados en formato simple.")
        db.close()
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    generate_simple_sql()
