from marshmallow import Schema, fields, validate


class ProveedorSchema(Schema):

    id = fields.Int(
        dump_only=True
    )

    nombre = fields.Str(
        required=True,
        validate=validate.Length(
            min=3,
            max=100
        )
    )

    contacto = fields.Str()

    telefono = fields.Str()

    email = fields.Email()

    direccion = fields.Str()

    ruc = fields.Str()

    notas = fields.Str()

    activo = fields.Bool(
        dump_only=True
    )

    fecha_registro = fields.DateTime(
        dump_only=True
    )