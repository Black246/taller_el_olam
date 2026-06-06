# crear_tablas.py
from app import app, db
from models import Factura, DetalleFactura

with app.app_context():
    # Esto crea SOLO las tablas que no existen aún
    db.create_all()
    print("✅ Tablas de facturación creadas exitosamente")
    print("   - facturas")
    print("   - detalles_factura")