"""Rutas CRUD para Tarjetas"""

from flask import Blueprint, jsonify, request
from extensions import db
from models.tarjeta import Tarjeta, TarjetaDebito, TarjetaCredito
from models.cuenta import Cuenta
from datetime import date
from dateutil.relativedelta import relativedelta

tarjetas_bp = Blueprint('tarjetas', __name__)


@tarjetas_bp.route('', methods=['GET'])
def listar_tarjetas():
    """Lista tarjetas"""
    try:
        id_cuenta = request.args.get('cuenta', type=int)
        tipo = request.args.get('tipo')
        
        query = Tarjeta.query.filter_by(estado='ACTIVA')
        
        if id_cuenta:
            query = query.filter_by(id_cuenta=id_cuenta)
        if tipo:
            query = query.filter_by(tipo_tarjeta=tipo.upper())
        
        tarjetas = query.all()
        
        return jsonify({
            'success': True,
            'data': [t.to_dict() for t in tarjetas],
            'total': len(tarjetas)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tarjetas_bp.route('/debito', methods=['POST'])
def crear_tarjeta_debito():
    """
    Crea tarjeta de débito
    Body: { "id_cuenta": 1, "nombre_titular": "JUAN PEREZ", "pin": "1234" }
    """
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['id_cuenta', 'nombre_titular', 'pin']):
            return jsonify({
                'success': False,
                'error': 'Se requiere id_cuenta, nombre_titular y pin'
            }), 400
        
        cuenta = Cuenta.query.get(data['id_cuenta'])
        if not cuenta:
            return jsonify({
                'success': False,
                'error': 'Cuenta no encontrada'
            }), 404
        
        # Crear tarjeta base
        cvv = Tarjeta.generar_cvv()
        tarjeta = Tarjeta(
            id_cuenta=data['id_cuenta'],
            numero_tarjeta=Tarjeta.generar_numero_tarjeta(),
            nombre_titular=data['nombre_titular'].upper(),
            fecha_expiracion=date.today() + relativedelta(years=5),
            tipo_tarjeta='DEBITO',
            cvv_hash=cvv  # En producción usar hash
        )
        tarjeta.set_pin(data['pin'])
        
        db.session.add(tarjeta)
        db.session.flush()
        
        debito = TarjetaDebito(
            id_tarjeta=tarjeta.id_tarjeta,
            limite_diario_retiro=data.get('limite_retiro', 500),
            limite_diario_compra=data.get('limite_compra', 2000)
        )
        
        db.session.add(debito)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarjeta de débito creada',
            'data': tarjeta.to_dict(ocultar_numero=False)  # Mostrar número solo al crear
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@tarjetas_bp.route('/credito', methods=['POST'])
def crear_tarjeta_credito():
    """
    Crea tarjeta de crédito
    Body: { "id_cuenta": 1, "nombre_titular": "JUAN PEREZ", "pin": "1234", "cupo": 5000 }
    """
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['id_cuenta', 'nombre_titular', 'pin', 'cupo']):
            return jsonify({
                'success': False,
                'error': 'Se requiere id_cuenta, nombre_titular, pin y cupo'
            }), 400
        
        cuenta = Cuenta.query.get(data['id_cuenta'])
        if not cuenta:
            return jsonify({
                'success': False,
                'error': 'Cuenta no encontrada'
            }), 404
        
        cvv = Tarjeta.generar_cvv()
        tarjeta = Tarjeta(
            id_cuenta=data['id_cuenta'],
            numero_tarjeta=Tarjeta.generar_numero_tarjeta(),
            nombre_titular=data['nombre_titular'].upper(),
            fecha_expiracion=date.today() + relativedelta(years=5),
            tipo_tarjeta='CREDITO',
            cvv_hash=cvv
        )
        tarjeta.set_pin(data['pin'])
        
        db.session.add(tarjeta)
        db.session.flush()
        
        credito = TarjetaCredito(
            id_tarjeta=tarjeta.id_tarjeta,
            cupo_total=data['cupo'],
            cupo_disponible=data['cupo']
        )
        
        db.session.add(credito)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarjeta de crédito creada',
            'data': tarjeta.to_dict(ocultar_numero=False)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@tarjetas_bp.route('/<int:id>/bloquear', methods=['POST'])
def bloquear_tarjeta(id):
    """Bloquea una tarjeta"""
    try:
        tarjeta = Tarjeta.query.get(id)
        
        if not tarjeta:
            return jsonify({
                'success': False,
                'error': 'Tarjeta no encontrada'
            }), 404
        
        tarjeta.estado = 'BLOQUEADA'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarjeta bloqueada'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tarjetas_bp.route('/<int:id>/cambiar-pin', methods=['POST'])
def cambiar_pin(id):
    """
    Cambia PIN de tarjeta
    Body: { "pin_actual": "1234", "pin_nuevo": "5678" }
    """
    try:
        tarjeta = Tarjeta.query.get(id)
        
        if not tarjeta:
            return jsonify({
                'success': False,
                'error': 'Tarjeta no encontrada'
            }), 404
        
        data = request.get_json()
        
        if not tarjeta.check_pin(data.get('pin_actual', '')):
            return jsonify({
                'success': False,
                'error': 'PIN actual incorrecto'
            }), 400
        
        tarjeta.set_pin(data['pin_nuevo'])
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'PIN actualizado'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
