"""
Rutas para Pago de Servicios Públicos
POST /api/v1/servicios-publicos/luz - Pagar servicio de luz
POST /api/v1/servicios-publicos/agua - Pagar servicio de agua
POST /api/v1/servicios-publicos/telefono - Pagar telefonía fija
POST /api/v1/servicios-publicos/internet - Pagar internet
GET /api/v1/servicios-publicos/consultar - Consultar planillas
"""

from flask import Blueprint, jsonify, request
from extensions import db
from models.pago import PagoServicio
from models.servicio import Servicio
from models.proveedor import ProveedorServicio
from models.tipo_servicio import TipoServicio
from decimal import Decimal
import random

servicios_publicos_bp = Blueprint('servicios_publicos', __name__)


@servicios_publicos_bp.route('', methods=['GET'])
def listar_servicios_publicos():
    """Lista todos los servicios públicos disponibles"""
    try:
        tipo = TipoServicio.query.filter_by(codigo='SERVICIOS').first()
        
        if not tipo:
            return jsonify({
                'success': True,
                'data': [],
                'total': 0
            })
        
        proveedores = ProveedorServicio.query.filter_by(id_tipo=tipo.id_tipo, activo=True).all()
        servicios = []
        for prov in proveedores:
            servicios.extend(Servicio.query.filter_by(id_proveedor=prov.id_proveedor, activo=True).all())
        
        return jsonify({
            'success': True,
            'data': [s.to_dict(include_proveedor=True) for s in servicios],
            'total': len(servicios)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_publicos_bp.route('/consultar', methods=['POST'])
def consultar_planilla():
    """
    Consulta planilla de servicio público
    Body: { "tipo": "luz|agua|telefono|internet", "numero_cuenta": "123456" }
    """
    try:
        data = request.get_json()
        
        if not data or 'tipo' not in data or 'numero_cuenta' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere tipo (luz/agua/telefono/internet) y numero_cuenta'
            }), 400
        
        tipo = data['tipo'].lower()
        numero_cuenta = data['numero_cuenta']
        
        codigo_map = {
            'luz': ['EEQ_LUZ', 'CNEL_LUZ'],
            'agua': ['EMAAP_AGUA', 'INTERAGUA_AGUA', 'ETAPA_AGUA'],
            'telefono': ['CNT_TELEFONO'],
            'internet': ['CNT_NET']
        }
        
        if tipo not in codigo_map:
            return jsonify({
                'success': False,
                'error': f'Tipo no válido. Opciones: {", ".join(codigo_map.keys())}'
            }), 400
        
        # Buscar el primer servicio disponible del tipo
        servicio = None
        for codigo in codigo_map[tipo]:
            servicio = Servicio.query.filter_by(codigo=codigo).first()
            if servicio:
                break
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': 'Servicio no disponible'
            }), 404
        
        # Simulación de consulta de planilla
        consumo = random.randint(50, 300)
        monto = round(random.uniform(10.00, 80.00), 2)
        
        return jsonify({
            'success': True,
            'data': {
                'servicio': servicio.to_dict(include_proveedor=True),
                'numero_cuenta': numero_cuenta,
                'planilla': {
                    'numero': f'PLN-{random.randint(100000, 999999)}',
                    'periodo': 'Enero 2026',
                    'consumo': consumo,
                    'unidad': 'kWh' if tipo == 'luz' else ('m³' if tipo == 'agua' else 'minutos'),
                    'monto_consumo': monto,
                    'cargo_fijo': 2.50,
                    'otros_cargos': 1.00,
                    'subtotal': monto + 3.50,
                    'comision': float(servicio.comision or 0),
                    'total': monto + 3.50 + float(servicio.comision or 0),
                    'fecha_emision': '2026-01-20',
                    'fecha_vencimiento': '2026-02-10',
                    'estado': 'PENDIENTE'
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_publicos_bp.route('/luz', methods=['POST'])
def pagar_luz():
    """
    Paga servicio de luz (EEQ o CNEL)
    Body: { "numero_suministro": "123456", "monto": 45.00, "proveedor": "EEQ", "id_cuenta": 1 }
    """
    try:
        data = request.get_json()
        
        if not data or 'numero_suministro' not in data or 'monto' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere numero_suministro y monto'
            }), 400
        
        proveedor = data.get('proveedor', 'EEQ').upper()
        codigo = 'EEQ_LUZ' if proveedor == 'EEQ' else 'CNEL_LUZ'
        
        servicio = Servicio.query.filter_by(codigo=codigo).first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': f'Servicio de luz {proveedor} no disponible'
            }), 404
        
        monto_base = Decimal(str(data['monto']))
        comision = servicio.comision or Decimal('0')
        monto_total = monto_base + comision
        
        pago = PagoServicio(
            id_servicio=servicio.id_servicio,
            id_cuenta=data.get('id_cuenta'),
            referencia_cliente=data['numero_suministro'],
            monto_base=monto_base,
            comision=comision,
            monto_total=monto_total,
            estado=PagoServicio.ESTADO_COMPLETADO,
            comprobante=PagoServicio.generar_comprobante(),
            detalle=f'Pago Luz {proveedor} - Suministro: {data["numero_suministro"]}'
        )
        
        db.session.add(pago)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Servicio de luz pagado exitosamente',
            'data': pago.to_dict(include_servicio=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_publicos_bp.route('/agua', methods=['POST'])
def pagar_agua():
    """
    Paga servicio de agua
    Body: { "numero_cuenta": "123456", "monto": 25.00, "proveedor": "EMAAP", "id_cuenta": 1 }
    """
    try:
        data = request.get_json()
        
        if not data or 'numero_cuenta' not in data or 'monto' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere numero_cuenta y monto'
            }), 400
        
        proveedor = data.get('proveedor', 'EMAAP').upper()
        codigo_map = {
            'EMAAP': 'EMAAP_AGUA',
            'INTERAGUA': 'INTERAGUA_AGUA',
            'ETAPA': 'ETAPA_AGUA'
        }
        
        codigo = codigo_map.get(proveedor, 'EMAAP_AGUA')
        servicio = Servicio.query.filter_by(codigo=codigo).first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': f'Servicio de agua {proveedor} no disponible'
            }), 404
        
        monto_base = Decimal(str(data['monto']))
        comision = servicio.comision or Decimal('0')
        monto_total = monto_base + comision
        
        pago = PagoServicio(
            id_servicio=servicio.id_servicio,
            id_cuenta=data.get('id_cuenta'),
            referencia_cliente=data['numero_cuenta'],
            monto_base=monto_base,
            comision=comision,
            monto_total=monto_total,
            estado=PagoServicio.ESTADO_COMPLETADO,
            comprobante=PagoServicio.generar_comprobante(),
            detalle=f'Pago Agua {proveedor} - Cuenta: {data["numero_cuenta"]}'
        )
        
        db.session.add(pago)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Servicio de agua pagado exitosamente',
            'data': pago.to_dict(include_servicio=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_publicos_bp.route('/telefono', methods=['POST'])
def pagar_telefono():
    """
    Paga servicio de telefonía fija
    Body: { "numero_telefono": "022123456", "monto": 18.00, "id_cuenta": 1 }
    """
    try:
        data = request.get_json()
        
        if not data or 'numero_telefono' not in data or 'monto' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere numero_telefono y monto'
            }), 400
        
        servicio = Servicio.query.filter_by(codigo='CNT_TELEFONO').first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': 'Servicio de telefonía no disponible'
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
            detalle=f'Pago Teléfono CNT - Tel: {data["numero_telefono"]}'
        )
        
        db.session.add(pago)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Servicio de telefonía pagado exitosamente',
            'data': pago.to_dict(include_servicio=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@servicios_publicos_bp.route('/internet', methods=['POST'])
def pagar_internet():
    """
    Paga servicio de internet
    Body: { "numero_cuenta": "123456", "monto": 35.00, "id_cuenta": 1 }
    """
    try:
        data = request.get_json()
        
        if not data or 'numero_cuenta' not in data or 'monto' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere numero_cuenta y monto'
            }), 400
        
        servicio = Servicio.query.filter_by(codigo='CNT_NET').first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': 'Servicio de internet no disponible'
            }), 404
        
        monto_base = Decimal(str(data['monto']))
        comision = servicio.comision or Decimal('0')
        monto_total = monto_base + comision
        
        pago = PagoServicio(
            id_servicio=servicio.id_servicio,
            id_cuenta=data.get('id_cuenta'),
            referencia_cliente=data['numero_cuenta'],
            monto_base=monto_base,
            comision=comision,
            monto_total=monto_total,
            estado=PagoServicio.ESTADO_COMPLETADO,
            comprobante=PagoServicio.generar_comprobante(),
            detalle=f'Pago Internet CNT - Cuenta: {data["numero_cuenta"]}'
        )
        
        db.session.add(pago)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Servicio de internet pagado exitosamente',
            'data': pago.to_dict(include_servicio=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
