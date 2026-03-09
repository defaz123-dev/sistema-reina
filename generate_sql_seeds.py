import MySQLdb
import MySQLdb.cursors

def generate_seeds():
    try:
        db = MySQLdb.connect(host='localhost', user='root', passwd='', db='sistema_reina', cursorclass=MySQLdb.cursors.DictCursor)
        cur = db.cursor()

        tables_to_export = [
            'empresa', 'sucursales', 'roles', 'usuarios', 'categorias', 
            'plataformas', 'cat_tarjetas', 'proveedores', 'productos', 'producto_precios'
        ]
        
        sql_output = "-- SEED DATA GENERATED AUTOMATICALLY\nSET FOREIGN_KEY_CHECKS = 0;\n\n"
        
        # Mapping for ID normalization
        mappings = {table: {} for table in tables_to_export}

        for table in tables_to_export:
            cur.execute(f"SELECT * FROM {table}")
            rows = cur.fetchall()
            if not rows: continue

            sql_output += f"TRUNCATE TABLE `{table}`;\n"
            sql_output += f"INSERT INTO `{table}` ("
            
            columns = [col for col in rows[0].keys()]
            sql_output += ", ".join([f"`{c}`" for c in columns]) + ") VALUES \n"
            
            value_lines = []
            new_id = 1
            for row in rows:
                # Map old ID to new ID
                if 'id' in row:
                    mappings[table][row['id']] = new_id
                    row['id'] = new_id
                    new_id += 1
                
                # Adjust Foreign Keys based on mappings
                if table == 'usuarios':
                    row['sucursal_id'] = mappings['sucursales'].get(row['sucursal_id'], row['sucursal_id'])
                    row['rol_id'] = mappings['roles'].get(row['rol_id'], row['rol_id'])
                elif table == 'productos':
                    row['categoria_id'] = mappings['categorias'].get(row['categoria_id'], row['categoria_id'])
                elif table == 'producto_precios':
                    row['producto_id'] = mappings['productos'].get(row['producto_id'], row['producto_id'])
                    row['plataforma_id'] = mappings['plataformas'].get(row['plataforma_id'], row['plataforma_id'])
                
                vals = []
                for col in columns:
                    v = row[col]
                    if v is None: vals.append("NULL")
                    elif isinstance(v, (int, float)): vals.append(str(v))
                    else: vals.append(f"'{db.escape_string(str(v)).decode('utf-8')}'")
                
                value_lines.append("(" + ", ".join(vals) + ")")
            
            sql_output += ",\n".join(value_lines) + ";\n\n"

        sql_output += "SET FOREIGN_KEY_CHECKS = 1;\n"
        
        with open('seed_data.sql', 'w', encoding='utf-8') as f:
            f.write(sql_output)
            
        cur.close()
        db.close()
        print("Seed data generated successfully in seed_data.sql")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_seeds()
