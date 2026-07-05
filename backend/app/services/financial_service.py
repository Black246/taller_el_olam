# app/services/financial_service.py
from datetime import datetime, timedelta
from app.extensions import db
from app.models.factura import Factura
from app.models.detalle_factura import DetalleFactura
import pandas as pd
from io import BytesIO

class FinancialService:
    
    @staticmethod
    def get_historial_facturas(filtros=None):
        """Obtiene historial de facturas con filtros"""
        query = Factura.query
        
        if filtros:
            if filtros.get('fecha_inicio'):
                query = query.filter(Factura.fecha >= filtros['fecha_inicio'])
            if filtros.get('fecha_fin'):
                query = query.filter(Factura.fecha <= filtros['fecha_fin'])
            if filtros.get('cliente'):
                query = query.filter(Factura.cliente_nombre.ilike(f'%{filtros["cliente"]}%'))
            if filtros.get('metodo_pago'):
                query = query.filter(Factura.metodo_pago == filtros['metodo_pago'])
            if filtros.get('estado'):
                query = query.filter(Factura.estado == filtros['estado'])
        
        return query.order_by(Factura.fecha.desc()).all()
    
    @staticmethod
    def get_dashboard_data(fecha_inicio=None, fecha_fin=None):
        """Obtiene todos los datos para el dashboard"""
        
        # Base query
        query = Factura.query
        
        # Aplicar filtros de fecha
        if fecha_inicio:
            query = query.filter(Factura.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Factura.fecha <= fecha_fin)
        
        # Obtener todas las facturas del período
        facturas = query.all()
        
        # Calcular totales
        total_ventas = sum(float(f.total) for f in facturas)
        total_facturas = len(facturas)
        promedio_venta = total_ventas / total_facturas if total_facturas > 0 else 0
        
        # Productos vendidos (productos únicos)
        productos_ids = set()
        for f in facturas:
            for detalle in f.detalles:
                productos_ids.add(detalle.producto_id)
        productos_vendidos = len(productos_ids)
        
        # Métodos de pago
        metodos_pago = {}
        for f in facturas:
            metodo = f.metodo_pago or 'No especificado'
            metodos_pago[metodo] = metodos_pago.get(metodo, 0) + 1
        
        ventas_metodo = [{'label': k, 'value': v} for k, v in metodos_pago.items()]
        
        # Top productos
        productos = {}
        for f in facturas:
            for detalle in f.detalles:
                nombre = detalle.producto.nombre if detalle.producto else 'Producto eliminado'
                if nombre not in productos:
                    productos[nombre] = {
                        'nombre': nombre,
                        'total_vendidos': 0,
                        'total_ingresos': 0
                    }
                productos[nombre]['total_vendidos'] += detalle.cantidad
                productos[nombre]['total_ingresos'] += float(detalle.subtotal)
        
        top_productos = sorted(
            productos.values(),
            key=lambda x: x['total_ingresos'],
            reverse=True
        )[:10]
        
        # Datos para gráficos
        # Ventas diarias (últimos 30 días)
        fechas, totales = FinancialService._get_ventas_diarias(fecha_inicio, fecha_fin)
        
        # Ventas mensuales (solo meses con ventas)
        meses, ventas_mes = FinancialService._get_ventas_mensuales(fecha_inicio, fecha_fin)
        
        # Ventas por día de la semana (todos los días con 0)
        dias_semana = FinancialService._get_ventas_dia_semana(fecha_inicio, fecha_fin)
        
        # Datos completos del dashboard
        dashboard_data = {
            'total_ventas': total_ventas,
            'total_facturas': total_facturas,
            'promedio_venta': promedio_venta,
            'productos_vendidos': productos_vendidos,
            'ventas_metodo': ventas_metodo,
            'top_productos': top_productos,
            'fechas': fechas,
            'totales': totales,
            'meses': meses,
            'ventas_mes': ventas_mes,
            'dias_semana': dias_semana,
            'tendencia': FinancialService._calcular_tendencia(fecha_inicio, fecha_fin)
        }
        
        return dashboard_data
    
    @staticmethod
    def _get_ventas_diarias(fecha_inicio=None, fecha_fin=None):
        """Obtiene ventas diarias para los últimos 30 días o período seleccionado"""
        if not fecha_inicio or not fecha_fin:
            fecha_fin = datetime.now()
            fecha_inicio = fecha_fin - timedelta(days=30)
        
        # Obtener todas las facturas del período
        facturas = Factura.query.filter(
            Factura.fecha >= fecha_inicio,
            Factura.fecha <= fecha_fin
        ).all()
        
        # Agrupar por día
        ventas_por_dia = {}
        for f in facturas:
            dia = f.fecha.strftime('%d/%m')
            ventas_por_dia[dia] = ventas_por_dia.get(dia, 0) + float(f.total)
        
        # Crear lista de días completos en el rango
        fechas = []
        totales = []
        current = fecha_inicio
        while current <= fecha_fin:
            dia_str = current.strftime('%d/%m')
            fechas.append(dia_str)
            totales.append(ventas_por_dia.get(dia_str, 0))
            current += timedelta(days=1)
        
        return fechas, totales
    
    @staticmethod
    def _get_ventas_mensuales(fecha_inicio=None, fecha_fin=None):
        """Obtiene ventas mensuales solo para meses con ventas"""
        if not fecha_inicio or not fecha_fin:
            fecha_fin = datetime.now()
            fecha_inicio = fecha_fin - timedelta(days=365)  # Último año
        
        # Obtener todas las facturas del período
        facturas = Factura.query.filter(
            Factura.fecha >= fecha_inicio,
            Factura.fecha <= fecha_fin
        ).all()
        
        # Agrupar por mes
        ventas_por_mes = {}
        for f in facturas:
            mes = f.fecha.strftime('%b')  # Abreviatura del mes (Ene, Feb, etc.)
            ventas_por_mes[mes] = ventas_por_mes.get(mes, 0) + float(f.total)
        
        # Filtrar solo meses con ventas y ordenar cronológicamente
        meses_orden = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        
        meses = []
        ventas_mes = []
        
        for mes in meses_orden:
            if mes in ventas_por_mes and ventas_por_mes[mes] > 0:
                meses.append(mes)
                ventas_mes.append(ventas_por_mes[mes])
        
        return meses, ventas_mes
    
    @staticmethod
    def _get_ventas_dia_semana(fecha_inicio=None, fecha_fin=None):
        """Obtiene ventas por día de la semana (todos los días con 0 si no hay datos)"""
        if not fecha_inicio or not fecha_fin:
            fecha_fin = datetime.now()
            fecha_inicio = fecha_fin - timedelta(days=30)
        
        # Obtener todas las facturas del período
        facturas = Factura.query.filter(
            Factura.fecha >= fecha_inicio,
            Factura.fecha <= fecha_fin
        ).all()
        
        # Agrupar por día de la semana (0=Dom, 1=Lun, ..., 6=Sáb)
        ventas_por_dia = {i: 0 for i in range(7)}  # Inicializar todos los días en 0
        
        for f in facturas:
            dia_semana = f.fecha.weekday()  # 0=Lun, 6=Dom en Python
            # Convertir a nuestro formato (0=Dom, 1=Lun, ..., 6=Sáb)
            dia_semana_convertido = (dia_semana + 1) % 7
            ventas_por_dia[dia_semana_convertido] += float(f.total)
        
        # Convertir a lista de diccionarios para el template
        resultado = []
        for i in range(7):
            resultado.append({
                'dia_semana': i,
                'total': ventas_por_dia[i]
            })
        
        return resultado
    
    @staticmethod
    def _calcular_tendencia(fecha_inicio, fecha_fin):
        """Calcula la tendencia de ventas vs período anterior"""
        if not fecha_inicio or not fecha_fin:
            return 0
        
        # Calcular período anterior
        duracion = fecha_fin - fecha_inicio
        fecha_inicio_anterior = fecha_inicio - duracion
        fecha_fin_anterior = fecha_inicio - timedelta(days=1)
        
        # Obtener ventas del período actual
        ventas_actual = FinancialService._get_ventas_periodo(fecha_inicio, fecha_fin)
        
        # Obtener ventas del período anterior
        ventas_anterior = FinancialService._get_ventas_periodo(fecha_inicio_anterior, fecha_fin_anterior)
        
        if ventas_anterior == 0:
            return 100 if ventas_actual > 0 else 0
        
        return ((ventas_actual - ventas_anterior) / ventas_anterior) * 100
    
    @staticmethod
    def _get_ventas_periodo(fecha_inicio, fecha_fin):
        """Obtiene el total de ventas en un período"""
        query = Factura.query.filter(
            Factura.fecha >= fecha_inicio,
            Factura.fecha <= fecha_fin
        )
        # No filtramos por estado para incluir todas las facturas
        # Si quieres filtrar solo pagadas, descomenta la línea siguiente:
        # Factura.estado == 'pagada'
        return sum(float(f.total) for f in query.all())
    
    @staticmethod
    def exportar_excel(facturas):
        """Exporta facturas a Excel"""
        output = BytesIO()
        
        data = []
        for f in facturas:
            data.append({
                'Folio': f.folio,
                'Fecha': f.fecha.strftime('%d/%m/%Y %H:%M') if f.fecha else '',
                'Cliente': f.cliente_nombre,
                'Documento': f.cliente_documento or '',
                'Subtotal': float(f.subtotal),
                'IVA': float(f.iva),
                'Total': float(f.total),
                'Método Pago': f.metodo_pago,
                'Estado': f.estado
            })
        
        df = pd.DataFrame(data)
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Facturas', index=False)
            
            # Calcular totales correctamente con float()
            total_ventas = sum(float(f.total) for f in facturas)
            
            resumen = pd.DataFrame({
                'Métrica': ['Total Facturas', 'Total Ventas', 'Fecha Generación'],
                'Valor': [
                    len(facturas),
                    f"${total_ventas:,.2f}",
                    datetime.now().strftime('%d/%m/%Y %H:%M')
                ]
            })
            resumen.to_excel(writer, sheet_name='Resumen', index=False)
        
        output.seek(0)
        return output