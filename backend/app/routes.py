import os

from flask import (
    Blueprint,
    current_app,
    json,
    render_template,
    request,
    redirect,
    send_file,
    session,
    url_for,
    flash,
    jsonify,
    
)
from flask_jwt_extended import current_user, jwt_required

from app.models.proveedor import Proveedor
from app.extensions import db
from datetime import datetime, date
from app.models.producto import Producto
from app.models.movimiento import Movimiento
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService
from app.services.facturacion_service import FacturacionService
from app.generators.pdf_generator import generar_pdf_inventario
from app.services.financial_service import FinancialService

web_bp = Blueprint(
    "web",
    __name__,
    template_folder="../../templates"
)

@web_bp.app_context_processor
def inject_user():
    return {
        "current_user": session.get("user"),
        "access_token": session.get("access_token")
    }

@web_bp.route("/")
def index():
    return redirect(url_for("web.login"))

@web_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form.get("usuario")
        password = request.form.get("password")

        try:

            resultado = AuthService.login(
                usuario,
                password
            )

            print("TOKEN GENERADO:")
            print(resultado["access_token"])

            session["access_token"] = resultado["access_token"]
            session["user"] = resultado["user"]

            print("TOKEN EN SESSION:")
            print(session.get("access_token"))

            return redirect(
                url_for("web.home")
            )
        except Exception as e:
            flash(str(e))

    return render_template("login.html")


@web_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("web.login"))

@web_bp.route("/home")
def home():
    """Página principal con resumen de inventario"""
    productos = Producto.query.all()

    total_productos = len(productos)

    productos_bajo_stock = len([
        p for p in productos
        if p.stock <= p.stock_minimo
    ])

    valor_inventario = sum(
        p.stock * p.precio_compra
        for p in productos
    )

    bajo_stock = [
        p for p in productos
        if p.stock <= p.stock_minimo
    ]

    ultimos_movimientos = (
        Movimiento.query
        .order_by(Movimiento.fecha.desc())
        .limit(10)
        .all()
    )

    hoy = date.today()

    salidas_hoy = (
        Movimiento.query
        .filter(
            Movimiento.tipo == "salida"
        )
        .all()
    )

    salidas_hoy = sum(
        mov.cantidad
        for mov in salidas_hoy
        if mov.fecha.date() == hoy
    )

    return render_template(
        "dashboard.html",
        total_productos=total_productos,
        productos_bajo_stock=productos_bajo_stock,
        valor_inventario=valor_inventario,
        salidas_hoy=salidas_hoy,
        bajo_stock=bajo_stock,
        ultimos_movimientos=ultimos_movimientos
    )

@web_bp.route("/productos")
def productos():

    productos = (
        Producto.query
        .order_by(Producto.nombre)
        .all()
    )

    return render_template(
        "productos.html",
        productos=productos
    )

@web_bp.route("/compra")
def compra():

    productos = Producto.query.order_by(
        Producto.nombre
    ).all()

    proveedores = Proveedor.query.filter_by(
        activo=True
    ).all()

    return render_template(
        "compra.html",
        productos=productos,
        proveedores=proveedores
    )
    
@web_bp.route("/salida")
def salida():

    productos = Producto.query.order_by(
        Producto.nombre
    ).all()

    return render_template(
        "salida.html",
        productos=productos
    )

@web_bp.route("/facturacion")
def facturacion():

    productos = Producto.query.filter_by(
        activo=True
    ).all()

    return render_template(
        "facturacion.html",
        productos=[
            p.to_dict()
            for p in productos
        ]
    )

@web_bp.route("/escanear")
def escanear():
    return render_template("escanear.html")

@web_bp.route("/reporte")
def reporte():
    """Reporte de inventario"""
    try:
        productos = Producto.query.order_by(Producto.nombre).all()
        total_valor = sum(p.stock * p.precio_compra for p in productos)
        productos_bajo_stock = [p for p in productos if p.stock <= p.stock_minimo]
        
        return render_template(
            'reporte.html',
            now=datetime.now(),
            productos=productos,
            total_valor=total_valor,
            productos_bajo_stock=productos_bajo_stock
        )
        
    except Exception as e:
        current_app.logger.error(f"❌ Error en reporte: {str(e)}")
        return render_template('error.html', error="Error al cargar el reporte"), 500

# ==========================
# EXPORTAR PDF INVENTARIO
# ==========================

@web_bp.route("/exportar_pdf_inventario")
def exportar_pdf_inventario():
    """Exporta reporte de inventario a PDF"""
    try:
        productos = Producto.query.order_by(Producto.nombre).all()
        total_valor = sum(p.stock * p.precio_compra for p in productos)
        productos_bajo_stock = [p for p in productos if p.stock <= p.stock_minimo]
        
        pdf_path = generar_pdf_inventario(
            productos=productos,
            total_valor=total_valor,
            productos_bajo_stock=productos_bajo_stock
        )
        
        return send_file(
            pdf_path,
            as_attachment=False,  # ✅ Abre en navegador
            download_name=f"reporte_inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        current_app.logger.error(f"❌ Error al exportar PDF inventario: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error al generar PDF'}), 500
        
@web_bp.route("/imprimir_pdf_inventario")
def imprimir_pdf_inventario():
    """Genera y descarga el PDF para imprimir"""
    try:
        from app.models.producto import Producto
        
        productos = Producto.query.order_by(Producto.nombre).all()
        total_valor = sum(p.stock * p.precio_compra for p in productos)
        productos_bajo_stock = [p for p in productos if p.stock <= p.stock_minimo]
        
        pdf_path = generar_pdf_inventario(
            productos=productos,
            total_valor=total_valor,
            productos_bajo_stock=productos_bajo_stock
        )
        
        # Descargar el PDF
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"reporte_inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        current_app.logger.error(f"❌ Error al generar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error al generar PDF',
            'message': str(e)
        }), 500
    

@web_bp.route("/buscar_por_codigo")
def buscar_por_codigo():

    codigo = request.args.get("codigo")

    producto = Producto.query.filter_by(
        codigo=codigo
    ).first()

    if producto:

        return jsonify({
            "encontrado": True,
            "id": producto.id,
            "codigo": producto.codigo,
            "nombre": producto.nombre,
            "stock": producto.stock,
            "precio_venta": producto.precio_venta
        })

    return jsonify({
        "encontrado": False
    })

# ==========================
# HISTORIAL DE FACTURAS
# ==========================

@web_bp.route("/historial")
def historial_facturas():
    """Historial de facturas con filtros avanzados"""
    try:
        # Obtener parámetros de filtro
        filtros = {
            'fecha_inicio': request.args.get('fecha_inicio'),
            'fecha_fin': request.args.get('fecha_fin'),
            'cliente': request.args.get('cliente'),
            'metodo_pago': request.args.get('metodo_pago'),
            'estado': request.args.get('estado')
        }
        
        # Convertir fechas si existen
        if filtros['fecha_inicio']:
            filtros['fecha_inicio'] = datetime.strptime(filtros['fecha_inicio'], '%Y-%m-%d')
        if filtros['fecha_fin']:
            filtros['fecha_fin'] = datetime.strptime(filtros['fecha_fin'] + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        
        # Obtener facturas con filtros
        facturas = FinancialService.get_historial_facturas(filtros)
        
        return render_template(
            'historial_facturas.html',
            facturas=facturas,
            filtros=filtros
        )
        
    except Exception as e:
        current_app.logger.error(f"❌ Error en historial: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('error.html', error="Error al cargar el historial"), 500

@web_bp.route('/factura/<int:id>/pdf')
@jwt_required(optional=True)  # Permitir acceso sin token para vista previa
def ver_factura_pdf(id):
    """Ver PDF de factura en el navegador"""
    try:
        factura = FacturacionService.obtener_factura(id)
        pdf_path = FacturacionService.generar_pdf(factura)
        
        if not os.path.exists(pdf_path):
            flash('El archivo PDF no existe', 'danger')
            return redirect(url_for('web.historial_facturas'))
        
        return send_file(
            pdf_path,
            as_attachment=False,
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'Error al cargar el PDF: {str(e)}', 'danger')
        return redirect(url_for('web.historial_facturas'))

@web_bp.route('/factura/<int:id>/descargar-pdf')
@jwt_required(optional=True)  # Permitir acceso sin token para descarga
def descargar_factura_pdf(id):
    """Descargar PDF de factura"""
    try:
        factura = FacturacionService.obtener_factura(id)
        pdf_path = FacturacionService.generar_pdf(factura)
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"factura_{factura.folio}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'Error al descargar el PDF: {str(e)}', 'danger')
        return redirect(url_for('web.historial_facturas'))

@web_bp.route(
    "/nuevo_producto",
    methods=["GET", "POST"]
)
def nuevo_producto():

    if request.method == "POST":

        try:

            producto = Producto(
                codigo=request.form["codigo"],
                nombre=request.form["nombre"],
                categoria=request.form.get("categoria"),
                ubicacion=request.form.get("ubicacion"),
                stock=int(
                    request.form["stock"]
                ),
                stock_minimo=int(
                    request.form["stock_minimo"]
                ),
                stock_maximo=int(
                    request.form["stock_maximo"]
                ),
                precio_compra=float(
                    request.form["precio_compra"]
                ),
                precio_venta=float(
                    request.form["precio_venta"]
                )
            )

            db.session.add(producto)
            db.session.commit()

            flash(
                "Producto creado correctamente"
            )

            return redirect(
                url_for("web.productos")
            )

        except Exception as e:

            db.session.rollback()

            flash(
                f"Error: {str(e)}"
            )

    codigo = request.args.get(
    "codigo",
    ""
)

    return render_template(
        "nuevo_producto.html",
        codigo=codigo
    )
    
@web_bp.route(
    "/producto/editar/<int:id>",
    methods=["GET", "POST"]
)
def editar_producto(id):

    producto = Producto.query.get_or_404(id)

    if request.method == "POST":

        producto.codigo = request.form["codigo"]
        producto.nombre = request.form["nombre"]
        producto.categoria = request.form.get("categoria")
        producto.ubicacion = request.form.get("ubicacion")

        producto.stock = int(
            request.form["stock"]
        )

        producto.stock_minimo = int(
            request.form["stock_minimo"]
        )

        producto.stock_maximo = int(
            request.form["stock_maximo"]
        )

        producto.precio_compra = float(
            request.form["precio_compra"]
        )

        producto.precio_venta = float(
            request.form["precio_venta"]
        )

        db.session.commit()

        flash(
            "Producto actualizado correctamente"
        )

        return redirect(
            url_for("web.productos")
        )

    return render_template(
        "editar_producto.html",
        producto=producto
    )
    
@web_bp.route(
    "/producto/eliminar/<int:id>",
    methods=["POST"]
)
def eliminar_producto(id):

    producto = Producto.query.get_or_404(id)

    db.session.delete(producto)

    db.session.commit()

    flash(
        "Producto eliminado correctamente"
    )

    return redirect(
        url_for("web.productos")
    )
    
@web_bp.route("/dashboard_financiero")
def dashboard_financiero():
    """Dashboard financiero con gráficos y resúmenes"""
    try:
        # Obtener filtros de fecha
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Convertir fechas si existen
        fecha_inicio_dt = None
        fecha_fin_dt = None
        if fecha_inicio:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        if fecha_fin:
            fecha_fin_dt = datetime.strptime(fecha_fin + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        
        # Obtener datos del dashboard
        resumen = DashboardService.get_resumen_general(fecha_inicio_dt, fecha_fin_dt)
        ventas_diarias = DashboardService.get_ventas_diarias(30)
        ventas_mensuales = DashboardService.get_ventas_mensuales()
        
        # Preparar datos para gráficos
        fechas = [v.fecha.strftime('%d/%m') for v in ventas_diarias if v.fecha]
        totales = [float(v.total) for v in ventas_diarias if v.total]
        
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        ventas_mes = [0] * 12
        for v in ventas_mensuales:
            if v.mes and v.total:
                ventas_mes[int(v.mes) - 1] = float(v.total)
        
        # Datos para gráfico de métodos de pago
        metodos = [{'label': v[0], 'value': float(v[2])} for v in resumen['ventas_metodo'] if v[0]]
        
        # Datos para gráfico de días de la semana
        dias_semana = []
        for v in resumen['ventas_dia_semana']:
            if v.dia_semana is not None:
                dias_semana.append({
                    'dia_semana': int(v.dia_semana),
                    'total': float(v.total) if v.total else 0
                })
        
        return render_template(
            'dashboard_financiero.html',
            now=datetime.now(),
            resumen=resumen,
            fechas=json.dumps(fechas),
            totales=json.dumps(totales),
            meses=json.dumps(meses),
            ventas_mes=json.dumps(ventas_mes),
            metodos=json.dumps(metodos),
            dias_semana=json.dumps(dias_semana)
        )
        
    except Exception as e:
        current_app.logger.error(f"❌ Error en dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('error.html', error="Error al cargar el dashboard"), 500
    
@web_bp.route("/exportar_excel")
def exportar_excel():
    """Exporta facturas a Excel con filtros"""
    try:
        # Obtener parámetros de filtro
        filtros = {
            'fecha_inicio': request.args.get('fecha_inicio'),
            'fecha_fin': request.args.get('fecha_fin'),
            'cliente': request.args.get('cliente'),
            'metodo_pago': request.args.get('metodo_pago'),
            'estado': request.args.get('estado')
        }
        
        # Convertir fechas si existen
        if filtros['fecha_inicio']:
            filtros['fecha_inicio'] = datetime.strptime(filtros['fecha_inicio'], '%Y-%m-%d')
        if filtros['fecha_fin']:
            filtros['fecha_fin'] = datetime.strptime(filtros['fecha_fin'] + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        
        # Obtener facturas con filtros
        facturas = FinancialService.get_historial_facturas(filtros)
        
        # Generar Excel
        excel_file = FinancialService.exportar_excel(facturas)
        
        return send_file(
            excel_file,
            as_attachment=True,
            download_name=f"facturas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        current_app.logger.error(f"❌ Error al exportar Excel: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error al exportar Excel'}), 500
    
# app/routes.py - Agregar ruta de registro
@web_bp.route("/register", methods=["GET", "POST"])
def register():
    """Registro de nuevos usuarios con Neon Auth"""
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validar contraseñas
        if password != confirm_password:
            flash("❌ Las contraseñas no coinciden", "danger")
            return render_template("register.html")
        
        if len(password) < 6:
            flash("❌ La contraseña debe tener al menos 6 caracteres", "danger")
            return render_template("register.html")
        
        # Validar rol (solo admin puede asignar)
        rol = request.form.get("rol", "mecanico")
        if current_user and current_user.rol == 'admin':
            rol = request.form.get("rol", "mecanico")
        else:
            rol = "mecanico"
        
        try:
            resultado = AuthService.register_user(nombre, email, password, rol)
            session["access_token"] = resultado["access_token"]
            session["user"] = resultado["user"]
            flash("✅ Usuario registrado exitosamente", "success")
            return redirect(url_for("web.home"))
        except Exception as e:
            flash(f"❌ Error al registrar: {str(e)}", "danger")
    
    return render_template("register.html")