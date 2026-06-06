# backend/app/utils/formatters.py
from datetime import datetime

def format_currency(value):
    """Formatea un número como moneda COP"""
    if value is None:
        return "$0"
    return f"${value:,.0f}"

def format_date(date_obj, fmt="%d/%m/%Y %H:%M"):
    """Formatea una fecha"""
    if date_obj is None:
        return ""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj)
        except:
            return date_obj
    return date_obj.strftime(fmt)

def format_number(value, decimals=0):
    """Formatea un número con separadores de miles"""
    if value is None:
        return "0"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_percentage(value, decimals=1):
    """Formatea un porcentaje"""
    if value is None:
        return "0%"
    return f"{value:.{decimals}f}%"

def truncate_text(text, max_length=50):
    """Abrevia un texto"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def format_product_code(code):
    """Formatea un código de producto"""
    if not code:
        return ""
    return code.strip().upper()