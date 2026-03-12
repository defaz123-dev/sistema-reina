from fpdf import FPDF
import io
import math
import os
import tempfile
import base64

class PDF(FPDF):
    def rounded_rect(self, x, y, w, h, r, style=''):
        k = self.k
        hp = self.h
        if style=='F':
            op='f'
        elif style=='FD' or style=='DF':
            op='B'
        else:
            op='S'
        MyArc = 4/3 * (math.sqrt(2) - 1)
        self._out('%.2f %.2f m' % ((x+r)*k, (hp-y)*k))
        xc = x+w-r
        yc = y+r
        self._out('%.2f %.2f l' % (xc*k, (hp-y)*k))
        self._arc(xc + r*MyArc, yc - r, xc + r, yc - r*MyArc, xc + r, yc)
        xc = x+w-r
        yc = y+h-r
        self._out('%.2f %.2f l' % ((x+w)*k, (hp-yc)*k))
        self._arc(xc + r, yc + r*MyArc, xc + r*MyArc, yc + r, xc, yc + r)
        xc = x+r
        yc = y+h-r
        self._out('%.2f %.2f l' % (xc*k, (hp-(y+h))*k))
        self._arc(xc - r*MyArc, yc + r, xc - r, yc + r*MyArc, xc - r, yc)
        xc = x+r
        yc = y+r
        self._out('%.2f %.2f l' % ((x)*k, (hp-yc)*k))
        self._arc(xc - r, yc - r*MyArc, xc - r*MyArc, yc - r, xc, yc - r)
        self._out(op)

    def _arc(self, x1, y1, x2, y2, x3, y3):
        h = self.h
        self._out('%.2f %.2f %.2f %.2f %.2f %.2f c ' % (x1*self.k, (h-y1)*self.k, x2*self.k, (h-y2)*self.k, x3*self.k, (h-y3)*self.k))

def generar_pdf_fpdf(d, empresa):
    pdf = PDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Colores corporativos (Verde Reina)
    verde_corp = (0, 137, 56)
    
    # --- Bloque Empresa (Izquierda) ---
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(*verde_corp)
    pdf.set_xy(10, 10)
    pdf.cell(90, 10, d['nombre_comercial'].encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'C')
    
    # Dibujar contorno empresa con bordes redondos
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.4)
    pdf.rounded_rect(10, 20, 90, 75, 4)
    
    pdf.set_text_color(0,0,0)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_xy(15, 25)
    pdf.multi_cell(80, 5, d['razon_social'].encode('latin-1', 'replace').decode('latin-1'), 0, 'C')
    
    pdf.set_font('Arial', 'B', 9)
    pdf.set_xy(15, 45)
    pdf.cell(25, 5, "Dir. Matriz:", 0, 0)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(55, 5, d['dir_matriz'].encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.set_font('Arial', 'B', 9)
    pdf.set_x(15)
    pdf.cell(25, 5, "Dir. Sucursal:", 0, 0)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(55, 5, d['dir_matriz'].encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.set_x(15)
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_x(15)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(50, 5, "Obligado a llevar contabilidad:", 0, 0)
    pdf.set_font('Arial', '', 9)
    pdf.cell(30, 5, empresa['obligado_contabilidad'].upper(), 0, 1)

    # --- Bloque SRI (Derecha) ---
    pdf.rounded_rect(105, 10, 95, 85, 4)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_xy(110, 15)
    pdf.cell(85, 6, "R.U.C.: " + d['ruc_emisor'], 0, 1)
    
    pdf.set_font('Arial', 'B', 16)
    pdf.set_x(110)
    pdf.cell(85, 8, "NOTA DE CREDITO" if d.get('es_nota_credito') else "FACTURA", 0, 1)
    
    pdf.set_font('Arial', 'B', 11)
    pdf.set_x(110)
    pdf.cell(85, 6, "No. " + d['clave_acceso'][24:27] + "-" + d['clave_acceso'][27:30] + "-" + d['clave_acceso'][30:39], 0, 1)
    
    pdf.set_font('Arial', 'B', 9)
    pdf.set_x(110)
    pdf.cell(85, 5, "NUMERO DE AUTORIZACION:", 0, 1)
    
    pdf.set_font('Arial', '', 8)
    pdf.set_x(110)
    pdf.cell(85, 5, d['num_autorizacion'], 0, 1)
    
    pdf.set_font('Arial', 'B', 9)
    pdf.set_x(110)
    pdf.cell(85, 5, "FECHA Y HORA AUTORIZACION:", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.set_x(110)
    pdf.cell(85, 5, d['fecha_autorizacion'], 0, 1)
    
    pdf.set_font('Arial', 'B', 9)
    pdf.set_x(110)
    pdf.cell(22, 5, "AMBIENTE:", 0, 0)
    pdf.set_font('Arial', '', 9)
    pdf.cell(63, 5, d['ambiente'], 0, 1)
    
    pdf.set_font('Arial', 'B', 9)
    pdf.set_x(110)
    pdf.cell(22, 5, "EMISION:", 0, 0)
    pdf.set_font('Arial', '', 9)
    pdf.cell(63, 5, "NORMAL", 0, 1)
    
    # Codigo de barras
    try:
        if d.get('barcode_64'):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(base64.b64decode(d['barcode_64']))
                tmp_path = tmp.name
            pdf.image(tmp_path, x=110, y=75, w=85, h=12)
            os.unlink(tmp_path)
    except:
        pass
        
    pdf.set_font('Arial', '', 8)
    pdf.set_xy(110, 88)
    pdf.cell(85, 5, d['clave_acceso'], 0, 1, 'C')
    
    # --- Bloque Cliente ---
    pdf.set_y(100)
    
    # Altura dinámica para el cuadro del cliente
    h_bloque_cliente = 25
    if d.get('es_nota_credito'):
        h_bloque_cliente = 42 # Aumentamos espacio para los datos de la NC
        
    pdf.rounded_rect(10, 100, 190, h_bloque_cliente, 4)
    
    pdf.set_font('Arial', 'B', 9)
    pdf.set_xy(15, 105)
    pdf.cell(65, 5, "RAZON SOCIAL / NOMBRES:", 0, 0)
    pdf.set_font('Arial', '', 9)
    # Limpiar nombres largos para que no rompan la estructura
    nombre_c = d['cliente_nombre'].encode('latin-1', 'replace').decode('latin-1')
    pdf.cell(70, 5, nombre_c[:45], 0, 0)
    
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(30, 5, "IDENTIFICACION:", 0, 0)
    pdf.set_font('Arial', '', 9)
    pdf.cell(20, 5, d['cliente_id'], 0, 1)
    
    pdf.set_font('Arial', 'B', 9)
    pdf.set_x(15)
    pdf.cell(30, 5, "FECHA EMISION:", 0, 0)
    pdf.set_font('Arial', '', 9)
    pdf.cell(105, 5, d['fecha_emision'], 0, 0)
    
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(30, 5, "GUIA REMISION:", 0, 0)
    pdf.set_font('Arial', '', 9)
    pdf.cell(20, 5, "N/A", 0, 1)
    
    if d.get('es_nota_credito'):
        pdf.set_y(pdf.get_y() + 2)
        pdf.set_font('Arial', 'B', 8.5)
        pdf.set_x(15)
        pdf.cell(180, 5, "COMPROBANTE QUE SE MODIFICA: FACTURA " + d.get('doc_modificado', ''), 0, 1)
        pdf.set_x(15)
        pdf.cell(180, 5, "FECHA EMISION (COMPROBANTE A MODIFICAR): " + d.get('fecha_emision', ''), 0, 1)
        pdf.set_x(15)
        pdf.cell(40, 5, "RAZON DE MODIFICACION: ", 0, 0)
        pdf.set_font('Arial', '', 8.5)
        # multi_cell para que el motivo no se salga del cuadro
        motivo = d.get('motivo_anulacion', '').upper().encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(140, 5, motivo, 0, 'L')
    
    # --- Tabla Productos ---
    y_tabla = 130 if not d.get('es_nota_credito') else 145
    pdf.set_y(y_tabla)
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(25, 8, "Cod. Princ.", 1, 0, 'C', 1)
    pdf.cell(15, 8, "Cant.", 1, 0, 'C', 1)
    pdf.cell(90, 8, "Descripcion", 1, 0, 'C', 1)
    pdf.cell(25, 8, "P. Unitario", 1, 0, 'C', 1)
    pdf.cell(15, 8, "Dscto.", 1, 0, 'C', 1)
    pdf.cell(20, 8, "P. Total", 1, 1, 'C', 1)
    
    pdf.set_font('Arial', '', 9)
    for det in d['detalles']:
        pdf.cell(25, 6, str(det['codigo']), 1, 0, 'C')
        pdf.cell(15, 6, "%.2f" % det['cantidad'], 1, 0, 'C')
        desc = str(det['descripcion']).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(90, 6, desc[:55], 1, 0, 'L')
        pdf.cell(25, 6, "%.2f" % det['precio_unitario'], 1, 0, 'R')
        pdf.cell(15, 6, "0.00", 1, 0, 'R')
        pdf.cell(20, 6, "%.2f" % det['total'], 1, 1, 'R')
        
    # --- Pie de Factura ---
    y_pie = pdf.get_y() + 10
    if y_pie > 220:
        pdf.add_page()
        y_pie = 20
        
    # Info Adicional
    pdf.set_xy(10, y_pie)
    pdf.rounded_rect(10, y_pie, 110, 40, 4)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_xy(15, y_pie + 5)
    pdf.cell(100, 5, "INFORMACION ADICIONAL", 'B', 1)
    
    pdf.set_font('Arial', 'B', 9)
    pdf.set_x(15)
    pdf.cell(25, 5, "Email:", 0, 0)
    pdf.set_font('Arial', '', 9)
    pdf.cell(75, 5, str(d.get('email', 'N/A'))[:40], 0, 1)
    
    pdf.set_font('Arial', 'B', 9)
    pdf.set_x(15)
    pdf.cell(25, 5, "Vendedor:", 0, 0)
    pdf.set_font('Arial', '', 9)
    pdf.cell(75, 5, "SISTEMA REINA", 0, 1)
    
    # Forma de Pago
    pdf.set_xy(10, y_pie + 45)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(80, 6, "FORMA DE PAGO", 1, 0, 'C', 1)
    pdf.cell(30, 6, "VALOR", 1, 1, 'C', 1)
    pdf.set_font('Arial', '', 8)
    pdf.set_x(10)
    
    # Lógica mejorada de Forma de Pago según estándar SRI y detalle interno
    fp_raw = d.get('forma_pago', 'EFECTIVO')
    fp_text = "OTROS CON UTILIZACION DEL SISTEMA FINANCIERO"
    
    if fp_raw == 'EFECTIVO':
        fp_text = "SIN UTILIZACION DEL SISTEMA FINANCIERO"
    elif fp_raw == 'TARJETA':
        nombre_tarjeta = d.get('tarjeta_nombre', '')
        fp_text = f"TARJETA DE CREDITO / DEBITO ({nombre_tarjeta})" if nombre_tarjeta else "TARJETA DE CREDITO / DEBITO"
    elif fp_raw == 'TRANSFERENCIA':
        fp_text = "OTROS CON UTILIZACION DEL SISTEMA FINANCIERO (TRANSFERENCIA)"
    elif fp_raw == 'PLATAFORMA':
        nombre_plat = d.get('plataforma_nombre', '')
        fp_text = f"OTROS CON UTILIZACION DEL SISTEMA FINANCIERO ({nombre_plat})" if nombre_plat else "PLATAFORMA DIGITAL"
        
    pdf.cell(80, 6, fp_text[:55], 1, 0, 'L') # Limitamos a 55 caracteres para que no se desborde
    pdf.set_font('Arial', '', 9)
    pdf.cell(30, 6, "$ %.2f" % d['total'], 1, 1, 'R')
    
    # Totales
    pdf.set_xy(125, y_pie)
    def fila_total(etiqueta, valor, bold=False, fill=False):
        if bold: pdf.set_font('Arial', 'B', 10)
        else: pdf.set_font('Arial', '', 9)
        if fill: pdf.set_fill_color(240, 240, 240)
        pdf.cell(50, 6, etiqueta, 1, 0, 'L', fill)
        pdf.cell(25, 6, valor, 1, 1, 'R', fill)
        
    pdf.set_x(125)
    fila_total("SUBTOTAL 15%", "%.2f" % d['subtotal_15'])
    pdf.set_x(125)
    fila_total("SUBTOTAL 0%", "%.2f" % d['subtotal_0'])
    pdf.set_x(125)
    fila_total("SUBTOTAL SIN IMPUESTOS", "%.2f" % (d['subtotal_0'] + d['subtotal_15']))
    pdf.set_x(125)
    fila_total("TOTAL DESCUENTO", "0.00")
    pdf.set_x(125)
    fila_total("IVA 15%", "%.2f" % d['iva_valor'])
    pdf.set_x(125)
    fila_total("VALOR TOTAL", "$ %.2f" % d['total'], bold=True, fill=True)
    
    # Retornar PDF como bytes
    return bytes(pdf.output(dest='S').encode('latin1'))
