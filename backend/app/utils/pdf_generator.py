# backend/app/utils/pdf_generator.py
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

def generar_pdf_factura(factura, detalles, config=None):
    """Genera PDF profesional de factura"""
    
    if config is None:
        config = {
            'EMPRESA_RAZON_SOCIAL': 'MOTOTALLER EL OLAM',
            'EMPRESA_NIT': '1065619550',
            'EMPRESA_DV': '5',
            'EMPRESA_DIRECCION': 'CR 26 13 52 BRR ENEAL',
            'EMPRESA_TELEFONO': '3154541158',
            'EMPRESA_EMAIL': 'matecari10@hotmail.com',
            'PDF_FOLDER': 'facturas_pdf'
        }
    
    os.makedirs(config['PDF_FOLDER'], exist_ok=True)
    pdf_path = f"{config['PDF_FOLDER']}/factura_{factura.id}.pdf"
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'],
                                    fontSize=24, alignment=1, spaceAfter=20,
                                    textColor=colors.HexColor('#1a3c34'))
    story.append(Paragraph(config['EMPRESA_RAZON_SOCIAL'], title_style))
    story.append(Paragraph("FACTURA ELECTRÓNICA", 
                            ParagraphStyle('InvoiceTitle', parent=styles['Heading2'],
                                        fontSize=14, alignment=1, spaceAfter=30)))
    
    # Información del taller
    taller_info = [
        ["NIT:", f"{config['EMPRESA_NIT']}-{config['EMPRESA_DV']}"],
        ["Dirección:", config['EMPRESA_DIRECCION']],
        ["Teléfono:", config['EMPRESA_TELEFONO']],
        ["Email:", config['EMPRESA_EMAIL']]
    ]
    taller_table = Table(taller_info, colWidths=[40*mm, 100*mm])
    taller_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(taller_table)
    story.append(Spacer(1, 5*mm))
    
    # Datos de la factura
    vendedor_nombre = factura.usuario.nombre if hasattr(factura, 'usuario') and factura.usuario else "Administrador"
    
    datos_factura = [
        ["FOLIO:", factura.folio],
        ["FECHA:", factura.fecha.strftime('%d/%m/%Y %H:%M') if factura.fecha else datetime.now().strftime('%d/%m/%Y %H:%M')],
        ["CLIENTE:", factura.cliente_nombre],
        ["DOCUMENTO:", factura.cliente_documento if factura.cliente_documento != "222222222222" else "Consumidor Final"],
        ["VENDEDOR:", vendedor_nombre]
    ]
    datos_table = Table(datos_factura, colWidths=[40*mm, 100*mm])
    datos_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(datos_table)
    story.append(Spacer(1, 10*mm))
    
    # Tabla de productos
    data_productos = [["CANT.", "DESCRIPCIÓN", "P. UNITARIO", "SUBTOTAL"]]
    for det in detalles:
        nombre_producto = det.producto.nombre if hasattr(det, 'producto') and det.producto else "Producto"
        data_productos.append([
            str(det.cantidad),
            nombre_producto,
            f"${det.precio_unitario:,.0f}",
            f"${det.subtotal:,.0f}"
        ])
    
    productos_table = Table(data_productos, colWidths=[20*mm, 80*mm, 35*mm, 35*mm])
    productos_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (2,1), (3,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    story.append(productos_table)
    story.append(Spacer(1, 10*mm))
    
    # Totales
    totales = [
        ["SUBTOTAL:", f"${factura.subtotal:,.0f}"],
        ["IVA 19%:", f"${factura.iva:,.0f}"],
        ["TOTAL:", f"${factura.total:,.0f}"]
    ]
    totales_table = Table(totales, colWidths=[120*mm, 35*mm])
    totales_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('LINEABOVE', (0,2), (1,2), 1, colors.black),
    ]))
    story.append(totales_table)
    
    # Método de pago
    story.append(Spacer(1, 10*mm))
    pago_info = Paragraph(f"<b>MÉTODO DE PAGO:</b> {factura.metodo_pago}", styles['Normal'])
    story.append(pago_info)
    
    # CUFE (si tiene)
    if hasattr(factura, 'cufe') and factura.cufe:
        story.append(Spacer(1, 5*mm))
        cufe_info = Paragraph(f"<b>CUFE:</b><br/>{factura.cufe[:50]}...", 
                                ParagraphStyle('CufeStyle', parent=styles['Italic'], fontSize=8))
        story.append(cufe_info)
    
    # Pie de página
    story.append(Spacer(1, 15*mm))
    footer = Paragraph("<i>Gracias por su compra - Este documento es válido como factura electrónica</i>", 
                        ParagraphStyle('Footer', parent=styles['Italic'], alignment=1, fontSize=9))
    story.append(footer)
    
    # Construir PDF
    doc.build(story)
    return pdf_path