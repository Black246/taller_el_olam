# backend/app/__init__.py
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.config import Config
from app.extensions import db
from app.middleware.error_handler import register_error_handlers

jwt = JWTManager()

def create_app(config_class=Config):
    """Factory pattern para crear la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Configuración
    app.config.from_object(config_class)
    config_class.init_directories(app)
    
    # Inicializar extensiones
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    jwt.init_app(app)
    
    # Middleware de errores
    register_error_handlers(app)
    
    # Registrar blueprints
    from app.api import auth_bp, productos_bp, movimientos_bp, facturas_bp, reportes_bp, escaner_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(productos_bp, url_prefix='/api/productos')
    app.register_blueprint(movimientos_bp, url_prefix='/api/movimientos')
    app.register_blueprint(facturas_bp, url_prefix='/api/facturas')
    app.register_blueprint(reportes_bp, url_prefix='/api/reportes')
    app.register_blueprint(escaner_bp, url_prefix='/api/escaner')
    
    # Ruta de salud
    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'ok',
            'message': 'Taller El Olam API funcionando',
            'version': '1.0.0'
        })
    
    # Crear tablas y datos iniciales
    with app.app_context():
        db.create_all()
        crear_datos_iniciales()
    
    return app

def crear_datos_iniciales():
    """Crea datos iniciales para la base de datos"""
    from app.models.usuario import Usuario
    from app.models.producto import Producto
    
    # Crear usuario admin si no existe
    if not Usuario.query.filter_by(usuario='admin').first():
        admin = Usuario(
            nombre='Administrador',
            usuario='admin',
            email='admin@tallerelolam.com',
            rol='admin',
            is_active=True
        )
        admin.password = 'admin123'
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuario admin creado: admin / admin123")
    
    # Crear productos de ejemplo si no existen
    if Producto.query.count() == 0:
        productos = [
            Producto(codigo='BR-001', nombre='Pastilla de freno delantera', categoria='Frenos', stock=12, stock_minimo=5, precio_compra=28000, precio_venta=45000),
            Producto(codigo='AC-001', nombre='Aceite 20W50 4L', categoria='Lubricantes', stock=8, stock_minimo=5, precio_compra=45000, precio_venta=65000),
            Producto(codigo='FL-001', nombre='Filtro de aceite', categoria='Filtros', stock=15, stock_minimo=10, precio_compra=12000, precio_venta=22000),
            Producto(codigo='BT-001', nombre='Batería 12V 60Ah', categoria='Electricidad', stock=5, stock_minimo=2, precio_compra=180000, precio_venta=250000),
            Producto(codigo='HL-001', nombre='Llave de impacto 1/2"', categoria='Herramientas', stock=3, stock_minimo=1, precio_compra=120000, precio_venta=180000),
        ]
        for p in productos:
            db.session.add(p)
        db.session.commit()
        print("✅ Productos de ejemplo creados")