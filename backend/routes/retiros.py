"""Rutas para Retiros (con y sin tarjeta)"""

from flask import Blueprint, jsonify, request
from extensions import db
from models.transaccion import Transaccion, RetiroSinTarjeta
from models.cuenta import Cuenta
from models.tarjeta import Tarjeta
from models.cajero import Cajero
from decimal import Decimal
from datetime import datetime, timedelta

retiros_bp = Blueprint('retiros', __name__)


@retiros_bp.route('/con-tarjeta', methods=['POST'])
def retiro_con_tarjeta():
    """
    Retiro con tarjeta en cajero
    Body: { "numero_tarjeta": "4551...", "pin": "1234", "monto": 100, "id_cajero": 1 }
    """
    try:
        data = request.get_json()
        
        campos = ['numero_tarjeta', 'pin', 'monto']
        for campo in campos:
            if campo not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {campo}'
                }), 400
        
        tarjeta = Tarjeta.query.filter_by(numero_tarjeta=data['numero_tarjeta']).first()
        
        if not tarjeta:
            return jsonify({
                'success': False,
                'error': 'Tarjeta no encontrada'
            }), 404
        
        if tarjeta.estado != 'ACTIVA':
            return jsonify({
                'success': False,
                'error': 'Tarjeta bloqueada o inactiva'
            }), 400
        
        if not tarjeta.check_pin(data['pin']):
            return jsonify({
                'success': False,
                'error': 'PIN incorrecto'
            }), 401
        
        cuenta = tarjeta.cuenta
        monto = Decimal(str(data['monto']))
        
        if cuenta.saldo_actual < monto:
            return jsonify({
                'success': False,
                'error': 'Saldo insuficiente'
            }), 400
        
        # Procesar retiro
        cuenta.saldo_actual -= monto
        
        transaccion = Transaccion(
            id_cuenta_origen=cuenta.id_cuenta,
            id_tarjeta=tarjeta.id_tarjeta,
            id_cajero=data.get('id_cajero'),
            tipo_transaccion=Transaccion.TIPO_RETIRO,
            monto=monto,
            descripcion='Retiro en cajero automático',
            referencia=Transaccion.generar_referencia()
        )
        
        db.session.add(transaccion)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Retiro exitoso',
            'data': {
                'transaccion': transaccion.to_dict(),
                'saldo_disponible': float(cuenta.saldo_actual)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@retiros_bp.route('/sin-tarjeta/generar', methods=['POST'])
def generar_codigo_retiro():
    """
    Genera código para retiro sin tarjeta
    Body: { "id_cuenta": 1, "monto": 100 }
    """
    try:
        data = request.get_json()
        
        if 'id_cuenta' not in data or 'monto' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere id_cuenta y monto'
            }), 400
        
        cuenta = Cuenta.query.get(data['id_cuenta'])
        
        if not cuenta:
            return jsonify({
                'success': False,
                'error': 'Cuenta no encontrada'
            }), 404
        
        monto = Decimal(str(data['monto']))
        
        if cuenta.saldo_actual < monto:
            return jsonify({
                'success': False,
                'error': 'Saldo insuficiente'
            }), 400
        
        # Crear código de retiro (válido por 10 minutos)
        retiro = RetiroSinTarjeta(
            id_cuenta=cuenta.id_cuenta,
            codigo=RetiroSinTarjeta.generar_codigo(),
            monto=monto,
            fecha_expiracion=datetime.utcnow() + timedelta(minutes=10)
        )
        
        db.session.add(retiro)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Código generado',
            'data': {
                'codigo': retiro.codigo,
                'monto': float(retiro.monto),
                'expira': retiro.fecha_expiracion.isoformat(),
                'minutos_valido': 10
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@retiros_bp.route('/sin-tarjeta/ejecutar', methods=['POST'])
def ejecutar_retiro_sin_tarjeta():
    """
    Ejecuta retiro sin tarjeta con código
    Body: { "codigo": "123456", "id_cajero": 1 }
    """
    try:
        data = request.get_json()
        
        if 'codigo' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere código'
            }), 400
        
        retiro = RetiroSinTarjeta.query.filter_by(
            codigo=data['codigo'],
            estado=RetiroSinTarjeta.ESTADO_PENDIENTE
        ).first()
        
        if not retiro:
            return jsonify({
                'success': False,
                'error': 'Código no válido o ya usado'
            }), 404
        
        if datetime.utcnow() > retiro.fecha_expiracion:
            retiro.estado = RetiroSinTarjeta.ESTADO_EXPIRADO
            db.session.commit()
            return jsonify({
                'success': False,
                'error': 'Código expirado'
            }), 400
        
        cuenta = retiro.cuenta
        
        if cuenta.saldo_actual < retiro.monto:
            return jsonify({
                'success': False,
                'error': 'Saldo insuficiente'
            }), 400
        
        # Procesar retiro
        cuenta.saldo_actual -= retiro.monto
        retiro.estado = RetiroSinTarjeta.ESTADO_USADO
        retiro.fecha_uso = datetime.utcnow()
        retiro.id_cajero_uso = data.get('id_cajero')
        
        transaccion = Transaccion(
            id_cuenta_origen=cuenta.id_cuenta,
            id_cajero=data.get('id_cajero'),
            tipo_transaccion=Transaccion.TIPO_RETIRO,
            monto=retiro.monto,
            descripcion='Retiro sin tarjeta',
            referencia=Transaccion.generar_referencia()
        )
        
        db.session.add(transaccion)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Retiro exitoso',
            'data': {
                'transaccion': transaccion.to_dict(),
                'saldo_disponible': float(cuenta.saldo_actual)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@retiros_bp.route('/sin-tarjeta/cancelar', methods=['POST'])
def cancelar_codigo():
    """
    Cancela un código de retiro pendiente
    Body: { "codigo": "123456" }
    """
    try:
        data = request.get_json()
        
        retiro = RetiroSinTarjeta.query.filter_by(
            codigo=data.get('codigo'),
            estado=RetiroSinTarjeta.ESTADO_PENDIENTE
        ).first()
        
        if not retiro:
            return jsonify({
                'success': False,
                'error': 'Código no encontrado o ya usado'
            }), 404
        
        retiro.estado = RetiroSinTarjeta.ESTADO_CANCELADO
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Código cancelado'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
