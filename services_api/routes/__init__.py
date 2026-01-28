"""
Rutas de la API de Servicios
Registra todos los blueprints
"""

from flask import Blueprint

# Importar blueprints
from routes.tipos_servicio import tipos_bp
from routes.proveedores import proveedores_bp
from routes.servicios import servicios_bp
from routes.pagos import pagos_bp
from routes.impuestos import impuestos_bp
from routes.matricula import matricula_bp
from routes.multas import multas_bp
from routes.servicios_publicos import servicios_publicos_bp


def register_blueprints(app):
    """Registrar todos los blueprints en la aplicación"""
    prefix = app.config.get('API_PREFIX', '/api/v1')
    
    app.register_blueprint(tipos_bp, url_prefix=f'{prefix}/tipos-servicio')
    app.register_blueprint(proveedores_bp, url_prefix=f'{prefix}/proveedores')
    app.register_blueprint(servicios_bp, url_prefix=f'{prefix}/servicios')
    app.register_blueprint(pagos_bp, url_prefix=f'{prefix}/pagos')
    app.register_blueprint(impuestos_bp, url_prefix=f'{prefix}/impuestos')
    app.register_blueprint(matricula_bp, url_prefix=f'{prefix}/matricula')
    app.register_blueprint(multas_bp, url_prefix=f'{prefix}/multas')
    app.register_blueprint(servicios_publicos_bp, url_prefix=f'{prefix}/servicios-publicos')
