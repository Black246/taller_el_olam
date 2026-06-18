from flask import request, jsonify

from flask_jwt_extended import jwt_required

from app.api import productos_bp

from app.services import InventarioService

from app.schemas import (
    ProductoCreateSchema,
    ProductoUpdateSchema
)

from app.extensions import db
from backend.app.models.producto import Producto


@productos_bp.route("/", methods=["GET"])
@jwt_required()
def get_productos():

    productos = InventarioService.obtener_todos()

    return jsonify([
        p.to_dict()
        for p in productos
    ])


@productos_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_producto(id):

    producto = InventarioService.obtener_producto(
        id
    )

    return jsonify(
        producto.to_dict()
    )


@productos_bp.route("/buscar", methods=["GET"])
@jwt_required()
def buscar_por_codigo():

    codigo = request.args.get(
        "codigo"
    )

    producto = InventarioService.buscar_por_codigo(
        codigo
    )

    return jsonify({
        "found": True,
        "producto": producto.to_dict()
    })


@productos_bp.route("/", methods=["POST"])
@jwt_required()
def create_producto():

    schema = ProductoCreateSchema()

    data = schema.load(
        request.get_json()
    )

    producto = InventarioService.crear_producto(
        data
    )

    return jsonify(
        producto.to_dict()
    ), 201


@productos_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_producto(id):

    producto = InventarioService.obtener_producto(
        id
    )

    schema = ProductoUpdateSchema()

    data = schema.load(
        request.get_json()
    )

    for campo, valor in data.items():
        setattr(
            producto,
            campo,
            valor
        )

    db.session.commit()

    return jsonify(
        producto.to_dict()
    )
    
@productos_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_producto(id):

    producto = InventarioService.obtener_producto(
        id
    )

    producto.activo = False

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Producto eliminado correctamente"
    })
    
@productos_bp.route("/categorias", methods=["GET"])
@jwt_required()
def get_categorias():

    categorias = db.session.query(
        Producto.categoria
    ).distinct().all()

    return jsonify([
        c[0]
        for c in categorias
        if c[0]
    ])