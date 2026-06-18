from datetime import datetime

from app.extensions import db

# Verificar si el modelo ya está registrado
if 'Factura' in db.Model.registry._class_registry:
    # Si ya existe, usar la clase existente
    Factura = db.Model.registry._class_registry['Factura']
else:
    # Si no existe, definir la clase

    class Proveedor(db.Model):
        __tablename__ = 'proveedores'
        __table_args__ = {'extend_existing': True}

        id = db.Column(
            db.Integer,
            primary_key=True
        )

        nombre = db.Column(
            db.String(100),
            nullable=False
        )

        contacto = db.Column(
            db.String(100)
        )

        telefono = db.Column(
            db.String(20)
        )

        email = db.Column(
            db.String(100)
        )

        direccion = db.Column(
            db.String(200)
        )

        ruc = db.Column(
            db.String(20)
        )

        notas = db.Column(
            db.Text
        )

        fecha_registro = db.Column(
            db.DateTime,
            default=datetime.utcnow
        )

        activo = db.Column(
            db.Boolean,
            default=True
        )

        movimientos = db.relationship(
            "Movimiento",
            backref="proveedor",
            lazy=True
        )

        def to_dict(self):

            return {
                "id": self.id,
                "nombre": self.nombre,
                "contacto": self.contacto,
                "telefono": self.telefono,
                "email": self.email,
                "direccion": self.direccion,
                "ruc": self.ruc,
                "notas": self.notas,
                "activo": self.activo,
                "fecha_registro": (
                    self.fecha_registro.isoformat()
                    if self.fecha_registro
                    else None
                )
            }

        def __repr__(self):

            return (
                f"<Proveedor {self.nombre}>"
            )