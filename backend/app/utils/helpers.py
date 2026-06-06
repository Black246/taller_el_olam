# backend/app/utils/helpers.py
from datetime import datetime
import random
import string

def generate_folio(prefix="FE"):
    """Genera un folio único para facturas"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}-{timestamp}-{random_suffix}"

def calculate_iva(subtotal, percentage=19):
    """Calcula el IVA sobre un subtotal"""
    return subtotal * (percentage / 100)

def calculate_total(subtotal, iva=None, percentage=19):
    """Calcula el total incluyendo IVA"""
    if iva is None:
        iva = calculate_iva(subtotal, percentage)
    return subtotal + iva

def sanitize_string(text):
    """Limpia un string eliminando caracteres especiales"""
    if not text:
        return ""
    # Eliminar caracteres no deseados
    import re
    return re.sub(r'[^\w\sáéíóúñÑ-]', '', text).strip()

def generar_cufe(xml_content):
    """Genera CUFE a partir del contenido XML"""
    import hashlib
    return hashlib.sha256(xml_content.encode()).hexdigest()

def obtener_fecha_hora_actual():
    """Retorna fecha y hora actual formateada para DIAN"""
    now = datetime.now()
    fecha = now.strftime("%Y-%m-%d")
    hora = now.strftime("%H:%M:%S-05:00")
    return fecha, hora