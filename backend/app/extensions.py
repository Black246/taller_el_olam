# backend/app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Base de datos
db = SQLAlchemy()

# Migraciones
migrate = Migrate()