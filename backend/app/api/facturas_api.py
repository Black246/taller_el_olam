import os

from flask import current_app, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.api import facturas_bp
from app.services import FacturacionService


@facturas_bp.route("/", methods=["POST"])
@jwt_required()
def crear_factura():
    """
    Crear una nueva factura
    """
    data = request.get_json()

    usuario_id = get_jwt_identity()

    factura = FacturacionService.crear_factura(
        data,
        usuario_id
    )

    return jsonify({
    "success": True,
    "factura_id": factura.id,
    "folio": factura.folio,
    "total": factura.total,
    "pdf_url": f"/api/facturas/{factura.id}/pdf"
    }), 201


@facturas_bp.route("/", methods=["GET"])
@jwt_required()
def get_facturas():
    """
    Obtener historial de facturas
    """

    facturas = FacturacionService.obtener_facturas()

    return jsonify({
        "items": [
            factura.to_dict()
            for factura in facturas
        ],
        "total": len(facturas)
    }), 200


@facturas_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_factura(id):
    """
    Obtener una factura específica
    """

    factura = FacturacionService.obtener_factura(id)

    return jsonify(
        factura.to_dict()
    ), 200


@facturas_bp.route("/<int:id>/anular", methods=["POST"])
@jwt_required()
def anular_factura(id):
    """
    Anular factura
    """

    factura = FacturacionService.obtener_factura(id)

    FacturacionService.anular_factura(
        factura
    )

    return jsonify({
        "success": True,
        "message": "Factura anulada correctamente"
    }), 200


@facturas_bp.route("/<int:id>/pdf", methods=["GET"])
@jwt_required()
def descargar_pdf(id):
    """
    Descargar PDF de factura
    """
    try:
        factura = FacturacionService.obtener_factura(id)
        pdf_path = FacturacionService.generar_pdf(factura)
        
        # Verificar que el archivo existe
        if not os.path.exists(pdf_path):
            return jsonify({
                "success": False,
                "error": f"El archivo PDF no existe: {pdf_path}"
            }), 404
        
        # Enviar el archivo
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"factura_{factura.folio}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        current_app.logger.error(f"Error descargando PDF: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@facturas_bp.route("/<int:id>/xml", methods=["GET"])
@jwt_required()
def descargar_xml(id):
    """
    Descargar XML de factura electrónica
    """

    factura = FacturacionService.obtener_factura(id)

    xml_path = FacturacionService.generar_xml(
        factura
    )

    return send_file(
        xml_path,
        as_attachment=True,
        download_name=f"fe_{id}.xml"
    )