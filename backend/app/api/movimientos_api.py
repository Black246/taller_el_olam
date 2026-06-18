from flask import request, jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from app.api import movimientos_bp

from app.services import InventarioService

from app.schemas import (
    EntradaInventarioSchema,
    SalidaInventarioSchema
)


@movimientos_bp.route("/entrada", methods=["POST"])
@jwt_required()
def registrar_entrada():

    schema = EntradaInventarioSchema()

    data = schema.load(
        request.get_json()
    )

    producto = InventarioService.obtener_producto(
        data["producto_id"]
    )

    InventarioService.actualizar_stock(
        producto,
        data["cantidad"],
        "entrada"
    )

    movimiento = InventarioService.registrar_movimiento({
        **data,
        "tipo": "entrada",
        "usuario_id": get_jwt_identity()
    })

    return jsonify(
        movimiento.to_dict()
    ), 201


@movimientos_bp.route("/salida", methods=["POST"])
@jwt_required()
def registrar_salida():

    schema = SalidaInventarioSchema()

    data = schema.load(
        request.get_json()
    )

    producto = InventarioService.obtener_producto(
        data["producto_id"]
    )

    InventarioService.actualizar_stock(
        producto,
        data["cantidad"],
        "salida"
    )

    movimiento = InventarioService.registrar_movimiento({
        **data,
        "tipo": "salida",
        "usuario_id": get_jwt_identity()
    })

    return jsonify(
        movimiento.to_dict()
    ), 201
    
@movimientos_bp.route("/", methods=["GET"])
@jwt_required()
def get_movimientos():

    from app.models.movimiento import Movimiento

    movimientos = (
        Movimiento.query
        .order_by(
            Movimiento.fecha.desc()
        )
        .all()
    )

    return jsonify([
        m.to_dict()
        for m in movimientos
    ])