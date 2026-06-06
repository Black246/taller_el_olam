from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Crear instancias
db = SQLAlchemy()
login_manager = LoginManager()

# Configuración de la base de datos (se usará en app.py)
def init_db_config(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taller_el_olam.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'taller-el-olam-secret-key-2025'
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Por favor inicia sesión para acceder'
    
    return db, login_manager