import os

from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
    redirect,
    send_file,
    session,
    url_for,
    flash
)
from flask_jwt_extended import jwt_required

from app.models.proveedor import Proveedor
from app.extensions import db
from datetime import datetime, date
from app.models.producto import Producto
from app.models.movimiento import Movimiento
from app.services.auth_service import AuthService
from flask import jsonify, session, redirect, Blueprint, render_template, redirect, url_for
from app.services.facturacion_service import FacturacionService
from app.generators.pdf_generator import generar_pdf_inventario

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
                url_for("web.dashboard")
            )

        except Exception as e:
            flash(str(e))

    return render_template("login.html")


@web_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("web.login"))

@web_bp.route("/dashboard")
def dashboard():

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

    productos = Producto.query.order_by(
        Producto.nombre
    ).all()

    total_valor = sum(
        p.stock * p.precio_compra
        for p in productos
    )

    productos_bajo_stock = [
        p for p in productos
        if p.stock <= p.stock_minimo
    ]

    return render_template(
        "reporte.html",
        now=datetime.now(),
        productos=productos,
        total_valor=total_valor,
        productos_bajo_stock=productos_bajo_stock
    )
    
@web_bp.route("/exportar_pdf_inventario")
def exportar_pdf_inventario():
    """Exporta el reporte de inventario a PDF"""
    try:
        from app.models.producto import Producto
        
        # Obtener datos
        productos = Producto.query.order_by(Producto.nombre).all()
        total_valor = sum(p.stock * p.precio_compra for p in productos)
        productos_bajo_stock = [p for p in productos if p.stock <= p.stock_minimo]
        
        # Generar PDF
        pdf_path = generar_pdf_inventario(
            productos=productos,
            total_valor=total_valor,
            productos_bajo_stock=productos_bajo_stock
        )
        
        # Enviar el PDF para visualizar en el navegador
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=False  # Abre en el navegador
        )
        
    except Exception as e:
        current_app.logger.error(f"❌ Error al generar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error al generar PDF',
            'message': str(e)
        }), 500
        
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

@web_bp.route('/historial-facturas')
def historial_facturas():
    """Vista del historial de facturas"""
    try:
        facturas = FacturacionService.obtener_facturas()
        print(f"📊 Facturas encontradas: {len(facturas)}")
        return render_template('historial_facturas.html', facturas=facturas)
    except Exception as e:
        print(f"❌ Error en historial: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('historial_facturas.html', facturas=[], error=str(e))

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