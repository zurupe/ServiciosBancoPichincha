"""
Backend Principal - Banco Pichincha
API REST para gestión bancaria
Puerto: 5001
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
import os

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    CORS(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Registrar blueprints
    from routes import register_blueprints
    register_blueprints(app)
    
    # Ruta raíz
    @app.route('/')
    def index():
        return jsonify({
            'nombre': 'Backend Banco Pichincha',
            'version': 'v1',
            'puerto': 5001,
            'endpoints': {
                'auth': '/api/auth',
                'personas': '/api/personas',
                'cuentas': '/api/cuentas',
                'tarjetas': '/api/tarjetas',
                'transacciones': '/api/transacciones',
                'cajeros': '/api/cajeros',
                'retiros': '/api/retiros'
            }
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'backend'})
    
    # Manejo de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'No encontrado', 'codigo': 404}), 404
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'No autorizado', 'codigo': 401}), 401
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Error interno', 'codigo': 500}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("  Backend Banco Pichincha")
    print("  Puerto: 5001")
    print("  http://localhost:5001/")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)
