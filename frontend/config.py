import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración del Frontend"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'banco-pichincha-frontend-2026'
    
    # URLs de las APIs
    BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:5001')
    SERVICES_API_URL = os.environ.get('SERVICES_API_URL', 'http://localhost:5002')
    
    # Sesión
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'
