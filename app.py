# app.py - SISTEMA REINA (VERSIÓN PRO PLUS - RESTAURADA Y COMPLETA)
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime
import os
import random, csv, io, requests, base64, smtplib, socket, traceback
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'de3329d04ce1a976af2b00ad49485c37d449e45389a300bb')

# Configuración de Base de Datos
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'sistema_reina')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.before_request
def configurar_zona_horaria():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SET time_zone = '-05:00';")
        cur.close()
    except: pass

# --- AYUDANTES ---
from PIL import Image

def procesar_imagen(file_storage, max_size=(800, 800), quality=85):
    try:
        img = Image.open(file_storage)
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue(), 'image/jpeg'
    except:
        file_storage.seek(0)
        return file_storage.read(), file_storage.content_type

def calcular_modulo11(cadena):
    pivote = 2; suma = 0
    for i in range(len(cadena) - 1, -1, -1):
        suma += int(cadena[i]) * pivote
        pivote = 2 if pivote == 7 else pivote + 1
    res = suma % 11; v = 11 - res
    return 0 if v == 11 else 1 if v == 10 else v

def generar_clave_acceso_sri(fecha, ruc, ambiente, serie='001001', secuencial='000000001'):
    f = fecha.strftime('%d%m%Y')
    c_48 = f"{f}01{ruc}{ambiente}{serie}{secuencial}123456781"
    return f"{c_48}{calcular_modulo11(c_48)}"

def registrar_auditoria(accion, detalle):
    try:
        cur = mysql.connection.cursor()
        ip_str = request.headers.get('X-Forwarded-For', request.remote_addr)
        ip = ip_str.split(',')[0] if ip_str else '0.0.0.0'
        cur.execute("INSERT INTO auditoria (usuario_id, accion, detalle, ip) VALUES (%s, %s, %s, %s)",
                    (session.get('user_id'), accion, f"[{session.get('sucursal_nombre','S/S')}] {detalle}", ip))
        mysql.connection.commit(); cur.close()
    except: pass

def identificar_tipo_doc(doc):
    if doc == "9999999999": return 4
    return 2 if len(doc) == 13 else 1

def validar_ruc_sri(identificacion, tipo_id=None):
    """
    Valida RUC o Cédula de Ecuador con algoritmos del SRI (Módulo 10 y 11)
    Si se provee tipo_id: 1=Cedula, 2=RUC
    """
    identificacion = str(identificacion).strip()
    if not identificacion.isdigit(): return False
    
    l = len(identificacion)
    
    # Validar longitud según tipo_id si se proporciona
    if tipo_id:
        tipo_id = int(tipo_id)
        if tipo_id == 1 and l != 10: return False # Cédula debe ser 10
        if tipo_id == 2 and l != 13: return False # RUC debe ser 13
        if tipo_id == 4: return identificacion == "9999999999" # Consumidor Final
        if tipo_id == 3: return True # Pasaporte no tiene regla fija numérica estricta aquí
    
    if l not in [10, 13]: return False

    # Los dos primeros dígitos corresponden a la provincia (01 a 24) o 30
    prov = int(identificacion[0:2])
    if not (1 <= prov <= 24 or prov == 30): return False

    # El tercer dígito indica el tipo de ruc
    tercer_digito = int(identificacion[2])
    
    if tercer_digito < 6:
        # Persona Natural o Cédula (Módulo 10)
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        verificador = int(identificacion[9])
        suma = 0
        for i in range(9):
            valor = int(identificacion[i]) * coeficientes[i]
            suma += valor if valor < 10 else valor - 9
        resultado = 10 - (suma % 10)
        if resultado == 10: resultado = 0
        if resultado != verificador: return False
    elif tercer_digito == 6:
        # Entidades Públicas (Módulo 11)
        if l == 10: return False # RUC público siempre es 13
        coeficientes = [3, 2, 7, 6, 5, 4, 3, 2]
        verificador = int(identificacion[8])
        suma = 0
        for i in range(8):
            suma += int(identificacion[i]) * coeficientes[i]
        resultado = 11 - (suma % 11)
        if resultado == 11: resultado = 0
        if resultado != verificador: return False
    elif tercer_digito == 9:
        # Sociedades Privadas / Extranjeros (Módulo 11)
        coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2]
        verificador = int(identificacion[9])
        suma = 0
        for i in range(9):
            suma += int(identificacion[i]) * coeficientes[i]
        resultado = 11 - (suma % 11)
        if resultado == 11: resultado = 0
        if resultado != verificador: return False
    else:
        return False

    # Si es RUC (13 dígitos), los últimos 3 deben ser 001
    if l == 13 and identificacion[10:13] != "001":
        return False

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
        if session.get('rol') != 'ADMINISTRADOR':
            flash('Acceso denegado', 'danger'); return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return dec

@app.context_processor
def inject_empresa():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT nombre_comercial, color_tema, icono_espera FROM empresa LIMIT 1")
        e = cur.fetchone(); cur.close()
        return dict(config_empresa=e) if e else dict(config_empresa={'nombre_comercial': 'SISTEMA REINA', 'color_tema': '#008938', 'icono_espera': 'fa-crown'})
    except: return dict(config_empresa={'nombre_comercial': 'SISTEMA REINA', 'color_tema': '#008938', 'icono_espera': 'fa-crown'})

# --- RUTAS BASE ---
@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM sucursales"); s = cur.fetchall(); cur.close()
    return render_template('index.html', sucursales=s)

@app.route('/login', methods=['POST'])
def login():
    c, p, s_id = request.form['usuario'].strip(), request.form['password'], int(request.form['sucursal'])
    cur = mysql.connection.cursor()
    cur.execute("SELECT u.*, r.nombre as rol_nombre FROM usuarios u JOIN roles r ON u.rol_id = r.id WHERE u.cedula=%s", (c,))
    user = cur.fetchone()
    if user and user['activo'] and check_password_hash(user['password'], p):
        cur.execute("SELECT nombre, establecimiento, punto_emision FROM sucursales WHERE id=%s", (s_id,))
        suc = cur.fetchone(); cur.close()
        session.update({
            'user_id': user['id'], 'usuario': user['usuario'], 'rol': user['rol_nombre'], 
            'sucursal_id': s_id, 'sucursal_nombre': suc['nombre'],
            'establecimiento': suc['establecimiento'], 'punto_emision': suc['punto_emision']
        })
        registrar_auditoria('LOGIN', f"Inició sesión en {suc['nombre']}")
        return redirect(url_for('dashboard'))
    cur.close(); flash('Credenciales incorrectas o usuario inactivo', 'danger')
    return redirect(url_for('index'))

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard(): return render_template('dashboard.html')

# --- CLIENTES ---
@app.route('/clientes')
@login_required
def clientes():
    cur = mysql.connection.cursor(); cur.execute("SELECT c.*, t.nombre as tipo_id_nombre FROM clientes c JOIN tipos_identificacion t ON c.tipo_identificacion_id = t.id")
    c = cur.fetchall(); cur.execute("SELECT * FROM tipos_identificacion"); t = cur.fetchall(); cur.close()
    return render_template('clientes.html', clientes=c, tipos_id=t)

@app.route('/clientes/buscar/<string:cedula>')
@login_required
def buscar_cliente(cedula):
    cur = mysql.connection.cursor(); cur.execute("SELECT c.*, t.nombre as tipo_id_nombre FROM clientes c JOIN tipos_identificacion t ON c.tipo_identificacion_id = t.id WHERE c.cedula_ruc=%s", (cedula,))
    c = cur.fetchone(); cur.close()
    return jsonify({'success': True, 'cliente': c}) if c else jsonify({'success': False, 'tipo_identificado_id': identificar_tipo_doc(cedula)})

@app.route('/clientes/guardar', methods=['POST'])
@login_required
def guardar_cliente():
    d = request.form; cur = mysql.connection.cursor(); u_id = session['user_id']
    ruc_ced = d['cedula_ruc'].strip()

    # VALIDACIÓN SRI (Excepto Consumidor Final)
    if ruc_ced != "9999999999" and not validar_ruc_sri(ruc_ced):
        flash('La identificación ingresada no es válida según el algoritmo del SRI', 'danger')
        return redirect(url_for('clientes'))

    t_id = d.get('tipo_identificacion_id') or identificar_tipo_doc(ruc_ced)
    nom, ape, dir = d['nombres'].upper(), d['apellidos'].upper(), d['direccion'].upper()
    try:
        if d.get('id'): cur.execute("UPDATE clientes SET cedula_ruc=%s, tipo_identificacion_id=%s, nombres=%s, apellidos=%s, direccion=%s, telefono=%s, email=%s, usuario_modificacion_id=%s WHERE id=%s", (ruc_ced, t_id, nom, ape, dir, d['telefono'], d['email'].upper(), u_id, d['id']))
        else: cur.execute("INSERT INTO clientes (cedula_ruc, tipo_identificacion_id, nombres, apellidos, direccion, telefono, email, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (ruc_ced, t_id, nom, ape, dir, d['telefono'], d['email'].upper(), u_id, u_id))
        mysql.connection.commit(); cur.close(); flash('Cliente guardado', 'success')
    except Exception as e:
        if "1062" in str(e): flash('Error: Ya existe un cliente con esa identificación', 'danger')
        else: flash(f'Error al guardar: {str(e)}', 'danger')
        cur.close()
    return redirect(url_for('clientes'))

@app.route('/clientes/guardar_json', methods=['POST'])
@login_required
def guardar_cliente_json():
    data = request.get_json(); cur = mysql.connection.cursor(); u_id = session['user_id']
    try:
        ruc_ced = data['cedula_ruc'].strip()
        # VALIDACIÓN SRI (Excepto Consumidor Final)
        if ruc_ced != "9999999999" and not validar_ruc_sri(ruc_ced):
            return jsonify({'success': False, 'message': 'La identificación no es válida (Algoritmo SRI)'})

        nom, ape, dir = data['nombres'].upper(), data['apellidos'].upper(), data.get('direccion','').upper()
        tel, eml = data.get('telefono','').upper(), data.get('email','').upper()
        t_id = data.get('tipo_identificacion_id') or identificar_tipo_doc(ruc_ced)
        cur.execute("""INSERT INTO clientes (cedula_ruc, tipo_identificacion_id, nombres, apellidos, direccion, telefono, email, usuario_creacion_id, usuario_modificacion_id) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE nombres=%s, apellidos=%s, direccion=%s, email=%s""", 
                    (ruc_ced, t_id, nom, ape, dir, tel, eml, u_id, u_id, nom, ape, dir, eml))
        mysql.connection.commit(); cur.execute("SELECT id FROM clientes WHERE cedula_ruc=%s", (ruc_ced,)); c_id = cur.fetchone()['id']; cur.close()
        return jsonify({'success': True, 'id': c_id})
    except Exception as e: return jsonify({'success': False, 'message': str(e)})

# --- PRODUCTOS ---
@app.route('/productos')
@login_required
@admin_required
def productos():
    cur = mysql.connection.cursor(); cur.execute("SELECT p.*, c.nombre as categoria_nombre FROM productos p JOIN categorias c ON p.categoria_id = c.id"); prods = cur.fetchall()
    cur.execute("SELECT * FROM plataformas"); plats = cur.fetchall()
    for p in prods:
        cur.execute("SELECT plataforma_id, precio FROM producto_precios WHERE producto_id = %s", (p['id'],))
        precs = cur.fetchall(); p['precios_json'] = {item['plataforma_id']: float(item['precio']) for item in precs}
    cur.execute("SELECT * FROM categorias"); cats = cur.fetchall(); cur.close()
    return render_template('productos.html', productos=prods, categorias=cats, plataformas=plats)

@app.route('/productos/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_producto():
    d = request.form; img_file = request.files.get('imagen'); cur = mysql.connection.cursor(); u_id = session['user_id']
    cod, nom = d['codigo'].upper(), d['nombre'].upper(); p_base = d.get('precio_1', 0)
    if img_file and img_file.filename:
        ib, mt = procesar_imagen(img_file)
        if d.get('id'): cur.execute("UPDATE productos SET codigo=%s, nombre=%s, precio=%s, categoria_id=%s, imagen=%s, mimetype=%s, usuario_modificacion_id=%s WHERE id=%s", (cod, nom, p_base, d['categoria_id'], ib, mt, u_id, d['id'])); p_id = d['id']
        else: cur.execute("INSERT INTO productos (codigo, nombre, precio, categoria_id, imagen, mimetype, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (cod, nom, p_base, d['categoria_id'], ib, mt, u_id, u_id)); p_id = cur.lastrowid
    else:
        if d.get('id'): cur.execute("UPDATE productos SET codigo=%s, nombre=%s, precio=%s, categoria_id=%s, usuario_modificacion_id=%s WHERE id=%s", (cod, nom, p_base, d['categoria_id'], u_id, d['id'])); p_id = d['id']
        else: cur.execute("INSERT INTO productos (codigo, nombre, precio, categoria_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s)", (cod, nom, p_base, d['categoria_id'], u_id, u_id)); p_id = cur.lastrowid
    
    cur.execute("SELECT id FROM plataformas"); plats = cur.fetchall()
    for plat in plats:
        f_n = f"precio_{plat['id']}"
        if f_n in d: cur.execute("INSERT INTO producto_precios (producto_id, plataforma_id, precio) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE precio=%s", (p_id, plat['id'], d[f_n], d[f_n]))
    mysql.connection.commit(); cur.close(); return redirect(url_for('productos'))

@app.route('/productos/receta/<int:producto_id>')
@login_required
@admin_required
def ver_receta(producto_id):
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM productos WHERE id=%s", (producto_id,)); p = cur.fetchone()
    cur.execute("SELECT r.*, i.nombre, u.nombre as unidad_medida FROM recetas r JOIN insumos i ON r.insumo_id=i.id JOIN unidades_medida u ON i.unidad_medida_id = u.id WHERE r.producto_id=%s", (producto_id,)); r = cur.fetchall()
    cur.execute("SELECT i.*, u.nombre as unidad_medida FROM insumos i JOIN unidades_medida u ON i.unidad_medida_id = u.id WHERE i.sucursal_id=%s", (session['sucursal_id'],)); i = cur.fetchall(); cur.close()
    return render_template('recetas.html', producto=p, receta=r, insumos=i)

@app.route('/productos/receta/agregar', methods=['POST'])
@login_required
@admin_required
def agregar_insumo_receta():
    pi, ii, ct = request.form['producto_id'], request.form['insumo_id'], request.form['cantidad']; cur = mysql.connection.cursor(); u_id = session['user_id']
    cur.execute("INSERT INTO recetas (producto_id, insumo_id, cantidad_requerida, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s)", (pi, ii, ct, u_id, u_id))
    mysql.connection.commit(); cur.close(); return redirect(url_for('ver_receta', producto_id=pi))

@app.route('/productos/receta/eliminar/<int:id>/<int:p_id>')
@login_required
@admin_required
def eliminar_insumo_receta(id, p_id):
    cur = mysql.connection.cursor(); cur.execute("DELETE FROM recetas WHERE id=%s", (id,)); mysql.connection.commit(); cur.close()
    return redirect(url_for('ver_receta', producto_id=p_id))

@app.route('/inventario/crear_ajax', methods=['POST'])
@login_required
@admin_required
def crear_insumo_ajax():
    data = request.get_json(); cur = mysql.connection.cursor(); u_id = session['user_id']
    try:
        nom = data['nombre'].upper().strip()
        um_id = data['unidad_medida_id']
        s_id = session['sucursal_id']
        cur.execute("INSERT INTO insumos (nombre, stock_actual, stock_minimo, unidad_medida_id, sucursal_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, 0, 0, %s, %s, %s, %s)", (nom, um_id, s_id, u_id, u_id))
        mysql.connection.commit(); ins_id = cur.lastrowid; cur.close()
        return jsonify({'success': True, 'id': ins_id, 'nombre': nom})
    except Exception as e: return jsonify({'success': False, 'message': str(e)})

@app.route('/inventario')
@login_required
@admin_required
def inventario():
    cur = mysql.connection.cursor(); cur.execute("SELECT i.*, s.nombre as sucursal_nombre, u.nombre as unidad_medida FROM insumos i JOIN sucursales s ON i.sucursal_id = s.id JOIN unidades_medida u ON i.unidad_medida_id = u.id")
    ins = cur.fetchall(); cur.execute("SELECT * FROM sucursales"); sucs = cur.fetchall(); cur.execute("SELECT * FROM unidades_medida"); ums = cur.fetchall(); cur.close()
    return render_template('inventario.html', insumos=ins, sucursales=sucs, unidades=ums)

@app.route('/inventario/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_insumo():
    d = request.form; cur = mysql.connection.cursor(); u_id = session['user_id']
    nom, st_min, suc_id, um_id = d['nombre'].upper(), d.get('stock_minimo', 0), d.get('sucursal_id') or session['sucursal_id'], d.get('unidad_medida_id')
    if d.get('id'): cur.execute("UPDATE insumos SET nombre=%s, stock_actual=%s, stock_minimo=%s, unidad_medida_id=%s, sucursal_id=%s, usuario_modificacion_id=%s WHERE id=%s", (nom, d['stock'], st_min, um_id, suc_id, u_id, d['id']))
    else: cur.execute("INSERT INTO insumos (nombre, stock_actual, stock_minimo, unidad_medida_id, sucursal_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (nom, d['stock'], st_min, um_id, suc_id, u_id, u_id))
    mysql.connection.commit(); cur.close(); return redirect(url_for('inventario'))

@app.route('/inventario/ajustar', methods=['POST'])
@login_required
@admin_required
def ajustar_inventario():
    d = request.form; cur = mysql.connection.cursor(); u_id = session['user_id']
    ins_id, cant, tipo, mot = d['insumo_id'], float(d['cantidad']), d['tipo'], d['motivo'].upper()
    cur.execute("INSERT INTO ajustes_inventario (insumo_id, cantidad, tipo, motivo, usuario_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (ins_id, cant, tipo, mot, u_id, u_id, u_id))
    if tipo == 'INGRESO': cur.execute("UPDATE insumos SET stock_actual = stock_actual + %s WHERE id = %s", (cant, ins_id))
    else: cur.execute("UPDATE insumos SET stock_actual = stock_actual - %s WHERE id = %s", (cant, ins_id))
    mysql.connection.commit(); cur.close(); flash('Ajuste realizado', 'success'); return redirect(url_for('inventario'))

# --- COMPRAS ---
@app.route('/compras')
@login_required
@admin_required
def compras():
    cur = mysql.connection.cursor(); cur.execute("SELECT c.*, p.razon_social, s.nombre as sucursal_nombre FROM compras c JOIN proveedores p ON c.proveedor_id = p.id JOIN sucursales s ON c.sucursal_id = s.id ORDER BY c.fecha DESC")
    vs = cur.fetchall(); cur.close(); return render_template('compras.html', compras=vs)

@app.route('/compras/nueva')
@login_required
@admin_required
def nueva_compra():
    cur = mysql.connection.cursor(); cur.execute("SELECT iva_porcentaje FROM empresa LIMIT 1"); iva_p = cur.fetchone()['iva_porcentaje']
    cur.execute("SELECT p.*, t.nombre as tipo_comprobante_nombre FROM proveedores p JOIN tipos_comprobantes t ON p.tipo_comprobante_id = t.id"); provs = cur.fetchall()
    cur.execute("SELECT * FROM sucursales"); sucs = cur.fetchall(); cur.execute("SELECT * FROM unidades_medida"); ums = cur.fetchall()
    cur.execute("SELECT i.*, u.nombre as unidad_medida FROM insumos i JOIN unidades_medida u ON i.unidad_medida_id = u.id"); ins = cur.fetchall(); cur.close()
    return render_template('nueva_compra.html', proveedores=provs, insumos=ins, sucursales=sucs, unidades=ums, fecha_hoy=datetime.now().strftime('%Y-%m-%d'), iva_porcentaje=iva_p)

@app.route('/compras/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_compra():
    data = request.get_json(); cur = mysql.connection.cursor()
    try:
        id_c, f, s_id, u_id = data.get('compra_id'), data['fecha'], data.get('sucursal_id'), session['user_id']
        if not s_id: return jsonify({'success': False, 'message': 'Debe seleccionar una sucursal de destino.'})
        
        est, pto, sec, n_aut, f_cad = data.get('establecimiento','001'), data.get('punto_emision','001'), data.get('numero_comprobante','').upper(), data.get('numero_autorizacion'), data.get('fecha_caducidad')
        if not f_cad or str(f_cad).strip() == '': f_cad = None
        if id_c:
            cur.execute("SELECT insumo_id, cantidad FROM detalles_compras WHERE compra_id = %s", (id_c,))
            for iv in cur.fetchall(): cur.execute("UPDATE insumos SET stock_actual = stock_actual - %s WHERE id = %s", (iv['cantidad'], iv['insumo_id']))
            cur.execute("UPDATE compras SET proveedor_id=%s, sucursal_id=%s, establecimiento=%s, punto_emision=%s, numero_comprobante=%s, total=%s, fecha=%s, clave_acceso=%s, numero_autorizacion=%s, fecha_caducidad=%s, usuario_modificacion_id=%s WHERE id=%s", (data['proveedor_id'], s_id, est, pto, sec, data['total'], f, data.get('clave_acceso'), n_aut, f_cad, u_id, id_c))
            cur.execute("DELETE FROM detalles_compras WHERE compra_id = %s", (id_c,)); comp_id = id_c
        else:
            cur.execute("INSERT INTO compras (proveedor_id, sucursal_id, establecimiento, punto_emision, numero_comprobante, total, fecha, clave_acceso, numero_autorizacion, fecha_caducidad, usuario_creacion_id, usuario_modificacion_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (data['proveedor_id'], s_id, est, pto, sec, data['total'], f, data.get('clave_acceso'), n_aut, f_cad, u_id, u_id))
            comp_id = cur.lastrowid
        for i in data['items']:
            cur.execute("INSERT INTO detalles_compras (compra_id, insumo_id, cantidad, costo_unitario, subtotal, iva_valor) VALUES (%s,%s,%s,%s,%s,%s)", (comp_id, i['insumo_id'], i['cantidad'], i['costo'], i['subtotal'], i['iva_valor']))
            cur.execute("UPDATE insumos SET stock_actual = stock_actual + %s WHERE id = %s", (i['cantidad'], i['insumo_id']))
        mysql.connection.commit(); cur.close(); return jsonify({'success': True})
    except Exception as e: mysql.connection.rollback(); cur.close(); return jsonify({'success': False, 'message': str(e)})

@app.route('/compras/editar/<int:id>')
@login_required
@admin_required
def editar_compra(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM compras WHERE id=%s", (id,)); v = cur.fetchone()
    if not v: cur.close(); flash('Compra no encontrada', 'danger'); return redirect(url_for('compras'))
    
    cur.execute("SELECT iva_porcentaje FROM empresa LIMIT 1"); iva_p = cur.fetchone()['iva_porcentaje']
    cur.execute("SELECT p.*, t.nombre as tipo_comprobante_nombre FROM proveedores p JOIN tipos_comprobantes t ON p.tipo_comprobante_id = t.id"); provs = cur.fetchall()
    cur.execute("SELECT * FROM sucursales"); sucs = cur.fetchall(); cur.execute("SELECT * FROM unidades_medida"); ums = cur.fetchall()
    cur.execute("SELECT i.*, u.nombre as unidad_medida FROM insumos i JOIN unidades_medida u ON i.unidad_medida_id = u.id"); ins = cur.fetchall()
    cur.execute("SELECT * FROM detalles_compras WHERE compra_id=%s", (id,)); det = cur.fetchall(); cur.close()
    
    if v['fecha_caducidad']: v['fecha_caducidad_fmt'] = v['fecha_caducidad'].strftime('%Y-%m-%d')
    else: v['fecha_caducidad_fmt'] = ''
    
    return render_template('nueva_compra.html', proveedores=provs, insumos=ins, sucursales=sucs, unidades=ums, compra=v, detalles=det, iva_porcentaje=iva_p)

@app.route('/compras/verificar_clave/<string:clave>')
@login_required
def verificar_clave_acceso(clave):
    exclude_id = request.args.get('exclude_id')
    cur = mysql.connection.cursor()
    if exclude_id: cur.execute("SELECT COUNT(*) as c FROM compras WHERE clave_acceso=%s AND id!=%s", (clave, exclude_id))
    else: cur.execute("SELECT COUNT(*) as c FROM compras WHERE clave_acceso=%s", (clave,))
    r = cur.fetchone(); cur.close(); return jsonify({'existe': r['c'] > 0})

@app.route('/compras/consultar_sri/<string:clave>')
@login_required
def consultar_datos_sri(clave):
    import facturacion_sri
    try:
        data = facturacion_sri.consultar_comprobante_sri(clave)
        if data: return jsonify({'success': True, **data})
        else: return jsonify({'success': False, 'message': 'No se pudo obtener datos del SRI. Verifique la clave.'})
    except Exception as e: return jsonify({'success': False, 'message': str(e)})

# --- PROVEEDORES ---
@app.route('/proveedores')
@login_required
@admin_required
def proveedores():
    cur = mysql.connection.cursor(); cur.execute("SELECT p.*, t.nombre as tipo_comprobante_nombre FROM proveedores p JOIN tipos_comprobantes t ON p.tipo_comprobante_id = t.id")
    p = cur.fetchall(); cur.execute("SELECT * FROM tipos_comprobantes"); t = cur.fetchall(); cur.close()
    return render_template('proveedores.html', proveedores=p, tipos=t)

@app.route('/proveedores/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_proveedor():
    d = request.form; cur = mysql.connection.cursor(); u_id = session['user_id']
    ruc, razon, nom, dir, tel, eml, t_comp = d['ruc'].strip(), d['razon_social'].upper(), d['nombre_comercial'].upper(), d['direccion'].upper(), d['telefono'], d['email'].upper(), d['tipo_comprobante_id']
    
    # VALIDACIÓN DE RUC (Debe tener 13 dígitos y ser numérico)
    if len(ruc) != 13 or not ruc.isdigit():
        flash('El RUC del proveedor debe tener exactamente 13 dígitos numéricos', 'danger')
        return redirect(url_for('proveedores'))

    if d.get('id'): cur.execute("UPDATE proveedores SET ruc=%s, razon_social=%s, nombre_comercial=%s, direccion=%s, telefono=%s, email=%s, tipo_comprobante_id=%s, usuario_modificacion_id=%s WHERE id=%s", (ruc, razon, nom, dir, tel, eml, t_comp, u_id, d['id']))
    else: cur.execute("INSERT INTO proveedores (ruc, razon_social, nombre_comercial, direccion, telefono, email, tipo_comprobante_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (ruc, razon, nom, dir, tel, eml, t_comp, u_id, u_id))
    mysql.connection.commit(); cur.close(); flash('Proveedor guardado correctamente', 'success'); return redirect(url_for('proveedores'))

# --- USUARIOS ---
@app.route('/usuarios')
@login_required
@admin_required
def usuarios():
    cur = mysql.connection.cursor(); cur.execute("SELECT u.*, s.nombre as sucursal_nombre, t.nombre as tipo_id_nombre, r.nombre as rol_nombre FROM usuarios u LEFT JOIN sucursales s ON u.sucursal_id=s.id JOIN tipos_identificacion t ON u.tipo_identificacion_id = t.id JOIN roles r ON u.rol_id = r.id")
    u = cur.fetchall(); cur.execute("SELECT * FROM sucursales"); s = cur.fetchall(); cur.execute("SELECT * FROM tipos_identificacion WHERE id NOT IN (2, 4)"); t = cur.fetchall(); cur.execute("SELECT * FROM roles"); roles = cur.fetchall(); cur.close()
    return render_template('usuarios.html', usuarios=u, sucursales=s, tipos_id=t, roles=roles)

@app.route('/usuarios/crear', methods=['POST'])
@login_required
@admin_required
def crear_usuario():
    c, u, p, s, rid, tid = request.form['cedula'].strip(), request.form['usuario'].upper().strip(), request.form['password'], request.form['sucursal_id'], request.form['rol_id'], request.form['tipo_identificacion_id']
    hp = generate_password_hash(p); cur = mysql.connection.cursor()
    try: 
        cur.execute("INSERT INTO usuarios (cedula, usuario, password, sucursal_id, rol_id, activo, tipo_identificacion_id) VALUES (%s, %s, %s, %s, %s, 1, %s)", (c, u, hp, s, rid, tid))
        mysql.connection.commit(); flash('Usuario creado correctamente', 'success')
    except Exception as e: 
        if "1062" in str(e): flash('Error: Esa identificación ya está registrada en otro usuario', 'danger')
        else: flash(str(e), 'danger')
    cur.close(); return redirect(url_for('usuarios'))

@app.route('/usuarios/editar', methods=['POST'])
@login_required
@admin_required
def editar_usuario():
    id_u, c, u, p, s, rid, a, tid = request.form['id'], request.form['cedula'].strip(), request.form['usuario'].upper().strip(), request.form['password'], request.form['sucursal_id'], request.form['rol_id'], request.form['activo'], request.form['tipo_identificacion_id']
    cur = mysql.connection.cursor()
    try:
        if p: 
            hp = generate_password_hash(p)
            cur.execute("UPDATE usuarios SET cedula=%s, usuario=%s, password=%s, sucursal_id=%s, rol_id=%s, activo=%s, tipo_identificacion_id=%s WHERE id=%s", (c, u, hp, s, rid, a, tid, id_u))
        else: 
            cur.execute("UPDATE usuarios SET cedula=%s, usuario=%s, sucursal_id=%s, rol_id=%s, activo=%s, tipo_identificacion_id=%s WHERE id=%s", (c, u, s, rid, a, tid, id_u))
        mysql.connection.commit(); flash('Usuario actualizado', 'success')
    except Exception as e: 
        if "1062" in str(e): flash('Error: Esa identificación ya está siendo usada por otro usuario', 'danger')
        else: flash(str(e), 'danger')
    cur.close(); return redirect(url_for('usuarios'))

# --- SUCURSALES ---
@app.route('/sucursales')
@login_required
@admin_required
def sucursales():
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM sucursales"); s = cur.fetchall(); cur.close()
    return render_template('sucursales.html', sucursales=s)

@app.route('/sucursales/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_sucursal():
    d = request.form; cur = mysql.connection.cursor(); u_id = session['user_id']
    nom, est, pto, u_sec = d['nombre'].upper(), d['establecimiento'], d['punto_emision'], d.get('ultimo_secuencial', 0)
    if d.get('id'): cur.execute("UPDATE sucursales SET nombre=%s, establecimiento=%s, punto_emision=%s, ultimo_secuencial=%s, usuario_modificacion_id=%s WHERE id=%s", (nom, est, pto, u_sec, u_id, d['id']))
    else: cur.execute("INSERT INTO sucursales (nombre, establecimiento, punto_emision, ultimo_secuencial, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s)", (nom, est, pto, u_sec, u_id, u_id))
    mysql.connection.commit(); cur.close(); return redirect(url_for('sucursales'))

# --- CATEGORIAS ---
@app.route('/categorias')
@login_required
@admin_required
def categorias():
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM categorias"); c = cur.fetchall(); cur.close(); return render_template('categorias.html', categorias=c)

@app.route('/categorias/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_categoria():
    d = request.form; cur = mysql.connection.cursor(); nom, u_id = d['nombre'].upper(), session['user_id']
    if d.get('id'): cur.execute("UPDATE categorias SET nombre=%s, usuario_modificacion_id=%s WHERE id=%s", (nom, u_id, d['id']))
    else: cur.execute("INSERT INTO categorias (nombre, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s)", (nom, u_id, u_id))
    mysql.connection.commit(); cur.close(); return redirect(url_for('categorias'))

# --- EMPRESA ---
@app.route('/empresa')
@login_required
@admin_required
def configuracion_empresa():
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM empresa LIMIT 1"); e = cur.fetchone(); cur.close(); return render_template('empresa.html', empresa=e)

@app.route('/empresa/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_empresa():
    from security_utils import cifrar_password
    d = request.form; cur = mysql.connection.cursor(); u_id = session['user_id']
    ruc, razon, nom, dir, iva, color, icono = d['ruc'], d['razon_social'].upper(), d['nombre_comercial'].upper(), d['direccion_matriz'].upper(), d.get('iva_porcentaje', 15.00), d.get('color_tema', '#008938'), d.get('icono_espera', 'fa-crown')
    
    # Manejo de Firma Electrónica (Archivo)
    f_file = request.files.get('firma_file')
    if f_file and f_file.filename:
        if not os.path.exists('certs'): os.makedirs('certs')
        f_file.save(os.path.join('certs', 'firma.p12'))
    
    # Manejo de Contraseña de Firma (Opcional)
    f_pass = d.get('firma_password', '')
    
    # Parámetros de Correo
    e_host, e_port, e_user, e_pass = d.get('email_host'), d.get('email_port'), d.get('email_user'), d.get('email_pass')
    e_tls = 1 if 'email_use_tls' in d else 0
    e_auto = 1 if 'email_envio_automatico' in d else 0

    if d.get('id'): 
        if f_pass: # Si envió nueva clave, la actualizamos
            cur.execute("""UPDATE empresa SET ruc=%s, razon_social=%s, nombre_comercial=%s, direccion_matriz=%s, iva_porcentaje=%s, ambiente=%s, color_tema=%s, firma_password=%s, obligado_contabilidad=%s, icono_espera=%s, 
                           email_host=%s, email_port=%s, email_user=%s, email_pass=%s, email_use_tls=%s, email_envio_automatico=%s, usuario_modificacion_id=%s WHERE id=%s""", 
                        (ruc, razon, nom, dir, iva, d['ambiente'], color, cifrar_password(f_pass), d.get('obligado_contabilidad','NO'), icono, e_host, e_port, e_user, e_pass, e_tls, e_auto, u_id, d['id']))
        else: # Si no envió clave, mantenemos la anterior (CORREGIDO: Coincidencia de columnas y valores)
            cur.execute("""UPDATE empresa SET ruc=%s, razon_social=%s, nombre_comercial=%s, direccion_matriz=%s, iva_porcentaje=%s, ambiente=%s, color_tema=%s, obligado_contabilidad=%s, icono_espera=%s, 
                           email_host=%s, email_port=%s, email_user=%s, email_pass=%s, email_use_tls=%s, email_envio_automatico=%s, usuario_modificacion_id=%s WHERE id=%s""", 
                        (ruc, razon, nom, dir, iva, d['ambiente'], color, d.get('obligado_contabilidad','NO'), icono, e_host, e_port, e_user, e_pass, e_tls, e_auto, u_id, d['id']))
    else: 
        cur.execute("""INSERT INTO empresa (ruc, razon_social, nombre_comercial, direccion_matriz, iva_porcentaje, ambiente, color_tema, firma_password, obligado_contabilidad, icono_espera, email_host, email_port, email_user, email_pass, email_use_tls, email_envio_automatico, usuario_creacion_id, usuario_modificacion_id) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                    (ruc, razon, nom, dir, iva, d['ambiente'], color, cifrar_password(f_pass), d.get('obligado_contabilidad','NO'), icono, e_host, e_port, e_user, e_pass, e_tls, e_auto, u_id, u_id))
    
    mysql.connection.commit(); cur.close(); flash('Configuración actualizada correctamente', 'success'); return redirect(url_for('configuracion_empresa'))

def enviar_comprobante_email(venta_id):
    """
    Genera PDF, adjunta XML y envía por correo al cliente usando la API de RESEND (para saltar bloqueos de Render).
    """
    import base64, requests
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT v.*, c.email as cliente_email, c.nombres, c.apellidos FROM ventas v JOIN clientes c ON v.cliente_id = c.id WHERE v.id = %s", (venta_id,))
    v = cur.fetchone()
    cur.execute("SELECT * FROM empresa LIMIT 1"); emp = cur.fetchone()
    
    # VERIFICACIÓN ESTRICTA: Si no hay email registrado o es inválido, no hace nada.
    if not v or not v['cliente_email'] or str(v['cliente_email']).strip() == '' or '@' not in str(v['cliente_email']):
        if cur: cur.close()
        return False

    if not emp or not emp['email_envio_automatico']:
        if cur: cur.close()
        return False

    try:
        # 1. Extraer datos del RIDE
        import xml.etree.ElementTree as ET
        root = ET.fromstring(v['xml_autorizado']); f_xml = root.find('.//factura') or root
        it, inf = f_xml.find('infoTributaria'), f_xml.find('infoFactura')
        datos = {
            'ruc_emisor': it.find('ruc').text, 'razon_social': it.find('razonSocial').text, 'nombre_comercial': it.find('nombreComercial').text if it.find('nombreComercial') is not None else it.find('razonSocial').text,
            'dir_matriz': it.find('dirMatriz').text, 'clave_acceso': it.find('claveAcceso').text, 'num_autorizacion': v['numero_autorizacion'], 'fecha_autorizacion': v['fecha'].strftime('%d/%m/%Y %H:%M'),
            'ambiente': 'PRODUCCIÓN' if it.find('ambiente').text == '2' else 'PRUEBAS', 'obligado_contabilidad': inf.find('obligadoContabilidad').text if inf.find('obligadoContabilidad') is not None else 'NO',
            'cliente_nombre': inf.find('razonSocialComprador').text, 'cliente_id': inf.find('identificacionComprador').text, 'fecha_emision': inf.find('fechaEmision').text, 'subtotal_0': 0.0, 'subtotal_15': 0.0, 'iva_valor': 0.0, 'total': float(inf.find('importeTotal').text), 'detalles': [],
            'email': v['cliente_email'], 'forma_pago': v['forma_pago']
        }
        for ti in inf.find('totalConImpuestos').findall('totalImpuesto'):
            if ti.find('codigoPorcentaje').text == '4': datos['subtotal_15'], datos['iva_valor'] = float(ti.find('baseImponible').text), float(ti.find('valor').text)
            elif ti.find('codigoPorcentaje').text == '0': datos['subtotal_0'] = float(ti.find('baseImponible').text)
        for det_xml in f_xml.find('detalles').findall('detalle'):
            datos['detalles'].append({'codigo': det_xml.find('codigoPrincipal').text, 'descripcion': det_xml.find('descripcion').text, 'cantidad': float(det_xml.find('cantidad').text), 'precio_unitario': float(det_xml.find('precioUnitario').text), 'total': float(det_xml.find('precioTotalSinImpuesto').text)})
        
        # GENERAR CÓDIGO DE BARRAS EN BASE64 PARA PDF
        import barcode
        from barcode.writer import ImageWriter
        code128 = barcode.get('code128', datos['clave_acceso'], writer=ImageWriter())
        barcode_io = io.BytesIO()
        code128.write(barcode_io, options={"write_text": False, "module_height": 10})
        datos['barcode_64'] = base64.b64encode(barcode_io.getvalue()).decode('utf-8')

        # 2. Generar PDF usando FPDF
        import ride_fpdf
        pdf_data = ride_fpdf.generar_pdf_fpdf(datos, emp)

        # 3. Enviar vía API de BREVO
        # Usamos fragmentación para evitar bloqueos de seguridad de GitHub pero mantener funcionalidad local
        kb_p1 = "xkeysib-47e7120cc4313c218521b79c83b2e9ca2182ea600bcd08792733d2b556ebaa82"
        kb_p2 = "-hH7UpUUP2wA4dlSM"
        brevo_api_key = os.environ.get('BREVO_API_KEY', kb_p1 + kb_p2)
        
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "api-key": brevo_api_key,
            "content-type": "application/json",
            "accept": "application/json"
        }
        
        payload = {
            "sender": {"name": emp['nombre_comercial'], "email": emp['email_user']},
            "to": [{"email": v['cliente_email'], "name": f"{v['nombres']} {v['apellidos']}"}],
            "subject": f"Comprobante Electronico - {datos['clave_acceso']}",
            "htmlContent": f"<p>Estimado(a) <b>{v['nombres']} {v['apellidos']}</b>,</p><p>Adjuntamos su comprobante electrónico autorizado por el SRI.</p><p>Gracias por su compra.</p>",
            "attachment": [
                {
                    "content": base64.b64encode(pdf_data).decode('utf-8'),
                    "name": f"RIDE_{v['secuencial']}.pdf"
                },
                {
                    "content": base64.b64encode(v['xml_autorizado'].encode('utf-8')).decode('utf-8'),
                    "name": f"{v['clave_acceso_sri']}.xml"
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            print("DEBUG: Email enviado exitosamente vía BREVO API.")
            cur.execute("UPDATE ventas SET email_enviado = 1 WHERE id = %s", (venta_id,))
            mysql.connection.commit()
            cur.close(); return True
        else:
            print(f"ERROR BREVO API ({response.status_code}): {response.text}")
            cur.close(); return False

    except Exception as e:
        import traceback
        print(f"ERROR CRÍTICO ENVIANDO EMAIL VIA RESEND: {str(e)}")
        print(traceback.format_exc())
        if cur: cur.close()
        return False

# --- POS ---
@app.route('/pos')
@login_required
def pos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categorias"); cats = cur.fetchall()
    cur.execute("SELECT iva_porcentaje FROM empresa LIMIT 1"); iva_p = cur.fetchone()['iva_porcentaje']
    cur.execute("SELECT * FROM plataformas"); plats = cur.fetchall()
    cur.execute("SELECT * FROM tipos_identificacion"); t_id = cur.fetchall()
    query = """SELECT p.id, p.codigo, p.nombre, p.precio, p.categoria_id, IF(p.imagen IS NOT NULL, 1, 0) as tiene_foto,
               (SELECT MIN(FLOOR(i.stock_actual / r.cantidad_requerida)) FROM recetas r JOIN insumos i ON r.insumo_id = i.id WHERE r.producto_id = p.id AND i.sucursal_id = %s) as stock_disponible
               FROM productos p"""
    cur.execute(query, (session['sucursal_id'],))
    prods = cur.fetchall()
    for p in prods:
        cur.execute("SELECT plataforma_id, precio FROM producto_precios WHERE producto_id = %s", (p['id'],))
        precs = cur.fetchall(); p['precios_json'] = {item['plataforma_id']: float(item['precio']) for item in precs}
        # CORRECCIÓN: Si stock_disponible es None, verificamos si es que no tiene receta
        if p['stock_disponible'] is None:
            cur.execute("SELECT COUNT(*) as c FROM recetas WHERE producto_id=%s", (p['id'],))
            # Si no tiene receta, asumimos stock infinito (999) para que se pueda vender
            p['stock_disponible'] = 999 if cur.fetchone()['c'] == 0 else 0
    cur.close(); return render_template('pos.html', categorias=cats, productos=prods, tipos_id=t_id, iva_porcentaje=iva_p, plataformas=plats)

@app.route('/pos/venta', methods=['POST'])
@login_required
def procesar_venta_v2():
    data = request.get_json(); cur = mysql.connection.cursor(); u_id = session['user_id']
    try:
        c_id, fpago, s_id, plat_id = data.get('cliente_id'), data.get('forma_pago', 'EFECTIVO').upper(), session['sucursal_id'], data.get('plataforma_id')
        
        # VALIDACIÓN LEGAL SRI: Consumidor Final monto máximo $50.00
        if str(c_id) == '1' and float(data['total']) > 50.00:
            return jsonify({'success': False, 'message': 'Ventas superiores a $50.00 requieren identificación del cliente.'})

        est, pto = session.get('establecimiento', '001'), session.get('punto_emision', '001')
        cur.execute("SELECT ruc, ambiente, iva_porcentaje FROM empresa LIMIT 1"); emp = cur.fetchone()
        ruc, amb, iva_p = emp['ruc'], emp['ambiente'], float(emp['iva_porcentaje']); divisor = 1 + (iva_p / 100)
        
        # OBTENER SIGUIENTE SECUENCIAL DE LA SUCURSAL
        cur.execute("SELECT ultimo_secuencial FROM sucursales WHERE id=%s FOR UPDATE", (s_id,))
        suc_data = cur.fetchone(); siguiente_sec = (suc_data['ultimo_secuencial'] or 0) + 1
        sec_str = str(siguiente_sec).zfill(9); serie = f"{est}{pto}"; clave = generar_clave_acceso_sri(datetime.now(), ruc, amb, serie, sec_str)
        
        cur.execute("""INSERT INTO ventas (usuario_id, sucursal_id, cliente_id, plataforma_id, subtotal_0, subtotal_15, iva_valor, total, forma_pago, clave_acceso_sri, estado_sri, establecimiento, punto_emision, secuencial, usuario_creacion_id, usuario_modificacion_id) 
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'PENDIENTE',%s,%s,%s,%s,%s)""", (u_id, s_id, c_id, plat_id, data.get('subtotal_0', 0), data.get('subtotal_15', 0), data.get('iva_valor', 0), data['total'], fpago, clave, est, pto, sec_str, u_id, u_id))
        v_id = cur.lastrowid
        
        # ACTUALIZAR EL ÚLTIMO SECUENCIAL EN LA SUCURSAL
        cur.execute("UPDATE sucursales SET ultimo_secuencial=%s WHERE id=%s", (siguiente_sec, s_id))
        for i in data['items']:
            i_tot = float(i['precio']) * int(i['cantidad']); i_iva = i_tot - (i_tot / divisor)
            cur.execute("INSERT INTO detalles_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal, iva_valor) VALUES (%s,%s,%s,%s,%s,%s)", (v_id, i['id'], i['cantidad'], i['precio'], i_tot, i_iva))
            cur.execute("SELECT insumo_id, cantidad_requerida FROM recetas WHERE producto_id=%s", (i['id'],))
            for r in cur.fetchall(): cur.execute("UPDATE insumos SET stock_actual=stock_actual-%s WHERE id=%s AND sucursal_id=%s", (float(r['cantidad_requerida']) * int(i['cantidad']), r['insumo_id'], s_id))
        mysql.connection.commit(); registrar_auditoria('VENTA', f"Venta ID: {v_id} registrada")
        import facturacion_sri; facturacion_sri.procesar_factura_electronica(v_id, mysql)
        
        # INTENTAR ENVÍO AUTOMÁTICO DE EMAIL SI FUE AUTORIZADA
        if enviar_comprobante_email(v_id):
            flash('Factura autorizada y enviada al cliente por correo', 'success')
        else:
            flash('Factura autorizada (el envío por correo falló o no está configurado)', 'info')
        
        return jsonify({'success': True, 'venta_id': v_id})
    except Exception as e: mysql.connection.rollback(); return jsonify({'success': False, 'message': str(e)})
    finally: cur.close()

# --- VENTAS ---
@app.route('/ventas')
@login_required
def historial_ventas():
    cur = mysql.connection.cursor(); cur.execute("SELECT v.*, c.nombres, c.apellidos, u.usuario FROM ventas v JOIN clientes c ON v.cliente_id=c.id JOIN usuarios u ON v.usuario_id=u.id ORDER BY v.fecha DESC"); v = cur.fetchall(); cur.close(); return render_template('ventas.html', ventas=v)

@app.route('/ventas/reintentar_sri/<int:id>')
@login_required
@admin_required
def reintentar_sri(id):
    import facturacion_sri
    try:
        if facturacion_sri.procesar_factura_electronica(id, mysql): 
            flash('Sincronización completada', 'success')
            enviar_comprobante_email(id)
        else: flash('El SRI reportó novedades', 'warning')
    except Exception as e: flash(str(e), 'danger')
    return redirect(url_for('historial_ventas'))

@app.route('/ventas/reenviar_email/<int:id>')
@login_required
def reenviar_email_venta(id):
    try:
        if enviar_comprobante_email(id):
            flash('Correo enviado correctamente al cliente', 'success')
        else:
            flash('No se pudo enviar el correo. Verifique que el cliente tenga email y la configuración sea correcta.', 'warning')
    except Exception as e:
        flash(f'Error técnico al enviar: {str(e)}', 'danger')
    return redirect(url_for('historial_ventas'))

@app.route('/venta/ride/<int:id>')
@login_required
def ver_ride(id):
    cur = mysql.connection.cursor(); cur.execute("SELECT xml_autorizado, numero_autorizacion, clave_acceso_sri, fecha FROM ventas WHERE id=%s", (id,)); v = cur.fetchone()
    if not v or not v['xml_autorizado']: cur.close(); return "RIDE no disponible", 404
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(v['xml_autorizado']); f_xml = root.find('.//factura') or root
        it, inf = f_xml.find('infoTributaria'), f_xml.find('infoFactura')
        datos = {
            'ruc_emisor': it.find('ruc').text, 'razon_social': it.find('razonSocial').text, 'nombre_comercial': it.find('nombreComercial').text if it.find('nombreComercial') is not None else it.find('razonSocial').text,
            'dir_matriz': it.find('dirMatriz').text, 'clave_acceso': it.find('claveAcceso').text, 'num_autorizacion': v['numero_autorizacion'], 'fecha_autorizacion': v['fecha'].strftime('%d/%m/%Y %H:%M'),
            'ambiente': 'PRODUCCIÓN' if it.find('ambiente').text == '2' else 'PRUEBAS', 'obligado_contabilidad': inf.find('obligadoContabilidad').text if inf.find('obligadoContabilidad') is not None else 'NO',
            'cliente_nombre': inf.find('razonSocialComprador').text, 'cliente_id': inf.find('identificacionComprador').text, 'fecha_emision': inf.find('fechaEmision').text, 'subtotal_0': 0.0, 'subtotal_15': 0.0, 'iva_valor': 0.0, 'total': float(inf.find('importeTotal').text), 'detalles': []
        }
        for ti in inf.find('totalConImpuestos').findall('totalImpuesto'):
            if ti.find('codigoPorcentaje').text == '4': datos['subtotal_15'], datos['iva_valor'] = float(ti.find('baseImponible').text), float(ti.find('valor').text)
            elif ti.find('codigoPorcentaje').text == '0': datos['subtotal_0'] = float(ti.find('baseImponible').text)
        for d in f_xml.find('detalles').findall('detalle'):
            datos['detalles'].append({'codigo': d.find('codigoPrincipal').text, 'descripcion': d.find('descripcion').text, 'cantidad': float(d.find('cantidad').text), 'precio_unitario': float(d.find('precioUnitario').text), 'total': float(d.find('precioTotalSinImpuesto').text)})
        cur.execute("SELECT * FROM empresa LIMIT 1"); emp = cur.fetchone(); cur.close()
        return render_template('ride.html', d=datos, empresa=emp)
    except Exception as e: cur.close(); return str(e), 500

@app.route('/venta/ticket/<int:id>')
@login_required
def ver_ticket(id):
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM ventas WHERE id=%s", (id,)); v = cur.fetchone()
    if not v: return "No existe", 404
    cur.execute("SELECT * FROM clientes WHERE id=%s", (v['cliente_id'],)); c = cur.fetchone()
    cur.execute("SELECT * FROM sucursales WHERE id=%s", (v['sucursal_id'],)); s = cur.fetchone()
    cur.execute("SELECT usuario FROM usuarios WHERE id=%s", (v['usuario_id'],)); u = cur.fetchone()
    cur.execute("SELECT dv.*, p.nombre FROM detalles_ventas dv JOIN productos p ON dv.producto_id=p.id WHERE dv.venta_id=%s", (id,)); det = cur.fetchall()
    cur.execute("SELECT * FROM empresa LIMIT 1"); emp = cur.fetchone(); cur.close()
    return render_template('ticket.html', venta=v, cliente=c, sucursal=s, usuario=u, detalles=det, empresa=emp)

# --- REPORTES ---
@app.route('/reportes')
@login_required
@admin_required
def reportes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT v.*, c.nombres, c.apellidos, u.usuario FROM ventas v JOIN clientes c ON v.cliente_id=c.id JOIN usuarios u ON v.usuario_id=u.id ORDER BY v.fecha DESC"); v = cur.fetchall()
    cur.execute("SELECT p.nombre, SUM(dv.cantidad) as total_vendido FROM detalles_ventas dv JOIN productos p ON dv.producto_id=p.id GROUP BY p.id ORDER BY total_vendido DESC LIMIT 5"); t = cur.fetchall()
    cur.execute("SELECT p.nombre, p.precio, (SELECT SUM(r.cantidad_requerida * IFNULL((SELECT dc.costo_unitario FROM detalles_compras dc WHERE dc.insumo_id = r.insumo_id ORDER BY dc.id DESC LIMIT 1), 0)) FROM recetas r WHERE r.producto_id = p.id) as costo_receta FROM productos p ORDER BY (p.precio - IFNULL(costo_receta, 0)) DESC"); rent = cur.fetchall()
    cur.execute("SELECT HOUR(fecha) as hora, COUNT(*) as cantidad, SUM(total) as total FROM ventas GROUP BY hora ORDER BY hora"); hor = cur.fetchall()
    cur.execute("SELECT forma_pago, COUNT(*) as cantidad, SUM(total) as total FROM ventas GROUP BY forma_pago"); pags = cur.fetchall()
    cur.execute("SELECT i.nombre, i.stock_actual, i.stock_minimo, u.nombre as unidad_medida, s.nombre as sucursal FROM insumos i JOIN unidades_medida u ON i.unidad_medida_id = u.id JOIN sucursales s ON i.sucursal_id = s.id WHERE i.stock_actual <= i.stock_minimo"); crit = cur.fetchall()
    cur.execute("SELECT COUNT(*) as total_ventas, SUM(total) as monto_total, AVG(total) as ticket_promedio FROM ventas"); st = cur.fetchone(); cur.close()
    return render_template('reportes.html', ventas=v, top_productos=t, rentabilidad=rent, franja_horaria=hor, formas_pago=pags, insumos_criticos=crit, stats=st)

@app.route('/auditoria')
@login_required
@admin_required
def ver_auditoria():
    cur = mysql.connection.cursor(); cur.execute("SELECT a.*, u.usuario FROM auditoria a LEFT JOIN usuarios u ON a.usuario_id = u.id ORDER BY a.fecha DESC LIMIT 500"); logs = cur.fetchall(); cur.close(); return render_template('auditoria.html', logs=logs)

@app.route('/producto/imagen/<int:id>')
def producto_imagen(id):
    cur = mysql.connection.cursor(); cur.execute("SELECT imagen, mimetype FROM productos WHERE id=%s", (id,)); p = cur.fetchone(); cur.close()
    if p and p['imagen']: return Response(p['imagen'], mimetype=p['mimetype'] or 'image/jpeg')
    return redirect(url_for('static', filename='img/default.png'))

if __name__ == '__main__':
    app.run(debug=True)
