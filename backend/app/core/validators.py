# backend/app/core/validators.py
import re

def validar_nit(nit):
    """Valida NIT colombiano"""
    if not nit:
        return False
    
    # Eliminar puntos y guiones
    nit = re.sub(r'[.-]', '', nit)
    
    # Verificar que sea numérico
    if not nit.isdigit():
        return False
    
    # Verificar longitud (NIT puede tener hasta 11 dígitos)
    if len(nit) > 11:
        return False
    
    return True

def validar_telefono_colombia(telefono):
    """Valida teléfono colombiano (fijo o móvil)"""
    if not telefono:
        return True
    
    # Eliminar espacios y caracteres especiales
    telefono = re.sub(r'[\s\-\(\)]', '', telefono)
    
    # Teléfono móvil: 10 dígitos, empieza con 3
    if len(telefono) == 10 and telefono.startswith('3'):
        return True
    
    # Teléfono fijo: 7 u 8 dígitos
    if len(telefono) in [7, 8] and telefono.isdigit():
        return True
    
    return False

def validar_email(email):
    """Valida formato de email"""
    if not email:
        return True
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitizar_codigo(codigo):
    """Limpia y normaliza código de producto"""
    if not codigo:
        return None
    
    # Convertir a mayúsculas y eliminar espacios
    codigo = codigo.strip().upper()
    
    # Eliminar caracteres no alfanuméricos (permitir guiones)
    codigo = re.sub(r'[^A-Z0-9-]', '', codigo)
    
    return codigo if codigo else None

def validar_cantidad(cantidad, stock_disponible=None):
    """Valida que la cantidad sea positiva y no exceda el stock"""
    if cantidad is None:
        return False, "Cantidad requerida"
    
    if not isinstance(cantidad, (int, float)):
        return False, "Cantidad debe ser un número"
    
    if cantidad <= 0:
        return False, "Cantidad debe ser mayor a cero"
    
    if stock_disponible is not None and cantidad > stock_disponible:
        return False, f"Stock insuficiente. Disponible: {stock_disponible}"
    
    return True, None

def validar_precio(precio):
    """Valida que el precio sea positivo"""
    if precio is None:
        return False, "Precio requerido"
    
    if not isinstance(precio, (int, float)):
        return False, "Precio debe ser un número"
    
    if precio < 0:
        return False, "Precio no puede ser negativo"
    
    return True, None