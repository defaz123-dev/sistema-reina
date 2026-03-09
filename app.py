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
def obtener_sesion_caja_activa(sucursal_id, usuario_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM sesiones_caja WHERE sucursal_id = %s AND usuario_id = %s AND estado = 'ABIERTA' ORDER BY id DESC LIMIT 1", (sucursal_id, usuario_id))
        s = cur.fetchone()
        cur.close()
        return s['id'] if s else None
    except: return None

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
        e = cur.fetchone()
        cur.execute("SELECT * FROM cat_tarjetas WHERE activo = 1 ORDER BY nombre")
        tarjetas = cur.fetchall()
        cur.close()
        return dict(config_empresa=e, cat_tarjetas=tarjetas) if e else dict(config_empresa={'nombre_comercial': 'SISTEMA REINA', 'color_tema': '#008938', 'icono_espera': 'fa-crown'}, cat_tarjetas=tarjetas)
    except: return dict(config_empresa={'nombre_comercial': 'SISTEMA REINA', 'color_tema': '#008938', 'icono_espera': 'fa-crown'}, cat_tarjetas=[])

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
        suc = cur.fetchone()
        
        # CARGAR MENÚS AUTORIZADOS PARA EL ROL
        cur.execute("""
            SELECT m.* FROM menus m 
            JOIN rol_menus rm ON m.id = rm.menu_id 
            WHERE rm.rol_id = %s 
            ORDER BY m.categoria, m.orden
        """, (user['rol_id'],))
        user_menus = cur.fetchall()
        cur.close()

        session.update({
            'user_id': user['id'], 'usuario': user['usuario'], 'rol': user['rol_nombre'], 
            'rol_id': user['rol_id'],
            'sucursal_id': s_id, 'sucursal_nombre': suc['nombre'],
            'establecimiento': suc['establecimiento'], 'punto_emision': suc['punto_emision'],
            'user_menus': user_menus # Guardamos los menús autorizados
        })
        registrar_auditoria('LOGIN', f"Inició sesión en {suc['nombre']}")
        return redirect(url_for('dashboard'))
    cur.close(); flash('Credenciales incorrectas o usuario inactivo', 'danger')
    return redirect(url_for('index'))

# --- ROLES Y PERMISOS ---
@app.route('/roles')
@login_required
@admin_required
def listar_roles():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM roles")
    roles = cur.fetchall()
    cur.execute("SELECT * FROM menus ORDER BY categoria, orden")
    todos_menus = cur.fetchall()
    cur.close()
    return render_template('roles.html', roles=roles, todos_menus=todos_menus)

@app.route('/roles/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_rol():
    d = request.form; cur = mysql.connection.cursor()
    nom = d['nombre'].upper().strip()
    if d.get('id'): cur.execute("UPDATE roles SET nombre=%s WHERE id=%s", (nom, d['id']))
    else: cur.execute("INSERT INTO roles (nombre) VALUES (%s)", (nom,))
    mysql.connection.commit(); cur.close(); flash('Rol guardado', 'success')
    return redirect(url_for('listar_roles'))

@app.route('/roles/permisos/<int:rol_id>')
@login_required
@admin_required
def obtener_permisos(rol_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT menu_id FROM rol_menus WHERE rol_id = %s", (rol_id,))
    permisos = [row['menu_id'] for row in cur.fetchall()]
    cur.close()
    return jsonify({'success': True, 'permisos': permisos})

@app.route('/roles/permisos/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_permisos():
    data = request.get_json(); rol_id = data.get('rol_id'); menus = data.get('menus', [])
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM rol_menus WHERE rol_id = %s", (rol_id,))
        for m_id in menus:
            cur.execute("INSERT INTO rol_menus (rol_id, menu_id) VALUES (%s, %s)", (rol_id, m_id))
        mysql.connection.commit()
        return jsonify({'success': True})
    except Exception as e:
        mysql.connection.rollback(); return jsonify({'success': False, 'message': str(e)})
    finally: cur.close()

# --- GESTIÓN DE MENÚS ---
@app.route('/menus/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_menu():
    d = request.form; cur = mysql.connection.cursor()
    nom, url, ico, cat, ord = d['nombre'], d['url'], d['icono'], d['categoria'].upper(), d.get('orden', 0)
    if d.get('id'):
        cur.execute("UPDATE menus SET nombre=%s, url=%s, icono=%s, categoria=%s, orden=%s WHERE id=%s", (nom, url, ico, cat, ord, d['id']))
    else:
        cur.execute("INSERT INTO menus (nombre, url, icono, categoria, orden) VALUES (%s, %s, %s, %s, %s)", (nom, url, ico, cat, ord))
    mysql.connection.commit(); cur.close(); flash('Menú guardado correctamente', 'success')
    return redirect(url_for('listar_roles'))

@app.route('/menus/eliminar/<int:id>')
@login_required
@admin_required
def eliminar_menu(id):
    cur = mysql.connection.cursor()
    try:
        # VALIDACIÓN: No eliminar si el menú está atado a un rol
        cur.execute("SELECT COUNT(*) as c FROM rol_menus WHERE menu_id = %s", (id,))
        if cur.fetchone()['c'] > 0:
            flash('No se puede eliminar: El menú está siendo usado por uno o más roles.', 'danger')
        else:
            cur.execute("DELETE FROM menus WHERE id = %s", (id,))
            mysql.connection.commit(); flash('Menú eliminado correctamente', 'info')
    except Exception as e: flash(f'Error al eliminar: {str(e)}', 'danger')
    finally: cur.close()
    return redirect(url_for('listar_roles'))

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

@app.route('/clientes/buscar_nombre/<string:nombre>')
@login_required
def buscar_cliente_nombre(nombre):
    cur = mysql.connection.cursor()
    search = f"%{nombre.upper()}%"
    # Mejora: Buscar combinando nombres y apellidos para permitir búsquedas de nombre completo
    cur.execute("""
        SELECT c.*, t.nombre as tipo_id_nombre 
        FROM clientes c 
        JOIN tipos_identificacion t ON c.tipo_identificacion_id = t.id 
        WHERE CONCAT(c.nombres, ' ', c.apellidos) LIKE %s 
           OR CONCAT(c.apellidos, ' ', c.nombres) LIKE %s 
           OR c.cedula_ruc LIKE %s 
        LIMIT 15
    """, (search, search, search))
    res = cur.fetchall(); cur.close()
    return jsonify({'success': True, 'clientes': res})

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
        if d.get('id'): 
            cur.execute("UPDATE clientes SET cedula_ruc=%s, tipo_identificacion_id=%s, nombres=%s, apellidos=%s, direccion=%s, telefono=%s, email=%s, usuario_modificacion_id=%s WHERE id=%s", (ruc_ced, t_id, nom, ape, dir, d['telefono'], d['email'].upper(), u_id, d['id']))
            registrar_auditoria('CLIENTE', f"Actualizó cliente: {nom} {ape} ({ruc_ced})")
        else: 
            cur.execute("INSERT INTO clientes (cedula_ruc, tipo_identificacion_id, nombres, apellidos, direccion, telefono, email, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (ruc_ced, t_id, nom, ape, dir, d['telefono'], d['email'].upper(), u_id, u_id))
            registrar_auditoria('CLIENTE', f"Creó nuevo cliente: {nom} {ape} ({ruc_ced})")
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
        registrar_auditoria('CLIENTE', f"Registro rápido de cliente: {nom} {ape} ({ruc_ced})")
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
        if d.get('id'): 
            cur.execute("UPDATE productos SET codigo=%s, nombre=%s, precio=%s, categoria_id=%s, imagen=%s, mimetype=%s, usuario_modificacion_id=%s WHERE id=%s", (cod, nom, p_base, d['categoria_id'], ib, mt, u_id, d['id']))
            registrar_auditoria('PRODUCTO', f"Actualizó producto e imagen: {nom} ({cod})")
            p_id = d['id']
        else: 
            cur.execute("INSERT INTO productos (codigo, nombre, precio, categoria_id, imagen, mimetype, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (cod, nom, p_base, d['categoria_id'], ib, mt, u_id, u_id))
            p_id = cur.lastrowid
            registrar_auditoria('PRODUCTO', f"Creó producto e imagen: {nom} ({cod})")
    else:
        if d.get('id'): 
            cur.execute("UPDATE productos SET codigo=%s, nombre=%s, precio=%s, categoria_id=%s, usuario_modificacion_id=%s WHERE id=%s", (cod, nom, p_base, d['categoria_id'], u_id, d['id']))
            registrar_auditoria('PRODUCTO', f"Actualizó producto: {nom} ({cod})")
            p_id = d['id']
        else: 
            cur.execute("INSERT INTO productos (codigo, nombre, precio, categoria_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (cod, nom, p_base, d['categoria_id'], u_id, u_id))
            p_id = cur.lastrowid
            registrar_auditoria('PRODUCTO', f"Creó producto: {nom} ({cod})")
    
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
    if d.get('id'): 
        cur.execute("UPDATE insumos SET nombre=%s, stock_actual=%s, stock_minimo=%s, unidad_medida_id=%s, sucursal_id=%s, usuario_modificacion_id=%s WHERE id=%s", (nom, d['stock'], st_min, um_id, suc_id, u_id, d['id']))
        registrar_auditoria('INVENTARIO', f"Actualizó insumo: {nom} - Stock: {d['stock']}")
    else: 
        cur.execute("INSERT INTO insumos (nombre, stock_actual, stock_minimo, unidad_medida_id, sucursal_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (nom, d['stock'], st_min, um_id, suc_id, u_id, u_id))
        registrar_auditoria('INVENTARIO', f"Creó nuevo insumo: {nom} - Stock Inicial: {d['stock']}")
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
    
    # Obtener nombre del insumo para auditoría
    cur.execute("SELECT nombre FROM insumos WHERE id = %s", (ins_id,))
    nom_ins = cur.fetchone()['nombre']
    registrar_auditoria('INVENTARIO', f"Ajuste manual ({tipo}): {nom_ins} x {cant} - Motivo: {mot}")
    
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
            sesion_id = obtener_sesion_caja_activa(s_id, u_id)
            cur.execute("INSERT INTO compras (proveedor_id, sucursal_id, establecimiento, punto_emision, numero_comprobante, total, fecha, clave_acceso, numero_autorizacion, fecha_caducidad, sesion_caja_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (data['proveedor_id'], s_id, est, pto, sec, data['total'], f, data.get('clave_acceso'), n_aut, f_cad, sesion_id, u_id, u_id))
            comp_id = cur.lastrowid
        for i in data['items']:
            cur.execute("INSERT INTO detalles_compras (compra_id, insumo_id, cantidad, costo_unitario, subtotal, iva_valor) VALUES (%s,%s,%s,%s,%s,%s)", (comp_id, i['insumo_id'], i['cantidad'], i['costo'], i['subtotal'], i['iva_valor']))
            cur.execute("UPDATE insumos SET stock_actual = stock_actual + %s WHERE id = %s", (i['cantidad'], i['insumo_id']))
        
        # REGISTRAR AUDITORÍA (Si es nueva compra)
        if not id_c:
            registrar_auditoria('COMPRA', f"Nueva compra de insumos: Doc {est}-{pto}-{sec} por ${data['total']}")
        else:
            registrar_auditoria('COMPRA', f"Editó compra de insumos ID: {id_c}")

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
    p = cur.fetchall(); cur.execute("SELECT * FROM tipos_identificacion"); t = cur.fetchall(); cur.close()
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

    if d.get('id'): 
        cur.execute("UPDATE proveedores SET ruc=%s, razon_social=%s, nombre_comercial=%s, direccion=%s, telefono=%s, email=%s, tipo_comprobante_id=%s, usuario_modificacion_id=%s WHERE id=%s", (ruc, razon, nom, dir, tel, eml, t_comp, u_id, d['id']))
        registrar_auditoria('PROVEEDOR', f"Actualizó proveedor: {razon} ({ruc})")
    else: 
        cur.execute("INSERT INTO proveedores (ruc, razon_social, nombre_comercial, direccion, telefono, email, tipo_comprobante_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (ruc, razon, nom, dir, tel, eml, t_comp, u_id, u_id))
        registrar_auditoria('PROVEEDOR', f"Creó nuevo proveedor: {razon} ({ruc})")
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
        registrar_auditoria('USUARIO', f"Creó usuario: {u} (Cédula: {c})")
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
        registrar_auditoria('USUARIO', f"Actualizó usuario: {u} (Cédula: {c})")
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
    if d.get('id'): 
        cur.execute("UPDATE sucursales SET nombre=%s, establecimiento=%s, punto_emision=%s, ultimo_secuencial=%s, usuario_modificacion_id=%s WHERE id=%s", (nom, est, pto, u_sec, u_id, d['id']))
        registrar_auditoria('CONFIG', f"Actualizó sucursal: {nom}")
    else: 
        cur.execute("INSERT INTO sucursales (nombre, establecimiento, punto_emision, ultimo_secuencial, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s)", (nom, est, pto, u_sec, u_id, u_id))
        registrar_auditoria('CONFIG', f"Creó nueva sucursal: {nom}")
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
    if d.get('id'): 
        cur.execute("UPDATE categorias SET nombre=%s, usuario_modificacion_id=%s WHERE id=%s", (nom, u_id, d['id']))
        registrar_auditoria('CONFIG', f"Actualizó categoría: {nom}")
    else: 
        cur.execute("INSERT INTO categorias (nombre, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s)", (nom, u_id, u_id))
        registrar_auditoria('CONFIG', f"Creó nueva categoría: {nom}")
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
    
    mysql.connection.commit(); cur.close(); flash('Configuración actualizada correctamente', 'success')
    registrar_auditoria('CONFIG', f"Actualizó configuración general de la empresa: {nom}")
    return redirect(url_for('configuracion_empresa'))

def enviar_comprobante_email(venta_id, forzar=False):
    """
    Genera PDF y XML basándose ÚNICAMENTE en el XML autorizado del SRI.
    Extrae datos de forma RESILIENTE para evitar errores de NoneType.
    """
    import base64, requests
    
    def log_mail(msg):
        print(f"DEBUG MAIL: {msg}")
        with open("email_error.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()}: {msg}\n")

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT v.anulada, v.xml_autorizado, v.numero_autorizacion, v.clave_acceso_sri, v.fecha, v.forma_pago,
               c.email as cliente_email, c.nombres, c.apellidos,
               a.nc_xml_autorizado, a.nc_clave_acceso, a.nc_numero_autorizacion
        FROM ventas v 
        JOIN clientes c ON v.cliente_id = c.id 
        LEFT JOIN anulaciones_factura a ON v.id = a.venta_id
        WHERE v.id = %s
    """, (venta_id,))
    v = cur.fetchone()
    
    if not v:
        log_mail(f"Venta ID {venta_id} no encontrada.")
        if cur: cur.close()
        return False

    # PRIORIDAD NC
    es_nc = True if (v['anulada'] and v['nc_xml_autorizado']) else False
    xml_str = v['nc_xml_autorizado'] if es_nc else v['xml_autorizado']
    clave_acc = v['nc_clave_acceso'] if es_nc else v['clave_acceso_sri']
    num_aut = v['nc_numero_autorizacion'] if es_nc else v['numero_autorizacion']
    tipo_doc_nombre = "Nota de Credito" if es_nc else "Factura"

    if not xml_str:
        log_mail(f"XML no disponible para Venta {venta_id}")
        if cur: cur.close()
        return False

    cur.execute("SELECT * FROM empresa LIMIT 1"); emp = cur.fetchone(); cur.close()

    try:
        import xml.etree.ElementTree as ET
        # Limpiar posibles envoltorios del SRI (CDATA o autorizacion)
        if '<comprobante>' in xml_str and '</comprobante>' in xml_str:
            import html
            xml_str = html.unescape(xml_str.split('<comprobante>')[1].split('</comprobante>')[0])
        
        root = ET.fromstring(xml_str.strip())
        
        # Ayudante para buscar nodos ignorando namespaces
        def find_node(parent, tag_name):
            if parent is None: return None
            # Primero intentamos búsqueda directa
            res = parent.find(tag_name)
            if res is not None: return res
            # Si no, recorremos todos los nodos buscando el tag local
            for node in parent.iter():
                if tag_name in node.tag: return node
            return None

        def g_txt(parent, tag_name, default=''):
            node = find_node(parent, tag_name)
            return node.text.strip() if node is not None and node.text else default

        it = find_node(root, 'infoTributaria')
        if it is None: it = root if 'infoTributaria' in root.tag else None
        if it is None: raise Exception("infoTributaria no hallada en el XML")

        datos = {
            'ruc_emisor': g_txt(it, 'ruc'),
            'razon_social': g_txt(it, 'razonSocial'),
            'nombre_comercial': g_txt(it, 'nombreComercial', g_txt(it, 'razonSocial')),
            'dir_matriz': g_txt(it, 'dirMatriz'),
            'clave_acceso': clave_acc,
            'num_autorizacion': num_aut,
            'fecha_autorizacion': v['fecha'].strftime('%d/%m/%Y %H:%M'),
            'ambiente': 'PRODUCCIÓN' if g_txt(it, 'ambiente') == '2' else 'PRUEBAS',
            'detalles': [],
            'email': v['cliente_email'],
            'es_nota_credito': es_nc
        }

        if es_nc:
            inf = find_node(root, 'infoNotaCredito')
            datos.update({
                'cliente_nombre': g_txt(inf, 'razonSocialComprador'),
                'cliente_id': g_txt(inf, 'identificacionComprador'),
                'fecha_emision': g_txt(inf, 'fechaEmision'),
                'total': float(g_txt(inf, 'valorModificacion', '0')),
                'doc_modificado': g_txt(inf, 'numDocModificado'),
                'motivo_anulacion': g_txt(inf, 'motivo'),
                'subtotal_0': 0.0, 'subtotal_15': 0.0, 'iva_valor': 0.0
            })
        else:
            inf = find_node(root, 'infoFactura')
            datos.update({
                'cliente_nombre': g_txt(inf, 'razonSocialComprador'),
                'cliente_id': g_txt(inf, 'identificacionComprador'),
                'fecha_emision': g_txt(inf, 'fechaEmision'),
                'total': float(g_txt(inf, 'importeTotal', '0')),
                'obligado_contabilidad': g_txt(inf, 'obligadoContabilidad', 'NO'),
                'subtotal_0': 0.0, 'subtotal_15': 0.0, 'iva_valor': 0.0,
                'forma_pago': v['forma_pago']
            })

        # Totales
        if inf is not None:
            # Buscamos todos los totalImpuesto en cualquier nivel bajo info
            for ti in inf.iter():
                if 'totalImpuesto' in ti.tag:
                    cp = g_txt(ti, 'codigoPorcentaje')
                    base = float(g_txt(ti, 'baseImponible', '0'))
                    val = float(g_txt(ti, 'valor', '0'))
                    if cp == '4': datos['subtotal_15'], datos['iva_valor'] = base, val
                    elif cp == '0': datos['subtotal_0'] = base

        # Detalles
        det_node = find_node(root, 'detalles')
        if det_node is not None:
            for d in det_node.findall('*'):
                datos['detalles'].append({
                    'codigo': g_txt(d, 'codigoPrincipal', g_txt(d, 'codigoInterno')),
                    'descripcion': g_txt(d, 'descripcion'),
                    'cantidad': float(g_txt(d, 'cantidad', '0')),
                    'precio_unitario': float(g_txt(d, 'precioUnitario', '0')),
                    'total': float(g_txt(d, 'precioTotalSinImpuesto', '0'))
                })

        # CÓDIGO DE BARRAS
        import barcode
        from barcode.writer import ImageWriter
        code128 = barcode.get('code128', clave_acc, writer=ImageWriter())
        barcode_io = io.BytesIO()
        code128.write(barcode_io, options={"write_text": False, "module_height": 10})
        datos['barcode_64'] = base64.b64encode(barcode_io.getvalue()).decode('utf-8')

        # Generar PDF
        import ride_fpdf
        pdf_data = ride_fpdf.generar_pdf_fpdf(datos, emp)

        # Enviar vía Brevo
        kb_p1 = "xkeysib-47e7120cc4313c218521b79c83b2e9ca2182ea600bcd08792733d2b556ebaa82"
        kb_p2 = "-hH7UpUUP2wA4dlSM"
        brevo_api_key = os.environ.get('BREVO_API_KEY', kb_p1 + kb_p2)
        
        payload = {
            "sender": {"name": emp['nombre_comercial'], "email": emp['email_user']},
            "to": [{"email": v['cliente_email'], "name": f"{v['nombres']} {v['apellidos']}"}],
            "subject": f"{tipo_doc_nombre} Electronica - {clave_acc}",
            "htmlContent": f"<p>Estimado(a) <b>{v['nombres']} {v['apellidos']}</b>,</p><p>Adjuntamos su <b>{tipo_doc_nombre}</b> autorizada por el SRI.</p><p>Gracias por su atención.</p>",
            "attachment": [
                {"content": base64.b64encode(pdf_data).decode('utf-8'), "name": f"{tipo_doc_nombre.replace(' ','_')}_{clave_acc[-9:]}.pdf"},
                {"content": base64.b64encode(xml_str.encode('utf-8')).decode('utf-8'), "name": f"{clave_acc}.xml"}
            ]
        }
        res = requests.post("https://api.brevo.com/v3/smtp/email", headers={"api-key": brevo_api_key, "content-type": "application/json"}, json=payload)
        
        if res.status_code in [200, 201]:
            log_mail(f"EXITO: {tipo_doc_nombre} enviada a {v['cliente_email']}")
            return True
        else:
            log_mail(f"Error Brevo ({res.status_code}): {res.text}")
            return False
    except Exception as e:
        log_mail(f"Fallo critico: {str(e)}")
        log_mail(traceback.format_exc())
        return False

# --- CAJA Y TURNOS ---
@app.route('/caja/sesion')
@login_required
def sesion_caja():
    cur = mysql.connection.cursor()
    s_id = session['sucursal_id']
    u_id = session['user_id']
    
    # Buscar si tiene una sesión abierta
    cur.execute("SELECT * FROM sesiones_caja WHERE sucursal_id = %s AND usuario_id = %s AND estado = 'ABIERTA' ORDER BY id DESC LIMIT 1", (s_id, u_id))
    sesion_abierta = cur.fetchone()
    
    if sesion_abierta:
        # Calcular ventas y egresos de la sesión actual
        ses_id = sesion_abierta['id']
        f_apertura = sesion_abierta['fecha_apertura']
        
        # Total Ventas Efectivo
        cur.execute("SELECT SUM(total) as t FROM ventas WHERE sesion_caja_id = %s AND forma_pago = 'EFECTIVO'", (ses_id,))
        v_efectivo = float(cur.fetchone()['t'] or 0)
        
        # Total Ventas Tarjeta
        cur.execute("SELECT SUM(total) as t FROM ventas WHERE sesion_caja_id = %s AND forma_pago = 'TARJETA'", (ses_id,))
        v_tarjeta = float(cur.fetchone()['t'] or 0)
        
        # Total Ventas Transferencia
        cur.execute("SELECT SUM(total) as t FROM ventas WHERE sesion_caja_id = %s AND forma_pago = 'TRANSFERENCIA'", (ses_id,))
        v_trans = float(cur.fetchone()['t'] or 0)

        # DESGLOSE DETALLADO POR TIPO DE TARJETA
        cur.execute("""
            SELECT ct.nombre as tarjeta, SUM(v.total) as total 
            FROM ventas v 
            JOIN cat_tarjetas ct ON v.id_tarjeta = ct.id 
            WHERE v.sesion_caja_id = %s AND v.forma_pago = 'TARJETA'
            GROUP BY ct.id
        """, (ses_id,))
        desglose_tarjetas = cur.fetchall()
        
        # Total Egresos (Solo del módulo de Egresos)
        cur.execute("SELECT SUM(monto) as t FROM egresos WHERE sesion_caja_id = %s", (ses_id,))
        total_salidas = float(cur.fetchone()['t'] or 0)

        # Listado Detallado de Egresos para el Cierre
        cur.execute("SELECT descripcion, monto FROM egresos WHERE sesion_caja_id = %s", (ses_id,))
        detalles_egresos = cur.fetchall()
        
        # TOTAL GENERAL DE LA JORNADA (PRODUCCIÓN TOTAL)
        total_jornada = v_efectivo + v_tarjeta + v_trans
        
        monto_esperado_efectivo = float(sesion_abierta['monto_inicial']) + v_efectivo - total_salidas
        
        cur.close()
        return render_template('cierre_turno.html', sesion=sesion_abierta, v_efectivo=v_efectivo, v_tarjeta=v_tarjeta, v_trans=v_trans, total_jornada=total_jornada, desglose_tarjetas=desglose_tarjetas, detalles_egresos=detalles_egresos, salidas=total_salidas, esperado=monto_esperado_efectivo)
    
    cur.close()
    return render_template('apertura_caja.html')

@app.route('/caja/abrir', methods=['POST'])
@login_required
def abrir_caja():
    monto_inicial = float(request.form.get('monto_inicial', 0))
    s_id = session['sucursal_id']
    u_id = session['user_id']
    
    cur = mysql.connection.cursor()
    # Verificar que no tenga ya una abierta
    cur.execute("SELECT id FROM sesiones_caja WHERE sucursal_id = %s AND usuario_id = %s AND estado = 'ABIERTA'", (s_id, u_id))
    if cur.fetchone():
        flash('Ya tienes un turno de caja abierto.', 'warning')
        return redirect(url_for('pos'))
        
    cur.execute("INSERT INTO sesiones_caja (sucursal_id, usuario_id, monto_inicial) VALUES (%s, %s, %s)", (s_id, u_id, monto_inicial))
    sesion_id = cur.lastrowid
    
    # REGISTRAR EL MONTO INICIAL EN EL FLUJO DE CAJA PARA QUE EL SALDO DISPONIBLE SEA CORRECTO
    cur.execute("""
        INSERT INTO flujo_caja (sucursal_id, usuario_id, tipo, monto, descripcion, referencia_id, tipo_referencia)
        VALUES (%s, %s, 'INGRESO', %s, %s, %s, 'APERTURA')
    """, (s_id, u_id, monto_inicial, f"Apertura de Caja - Turno #{sesion_id}", sesion_id))
    
    mysql.connection.commit()
    registrar_auditoria('CAJA', f"Abrió turno de caja con ${monto_inicial:.2f}")
    cur.close()
    flash('Turno de caja abierto exitosamente.', 'success')
    return redirect(url_for('pos'))

@app.route('/caja/cerrar', methods=['POST'])
@login_required
def cerrar_caja():
    r_efe = float(request.form.get('real_efectivo', 0))
    r_tar = float(request.form.get('real_tarjeta', 0))
    r_tra = float(request.form.get('real_transferencia', 0))
    
    # Nuevas observaciones específicas
    o_efe = request.form.get('obs_efectivo', '')
    o_tar = request.form.get('obs_tarjeta', '')
    o_tra = request.form.get('obs_transferencia', '')
    
    s_id = session['sucursal_id']
    u_id = session['user_id']
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM sesiones_caja WHERE sucursal_id = %s AND usuario_id = %s AND estado = 'ABIERTA' ORDER BY id DESC LIMIT 1", (s_id, u_id))
    sesion = cur.fetchone()
    
    if not sesion:
        flash('No tienes una sesión de caja abierta.', 'danger')
        return redirect(url_for('dashboard'))
        
    ses_id = sesion['id']
    
    # Recalcular totales exactos del sistema
    cur.execute("SELECT SUM(total) as t FROM ventas WHERE sesion_caja_id = %s AND forma_pago = 'EFECTIVO'", (ses_id,))
    v_efectivo = float(cur.fetchone()['t'] or 0)
    cur.execute("SELECT SUM(total) as t FROM ventas WHERE sesion_caja_id = %s AND forma_pago = 'TARJETA'", (ses_id,))
    v_tarjeta = float(cur.fetchone()['t'] or 0)
    cur.execute("SELECT SUM(total) as t FROM ventas WHERE sesion_caja_id = %s AND forma_pago = 'TRANSFERENCIA'", (ses_id,))
    v_trans = float(cur.fetchone()['t'] or 0)
    cur.execute("SELECT SUM(monto) as t FROM egresos WHERE sesion_caja_id = %s", (ses_id,))
    t_egresos = float(cur.fetchone()['t'] or 0)
    cur.execute("SELECT SUM(total) as t FROM compras WHERE sesion_caja_id = %s", (ses_id,))
    t_compras = float(cur.fetchone()['t'] or 0)
    
    total_salidas = t_egresos + t_compras
    e_efe = float(sesion['monto_inicial']) + v_efectivo - total_salidas
    
    total_real = r_efe + r_tar + r_tra
    total_esperado = e_efe + v_tarjeta + v_trans
    dif_total = total_real - total_esperado

    cur.execute("""
        UPDATE sesiones_caja 
        SET fecha_cierre = CURRENT_TIMESTAMP, 
            monto_ventas_efectivo = %s, monto_ventas_tarjeta = %s, monto_ventas_transferencia = %s,
            monto_egresos = %s, monto_final_esperado = %s, monto_final_real = %s,
            real_efectivo = %s, real_tarjeta = %s, real_transferencia = %s,
            obs_efectivo = %s, obs_tarjeta = %s, obs_transferencia = %s,
            diferencia = %s, estado = 'CERRADA'
        WHERE id = %s
    """, (v_efectivo, v_tarjeta, v_trans, total_salidas, total_esperado, total_real, r_efe, r_tar, r_tra, o_efe, o_tar, o_tra, dif_total, ses_id))
    
    mysql.connection.commit()
    registrar_auditoria('CAJA', f"Cerró turno. Diferencia Total: ${dif_total:.2f}")
    cur.close()
    flash(f'Turno cerrado correctamente.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/caja/cierre_diario')
@login_required
@admin_required
def cierre_diario():
    cur = mysql.connection.cursor()
    s_id = session['sucursal_id']
    
    # Verificar si hay sesiones abiertas
    cur.execute("SELECT u.usuario, s.fecha_apertura FROM sesiones_caja s JOIN usuarios u ON s.usuario_id = u.id WHERE s.sucursal_id = %s AND s.estado = 'ABIERTA'", (s_id,))
    abiertas = cur.fetchall()
    
    hoy = datetime.now().strftime('%Y-%m-%d')
    # Sumar todo lo de hoy que esté CERRADO y no consolidado
    cur.execute("""
        SELECT 
            COUNT(id) as turnos,
            SUM(monto_ventas_efectivo) as t_efectivo,
            SUM(monto_ventas_tarjeta) as t_tarjeta,
            SUM(monto_ventas_transferencia) as t_trans,
            SUM(monto_egresos) as t_egresos,
            SUM(monto_final_real) as saldo_real_entregado
        FROM sesiones_caja
        WHERE sucursal_id = %s AND estado = 'CERRADA' AND DATE(fecha_cierre) = %s
    """, (s_id, hoy))
    resumen = cur.fetchone()

    # Detalle por cajero (sesiones cerradas hoy)
    cur.execute("""
        SELECT 
            s.id,
            u.usuario,
            s.fecha_apertura,
            s.fecha_cierre,
            s.monto_inicial,
            s.monto_ventas_efectivo,
            s.monto_ventas_tarjeta,
            s.monto_ventas_transferencia,
            s.monto_egresos,
            s.monto_final_real
        FROM sesiones_caja s
        JOIN usuarios u ON s.usuario_id = u.id
        WHERE s.sucursal_id = %s AND s.estado = 'CERRADA' AND DATE(s.fecha_cierre) = %s
        ORDER BY s.fecha_cierre DESC
    """, (s_id, hoy))
    detalle_cajeros = cur.fetchall()

    # Por cada sesión, traer su desglose de tarjetas y lista de egresos
    for ses in detalle_cajeros:
        # Desglose tarjetas
        cur.execute("""
            SELECT ct.nombre as tarjeta, SUM(v.total) as total 
            FROM ventas v 
            JOIN cat_tarjetas ct ON v.id_tarjeta = ct.id 
            WHERE v.sesion_caja_id = %s AND v.forma_pago = 'TARJETA'
            GROUP BY ct.id
        """, (ses['id'],))
        ses['desglose_tarjetas'] = cur.fetchall()

        # Lista egresos
        cur.execute("SELECT descripcion, monto FROM egresos WHERE sesion_caja_id = %s", (ses['id'],))
        ses['lista_egresos'] = cur.fetchall()

    cur.execute("SELECT * FROM cierres_diarios WHERE sucursal_id = %s ORDER BY fecha_cierre DESC LIMIT 5", (s_id,))
    historial = cur.fetchall()

    cur.close()
    return render_template('cierre_diario.html', abiertas=abiertas, resumen=resumen, historial=historial, hoy=hoy, detalle_cajeros=detalle_cajeros)
@app.route('/caja/ejecutar_cierre_diario', methods=['POST'])
@login_required
@admin_required
def ejecutar_cierre_diario():
    cur = mysql.connection.cursor()
    s_id = session['sucursal_id']
    u_id = session['user_id']
    obs = request.form.get('observaciones', '')
    hoy = datetime.now().strftime('%Y-%m-%d')
    
    # 1. VALIDACIÓN CRÍTICA: ¿Ya se hizo el cierre hoy?
    cur.execute("SELECT id FROM cierres_diarios WHERE sucursal_id = %s AND fecha_dia = %s", (s_id, hoy))
    if cur.fetchone():
        cur.close()
        flash('El Cierre Diario para hoy ya fue realizado previamente.', 'warning')
        return redirect(url_for('cierre_diario'))
    
    # Verificar sesiones abiertas
    cur.execute("SELECT id FROM sesiones_caja WHERE sucursal_id = %s AND estado = 'ABIERTA'", (s_id,))
    if cur.fetchone():
        flash('No se puede hacer el cierre diario. Hay turnos de empleados aún abiertos.', 'danger')
        return redirect(url_for('cierre_diario'))
        
    cur.execute("""
        SELECT 
            COUNT(id) as turnos_conteo,
            SUM(monto_ventas_efectivo + monto_ventas_tarjeta + monto_ventas_transferencia) as total_v,
            SUM(monto_ventas_efectivo) as t_efectivo,
            SUM(monto_ventas_tarjeta) as t_tarjeta,
            SUM(monto_ventas_transferencia) as t_trans,
            SUM(monto_egresos) as t_egresos,
            SUM(monto_final_real) as saldo_real
        FROM sesiones_caja 
        WHERE sucursal_id = %s AND estado = 'CERRADA' AND DATE(fecha_cierre) = %s
    """, (s_id, hoy))
    res = cur.fetchone()
    
    if not res or res['total_v'] is None:
        flash('No hay movimientos en turnos cerrados hoy para consolidar.', 'warning')
        return redirect(url_for('cierre_diario'))
        
    cur.execute("""
        INSERT INTO cierres_diarios (sucursal_id, usuario_id, cantidad_turnos, fecha_dia, total_ventas, total_efectivo, total_tarjetas, total_transferencias, total_egresos, saldo_final_caja, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (s_id, u_id, res['turnos_conteo'], hoy, res['total_v'], res['t_efectivo'], res['t_tarjeta'], res['t_trans'], res['t_egresos'], res['saldo_real'], obs))
    
    mysql.connection.commit()
    registrar_auditoria('CAJA_ADMIN', f"Ejecutó Cierre Diario. Saldo Consolidado: ${res['saldo_real']:.2f}")
    cur.close()
    flash('Cierre Diario Consolidado exitosamente.', 'success')
    return redirect(url_for('cierre_diario'))

# --- POS ---
@app.route('/pos')
@login_required
def pos():
    sesion_id = obtener_sesion_caja_activa(session['sucursal_id'], session['user_id'])
    if not sesion_id:
        flash('Debe abrir un turno de caja antes de poder realizar ventas.', 'warning')
        return redirect(url_for('sesion_caja'))
        
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
        id_tarjeta = data.get('id_tarjeta')
        if not id_tarjeta or str(id_tarjeta).strip() == '':
            id_tarjeta = None # Evita error de FK si llega vacío
        
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
        
        sesion_id = obtener_sesion_caja_activa(s_id, u_id)
        
        cur.execute("""INSERT INTO ventas (usuario_id, sucursal_id, cliente_id, plataforma_id, id_tarjeta, sesion_caja_id, subtotal_0, subtotal_15, iva_valor, total, forma_pago, clave_acceso_sri, estado_sri, establecimiento, punto_emision, secuencial, usuario_creacion_id, usuario_modificacion_id) 
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'PENDIENTE',%s,%s,%s,%s,%s)""", 
                    (u_id, s_id, c_id, plat_id, id_tarjeta, sesion_id, data.get('subtotal_0', 0), data.get('subtotal_15', 0), data.get('iva_valor', 0), data['total'], fpago, clave, est, pto, sec_str, u_id, u_id))
        v_id = cur.lastrowid
        
        # ACTUALIZAR EL ÚLTIMO SECUENCIAL EN LA SUCURSAL
        cur.execute("UPDATE sucursales SET ultimo_secuencial=%s WHERE id=%s", (siguiente_sec, s_id))
        for i in data['items']:
            i_tot = float(i['precio']) * int(i['cantidad']); i_iva = i_tot - (i_tot / divisor)
            cur.execute("INSERT INTO detalles_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal, iva_valor) VALUES (%s,%s,%s,%s,%s,%s)", (v_id, i['id'], i['cantidad'], i['precio'], i_tot, i_iva))
            cur.execute("SELECT insumo_id, cantidad_requerida FROM recetas WHERE producto_id=%s", (i['id'],))
            for r in cur.fetchall(): cur.execute("UPDATE insumos SET stock_actual=stock_actual-%s WHERE id=%s AND sucursal_id=%s", (float(r['cantidad_requerida']) * int(i['cantidad']), r['insumo_id'], s_id))
        mysql.connection.commit(); registrar_auditoria('VENTA', f"Venta ID: {v_id} registrada")
        
        # REGISTRAR INGRESO EN FLUJO DE CAJA SI ES EFECTIVO
        if fpago == 'EFECTIVO':
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO flujo_caja (sucursal_id, usuario_id, tipo, monto, descripcion, referencia_id, tipo_referencia)
                VALUES (%s, %s, 'INGRESO', %s, %s, %s, 'VENTA')
            """, (s_id, u_id, data['total'], f"Venta #{v_id}", v_id))
            mysql.connection.commit()

        import facturacion_sri
        autorizada = facturacion_sri.procesar_factura_electronica(v_id, mysql)
        
        # INTENTAR ENVÍO AUTOMÁTICO DE EMAIL SOLO SI FUE AUTORIZADA
        if autorizada:
            if enviar_comprobante_email(v_id):
                flash('Factura AUTORIZADA y enviada al cliente por correo', 'success')
            else:
                flash('Factura AUTORIZADA, pero el envío de correo falló (verifique configuración)', 'info')
        else:
            # Si no fue autorizada, verificamos por qué (Pendiente o Devuelta)
            cur = mysql.connection.cursor()
            cur.execute("SELECT estado_sri FROM ventas WHERE id = %s", (v_id,))
            v_actual = cur.fetchone()
            cur.close()
            if v_actual and 'PENDIENTE' in v_actual['estado_sri'].upper():
                flash('Venta registrada. La factura quedó PENDIENTE de autorización en el SRI.', 'warning')
            else:
                flash(f'Venta registrada, pero el SRI reportó: {v_actual["estado_sri"] if v_actual else "Error"}', 'danger')
        
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

@app.route('/ventas/anulaciones')
@login_required
@admin_required
def listar_anulaciones():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT a.*, v.secuencial, v.establecimiento, v.punto_emision, v.fecha as fecha_venta, 
               c.nombres, c.apellidos, u.usuario as cajero
        FROM anulaciones_factura a
        JOIN ventas v ON a.venta_id = v.id
        JOIN clientes c ON v.cliente_id = c.id
        JOIN usuarios u ON v.usuario_id = u.id
        ORDER BY a.fecha_solicitud DESC
    """)
    anulaciones = cur.fetchall()
    cur.close()
    return render_template('anulaciones.html', anulaciones=anulaciones)

@app.route('/ventas/anular/<int:id>', methods=['POST'])
@login_required
@admin_required
def anular_venta(id):
    import facturacion_sri
    motivo = request.form.get('motivo', 'ANULACIÓN SOLICITADA POR EL USUARIO')
    try:
        success, message = facturacion_sri.anular_factura_sri(id, motivo, mysql, session.get('user_id'))
        if success:
            # DISPARAR ENVÍO DE EMAIL DE LA NOTA DE CRÉDITO
            enviar_comprobante_email(id, forzar=True)
            flash(message + " Se ha enviado la Nota de Crédito al cliente.", 'success')
            registrar_auditoria('ANULACION', f"Factura ID {id} anulada con NC exitosamente.")
        else:
            flash(f"No se pudo anular: {message}", 'danger')
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", 'danger')
    
    return redirect(url_for('historial_ventas'))

@app.route('/ventas/reenviar_email/<int:id>')
@login_required
def reenviar_email_venta(id):
    try:
        if enviar_comprobante_email(id, forzar=True):
            flash('Correo enviado correctamente al cliente', 'success')
        else:
            flash('No se pudo enviar el correo. Verifique que el cliente tenga email y la configuración sea correcta.', 'warning')
    except Exception as e:
        flash(f'Error técnico al enviar: {str(e)}', 'danger')
    return redirect(url_for('historial_ventas'))

@app.route('/venta/ride/<int:id>')
@login_required
def ver_ride(id):
    cur = mysql.connection.cursor()
    # Verificar si está anulada para traer datos de la Nota de Crédito
    cur.execute("SELECT v.*, a.nc_xml_autorizado, a.nc_numero_autorizacion, a.nc_clave_acceso FROM ventas v LEFT JOIN anulaciones_factura a ON v.id = a.venta_id WHERE v.id=%s", (id,))
    v = cur.fetchone()
    
    # Decidimos qué XML usar
    xml_data = v['nc_xml_autorizado'] if (v['anulada'] and v['nc_xml_autorizado']) else v['xml_autorizado']
    num_aut = v['nc_numero_autorizacion'] if (v['anulada'] and v['nc_xml_autorizado']) else v['numero_autorizacion']
    clave = v['nc_clave_acceso'] if (v['anulada'] and v['nc_xml_autorizado']) else v['clave_acceso_sri']
    es_nc = True if (v['anulada'] and v['nc_xml_autorizado']) else False

    if not v or not xml_data: cur.close(); return "RIDE no disponible", 404
    
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(xml_data); 
        f_xml = root.find('.//factura') or root.find('.//notaCredito') or root
        it = f_xml.find('infoTributaria')
        
        datos = {
            'ruc_emisor': it.find('ruc').text, 
            'razon_social': it.find('razonSocial').text, 
            'nombre_comercial': it.find('nombreComercial').text if it.find('nombreComercial') is not None else it.find('razonSocial').text,
            'dir_matriz': it.find('dirMatriz').text, 
            'clave_acceso': clave, 
            'num_autorizacion': num_aut, 
            'fecha_autorizacion': v['fecha'].strftime('%d/%m/%Y %H:%M'),
            'ambiente': 'PRODUCCIÓN' if it.find('ambiente').text == '2' else 'PRUEBAS',
            'detalles': [],
            'es_nota_credito': es_nc
        }

        if es_nc:
            inf = f_xml.find('infoNotaCredito')
            datos.update({
                'cliente_nombre': inf.find('razonSocialComprador').text,
                'cliente_id': inf.find('identificacionComprador').text,
                'fecha_emision': inf.find('fechaEmision').text,
                'total': float(inf.find('valorModificacion').text),
                'doc_modificado': inf.find('numDocModificado').text,
                'motivo_anulacion': inf.find('motivo').text,
                'subtotal_0': 0.0, 'subtotal_15': 0.0, 'iva_valor': 0.0
            })
        else:
            inf = f_xml.find('infoFactura')
            datos.update({
                'cliente_nombre': inf.find('razonSocialComprador').text,
                'cliente_id': inf.find('identificacionComprador').text,
                'fecha_emision': inf.find('fechaEmision').text,
                'total': float(inf.find('importeTotal').text),
                'obligado_contabilidad': inf.find('obligadoContabilidad').text if inf.find('obligadoContabilidad') is not None else 'NO',
                'subtotal_0': 0.0, 'subtotal_15': 0.0, 'iva_valor': 0.0,
                'forma_pago': v['forma_pago']
            })

        # Totales e Impuestos (Lógica similar para ambos)
        for ti in inf.find('totalConImpuestos').findall('totalImpuesto'):
            if ti.find('codigoPorcentaje').text == '4': 
                datos['subtotal_15'], datos['iva_valor'] = float(ti.find('baseImponible').text), float(ti.find('valor').text)
            elif ti.find('codigoPorcentaje').text == '0': 
                datos['subtotal_0'] = float(ti.find('baseImponible').text)

        # Detalles
        for d_node in f_xml.find('detalles').findall('detalle'):
            datos['detalles'].append({
                'codigo': (d_node.find('codigoPrincipal') or d_node.find('codigoInterno')).text, 
                'descripcion': d_node.find('descripcion').text, 
                'cantidad': float(d_node.find('cantidad').text), 
                'precio_unitario': float(d_node.find('precioUnitario').text), 
                'total': float(d_node.find('precioTotalSinImpuesto').text)
            })

        cur.execute("SELECT * FROM empresa LIMIT 1"); emp = cur.fetchone(); cur.close()
        return render_template('ride.html', d=datos, empresa=emp)
    except Exception as e: 
        import traceback
        print(traceback.format_exc())
        cur.close(); return str(e), 500

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

# --- EGRESOS Y FLUJO DE CAJA ---
@app.route('/egresos')
@login_required
def listar_egresos():
    cur = mysql.connection.cursor()
    s_id = session['sucursal_id']
    cur.execute("""
        SELECT e.*, u.usuario, p.razon_social as proveedor_nombre 
        FROM egresos e 
        JOIN usuarios u ON e.usuario_id = u.id 
        LEFT JOIN proveedores p ON e.proveedor_id = p.id 
        WHERE e.sucursal_id = %s 
        ORDER BY e.fecha DESC
    """, (s_id,))
    egresos = cur.fetchall()
    
    # Obtener proveedores para el formulario
    cur.execute("SELECT id, razon_social, ruc FROM proveedores ORDER BY razon_social")
    proveedores = cur.fetchall()
    
    # Calcular saldo actual en caja (solo EFECTIVO)
    cur.execute("""
        SELECT SUM(CASE WHEN tipo='INGRESO' THEN monto ELSE -monto END) as saldo 
        FROM flujo_caja WHERE sucursal_id = %s
    """, (s_id,))
    caja = cur.fetchone()
    saldo_actual = float(caja['saldo'] or 0)
    
    cur.close()
    return render_template('egresos.html', egresos=egresos, proveedores=proveedores, saldo_actual=saldo_actual)

@app.route('/egresos/nuevo', methods=['POST'])
@login_required
def registrar_egreso():
    cur = mysql.connection.cursor()
    try:
        s_id = session['sucursal_id']
        u_id = session['user_id']
        monto = float(request.form['monto'])
        descripcion = request.form['descripcion']
        tipo_doc = request.form.get('tipo_documento', 'RECIBO_INTERNO')
        num_doc = request.form.get('numero_documento', '')
        categoria = request.form.get('categoria', 'GASTOS VARIOS')
        prov_id = request.form.get('proveedor_id')

        # Si no hay proveedor, asignar el genérico 'GASTOS VARIOS'
        if not prov_id or prov_id == '':
            cur.execute("SELECT id FROM proveedores WHERE ruc = '9999999999999' LIMIT 1")
            res_prov = cur.fetchone()
            prov_id = res_prov['id'] if res_prov else None

        # 1. VALIDACIÓN DE CAJA (Verificar si hay suficiente efectivo)
        cur.execute("""
            SELECT SUM(CASE WHEN tipo='INGRESO' THEN monto ELSE -monto END) as saldo 
            FROM flujo_caja WHERE sucursal_id = %s
        """, (s_id,))
        saldo_actual = float(cur.fetchone()['saldo'] or 0)

        if monto > saldo_actual:
            return jsonify({'success': False, 'message': f'Efectivo insuficiente en caja. Saldo disponible: ${saldo_actual:.2f}'})

        # 2. REGISTRAR EL EGRESO
        sesion_id = obtener_sesion_caja_activa(s_id, u_id)
        cur.execute("""
            INSERT INTO egresos (sucursal_id, usuario_id, proveedor_id, descripcion, monto, tipo_documento, numero_documento, categoria, sesion_caja_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (s_id, u_id, prov_id, descripcion, monto, tipo_doc, num_doc, categoria, sesion_id))
        egreso_id = cur.lastrowid

        # 3. REGISTRAR MOVIMIENTO EN FLUJO DE CAJA
        cur.execute("""
            INSERT INTO flujo_caja (sucursal_id, usuario_id, tipo, monto, descripcion, referencia_id, tipo_referencia)
            VALUES (%s, %s, 'EGRESO', %s, %s, %s, 'EGRESO_VARIO')
        """, (s_id, u_id, monto, f"Egreso: {descripcion}", egreso_id))

        mysql.connection.commit()
        registrar_auditoria('EGRESO', f"Egreso registrado: {descripcion} por ${monto}")
        return jsonify({'success': True, 'message': 'Egreso registrado correctamente'})

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    finally:
        cur.close()

@app.route('/utilidad_real')
@login_required
@admin_required
def utilidad_real():
    cur = mysql.connection.cursor()
    s_id = session['sucursal_id']
    
    # 1. Total Ventas (Ingresos reales)
    cur.execute("SELECT SUM(total) as total FROM ventas WHERE sucursal_id = %s", (s_id,))
    total_ventas = float(cur.fetchone()['total'] or 0)
    
    # 2. Total Compras (Gastos con factura/insumos)
    cur.execute("SELECT SUM(total) as total FROM compras WHERE sucursal_id = %s", (s_id,))
    total_compras = float(cur.fetchone()['total'] or 0)
    
    # 3. Total Egresos Varios (Informales/Recibos internos)
    cur.execute("SELECT SUM(monto) as total FROM egresos WHERE sucursal_id = %s", (s_id,))
    total_egresos = float(cur.fetchone()['total'] or 0)
    
    utilidad = total_ventas - (total_compras + total_egresos)
    
    cur.close()
    return jsonify({
        'total_ventas': total_ventas,
        'total_compras': total_compras,
        'total_egresos_varios': total_egresos,
        'utilidad_neta': utilidad
    })

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
    cur.execute("SELECT COUNT(*) as total_ventas, SUM(total) as monto_total, AVG(total) as ticket_promedio FROM ventas"); st = cur.fetchone()
    
    # HISTORIAL DE CIERRES DE CAJA (SESIONES)
    cur.execute("""
        SELECT s.*, u.usuario, suc.nombre as sucursal_nombre 
        FROM sesiones_caja s 
        JOIN usuarios u ON s.usuario_id = u.id 
        JOIN sucursales suc ON s.sucursal_id = suc.id 
        WHERE s.estado = 'CERRADA' 
        ORDER BY s.fecha_cierre DESC 
        LIMIT 100
    """)
    cierres = cur.fetchall()

    # HISTORIAL DE CIERRES DIARIOS CONSOLIDADOS
    cur.execute("""
        SELECT cd.*, u.usuario, suc.nombre as sucursal_nombre 
        FROM cierres_diarios cd
        JOIN usuarios u ON cd.usuario_id = u.id
        JOIN sucursales suc ON cd.sucursal_id = suc.id
        ORDER BY cd.fecha_dia DESC
        LIMIT 100
    """)
    cierres_consolidados = cur.fetchall()

    # Por cada cierre consolidado, traer el detalle agrupado de ese día
    for c_con in cierres_consolidados:
        # Traer nombres de cajeros que estuvieron en los turnos de ese día/sucursal
        cur.execute("""
            SELECT DISTINCT u.usuario 
            FROM sesiones_caja s 
            JOIN usuarios u ON s.usuario_id = u.id 
            WHERE s.sucursal_id = %s AND DATE(s.fecha_apertura) = %s
        """, (c_con['sucursal_id'], c_con['fecha_dia']))
        cajeros_list = [row['usuario'] for row in cur.fetchall()]
        c_con['cajeros'] = ", ".join(cajeros_list)

        # Desglose global de tarjetas de ese día/sucursal
        cur.execute("""
            SELECT ct.nombre as tarjeta, SUM(v.total) as total 
            FROM ventas v 
            JOIN cat_tarjetas ct ON v.id_tarjeta = ct.id 
            WHERE v.sucursal_id = %s AND DATE(v.fecha) = %s AND v.forma_pago = 'TARJETA'
            GROUP BY ct.id
        """, (c_con['sucursal_id'], c_con['fecha_dia']))
        c_con['desglose_tarjetas'] = cur.fetchall()

        # Lista global de egresos de ese día/sucursal
        cur.execute("""
            SELECT descripcion, monto FROM egresos 
            WHERE sucursal_id = %s AND DATE(fecha) = %s
        """, (c_con['sucursal_id'], c_con['fecha_dia']))
        c_con['lista_egresos'] = cur.fetchall()
    
    cur.close()
    return render_template('reportes.html', ventas=v, top_productos=t, rentabilidad=rent, franja_horaria=hor, formas_pago=pags, insumos_criticos=crit, stats=st, cierres_caja=cierres, cierres_consolidados=cierres_consolidados)

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
