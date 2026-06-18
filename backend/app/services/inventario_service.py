from app.extensions import db

from app.models.producto import Producto
from app.models.movimiento import Movimiento

from app.core.exceptions import (
    ValidationException,
    NotFoundException
)


class InventarioService:

    @staticmethod
    def obtener_producto(producto_id):

        producto = db.session.get(
            Producto,
            producto_id
        )

        if not producto:
            raise NotFoundException(
                "Producto no encontrado"
            )

        return producto

    @staticmethod
    def buscar_por_codigo(codigo):

        producto = Producto.query.filter_by(
            codigo=codigo,
            activo=True
        ).first()

        if not producto:
            raise NotFoundException(
                "Producto no encontrado"
            )

        return producto

    @staticmethod
    def crear_producto(data):

        if Producto.query.filter_by(
            codigo=data["codigo"]
        ).first():

            raise ValidationException(
                "Ya existe un producto con este código"
            )

        producto = Producto(**data)

        db.session.add(producto)
        db.session.commit()

        return producto

    @staticmethod
    def actualizar_stock(
        producto,
        cantidad,
        tipo="entrada"
    ):

        if tipo == "entrada":

            producto.stock += cantidad

        else:

            if producto.stock < cantidad:

                raise ValidationException(
                    "Stock insuficiente"
                )

            producto.stock -= cantidad

        db.session.commit()

        return producto

    @staticmethod
    def registrar_movimiento(data):

        movimiento = Movimiento(**data)

        db.session.add(movimiento)
        db.session.commit()

        return movimiento

    @staticmethod
    def obtener_todos():

        return (
            Producto.query
            .filter_by(activo=True)
            .order_by(Producto.nombre)
            .all()
        )