import MySQLdb
import os
import re

def parse_sql_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tables = {}
    
    parts = re.split(r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?`?(\w+)`?', content, flags=re.IGNORECASE)
    
    for i in range(1, len(parts), 2):
        table_name = parts[i]
        table_def = parts[i+1].split(';')[0]
        
        # Extracción más robusta de columnas: busca líneas que empiezan con un nombre de columna
        # ignorando palabras clave comunes de restricciones (CONSTRAINT, PRIMARY, KEY, FOREIGN, UNIQUE)
        lines = table_def.split('\n')
        cols = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('--') or line.startswith('/*'):
                continue
            
            upper_line = line.upper()
            if upper_line.startswith('PRIMARY KEY') or upper_line.startswith('FOREIGN KEY') or \
               upper_line.startswith('UNIQUE KEY') or upper_line.startswith('KEY ') or \
               upper_line.startswith('CONSTRAINT '):
                continue
                
            match = re.match(r'`?(\w+)`?\s+', line)
            if match:
                cols.append(match.group(1).lower())
                
        tables[table_name.lower()] = cols
        
    return tables

def get_live_schema():
    host = os.environ.get('MYSQL_HOST', 'localhost')
    user = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', '')
    database = os.environ.get('MYSQL_DB', 'sistema_reina')
    port = int(os.environ.get('MYSQL_PORT', 3306))

    db = MySQLdb.connect(host=host, user=user, passwd=password, db=database, port=port)
    cur = db.cursor()
    
    cur.execute("SHOW TABLES")
    tables_raw = cur.fetchall()
    
    schema = {}
    for (t,) in tables_raw:
        cur.execute(f"SHOW COLUMNS FROM {t}")
        cols = cur.fetchall()
        schema[t.lower()] = [c[0].lower() for c in cols]
        
    db.close()
    return schema

def compare(live, sql_schema, file_name):
    print(f"\n--- Comparando con {file_name} ---")
    missing_tables = []
    missing_columns = {}
    
    for table, cols in live.items():
        if table not in sql_schema:
            missing_tables.append(table)
        else:
            file_cols = sql_schema[table]
            for c in cols:
                if c not in file_cols:
                    if table not in missing_columns:
                        missing_columns[table] = []
                    missing_columns[table].append(c)
                    
    if missing_tables:
        print(f"Tablas faltantes en {file_name}:")
        for t in missing_tables:
            print(f"  - {t}")
    else:
        print(f"Todas las tablas de la BD actual existen en {file_name}.")
        
    if missing_columns:
        print(f"Columnas faltantes en {file_name}:")
        for t, cols in missing_columns.items():
            print(f"  Tabla '{t}': {', '.join(cols)}")
    else:
        print(f"Todas las columnas de la BD actual existen en {file_name}.")

try:
    live_schema = get_live_schema()
    local_schema = parse_sql_file('database.sql')
    nube_schema = parse_sql_file('database_nube.sql')

    compare(live_schema, local_schema, 'database.sql')
    compare(live_schema, nube_schema, 'database_nube.sql')
except Exception as e:
    print(f"Error: {e}")
