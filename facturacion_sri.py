from datetime import datetime
import requests
import os
import base64
import time
import unicodedata
import io
import uuid
from lxml import etree, builder
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from endesive import xades

def log_sri(mensaje):
    with open("sri_debug.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mensaje}\n")

def limpiar_texto(texto):
    if not texto: return ""
    texto = str(texto)
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('ñ', 'n').replace('Ñ', 'N')

# --- CLASE PERSONALIZADA PARA FIRMA SRI ECUADOR ---
class SRI_BES(xades.BES):
    def enveloped_sri(self, data, cert, certcontent, signproc):
        """
        Versión modificada de endesive.xades.bes.enveloped para cumplir con el SRI Ecuador.
        Cambia URI="" por URI="#comprobante".
        """
        tree = etree.parse(io.BytesIO(data))
        signedobj = tree.getroot()
        
        # El SRI requiere canonicalización C14N
        canonicalizedxml = self._c14n(signedobj, "")
        digestvalue1 = self.sha256(canonicalizedxml)

        nsmap = signedobj.nsmap.copy()
        nsmap.update({
            "xades": "http://uri.etsi.org/01903/v1.3.2#",
            "ds": "http://www.w3.org/2000/09/xmldsig#",
        })
        siXADES = builder.ElementMaker(namespace="http://uri.etsi.org/01903/v1.3.2#", nsmap=nsmap)
        siDS = builder.ElementMaker(namespace="http://www.w3.org/2000/09/xmldsig#", nsmap={"ds": "http://www.w3.org/2000/09/xmldsig#"})

        certdigest = self.sha256(certcontent)
        certcontent_b64 = self.base64(certcontent)
        certserialnumber = "%d" % cert.serial_number
        certissuer = self.get_rdns_name(cert.issuer.rdns)

        signedproperties = siXADES.SignedProperties(
            siXADES.SignedSignatureProperties(
                siXADES.SigningTime(self.time),
                siXADES.SigningCertificate(
                    siXADES.Cert(
                        siXADES.CertDigest(
                            xades.bes.DigestMethod(Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"),
                            xades.bes.DigestValue(certdigest),
                        ),
                        siXADES.IssuerSerial(
                            xades.bes.X509IssuerName(certissuer),
                            xades.bes.X509SerialNumber(certserialnumber),
                        ),
                    )
                ),
                Id="SignedSignatureProperties_" + self.guid + self.mapa["_02"],
            ),
            siXADES.SignedDataObjectProperties(
                siXADES.DataObjectFormat(
                    siXADES.Description('MIME-Version: 1.0\nContent-Type: text/xml'),
                    siXADES.MimeType("text/xml"),
                    ObjectReference="#Reference1_" + self.guid + self.mapa["_2f"],
                ),
                Id="SignedDataObjectProperties_" + self.guid + self.mapa["_43"],
            ),
            Id="SignedProperties_" + self.guid + self.mapa["_46"],
        )

        canonicalizedxml_props = self._c14n(signedproperties, "")
        digestvalue2 = self.sha256(canonicalizedxml_props)

        unsignedproperties = self.unsignedpropertied(digestvalue2, None, None, "sha256")

        signedinfo = xades.bes.SignedInfo(
            xades.bes.CanonicalizationMethod(Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"),
            xades.bes.SignatureMethod(Algorithm='http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'),
            xades.bes.Reference(
                xades.bes.Transforms(
                    xades.bes.Transform(
                        xades.bes.XPath("not(ancestor-or-self::ds:Signature)"),
                        Algorithm="http://www.w3.org/TR/1999/REC-xpath-19991116",
                    ),
                    xades.bes.Transform(Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315")
                ),
                xades.bes.DigestMethod(Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"),
                xades.bes.DigestValue(digestvalue1),
                Id="Reference1_" + self.guid + self.mapa["_2f"],
                URI="#comprobante", # CAMBIO CRÍTICO PARA SRI ECUADOR
            ),
            xades.bes.Reference(
                xades.bes.DigestMethod(Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"),
                xades.bes.DigestValue(digestvalue2),
                Id="SignedProperties-Reference_" + self.guid + self.mapa["_20"],
                Type="http://uri.etsi.org/01903#SignedProperties",
                URI="#SignedProperties_" + self.guid + self.mapa["_46"],
            ),
            Id="SignedInfo_" + self.guid + self.mapa["_49"],
        )

        canonicalizedxml_si = self._c14n(signedinfo, "")
        signature = signproc(canonicalizedxml_si, "sha256")
        actualdigestencoded = base64.b64encode(signature).decode()
        
        # Formatear la firma en bloques de 64 caracteres
        digestvalue3 = "\n".join([actualdigestencoded[i:i+64] for i in range(0, len(actualdigestencoded), 64)])

        DOC = xades.bes.Signature(
            signedinfo,
            xades.bes.SignatureValue(digestvalue3, Id="SignatureValue_" + self.guid + self.mapa["_5a"]),
            xades.bes.KeyInfo(
                xades.bes.X509Data(xades.bes.X509Certificate(certcontent_b64)),
                Id="KeyInfo_" + self.guid + self.mapa["_2c"],
            ),
            xades.bes.Object(
                siXADES.QualifyingProperties(
                    signedproperties,
                    unsignedproperties,
                    Id="QualifyingProperties_" + self.guid + self.mapa["_4b"],
                    Target="#Signature_" + self.guid + self.mapa["_11"],
                )
            ),
            Id="Signature_" + self.guid + self.mapa["_11"],
        )

        signedobj.append(DOC)
        return tree

def procesar_factura_electronica(venta_id, mysql):
    cur = mysql.connection.cursor()
    try:
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
        
        if not empresa: raise Exception("Empresa no configurada.")
        ambiente = empresa.get('ambiente', 1)
        clave = venta['clave_acceso_sri']

        log_sri(f"--- INICIO VENTA {venta_id} ({clave}) ---")

        # 1. CONSULTA PREVIA
        estado_aut, num_aut, xml_aut, msj_aut = solicitar_autorizacion_sri(clave, ambiente)
        if estado_aut == 'AUTORIZADO':
            cur.execute("""UPDATE ventas SET estado_sri = 'AUTORIZADO', numero_autorizacion = %s, xml_autorizado = %s, autorizado_sri = 1 WHERE id = %s""", (num_aut, xml_aut, venta_id))
            mysql.connection.commit()
            return True

        # 2. GENERAR Y FIRMAR
        cur.execute("""
            SELECT dv.*, p.codigo as codigo_principal, p.nombre as descripcion 
            FROM detalles_ventas dv 
            JOIN productos p ON dv.producto_id = p.id 
            WHERE dv.venta_id = %s
        """, (venta_id,))
        detalles = cur.fetchall()
        
        xml_bytes = generar_xml_factura_bytes(venta, empresa, detalles)
        
        from security_utils import descifrar_password
        firma_path = os.path.join(os.path.dirname(__file__), 'certs', 'firma.p12')
        firma_pass = descifrar_password(empresa.get('firma_password', ''))
        
        if not os.path.exists(firma_path): raise Exception("Certificado .p12 no encontrado.")

        # FIRMA CON MOTOR SRI PERSONALIZADO
        with open(firma_path, 'rb') as f: p12_data = f.read()
        p_key, cert, o_certs = pkcs12.load_key_and_certificates(p12_data, firma_pass.encode('utf-8'))
        c_bytes = cert.public_bytes(serialization.Encoding.DER)
        def signproc(data, hashalgo): return p_key.sign(data, padding.PKCS1v15(), getattr(hashes, hashalgo.upper())())
        
        sri_signer = SRI_BES()
        signed_tree = sri_signer.enveloped_sri(xml_bytes, cert, c_bytes, signproc)
        xml_firmado_str = etree.tostring(signed_tree, encoding='UTF-8', xml_declaration=True, standalone=None).decode('utf-8')
        
        # 3. ENVIAR
        estado_recepcion, mensaje_recepcion = enviar_recepcion_sri(xml_firmado_str, ambiente)
        
        if (estado_recepcion == 'RECIBIDA') or ("EN PROCESAMIENTO" in mensaje_recepcion.upper()):
            time.sleep(5)
            for intento in range(3):
                estado_aut, num_aut, xml_aut, msj_aut = solicitar_autorizacion_sri(clave, ambiente)
                if estado_aut == 'AUTORIZADO':
                    cur.execute("""UPDATE ventas SET estado_sri = 'AUTORIZADO', numero_autorizacion = %s, xml_autorizado = %s, autorizado_sri = 1 WHERE id = %s""", (num_aut, xml_aut, venta_id))
                    mysql.connection.commit()
                    return True
                time.sleep(3)
            cur.execute("UPDATE ventas SET estado_sri = 'PENDIENTE DE AUTORIZACION' WHERE id = %s", (venta_id,))
            mysql.connection.commit()
            return False # Retornamos False porque no se autorizó en este ciclo
        else:
            cur.execute("UPDATE ventas SET estado_sri = %s WHERE id = %s", (f"DEVUELTA: {mensaje_recepcion}"[:500], venta_id))
            mysql.connection.commit()
            return False # Retornamos False porque fue devuelta
        
    except Exception as e:
        error_msg = str(e)
        log_sri(f"ERROR: {error_msg}")
        cur.execute("UPDATE ventas SET estado_sri = %s WHERE id = %s", (f"ERROR: {error_msg}"[:500], venta_id))
        mysql.connection.commit()
        return False
    finally: cur.close()

def generar_xml_factura_bytes(venta, empresa, detalles):
    fecha_emision = venta['fecha'].strftime('%d/%m/%Y')
    sub0 = float(venta.get('subtotal_0') or 0); sub15 = float(venta.get('subtotal_15') or 0)
    iva = float(venta.get('iva_valor') or 0); total = float(venta.get('total') or 0)

    root = etree.Element("factura", id="comprobante", version="1.1.0")
    it = etree.SubElement(root, "infoTributaria")
    etree.SubElement(it, "ambiente").text = str(empresa['ambiente'])
    etree.SubElement(it, "tipoEmision").text = "1"
    etree.SubElement(it, "razonSocial").text = limpiar_texto(empresa['razon_social'])
    if empresa.get('nombre_comercial'): etree.SubElement(it, "nombreComercial").text = limpiar_texto(empresa['nombre_comercial'])
    etree.SubElement(it, "ruc").text = str(empresa['ruc'])
    etree.SubElement(it, "claveAcceso").text = str(venta['clave_acceso_sri'])
    etree.SubElement(it, "codDoc").text = "01"
    etree.SubElement(it, "estab").text = str(venta.get('establecimiento') or '001').zfill(3)
    etree.SubElement(it, "ptoEmi").text = str(venta.get('punto_emision') or '001').zfill(3)
    etree.SubElement(it, "secuencial").text = str(venta.get('secuencial') or '000000001').zfill(9)
    etree.SubElement(it, "dirMatriz").text = limpiar_texto(empresa['direccion_matriz'])
    
    inf = etree.SubElement(root, "infoFactura")
    etree.SubElement(inf, "fechaEmision").text = fecha_emision
    etree.SubElement(inf, "dirEstablecimiento").text = limpiar_texto(empresa['direccion_matriz'])
    etree.SubElement(inf, "obligadoContabilidad").text = empresa.get('obligado_contabilidad', 'NO')
    etree.SubElement(inf, "tipoIdentificacionComprador").text = str(venta['tipo_id_sri']).zfill(2)
    etree.SubElement(inf, "razonSocialComprador").text = limpiar_texto(f"{venta['nombres']} {venta['apellidos']}")
    etree.SubElement(inf, "identificacionComprador").text = str(venta['cedula_ruc'])
    if venta.get('direccion'): etree.SubElement(inf, "direccionComprador").text = limpiar_texto(venta['direccion'])
    
    etree.SubElement(inf, "totalSinImpuestos").text = f"{sub0 + sub15:.2f}"
    etree.SubElement(inf, "totalDescuento").text = "0.00"
    tci = etree.SubElement(inf, "totalConImpuestos")
    if sub15 > 0:
        ti = etree.SubElement(tci, "totalImpuesto")
        etree.SubElement(ti, "codigo").text = "2"; etree.SubElement(ti, "codigoPorcentaje").text = "4"
        etree.SubElement(ti, "baseImponible").text = f"{sub15:.2f}"; etree.SubElement(ti, "valor").text = f"{iva:.2f}"
    if sub0 > 0:
        ti = etree.SubElement(tci, "totalImpuesto")
        etree.SubElement(ti, "codigo").text = "2"; etree.SubElement(ti, "codigoPorcentaje").text = "0"
        etree.SubElement(ti, "baseImponible").text = f"{sub0:.2f}"; etree.SubElement(ti, "valor").text = "0.00"
    etree.SubElement(inf, "propina").text = "0.00"; etree.SubElement(inf, "importeTotal").text = f"{total:.2f}"; etree.SubElement(inf, "moneda").text = "DOLAR"
    pag = etree.SubElement(inf, "pagos"); p = etree.SubElement(pag, "pago")
    fp = "01"
    if venta['forma_pago'] == 'TARJETA': fp = "19"
    elif venta['forma_pago'] == 'TRANSFERENCIA': fp = "20"
    etree.SubElement(p, "formaPago").text = fp; etree.SubElement(p, "total").text = f"{total:.2f}"
    etree.SubElement(p, "plazo").text = "0"; etree.SubElement(p, "unidadTiempo").text = "dias"
    dets = etree.SubElement(root, "detalles")
    for d in detalles:
        det = etree.SubElement(dets, "detalle")
        etree.SubElement(det, "codigoPrincipal").text = str(d['codigo_principal'] or d['producto_id'])[:25]
        etree.SubElement(det, "descripcion").text = limpiar_texto(d['descripcion'])
        etree.SubElement(det, "cantidad").text = f"{float(d['cantidad']):.6f}"
        etree.SubElement(det, "precioUnitario").text = f"{float(d['precio_unitario']):.6f}"
        etree.SubElement(det, "descuento").text = "0.00"
        s_det = float(d['subtotal']); i_det = float(d['iva_valor'])
        b_det = s_det / 1.15 if i_det > 0 else s_det
        etree.SubElement(det, "precioTotalSinImpuesto").text = f"{b_det:.2f}"
        imps = etree.SubElement(det, "impuestos"); imp = etree.SubElement(imps, "impuesto")
        etree.SubElement(imp, "codigo").text = "2"
        if i_det > 0:
            etree.SubElement(imp, "codigoPorcentaje").text = "4"; etree.SubElement(imp, "tarifa").text = "15.00"
            etree.SubElement(imp, "baseImponible").text = f"{b_det:.2f}"; etree.SubElement(imp, "valor").text = f"{i_det:.2f}"
        else:
            etree.SubElement(imp, "codigoPorcentaje").text = "0"; etree.SubElement(imp, "tarifa").text = "0.00"
            etree.SubElement(imp, "baseImponible").text = f"{b_det:.2f}"; etree.SubElement(imp, "valor").text = "0.00"
    return etree.tostring(root, encoding='UTF-8', xml_declaration=False)

def enviar_recepcion_sri(xml_firmado_str, ambiente):
    url = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl" if ambiente == 1 else "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
    xml_encoded = base64.b64encode(xml_firmado_str.encode('utf-8')).decode('utf-8')
    soap = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ec="http://ec.gob.sri.ws.recepcion"><soapenv:Header/><soapenv:Body><ec:validarComprobante><xml>{xml_encoded}</xml></ec:validarComprobante></soapenv:Body></soapenv:Envelope>"""
    try:
        res = requests.post(url, data=soap, headers={'Content-Type': 'text/xml; charset=utf-8'}, timeout=25)
        root = etree.fromstring(res.content)
        st = root.xpath("//*[local-name()='estado']/text()")
        if st and st[0] == 'RECIBIDA': return 'RECIBIDA', 'OK'
        msgs = root.xpath("//*[local-name()='mensaje']/*[local-name()='mensaje']/text()")
        return 'DEVUELTA', " | ".join(msgs) if msgs else "Error Recepcion"
    except Exception as e: return 'ERROR', str(e)

def consultar_comprobante_sri(clave):
    """
    Consulta una factura en el SRI por clave de acceso y extrae los datos para importación.
    """
    # Determinamos ambiente por la clave (dígito 24)
    ambiente = int(clave[23])
    estado, num_aut, xml_str, msj = solicitar_autorizacion_sri(clave, ambiente)
    
    if estado != 'AUTORIZADO':
        return None

    try:
        root = etree.fromstring(xml_str.encode('utf-8'))
        # El XML del SRI a veces viene con el comprobante dentro de un CDATA o como nodo hijo
        factura_xml = root
        if root.tag != 'factura':
            fact_node = root.find('.//factura')
            if fact_node is not None: factura_xml = fact_node
            else:
                # Intentar parsear el contenido de <comprobante>
                comp_text = root.find('.//comprobante').text
                factura_xml = etree.fromstring(comp_text.encode('utf-8'))

        it = factura_xml.find('infoTributaria')
        inf = factura_xml.find('infoFactura')
        
        datos = {
            'razon_social': it.find('razonSocial').text,
            'ruc_proveedor': it.find('ruc').text,
            'establecimiento': it.find('estab').text,
            'punto_emision': it.find('ptoEmi').text,
            'secuencial': it.find('secuencial').text,
            'fecha_emision': datetime.strptime(inf.find('fechaEmision').text, '%d/%m/%Y').strftime('%Y-%m-%d'),
            'total': float(inf.find('importeTotal').text),
            'razon_social_comprador': inf.find('razonSocialComprador').text,
            'items': []
        }

        for d in factura_xml.find('detalles').findall('detalle'):
            paga_iva = False
            for imp in d.find('impuestos').findall('impuesto'):
                if imp.find('codigo').text == '2' and imp.find('codigoPorcentaje').text in ['2', '3', '4', '10']:
                    paga_iva = True
            
            datos['items'].append({
                'nombre': d.find('descripcion').text,
                'cantidad': float(d.find('cantidad').text),
                'precio_unitario': float(d.find('precioUnitario').text),
                'subtotal': float(d.find('precioTotalSinImpuesto').text),
                'paga_iva': paga_iva
            })
        
        return datos
    except Exception as e:
        log_sri(f"Error parseando XML importacion: {str(e)}")
        return None

def anular_factura_sri(venta_id, motivo, mysql, usuario_id):
    """
    Anula una factura generando y autorizando una NOTA DE CRÉDITO (04).
    Reutiliza la clave si ya se intentó anular antes.
    """
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT v.*, c.cedula_ruc, c.nombres, c.apellidos, c.direccion, c.telefono, c.email, 
                   t.codigo_sri as tipo_id_sri
            FROM ventas v 
            JOIN clientes c ON v.cliente_id = c.id
            JOIN tipos_identificacion t ON c.tipo_identificacion_id = t.id
            WHERE v.id = %s
        """, (venta_id,))
        venta = cur.fetchone()
        if not venta: raise Exception("Factura no encontrada.")
        if not venta['autorizado_sri']: raise Exception("Solo se pueden anular facturas autorizadas.")
        
        cur.execute("SELECT * FROM empresa LIMIT 1")
        empresa = cur.fetchone()
        ambiente = empresa.get('ambiente', 1)
        
        # VERIFICAR SI YA EXISTE UN INTENTO DE ANULACIÓN (NOTA DE CRÉDITO)
        cur.execute("SELECT * FROM anulaciones_factura WHERE venta_id = %s", (venta_id,))
        anulacion_previa = cur.fetchone()
        
        if anulacion_previa and anulacion_previa['nc_clave_acceso']:
            clave_nc = anulacion_previa['nc_clave_acceso']
            fecha_nc = anulacion_previa['fecha_solicitud']
            log_sri(f"REUTILIZANDO CLAVE NC: {clave_nc}")
        else:
            # Generar Clave de Acceso Nueva para la Nota de Crédito
            fecha_nc = datetime.now()
            sec_nc = str(venta['secuencial']).zfill(9) 
            serie = f"{venta['establecimiento']}{venta['punto_emision']}"
            ruc_empresa = empresa['ruc']
            f_str = fecha_nc.strftime('%d%m%Y')
            c_48 = f"{f_str}04{ruc_empresa}{ambiente}{serie}{sec_nc}876543211"
            from app import calcular_modulo11
            clave_nc = f"{c_48}{calcular_modulo11(c_48)}"
            
            # Registrar solicitud inicial si no existe
            if not anulacion_previa:
                cur.execute("""
                    INSERT INTO anulaciones_factura (venta_id, motivo_anulacion, usuario_id, estado_anulacion, nc_clave_acceso) 
                    VALUES (%s, %s, %s, 'PENDIENTE', %s)
                """, (venta_id, motivo, usuario_id, clave_nc))
                mysql.connection.commit()

        log_sri(f"--- PROCESANDO NOTA DE CRÉDITO PARA VENTA {venta_id} ({clave_nc}) ---")

        # 1. CONSULTA PREVIA (Por si ya se autorizó y hubo error de red antes)
        est_aut, num_aut, xml_aut, msj_aut = solicitar_autorizacion_sri(clave_nc, ambiente)
        if est_aut == 'AUTORIZADO':
            cur.execute("""
                UPDATE anulaciones_factura 
                SET estado_anulacion = 'PROCESADO', nc_numero_autorizacion = %s, 
                    nc_xml_autorizado = %s, mensaje_sri = 'AUTORIZADO (RECUPERADO)'
                WHERE venta_id = %s
            """, (num_aut, xml_aut, venta_id))
            cur.execute("UPDATE ventas SET anulada = 1, estado_sri = 'ANULADA' WHERE id = %s", (venta_id,))
            mysql.connection.commit()
            return True, "Anulación sincronizada y autorizada."

        # 2. GENERAR XML Y FIRMAR (Solo si no estaba autorizada)
        cur.execute("""
            SELECT dv.*, p.codigo as codigo_principal, p.nombre as descripcion 
            FROM detalles_ventas dv 
            JOIN productos p ON dv.producto_id = p.id 
            WHERE dv.venta_id = %s
        """, (venta_id,))
        detalles = cur.fetchall()
        xml_nc_bytes = generar_xml_nota_credito_bytes(venta, empresa, detalles, motivo, clave_nc, fecha_nc)
        
        from security_utils import descifrar_password
        firma_path = os.path.join(os.path.dirname(__file__), 'certs', 'firma.p12')
        firma_pass = descifrar_password(empresa.get('firma_password', ''))
        
        with open(firma_path, 'rb') as f: p12_data = f.read()
        p_key, cert, o_certs = pkcs12.load_key_and_certificates(p12_data, firma_pass.encode('utf-8'))
        c_bytes = cert.public_bytes(serialization.Encoding.DER)
        def signproc(data, hashalgo): return p_key.sign(data, padding.PKCS1v15(), getattr(hashes, hashalgo.upper())())
        
        sri_signer = SRI_BES()
        signed_tree = sri_signer.enveloped_sri(xml_nc_bytes, cert, c_bytes, signproc)
        xml_firmado_str = etree.tostring(signed_tree, encoding='UTF-8', xml_declaration=True, standalone=None).decode('utf-8')

        # 3. ENVIAR AL SRI
        estado_recepcion, msj_recepcion = enviar_recepcion_sri(xml_firmado_str, ambiente)
        
        if estado_recepcion == 'RECIBIDA' or "EN PROCESAMIENTO" in msj_recepcion.upper():
            # Actualizar estado visual inmediatamente
            cur.execute("UPDATE ventas SET estado_sri = 'ANULACIÓN EN PROCESO' WHERE id = %s", (venta_id,))
            mysql.connection.commit()
            
            time.sleep(4)
            for i in range(3):
                est_aut, num_aut, xml_aut, msj_aut = solicitar_autorizacion_sri(clave_nc, ambiente)
                if est_aut == 'AUTORIZADO':
                    cur.execute("""
                        UPDATE anulaciones_factura 
                        SET estado_anulacion = 'PROCESADO', nc_numero_autorizacion = %s, 
                            nc_xml_autorizado = %s, mensaje_sri = 'NOTA DE CRÉDITO AUTORIZADA'
                        WHERE venta_id = %s
                    """, (num_aut, xml_aut, venta_id))
                    cur.execute("UPDATE ventas SET anulada = 1, estado_sri = 'ANULADA' WHERE id = %s", (venta_id,))
                    mysql.connection.commit()
                    return True, "Factura anulada con Nota de Crédito autorizada."
                time.sleep(3)
            return False, "La Nota de Crédito sigue en procesamiento. El estado se ha actualizado en el historial."
        else:
            cur.execute("UPDATE anulaciones_factura SET mensaje_sri = %s WHERE venta_id = %s", (f"RECEPCIÓN: {msj_recepcion}"[:500], venta_id))
            mysql.connection.commit()
            return False, f"Error en recepción del SRI: {msj_recepcion}"

    except Exception as e:
        mysql.connection.rollback()
        return False, str(e)
    finally: cur.close()

def generar_xml_nota_credito_bytes(venta, empresa, detalles, motivo, clave_nc, fecha_nc):
    """
    Genera el XML de una Nota de Crédito (Tipo 04) referenciando a la factura original.
    """
    sub0 = float(venta.get('subtotal_0') or 0); sub15 = float(venta.get('subtotal_15') or 0)
    iva = float(venta.get('iva_valor') or 0); total = float(venta.get('total') or 0)

    root = etree.Element("notaCredito", id="comprobante", version="1.0.0")
    it = etree.SubElement(root, "infoTributaria")
    etree.SubElement(it, "ambiente").text = str(empresa['ambiente'])
    etree.SubElement(it, "tipoEmision").text = "1"
    etree.SubElement(it, "razonSocial").text = limpiar_texto(empresa['razon_social'])
    if empresa.get('nombre_comercial'): etree.SubElement(it, "nombreComercial").text = limpiar_texto(empresa['nombre_comercial'])
    etree.SubElement(it, "ruc").text = str(empresa['ruc'])
    etree.SubElement(it, "claveAcceso").text = str(clave_nc)
    etree.SubElement(it, "codDoc").text = "04"
    etree.SubElement(it, "estab").text = str(venta.get('establecimiento')).zfill(3)
    etree.SubElement(it, "ptoEmi").text = str(venta.get('punto_emision')).zfill(3)
    etree.SubElement(it, "secuencial").text = str(venta.get('secuencial')).zfill(9)
    etree.SubElement(it, "dirMatriz").text = limpiar_texto(empresa['direccion_matriz'])

    inf = etree.SubElement(root, "infoNotaCredito")
    etree.SubElement(inf, "fechaEmision").text = fecha_nc.strftime('%d/%m/%Y')
    etree.SubElement(inf, "dirEstablecimiento").text = limpiar_texto(empresa['direccion_matriz'])
    etree.SubElement(inf, "tipoIdentificacionComprador").text = str(venta['tipo_id_sri']).zfill(2)
    etree.SubElement(inf, "razonSocialComprador").text = limpiar_texto(f"{venta['nombres']} {venta['apellidos']}")
    etree.SubElement(inf, "identificacionComprador").text = str(venta['cedula_ruc'])
    etree.SubElement(inf, "obligadoContabilidad").text = empresa.get('obligado_contabilidad', 'NO')
    
    # Datos del comprobante modificado (Factura original)
    etree.SubElement(inf, "codDocModificado").text = "01"
    etree.SubElement(inf, "numDocModificado").text = f"{venta['establecimiento']}-{venta['punto_emision']}-{venta['secuencial']}"
    etree.SubElement(inf, "fechaEmisionDocSustento").text = venta['fecha'].strftime('%d/%m/%Y')
    etree.SubElement(inf, "totalSinImpuestos").text = f"{sub0 + sub15:.2f}"
    etree.SubElement(inf, "valorModificacion").text = f"{total:.2f}"
    etree.SubElement(inf, "moneda").text = "DOLAR"

    tci = etree.SubElement(inf, "totalConImpuestos")
    if sub15 > 0:
        ti = etree.SubElement(tci, "totalImpuesto")
        etree.SubElement(ti, "codigo").text = "2"; etree.SubElement(ti, "codigoPorcentaje").text = "4"
        etree.SubElement(ti, "baseImponible").text = f"{sub15:.2f}"; etree.SubElement(ti, "valor").text = f"{iva:.2f}"
    if sub0 > 0:
        ti = etree.SubElement(tci, "totalImpuesto")
        etree.SubElement(ti, "codigo").text = "2"; etree.SubElement(ti, "codigoPorcentaje").text = "0"
        etree.SubElement(ti, "baseImponible").text = f"{sub0:.2f}"; etree.SubElement(ti, "valor").text = "0.00"
    
    etree.SubElement(inf, "motivo").text = limpiar_texto(motivo)

    dets = etree.SubElement(root, "detalles")
    for d in detalles:
        det = etree.SubElement(dets, "detalle")
        etree.SubElement(det, "codigoInterno").text = str(d['codigo_principal'] or d['producto_id'])[:25]
        etree.SubElement(det, "descripcion").text = limpiar_texto(d['descripcion'])
        etree.SubElement(det, "cantidad").text = f"{float(d['cantidad']):.6f}"
        etree.SubElement(det, "precioUnitario").text = f"{float(d['precio_unitario']):.6f}"
        etree.SubElement(det, "descuento").text = "0.00"
        s_det = float(d['subtotal']); i_det = float(d['iva_valor'])
        b_det = s_det / 1.15 if i_det > 0 else s_det
        etree.SubElement(det, "precioTotalSinImpuesto").text = f"{b_det:.2f}"
        imps = etree.SubElement(det, "impuestos"); imp = etree.SubElement(imps, "impuesto")
        etree.SubElement(imp, "codigo").text = "2"
        if i_det > 0:
            etree.SubElement(imp, "codigoPorcentaje").text = "4"; etree.SubElement(imp, "tarifa").text = "15.00"
            etree.SubElement(imp, "baseImponible").text = f"{b_det:.2f}"; etree.SubElement(imp, "valor").text = f"{i_det:.2f}"
        else:
            etree.SubElement(imp, "codigoPorcentaje").text = "0"; etree.SubElement(imp, "tarifa").text = "0.00"
            etree.SubElement(imp, "baseImponible").text = f"{b_det:.2f}"; etree.SubElement(imp, "valor").text = "0.00"
    
    return etree.tostring(root, encoding='UTF-8', xml_declaration=False)

def solicitar_autorizacion_sri(clave, ambiente):
    url = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl" if ambiente == 1 else "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"
    soap = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ec="http://ec.gob.sri.ws.autorizacion"><soapenv:Header/><soapenv:Body><ec:autorizacionComprobante><claveAccesoComprobante>{clave}</claveAccesoComprobante></ec:autorizacionComprobante></soapenv:Body></soapenv:Envelope>"""
    try:
        res = requests.post(url, data=soap, headers={'Content-Type': 'text/xml; charset=utf-8'}, timeout=25)
        root = etree.fromstring(res.content)
        autorizaciones = root.xpath("//*[local-name()='autorizacion']")
        for aut in autorizaciones:
            estado = aut.xpath(".//*[local-name()='estado']/text()")
            if estado and estado[0] == 'AUTORIZADO':
                num = aut.xpath(".//*[local-name()='numeroAutorizacion']/text()")
                comprobante = aut.xpath(".//*[local-name()='comprobante']/text()")
                return 'AUTORIZADO', num[0], comprobante[0], 'OK'
        msgs = root.xpath("//*[local-name()='mensaje']/*[local-name()='mensaje']/text()")
        err = " | ".join(msgs) if msgs else "No autorizado"
        return 'RECHAZADO', None, None, err
    except Exception as e: return 'ERROR', None, None, str(e)
