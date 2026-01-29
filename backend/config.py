import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración del Backend Principal"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'banco-pichincha-backend-secret-2026'
    
    # PostgreSQL
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'banco_pichincha')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API de Servicios
    SERVICES_API_URL = os.environ.get('SERVICES_API_URL', 'http://localhost:5002')
    
    # Configuración de sesión
    SESSION_TYPE = 'filesystem'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
