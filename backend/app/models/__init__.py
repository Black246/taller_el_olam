# backend/app/models/__init__.py

from .usuario import Usuario
from .producto import Producto
from .movimiento import Movimiento
from .proveedor import Proveedor
from .categoria import Categoria
from .factura import Factura
from .detalle_factura import DetalleFactura

__all__ = [
    "Usuario",
    "Producto",
    "Movimiento",
    "Proveedor",
    "Categoria",
    "Factura",
    "DetalleFactura"
]