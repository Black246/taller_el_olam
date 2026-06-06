from flask import Flask, render_template, request, redirect, send_file, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database import db, login_manager, init_db_config
from models import DetalleFactura, Factura, Usuario, Producto, Movimiento, Proveedor, Categoria
from reportlab.lib.pagesizes import A4, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import uuid
import os

# Inicializar Flask
app = Flask(__name__)

# Configurar base de datos
init_db_config(app)

# User loader para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))  # ← Usar session.get

# ==================== RUTAS ====================

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        user = Usuario.query.filter_by(usuario=usuario, activo=True).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Estadísticas
    total_productos = Producto.query.filter_by(activo=True).count()
    productos_bajo_stock = Producto.query.filter(
        Producto.stock <= Producto.stock_minimo,
        Producto.activo == True
    ).count()
    
    valor_inventario = db.session.query(db.func.sum(Producto.stock * Producto.precio_compra)).filter(
        Producto.activo == True
    ).scalar() or 0
    
    salidas_hoy = Movimiento.query.filter(
        Movimiento.tipo == 'salida',
        db.func.date(Movimiento.fecha) == datetime.utcnow().date()
    ).count()
    
    # Productos con bajo stock
    bajo_stock = Producto.query.filter(
        Producto.stock <= Producto.stock_minimo,
        Producto.activo == True
    ).limit(10).all()
    
    # Últimos movimientos
    ultimos_movimientos = Movimiento.query.order_by(Movimiento.fecha.desc()).limit(10).all()
    
    return render_template('dashboard.html',
                            total_productos=total_productos,
                            productos_bajo_stock=productos_bajo_stock,
                            valor_inventario=valor_inventario,
                            salidas_hoy=salidas_hoy,
                            bajo_stock=bajo_stock,
                            ultimos_movimientos=ultimos_movimientos)

@app.route('/productos')
@login_required
def productos():
    productos = Producto.query.filter_by(activo=True).all()
    return render_template('productos.html', productos=productos)

@app.route('/producto/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    if request.method == 'POST':
        producto = Producto(
            codigo=request.form['codigo'],
            nombre=request.form['nombre'],
            categoria=request.form.get('categoria'),
            stock=int(request.form.get('stock', 0)),
            stock_minimo=int(request.form.get('stock_minimo', 5)),
            stock_maximo=int(request.form.get('stock_maximo', 100)),
            precio_compra=float(request.form.get('precio_compra', 0)),
            precio_venta=float(request.form.get('precio_venta', 0)),
            ubicacion=request.form.get('ubicacion')
        )
        db.session.add(producto)
        db.session.commit()
        flash('Producto creado exitosamente')
        return redirect(url_for('productos'))
    
    return render_template('nuevo_producto.html')

@app.route('/compra', methods=['GET', 'POST'])
@login_required
def registrar_compra():
    proveedores = Proveedor.query.filter_by(activo=True).all()
    productos = Producto.query.filter_by(activo=True).all()
    
    if request.method == 'POST':
        producto_id = request.form['producto_id']
        cantidad = int(request.form['cantidad'])
        costo_unitario = float(request.form['costo_unitario'])
        proveedor_id = request.form.get('proveedor_id')
        
        producto = Producto.query.get(producto_id)
        if producto:
            producto.stock += cantidad
            producto.precio_compra = costo_unitario
            
            movimiento = Movimiento(
                producto_id=producto_id,
                tipo='entrada',
                cantidad=cantidad,
                usuario_id=current_user.id,
                motivo='Compra a proveedor',
                orden_trabajo=request.form.get('orden_trabajo', ''),
                proveedor_id=proveedor_id if proveedor_id else None,
                costo_unitario=costo_unitario,
                nota=request.form.get('nota', '')
            )
            db.session.add(movimiento)
            db.session.commit()
            flash('Compra registrada exitosamente')
        else:
            flash('Producto no encontrado')
        
        return redirect(url_for('dashboard'))
    
    return render_template('compra.html', proveedores=proveedores, productos=productos)

@app.route('/salida', methods=['GET', 'POST'])
@login_required
def registrar_salida():
    productos = Producto.query.filter_by(activo=True).all()
    
    if request.method == 'POST':
        producto_id = request.form['producto_id']
        cantidad = int(request.form['cantidad'])
        
        producto = Producto.query.get(producto_id)
        if producto and producto.stock >= cantidad:
            producto.stock -= cantidad
            
            movimiento = Movimiento(
                producto_id=producto_id,
                tipo='salida',
                cantidad=cantidad,
                usuario_id=current_user.id,
                motivo=request.form['motivo'],
                orden_trabajo=request.form.get('orden_trabajo', '')
            )
            db.session.add(movimiento)
            db.session.commit()
            flash('Salida registrada exitosamente')
        else:
            flash('Stock insuficiente o producto no encontrado')
        
        return redirect(url_for('dashboard'))
    
    return render_template('salida.html', productos=productos)

@app.route('/reporte')
@login_required
def reporte():
    productos = Producto.query.filter_by(activo=True).all()
    total_valor = sum(p.stock * p.precio_compra for p in productos)
    
    # Calcular productos bajo stock en Python, no en Jinja
    productos_bajo_stock = [p for p in productos if p.stock <= p.stock_minimo]
    
    return render_template('reporte.html', 
                            productos=productos, 
                            total_valor=total_valor,
                            productos_bajo_stock=productos_bajo_stock,
                            now=datetime.now())
    
@app.route('/buscar_por_codigo', methods=['GET'])
@login_required
def buscar_por_codigo():
    """Busca un producto por su código de barra (para escáner)"""
    codigo = request.args.get('codigo', '')
    producto = Producto.query.filter_by(codigo=codigo, activo=True).first()
    
    if producto:
        return {
            'encontrado': True,
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'stock': producto.stock,
            'precio_venta': producto.precio_venta
        }
    else:
        return {'encontrado': False, 'mensaje': 'Producto no encontrado'}
    
@app.route('/escanear')
@login_required
def escanear():
    return render_template('escanear.html')

# ==================== RUTAS DE FACTURACIÓN ====================

@app.route('/facturacion')
@login_required
def facturacion():
    """Pantalla principal de facturación"""
    productos = Producto.query.filter_by(activo=True).all()
    
    # Convertir objetos Producto a diccionarios serializables
    productos_serializables = []
    for p in productos:
        productos_serializables.append({
            'id': p.id,
            'codigo': p.codigo,
            'nombre': p.nombre,
            'categoria': p.categoria,
            'stock': p.stock,
            'precio_venta': p.precio_venta
        })
    
    return render_template('facturacion.html', productos=productos_serializables)

@app.route('/crear_factura', methods=['POST'])
@login_required
def crear_factura():
    """Crea una factura a partir del carrito"""
    data = request.get_json()
    
    # Crear la factura
    cliente_nombre = data.get('cliente_nombre', 'CONSUMIDOR FINAL')
    cliente_documento = data.get('cliente_documento', '')
    metodo_pago = data.get('metodo_pago', 'EFECTIVO')
    items = data.get('items', [])
    
    if not items:
        return {'error': 'No hay productos en la factura'}, 400
    
    subtotal = 0
    detalles = []
    
    # Procesar cada item y actualizar stock
    for item in items:
        producto = db.session.get(Producto, item['producto_id'])  # ← Línea nueva
        if not producto:
            return {'error': f'Producto no encontrado: {item["producto_id"]}'}, 404
        
        if producto.stock < item['cantidad']:
            return {'error': f'Stock insuficiente para {producto.nombre}'}, 400
        
        # Calcular subtotal del item
        item_subtotal = item['cantidad'] * item['precio']
        subtotal += item_subtotal
        
        # Actualizar stock
        producto.stock -= item['cantidad']
        
        # Registrar movimiento
        movimiento = Movimiento(
            producto_id=producto.id,
            tipo='salida',
            cantidad=item['cantidad'],
            usuario_id=current_user.id,
            motivo='Venta - Factura',
            orden_trabajo=f"F-{datetime.now().strftime('%Y%m%d')}"
        )
        db.session.add(movimiento)
        
        detalles.append({
            'producto': producto,
            'cantidad': item['cantidad'],
            'precio_unitario': item['precio'],
            'subtotal': item_subtotal
        })
    
    # Calcular IVA (19% por defecto)
    iva = subtotal * 0.19
    total = subtotal + iva
    
    # Guardar factura
    factura = Factura(
        folio='',  # Se generará después de guardar
        fecha=datetime.now(),
        cliente_nombre=cliente_nombre,
        cliente_documento=cliente_documento,
        subtotal=subtotal,
        iva=iva,
        total=total,
        usuario_id=current_user.id,
        metodo_pago=metodo_pago,
        estado='PAGADA'
    )
    db.session.add(factura)
    db.session.flush()  # Para obtener el ID
    
    # Generar folio
    factura.folio = f"F-{datetime.now().strftime('%Y%m%d')}-{factura.id:04d}"
    
    # Guardar detalles
    for det in detalles:
        detalle = DetalleFactura(
            factura_id=factura.id,
            producto_id=det['producto'].id,
            cantidad=det['cantidad'],
            precio_unitario=det['precio_unitario'],
            subtotal=det['subtotal']
        )
        db.session.add(detalle)
    
    db.session.commit()
    
    # Generar PDF
    pdf_path = generar_pdf_factura(factura.id)
    
    return {
        'success': True,
        'factura_id': factura.id,
        'folio': factura.folio,
        'total': total,
        'pdf_url': f'/descargar_factura/{factura.id}'
    }

def generar_pdf_factura(factura_id):
    """Genera un PDF profesional para la factura usando ReportLab"""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    
    # Usar db.session.get en lugar de Query.get
    factura = db.session.get(Factura, factura_id)
    if not factura:
        return None
    
    detalles = DetalleFactura.query.filter_by(factura_id=factura_id).all()
    
    # Obtener el usuario que creó la factura
    vendedor = db.session.get(Usuario, factura.usuario_id)
    nombre_vendedor = vendedor.nombre if vendedor else "Desconocido"
    
    # Crear directorio si no existe
    os.makedirs('facturas_pdf', exist_ok=True)
    pdf_path = f'facturas_pdf/factura_{factura_id}.pdf'
    
    # Configurar documento
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, 
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], 
                                    fontSize=24, alignment=1, spaceAfter=20)
    story.append(Paragraph("TALLER EL OLAM", title_style))
    story.append(Paragraph("FACTURA", ParagraphStyle('InvoiceTitle', parent=styles['Heading2'], 
                                                        fontSize=16, alignment=1, spaceAfter=30)))
    
    # Información del taller
    taller_info = [
        ["R.U.T.:", "99.999.999-9"],
        ["Dirección:", "Av. Principal #123, Ciudad"],
        ["Teléfono:", "+56 9 1234 5678"],
        ["Email:", "contacto@tallerelolam.cl"]
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
    datos_factura = [
        ["FOLIO:", factura.folio],
        ["FECHA:", factura.fecha.strftime('%d/%m/%Y %H:%M') if factura.fecha else datetime.now().strftime('%d/%m/%Y %H:%M')],
        ["CLIENTE:", factura.cliente_nombre],
        ["R.U.T./DOC.:", factura.cliente_documento if factura.cliente_documento else "--------------"],
        ["VENDEDOR:", nombre_vendedor]
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
        producto = db.session.get(Producto, det.producto_id)
        nombre_producto = producto.nombre if producto else "Producto eliminado"
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
    
    # Pie de página
    story.append(Spacer(1, 15*mm))
    footer = Paragraph("<i>Gracias por su compra - Este documento es válido como factura</i>", 
                        ParagraphStyle('Footer', parent=styles['Italic'], alignment=1, fontSize=9))
    story.append(footer)
    
    # Construir PDF
    doc.build(story)
    return pdf_path

@app.route('/descargar_factura/<int:factura_id>')
@login_required
def descargar_factura(factura_id):
    """Descarga el PDF de una factura"""
    pdf_path = f'facturas_pdf/factura_{factura_id}.pdf'
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, download_name=f'factura_{factura_id}.pdf')
    else:
        # Si no existe, generarlo
        generar_pdf_factura(factura_id)
        return send_file(pdf_path, as_attachment=True, download_name=f'factura_{factura_id}.pdf')

@app.route('/historial_facturas')
@login_required
def historial_facturas():
    """Muestra el historial de facturas"""
    facturas = Factura.query.order_by(Factura.fecha.desc()).all()
    return render_template('historial_facturas.html', facturas=facturas)

@app.route('/anular_factura/<int:factura_id>', methods=['POST'])
@login_required
def anular_factura(factura_id):
    """Anula una factura y restaura el stock"""
    factura = Factura.query.get(factura_id)
    if not factura:
        return {'error': 'Factura no encontrada'}, 404
    
    if factura.estado == 'ANULADA':
        return {'error': 'La factura ya está anulada'}, 400
    
    # Restaurar stock
    detalles = DetalleFactura.query.filter_by(factura_id=factura_id).all()
    for det in detalles:
        producto = Producto.query.get(det.producto_id)
        if producto:
            producto.stock += det.cantidad
    
    factura.estado = 'ANULADA'
    db.session.commit()
    
    return {'success': True}

# ==================== INICIALIZAR BASE DE DATOS Y DATOS POR DEFECTO ====================
def init_database():
    """Crea tablas y datos por defecto si no existen"""
    db.create_all()
    
    # Crear usuario admin por defecto
    if not Usuario.query.filter_by(usuario='admin').first():
        admin = Usuario(
            nombre='Administrador',
            usuario='admin',
            password=generate_password_hash('admin123'),
            rol='admin'
        )
        db.session.add(admin)
    
    # Crear usuario mecánico de prueba
    if not Usuario.query.filter_by(usuario='mecanico1').first():
        mecanico = Usuario(
            nombre='Carlos Méndez',
            usuario='mecanico1',
            password=generate_password_hash('mec123'),
            rol='mecanico'
        )
        db.session.add(mecanico)
    
    # Crear categorías por defecto
    categorias_default = ['Motor', 'Frenos', 'Suspensión', 'Electricidad', 'Lubricantes', 'Filtros', 'Herramientas']
    for cat_nombre in categorias_default:
        if not Categoria.query.filter_by(nombre=cat_nombre).first():
            categoria = Categoria(nombre=cat_nombre)
            db.session.add(categoria)
    
    # Crear proveedor de ejemplo
    if not Proveedor.query.filter_by(nombre='Autopartes López').first():
        proveedor = Proveedor(
            nombre='Autopartes López',
            contacto='Juan López',
            telefono='555-1234',
            email='ventas@autoparteslopez.com',
            direccion='Av. Principal #123'
        )
        db.session.add(proveedor)
    
    # Crear productos de ejemplo
    if Producto.query.count() == 0:
        productos_ejemplo = [
            Producto(codigo='BR-01', nombre='Pastilla de freno delantera', categoria='Frenos', stock=12, stock_minimo=5, precio_compra=280, precio_venta=380, ubicacion='Estante A-1'),
            Producto(codigo='AC-02', nombre='Aceite 20W50', categoria='Lubricantes', stock=2, stock_minimo=5, precio_compra=150, precio_venta=220, ubicacion='Estante B-3'),
            Producto(codigo='FL-03', nombre='Filtro de aceite', categoria='Filtros', stock=1, stock_minimo=3, precio_compra=80, precio_venta=150, ubicacion='Estante C-2'),
            Producto(codigo='BT-04', nombre='Batería 12V', categoria='Electricidad', stock=0, stock_minimo=2, precio_compra=1200, precio_venta=1800, ubicacion='Estante D-1'),
            Producto(codigo='HL-05', nombre='Llave de impacto', categoria='Herramientas', stock=3, stock_minimo=1, precio_compra=1800, precio_venta=2500, ubicacion='Caja de herramientas'),
        ]
        for p in productos_ejemplo:
            db.session.add(p)
    
    db.session.commit()
    print("✅ Base de datos inicializada correctamente")
    print("📌 Usuario admin: admin / admin123")
    print("📌 Usuario mecánico: mecanico1 / mec123")

# Ejecutar inicialización
with app.app_context():
    init_database()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    
from dian_fe import FacturaElectronicaDIAN

@app.route('/crear_factura_dian', methods=['POST'])
@login_required
def crear_factura_dian():
    """Crea una factura electrónica según estándares DIAN"""
    data = request.get_json()
    
    cliente_nombre = data.get('cliente_nombre', 'CONSUMIDOR FINAL')
    cliente_documento = data.get('cliente_documento', '222222222222')
    metodo_pago = data.get('metodo_pago', 'EFECTIVO')
    items = data.get('items', [])
    
    if not items:
        return {'error': 'No hay productos en la factura'}, 400
    
    subtotal = 0
    
    for item in items:
        producto = db.session.get(Producto, item['producto_id'])
        if not producto:
            return {'error': f'Producto no encontrado'}, 404
        
        if producto.stock < item['cantidad']:
            return {'error': f'Stock insuficiente para {producto.nombre}'}, 400
        
        item_subtotal = item['cantidad'] * item['precio']
        subtotal += item_subtotal
        
        producto.stock -= item['cantidad']
        
        movimiento = Movimiento(
            producto_id=producto.id,
            tipo='salida',
            cantidad=item['cantidad'],
            usuario_id=current_user.id,
            motivo='Venta - Factura Electrónica DIAN'
        )
        db.session.add(movimiento)
    
    iva = 0  # Según tu RUT: No responsable de IVA
    total = subtotal + iva
    
    factura = Factura(
        folio='',
        fecha=datetime.now(),
        cliente_nombre=cliente_nombre,
        cliente_documento=cliente_documento,
        subtotal=subtotal,
        iva=iva,
        total=total,
        usuario_id=current_user.id,
        metodo_pago=metodo_pago,
        estado='PAGADA'
    )
    db.session.add(factura)
    db.session.flush()
    
    factura.folio = f"FE-{datetime.now().strftime('%Y%m%d')}-{factura.id:04d}"
    
    # Guardar detalles
    detalles_objs = []
    for item in items:
        producto = db.session.get(Producto, item['producto_id'])
        detalle = DetalleFactura(
            factura_id=factura.id,
            producto_id=item['producto_id'],
            cantidad=item['cantidad'],
            precio_unitario=item['precio'],
            subtotal=item['cantidad'] * item['precio']
        )
        db.session.add(detalle)
        detalles_objs.append(detalle)
    
    db.session.commit()
    
    # Generar XML DIAN
    dian = FacturaElectronicaDIAN()
    xml_content = dian.generar_factura(factura, detalles_objs, items)
    xml_path = dian.guardar_xml(factura.id, xml_content)
    
    # Generar PDF visual (opcional)
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    
    os.makedirs('facturas_pdf', exist_ok=True)
    pdf_path = f'facturas_pdf/factura_{factura.id}.pdf'
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Logo y título
    story.append(Paragraph("MOTOTALLER EL OLAM", styles['Title']))
    story.append(Paragraph(f"FACTURA ELECTRÓNICA {factura.folio}", styles['Heading2']))
    story.append(Spacer(1, 10*mm))
    
    # Datos del taller
    taller_info = [
        ["NIT:", "1065619550-5"],
        ["Dirección:", "CR 26 13 52 BRR ENEAL, Valledupar"],
        ["Teléfono:", "3154541158"],
        ["Email:", "matecari10@hotmail.com"]
    ]
    story.append(Table(taller_info, colWidths=[40*mm, 100*mm]))
    story.append(Spacer(1, 10*mm))
    
    # Datos del cliente
    cliente_info = [
        ["Cliente:", cliente_nombre],
        ["Documento:", cliente_documento if cliente_documento != "222222222222" else "Consumidor Final"],
        ["Fecha:", datetime.now().strftime('%d/%m/%Y %H:%M')]
    ]
    story.append(Table(cliente_info, colWidths=[40*mm, 100*mm]))
    story.append(Spacer(1, 10*mm))
    
    # Tabla de productos
    data = [["Cant", "Producto", "Precio", "Subtotal"]]
    for item in items:
        producto = db.session.get(Producto, item['producto_id'])
        data.append([
            str(item['cantidad']),
            producto.nombre if producto else "N/A",
            f"${item['precio']:,.0f}",
            f"${item['cantidad'] * item['precio']:,.0f}"
        ])
    
    t = Table(data, colWidths=[30*mm, 70*mm, 40*mm, 40*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (2,1), (3,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 10*mm))
    
    # Totales
    story.append(Paragraph(f"<b>Subtotal:</b> ${subtotal:,.0f}", styles['Normal']))
    story.append(Paragraph(f"<b>Total:</b> ${total:,.0f}", styles['Normal']))
    
    doc.build(story)
    
    return {
        'success': True,
        'factura_id': factura.id,
        'folio': factura.folio,
        'total': total,
        'pdf_url': f'/descargar_factura/{factura.id}',
        'xml_url': f'/descargar_xml/{factura.id}'
    }

@app.route('/descargar_xml/<int:factura_id>')
@login_required
def descargar_xml(factura_id):
    """Descarga el XML de factura electrónica DIAN"""
    xml_path = f'facturas_electronicas/fe_{factura_id}.xml'
    if os.path.exists(xml_path):
        return send_file(xml_path, as_attachment=True, download_name=f'factura_{factura_id}.xml')
    return {'error': 'XML no encontrado'}, 404