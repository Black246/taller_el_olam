# app/services/facturacion_service.py
from datetime import datetime
import os
from flask import current_app
from app.extensions import db
from app.models.factura import Factura
from app.models.detalle_factura import DetalleFactura
from app.models.producto import Producto
from app.models.movimiento import Movimiento
from app.generators.pdf_generator import generar_pdf_factura
from app.integrations.dian.dian_fe import FacturaElectronicaDIAN
from app.core.exceptions import ValidationException, NotFoundException

class FacturacionService:

    @staticmethod
    def obtener_factura(factura_id):
        factura = db.session.get(Factura, factura_id)
        if not factura:
            raise NotFoundException("Factura no encontrada")
        return factura

    @staticmethod
    def obtener_facturas():
        """Obtener todas las facturas ordenadas por fecha descendente"""
        try:
            facturas = Factura.query.order_by(Factura.id.desc()).all()
            print(f"📊 DEBUG - Facturas encontradas: {len(facturas)}")
            for f in facturas:
                print(f"  - {f.id}: {f.folio} - {f.cliente_nombre} - ${f.total}")
            return facturas
        except Exception as e:
            print(f"❌ ERROR en obtener_facturas: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    def generar_pdf(factura):
        """Genera el PDF de una factura"""
        try:
            # Asegurar que los detalles estén cargados
            if not hasattr(factura, 'detalles') or not factura.detalles:
                # Cargar los detalles desde la base de datos
                detalles = DetalleFactura.query.filter_by(factura_id=factura.id).all()
            else:
                detalles = factura.detalles
            
            # Generar el PDF
            pdf_path = generar_pdf_factura(factura, detalles)
            
            # Verificar que el archivo existe
            if not os.path.exists(pdf_path):
                raise Exception(f"El PDF no se generó correctamente: {pdf_path}")
            
            return pdf_path
            
        except Exception as e:
            current_app.logger.error(f"Error generando PDF: {str(e)}")
            raise

    @staticmethod
    def generar_xml(factura):
        try:
            dian = FacturaElectronicaDIAN()
            xml_content = dian.generar_factura(factura, factura.detalles, [])
            return dian.guardar_xml(factura.id, xml_content)
        except Exception as e:
            current_app.logger.error(f"Error generando XML: {str(e)}")
            raise


    @staticmethod
    def anular_factura(factura):

        if factura.estado == "ANULADA":

            raise ValidationException(
                "La factura ya está anulada"
            )

        for detalle in factura.detalles:

            producto = db.session.get(
                Producto,
                detalle.producto_id
            )

            if producto:

                producto.stock += detalle.cantidad

        factura.estado = "ANULADA"

        db.session.commit()

        return factura

    @staticmethod
    def crear_factura(
        data,
        usuario_id
    ):

        try:

            items = data.get(
                "items",
                []
            )

            if not items:

                raise ValidationException(
                    "No hay productos en la factura"
                )

            subtotal = 0

            # Validar stock y calcular subtotal
            for item in items:

                producto = db.session.get(
                    Producto,
                    item["producto_id"]
                )

                if not producto:

                    raise NotFoundException(
                        "Producto no encontrado"
                    )

                if producto.stock < item["cantidad"]:

                    raise ValidationException(
                        f"Stock insuficiente para {producto.nombre}"
                    )

                subtotal += (
                    item["cantidad"]
                    * item["precio"]
                )

            iva_porcentaje = current_app.config[
                "IVA_PORCENTAJE"
            ]

            iva = subtotal * (
                iva_porcentaje / 100
            )

            total = subtotal + iva

            factura = Factura(
                folio=f"TEMP-{datetime.now().strftime('%Y%m%d%H%M%S')}",

                cliente_nombre=data.get(
                    "cliente_nombre",
                    "CONSUMIDOR FINAL",
                ),

                cliente_documento=(
                    data.get("cliente_documento")
                    or "222222222222"
                ),

                subtotal=subtotal,
                iva=iva,
                total=total,
                usuario_id=usuario_id,

                metodo_pago=data.get(
                    "metodo_pago",
                    "EFECTIVO"
                )
            )

            db.session.add(
                factura
            )

            db.session.flush()

            # Generar folio usando el ID real
            factura.folio = (
                f"FE-"
                f"{datetime.now().strftime('%Y%m%d')}-"
                f"{factura.id:04d}"
            )

            # Crear detalles y actualizar stock
            for item in items:

                producto = db.session.get(
                    Producto,
                    item["producto_id"]
                )

                detalle = DetalleFactura(
                    factura_id=factura.id,
                    producto_id=item["producto_id"],
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio"],
                    subtotal=(
                        item["cantidad"]
                        * item["precio"]
                    )
                )

                db.session.add(
                    detalle
                )

                producto.stock -= (
                    item["cantidad"]
                )

                movimiento = Movimiento(
                    producto_id=producto.id,
                    usuario_id=usuario_id,
                    tipo="salida",
                    cantidad=item["cantidad"],
                    motivo="Venta - Factura",
                    orden_trabajo=factura.folio
                )

                db.session.add(
                    movimiento
                )

            db.session.commit()

            # Generar documentos
            try:

                FacturacionService.generar_pdf(
                    factura
                )

                FacturacionService.generar_xml(
                    factura
                )

            except Exception as e:

                current_app.logger.error(
                    f"Error generando PDF/XML: {str(e)}"
                )

            return factura

        except Exception:

            db.session.rollback()

            raise