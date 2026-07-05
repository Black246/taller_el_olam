# app/services/dashboard_service.py
from datetime import datetime, timedelta
from sqlalchemy import distinct, func, extract, and_
from app.extensions import db
from app.models.factura import Factura
from app.models.detalle_factura import DetalleFactura
from app.models.producto import Producto
from app.models.usuario import Usuario

class DashboardService:
    
    @staticmethod
    def get_resumen_general(fecha_inicio=None, fecha_fin=None):
        """Obtiene el resumen general de ventas"""
        query = Factura.query.filter_by(estado='PAGADA')
        
        if fecha_inicio:
            query = query.filter(Factura.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Factura.fecha <= fecha_fin)
        
        facturas = query.all()
        
        total_ventas = sum(f.total for f in facturas)
        total_facturas = len(facturas)
        promedio_venta = total_ventas / total_facturas if total_facturas > 0 else 0
        
        # Productos más vendidos
        top_productos = db.session.query(
            Producto.nombre,
            func.sum(DetalleFactura.cantidad).label('total_vendidos'),
            func.sum(DetalleFactura.subtotal).label('total_ingresos')
        ).join(DetalleFactura.producto)\
        .join(DetalleFactura.factura)\
        .filter(Factura.estado == 'PAGADA')\
        .group_by(Producto.id)\
        .order_by(func.sum(DetalleFactura.cantidad).desc())\
        .limit(10).all()
        
        # Ventas por método de pago
        ventas_metodo = db.session.query(
            Factura.metodo_pago,
            func.count(Factura.id).label('cantidad'),
            func.sum(Factura.total).label('total')
        ).filter(Factura.estado == 'PAGADA')\
        .group_by(Factura.metodo_pago).all()
        
        # Ventas por día de la semana
        ventas_dia_semana = db.session.query(
            extract('dow', Factura.fecha).label('dia_semana'),
            func.count(Factura.id).label('cantidad'),
            func.sum(Factura.total).label('total')
        ).filter(Factura.estado == 'PAGADA')\
        .group_by(extract('dow', Factura.fecha))\
        .order_by(extract('dow', Factura.fecha)).all()
        
        # Total de productos únicos vendidos
        productos_vendidos = db.session.query(
            func.count(distinct(DetalleFactura.producto_id))
        ).join(DetalleFactura.factura)\
        .filter(Factura.estado == 'PAGADA')\
        .scalar() or 0
        
        return {
            'total_ventas': total_ventas,
            'total_facturas': total_facturas,
            'promedio_venta': promedio_venta,
            'top_productos': top_productos,
            'ventas_metodo': ventas_metodo,
            'ventas_dia_semana': ventas_dia_semana,
            'productos_vendidos': productos_vendidos
        }
    
    @staticmethod
    def get_ventas_diarias(dias=30):
        """Obtiene ventas de los últimos N días"""
        fecha_inicio = datetime.now() - timedelta(days=dias)
        
        ventas = db.session.query(
            func.date(Factura.fecha).label('fecha'),
            func.count(Factura.id).label('cantidad'),
            func.sum(Factura.total).label('total')
        ).filter(
            Factura.estado == 'PAGADA',
            Factura.fecha >= fecha_inicio
        ).group_by(func.date(Factura.fecha))\
        .order_by(func.date(Factura.fecha)).all()
        
        return ventas
    
    @staticmethod
    def get_ventas_mensuales(anio=None):
        """Obtiene ventas mensuales del año"""
        if anio is None:
            anio = datetime.now().year
        
        ventas = db.session.query(
            extract('month', Factura.fecha).label('mes'),
            func.count(Factura.id).label('cantidad'),
            func.sum(Factura.total).label('total')
        ).filter(
            Factura.estado == 'PAGADA',
            extract('year', Factura.fecha) == anio
        ).group_by(extract('month', Factura.fecha))\
        .order_by(extract('month', Factura.fecha)).all()
        
        return ventas