"""Rutas CRUD para Cuentas"""

from flask import Blueprint, jsonify, request
from extensions import db
from models.cuenta import Cuenta, CuentaAhorros, CuentaCorriente
from models.persona import Persona

cuentas_bp = Blueprint('cuentas', __name__)


@cuentas_bp.route('', methods=['GET'])
def listar_cuentas():
    """Lista todas las cuentas"""
    try:
        id_persona = request.args.get('persona', type=int)
        tipo = request.args.get('tipo')
        
        query = Cuenta.query
        
        if id_persona:
            query = query.filter_by(id_persona=id_persona)
        if tipo:
            query = query.filter_by(tipo_cuenta=tipo.upper())
        
        cuentas = query.filter_by(estado='ACTIVA').all()
        
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in cuentas],
            'total': len(cuentas)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cuentas_bp.route('/<int:id>', methods=['GET'])
def obtener_cuenta(id):
    """Obtiene una cuenta por ID"""
    try:
        cuenta = Cuenta.query.get(id)
        
        if not cuenta:
            return jsonify({
                'success': False,
                'error': 'Cuenta no encontrada'
            }), 404
        
        include_tarjetas = request.args.get('tarjetas', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'data': cuenta.to_dict(include_tarjetas=include_tarjetas)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cuentas_bp.route('/numero/<string:numero>', methods=['GET'])
def obtener_por_numero(numero):
    """Obtiene cuenta por número"""
    try:
        cuenta = Cuenta.query.filter_by(numero_cuenta=numero).first()
        
        if not cuenta:
            return jsonify({
                'success': False,
                'error': 'Cuenta no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': cuenta.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cuentas_bp.route('/ahorros', methods=['POST'])
def crear_cuenta_ahorros():
    """
    Crea cuenta de ahorros
    Body: { "id_persona": 1, "saldo_inicial": 100 }
    """
    try:
        data = request.get_json()
        
        if 'id_persona' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere id_persona'
            }), 400
        
        persona = Persona.query.get(data['id_persona'])
        if not persona:
            return jsonify({
                'success': False,
                'error': 'Persona no encontrada'
            }), 404
        
        # Crear cuenta base
        cuenta = Cuenta(
            id_persona=data['id_persona'],
            numero_cuenta=Cuenta.generar_numero_cuenta(),
            tipo_cuenta='AHORROS',
            saldo_actual=data.get('saldo_inicial', 0)
        )
        
        db.session.add(cuenta)
        db.session.flush()
        
        # Crear detalle de ahorros
        ahorros = CuentaAhorros(
            id_cuenta=cuenta.id_cuenta,
            tipo_ahorro=data.get('tipo_ahorro', 'BASICA'),
            tasa_interes=data.get('tasa_interes', 0.0100)
        )
        
        db.session.add(ahorros)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cuenta de ahorros creada',
            'data': cuenta.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@cuentas_bp.route('/corriente', methods=['POST'])
def crear_cuenta_corriente():
    """
    Crea cuenta corriente
    Body: { "id_persona": 1, "saldo_inicial": 500, "sobregiro": 1000 }
    """
    try:
        data = request.get_json()
        
        if 'id_persona' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere id_persona'
            }), 400
        
        persona = Persona.query.get(data['id_persona'])
        if not persona:
            return jsonify({
                'success': False,
                'error': 'Persona no encontrada'
            }), 404
        
        cuenta = Cuenta(
            id_persona=data['id_persona'],
            numero_cuenta=Cuenta.generar_numero_cuenta(),
            tipo_cuenta='CORRIENTE',
            saldo_actual=data.get('saldo_inicial', 0)
        )
        
        db.session.add(cuenta)
        db.session.flush()
        
        corriente = CuentaCorriente(
            id_cuenta=cuenta.id_cuenta,
            sobregiro_autorizado=data.get('sobregiro', 0)
        )
        
        db.session.add(corriente)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cuenta corriente creada',
            'data': cuenta.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@cuentas_bp.route('/<int:id>/saldo', methods=['GET'])
def consultar_saldo(id):
    """Consulta saldo de cuenta"""
    try:
        cuenta = Cuenta.query.get(id)
        
        if not cuenta:
            return jsonify({
                'success': False,
                'error': 'Cuenta no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'numero_cuenta': cuenta.numero_cuenta,
                'saldo_actual': float(cuenta.saldo_actual),
                'saldo_disponible': float(cuenta.saldo_actual),  # Simplificado
                'moneda': 'USD'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
