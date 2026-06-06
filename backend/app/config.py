# backend/app/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base de la aplicación"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///taller_el_olam.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
    
    # DIAN Configuration
    DIAN_SOFTWARE_ID = os.getenv('DIAN_SOFTWARE_ID', 'TallerElOlam')
    DIAN_SOFTWARE_PIN = os.getenv('DIAN_SOFTWARE_PIN', '123456')
    DIAN_TESTING_MODE = os.getenv('DIAN_TESTING_MODE', 'true').lower() == 'true'
    
    # Empresa
    EMPRESA_NIT = os.getenv('EMPRESA_NIT', '1065619550')
    EMPRESA_DV = os.getenv('EMPRESA_DV', '5')
    EMPRESA_RAZON_SOCIAL = os.getenv('EMPRESA_RAZON_SOCIAL', 'MOTOTALLER EL OLAM')
    EMPRESA_NOMBRE_COMERCIAL = os.getenv('EMPRESA_NOMBRE_COMERCIAL', 'MOTOTALLER EL OLAM')
    EMPRESA_DIRECCION = os.getenv('EMPRESA_DIRECCION', 'CR 26 13 52 BRR ENEAL')
    EMPRESA_CIUDAD = os.getenv('EMPRESA_CIUDAD', 'Valledupar')
    EMPRESA_DEPARTAMENTO = os.getenv('EMPRESA_DEPARTAMENTO', 'Cesar')
    EMPRESA_TELEFONO = os.getenv('EMPRESA_TELEFONO', '3154541158')
    EMPRESA_EMAIL = os.getenv('EMPRESA_EMAIL', 'matecari10@hotmail.com')
    
    # IVA (según RUT: No responsable de IVA)
    IVA_PORCENTAJE = float(os.getenv('IVA_PORCENTAJE', '0'))
    
    # Directorios
    UPLOAD_FOLDER = 'uploads'
    PDF_FOLDER = 'facturas_pdf'
    XML_FOLDER = 'facturas_electronicas'
    
    @classmethod
    def init_directories(cls, app):
        """Crea los directorios necesarios"""
        for folder in [cls.UPLOAD_FOLDER, cls.PDF_FOLDER, cls.XML_FOLDER]:
            path = os.path.join(app.root_path, '..', folder)
            os.makedirs(path, exist_ok=True)
            app.config[folder.upper() + '_PATH'] = path


class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configuración de pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}