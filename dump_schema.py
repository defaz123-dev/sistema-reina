import MySQLdb
import os

def dump_schema():
    host = os.environ.get('MYSQL_HOST', 'localhost')
    user = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', '')
    database = os.environ.get('MYSQL_DB', 'sistema_reina')
    port = int(os.environ.get('MYSQL_PORT', 3306))

    db = MySQLdb.connect(host=host, user=user, passwd=password, db=database, port=port)
    cur = db.cursor()
    
    # Get all tables
    cur.execute("SHOW TABLES")
    tables = [row[0] for row in cur.fetchall()]
    
    schema_sql = ""
    
    # Optional setup for constraints
    schema_sql += "SET FOREIGN_KEY_CHECKS=0;\n\n"
    
    for table in tables:
        cur.execute(f"SHOW CREATE TABLE {table}")
        result = cur.fetchone()
        create_table_stmt = result[1]
        
        # Add DROP TABLE IF EXISTS just in case it's needed when sourcing
        schema_sql += f"DROP TABLE IF EXISTS `{table}`;\n"
        schema_sql += create_table_stmt + ";\n\n"
        
    schema_sql += "SET FOREIGN_KEY_CHECKS=1;\n"

    db.close()
    
    # Write to database.sql
    with open('database.sql', 'w', encoding='utf-8') as f:
        f.write(schema_sql)
        
    # Write to database_nube.sql
    with open('database_nube.sql', 'w', encoding='utf-8') as f:
        f.write(schema_sql)

    print(f"Esquema exportado con éxito a database.sql y database_nube.sql con {len(tables)} tablas.")

if __name__ == "__main__":
    try:
        dump_schema()
    except Exception as e:
        print(f"Error: {e}")
