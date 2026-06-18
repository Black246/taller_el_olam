from functools import wraps

from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity
)

from app.extensions import db
from app.models.usuario import Usuario

from app.core.exceptions import (
    AuthorizationException,
    NotFoundException
)


def role_required(roles):
    """
    Decorador para verificar roles.

    Ejemplo:

    @role_required(["admin"])

    @role_required(["admin", "mecanico"])
    """

    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            verify_jwt_in_request()

            user_id = get_jwt_identity()

            user = db.session.get(
                Usuario,
                user_id
            )

            if not user:
                raise NotFoundException(
                    "Usuario no encontrado"
                )

            if not user.is_active:
                raise AuthorizationException(
                    "Usuario inactivo"
                )

            if user.rol not in roles:
                raise AuthorizationException(
                    f"Se requiere rol: {', '.join(roles)}"
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(fn):
    """
    Requiere rol admin
    """

    return role_required(
        ["admin"]
    )(fn)


def mecanico_required(fn):
    """
    Requiere rol admin o mecanico
    """

    return role_required(
        ["admin", "mecanico"]
    )(fn)