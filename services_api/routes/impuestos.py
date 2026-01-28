"""
Rutas para Pago de Impuestos
POST /api/v1/impuestos/predial - Pagar impuesto predial
POST /api/v1/impuestos/municipal - Pagar impuesto municipal
GET /api/v1/impuestos/consultar - Consultar deuda de impuestos
"""

from flask import Blueprint, jsonify, request
from app import db
from models.pago import PagoServicio
from models.servicio import Servicio
from models.proveedor import ProveedorServicio
from models.tipo_servicio import TipoServicio
from decimal import Decimal
import random

impuestos_bp = Blueprint('impuestos', __name__)


def _obtener_servicios_impuestos():
    """Obtiene todos los servicios de la categoría IMPUESTOS"""
    tipo = TipoServicio.query.filter_by(codigo='IMPUESTOS').first()
    if not tipo:
        return []
    
    proveedores = ProveedorServicio.query.filter_by(id_tipo=tipo.id_tipo, activo=True).all()
    servicios = []
    for prov in proveedores:
        servicios.extend(Servicio.query.filter_by(id_proveedor=prov.id_proveedor, activo=True).all())
    return servicios


@impuestos_bp.route('', methods=['GET'])
def listar_impuestos():
    """Lista todos los servicios de impuestos disponibles"""
    try:
        servicios = _obtener_servicios_impuestos()
        return jsonify({
            'success': True,
            'data': [s.to_dict(include_proveedor=True) for s in servicios],
            'total': len(servicios)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@impuestos_bp.route('/consultar', methods=['POST'])
def consultar_impuesto():
    """
    Consulta deuda de impuestos
    Body: { "tipo": "predial|municipal|renta|iva", "referencia": "numero_predio_o_ruc" }
    """
    try:
        data = request.get_json()
        
        if not data or 'tipo' not in data or 'referencia' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere tipo (predial/municipal/renta/iva) y referencia'
            }), 400
        
        tipo = data['tipo'].lower()
        referencia = data['referencia']
        
        # Mapeo de tipos a códigos de servicio
        codigo_map = {
            'predial': 'QUITO_PREDIAL',
            'municipal': 'QUITO_PATENTE',
            'renta': 'SRI_RENTA',
            'iva': 'SRI_IVA'
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
        
        # Simulación de consulta
        monto_simulado = round(random.uniform(50.00, 500.00), 2)
        
        return jsonify({
            'success': True,
            'data': {
                'tipo_impuesto': tipo,
                'servicio': servicio.to_dict(include_proveedor=True),
                'referencia': referencia,
                'deuda': {
                    'anio_fiscal': 2025,
                    'monto_base': monto_simulado,
                    'recargo': 0,
                    'interes': 0,
                    'comision': float(servicio.comision or 0),
                    'monto_total': monto_simulado + float(servicio.comision or 0),
                    'estado': 'PENDIENTE',
                    'fecha_vencimiento': '2026-03-31'
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@impuestos_bp.route('/predial', methods=['POST'])
def pagar_predial():
    """
    Paga impuesto predial
    Body: { "numero_predio": "123456", "monto": 150.00, "id_cuenta": 1 }
    """
    try:
        data = request.get_json()
        
        if not data or 'numero_predio' not in data or 'monto' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere numero_predio y monto'
            }), 400
        
        servicio = Servicio.query.filter_by(codigo='QUITO_PREDIAL').first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': 'Servicio de impuesto predial no disponible'
            }), 404
        
        monto_base = Decimal(str(data['monto']))
        comision = servicio.comision or Decimal('0')
        monto_total = monto_base + comision
        
        pago = PagoServicio(
            id_servicio=servicio.id_servicio,
            id_cuenta=data.get('id_cuenta'),
            referencia_cliente=data['numero_predio'],
            monto_base=monto_base,
            comision=comision,
            monto_total=monto_total,
            estado=PagoServicio.ESTADO_COMPLETADO,
            comprobante=PagoServicio.generar_comprobante(),
            detalle=f'Pago Impuesto Predial - Predio: {data["numero_predio"]}'
        )
        
        db.session.add(pago)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Impuesto predial pagado exitosamente',
            'data': pago.to_dict(include_servicio=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@impuestos_bp.route('/municipal', methods=['POST'])
def pagar_municipal():
    """
    Paga impuesto/patente municipal
    Body: { "ruc_cedula": "1234567890", "monto": 200.00, "id_cuenta": 1 }
    """
    try:
        data = request.get_json()
        
        if not data or 'ruc_cedula' not in data or 'monto' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere ruc_cedula y monto'
            }), 400
        
        servicio = Servicio.query.filter_by(codigo='QUITO_PATENTE').first()
        
        if not servicio:
            return jsonify({
                'success': False,
                'error': 'Servicio de patente municipal no disponible'
            }), 404
        
        monto_base = Decimal(str(data['monto']))
        comision = servicio.comision or Decimal('0')
        monto_total = monto_base + comision
        
        pago = PagoServicio(
            id_servicio=servicio.id_servicio,
            id_cuenta=data.get('id_cuenta'),
            referencia_cliente=data['ruc_cedula'],
            monto_base=monto_base,
            comision=comision,
            monto_total=monto_total,
            estado=PagoServicio.ESTADO_COMPLETADO,
            comprobante=PagoServicio.generar_comprobante(),
            detalle=f'Pago Patente Municipal - RUC/Cédula: {data["ruc_cedula"]}'
        )
        
        db.session.add(pago)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Patente municipal pagada exitosamente',
            'data': pago.to_dict(include_servicio=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
