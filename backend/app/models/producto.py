from datetime import datetime


from app.extensions import db

# Verificar si el modelo ya está registrado
if 'Factura' in db.Model.registry._class_registry:
    # Si ya existe, usar la clase existente
    Factura = db.Model.registry._class_registry['Factura']
else:
    # Si no existe, definir la clase

    class Producto(db.Model):
        __tablename__ = "productos"
        __table_args__ = {'extend_existing': True}

        id = db.Column(
            db.Integer,
            primary_key=True
        )

        codigo = db.Column(
            db.String(20),
            unique=True,
            nullable=False,
            index=True
        )

        nombre = db.Column(
            db.String(100),
            nullable=False
        )

        categoria = db.Column(
            db.String(50)
        )

        descripcion = db.Column(
            db.Text
        )

        stock = db.Column(
            db.Integer,
            default=0
        )

        stock_minimo = db.Column(
            db.Integer,
            default=5
        )

        stock_maximo = db.Column(
            db.Integer,
            default=100
        )

        precio_compra = db.Column(
            db.Float,
            default=0
        )

        precio_venta = db.Column(
            db.Float,
            default=0
        )

        ubicacion = db.Column(
            db.String(50)
        )

        activo = db.Column(
            db.Boolean,
            default=True
        )

        fecha_creacion = db.Column(
            db.DateTime,
            default=datetime.utcnow
        )

        ultima_actualizacion = db.Column(
            db.DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow
        )
        

        movimientos = db.relationship(
            "Movimiento",
            backref="producto",
            lazy=True
        )

        detalles_factura = db.relationship(
        "DetalleFactura",
        back_populates="producto",
        lazy=True
        )

        @property
        def valor_inventario(self):
            return self.stock * self.precio_compra

        @property
        def is_bajo_stock(self):
            return self.stock <= self.stock_minimo

        def to_dict(self):
            return {
                "id": self.id,
                "codigo": self.codigo,
                "nombre": self.nombre,
                "categoria": self.categoria,
                "descripcion": self.descripcion,
                "stock": self.stock,
                "stock_minimo": self.stock_minimo,
                "stock_maximo": self.stock_maximo,
                "precio_compra": self.precio_compra,
                "precio_venta": self.precio_venta,
                "ubicacion": self.ubicacion,
                "activo": self.activo,
                "valor_inventario": self.valor_inventario,
                "is_bajo_stock": self.is_bajo_stock,
                "fecha_creacion": self.fecha_creacion.isoformat()
                if self.fecha_creacion else None
            }

        def __repr__(self):
            return f"<Producto {self.codigo} - {self.nombre}>"