"""
Rutas para Proveedores de Servicio
GET /api/v1/proveedores - Lista todos los proveedores
GET /api/v1/proveedores/<codigo> - Obtiene un proveedor por código
GET /api/v1/proveedores/categoria/<categoria> - Lista proveedores por categoría
"""

from flask import Blueprint, jsonify, request
from models.proveedor import ProveedorServicio
from models.tipo_servicio import TipoServicio

proveedores_bp = Blueprint('proveedores', __name__)


@proveedores_bp.route('', methods=['GET'])
def listar_proveedores():
    """Lista todos los proveedores de servicios"""
    try:
        solo_activos = request.args.get('activos', 'true').lower() == 'true'
        categoria = request.args.get('categoria')
        
        query = ProveedorServicio.query
        
        if solo_activos:
            query = query.filter_by(activo=True)
        
        if categoria:
            tipo = TipoServicio.query.filter_by(codigo=categoria.upper()).first()
            if tipo:
                query = query.filter_by(id_tipo=tipo.id_tipo)
        
        proveedores = query.all()
        
        return jsonify({
            'success': True,
            'data': [p.to_dict(include_tipo=True) for p in proveedores],
            'total': len(proveedores)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@proveedores_bp.route('/<string:codigo>', methods=['GET'])
def obtener_proveedor(codigo):
    """Obtiene un proveedor por su código"""
    try:
        proveedor = ProveedorServicio.query.filter_by(codigo=codigo.upper()).first()
        
        if not proveedor:
            return jsonify({
                'success': False,
                'error': f'Proveedor "{codigo}" no encontrado'
            }), 404
        
        include_servicios = request.args.get('servicios', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'data': proveedor.to_dict(include_tipo=True, include_servicios=include_servicios)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@proveedores_bp.route('/categoria/<string:categoria>', methods=['GET'])
def listar_por_categoria(categoria):
    """Lista proveedores por categoría (IMPUESTOS, MATRICULA, MULTAS, SERVICIOS)"""
    try:
        tipo = TipoServicio.query.filter_by(codigo=categoria.upper()).first()
        
        if not tipo:
            return jsonify({
                'success': False,
                'error': f'Categoría "{categoria}" no encontrada. Categorías válidas: IMPUESTOS, MATRICULA, MULTAS, SERVICIOS'
            }), 404
        
        solo_activos = request.args.get('activos', 'true').lower() == 'true'
        query = ProveedorServicio.query.filter_by(id_tipo=tipo.id_tipo)
        
        if solo_activos:
            query = query.filter_by(activo=True)
        
        proveedores = query.all()
        
        return jsonify({
            'success': True,
            'categoria': tipo.to_dict(),
            'data': [p.to_dict(include_servicios=True) for p in proveedores],
            'total': len(proveedores)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
