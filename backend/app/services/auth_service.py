from app.extensions import db
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token
)

from app.models.usuario import Usuario

from app.core.exceptions import (
    ValidationException,
    AuthorizationException
)


class AuthService:

    @staticmethod
    def login(usuario, password):

        user = Usuario.query.filter_by(
            usuario=usuario,
            activo=True
        ).first()

        if not user:
            raise AuthorizationException(
                "Usuario no encontrado"
            )

        if not user.check_password(password):
            raise AuthorizationException(
                "Contraseña incorrecta"
            )

        return {
            "access_token": create_access_token(
                identity=user.id
            ),
            "refresh_token": create_refresh_token(
                identity=user.id
            ),
            "user": user.to_dict()
        }

    @staticmethod
    def obtener_usuario(user_id):

        usuario = db.session.get(
            Usuario,
            user_id
        )

        if not usuario:
            raise ValidationException(
                "Usuario no encontrado"
            )

        return usuario