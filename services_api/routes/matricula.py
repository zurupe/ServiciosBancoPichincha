"""
Rutas para Pago de Matrícula Vehicular
POST /api/v1/matricula/vehicular - Pagar matrícula
GET /api/v1/matricula/consultar - Consultar valor de matrícula
"""

from flask import Blueprint, jsonify, request
from app import db
from models.pago import PagoServicio
from models.servicio import Servicio
from decimal import Decimal
import random

matricula_bp = Blueprint('matricula', __name__)


@matricula_bp.route('', methods=['GET'])
def listar_servicios_matricula():
    """Lista servicios de matrícula vehicular disponibles"""
    try:
        servicios = Servicio.query.filter(
            Servicio.codigo.in_(['MATRICULA_VEHICULAR', 'IMP_VEHICULAR'])
        ).all()
        
        return jsonify({
            'success': True,
            'data': [s.to_dict(include_proveedor=True) for s in servicios],
            'total': len(servicios)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@matricula_bp.route('/consultar', methods=['POST'])
def consultar_matricula():
    """
    Consulta valor de matrícula vehicular
    Body: { "placa": "PBM-1234" }
    """
    try:
        data = request.get_json()
        
        if not data or 'placa' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere el número de placa'
            }), 400
        
        placa = data['placa'].upper().replace(' ', '-')
        
        # Simulación de consulta de matrícula
        # Valores basados en cilindraje y año del vehículo (simulado)
        valor_matricula = round(random.uniform(80.00, 350.00), 2)
        impuesto_vehicular = round(random.uniform(20.00, 150.00), 2)
        
        servicio_matricula = Servicio.query.filter_by(codigo='MATRICULA_VEHICULAR').first()
        servicio_impuesto = Servicio.query.filter_by(codigo='IMP_VEHICULAR').first()
        
        comision_matricula = float(servicio_matricula.comision) if servicio_matricula else 1.00
        
        return jsonify({
            'success': True,
            'data': {
                'placa': placa,
                'vehiculo': {
                    'marca': 'CHEVROLET',
                    'modelo': 'AVEO',
                    'anio': 2020,
                    'cilindraje': 1500
                },
                'valores': {
                    'matricula': {
                        'valor': valor_matricula,
                        'comision': comision_matricula,
                        'total': valor_matricula + comision_matricula
                    },
                    'impuesto_vehicular': {
                        'valor': impuesto_vehicular,
                        'comision': 0,
                        'total': impuesto_vehicular
                    },
                    'total_general': valor_matricula + impuesto_vehicular + comision_matricula
                },
                'estado': 'PENDIENTE',
                'fecha_vencimiento': '2026-12-31'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@matricula_bp.route('/vehicular', methods=['POST'])
def pagar_matricula():
    """
    Paga matrícula vehicular
    Body: { "placa": "PBM-1234", "monto": 250.00, "id_cuenta": 1 }
    """
    try:
        data = request.get_json()
        
        if not data or 'placa' not in data or 'monto' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere placa y monto'
            }), 400
        
        servicio = Servicio.query.filter_by(codigo='MATRICULA_VEHICULAR').first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': 'Servicio de matrícula vehicular no disponible'
            }), 404
        
        placa = data['placa'].upper().replace(' ', '-')
        monto_base = Decimal(str(data['monto']))
        comision = servicio.comision or Decimal('0')
        monto_total = monto_base + comision
        
        pago = PagoServicio(
            id_servicio=servicio.id_servicio,
            id_cuenta=data.get('id_cuenta'),
            referencia_cliente=placa,
            monto_base=monto_base,
            comision=comision,
            monto_total=monto_total,
            estado=PagoServicio.ESTADO_COMPLETADO,
            comprobante=PagoServicio.generar_comprobante(),
            detalle=f'Pago Matrícula Vehicular - Placa: {placa}'
        )
        
        db.session.add(pago)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Matrícula vehicular pagada exitosamente',
            'data': pago.to_dict(include_servicio=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@matricula_bp.route('/impuesto-vehicular', methods=['POST'])
def pagar_impuesto_vehicular():
    """
    Paga impuesto a la propiedad de vehículos
    Body: { "placa": "PBM-1234", "monto": 100.00, "id_cuenta": 1 }
    """
    try:
        data = request.get_json()
        
        if not data or 'placa' not in data or 'monto' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere placa y monto'
            }), 400
        
        servicio = Servicio.query.filter_by(codigo='IMP_VEHICULAR').first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': 'Servicio de impuesto vehicular no disponible'
            }), 404
        
        placa = data['placa'].upper().replace(' ', '-')
        monto_base = Decimal(str(data['monto']))
        comision = servicio.comision or Decimal('0')
        monto_total = monto_base + comision
        
        pago = PagoServicio(
            id_servicio=servicio.id_servicio,
            id_cuenta=data.get('id_cuenta'),
            referencia_cliente=placa,
            monto_base=monto_base,
            comision=comision,
            monto_total=monto_total,
            estado=PagoServicio.ESTADO_COMPLETADO,
            comprobante=PagoServicio.generar_comprobante(),
            detalle=f'Pago Impuesto Vehicular - Placa: {placa}'
        )
        
        db.session.add(pago)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Impuesto vehicular pagado exitosamente',
            'data': pago.to_dict(include_servicio=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
