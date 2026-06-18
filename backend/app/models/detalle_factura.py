from datetime import datetime
from app.extensions import db

# Verificar si el modelo ya está registrado
if 'Factura' in db.Model.registry._class_registry:
    # Si ya existe, usar la clase existente
    Factura = db.Model.registry._class_registry['Factura']
else:
    # Si no existe, definir la clase

    class DetalleFactura(db.Model):
        __tablename__ = "detalles_factura"
        __table_args__ = {'extend_existing': True}

        id = db.Column(
            db.Integer,
            primary_key=True
        )

        factura_id = db.Column(
            db.Integer,
            db.ForeignKey("facturas.id"),
            nullable=False,
            index=True
        )

        producto_id = db.Column(
            db.Integer,
            db.ForeignKey("productos.id"),
            nullable=False,
            index=True
        )

        cantidad = db.Column(
            db.Integer,
            nullable=False
        )

        precio_unitario = db.Column(
            db.Float,
            nullable=False
        )

        subtotal = db.Column(
            db.Float,
            nullable=False
        )

        fecha = db.Column(
            db.DateTime,
            default=datetime.utcnow
        )

        # RELACIONES
        factura = db.relationship(
            "Factura",
            back_populates="detalles"
        )

        producto = db.relationship(
            "Producto",
            back_populates="detalles_factura"
        )

        def to_dict(self):
            return {
                "id": self.id,
                "factura_id": self.factura_id,
                "producto_id": self.producto_id,
                "cantidad": self.cantidad,
                "precio_unitario": self.precio_unitario,
                "subtotal": self.subtotal,
                "fecha": self.fecha.isoformat()
                if self.fecha else None
            }

        def __repr__(self):
            return (
                f"<DetalleFactura "
                f"Factura:{self.factura_id} "
                f"Producto:{self.producto_id}>"
            )