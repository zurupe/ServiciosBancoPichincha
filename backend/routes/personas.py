"""Rutas CRUD para Personas"""

from flask import Blueprint, jsonify, request
from app import db
from models.persona import Persona, PersonaNatural, PersonaJuridica
from datetime import datetime

personas_bp = Blueprint('personas', __name__)


@personas_bp.route('', methods=['GET'])
def listar_personas():
    """Lista todas las personas"""
    try:
        tipo = request.args.get('tipo')  # NATURAL o JURIDICA
        activo = request.args.get('activo', 'true').lower() == 'true'
        limite = request.args.get('limite', 50, type=int)
        
        query = Persona.query
        
        if activo:
            query = query.filter_by(activo=True)
        
        personas = query.limit(limite).all()
        
        # Filtrar por tipo si se especifica
        if tipo == 'NATURAL':
            personas = [p for p in personas if p.persona_natural]
        elif tipo == 'JURIDICA':
            personas = [p for p in personas if p.persona_juridica]
        
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in personas],
            'total': len(personas)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@personas_bp.route('/<int:id>', methods=['GET'])
def obtener_persona(id):
    """Obtiene una persona por ID"""
    try:
        persona = Persona.query.get(id)
        
        if not persona:
            return jsonify({
                'success': False,
                'error': 'Persona no encontrada'
            }), 404
        
        include_cuentas = request.args.get('cuentas', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'data': persona.to_dict(include_cuentas=include_cuentas)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@personas_bp.route('/natural', methods=['POST'])
def crear_persona_natural():
    """
    Crea una persona natural
    Body: { "cedula", "nombre", "apellido", "fecha_nacimiento", "celular", "correo", "password", ... }
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        campos = ['cedula', 'nombre', 'apellido', 'fecha_nacimiento', 'celular', 'correo']
        for campo in campos:
            if campo not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {campo}'
                }), 400
        
        # Verificar que no exista
        if PersonaNatural.query.filter_by(cedula=data['cedula']).first():
            return jsonify({
                'success': False,
                'error': 'Ya existe una persona con esta cédula'
            }), 400
        
        if Persona.query.filter_by(correo=data['correo']).first():
            return jsonify({
                'success': False,
                'error': 'Ya existe una persona con este correo'
            }), 400
        
        # Crear persona base
        persona = Persona(
            celular=data['celular'],
            correo=data['correo'],
            patrimonio=data.get('patrimonio', 0)
        )
        
        if 'password' in data:
            persona.set_password(data['password'])
        
        db.session.add(persona)
        db.session.flush()  # Obtener ID
        
        # Crear persona natural
        pn = PersonaNatural(
            id=persona.id,
            cedula=data['cedula'],
            nombre=data['nombre'],
            apellido=data['apellido'],
            fecha_nacimiento=datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date(),
            genero=data.get('genero'),
            estado_civil=data.get('estado_civil'),
            ocupacion=data.get('ocupacion'),
            nacionalidad=data.get('nacionalidad', 'Ecuatoriana'),
            direccion=data.get('direccion')
        )
        
        db.session.add(pn)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Persona creada exitosamente',
            'data': persona.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@personas_bp.route('/juridica', methods=['POST'])
def crear_persona_juridica():
    """
    Crea una persona jurídica
    Body: { "ruc", "razon_social", "fecha_constitucion", "tipo_empresa", "celular", "correo", ... }
    """
    try:
        data = request.get_json()
        
        campos = ['ruc', 'razon_social', 'fecha_constitucion', 'tipo_empresa', 'celular', 'correo']
        for campo in campos:
            if campo not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {campo}'
                }), 400
        
        if PersonaJuridica.query.filter_by(ruc=data['ruc']).first():
            return jsonify({
                'success': False,
                'error': 'Ya existe una empresa con este RUC'
            }), 400
        
        persona = Persona(
            celular=data['celular'],
            correo=data['correo'],
            patrimonio=data.get('patrimonio', 0)
        )
        
        if 'password' in data:
            persona.set_password(data['password'])
        
        db.session.add(persona)
        db.session.flush()
        
        pj = PersonaJuridica(
            id=persona.id,
            ruc=data['ruc'],
            razon_social=data['razon_social'],
            nombre_comercial=data.get('nombre_comercial'),
            fecha_constitucion=datetime.strptime(data['fecha_constitucion'], '%Y-%m-%d').date(),
            tipo_empresa=data['tipo_empresa'],
            representante_legal=data.get('representante_legal'),
            direccion=data.get('direccion')
        )
        
        db.session.add(pj)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Empresa creada exitosamente',
            'data': persona.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@personas_bp.route('/<int:id>', methods=['PUT'])
def actualizar_persona(id):
    """Actualiza una persona"""
    try:
        persona = Persona.query.get(id)
        
        if not persona:
            return jsonify({
                'success': False,
                'error': 'Persona no encontrada'
            }), 404
        
        data = request.get_json()
        
        # Actualizar campos base
        if 'celular' in data:
            persona.celular = data['celular']
        if 'correo' in data:
            persona.correo = data['correo']
        if 'patrimonio' in data:
            persona.patrimonio = data['patrimonio']
        if 'activo' in data:
            persona.activo = data['activo']
        
        # Actualizar persona natural si aplica
        if persona.persona_natural:
            pn = persona.persona_natural
            for campo in ['nombre', 'apellido', 'genero', 'estado_civil', 'ocupacion', 'direccion']:
                if campo in data:
                    setattr(pn, campo, data[campo])
        
        # Actualizar persona jurídica si aplica
        if persona.persona_juridica:
            pj = persona.persona_juridica
            for campo in ['razon_social', 'nombre_comercial', 'tipo_empresa', 'representante_legal', 'direccion']:
                if campo in data:
                    setattr(pj, campo, data[campo])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Persona actualizada',
            'data': persona.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@personas_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_persona(id):
    """Desactiva una persona (soft delete)"""
    try:
        persona = Persona.query.get(id)
        
        if not persona:
            return jsonify({
                'success': False,
                'error': 'Persona no encontrada'
            }), 404
        
        persona.activo = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Persona desactivada'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
