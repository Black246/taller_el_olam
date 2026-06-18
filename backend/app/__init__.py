# backend/app/__init__.py

from app.routes import web_bp
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.config import Config
from app.extensions import db, migrate
from app.middleware.error_handler import register_error_handlers

jwt = JWTManager()


def create_app(config_class=Config):
    """
    Factory Pattern para crear la aplicación Flask
    """

    app = Flask(
    __name__,
    template_folder="../../templates",
    static_folder="../../static"
)

    # ==========================
    # Configuración
    # ==========================

    app.config.from_object(config_class)

    config_class.init_directories(app)

    # ==========================
    # Extensiones
    # ==========================
    print("DATABASE URI:")
    print(app.config["SQLALCHEMY_DATABASE_URI"])
    db.init_app(app)

    migrate.init_app(app, db)

    CORS(
        app,
        origins=app.config["CORS_ORIGINS"]
    )


    jwt.init_app(app)

    # ==========================
    # Middleware
    # ==========================

    register_error_handlers(app)

    # ==========================
    # Blueprints
    # ==========================

    from app.api import (
        auth_bp,
        productos_bp,
        movimientos_bp,
        facturas_bp,
        reportes_bp,
        escaner_bp
    )

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    app.register_blueprint(
        productos_bp,
        url_prefix="/api/productos"
    )

    app.register_blueprint(
        movimientos_bp,
        url_prefix="/api/movimientos"
    )

    app.register_blueprint(
        facturas_bp,
        url_prefix="/api/facturas"
    )

    app.register_blueprint(
        reportes_bp,
        url_prefix="/api/reportes"
    )

    app.register_blueprint(
        escaner_bp,
        url_prefix="/api/escaner"
    )
    
    app.register_blueprint(web_bp)

    # ==========================
    # Health Check
    # ==========================

    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "message": "Taller El Olam API funcionando",
            "version": "1.0.0"
        })

    # ==========================
    # Inicialización BD
    # ==========================

    # ❌ COMENTA o ELIMINA este bloque:
    # with app.app_context():
    #     try:
    #         # Temporal mientras migramos
    #         db.create_all()
    #         crear_datos_iniciales()
    #     except Exception as e:
    #         app.logger.error(f"Error inicializando base de datos: {e}")

    return app


def crear_datos_iniciales():
    """
    Crear usuario administrador
    y productos de ejemplo
    """

    from app.models import Usuario, Producto

    # ==========================
    # Usuario Admin
    # ==========================

    admin = Usuario.query.filter_by(
        usuario="admin"
    ).first()

    if not admin:

        admin = Usuario(
            nombre="Administrador",
            usuario="admin",
            email="admin@tallerelolam.com",
            rol="admin",
            activo =True
        )

        admin.password = "admin123"

        db.session.add(admin)

        db.session.commit()

        print(
            "✅ Usuario admin creado"
        )

    # ==========================
    # Productos de ejemplo
    # ==========================

    if Producto.query.count() == 0:

        productos = [

            Producto(
                codigo="BR-001",
                nombre="Pastilla de freno delantera",
                categoria="Frenos",
                stock=12,
                stock_minimo=5,
                precio_compra=28000,
                precio_venta=45000
            ),

            Producto(
                codigo="AC-001",
                nombre="Aceite 20W50 4L",
                categoria="Lubricantes",
                stock=8,
                stock_minimo=5,
                precio_compra=45000,
                precio_venta=65000
            ),

            Producto(
                codigo="FL-001",
                nombre="Filtro de aceite",
                categoria="Filtros",
                stock=15,
                stock_minimo=10,
                precio_compra=12000,
                precio_venta=22000
            ),

            Producto(
                codigo="BT-001",
                nombre="Batería 12V 60Ah",
                categoria="Electricidad",
                stock=5,
                stock_minimo=2,
                precio_compra=180000,
                precio_venta=250000
            ),

            Producto(
                codigo="HL-001",
                nombre='Llave de impacto 1/2"',
                categoria="Herramientas",
                stock=3,
                stock_minimo=1,
                precio_compra=120000,
                precio_venta=180000
            )
        ]

        db.session.add_all(productos)

        db.session.commit()

        print(
            "✅ Productos de ejemplo creados"
        )