"""
Rutas para Pagos de Servicios
GET /api/v1/pagos - Lista historial de pagos
GET /api/v1/pagos/<id> - Obtiene detalle de un pago
POST /api/v1/pagos - Procesa un nuevo pago
"""

from flask import Blueprint, jsonify, request
from extensions import db
from models.pago import PagoServicio
from models.servicio import Servicio
from datetime import datetime
from decimal import Decimal

pagos_bp = Blueprint('pagos', __name__)


@pagos_bp.route('', methods=['GET'])
def listar_pagos():
    """Lista el historial de pagos"""
    try:
        # Parámetros de filtrado
        referencia = request.args.get('referencia')
        id_cuenta = request.args.get('id_cuenta')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        limite = request.args.get('limite', 50, type=int)
        
        query = PagoServicio.query
        
        if referencia:
            query = query.filter(PagoServicio.referencia_cliente.ilike(f'%{referencia}%'))
        
        if id_cuenta:
            query = query.filter_by(id_cuenta=int(id_cuenta))
        
        if fecha_desde:
            query = query.filter(PagoServicio.fecha_pago >= datetime.fromisoformat(fecha_desde))
        
        if fecha_hasta:
            query = query.filter(PagoServicio.fecha_pago <= datetime.fromisoformat(fecha_hasta))
        
        pagos = query.order_by(PagoServicio.fecha_pago.desc()).limit(limite).all()
        
        return jsonify({
            'success': True,
            'data': [p.to_dict(include_servicio=True) for p in pagos],
            'total': len(pagos)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pagos_bp.route('/<int:id_pago>', methods=['GET'])
def obtener_pago(id_pago):
    """Obtiene el detalle de un pago por ID"""
    try:
        pago = PagoServicio.query.get(id_pago)
        
        if not pago:
            return jsonify({
                'success': False,
                'error': f'Pago con ID {id_pago} no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': pago.to_dict(include_servicio=True)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pagos_bp.route('/comprobante/<string:comprobante>', methods=['GET'])
def obtener_por_comprobante(comprobante):
    """Obtiene un pago por número de comprobante"""
    try:
        pago = PagoServicio.query.filter_by(comprobante=comprobante.upper()).first()
        
        if not pago:
            return jsonify({
                'success': False,
                'error': f'Pago con comprobante {comprobante} no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': pago.to_dict(include_servicio=True)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pagos_bp.route('', methods=['POST'])
def procesar_pago():
    """
    Procesa un nuevo pago de servicio
    
    Body JSON:
    {
        "codigo_servicio": "EEQ_LUZ",
        "referencia": "123456789",
        "monto": 45.50,
        "id_cuenta": 1,  (opcional)
        "detalle": "Pago de luz enero 2026"  (opcional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Se requiere un cuerpo JSON'
            }), 400
        
        # Validar campos requeridos
        campos_requeridos = ['codigo_servicio', 'referencia', 'monto']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {campo}'
                }), 400
        
        # Buscar servicio
        servicio = Servicio.query.filter_by(codigo=data['codigo_servicio'].upper()).first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': f'Servicio "{data["codigo_servicio"]}" no encontrado'
            }), 404
        
        if not servicio.activo:
            return jsonify({
                'success': False,
                'error': 'Este servicio no está disponible actualmente'
            }), 400
        
        # Validar monto
        monto_base = Decimal(str(data['monto']))
        
        if servicio.monto_minimo and monto_base < servicio.monto_minimo:
            return jsonify({
                'success': False,
                'error': f'Monto mínimo permitido: ${servicio.monto_minimo}'
            }), 400
        
        if servicio.monto_maximo and monto_base > servicio.monto_maximo:
            return jsonify({
                'success': False,
                'error': f'Monto máximo permitido: ${servicio.monto_maximo}'
            }), 400
        
        # Calcular comisión y total
        comision = servicio.comision or Decimal('0')
        monto_total = monto_base + comision
        
        # Crear registro de pago
        pago = PagoServicio(
            id_servicio=servicio.id_servicio,
            id_cuenta=data.get('id_cuenta'),
            referencia_cliente=data['referencia'],
            monto_base=monto_base,
            comision=comision,
            monto_total=monto_total,
            estado=PagoServicio.ESTADO_COMPLETADO,
            comprobante=PagoServicio.generar_comprobante(),
            detalle=data.get('detalle', f'Pago de {servicio.nombre}')
        )
        
        db.session.add(pago)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pago procesado exitosamente',
            'data': pago.to_dict(include_servicio=True)
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Error en los datos: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
