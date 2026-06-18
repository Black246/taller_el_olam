from marshmallow import Schema, fields, validate


class ProductoSchema(Schema):

    id = fields.Int(
        dump_only=True
    )

    codigo = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=20)
    )

    nombre = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=100)
    )

    categoria = fields.Str()

    descripcion = fields.Str()

    stock = fields.Int()

    stock_minimo = fields.Int()

    stock_maximo = fields.Int()

    precio_compra = fields.Float()

    precio_venta = fields.Float()

    ubicacion = fields.Str()

    activo = fields.Bool(
        dump_only=True
    )

    valor_inventario = fields.Float(
        dump_only=True
    )

    is_bajo_stock = fields.Bool(
        dump_only=True
    )

    fecha_creacion = fields.DateTime(
        dump_only=True
    )

    ultima_actualizacion = fields.DateTime(
        dump_only=True
    )


class ProductoCreateSchema(Schema):

    codigo = fields.Str(
        required=True
    )

    nombre = fields.Str(
        required=True
    )

    categoria = fields.Str()

    descripcion = fields.Str()

    stock = fields.Int(
        load_default=0
    )

    stock_minimo = fields.Int(
        load_default=5
    )

    stock_maximo = fields.Int(
        load_default=100
    )

    precio_compra = fields.Float(
        load_default=0
    )

    precio_venta = fields.Float(
        load_default=0
    )

    ubicacion = fields.Str()


class ProductoUpdateSchema(Schema):

    nombre = fields.Str()

    categoria = fields.Str()

    descripcion = fields.Str()

    stock_minimo = fields.Int()

    stock_maximo = fields.Int()

    precio_compra = fields.Float()

    precio_venta = fields.Float()

    ubicacion = fields.Str()