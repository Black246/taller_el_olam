# app/generators/pdf_generator.py
import os
from datetime import datetime
from flask import current_app
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

def generar_pdf_factura(factura, detalles, config=None):
    """Genera PDF profesional de factura"""
    
    # Obtener la ruta de la carpeta de PDFs
    if config is None:
        # Primero intentar obtener de la configuración de Flask
        pdf_folder_path = current_app.config.get('PDF_FOLDER_PATH')
        
        if not pdf_folder_path:
            # Si no existe, usar una ruta por defecto en el nivel superior
            # current_app.root_path = backend/app/
            # Queremos backend/facturas_pdf/
            base_dir = os.path.dirname(current_app.root_path)  # Sube un nivel a backend/
            pdf_folder_path = os.path.join(base_dir, 'facturas_pdf')
            current_app.logger.info(f"📁 Usando ruta PDF: {pdf_folder_path}")
        
        config = {
            "EMPRESA_RAZON_SOCIAL": current_app.config.get("EMPRESA_RAZON_SOCIAL", "Taller El Olam"),
            "EMPRESA_NIT": current_app.config.get("EMPRESA_NIT", "1065619550"),
            "EMPRESA_DV": current_app.config.get("EMPRESA_DV", "5"),
            "EMPRESA_DIRECCION": current_app.config.get("EMPRESA_DIRECCION", "CR 26 13 52 BRR ENEAL"),
            "EMPRESA_TELEFONO": current_app.config.get("EMPRESA_TELEFONO", "3154541158"),
            "EMPRESA_EMAIL": current_app.config.get("EMPRESA_EMAIL", "matecari10@hotmail.com"),
            "PDF_FOLDER": pdf_folder_path
        }
        
    
    # Crear carpeta si no existe
    os.makedirs(config['PDF_FOLDER'], exist_ok=True)
    
    # Generar nombre de archivo
    pdf_path = os.path.join(config['PDF_FOLDER'], f"factura_{factura.id}.pdf")
    
    # Verificar que la ruta sea absoluta
    pdf_path = os.path.abspath(pdf_path)
    
    current_app.logger.info(f"📄 Generando PDF en: {pdf_path}")
    
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
    
    # Agregar logo
    logo_path = current_app.config.get('LOGO_PATH', 'static/img/logo.png')
    
    try:
        if os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            # Dibujar logo en la parte superior
            from reportlab.platypus import Image
            logo_img = Image(logo_path, width=40*mm, height=20*mm)
            logo_img.hAlign = 'CENTER'
            story.append(logo_img)
            story.append(Spacer(1, 5*mm))
    except Exception as e:
            current_app.logger.warning(f"No se pudo cargar el logo: {e}")
    
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
    
    current_app.logger.info(f"✅ PDF generado exitosamente: {pdf_path}")
    return pdf_path

# app/generators/pdf_generator.py
# ... (código existente de generar_pdf_factura) ...

def generar_pdf_inventario(productos, total_valor, productos_bajo_stock, config=None):
    """
    Genera PDF con el reporte de inventario
    
    Args:
        productos: Lista de objetos Producto
        total_valor: Valor total del inventario
        productos_bajo_stock: Lista de productos con stock bajo
        config: Configuración de la empresa
    
    Returns:
        str: Ruta del archivo PDF generado
    """
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, SimpleDocTemplate
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    import os
    from datetime import datetime
    
    # Configuración
    if config is None:
        # Obtener configuración de Flask
        pdf_folder_path = current_app.config.get('PDF_FOLDER_PATH')
        if not pdf_folder_path:
            base_dir = os.path.dirname(current_app.root_path)
            pdf_folder_path = os.path.join(base_dir, 'reportes_pdf')
            current_app.logger.info(f"📁 Usando ruta PDF: {pdf_folder_path}")
        
        config = {
            "EMPRESA_RAZON_SOCIAL": current_app.config.get("EMPRESA_RAZON_SOCIAL", "Taller El Olam"),
            "EMPRESA_NIT": current_app.config.get("EMPRESA_NIT", "1065619550"),
            "PDF_FOLDER": pdf_folder_path
        }
    
    # Crear carpeta si no existe
    os.makedirs(config['PDF_FOLDER'], exist_ok=True)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_path = os.path.join(config['PDF_FOLDER'], f"reporte_inventario_{timestamp}.pdf")
    pdf_path = os.path.abspath(pdf_path)
    
    current_app.logger.info(f"📄 Generando PDF de inventario en: {pdf_path}")
    
    # Crear documento
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    titulo_style = ParagraphStyle(
        'TituloInventario',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=10,
        textColor=colors.HexColor('#1a3c34')
    )
    
    subtitulo_style = ParagraphStyle(
        'SubtituloInventario',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    # Elementos del PDF
    elementos = []
    
    # Título
    elementos.append(Paragraph(f"📋 REPORTE DE INVENTARIO", titulo_style))
    elementos.append(Paragraph(config['EMPRESA_RAZON_SOCIAL'], subtitulo_style))
    elementos.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitulo_style))
    elementos.append(Spacer(1, 0.2 * inch))
    
    # Resumen - Tarjetas
    resumen_data = [
        ['TOTAL PRODUCTOS', 'VALOR TOTAL INVENTARIO', 'PRODUCTOS BAJO STOCK'],
        [
            str(len(productos)),
            f'${total_valor:,.2f}',
            str(len(productos_bajo_stock))
        ]
    ]
    
    resumen_tabla = Table(resumen_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
    resumen_tabla.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        # Body
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 12),
        # Borde
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ]))
    elementos.append(resumen_tabla)
    elementos.append(Spacer(1, 0.3 * inch))
    
    # Tabla de productos
    headers = ['Código', 'Producto', 'Categoría', 'Stock', 'Mínimo', 'Precio Compra', 'Precio Venta', 'Valor Total']
    
    data = [headers]
    
    # Agregar productos
    for p in productos:
        es_bajo_stock = p.stock <= p.stock_minimo
        data.append([
            p.codigo,
            p.nombre[:30] + '...' if len(p.nombre) > 30 else p.nombre,
            (p.categoria or '-')[:15],
            str(p.stock),
            str(p.stock_minimo),
            f'${p.precio_compra:,.2f}',
            f'${p.precio_venta:,.2f}',
            f'${(p.stock * p.precio_compra):,.2f}'
        ])
    
    # Fila de total
    data.append(['', '', '', '', '', '', 'TOTAL:', f'${total_valor:,.2f}'])
    
    # Anchos de columna
    col_widths = [
        0.9*inch,   # Código
        1.6*inch,   # Producto
        0.9*inch,   # Categoría
        0.6*inch,   # Stock
        0.6*inch,   # Mínimo
        1.0*inch,   # Precio Compra
        1.0*inch,   # Precio Venta
        1.0*inch    # Valor Total
    ]
    
    tabla = Table(data, colWidths=col_widths, repeatRows=1)
    
    # Estilo de la tabla
    table_style = [
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        
        # Alinear columnas numéricas a la derecha
        ('ALIGN', (5, 1), (7, -2), 'RIGHT'),
        ('ALIGN', (3, 1), (4, -2), 'CENTER'),
        
        # Productos bajo stock (fondo rojo claro)
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#fff5f5')),
        
        # Líneas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#2c3e50')),
        
        # Fila de total
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4f8')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('ALIGN', (6, -1), (7, -1), 'RIGHT'),
    ]
    
    # Resaltar filas de productos bajo stock (con borde rojo)
    # Esto se hace iterando sobre las filas (índice 1 hasta -2)
    for i in range(1, len(data) - 1):
        if i <= len(productos):
            producto = productos[i-1]
            if producto.stock <= producto.stock_minimo:
                table_style.append(('BOX', (0, i), (-1, i), 1.5, colors.HexColor('#e74c3c')))
    
    tabla.setStyle(TableStyle(table_style))
    elementos.append(tabla)
    
    # Nota de productos bajo stock
    if productos_bajo_stock:
        elementos.append(Spacer(1, 0.2 * inch))
        nota = Paragraph(
            f"<b>⚠️ Alerta:</b> {len(productos_bajo_stock)} producto(s) con stock mínimo alcanzado.",
            ParagraphStyle('Nota', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#e74c3c'))
        )
        elementos.append(nota)
    
    # Pie de página
    elementos.append(Spacer(1, 0.3 * inch))
    footer_text = f"Reporte generado automáticamente - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    footer = Paragraph(
        footer_text,
        ParagraphStyle('Footer', parent=styles['Italic'], alignment=TA_CENTER, fontSize=8, textColor=colors.grey)
    )
    elementos.append(footer)
    
    # Construir PDF
    doc.build(elementos)
    
    current_app.logger.info(f"✅ PDF de inventario generado: {pdf_path}")
    return pdf_path