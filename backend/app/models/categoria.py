from app.extensions import db

# Verificar si el modelo ya está registrado
if 'Factura' in db.Model.registry._class_registry:
    # Si ya existe, usar la clase existente
    Factura = db.Model.registry._class_registry['Factura']
else:
    # Si no existe, definir la clase

    class Categoria(db.Model):
        __tablename__ = 'categorias'
        __table_args__ = {'extend_existing': True}

        id = db.Column(
            db.Integer,
            primary_key=True
        )

        nombre = db.Column(
            db.String(50),
            unique=True,
            nullable=False
        )

        descripcion = db.Column(
            db.String(200)
        )

        def to_dict(self):

            return {
                "id": self.id,
                "nombre": self.nombre,
                "descripcion": self.descripcion
            }

        def __repr__(self):

            return (
                f"<Categoria {self.nombre}>"
            )