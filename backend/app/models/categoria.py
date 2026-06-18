from app.extensions import db


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