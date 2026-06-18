# backend/app/api/escaner_api.py
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.models.producto import Producto
from app.api import escaner_bp

@escaner_bp.route('/buscar', methods=['GET'])
@jwt_required()
def buscar_por_codigo():
    """Buscar producto por código de barras (para escáner)"""
    try:
        codigo = request.args.get('codigo', '')
        
        if not codigo:
            return jsonify({'error': 'Código requerido'}), 400
        
        producto = Producto.query.filter_by(codigo=codigo, is_active=True).first()
        
        if not producto:
            return jsonify({
                'found': False,
                'message': 'Producto no encontrado',
                'codigo': codigo
            }), 404
        
        return jsonify({
            'found': True,
            'producto': producto.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500