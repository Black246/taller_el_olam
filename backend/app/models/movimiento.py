from datetime import datetime

from app.extensions import db


class Movimiento(db.Model):
    __tablename__ = "movimientos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    producto_id = db.Column(
        db.Integer,
        db.ForeignKey("productos.id"),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    proveedor_id = db.Column(
        db.Integer,
        db.ForeignKey("proveedores.id"),
        nullable=True
    )

    tipo = db.Column(
        db.String(10),
        nullable=False
    )

    cantidad = db.Column(
        db.Integer,
        nullable=False
    )

    motivo = db.Column(
        db.String(200)
    )

    orden_trabajo = db.Column(
        db.String(50)
    )

    costo_unitario = db.Column(
        db.Float,
        default=0
    )

    nota = db.Column(
        db.Text
    )

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "usuario_id": self.usuario_id,
            "proveedor_id": self.proveedor_id,
            "tipo": self.tipo,
            "cantidad": self.cantidad,
            "motivo": self.motivo,
            "orden_trabajo": self.orden_trabajo,
            "costo_unitario": self.costo_unitario,
            "nota": self.nota,
            "fecha": self.fecha.isoformat()
            if self.fecha else None
        }

    def __repr__(self):
        return f"<Movimiento {self.tipo} - {self.cantidad}>"