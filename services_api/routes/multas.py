"""
Rutas para Pago de Multas y Citaciones
POST /api/v1/multas/ant - Pagar multa ANT
POST /api/v1/multas/cnt - Pagar factura CNT
POST /api/v1/multas/claro - Pagar factura Claro
GET /api/v1/multas/consultar - Consultar multas pendientes
"""

from flask import Blueprint, jsonify, request
from extensions import db
from models.pago import PagoServicio
from models.servicio import Servicio
from decimal import Decimal
import random

multas_bp = Blueprint('multas', __name__)


@multas_bp.route('', methods=['GET'])
def listar_servicios_multas():
    """Lista servicios de multas disponibles"""
    try:
        servicios = Servicio.query.filter(
            Servicio.codigo.in_([
                'ANT_MULTA_TRANSITO', 'AMT_CITACION',
                'CNT_FACTURA', 'CLARO_FACTURA', 'MOVISTAR_FACTURA'
            ])
        ).all()
        
        return jsonify({
            'success': True,
            'data': [s.to_dict(include_proveedor=True) for s in servicios],
            'total': len(servicios)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@multas_bp.route('/consultar', methods=['POST'])
def consultar_multas():
    """
    Consulta multas pendientes
    Body: { "tipo": "ant|amt|cnt|claro|movistar", "referencia": "cedula_o_placa_o_numero" }
    """
    try:
        data = request.get_json()
        
        if not data or 'tipo' not in data or 'referencia' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere tipo y referencia'
            }), 400
        
        tipo = data['tipo'].lower()
        referencia = data['referencia']
        
        codigo_map = {
            'ant': 'ANT_MULTA_TRANSITO',
            'amt': 'AMT_CITACION',
            'cnt': 'CNT_FACTURA',
            'claro': 'CLARO_FACTURA',
            'movistar': 'MOVISTAR_FACTURA'
        }
        
        if tipo not in codigo_map:
            return jsonify({
                'success': False,
                'error': f'Tipo no válido. Opciones: {", ".join(codigo_map.keys())}'
            }), 400
        
        servicio = Servicio.query.filter_by(codigo=codigo_map[tipo]).first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': 'Servicio no disponible'
            }), 404
        
        # Simulación de consulta de multas/facturas
        if tipo in ['ant', 'amt']:
            # Simulación de multas de tránsito
            num_multas = random.randint(0, 3)
            multas = []
            for i in range(num_multas):
                monto = round(random.uniform(50.00, 400.00), 2)
                multas.append({
                    'numero_citacion': f'CIT-2025-{random.randint(10000, 99999)}',
                    'fecha': f'2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                    'infraccion': random.choice([
                        'Exceso de velocidad',
                        'Estacionamiento prohibido',
                        'No usar cinturón',
                        'Uso de celular'
                    ]),
                    'monto': monto,
                    'estado': 'PENDIENTE'
                })
            
            total = sum(m['monto'] for m in multas)
            
            return jsonify({
                'success': True,
                'data': {
                    'referencia': referencia,
                    'servicio': servicio.to_dict(include_proveedor=True),
                    'multas': multas,
                    'resumen': {
                        'cantidad': num_multas,
                        'monto_total': total,
                        'comision': float(servicio.comision or 0),
                        'total_a_pagar': total + float(servicio.comision or 0)
                    }
                }
            })
        else:
            # Simulación de facturas telefónicas
            monto = round(random.uniform(15.00, 80.00), 2)
            
            return jsonify({
                'success': True,
                'data': {
                    'referencia': referencia,
                    'servicio': servicio.to_dict(include_proveedor=True),
                    'factura': {
                        'numero': f'FAC-{random.randint(100000, 999999)}',
                        'periodo': 'Enero 2026',
                        'monto': monto,
                        'comision': float(servicio.comision or 0),
                        'total': monto + float(servicio.comision or 0),
                        'fecha_vencimiento': '2026-02-10',
                        'estado': 'PENDIENTE'
                    }
                }
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@multas_bp.route('/ant', methods=['POST'])
def pagar_multa_ant():
    """
    Paga multa de tránsito ANT
    Body: { "cedula_placa": "1234567890", "monto": 150.00, "id_cuenta": 1 }
    """
    try:
        data = request.get_json()
        
        if not data or 'cedula_placa' not in data or 'monto' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere cedula_placa y monto'
            }), 400
        
        servicio = Servicio.query.filter_by(codigo='ANT_MULTA_TRANSITO').first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': 'Servicio de multas ANT no disponible'
            }), 404
        
        monto_base = Decimal(str(data['monto']))
        comision = servicio.comision or Decimal('0')
        monto_total = monto_base + comision
        
        pago = PagoServicio(
            id_servicio=servicio.id_servicio,
            id_cuenta=data.get('id_cuenta'),
            referencia_cliente=data['cedula_placa'],
            monto_base=monto_base,
            comision=comision,
            monto_total=monto_total,
            estado=PagoServicio.ESTADO_COMPLETADO,
            comprobante=PagoServicio.generar_comprobante(),
            detalle=f'Pago Multa ANT - Ref: {data["cedula_placa"]}'
        )
        
        db.session.add(pago)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Multa ANT pagada exitosamente',
            'data': pago.to_dict(include_servicio=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@multas_bp.route('/cnt', methods=['POST'])
def pagar_cnt():
    """
    Paga factura CNT
    Body: { "numero_telefono": "022123456", "monto": 35.00, "id_cuenta": 1 }
    """
    try:
        data = request.get_json()
        
        if not data or 'numero_telefono' not in data or 'monto' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere numero_telefono y monto'
            }), 400
        
        servicio = Servicio.query.filter_by(codigo='CNT_FACTURA').first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': 'Servicio CNT no disponible'
            }), 404
        
        monto_base = Decimal(str(data['monto']))
        comision = servicio.comision or Decimal('0')
        monto_total = monto_base + comision
        
        pago = PagoServicio(
            id_servicio=servicio.id_servicio,
            id_cuenta=data.get('id_cuenta'),
            referencia_cliente=data['numero_telefono'],
            monto_base=monto_base,
            comision=comision,
            monto_total=monto_total,
            estado=PagoServicio.ESTADO_COMPLETADO,
            comprobante=PagoServicio.generar_comprobante(),
            detalle=f'Pago Factura CNT - Tel: {data["numero_telefono"]}'
        )
        
        db.session.add(pago)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Factura CNT pagada exitosamente',
            'data': pago.to_dict(include_servicio=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@multas_bp.route('/claro', methods=['POST'])
def pagar_claro():
    """
    Paga factura Claro
    Body: { "numero_linea": "0991234567", "monto": 25.00, "id_cuenta": 1 }
    """
    try:
        data = request.get_json()
        
        if not data or 'numero_linea' not in data or 'monto' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere numero_linea y monto'
            }), 400
        
        servicio = Servicio.query.filter_by(codigo='CLARO_FACTURA').first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': 'Servicio Claro no disponible'
            }), 404
        
        monto_base = Decimal(str(data['monto']))
        comision = servicio.comision or Decimal('0')
        monto_total = monto_base + comision
        
        pago = PagoServicio(
            id_servicio=servicio.id_servicio,
            id_cuenta=data.get('id_cuenta'),
            referencia_cliente=data['numero_linea'],
            monto_base=monto_base,
            comision=comision,
            monto_total=monto_total,
            estado=PagoServicio.ESTADO_COMPLETADO,
            comprobante=PagoServicio.generar_comprobante(),
            detalle=f'Pago Factura Claro - Línea: {data["numero_linea"]}'
        )
        
        db.session.add(pago)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Factura Claro pagada exitosamente',
            'data': pago.to_dict(include_servicio=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
