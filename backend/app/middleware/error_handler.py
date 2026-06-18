from flask import jsonify
from werkzeug.exceptions import HTTPException

from app.core.exceptions import (
    ValidationException,
    NotFoundException,
    AuthorizationException,
    BusinessException
)


def register_error_handlers(app):
    """
    Registrar manejadores globales de errores
    """

    @app.errorhandler(ValidationException)
    def handle_validation_error(error):

        return jsonify({
            "success": False,
            "error": "Validación",
            "message": str(error),
            "status_code": 400
        }), 400

    @app.errorhandler(NotFoundException)
    def handle_not_found_error(error):

        return jsonify({
            "success": False,
            "error": "No encontrado",
            "message": str(error),
            "status_code": 404
        }), 404

    @app.errorhandler(AuthorizationException)
    def handle_authorization_error(error):

        return jsonify({
            "success": False,
            "error": "Acceso denegado",
            "message": str(error),
            "status_code": 403
        }), 403

    @app.errorhandler(BusinessException)
    def handle_business_error(error):

        return jsonify({
            "success": False,
            "error": "Error de negocio",
            "message": str(error),
            "status_code": 400
        }), 400

    @app.errorhandler(400)
    def bad_request(error):

        return jsonify({
            "success": False,
            "error": "Solicitud incorrecta",
            "message": getattr(
                error,
                "description",
                "Los datos enviados no son válidos"
            ),
            "status_code": 400
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):

        return jsonify({
            "success": False,
            "error": "No autorizado",
            "message": "Token inválido o expirado",
            "status_code": 401
        }), 401

    @app.errorhandler(403)
    def forbidden(error):

        return jsonify({
            "success": False,
            "error": "Prohibido",
            "message": "No tiene permisos para acceder a este recurso",
            "status_code": 403
        }), 403

    @app.errorhandler(404)
    def not_found(error):

        return jsonify({
            "success": False,
            "error": "No encontrado",
            "message": "El recurso solicitado no existe",
            "status_code": 404
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):

        return jsonify({
            "success": False,
            "error": "Método no permitido",
            "message": "Método HTTP no permitido",
            "status_code": 405
        }), 405

    @app.errorhandler(409)
    def conflict(error):

        return jsonify({
            "success": False,
            "error": "Conflicto",
            "message": getattr(
                error,
                "description",
                "Conflicto de datos"
            ),
            "status_code": 409
        }), 409

    @app.errorhandler(422)
    def unprocessable_entity(error):

        return jsonify({
            "success": False,
            "error": "Entidad no procesable",
            "message": getattr(
                error,
                "description",
                "Datos inválidos"
            ),
            "status_code": 422
        }), 422

    @app.errorhandler(Exception)
    def handle_exception(error):

        app.logger.exception(error)

        if isinstance(error, HTTPException):

            return jsonify({
                "success": False,
                "error": error.name,
                "message": error.description,
                "status_code": error.code
            }), error.code

        return jsonify({
            "success": False,
            "error": "Error interno",
            "message": (
                str(error)
                if app.debug
                else "Ocurrió un error inesperado"
            ),
            "status_code": 500
        }), 500