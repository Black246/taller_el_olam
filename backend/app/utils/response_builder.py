# backend/app/utils/response_builder.py
from flask import jsonify

def build_response(data=None, message="Success", status_code=200):
    """Construye una respuesta JSON exitosa"""
    response = {
        "success": True,
        "message": message,
        "status_code": status_code
    }
    if data is not None:
        response["data"] = data
    
    return jsonify(response), status_code

def build_error_response(error_message, status_code=400, details=None):
    """Construye una respuesta JSON de error"""
    response = {
        "success": False,
        "error": error_message,
        "status_code": status_code
    }
    if details is not None:
        response["details"] = details
    
    return jsonify(response), status_code

def build_paginated_response(items, total, page, per_page):
    """Construye una respuesta paginada"""
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page > 0 else 0
    }

def build_list_response(items, total=None):
    """Construye una respuesta de lista simple"""
    if total is None:
        total = len(items)
    
    return {
        "items": items,
        "total": total,
        "count": len(items)
    }