from flask import jsonify

from flask_jwt_extended import jwt_required

from app.api import reportes_bp

from app.services import ReporteService


@reportes_bp.route("/inventario", methods=["GET"])
@jwt_required()
def reporte_inventario():

    bajo_stock = (
        ReporteService
        .productos_bajo_stock()
    )

    movimientos = (
        ReporteService
        .ultimos_movimientos()
    )

    return jsonify({

        "estadisticas": {

            "total_productos":
                ReporteService.total_productos(),

            "productos_bajo_stock":
                len(bajo_stock),

            "valor_inventario":
                ReporteService.valor_inventario(),

            "total_movimientos":
                ReporteService.total_movimientos()
        },

        "bajo_stock": [
            p.to_dict()
            for p in bajo_stock
        ],

        "ultimos_movimientos": [
            m.to_dict()
            for m in movimientos
        ]
    })