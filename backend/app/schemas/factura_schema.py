from marshmallow import Schema, fields, validate


class DetalleFacturaSchema(Schema):

    producto_id = fields.Int(
        required=True
    )

    cantidad = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

    precio = fields.Float(
        required=True
    )


class FacturaCreateSchema(Schema):

    cliente_nombre = fields.Str(
    load_default="CONSUMIDOR FINAL"
    )

    cliente_documento = fields.Str()

    metodo_pago = fields.Str(
        load_default="EFECTIVO"
    )

    items = fields.List(
        fields.Nested(
            DetalleFacturaSchema
        ),
        required=True
    )


class FacturaResponseSchema(Schema):

    id = fields.Int()

    folio = fields.Str()

    cliente_nombre = fields.Str()

    cliente_documento = fields.Str()

    subtotal = fields.Float()

    iva = fields.Float()

    total = fields.Float()

    estado = fields.Str()

    metodo_pago = fields.Str()

    usuario = fields.Str(
        dump_only=True
    )

    fecha = fields.DateTime()