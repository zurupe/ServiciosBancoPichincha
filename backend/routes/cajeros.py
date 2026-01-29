"""Rutas para Cajeros"""

from flask import Blueprint, jsonify, request
from app import db
from models.cajero import Cajero

cajeros_bp = Blueprint('cajeros', __name__)


@cajeros_bp.route('', methods=['GET'])
def listar_cajeros():
    """Lista cajeros activos"""
    try:
        ciudad = request.args.get('ciudad')
        solo_activos = request.args.get('activos', 'true').lower() == 'true'
        
        query = Cajero.query
        
        if solo_activos:
            query = query.filter_by(activo=True)
        if ciudad:
            query = query.filter(Cajero.ciudad.ilike(f'%{ciudad}%'))
        
        cajeros = query.all()
        
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in cajeros],
            'total': len(cajeros)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cajeros_bp.route('/<int:id>', methods=['GET'])
def obtener_cajero(id):
    """Obtiene un cajero por ID"""
    try:
        cajero = Cajero.query.get(id)
        
        if not cajero:
            return jsonify({
                'success': False,
                'error': 'Cajero no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': cajero.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cajeros_bp.route('/cercanos', methods=['GET'])
def buscar_cercanos():
    """
    Busca cajeros cercanos a una ubicación
    Query: ?lat=-0.1807&lon=-78.4678&radio=5
    """
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        radio_km = request.args.get('radio', 5, type=float)
        
        if lat is None or lon is None:
            return jsonify({
                'success': False,
                'error': 'Se requiere lat y lon'
            }), 400
        
        # Búsqueda simple por rango (aproximado)
        # En producción usar PostGIS para cálculos geoespaciales
        delta = radio_km / 111  # Aproximación: 1 grado ≈ 111 km
        
        cajeros = Cajero.query.filter(
            Cajero.activo == True,
            Cajero.latitud.between(lat - delta, lat + delta),
            Cajero.longitud.between(lon - delta, lon + delta)
        ).all()
        
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in cajeros],
            'total': len(cajeros)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
