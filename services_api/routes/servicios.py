"""
Rutas para Servicios
GET /api/v1/servicios - Lista todos los servicios
GET /api/v1/servicios/<codigo> - Obtiene un servicio por código
POST /api/v1/servicios/consultar - Consulta deuda por referencia
"""

from flask import Blueprint, jsonify, request
from models.servicio import Servicio
from models.proveedor import ProveedorServicio
import random
from decimal import Decimal

servicios_bp = Blueprint('servicios', __name__)


@servicios_bp.route('', methods=['GET'])
def listar_servicios():
    """Lista todos los servicios disponibles"""
    try:
        solo_activos = request.args.get('activos', 'true').lower() == 'true'
        proveedor = request.args.get('proveedor')
        
        query = Servicio.query
        
        if solo_activos:
            query = query.filter_by(activo=True)
        
        if proveedor:
            prov = ProveedorServicio.query.filter_by(codigo=proveedor.upper()).first()
            if prov:
                query = query.filter_by(id_proveedor=prov.id_proveedor)
        
        servicios = query.all()
        
        return jsonify({
            'success': True,
            'data': [s.to_dict(include_proveedor=True) for s in servicios],
            'total': len(servicios)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_bp.route('/<string:codigo>', methods=['GET'])
def obtener_servicio(codigo):
    """Obtiene un servicio por su código"""
    try:
        servicio = Servicio.query.filter_by(codigo=codigo.upper()).first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': f'Servicio "{codigo}" no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': servicio.to_dict(include_proveedor=True)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_bp.route('/consultar', methods=['POST'])
def consultar_deuda():
    """
    Consulta la deuda pendiente de un servicio
    Body: { "codigo_servicio": "EEQ_LUZ", "referencia": "123456" }
    
    NOTA: Esta es una simulación. En producción se conectaría con
    los sistemas de cada proveedor.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Se requiere un cuerpo JSON con codigo_servicio y referencia'
            }), 400
        
        codigo_servicio = data.get('codigo_servicio')
        referencia = data.get('referencia')
        
        if not codigo_servicio or not referencia:
            return jsonify({
                'success': False,
                'error': 'Se requieren codigo_servicio y referencia'
            }), 400
        
        servicio = Servicio.query.filter_by(codigo=codigo_servicio.upper()).first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': f'Servicio "{codigo_servicio}" no encontrado'
            }), 404
        
        # Simulación de consulta de deuda
        # En producción esto se conectaría con el API del proveedor
        monto_simulado = round(random.uniform(15.00, 250.00), 2)
        
        if servicio.monto_fijo:
            monto_simulado = float(servicio.monto_fijo)
        
        comision = float(servicio.comision or 0)
        monto_total = monto_simulado + comision
        
        return jsonify({
            'success': True,
            'data': {
                'servicio': servicio.to_dict(include_proveedor=True),
                'referencia': referencia,
                'deuda': {
                    'monto_base': monto_simulado,
                    'comision': comision,
                    'monto_total': round(monto_total, 2),
                    'moneda': 'USD',
                    'estado': 'PENDIENTE',
                    'fecha_vencimiento': '2026-02-15',
                    'descripcion': f'Deuda pendiente - Referencia: {referencia}'
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
