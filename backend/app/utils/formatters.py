from datetime import datetime


def format_currency(value):
    """
    Formato COP
    """

    if value is None:
        return "$0"

    return (
        f"${value:,.0f}"
        .replace(",", ".")
    )


def format_date(
    date_obj,
    fmt="%d/%m/%Y %H:%M"
):
    """
    Formatea fechas
    """

    if date_obj is None:
        return ""

    if isinstance(
        date_obj,
        str
    ):
        try:
            date_obj = datetime.fromisoformat(
                date_obj
            )
        except ValueError:
            return date_obj

    return date_obj.strftime(fmt)


def format_number(
    value,
    decimals=0
):
    """
    Formato numérico latinoamericano
    """

    if value is None:
        return "0"

    return (
        f"{value:,.{decimals}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def format_percentage(
    value,
    decimals=1
):
    """
    Formato porcentaje
    """

    if value is None:
        return "0%"

    return f"{value:.{decimals}f}%"


def truncate_text(
    text,
    max_length=50
):
    """
    Acorta textos largos
    """

    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return (
        text[:max_length]
        + "..."
    )


def format_product_code(code):
    """
    Formato código producto
    """

    if not code:
        return ""

    return code.strip().upper()