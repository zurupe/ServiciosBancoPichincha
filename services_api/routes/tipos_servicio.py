"""
Rutas para Tipos de Servicio
GET /api/v1/tipos-servicio - Lista todas las categorías
GET /api/v1/tipos-servicio/<codigo> - Obtiene una categoría por código
"""

from flask import Blueprint, jsonify, request
from models.tipo_servicio import TipoServicio

tipos_bp = Blueprint('tipos_servicio', __name__)


@tipos_bp.route('', methods=['GET'])
def listar_tipos():
    """Lista todas las categorías de servicios"""
    try:
        solo_activos = request.args.get('activos', 'true').lower() == 'true'
        
        query = TipoServicio.query
        if solo_activos:
            query = query.filter_by(activo=True)
        
        tipos = query.order_by(TipoServicio.orden).all()
        
        return jsonify({
            'success': True,
            'data': [t.to_dict() for t in tipos],
            'total': len(tipos)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tipos_bp.route('/<string:codigo>', methods=['GET'])
def obtener_tipo(codigo):
    """Obtiene una categoría por su código"""
    try:
        tipo = TipoServicio.query.filter_by(codigo=codigo.upper()).first()
        
        if not tipo:
            return jsonify({
                'success': False,
                'error': f'Tipo de servicio "{codigo}" no encontrado'
            }), 404
        
        # Incluir proveedores si se solicita
        include_proveedores = request.args.get('proveedores', 'false').lower() == 'true'
        data = tipo.to_dict()
        
        if include_proveedores:
            data['proveedores'] = [
                p.to_dict() for p in tipo.proveedores.filter_by(activo=True)
            ]
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
