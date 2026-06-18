# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Configuración base de la aplicación
    """

    # ==========================
    # FLASK
    # ==========================

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-secret-key"
    )

    # ==========================
    # DATABASE
    # ==========================

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://taller_user:taller_password@localhost:5432/taller_el_olam"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300
    }

    # ==========================
    # JWT
    # ==========================

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "change-this-jwt-secret"
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    JWT_TOKEN_LOCATION = ["headers"]

    JWT_HEADER_NAME = "Authorization"

    JWT_HEADER_TYPE = "Bearer"

    # ==========================
    # CORS
    # ==========================

    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000"
    ).split(",")

    # ==========================
    # DIAN
    # ==========================

    DIAN_SOFTWARE_ID = os.getenv(
        "DIAN_SOFTWARE_ID",
        "TallerElOlam"
    )

    DIAN_SOFTWARE_PIN = os.getenv(
        "DIAN_SOFTWARE_PIN",
        "123456"
    )

    DIAN_TESTING_MODE = (
        os.getenv(
            "DIAN_TESTING_MODE",
            "true"
        ).lower() == "true"
    )

    DIAN_XML_VERSION = "UBL 2.1"

    # ==========================
    # EMPRESA
    # ==========================

    EMPRESA_NIT = os.getenv(
        "EMPRESA_NIT",
        "1065619550"
    )

    EMPRESA_DV = os.getenv(
        "EMPRESA_DV",
        "5"
    )

    EMPRESA_RAZON_SOCIAL = os.getenv(
        "EMPRESA_RAZON_SOCIAL",
        "MOTOTALLER EL OLAM"
    )

    EMPRESA_NOMBRE_COMERCIAL = os.getenv(
        "EMPRESA_NOMBRE_COMERCIAL",
        "MOTOTALLER EL OLAM"
    )

    EMPRESA_DIRECCION = os.getenv(
        "EMPRESA_DIRECCION",
        "CR 26 13 52 BRR ENEAL"
    )

    EMPRESA_CIUDAD = os.getenv(
        "EMPRESA_CIUDAD",
        "Valledupar"
    )

    EMPRESA_DEPARTAMENTO = os.getenv(
        "EMPRESA_DEPARTAMENTO",
        "Cesar"
    )

    EMPRESA_TELEFONO = os.getenv(
        "EMPRESA_TELEFONO",
        "3154541158"
    )

    EMPRESA_EMAIL = os.getenv(
        "EMPRESA_EMAIL",
        "matecari10@hotmail.com"
    )

    # ==========================
    # IMPUESTOS
    # ==========================

    IVA_PORCENTAJE = float(
        os.getenv(
            "IVA_PORCENTAJE",
            "19"
        )
    )
    
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "tu-email@gmail.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "tu-contraseña")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "tu-email@gmail.com")

    # ==========================
    # ARCHIVOS
    # ==========================

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    UPLOAD_FOLDER = "uploads"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # 🔥 CAMBIO IMPORTANTE: Usar nombres consistentes con _PATH
    PDF_FOLDER_PATH = "facturas_pdf"  # Antes era PDF_FOLDER

    XML_FOLDER_PATH = "facturas_electronicas"  # Antes era XML_FOLDER
    
    LOGO_PATH = os.getenv("LOGO_PATH", "static/img/logo.png")


    # ==========================
    # DIRECTORIOS
    # ==========================

    @classmethod
    def init_directories(cls, app):
        """
        Crear directorios requeridos
        """

        # 🔥 Usar los nuevos nombres
        folders = [
            cls.UPLOAD_FOLDER,
            cls.PDF_FOLDER_PATH,  # Cambiado
            cls.XML_FOLDER_PATH   # Cambiado
        ]

        for folder in folders:

            path = os.path.abspath(
                os.path.join(
                    app.root_path,
                    "..",
                    folder
                )
            )

            os.makedirs(
                path,
                exist_ok=True
            )

            # Guardar en app.config con el nombre correcto
            app.config[
                f"{folder.upper()}_PATH"  # Esto crea PDF_FOLDER_PATH y XML_FOLDER_PATH
            ] = path
            
            print(f"📁 Directorio creado/configurado: {folder} -> {path}")


class DevelopmentConfig(Config):

    DEBUG = True

    TESTING = False


class ProductionConfig(Config):

    DEBUG = False

    TESTING = False

    SESSION_COOKIE_SECURE = True

    REMEMBER_COOKIE_SECURE = True

    PREFERRED_URL_SCHEME = "https"


class TestingConfig(Config):

    TESTING = True

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///taller_el_olam.db"
    )


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}