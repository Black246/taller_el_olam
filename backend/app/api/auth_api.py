from flask import request, jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token
)

from app.api import auth_bp

from app.services import AuthService

from app.models.usuario import Usuario

from app.extensions import db


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    resultado = AuthService.login(
        data.get("usuario"),
        data.get("password")
    )

    return jsonify(resultado), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():

    user_id = get_jwt_identity()

    usuario = AuthService.obtener_usuario(
        user_id
    )

    return jsonify(
        usuario.to_dict()
    ), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():

    user_id = get_jwt_identity()

    access_token = create_access_token(
        identity=user_id
    )

    return jsonify({
        "access_token": access_token
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():

    return jsonify({
        "message": "Sesión cerrada exitosamente"
    }), 200