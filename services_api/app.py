"""
API de Servicios - Banco Pichincha
Microservicio independiente para pago de servicios
Puerto: 5002
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import config
import os

# Inicializar extensiones
db = SQLAlchemy()

def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'))
    
    # Registrar blueprints
    from routes import register_blueprints
    register_blueprints(app)
    
    # Ruta raíz
    @app.route('/')
    def index():
        return jsonify({
            'nombre': 'API de Servicios - Banco Pichincha',
            'version': app.config.get('API_VERSION', 'v1'),
            'descripcion': 'Microservicio para pago de servicios públicos, impuestos, matrículas y multas',
            'endpoints': {
                'tipos_servicio': '/api/v1/tipos-servicio',
                'proveedores': '/api/v1/proveedores',
                'servicios': '/api/v1/servicios',
                'pagos': '/api/v1/pagos',
                'impuestos': '/api/v1/impuestos',
                'matricula': '/api/v1/matricula',
                'multas': '/api/v1/multas',
                'servicios_publicos': '/api/v1/servicios-publicos'
            },
            'estado': 'activo'
        })
    
    # Health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'services-api'})
    
    # Manejo de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso no encontrado', 'codigo': 404}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Error interno del servidor', 'codigo': 500}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Solicitud inválida', 'codigo': 400}), 400
    
    return app


# Punto de entrada principal
if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("  API de Servicios - Banco Pichincha")
    print("  Puerto: 5002")
    print("  Documentación: http://localhost:5002/")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5002, debug=True)
