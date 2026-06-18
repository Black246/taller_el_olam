from datetime import datetime
import random
import string
import hashlib
import re


def generate_folio(prefix="FE"):
    """
    Genera un folio único para facturas
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    random_suffix = "".join(
        random.choices(
            string.digits,
            k=4
        )
    )

    return (
        f"{prefix}-{timestamp}-{random_suffix}"
    )


def calculate_iva(
    subtotal,
    percentage=19
):
    """
    Calcula IVA
    """

    return subtotal * (
        percentage / 100
    )


def calculate_total(
    subtotal,
    iva=None,
    percentage=19
):
    """
    Calcula total con IVA
    """

    if iva is None:
        iva = calculate_iva(
            subtotal,
            percentage
        )

    return subtotal + iva


def sanitize_string(text):
    """
    Limpia caracteres especiales
    """

    if not text:
        return ""

    return re.sub(
        r"[^\w\sáéíóúñÑ-]",
        "",
        text
    ).strip()


def generar_cufe(xml_content):
    """
    Genera CUFE para DIAN
    """

    return hashlib.sha256(
        xml_content.encode()
    ).hexdigest()


def obtener_fecha_hora_actual():
    """
    Fecha y hora compatible DIAN
    """

    now = datetime.now()

    fecha = now.strftime(
        "%Y-%m-%d"
    )

    hora = now.strftime(
        "%H:%M:%S-05:00"
    )

    return fecha, hora