# wsgi.py (en la raíz)
import sys
import os

# Agregar la carpeta backend al path de Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Ahora importar desde backend
from app import create_app  # Asumiendo que tienes backend/app/__init__.py

app = create_app()

if __name__ == "__main__":
    app.run()