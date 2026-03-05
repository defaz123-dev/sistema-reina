# app.py - SISTEMA REINA (VERSIÓN NORMALIZADA CON CATÁLOGOS)
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime
import os
import random, csv, io, requests
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_secreta_reina_2024')

# Configuración de Base de Datos
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'sistema_reina')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# Configuraciones adicionales para estabilidad en la nube
app.config['MYSQL_CONNECT_TIMEOUT'] = 10
app.config['MYSQL_CUSTOM_OPTIONS'] = {"connect_timeout": 10}

# SSL Flexible para Aiven
if 'MYSQL_HOST' in os.environ and os.environ['MYSQL_HOST'] != 'localhost':
    app.config['MYSQL_CUSTOM_OPTIONS'] = {"ssl": {"ca": None}, "ssl_mode": "REQUIRED"} 
else:
    app.config['MYSQL_CUSTOM_OPTIONS'] = {}

mysql = MySQL(app)

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
    except Exception as e:
        file_storage.seek(0)
        return file_storage.read(), file_storage.content_type

def get_db_cursor():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SET time_zone = '-05:00'")
        return cur
    except Exception as e: return str(e)

def registrar_auditoria(accion, detalle):
    try:
        cur = mysql.connection.cursor()
        # Capturar IP real (considerando proxies/nube)
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in ip: ip = ip.split(',')[0] # Tomar la primera si hay varias
        cur.execute("INSERT INTO auditoria (usuario_id, accion, detalle, ip) VALUES (%s, %s, %s, %s)",
                    (session.get('user_id'), accion, detalle, ip))
        mysql.connection.commit(); cur.close()
    except: pass

def identificar_tipo_doc(doc):
    if doc == "9999999999": return 4 # CONSUMIDOR FINAL
    return 2 if len(doc) == 13 else 1 # RUC o CEDULA

def generar_clave_acceso_sri(fecha, ruc_empresa, ambiente):
    f = fecha.strftime('%d%m%Y')
    clave = f"{f}01{ruc_empresa}{ambiente}001001{random.randint(1,999999):09d}123456781"
    return clave[:49]

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
@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM sucursales"); s = cur.fetchall(); cur.close()
    return render_template('index.html', sucursales=s)

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        u, p, s = request.form['usuario'].lower().strip(), request.form['password'], int(request.form['sucursal'])
        cur = mysql.connection.cursor()
        cur.execute("SELECT u.*, s.nombre as sucursal_nombre FROM usuarios u JOIN sucursales s ON u.sucursal_id = s.id WHERE LOWER(u.usuario)=%s AND u.activo=1", (u,))
        user = cur.fetchone(); cur.close()
        if user and check_password_hash(user['password'], p):
            # Se elimina la validación estricta de sucursal para permitir rotación de empleados
            session.update({'user_id': user['id'], 'usuario': user['usuario'], 'rol': user['rol'], 'sucursal_id': s, 'sucursal_nombre': user['sucursal_nombre']})
            registrar_auditoria('LOGIN', f"Usuario {user['usuario']} inició sesión en sucursal ID: {s}")
            return redirect(url_for('dashboard'))
        flash('Credenciales incorrectas', 'danger')
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
    cur.execute("SELECT c.*, p.razon_social, s.nombre as sucursal_nombre FROM compras c JOIN proveedores p ON c.proveedor_id = p.id JOIN sucursales s ON c.sucursal_id = s.id ORDER BY c.fecha DESC")
    vs = cur.fetchall(); cur.close()
    return render_template('compras.html', compras=vs)

@app.route('/compras/nueva')
@login_required
@admin_required
def nueva_compra():
    cur = mysql.connection.cursor()
    cur.execute("SELECT iva_porcentaje FROM empresa LIMIT 1"); emp = cur.fetchone()
    iva_p = emp['iva_porcentaje'] if emp else 15.00
    cur.execute("SELECT p.*, t.nombre as tipo_comprobante_nombre FROM proveedores p JOIN tipos_comprobantes t ON p.tipo_comprobante_id = t.id")
    provs = cur.fetchall()
    cur.execute("SELECT * FROM sucursales"); sucs = cur.fetchall()
    cur.execute("SELECT * FROM unidades_medida"); ums = cur.fetchall()
    cur.execute("SELECT i.*, u.nombre as unidad_medida FROM insumos i JOIN unidades_medida u ON i.unidad_medida_id = u.id")
    ins = cur.fetchall(); cur.close()
    return render_template('nueva_compra.html', proveedores=provs, insumos=ins, sucursales=sucs, unidades=ums, fecha_hoy=datetime.now().strftime('%Y-%m-%d'), iva_porcentaje=iva_p)

@app.route('/compras/editar/<int:id>')
@login_required
@admin_required
def editar_compra(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT iva_porcentaje FROM empresa LIMIT 1"); emp = cur.fetchone()
    iva_p = emp['iva_porcentaje'] if emp else 15.00
    cur.execute("SELECT * FROM compras WHERE id = %s", (id,))
    compra = cur.fetchone()
    cur.execute("SELECT dc.*, i.nombre, u.nombre as unidad_medida FROM detalles_compras dc JOIN insumos i ON dc.insumo_id = i.id JOIN unidades_medida u ON i.unidad_medida_id = u.id WHERE dc.compra_id = %s", (id,))
    detalles = cur.fetchall()
    cur.execute("SELECT p.*, t.nombre as tipo_comprobante_nombre FROM proveedores p JOIN tipos_comprobantes t ON p.tipo_comprobante_id = t.id")
    provs = cur.fetchall()
    cur.execute("SELECT * FROM sucursales"); sucs = cur.fetchall()
    cur.execute("SELECT * FROM unidades_medida"); ums = cur.fetchall()
    cur.execute("SELECT i.*, u.nombre as unidad_medida FROM insumos i JOIN unidades_medida u ON i.unidad_medida_id = u.id")
    ins = cur.fetchall(); cur.close()
    return render_template('nueva_compra.html', proveedores=provs, insumos=ins, sucursales=sucs, unidades=ums, compra=compra, detalles=detalles, iva_porcentaje=iva_p)

@app.route('/compras/consultar_sri/<string:clave>')
@login_required
@admin_required
def consultar_sri(clave):
    if len(clave) != 49: return jsonify({'success': False, 'message': 'Clave debe tener 49 dígitos'})
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT ambiente FROM empresa LIMIT 1"); emp = cur.fetchone(); cur.close()
    ambiente = emp['ambiente'] if emp else 1
    
    # URL dinámica según ambiente
    if ambiente == 2: # PRODUCCIÓN
        url = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline"
    else: # PRUEBAS
        url = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline"
    
    soap_body = f"""<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ecua="http://ec.gob.sri.ws.autorizacion"><soap:Body><ecua:autorizacionComprobante><claveAccesoComprobante>{clave}</claveAccesoComprobante></ecua:autorizacionComprobante></soap:Body></soap:Envelope>"""
    try:
        headers = {'Content-Type': 'text/xml; charset=utf-8'}
        response = requests.post(url, data=soap_body, headers=headers, timeout=10)
        if response.status_code != 200: return jsonify({'success': False, 'message': f'Error de conexión con SRI (Ambiente {ambiente})'})
        root = ET.fromstring(response.content); comprobante_xml_str = ""
        for elem in root.iter('comprobante'): comprobante_xml_str = elem.text; break
        if not comprobante_xml_str: return jsonify({'success': False, 'message': f'Comprobante no encontrado en SRI (Ambiente {"Producción" if ambiente==2 else "Pruebas"})'})
        factura_root = ET.fromstring(comprobante_xml_str)
        info_t = factura_root.find('infoTributaria'); info_f = factura_root.find('infoFactura')
        
        # Extraer Detalles (Items)
        items_sri = []
        detalles_node = factura_root.find('detalles')
        if detalles_node is not None:
            for d in detalles_node.findall('detalle'):
                paga_iva = False
                impuestos = d.find('impuestos')
                if impuestos is not None:
                    for imp in impuestos.findall('impuesto'):
                        tarifa = imp.find('tarifa')
                        if tarifa is not None and float(tarifa.text) > 0: paga_iva = True; break
                
                items_sri.append({
                    'nombre': d.find('descripcion').text.upper(),
                    'cantidad': float(d.find('cantidad').text),
                    'precio_unitario': float(d.find('precioUnitario').text),
                    'subtotal': float(d.find('precioTotalSinImpuesto').text),
                    'paga_iva': paga_iva
                })

        f_sri = info_f.find('fechaEmision').text; f_parts = f_sri.split('/'); f_iso = f"{f_parts[2]}-{f_parts[1]}-{f_parts[0]}"
        return jsonify({
            'success': True, 'ruc_proveedor': info_t.find('ruc').text, 'razon_social': info_t.find('razonSocial').text,
            'establecimiento': info_t.find('estab').text, 'punto_emision': info_t.find('ptoEmi').text,
            'secuencial': info_t.find('secuencial').text, 'fecha_emision': f_iso, 'total': float(info_f.find('importeTotal').text),
            'items': items_sri
        })
    except Exception as e: return jsonify({'success': False, 'message': str(e)})

@app.route('/compras/verificar_clave/<string:clave>')
@login_required
@admin_required
def verificar_clave_compra(clave):
    compra_id = request.args.get('exclude_id')
    cur = mysql.connection.cursor()
    if compra_id:
        cur.execute("SELECT id FROM compras WHERE clave_acceso = %s AND id != %s", (clave, compra_id))
    else:
        cur.execute("SELECT id FROM compras WHERE clave_acceso = %s", (clave,))
    existe = cur.fetchone(); cur.close()
    return jsonify({'existe': True if existe else False})

@app.route('/compras/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_compra():
    data = request.get_json(); cur = mysql.connection.cursor()
    try:
        id_c = data.get('compra_id'); f = data['fecha']; cl = data.get('clave_acceso'); s_id = data.get('sucursal_id') or session['sucursal_id']
        u_id = session['user_id']
        est = data.get('establecimiento') or '001'
        pto = data.get('punto_emision') or '001'
        sec = (data.get('numero_comprobante') or '').upper()
        n_aut = data.get('numero_autorizacion')
        
        if id_c:
            cur.execute("SELECT insumo_id, cantidad FROM detalles_compras WHERE compra_id = %s", (id_c,))
            for iv in cur.fetchall(): cur.execute("UPDATE insumos SET stock_actual = stock_actual - %s WHERE id = %s", (iv['cantidad'], iv['insumo_id']))
            cur.execute("""UPDATE compras SET proveedor_id=%s, sucursal_id=%s, establecimiento=%s, punto_emision=%s, numero_comprobante=%s, 
                           total=%s, fecha=%s, clave_acceso=%s, numero_autorizacion=%s, usuario_modificacion_id=%s WHERE id=%s""", 
                        (data['proveedor_id'], s_id, est, pto, sec, data['total'], f, cl, n_aut, u_id, id_c))
            cur.execute("DELETE FROM detalles_compras WHERE compra_id = %s", (id_c,)); comp_id = id_c
        else:
            cur.execute("""INSERT INTO compras (proveedor_id, sucursal_id, establecimiento, punto_emision, numero_comprobante, total, fecha, clave_acceso, numero_autorizacion, usuario_creacion_id, usuario_modificacion_id) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                        (data['proveedor_id'], s_id, est, pto, sec, data['total'], f, cl, n_aut, u_id, u_id))
            comp_id = cur.lastrowid
        
        for i in data['items']:
            cur.execute("INSERT INTO detalles_compras (compra_id, insumo_id, cantidad, costo_unitario, subtotal, iva_valor) VALUES (%s, %s, %s, %s, %s, %s)", (comp_id, i['insumo_id'], i['cantidad'], i['costo'], i['subtotal'], i['iva_valor']))
            cur.execute("UPDATE insumos SET stock_actual = stock_actual + %s WHERE id = %s", (i['cantidad'], i['insumo_id']))
        
        mysql.connection.commit(); cur.close()
        registrar_auditoria('COMPRA', f"Guardó factura {est}-{pto}-{data['numero_comprobante']}")
        return jsonify({'success': True})
    except Exception as e: mysql.connection.rollback(); cur.close(); return jsonify({'success': False, 'message': str(e)})

@app.route('/compras/eliminar/<int:id>')
@login_required
@admin_required
def eliminar_compra(id):
    cur = mysql.connection.cursor()
    try:
        # 1. Obtener datos para auditoría y reversión de stock
        cur.execute("SELECT numero_comprobante, sucursal_id FROM compras WHERE id = %s", (id,))
        compra = cur.fetchone()
        if not compra: return redirect(url_for('compras'))

        # 2. Revertir Stock de Insumos
        cur.execute("SELECT insumo_id, cantidad FROM detalles_compras WHERE compra_id = %s", (id,))
        detalles = cur.fetchall()
        for d in detalles:
            cur.execute("UPDATE insumos SET stock_actual = stock_actual - %s WHERE id = %s", (d['cantidad'], d['insumo_id']))

        # 3. Eliminar Compra (Detalles se borran por cascada o manualmente)
        cur.execute("DELETE FROM detalles_compras WHERE compra_id = %s", (id,))
        cur.execute("DELETE FROM compras WHERE id = %s", (id,))
        
        registrar_auditoria('ELIMINAR_COMPRA', f"Eliminó factura de compra N° {compra['numero_comprobante']}")
        mysql.connection.commit(); flash('Compra eliminada y stock revertido', 'success')
    except Exception as e:
        mysql.connection.rollback(); flash(f"Error al eliminar: {str(e)}", 'danger')
    finally:
        cur.close()
    return redirect(url_for('compras'))

# --- CLIENTES ---
@app.route('/clientes')
@login_required
def clientes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT c.*, t.nombre as tipo_id_nombre FROM clientes c JOIN tipos_identificacion t ON c.tipo_identificacion_id = t.id")
    c = cur.fetchall()
    cur.execute("SELECT * FROM tipos_identificacion"); t = cur.fetchall(); cur.close()
    return render_template('clientes.html', clientes=c, tipos_id=t)

@app.route('/clientes/buscar/<string:cedula>')
@login_required
def buscar_cliente(cedula):
    cur = mysql.connection.cursor()
    cur.execute("SELECT c.*, t.nombre as tipo_id_nombre FROM clientes c JOIN tipos_identificacion t ON c.tipo_identificacion_id = t.id WHERE c.cedula_ruc=%s", (cedula,))
    c = cur.fetchone(); cur.close()
    if c: return jsonify({'success': True, 'cliente': c})
    return jsonify({'success': False, 'tipo_identificado_id': identificar_tipo_doc(cedula)})

@app.route('/clientes/guardar', methods=['POST'])
@login_required
def guardar_cliente():
    d = request.form; cur = mysql.connection.cursor(); u_id = session['user_id']
    t_id = d.get('tipo_identificacion_id') or identificar_tipo_doc(d['cedula_ruc'])
    nom, ape, dir = d['nombres'].upper(), d['apellidos'].upper(), d['direccion'].upper()
    if d.get('id'):
        cur.execute("UPDATE clientes SET cedula_ruc=%s, tipo_identificacion_id=%s, nombres=%s, apellidos=%s, direccion=%s, telefono=%s, email=%s, usuario_modificacion_id=%s WHERE id=%s", (d['cedula_ruc'], t_id, nom, ape, dir, d['telefono'], d['email'].upper(), u_id, d['id']))
    else:
        cur.execute("INSERT INTO clientes (cedula_ruc, tipo_identificacion_id, nombres, apellidos, direccion, telefono, email, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (d['cedula_ruc'], t_id, nom, ape, dir, d['telefono'], d['email'].upper(), u_id, u_id))
    mysql.connection.commit(); cur.close(); flash('Cliente guardado', 'success'); return redirect(url_for('clientes'))

@app.route('/clientes/guardar_json', methods=['POST'])
@login_required
def guardar_cliente_json():
    data = request.get_json(); cur = mysql.connection.cursor(); u_id = session['user_id']
    try:
        nom, ape, dir = data['nombres'].upper(), data['apellidos'].upper(), data.get('direccion','').upper()
        tel, eml = data.get('telefono','').upper(), data.get('email','').upper()
        t_id = data.get('tipo_identificacion_id') or identificar_tipo_doc(data['cedula_ruc'])
        cur.execute("""INSERT INTO clientes (cedula_ruc, tipo_identificacion_id, nombres, apellidos, direccion, telefono, email, usuario_creacion_id, usuario_modificacion_id) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                       ON DUPLICATE KEY UPDATE tipo_identificacion_id=%s, nombres=%s, apellidos=%s, direccion=%s, telefono=%s, email=%s, usuario_modificacion_id=%s""", 
                    (data['cedula_ruc'], t_id, nom, ape, dir, tel, eml, u_id, u_id, t_id, nom, ape, dir, tel, eml, u_id))
        mysql.connection.commit(); cur.execute("SELECT id FROM clientes WHERE cedula_ruc=%s", (data['cedula_ruc'],)); c_id = cur.fetchone()['id']; cur.close()
        return jsonify({'success': True, 'id': c_id})
    except Exception as e: return jsonify({'success': False, 'message': str(e)})

# --- INVENTARIO ---
@app.route('/inventario')
@login_required
@admin_required
def inventario():
    cur = mysql.connection.cursor()
    cur.execute("SELECT i.*, s.nombre as sucursal_nombre, u.nombre as unidad_medida FROM insumos i JOIN sucursales s ON i.sucursal_id = s.id JOIN unidades_medida u ON i.unidad_medida_id = u.id")
    i = cur.fetchall()
    cur.execute("SELECT * FROM sucursales"); sucs = cur.fetchall()
    cur.execute("SELECT * FROM unidades_medida"); ums = cur.fetchall(); cur.close()
    return render_template('inventario.html', insumos=i, sucursales=sucs, unidades=ums)

@app.route('/inventario/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_insumo():
    d = request.form; cur = mysql.connection.cursor(); u_id = session['user_id']
    nom = d['nombre'].upper(); st_min = d.get('stock_minimo', 0); suc_id = d.get('sucursal_id') or session['sucursal_id']; um_id = d.get('unidad_medida_id')
    if d.get('id'): 
        cur.execute("UPDATE insumos SET nombre=%s, stock_actual=%s, stock_minimo=%s, unidad_medida_id=%s, sucursal_id=%s, usuario_modificacion_id=%s WHERE id=%s", (nom, d['stock'], st_min, um_id, suc_id, u_id, d['id']))
        registrar_auditoria('EDITAR_INSUMO', f"Editó insumo: {nom} (ID: {d['id']})")
    else: 
        cur.execute("INSERT INTO insumos (nombre, stock_actual, stock_minimo, unidad_medida_id, sucursal_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (nom, d['stock'], st_min, um_id, suc_id, u_id, u_id))
        registrar_auditoria('CREAR_INSUMO', f"Creó insumo: {nom}")
    mysql.connection.commit(); cur.close(); return redirect(url_for('inventario'))

@app.route('/inventario/crear_ajax', methods=['POST'])
@login_required
@admin_required
def crear_insumo_ajax():
    try:
        data = request.get_json()
        cur = mysql.connection.cursor()
        u_id = session['user_id']
        nom = data['nombre'].upper()
        um_id = data['unidad_medida_id']
        suc_id = data.get('sucursal_id') or session['sucursal_id']
        
        cur.execute("INSERT INTO insumos (nombre, stock_actual, stock_minimo, unidad_medida_id, sucursal_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, 0, 0, %s, %s, %s, %s)", (nom, um_id, suc_id, u_id, u_id))
        new_id = cur.lastrowid
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'id': new_id, 'nombre': nom})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/inventario/ajustar', methods=['POST'])
@login_required
@admin_required
def ajustar_inventario():
    d = request.form; cur = mysql.connection.cursor(); u_id = session['user_id']
    ins_id, cant, tipo, mot = d['insumo_id'], float(d['cantidad']), d['tipo'], d['motivo'].upper()
    try:
        # Obtener nombre del insumo para el log
        cur.execute("SELECT nombre FROM insumos WHERE id=%s", (ins_id,))
        ins_nom = cur.fetchone()['nombre']
        
        cur.execute("INSERT INTO ajustes_inventario (insumo_id, cantidad, tipo, motivo, usuario_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (ins_id, cant, tipo, mot, u_id, u_id, u_id))
        if tipo == 'INGRESO': cur.execute("UPDATE insumos SET stock_actual = stock_actual + %s WHERE id = %s", (cant, ins_id))
        else: cur.execute("UPDATE insumos SET stock_actual = stock_actual - %s WHERE id = %s", (cant, ins_id))
        
        registrar_auditoria('AJUSTE_STOCK', f"{tipo} de {cant} en {ins_nom}. Motivo: {mot}")
        mysql.connection.commit(); flash('Ajuste realizado', 'success')
    except Exception as e: mysql.connection.rollback(); flash(str(e), 'danger')
    cur.close(); return redirect(url_for('inventario'))

# (Resto de rutas: Empresa, POS, Ventas, Usuarios, Productos, Sucursales, Categorías permanecen igual pero asegurando tracking)
# --- PRODUCTOS ---
@app.route('/productos')
@login_required
@admin_required
def productos():
    cur = mysql.connection.cursor(); cur.execute("SELECT p.*, c.nombre as categoria_nombre FROM productos p JOIN categorias c ON p.categoria_id = c.id"); p = cur.fetchall(); cur.execute("SELECT * FROM categorias"); cats = cur.fetchall(); cur.close(); return render_template('productos.html', productos=p, categorias=cats)

@app.route('/productos/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_producto():
    d = request.form; img_file = request.files.get('imagen'); cur = mysql.connection.cursor(); u_id = session['user_id']
    cod, nom = d['codigo'].upper(), d['nombre'].upper()
    
    if img_file and img_file.filename != '':
        # Procesar imagen con Pillow (Redimensión y Compresión)
        ib, mt = procesar_imagen(img_file)
        if d.get('id'): cur.execute("UPDATE productos SET codigo=%s, nombre=%s, precio=%s, categoria_id=%s, imagen=%s, mimetype=%s, usuario_modificacion_id=%s WHERE id=%s", (cod, nom, d['precio'], d['categoria_id'], ib, mt, u_id, d['id']))
        else: cur.execute("INSERT INTO productos (codigo, nombre, precio, categoria_id, imagen, mimetype, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (cod, nom, d['precio'], d['categoria_id'], ib, mt, u_id, u_id))
    else:
        if d.get('id'): cur.execute("UPDATE productos SET codigo=%s, nombre=%s, precio=%s, categoria_id=%s, usuario_modificacion_id=%s WHERE id=%s", (cod, nom, d['precio'], d['categoria_id'], u_id, d['id']))
        else: cur.execute("INSERT INTO productos (codigo, nombre, precio, categoria_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s)", (cod, nom, d['precio'], d['categoria_id'], u_id, u_id))
    
    mysql.connection.commit(); cur.close(); return redirect(url_for('productos'))

@app.route('/productos/receta/<int:producto_id>')
@login_required
@admin_required
def ver_receta(producto_id):
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM productos WHERE id=%s", (producto_id,)); p = cur.fetchone(); cur.execute("SELECT r.*, i.nombre, u.nombre as unidad_medida FROM recetas r JOIN insumos i ON r.insumo_id=i.id JOIN unidades_medida u ON i.unidad_medida_id = u.id WHERE r.producto_id=%s", (producto_id,)); r = cur.fetchall(); cur.execute("SELECT i.*, u.nombre as unidad_medida FROM insumos i JOIN unidades_medida u ON i.unidad_medida_id = u.id WHERE i.sucursal_id=%s", (session['sucursal_id'],)); i = cur.fetchall(); cur.close(); return render_template('recetas.html', producto=p, receta=r, insumos=i)

@app.route('/productos/receta/agregar', methods=['POST'])
@login_required
@admin_required
def agregar_insumo_receta():
    pi, ii, ct = request.form['producto_id'], request.form['insumo_id'], request.form['cantidad']; cur = mysql.connection.cursor(); u_id = session['user_id']
    
    # Obtener nombres para auditoría
    cur.execute("SELECT nombre FROM productos WHERE id=%s", (pi,))
    p_nom = cur.fetchone()['nombre']
    cur.execute("SELECT nombre FROM insumos WHERE id=%s", (ii,))
    i_nom = cur.fetchone()['nombre']
    
    cur.execute("INSERT INTO recetas (producto_id, insumo_id, cantidad_requerida, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s)", (pi, ii, ct, u_id, u_id))
    registrar_auditoria('AGREGAR_RECETA', f"Añadió {ct} de {i_nom} al producto {p_nom}")
    
    mysql.connection.commit(); cur.close(); return redirect(url_for('ver_receta', producto_id=pi))

@app.route('/productos/receta/eliminar/<int:id>/<int:p_id>')
@login_required
@admin_required
def eliminar_insumo_receta(id, p_id):
    cur = mysql.connection.cursor()
    
    # Obtener nombres para auditoría antes de borrar
    cur.execute("SELECT p.nombre as prod, i.nombre as ins FROM recetas r JOIN productos p ON r.producto_id=p.id JOIN insumos i ON r.insumo_id=i.id WHERE r.id=%s", (id,))
    data = cur.fetchone()
    
    cur.execute("DELETE FROM recetas WHERE id=%s", (id,))
    if data: registrar_auditoria('ELIMINAR_RECETA', f"Eliminó {data['ins']} de la receta de {data['prod']}")
    
    mysql.connection.commit(); cur.close(); return redirect(url_for('ver_receta', producto_id=p_id))

@app.route('/auditoria')
@login_required
@admin_required
def ver_auditoria():
    cur = mysql.connection.cursor(); cur.execute("SELECT a.*, u.usuario FROM auditoria a LEFT JOIN usuarios u ON a.usuario_id = u.id ORDER BY a.fecha DESC LIMIT 500"); logs = cur.fetchall(); cur.close(); return render_template('auditoria.html', logs=logs)

# --- CONFIGURACIÓN RESTO (Usuarios, Sucursales, Categorías, Empresa, POS) ---
# (Implementados con la misma lógica de tracking)

@app.route('/usuarios')
@login_required
@admin_required
def usuarios():
    cur = mysql.connection.cursor(); cur.execute("SELECT u.*, s.nombre as sucursal_nombre FROM usuarios u LEFT JOIN sucursales s ON u.sucursal_id=s.id"); u = cur.fetchall(); cur.execute("SELECT * FROM sucursales"); s = cur.fetchall(); cur.close(); return render_template('usuarios.html', usuarios=u, sucursales=s)

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

@app.route('/proveedores')
@login_required
@admin_required
def proveedores():
    cur = mysql.connection.cursor()
    cur.execute("SELECT p.*, t.nombre as tipo_comprobante FROM proveedores p JOIN tipos_comprobantes t ON p.tipo_comprobante_id = t.id")
    p = cur.fetchall()
    cur.execute("SELECT * FROM tipos_comprobantes"); t = cur.fetchall(); cur.close()
    return render_template('proveedores.html', proveedores=p, tipos=t)

@app.route('/proveedores/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_proveedor():
    d = request.form; cur = mysql.connection.cursor(); u_id = session['user_id']
    ruc = d['ruc']; razon = d['razon_social'].upper(); nombre = d['nombre_comercial'].upper()
    dire = d['direccion'].upper(); tel = d['telefono']; eml = d['email'].upper(); tipo_comp = d['tipo_comprobante_id']
    try:
        if d.get('id'): 
            cur.execute("UPDATE proveedores SET ruc=%s, razon_social=%s, nombre_comercial=%s, direccion=%s, telefono=%s, email=%s, tipo_comprobante_id=%s, usuario_modificacion_id=%s WHERE id=%s", (ruc, razon, nombre, dire, tel, eml, tipo_comp, u_id, d['id']))
            registrar_auditoria('EDITAR_PROVEEDOR', f"Editó proveedor: {razon}")
        else: 
            cur.execute("INSERT INTO proveedores (ruc, razon_social, nombre_comercial, direccion, telefono, email, tipo_comprobante_id, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (ruc, razon, nombre, dire, tel, eml, tipo_comp, u_id, u_id))
            registrar_auditoria('CREAR_PROVEEDOR', f"Creó proveedor: {razon}")
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
    d = request.form; cur = mysql.connection.cursor(); nom = d['nombre'].upper(); u_id = session['user_id']
    if d.get('id'): cur.execute("UPDATE sucursales SET nombre=%s, usuario_modificacion_id=%s WHERE id=%s", (nom, u_id, d['id']))
    else: cur.execute("INSERT INTO sucursales (nombre, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s)", (nom, u_id, u_id))
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
    d = request.form; cur = mysql.connection.cursor(); nom = d['nombre'].upper(); u_id = session['user_id']
    if d.get('id'): cur.execute("UPDATE categorias SET nombre=%s, usuario_modificacion_id=%s WHERE id=%s", (nom, u_id, d['id']))
    else: cur.execute("INSERT INTO categorias (nombre, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s)", (nom, u_id, u_id))
    mysql.connection.commit(); cur.close(); return redirect(url_for('categorias'))

@app.route('/empresa')
@login_required
@admin_required
def configuracion_empresa():
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM empresa LIMIT 1"); e = cur.fetchone(); cur.close(); return render_template('empresa.html', empresa=e)

@app.route('/empresa/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_empresa():
    d = request.form; cur = mysql.connection.cursor(); u_id = session['user_id']
    ruc, razon, nom, dir = d['ruc'], d['razon_social'].upper(), d['nombre_comercial'].upper(), d['direccion_matriz'].upper()
    iva = d.get('iva_porcentaje', 15.00)
    if d.get('id'): cur.execute("UPDATE empresa SET ruc=%s, razon_social=%s, nombre_comercial=%s, direccion_matriz=%s, iva_porcentaje=%s, ambiente=%s, usuario_modificacion_id=%s WHERE id=%s", (ruc, razon, nom, dir, iva, d['ambiente'], u_id, d['id']))
    else: cur.execute("INSERT INTO empresa (ruc, razon_social, nombre_comercial, direccion_matriz, iva_porcentaje, ambiente, usuario_creacion_id, usuario_modificacion_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (ruc, razon, nom, dir, iva, d['ambiente'], u_id, u_id))
    mysql.connection.commit(); cur.close(); flash('Datos guardados', 'success'); return redirect(url_for('configuracion_empresa'))

@app.route('/pos')
@login_required
def pos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categorias")
    c = cur.fetchall()
    
    # Obtener IVA parametrizado
    cur.execute("SELECT iva_porcentaje FROM empresa LIMIT 1")
    emp = cur.fetchone()
    iva_p = emp['iva_porcentaje'] if emp else 15.00
    
    query_productos = """
        SELECT p.id, p.codigo, p.nombre, p.precio, p.categoria_id, IF(p.imagen IS NOT NULL, 1, 0) as tiene_foto,
        (
            SELECT MIN(FLOOR(i.stock_actual / r.cantidad_requerida))
            FROM recetas r
            JOIN insumos i ON r.insumo_id = i.id
            WHERE r.producto_id = p.id AND i.sucursal_id = %s
        ) as stock_disponible
        FROM productos p
    """
    cur.execute(query_productos, (session['sucursal_id'],))
    p = cur.fetchall()
    cur.close()
    
    for prod in p:
        if prod['stock_disponible'] is None:
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) as cuenta FROM recetas WHERE producto_id = %s", (prod['id'],))
            tiene_receta = cur.fetchone()['cuenta'] > 0
            cur.close()
            prod['stock_disponible'] = 0 if tiene_receta else 999

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tipos_identificacion")
    ti = cur.fetchall()
    cur.close()

    return render_template('pos.html', categorias=c, productos=p, tipos_id=ti, iva_porcentaje=iva_p)

@app.route('/pos/venta', methods=['POST'])
@login_required
def procesar_venta_v2():
    data = request.get_json(); cur = mysql.connection.cursor(); u_id = session['user_id']
    try:
        c_id = data.get('cliente_id'); fpago = data.get('forma_pago', 'EFECTIVO').upper()
        s_id = session['sucursal_id']
        
        # 1. Obtener datos de empresa e IVA dinámico
        cur.execute("SELECT ruc, ambiente, iva_porcentaje FROM empresa LIMIT 1"); emp = cur.fetchone()
        ruc = emp['ruc'] if emp else "1790000000001"; amb = emp['ambiente'] if emp else 1
        iva_p = float(emp['iva_porcentaje']) if emp else 15.00
        divisor_iva = 1 + (iva_p / 100)
        clave = generar_clave_acceso_sri(datetime.now(), ruc, amb)

        # 2. Insertar Cabecera
        cur.execute("""INSERT INTO ventas 
            (usuario_id, sucursal_id, cliente_id, subtotal_0, subtotal_15, iva_valor, total, forma_pago, clave_acceso_sri, estado_sri, usuario_creacion_id, usuario_modificacion_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'AUTORIZADO', %s, %s)""", 
            (u_id, s_id, c_id, data.get('subtotal_0', 0), data.get('subtotal_15', 0), 
             data.get('iva_valor', 0), data['total'], fpago, clave, u_id, u_id))
        v_id = cur.lastrowid

        # 3. Procesar Items
        for i in data['items']:
            item_total = float(i['precio']) * int(i['cantidad'])
            item_iva = item_total - (item_total / divisor_iva)
            
            cur.execute("INSERT INTO detalles_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal, iva_valor) VALUES (%s, %s, %s, %s, %s, %s)", 
                        (v_id, i['id'], i['cantidad'], i['precio'], item_total, item_iva))
            
            cur.execute("SELECT insumo_id, cantidad_requerida FROM recetas WHERE producto_id=%s", (i['id'],))
            for ing in cur.fetchall():
                cur.execute("UPDATE insumos SET stock_actual=stock_actual-%s WHERE id=%s AND sucursal_id=%s", 
                            (float(ing['cantidad_requerida']) * int(i['cantidad']), ing['insumo_id'], s_id))
        
        mysql.connection.commit(); registrar_auditoria('VENTA', f"Venta registrada ID: {v_id} por ${data['total']}")
        return jsonify({'success': True, 'venta_id': v_id})
    except Exception as e:
        mysql.connection.rollback(); return jsonify({'success': False, 'message': str(e)})
    finally: cur.close()

@app.route('/ventas')
@login_required
def historial_ventas():
    cur = mysql.connection.cursor(); cur.execute("SELECT v.*, c.nombres, c.apellidos, u.usuario FROM ventas v JOIN clientes c ON v.cliente_id=c.id JOIN usuarios u ON v.usuario_id=u.id ORDER BY v.fecha DESC"); v = cur.fetchall(); cur.close(); return render_template('ventas.html', ventas=v)

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

@app.route('/reportes')
@login_required
@admin_required
def reportes():
    cur = mysql.connection.cursor(); cur.execute("SELECT v.*, c.nombres, c.apellidos, u.usuario FROM ventas v JOIN clientes c ON v.cliente_id=c.id JOIN usuarios u ON v.usuario_id=u.id ORDER BY v.fecha DESC"); v = cur.fetchall()
    cur.execute("SELECT p.nombre, SUM(dv.cantidad) as total_vendido FROM detalles_ventas dv JOIN productos p ON dv.producto_id=p.id GROUP BY p.id ORDER BY total_vendido DESC LIMIT 5"); t = cur.fetchall(); cur.close(); return render_template('reportes.html', ventas=v, top_productos=t)

@app.route('/producto/imagen/<int:id>')
def producto_imagen(id):
    cur = mysql.connection.cursor(); cur.execute("SELECT imagen, mimetype FROM productos WHERE id=%s", (id,)); p = cur.fetchone(); cur.close()
    if p and p['imagen']: return Response(p['imagen'], mimetype=p['mimetype'] or 'image/jpeg')
    return redirect(url_for('static', filename='img/default.png'))

if __name__ == '__main__':
    app.run(debug=True)
