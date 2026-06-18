# backend/app/api/__init__.py

from flask import Blueprint

# ==========================
# Blueprints
# ==========================

auth_bp = Blueprint(
    "auth",
    __name__
)

productos_bp = Blueprint(
    "productos",
    __name__
)

movimientos_bp = Blueprint(
    "movimientos",
    __name__
)

facturas_bp = Blueprint(
    "facturas",
    __name__
)

reportes_bp = Blueprint(
    "reportes",
    __name__
)

escaner_bp = Blueprint(
    "escaner",
    __name__
)

# ==========================
# Importar rutas
# ==========================

from . import (
    auth_api,
    productos_api,
    movimientos_api,
    facturas_api,
    reportes_api,
    escaner_api,
)

# ==========================
# Exports
# ==========================

__all__ = [
    "auth_bp",
    "productos_bp",
    "movimientos_bp",
    "facturas_bp",
    "reportes_bp",
    "escaner_bp"
]