from .auth_middleware import (
    role_required,
    admin_required,
    mecanico_required
)

from .error_handler import (
    register_error_handlers
)

__all__ = [
    "role_required",
    "admin_required",
    "mecanico_required",
    "register_error_handlers"
]