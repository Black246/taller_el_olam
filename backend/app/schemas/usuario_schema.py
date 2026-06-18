from marshmallow import Schema, fields, validate


class UsuarioSchema(Schema):

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

    usuario = fields.Str(
        required=True,
        validate=validate.Length(
            min=3,
            max=50
        )
    )

    rol = fields.Str(
        dump_default="mecanico"
    )

    activo = fields.Bool(
        dump_default=True
    )

    fecha_creacion = fields.DateTime(
        dump_only=True
    )


class LoginSchema(Schema):

    usuario = fields.Str(
        required=True
    )

    password = fields.Str(
        required=True,
        load_only=True
    )