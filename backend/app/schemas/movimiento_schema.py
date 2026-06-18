from marshmallow import Schema, fields, validate


class MovimientoSchema(Schema):

    id = fields.Int(
        dump_only=True
    )

    producto_id = fields.Int(
        required=True
    )

    usuario_id = fields.Int(
        dump_only=True
    )

    proveedor_id = fields.Int(
        allow_none=True
    )

    tipo = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["entrada", "salida"]
        )
    )

    cantidad = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

    motivo = fields.Str()

    orden_trabajo = fields.Str()

    costo_unitario = fields.Float()

    nota = fields.Str()

    fecha = fields.DateTime(
        dump_only=True
    )


class EntradaInventarioSchema(Schema):

    producto_id = fields.Int(
        required=True
    )

    cantidad = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

    costo_unitario = fields.Float(
        required=True
    )

    proveedor_id = fields.Int(
        allow_none=True
    )

    nota = fields.Str()


class SalidaInventarioSchema(Schema):

    producto_id = fields.Int(
        required=True
    )

    cantidad = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

    motivo = fields.Str(
        required=True
    )

    orden_trabajo = fields.Str()

    nota = fields.Str()