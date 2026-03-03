# app.py - SISTEMA REINA (COMPRAS CON FECHA Y EDICIÓN)
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime
import os
import random, csv, io

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_secreta_reina_2024')

# Configuración de Base de Datos (Prioriza variables de entorno para la nube)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'sistema_reina')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Ajuste para evitar desconexiones en la nube
if 'MYSQL_HOST' in os.environ and os.environ['MYSQL_HOST'] != 'localhost':
    # En la nube (Aiven), forzamos SSL de forma robusta
    app.config['MYSQL_CUSTOM_OPTIONS'] = {"ssl": {"ca": None}, "ssl_mode": "REQUIRED"} 
else:
    app.config['MYSQL_CUSTOM_OPTIONS'] = {}

mysql = MySQL(app)

# --- AYUDANTES ---
def get_db_cursor():
    try:
        return mysql.connection.cursor()
    except Exception as e:
        return str(e)

def identificar_tipo_doc(doc):
    return 'RUC' if len(doc) == 13 else 'CEDULA'

def generar_clave_acceso_sri(fecha, ruc_empresa, ambiente):
    f = fecha.strftime('%d%m%Y')
    clave = f"{f}01{ruc_empresa}{ambiente}001001{random.randint(1,999999):09d}123456781"
    return clave[:49]

def validar_ecuador_id(doc):
    if doc == "9999999999": return True
    if not doc or not doc.isdigit() or len(doc) not in [10, 13]: return False
    return True

# --- DECORADORES ---
def login_required(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if 'user_id' not in session: return redirect(url_for('index'))
        return f(*args, **kwargs)
    return dec

def admin_required(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if session.get('rol') != 'ADMIN':
            flash('Acceso denegado', 'danger'); return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return dec

# --- RUTAS BASE ---
@app.route('/reset_admin')
def reset_admin_emergency():
    try:
        cur = mysql.connection.cursor()
        # 1. Asegurar sucursal
        cur.execute("INSERT IGNORE INTO sucursales (id, nombre) VALUES (1, 'MATRIZ - LA REINA')")
        # 2. Asegurar admin (borramos y creamos con el hash del servidor)
        hp = generate_password_hash('admin')
        cur.execute("DELETE FROM usuarios WHERE usuario = 'admin'")
        cur.execute("INSERT INTO usuarios (usuario, password, sucursal_id, rol, activo) VALUES (%s, %s, %s, %s, %s)",
                    ('admin', hp, 1, 'ADMIN', 1))
        mysql.connection.commit()
        cur.close()
        return "<h3>Acceso Restaurado</h3><p>Usuario: <b>admin</b><br>Clave: <b>admin</b><br>Sucursal: <b>MATRIZ - LA REINA</b></p><a href='/'>Ir al Login</a>"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM sucursales")
    s = cur.fetchall()
    cur.close()
    return render_template('index.html', sucursales=s)

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        u, p, s = request.form['usuario'].lower().strip(), request.form['password'], int(request.form['sucursal'])
        cur = mysql.connection.cursor()
        
        # Primero buscamos al usuario por nombre (ignorando sucursal para admin)
        cur.execute("SELECT u.*, s.nombre as sucursal_nombre FROM usuarios u JOIN sucursales s ON u.sucursal_id = s.id WHERE LOWER(u.usuario)=%s AND u.activo=1", (u,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password'], p):
            # Si es ADMIN, le dejamos entrar aunque haya elegido mal la sucursal
            if user['rol'] == 'ADMIN' or user['sucursal_id'] == s:
                session.update({
                    'user_id': user['id'], 
                    'usuario': user['usuario'], 
                    'rol': user['rol'], 
                    'sucursal_id': user['sucursal_id'],
                    'sucursal_nombre': user['sucursal_nombre']
                })
                return redirect(url_for('dashboard'))
        
        flash('Credenciales incorrectas o sucursal no válida', 'danger')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# --- COMPRAS ---
@app.route('/compras')
@login_required
@admin_required
def compras():
    cur = mysql.connection.cursor()
    cur.execute("SELECT c.*, p.razon_social FROM compras c JOIN proveedores p ON c.proveedor_id = p.id ORDER BY c.fecha DESC")
    vs = cur.fetchall(); cur.close()
    return render_template('compras.html', compras=vs)

@app.route('/compras/nueva')
@login_required
@admin_required
def nueva_compra():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT p.*, t.nombre as tipo_comprobante_nombre 
                   FROM proveedores p 
                   JOIN tipos_comprobantes t ON p.tipo_comprobante_id = t.id""")
    provs = cur.fetchall()
    cur.execute("SELECT * FROM insumos WHERE sucursal_id = %s", (session['sucursal_id'],)); ins = cur.fetchall(); cur.close()
    hoy = datetime.now().strftime('%Y-%m-%d')
    return render_template('nueva_compra.html', proveedores=provs, insumos=ins, fecha_hoy=hoy)

@app.route('/compras/editar/<int:id>')
@login_required
@admin_required
def editar_compra(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM compras WHERE id = %s", (id,))
    compra = cur.fetchone()
    cur.execute("""SELECT dc.*, i.nombre, i.unidad_medida 
                   FROM detalles_compras dc JOIN insumos i ON dc.insumo_id = i.id 
                   WHERE dc.compra_id = %s""", (id,))
    detalles = cur.fetchall()
    cur.execute("""SELECT p.*, t.nombre as tipo_comprobante_nombre 
                   FROM proveedores p 
                   JOIN tipos_comprobantes t ON p.tipo_comprobante_id = t.id""")
    provs = cur.fetchall()
    cur.execute("SELECT * FROM insumos WHERE sucursal_id = %s", (session['sucursal_id'],)); ins = cur.fetchall()
    cur.close()
    return render_template('nueva_compra.html', proveedores=provs, insumos=ins, compra=compra, detalles=detalles)

@app.route('/compras/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_compra():
    data = request.get_json(); cur = mysql.connection.cursor()
    try:
        id_compra = data.get('compra_id')
        fecha = data['fecha']
        clave = data.get('clave_acceso')
        if id_compra:
            cur.execute("SELECT insumo_id, cantidad FROM detalles_compras WHERE compra_id = %s", (id_compra,))
            items_viejos = cur.fetchall()
            for iv in items_viejos:
                cur.execute("UPDATE insumos SET stock_actual = stock_actual - %s WHERE id = %s", (iv['cantidad'], iv['insumo_id']))
            cur.execute("UPDATE compras SET proveedor_id=%s, numero_comprobante=%s, total=%s, fecha=%s, clave_acceso=%s WHERE id=%s",
                        (data['proveedor_id'], data['numero_comprobante'].upper(), data['total'], fecha, clave, id_compra))
            cur.execute("DELETE FROM detalles_compras WHERE compra_id = %s", (id_compra,))
            comp_id_final = id_compra
        else:
            cur.execute("INSERT INTO compras (proveedor_id, sucursal_id, numero_comprobante, total, fecha, clave_acceso) VALUES (%s, %s, %s, %s, %s, %s)",
                        (data['proveedor_id'], session['sucursal_id'], data['numero_comprobante'].upper(), data['total'], fecha, clave))
            comp_id_final = cur.lastrowid
        for i in data['items']:
            cur.execute("""INSERT INTO detalles_compras (compra_id, insumo_id, cantidad, costo_unitario, subtotal, iva_valor) 
                           VALUES (%s, %s, %s, %s, %s, %s)""", 
                        (comp_id_final, i['insumo_id'], i['cantidad'], i['costo'], i['subtotal'], i['iva_valor']))
            cur.execute("UPDATE insumos SET stock_actual = stock_actual + %s WHERE id = %s", (i['cantidad'], i['insumo_id']))
        mysql.connection.commit(); cur.close()
        return jsonify({'success': True})
    except Exception as e:
        mysql.connection.rollback(); cur.close()
        return jsonify({'success': False, 'message': str(e)})

# --- CLIENTES ---
@app.route('/clientes')
@login_required
def clientes():
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM clientes"); c = cur.fetchall(); cur.close()
    return render_template('clientes.html', clientes=c)

@app.route('/clientes/buscar/<string:cedula>')
@login_required
def buscar_cliente(cedula):
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM clientes WHERE cedula_ruc=%s", (cedula,)); c = cur.fetchone(); cur.close()
    if c: return jsonify({'success': True, 'cliente': c})
    return jsonify({'success': False, 'tipo_identificado': identificar_tipo_doc(cedula)})

@app.route('/clientes/guardar', methods=['POST'])
@login_required
def guardar_cliente():
    d = request.form; cur = mysql.connection.cursor(); t = identificar_tipo_doc(d['cedula_ruc'])
    nom, ape, dir = d['nombres'].upper(), d['apellidos'].upper(), d['direccion'].upper()
    tel, eml = d['telefono'].upper(), d['email'].upper()
    if d.get('id'):
        cur.execute("UPDATE clientes SET cedula_ruc=%s, tipo_documento=%s, nombres=%s, apellidos=%s, direccion=%s, telefono=%s, email=%s WHERE id=%s", (d['cedula_ruc'], t, nom, ape, dir, tel, eml, d['id']))
    else:
        cur.execute("INSERT INTO clientes (cedula_ruc, tipo_documento, nombres, apellidos, direccion, telefono, email) VALUES (%s, %s, %s, %s, %s, %s, %s)", (d['cedula_ruc'], t, nom, ape, dir, tel, eml))
    mysql.connection.commit(); cur.close(); flash('Cliente guardado', 'success'); return redirect(url_for('clientes'))

@app.route('/clientes/guardar_json', methods=['POST'])
@login_required
def guardar_cliente_json():
    data = request.get_json(); cur = mysql.connection.cursor()
    try:
        nom, ape, dir = data['nombres'].upper(), data['apellidos'].upper(), data.get('direccion','').upper()
        tel, eml = data.get('telefono','').upper(), data.get('email','').upper()
        cur.execute("""INSERT INTO clientes (cedula_ruc, tipo_documento, nombres, apellidos, direccion, telefono, email) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE nombres=%s, apellidos=%s, direccion=%s, telefono=%s, email=%s""", 
                    (data['cedula_ruc'], identificar_tipo_doc(data['cedula_ruc']), nom, ape, dir, tel, eml, nom, ape, dir, tel, eml))
        mysql.connection.commit(); cur.execute("SELECT id FROM clientes WHERE cedula_ruc=%s", (data['cedula_ruc'],)); c_id = cur.fetchone()['id']; cur.close()
        return jsonify({'success': True, 'id': c_id})
    except Exception as e: return jsonify({'success': False, 'message': str(e)})

# --- EMPRESA ---
@app.route('/empresa')
@login_required
@admin_required
def configuracion_empresa():
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM empresa LIMIT 1"); e = cur.fetchone(); cur.close()
    return render_template('empresa.html', empresa=e)

@app.route('/empresa/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_empresa():
    d = request.form; cur = mysql.connection.cursor()
    ruc, razon, nombre, dir = d['ruc'], d['razon_social'].upper(), d['nombre_comercial'].upper(), d['direccion_matriz'].upper()
    if d.get('id'):
        cur.execute("UPDATE empresa SET ruc=%s, razon_social=%s, nombre_comercial=%s, direccion_matriz=%s, ambiente=%s WHERE id=%s", (ruc, razon, nombre, dir, d['ambiente'], d['id']))
    else:
        cur.execute("INSERT INTO empresa (ruc, razon_social, nombre_comercial, direccion_matriz, ambiente) VALUES (%s, %s, %s, %s, %s)", (ruc, razon, nombre, dir, d['ambiente']))
    mysql.connection.commit(); cur.close(); flash('Datos guardados', 'success'); return redirect(url_for('configuracion_empresa'))

# --- POS Y VENTAS ---
@app.route('/pos')
@login_required
def pos():
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM categorias"); c = cur.fetchall()
    cur.execute("SELECT id, codigo, nombre, precio, categoria_id, IF(imagen IS NOT NULL, 1, 0) as tiene_foto FROM productos"); p = cur.fetchall(); cur.close()
    return render_template('pos.html', categorias=c, productos=p)

@app.route('/pos/venta', methods=['POST'])
@login_required
def procesar_venta():
    data = request.get_json(); cur = mysql.connection.cursor()
    try:
        c_id = data.get('cliente_id'); fpago = data.get('forma_pago', 'EFECTIVO').upper()
        cur.execute("SELECT ruc, ambiente FROM empresa LIMIT 1"); emp = cur.fetchone()
        ruc = emp['ruc'] if emp else "1790000000001"; amb = emp['ambiente'] if emp else 1
        clave = generar_clave_acceso_sri(datetime.now(), ruc, amb)
        cur.execute("""INSERT INTO ventas (usuario_id, sucursal_id, cliente_id, total, forma_pago, clave_acceso_sri, estado_sri) 
                       VALUES (%s, %s, %s, %s, %s, %s, 'AUTORIZADO (PRUEBAS)')""", (session['user_id'], session['sucursal_id'], c_id, data['total'], fpago, clave))
        v_id = cur.lastrowid
        for i in data['items']:
            cur.execute("INSERT INTO detalles_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)", (v_id, i['id'], i['cantidad'], i['precio'], float(i['precio']) * int(i['cantidad'])))
            cur.execute("SELECT insumo_id, cantidad_requerida FROM recetas WHERE producto_id=%s", (i['id'],))
            for ing in cur.fetchall(): cur.execute("UPDATE insumos SET stock_actual=stock_actual-%s WHERE id=%s", (float(ing['cantidad_requerida']) * int(i['cantidad']), ing['insumo_id']))
        mysql.connection.commit(); cur.close(); return jsonify({'success': True, 'venta_id': v_id})
    except Exception as e: return jsonify({'success': False, 'message': str(e)})

@app.route('/ventas')
@login_required
def historial_ventas():
    cur = mysql.connection.cursor(); cur.execute("""SELECT v.*, c.nombres, c.apellidos, u.usuario FROM ventas v JOIN clientes c ON v.cliente_id=c.id JOIN usuarios u ON v.usuario_id=u.id ORDER BY v.fecha DESC"""); v = cur.fetchall(); cur.close()
    return render_template('ventas.html', ventas=v)

@app.route('/venta/ticket/<int:id>')
@login_required
def ver_ticket(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ventas WHERE id=%s", (id,)); v = cur.fetchone()
    if not v: return "No existe", 404
    cur.execute("SELECT * FROM clientes WHERE id=%s", (v['cliente_id'],)); c = cur.fetchone()
    cur.execute("SELECT * FROM sucursales WHERE id=%s", (v['sucursal_id'],)); s = cur.fetchone()
    cur.execute("SELECT usuario FROM usuarios WHERE id=%s", (v['usuario_id'],)); u = cur.fetchone()
    cur.execute("""SELECT dv.*, p.nombre FROM detalles_ventas dv JOIN productos p ON dv.producto_id=p.id WHERE dv.venta_id=%s""", (id,))
    det = cur.fetchall()
    cur.execute("SELECT * FROM empresa LIMIT 1"); emp = cur.fetchone()
    cur.close()
    return render_template('ticket.html', venta=v, cliente=c, sucursal=s, usuario=u, detalles=det, empresa=emp)

# --- REPORTES ---
@app.route('/reportes')
@login_required
@admin_required
def reportes():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT v.*, c.nombres, c.apellidos, u.usuario FROM ventas v JOIN clientes c ON v.cliente_id=c.id JOIN usuarios u ON v.usuario_id=u.id ORDER BY v.fecha DESC"""); v = cur.fetchall()
    cur.execute("""SELECT p.nombre, SUM(dv.cantidad) as total_vendido FROM detalles_ventas dv JOIN productos p ON dv.producto_id=p.id GROUP BY p.id ORDER BY total_vendido DESC LIMIT 5"""); t = cur.fetchall(); cur.close()
    return render_template('reportes.html', ventas=v, top_productos=t)

# --- MANTENIMIENTOS ---
@app.route('/usuarios')
@login_required
@admin_required
def usuarios():
    cur = mysql.connection.cursor(); cur.execute("SELECT u.*, s.nombre as sucursal_nombre FROM usuarios u LEFT JOIN sucursales s ON u.sucursal_id=s.id"); u = cur.fetchall()
    cur.execute("SELECT * FROM sucursales"); s = cur.fetchall(); cur.close(); return render_template('usuarios.html', usuarios=u, sucursales=s)

@app.route('/usuarios/crear', methods=['POST'])
@login_required
@admin_required
def crear_usuario():
    u, p, s, r = request.form['usuario'], request.form['password'], request.form['sucursal_id'], request.form['rol']; hp = generate_password_hash(p); cur = mysql.connection.cursor()
    cur.execute("INSERT INTO usuarios (usuario, password, sucursal_id, rol, activo) VALUES (%s, %s, %s, %s, 1)", (u, hp, s, r)); mysql.connection.commit(); cur.close(); return redirect(url_for('usuarios'))

@app.route('/usuarios/editar', methods=['POST'])
@login_required
@admin_required
def editar_usuario():
    id_u, u, p, s, r, a = request.form['id'], request.form['usuario'], request.form['password'], request.form['sucursal_id'], request.form['rol'], request.form['activo']; cur = mysql.connection.cursor()
    if p: hp = generate_password_hash(p); cur.execute("UPDATE usuarios SET usuario=%s, password=%s, sucursal_id=%s, rol=%s, activo=%s WHERE id=%s", (u, hp, s, r, a, id_u))
    else: cur.execute("UPDATE usuarios SET usuario=%s, sucursal_id=%s, rol=%s, activo=%s WHERE id=%s", (u, s, r, a, id_u))
    mysql.connection.commit(); cur.close(); return redirect(url_for('usuarios'))

@app.route('/inventario')
@login_required
@admin_required
def inventario():
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM insumos WHERE sucursal_id=%s", (session['sucursal_id'],)); i = cur.fetchall(); cur.close(); return render_template('inventario.html', insumos=i)

@app.route('/inventario/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_insumo():
    d = request.form; cur = mysql.connection.cursor(); nom, uni = d['nombre'].upper(), d['unidad'].upper()
    if d.get('id'): cur.execute("UPDATE insumos SET nombre=%s, stock_actual=%s, unidad_medida=%s WHERE id=%s", (nom, d['stock'], uni, d['id']))
    else: cur.execute("INSERT INTO insumos (nombre, stock_actual, unidad_medida, sucursal_id) VALUES (%s, %s, %s, %s)", (nom, d['stock'], uni, session['sucursal_id']))
    mysql.connection.commit(); cur.close(); return redirect(url_for('inventario'))

@app.route('/productos')
@login_required
@admin_required
def productos():
    cur = mysql.connection.cursor(); cur.execute("""SELECT p.*, c.nombre as categoria_nombre FROM productos p JOIN categorias c ON p.categoria_id = c.id"""); p = cur.fetchall(); cur.execute("SELECT * FROM categorias"); cats = cur.fetchall(); cur.close(); return render_template('productos.html', productos=p, categorias=cats)

@app.route('/productos/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_producto():
    d = request.form; img = request.files.get('imagen'); cur = mysql.connection.cursor(); cod, nom = d['codigo'].upper(), d['nombre'].upper()
    try:
        if img and img.filename != '':
            ib = img.read(); mt = img.content_type
            if d.get('id'): cur.execute("UPDATE productos SET codigo=%s, nombre=%s, precio=%s, categoria_id=%s, imagen=%s, mimetype=%s WHERE id=%s", (cod, nom, d['precio'], d['categoria_id'], ib, mt, d['id']))
            else: cur.execute("INSERT INTO productos (codigo, nombre, precio, categoria_id, imagen, mimetype) VALUES (%s, %s, %s, %s, %s, %s)", (cod, nom, d['precio'], d['categoria_id'], ib, mt))
        else:
            if d.get('id'): cur.execute("UPDATE productos SET codigo=%s, nombre=%s, precio=%s, categoria_id=%s WHERE id=%s", (cod, nom, d['precio'], d['categoria_id'], d['id']))
            else: cur.execute("INSERT INTO productos (codigo, nombre, precio, categoria_id) VALUES (%s, %s, %s, %s)", (cod, nom, d['precio'], d['categoria_id']))
        mysql.connection.commit()
    except Exception as e: flash(str(e), 'danger')
    cur.close(); return redirect(url_for('productos'))

@app.route('/productos/receta/<int:producto_id>')
@login_required
@admin_required
def ver_receta(producto_id):
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM productos WHERE id=%s", (producto_id,)); p = cur.fetchone(); cur.execute("""SELECT r.*, i.nombre, i.unidad_medida FROM recetas r JOIN insumos i ON r.insumo_id=i.id WHERE r.producto_id=%s""", (producto_id,)); r = cur.fetchall(); cur.execute("SELECT * FROM insumos WHERE sucursal_id=%s", (session['sucursal_id'],)); i = cur.fetchall(); cur.close(); return render_template('recetas.html', producto=p, receta=r, insumos=i)

@app.route('/productos/receta/agregar', methods=['POST'])
@login_required
@admin_required
def agregar_insumo_receta():
    pi, ii, ct = request.form['producto_id'], request.form['insumo_id'], request.form['cantidad']; cur = mysql.connection.cursor(); cur.execute("INSERT INTO recetas (producto_id, insumo_id, cantidad_requerida) VALUES (%s, %s, %s)", (pi, ii, ct)); mysql.connection.commit(); cur.close(); return redirect(url_for('ver_receta', producto_id=pi))

@app.route('/productos/receta/eliminar/<int:id>/<int:p_id>')
@login_required
@admin_required
def eliminar_insumo_receta(id, p_id):
    cur = mysql.connection.cursor(); cur.execute("DELETE FROM recetas WHERE id=%s", (id,)); mysql.connection.commit(); cur.close(); return redirect(url_for('ver_receta', producto_id=p_id))

@app.route('/proveedores')
@login_required
@admin_required
def proveedores():
    cur = mysql.connection.cursor(); cur.execute("""SELECT p.*, t.nombre as tipo_comprobante FROM proveedores p JOIN tipos_comprobantes t ON p.tipo_comprobante_id = t.id"""); p = cur.fetchall(); cur.execute("SELECT * FROM tipos_comprobantes"); t = cur.fetchall(); cur.close(); return render_template('proveedores.html', proveedores=p, tipos=t)

@app.route('/proveedores/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_proveedor():
    d = request.form; cur = mysql.connection.cursor(); ruc = d['ruc']; razon = d['razon_social'].upper(); nombre = d['nombre_comercial'].upper(); dire = d['direccion'].upper(); tel = d['telefono']; eml = d['email'].upper(); tipo_comp = d['tipo_comprobante_id']
    try:
        if d.get('id'): cur.execute("UPDATE proveedores SET ruc=%s, razon_social=%s, nombre_comercial=%s, direccion=%s, telefono=%s, email=%s, tipo_comprobante_id=%s WHERE id=%s", (ruc, razon, nombre, dire, tel, eml, tipo_comp, d['id']))
        else: cur.execute("INSERT INTO proveedores (ruc, razon_social, nombre_comercial, direccion, telefono, email, tipo_comprobante_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (ruc, razon, nombre, dire, tel, eml, tipo_comp))
        mysql.connection.commit(); flash('Proveedor guardado', 'success')
    except Exception as e: flash(str(e), 'danger')
    cur.close(); return redirect(url_for('proveedores'))

@app.route('/sucursales')
@login_required
@admin_required
def sucursales():
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM sucursales"); s = cur.fetchall(); cur.close(); return render_template('sucursales.html', sucursales=s)

@app.route('/sucursales/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_sucursal():
    d = request.form; cur = mysql.connection.cursor(); nom = d['nombre'].upper()
    if d.get('id'): cur.execute("UPDATE sucursales SET nombre=%s WHERE id=%s", (nom, d['id']))
    else: cur.execute("INSERT INTO sucursales (nombre) VALUES (%s)", (nom,))
    mysql.connection.commit(); cur.close(); return redirect(url_for('sucursales'))

@app.route('/categorias')
@login_required
@admin_required
def categorias():
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM categorias"); c = cur.fetchall(); cur.close(); return render_template('categorias.html', categorias=c)

@app.route('/categorias/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_categoria():
    d = request.form; cur = mysql.connection.cursor(); nom = d['nombre'].upper()
    if d.get('id'): cur.execute("UPDATE categorias SET nombre=%s WHERE id=%s", (nom, d['id']))
    else: cur.execute("INSERT INTO categorias (nombre) VALUES (%s)", (nom,))
    mysql.connection.commit(); cur.close(); return redirect(url_for('categorias'))

@app.route('/producto/imagen/<int:id>')
def producto_imagen(id):
    cur = mysql.connection.cursor(); cur.execute("SELECT imagen, mimetype FROM productos WHERE id=%s", (id,)); p = cur.fetchone(); cur.close()
    if p and p['imagen']: return Response(p['imagen'], mimetype=p['mimetype'] or 'image/jpeg')
    return redirect(url_for('static', filename='img/default.png'))

if __name__ == '__main__':
    app.run(debug=True)
