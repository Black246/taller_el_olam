# app/generators/__init__.py
from app.generators.pdf_generator import generar_pdf_factura, generar_pdf_inventario

__all__ = ['generar_pdf_factura', 'generar_pdf_inventario']