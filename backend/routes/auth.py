"""Rutas de Autenticación"""

from flask import Blueprint, jsonify, request, session
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, login_manager
from models.persona import Persona, PersonaNatural

auth_bp = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    return Persona.query.get(int(user_id))


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login con cédula/correo y contraseña
    Body: { "usuario": "cedula_o_correo", "password": "contraseña" }
    """
    try:
        data = request.get_json()
        
        if not data or 'usuario' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere usuario y password'
            }), 400
        
        usuario = data['usuario']
        password = data['password']
        
        # Buscar por correo
        persona = Persona.query.filter_by(correo=usuario).first()
        
        # Si no encuentra, buscar por cédula
        if not persona:
            pn = PersonaNatural.query.filter_by(cedula=usuario).first()
            if pn:
                persona = pn.persona
        
        if not persona:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 401
        
        if not persona.check_password(password):
            return jsonify({
                'success': False,
                'error': 'Contraseña incorrecta'
            }), 401
        
        if not persona.activo:
            return jsonify({
                'success': False,
                'error': 'Usuario inactivo'
            }), 401
        
        login_user(persona)
        
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'data': {
                'usuario': persona.to_dict(),
                'token': 'session-based'  # Para implementación con JWT
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    return jsonify({
        'success': True,
        'message': 'Sesión cerrada'
    })


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    """Obtener usuario actual"""
    return jsonify({
        'success': True,
        'data': current_user.to_dict(include_cuentas=True)
    })


@auth_bp.route('/cambiar-password', methods=['POST'])
@login_required
def cambiar_password():
    """
    Cambiar contraseña
    Body: { "password_actual": "...", "password_nuevo": "..." }
    """
    try:
        data = request.get_json()
        
        if not current_user.check_password(data.get('password_actual', '')):
            return jsonify({
                'success': False,
                'error': 'Contraseña actual incorrecta'
            }), 400
        
        current_user.set_password(data['password_nuevo'])
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Contraseña actualizada'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
