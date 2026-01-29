"""Rutas del Backend Principal"""

from flask import Blueprint

from routes.auth import auth_bp
from routes.personas import personas_bp
from routes.cuentas import cuentas_bp
from routes.tarjetas import tarjetas_bp
from routes.transacciones import transacciones_bp
from routes.cajeros import cajeros_bp
from routes.retiros import retiros_bp


def register_blueprints(app):
    """Registrar blueprints"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(personas_bp, url_prefix='/api/personas')
    app.register_blueprint(cuentas_bp, url_prefix='/api/cuentas')
    app.register_blueprint(tarjetas_bp, url_prefix='/api/tarjetas')
    app.register_blueprint(transacciones_bp, url_prefix='/api/transacciones')
    app.register_blueprint(cajeros_bp, url_prefix='/api/cajeros')
    app.register_blueprint(retiros_bp, url_prefix='/api/retiros')
