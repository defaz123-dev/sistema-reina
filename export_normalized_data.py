import MySQLdb
import MySQLdb.cursors
import os

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',
    'db': 'sistema_reina',
    'cursorclass': MySQLdb.cursors.DictCursor
}

def generate_full_scripts():
    try:
        db = MySQLdb.connect(**DB_CONFIG)
        cur = db.cursor()

        # Tablas de las que extraeremos DATOS reales
        data_tables = [
            'roles', 'tipos_identificacion', 'tipos_comprobantes', 'unidades_medida',
            'empresa', 'sucursales', 'usuarios', 'categorias', 'plataformas', 
            'cat_tarjetas', 'proveedores', 'productos', 'producto_precios', 'menus', 'rol_menus'
        ]
        
        # Todas las tablas para la ESTRUCTURA (en orden de dependencia para evitar errores de FK)
        structure_tables = [
            'roles', 'tipos_identificacion', 'tipos_comprobantes', 'unidades_medida',
            'sucursales', 'empresa', 'usuarios', 'categorias', 'plataformas', 'cat_tarjetas',
            'proveedores', 'insumos', 'productos', 'recetas', 'producto_precios',
            'sesiones_caja', 'ventas', 'detalles_ventas', 'compras', 'detalles_compras',
            'egresos', 'flujo_caja', 'cierres_diarios', 'auditoria', 'ajustes_inventario',
            'anulaciones_factura', 'menus', 'rol_menus'
        ]

        sql_output = "-- SISTEMA REINA - SCRIPT DE RESTAURACION COMPLETA (IDS NORMALIZADOS)\n"
        sql_output += "-- Generado el: 9 de marzo de 2026\n"
        sql_output += "SET FOREIGN_KEY_CHECKS = 0;\n\n"

        # 1. Generar ESTRUCTURA (DROP y CREATE)
        for table in structure_tables:
            sql_output += f"DROP TABLE IF EXISTS `{table}`;\n"
            cur.execute(f"SHOW CREATE TABLE `{table}`")
            create_stmt = cur.fetchone()['Create Table']
            sql_output += f"{create_stmt};\n\n"

        # 2. Generar DATOS normalizados
        mappings = {table: {} for table in data_tables}
        
        for table in data_tables:
            cur.execute(f"SELECT * FROM `{table}`")
            rows = cur.fetchall()
            if not rows: continue

            sql_output += f"-- Datos para {table}\n"
            
            # Normalización de IDs
            new_id = 1
            for row in rows:
                old_id = row.get('id')
                if old_id is not None:
                    mappings[table][old_id] = new_id
                    row['id'] = new_id
                    new_id += 1
                
                # Ajuste de Foreign Keys basándose en los nuevos mappings
                if table == 'usuarios':
                    row['sucursal_id'] = mappings['sucursales'].get(row['sucursal_id'], row['sucursal_id'])
                    row['rol_id'] = mappings['roles'].get(row['rol_id'], row['rol_id'])
                    row['tipo_identificacion_id'] = mappings['tipos_identificacion'].get(row['tipo_identificacion_id'], row['tipo_identificacion_id'])
                elif table == 'sucursales':
                    # Reiniciar secuencial a 0 si se desea una base limpia, o mantener actual
                    pass
                elif table == 'productos':
                    row['categoria_id'] = mappings['categorias'].get(row['categoria_id'], row['categoria_id'])
                elif table == 'producto_precios':
                    row['producto_id'] = mappings['productos'].get(row['producto_id'], row['producto_id'])
                    row['plataforma_id'] = mappings['plataformas'].get(row['plataforma_id'], row['plataforma_id'])
                elif table == 'proveedores':
                    row['tipo_comprobante_id'] = mappings['tipos_comprobantes'].get(row['tipo_comprobante_id'], row['tipo_comprobante_id'])
                elif table == 'rol_menus':
                    row['rol_id'] = mappings['roles'].get(row['rol_id'], row['rol_id'])
                    row['menu_id'] = mappings['menus'].get(row['menu_id'], row['menu_id'])

                # Construir INSERT
                cols = ", ".join([f"`{k}`" for k in row.keys()])
                vals = []
                for v in row.values():
                    if v is None: vals.append("NULL")
                    elif isinstance(v, (int, float)): vals.append(str(v))
                    elif isinstance(v, bytes): vals.append(f"0x{v.hex()}")
                    else: vals.append(f"'{db.escape_string(str(v)).decode()}'")
                
                sql_output += f"INSERT INTO `{table}` ({cols}) VALUES ({', '.join(vals)});\n"
            sql_output += "\n"

        sql_output += "SET FOREIGN_KEY_CHECKS = 1;\n"

        # Guardar archivos
        with open('database.sql', 'w', encoding='utf-8') as f:
            f.write(sql_output)
        with open('database_nube.sql', 'w', encoding='utf-8') as f:
            f.write(sql_output)

        print("✅ Archivos database.sql y database_nube.sql generados con éxito.")
        cur.close()
        db.close()
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")

if __name__ == "__main__":
    generate_full_scripts()
