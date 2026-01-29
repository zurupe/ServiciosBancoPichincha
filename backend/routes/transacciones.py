"""Rutas para Transacciones"""

from flask import Blueprint, jsonify, request
from extensions import db
from models.transaccion import Transaccion
from models.cuenta import Cuenta
from decimal import Decimal
from datetime import datetime, timedelta

transacciones_bp = Blueprint('transacciones', __name__)


@transacciones_bp.route('', methods=['GET'])
def listar_transacciones():
    """Lista transacciones"""
    try:
        id_cuenta = request.args.get('cuenta', type=int)
        tipo = request.args.get('tipo')
        fecha_desde = request.args.get('desde')
        fecha_hasta = request.args.get('hasta')
        limite = request.args.get('limite', 50, type=int)
        
        query = Transaccion.query
        
        if id_cuenta:
            query = query.filter(
                (Transaccion.id_cuenta_origen == id_cuenta) |
                (Transaccion.id_cuenta_destino == id_cuenta)
            )
        if tipo:
            query = query.filter_by(tipo_transaccion=tipo.upper())
        if fecha_desde:
            query = query.filter(Transaccion.fecha_hora >= datetime.fromisoformat(fecha_desde))
        if fecha_hasta:
            query = query.filter(Transaccion.fecha_hora <= datetime.fromisoformat(fecha_hasta))
        
        transacciones = query.order_by(Transaccion.fecha_hora.desc()).limit(limite).all()
        
        return jsonify({
            'success': True,
            'data': [t.to_dict() for t in transacciones],
            'total': len(transacciones)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@transacciones_bp.route('/transferir', methods=['POST'])
def transferir():
    """
    Realiza transferencia entre cuentas
    Body: { "cuenta_origen": 1, "cuenta_destino": 2, "monto": 100.00, "descripcion": "..." }
    """
    try:
        data = request.get_json()
        
        campos = ['cuenta_origen', 'cuenta_destino', 'monto']
        for campo in campos:
            if campo not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {campo}'
                }), 400
        
        origen = Cuenta.query.get(data['cuenta_origen'])
        destino = Cuenta.query.get(data['cuenta_destino'])
        
        if not origen:
            return jsonify({
                'success': False,
                'error': 'Cuenta origen no encontrada'
            }), 404
        
        if not destino:
            return jsonify({
                'success': False,
                'error': 'Cuenta destino no encontrada'
            }), 404
        
        monto = Decimal(str(data['monto']))
        
        if origen.saldo_actual < monto:
            return jsonify({
                'success': False,
                'error': 'Saldo insuficiente'
            }), 400
        
        # Realizar transferencia
        origen.saldo_actual -= monto
        destino.saldo_actual += monto
        
        transaccion = Transaccion(
            id_cuenta_origen=origen.id_cuenta,
            id_cuenta_destino=destino.id_cuenta,
            tipo_transaccion=Transaccion.TIPO_TRANSFERENCIA,
            monto=monto,
            descripcion=data.get('descripcion', 'Transferencia bancaria'),
            referencia=Transaccion.generar_referencia()
        )
        
        db.session.add(transaccion)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transferencia realizada',
            'data': transaccion.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@transacciones_bp.route('/depositar', methods=['POST'])
def depositar():
    """
    Deposita dinero en cuenta
    Body: { "id_cuenta": 1, "monto": 500.00 }
    """
    try:
        data = request.get_json()
        
        cuenta = Cuenta.query.get(data.get('id_cuenta'))
        
        if not cuenta:
            return jsonify({
                'success': False,
                'error': 'Cuenta no encontrada'
            }), 404
        
        monto = Decimal(str(data['monto']))
        
        cuenta.saldo_actual += monto
        
        transaccion = Transaccion(
            id_cuenta_destino=cuenta.id_cuenta,
            tipo_transaccion=Transaccion.TIPO_DEPOSITO,
            monto=monto,
            descripcion='Depósito en efectivo',
            referencia=Transaccion.generar_referencia()
        )
        
        db.session.add(transaccion)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Depósito realizado',
            'data': {
                'transaccion': transaccion.to_dict(),
                'saldo_actual': float(cuenta.saldo_actual)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
