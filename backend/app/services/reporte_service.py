from app.extensions import db

from app.models.producto import Producto
from app.models.movimiento import Movimiento


class ReporteService:

    @staticmethod
    def productos_bajo_stock():

        return Producto.query.filter(
            Producto.stock <= Producto.stock_minimo,
            Producto.activo == True
        ).all()

    @staticmethod
    def valor_inventario():

        return (
            db.session.query(
                db.func.sum(
                    Producto.stock *
                    Producto.precio_compra
                )
            )
            .scalar()
            or 0
        )

    @staticmethod
    def ultimos_movimientos(limit=10):

        return (
            Movimiento.query
            .order_by(
                Movimiento.fecha.desc()
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def total_productos():

        return Producto.query.filter_by(
            activo=True
        ).count()

    @staticmethod
    def total_movimientos():

        return Movimiento.query.count()