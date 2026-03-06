from datetime import datetime
import xml.etree.ElementTree as ET
import requests
import os
import base64
from endesive import xades

def procesar_factura_electronica(venta_id, mysql):
    """
    Orquesta el flujo completo: Generar XML, Firmar, Enviar a SRI y Autorizar.
    """
    try:
        cur = mysql.connection.cursor()
        
        # 1. Obtener datos necesarios
        cur.execute("""
            SELECT v.*, c.cedula_ruc, c.nombres, c.apellidos, c.direccion, c.telefono, c.email, 
                   t.codigo_sri as tipo_id_sri
            FROM ventas v 
            JOIN clientes c ON v.cliente_id = c.id
            JOIN tipos_identificacion t ON c.tipo_identificacion_id = t.id
            WHERE v.id = %s
        """, (venta_id,))
        venta = cur.fetchone()
        
        cur.execute("SELECT * FROM empresa LIMIT 1")
        empresa = cur.fetchone()
        
        cur.execute("""
            SELECT dv.*, p.codigo as codigo_principal, p.nombre as descripcion 
            FROM detalles_ventas dv 
            JOIN productos p ON dv.producto_id = p.id 
            WHERE dv.venta_id = %s
        """, (venta_id,))
        detalles = cur.fetchall()
        
        # 2. Generar XML
        xml_str = generar_xml_factura(venta, empresa, detalles)
        
        # 3. Firmar XML
        from security_utils import descifrar_password
        firma_path = os.path.join(os.path.dirname(__file__), 'certs', 'firma.p12')
        firma_pass_cifrada = empresa.get('firma_password', '')
        firma_pass = descifrar_password(firma_pass_cifrada)
        
        xml_firmado = firmar_xml_xades(xml_str, firma_path, firma_pass)
        
        if xml_firmado:
            ambiente = empresa.get('ambiente', 1) # 1 Pruebas, 2 Producción
            
            # 4. Enviar a Recepción SRI
            estado_recepcion, mensaje_recepcion = enviar_recepcion_sri(xml_firmado, ambiente)
            
            if estado_recepcion == 'RECIBIDA':
                # 5. Solicitar Autorización
                estado_aut, num_aut, xml_aut, msj_aut = solicitar_autorizacion_sri(venta['clave_acceso_sri'], ambiente)
                
                if estado_aut == 'AUTORIZADO':
                    cur.execute("""
                        UPDATE ventas 
                        SET estado_sri = 'AUTORIZADO', numero_autorizacion = %s, xml_autorizado = %s, autorizado_sri = 1 
                        WHERE id = %s
                    """, (num_aut, xml_aut, venta_id))
                else:
                    cur.execute("UPDATE ventas SET estado_sri = %s WHERE id = %s", (f"RECHAZADA: {msj_aut}", venta_id))
            else:
                cur.execute("UPDATE ventas SET estado_sri = %s WHERE id = %s", (f"DEVUELTA: {mensaje_recepcion}", venta_id))
        
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error Facturación SRI: {e}")
        return False

def generar_xml_factura(venta, empresa, detalles):
    fecha_emision = venta['fecha'].strftime('%d/%m/%Y')
    
    # Raíz
    factura = ET.Element("factura", id="comprobante", version="1.1.0")
    
    # Info Tributaria
    info_tributaria = ET.SubElement(factura, "infoTributaria")
    ET.SubElement(info_tributaria, "ambiente").text = str(empresa['ambiente'])
    ET.SubElement(info_tributaria, "tipoEmision").text = "1"
    ET.SubElement(info_tributaria, "razonSocial").text = empresa['razon_social']
    if empresa.get('nombre_comercial'):
        ET.SubElement(info_tributaria, "nombreComercial").text = empresa['nombre_comercial']
    ET.SubElement(info_tributaria, "ruc").text = empresa['ruc']
    ET.SubElement(info_tributaria, "claveAcceso").text = venta['clave_acceso_sri']
    ET.SubElement(info_tributaria, "codDoc").text = "01" # 01 = Factura
    ET.SubElement(info_tributaria, "estab").text = venta['establecimiento']
    ET.SubElement(info_tributaria, "ptoEmi").text = venta['punto_emision']
    ET.SubElement(info_tributaria, "secuencial").text = venta['secuencial']
    ET.SubElement(info_tributaria, "dirMatriz").text = empresa['direccion_matriz']
    
    # Info Factura
    info_factura = ET.SubElement(factura, "infoFactura")
    ET.SubElement(info_factura, "fechaEmision").text = fecha_emision
    ET.SubElement(info_factura, "dirEstablecimiento").text = empresa['direccion_matriz']
    ET.SubElement(info_factura, "obligadoContabilidad").text = empresa.get('obligado_contabilidad', 'NO')
    ET.SubElement(info_factura, "tipoIdentificacionComprador").text = venta['tipo_id_sri']
    ET.SubElement(info_factura, "razonSocialComprador").text = f"{venta['nombres']} {venta['apellidos']}".strip()
    ET.SubElement(info_factura, "identificacionComprador").text = venta['cedula_ruc']
    if venta.get('direccion'):
        ET.SubElement(info_factura, "direccionComprador").text = venta['direccion']
    
    ET.SubElement(info_factura, "totalSinImpuestos").text = f"{venta['subtotal_0'] + venta['subtotal_15']:.2f}"
    ET.SubElement(info_factura, "totalDescuento").text = "0.00"
    
    # Total con Impuestos
    total_con_impuestos = ET.SubElement(info_factura, "totalConImpuestos")
    
    if venta['subtotal_0'] > 0:
        ti0 = ET.SubElement(total_con_impuestos, "totalImpuesto")
        ET.SubElement(ti0, "codigo").text = "2" # IVA
        ET.SubElement(ti0, "codigoPorcentaje").text = "0" # 0%
        ET.SubElement(ti0, "baseImponible").text = f"{venta['subtotal_0']:.2f}"
        ET.SubElement(ti0, "valor").text = "0.00"
        
    if venta['subtotal_15'] > 0:
        ti15 = ET.SubElement(total_con_impuestos, "totalImpuesto")
        ET.SubElement(ti15, "codigo").text = "2" # IVA
        ET.SubElement(ti15, "codigoPorcentaje").text = "4" # 15%
        ET.SubElement(ti15, "baseImponible").text = f"{venta['subtotal_15']:.2f}"
        ET.SubElement(ti15, "valor").text = f"{venta['iva_valor']:.2f}"
    
    ET.SubElement(info_factura, "propina").text = "0.00"
    ET.SubElement(info_factura, "importeTotal").text = f"{venta['total']:.2f}"
    ET.SubElement(info_factura, "moneda").text = "DOLAR"
    
    # Pagos
    pagos = ET.SubElement(info_factura, "pagos")
    pago = ET.SubElement(pagos, "pago")
    forma_pago_sri = "01" # Efectivo
    if venta['forma_pago'] == 'TARJETA': forma_pago_sri = "19"
    if venta['forma_pago'] == 'TRANSFERENCIA': forma_pago_sri = "20"
    
    ET.SubElement(pago, "formaPago").text = forma_pago_sri
    ET.SubElement(pago, "total").text = f"{venta['total']:.2f}"
    
    # Detalles
    detalles_node = ET.SubElement(factura, "detalles")
    for d in detalles:
        detalle = ET.SubElement(detalles_node, "detalle")
        ET.SubElement(detalle, "codigoPrincipal").text = d['codigo_principal'] or str(d['producto_id'])
        ET.SubElement(detalle, "descripcion").text = d['descripcion']
        ET.SubElement(detalle, "cantidad").text = f"{d['cantidad']:.6f}"
        ET.SubElement(detalle, "precioUnitario").text = f"{d['precio_unitario']:.6f}"
        ET.SubElement(detalle, "descuento").text = "0.00"
        
        subtotal_det = d['subtotal']
        if d['iva_valor'] > 0: base_imp = subtotal_det / 1.15
        else: base_imp = subtotal_det
            
        ET.SubElement(detalle, "precioTotalSinImpuesto").text = f"{base_imp:.2f}"
        
        impuestos_det = ET.SubElement(detalle, "impuestos")
        imp_det = ET.SubElement(impuestos_det, "impuesto")
        ET.SubElement(imp_det, "codigo").text = "2"
        if d['iva_valor'] > 0:
            ET.SubElement(imp_det, "codigoPorcentaje").text = "4"
            ET.SubElement(imp_det, "tarifa").text = "15.00"
            ET.SubElement(imp_det, "baseImponible").text = f"{base_imp:.2f}"
            ET.SubElement(imp_det, "valor").text = f"{d['iva_valor']:.2f}"
        else:
            ET.SubElement(imp_det, "codigoPorcentaje").text = "0"
            ET.SubElement(imp_det, "tarifa").text = "0.00"
            ET.SubElement(imp_det, "baseImponible").text = f"{base_imp:.2f}"
            ET.SubElement(imp_det, "valor").text = "0.00"

    # Info Adicional
    info_adicional = ET.SubElement(factura, "infoAdicional")
    if venta.get('email'):
        ET.SubElement(info_adicional, "campoAdicional", nombre="Email").text = venta['email']
    if venta.get('telefono'):
        ET.SubElement(info_adicional, "campoAdicional", nombre="Telefono").text = venta['telefono']
        
    xml_string = ET.tostring(factura, encoding='utf-8', xml_declaration=True).decode('utf-8')
    return xml_string

def firmar_xml_xades(xml_str, firma_path, password):
    """
    Firma el XML utilizando XAdES-BES con la librería endesive.
    """
    try:
        if not os.path.exists(firma_path):
            print(f"ERROR: Firma no encontrada en {firma_path}")
            return None
            
        # Leer el archivo P12
        with open(firma_path, 'rb') as f:
            p12_data = f.read()
            
        # Firmar el XML
        # endesive.xades.sign requiere el XML en bytes, el P12 en bytes y la contraseña
        xml_firmado = xades.sign(xml_str.encode('utf-8'), p12_data, password.encode('utf-8'))
        
        return xml_firmado.decode('utf-8')
    except Exception as e:
        print(f"Error al firmar XML: {e}")
        return None

def enviar_recepcion_sri(xml_firmado_str, ambiente):
    """
    Envía el comprobante firmado al Web Service de Recepción del SRI.
    """
    url = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl" if ambiente == 1 else "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
    
    xml_encoded = base64.b64encode(xml_firmado_str.encode('utf-8')).decode('utf-8')
    
    soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ec="http://ec.gob.sri.ws.recepcion">
       <soapenv:Header/>
       <soapenv:Body>
          <ec:validarComprobante>
             <xml>{xml_encoded}</xml>
          </ec:validarComprobante>
       </soapenv:Body>
    </soapenv:Envelope>"""
    
    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    try:
        response = requests.post(url, data=soap_body, headers=headers, timeout=15)
        root = ET.fromstring(response.content)
        estado = root.find('.//estado')
        if estado is not None and estado.text == 'RECIBIDA':
            return 'RECIBIDA', 'OK'
        
        mensajes = root.findall('.//mensaje')
        error = " ".join([m.find('mensaje').text for m in mensajes if m.find('mensaje') is not None]) if mensajes else "Error desconocido"
        return 'DEVUELTA', error
    except Exception as e:
        return 'ERROR', str(e)

def solicitar_autorizacion_sri(clave_acceso, ambiente):
    """
    Consulta el Web Service de Autorización del SRI.
    """
    url = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl" if ambiente == 1 else "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"
    
    soap_body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ec="http://ec.gob.sri.ws.autorizacion">
       <soapenv:Header/>
       <soapenv:Body>
          <ec:autorizacionComprobante>
             <claveAccesoComprobante>{clave_acceso}</claveAccesoComprobante>
          </ec:autorizacionComprobante>
       </soapenv:Body>
    </soapenv:Envelope>"""
    
    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    try:
        response = requests.post(url, data=soap_body, headers=headers, timeout=15)
        root = ET.fromstring(response.content)
        
        autorizacion = root.find('.//autorizacion')
        if autorizacion is not None:
            estado = autorizacion.find('estado').text
            if estado == 'AUTORIZADO':
                numero_aut = autorizacion.find('numeroAutorizacion').text
                comprobante = autorizacion.find('comprobante').text
                return 'AUTORIZADO', numero_aut, comprobante, 'OK'
            
            mensajes = autorizacion.findall('.//mensaje')
            error = " ".join([m.find('mensaje').text for m in mensajes if m.find('mensaje') is not None])
            return 'RECHAZADO', None, None, error
            
        return 'ERROR', None, None, "No se recibió respuesta de autorización"
    except Exception as e:
        return 'ERROR', None, None, str(e)
