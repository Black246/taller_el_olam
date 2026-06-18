from marshmallow import Schema, fields, validate


class CategoriaSchema(Schema):

    id = fields.Int(
        dump_only=True
    )

    nombre = fields.Str(
        required=True,
        validate=validate.Length(
            min=2,
            max=50
        )
    )

    descripcion = fields.Str()