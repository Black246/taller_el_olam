from datetime import datetime

from app.extensions import db

# Verificar si el modelo ya está registrado
if 'Factura' in db.Model.registry._class_registry:
    # Si ya existe, usar la clase existente
    Factura = db.Model.registry._class_registry['Factura']
else:
    # Si no existe, definir la clase

    class Factura(db.Model):
        __tablename__ = "facturas"
        __table_args__ = {'extend_existing': True}

        id = db.Column(
            db.Integer,
            primary_key=True
        )

        folio = db.Column(
            db.String(50),
            unique=True,
            nullable=False
        )

        cliente_nombre = db.Column(
            db.String(100),
            nullable=False
        )

        cliente_documento = db.Column(
            db.String(30)
        )

        subtotal = db.Column(
            db.Float,
            default=0
        )

        iva = db.Column(
            db.Float,
            default=0
        )

        total = db.Column(
            db.Float,
            default=0
        )

        usuario_id = db.Column(
            db.Integer,
            db.ForeignKey("usuarios.id")
        )

        metodo_pago = db.Column(
            db.String(30),
            default="EFECTIVO"
        )

        estado = db.Column(
            db.String(20),
            default="PAGADA"
        )

        fecha = db.Column(
            db.DateTime,
            default=datetime.utcnow
        )

        updated_at = db.Column(
            db.DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow
        )

        detalles = db.relationship(
        "DetalleFactura",
        back_populates="factura",
        cascade="all, delete-orphan"
        )

        def to_dict(self):
            return {
                "id": self.id,
                "folio": self.folio,
                "cliente_nombre": self.cliente_nombre,
                "cliente_documento": self.cliente_documento,
                "subtotal": self.subtotal,
                "iva": self.iva,
                "total": self.total,
                "estado": self.estado,
                "metodo_pago": self.metodo_pago,
                "fecha": self.fecha.isoformat() if self.fecha else None
            }