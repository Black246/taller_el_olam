from flask_login import UserMixin
from datetime import datetime
from database import db

# ==================== MODELO USUARIO ====================
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), default='mecanico')  # admin, mecanico
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    movimientos = db.relationship('Movimiento', backref='usuario', lazy=True)
    
    def __repr__(self):
        return f'<Usuario {self.usuario}>'


# ==================== MODELO PRODUCTO ====================
class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))
    stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    stock_maximo = db.Column(db.Integer, default=100)
    precio_compra = db.Column(db.Float, default=0)
    precio_venta = db.Column(db.Float, default=0)
    ubicacion = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    movimientos = db.relationship('Movimiento', backref='producto', lazy=True)
    
    @property
    def valor_inventario(self):
        return self.stock * self.precio_compra
    
    @property
    def is_bajo_stock(self):
        return self.stock <= self.stock_minimo
    
    def __repr__(self):
        return f'<Producto {self.codigo} - {self.nombre}>'


# ==================== MODELO MOVIMIENTO (entradas/salidas) ====================
class Movimiento(db.Model):
    __tablename__ = 'movimientos'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # entrada o salida
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    motivo = db.Column(db.String(200))
    orden_trabajo = db.Column(db.String(50))
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=True)
    costo_unitario = db.Column(db.Float, default=0)
    nota = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Movimiento {self.tipo} - {self.cantidad}>'


# ==================== MODELO PROVEEDOR ====================
class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    ruc = db.Column(db.String(20))
    notas = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    movimientos = db.relationship('Movimiento', backref='proveedor', lazy=True)
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'


# ==================== MODELO CATEGORÍA (opcional) ====================
class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'
    
# ==================== MODELO FACTURA ====================
class Factura(db.Model):
    __tablename__ = 'facturas'
    
    id = db.Column(db.Integer, primary_key=True)
    folio = db.Column(db.String(20), unique=True, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_nombre = db.Column(db.String(100), nullable=False)
    cliente_documento = db.Column(db.String(20))
    subtotal = db.Column(db.Float, default=0)
    iva = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    metodo_pago = db.Column(db.String(30), default='EFECTIVO')
    estado = db.Column(db.String(20), default='PAGADA')
    
    # Relación con Usuario - ¡Esta línea es importante!
    usuario = db.relationship('Usuario', backref='facturas', foreign_keys=[usuario_id])
    
    # Relación con detalles
    detalles = db.relationship('DetalleFactura', backref='factura', lazy=True, cascade='all, delete-orphan')

class DetalleFactura(db.Model):
    __tablename__ = 'detalles_factura'
    
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    
    producto = db.relationship('Producto', backref='detalles_factura')