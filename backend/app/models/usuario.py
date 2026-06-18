from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

# Verificar si el modelo ya está registrado
if 'Factura' in db.Model.registry._class_registry:
    # Si ya existe, usar la clase existente
    Factura = db.Model.registry._class_registry['Factura']
else:
    # Si no existe, definir la clase

    class Usuario(UserMixin, db.Model):
        __tablename__ = "usuarios"
        __table_args__ = {'extend_existing': True}

        id = db.Column(db.Integer, primary_key=True)

        nombre = db.Column(db.String(100), nullable=False)

        usuario = db.Column(
            db.String(50),
            unique=True,
            nullable=False,
            index=True
        )

        email = db.Column(
            db.String(120),
            unique=True,
            nullable=True
        )

        password_hash = db.Column(
            db.String(255),
            nullable=False
        )

        rol = db.Column(
            db.String(20),
            default="mecanico"
        )

        activo = db.Column(
            db.Boolean,
            default=True
        )

        fecha_creacion = db.Column(
            db.DateTime,
            default=datetime.utcnow
        )

        updated_at = db.Column(
            db.DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow
        )

        movimientos = db.relationship(
            "Movimiento",
            backref="usuario",
            lazy=True
        )

        facturas = db.relationship(
            "Factura",
            backref="usuario",
            lazy=True
        )

        @property
        def password(self):
            raise AttributeError(
                "Password is write-only"
            )

        @password.setter
        def password(self, password):
            self.password_hash = generate_password_hash(
                password
            )

        def check_password(self, password):
            return check_password_hash(
                self.password_hash,
                password
            )

        def to_dict(self):
            return {
                "id": self.id,
                "nombre": self.nombre,
                "usuario": self.usuario,
                "email": self.email,
                "rol": self.rol,
                "activo": self.activo,
                "fecha_creacion": self.fecha_creacion.isoformat()
                if self.fecha_creacion else None
            }

        def __repr__(self):
            return f"<Usuario {self.usuario}>"