"""Modelo Persona - Cliente del banco"""

from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Persona(db.Model, UserMixin):
    """Persona base del sistema bancario"""
    __tablename__ = 'persona'
    
    id = db.Column(db.Integer, primary_key=True)
    celular = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    patrimonio = db.Column(db.Numeric(15, 2), default=0)
    password_hash = db.Column(db.String(256))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    cuentas = db.relationship('Cuenta', backref='propietario', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_cuentas=False):
        data = {
            'id': self.id,
            'celular': self.celular,
            'correo': self.correo,
            'patrimonio': float(self.patrimonio) if self.patrimonio else 0,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'activo': self.activo
        }
        
        # Intentar obtener datos de persona natural o jurídica
        if hasattr(self, 'persona_natural') and self.persona_natural:
            data['tipo'] = 'NATURAL'
            data.update(self.persona_natural.to_dict())
        elif hasattr(self, 'persona_juridica') and self.persona_juridica:
            data['tipo'] = 'JURIDICA'
            data.update(self.persona_juridica.to_dict())
        
        if include_cuentas:
            data['cuentas'] = [c.to_dict() for c in self.cuentas]
        
        return data


class PersonaNatural(db.Model):
    """Persona Natural - Cliente individual"""
    __tablename__ = 'persona_natural'
    
    id = db.Column(db.Integer, db.ForeignKey('persona.id'), primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    genero = db.Column(db.String(20))
    estado_civil = db.Column(db.String(20))
    ocupacion = db.Column(db.String(50))
    nacionalidad = db.Column(db.String(50), default='Ecuatoriana')
    direccion = db.Column(db.String(256))
    
    persona = db.relationship('Persona', backref=db.backref('persona_natural', uselist=False))
    
    def to_dict(self):
        return {
            'cedula': self.cedula,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'nombre_completo': f'{self.nombre} {self.apellido}',
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'genero': self.genero,
            'estado_civil': self.estado_civil,
            'ocupacion': self.ocupacion,
            'nacionalidad': self.nacionalidad,
            'direccion': self.direccion
        }


class PersonaJuridica(db.Model):
    """Persona Jurídica - Empresa"""
    __tablename__ = 'persona_juridica'
    
    id = db.Column(db.Integer, db.ForeignKey('persona.id'), primary_key=True)
    ruc = db.Column(db.String(13), unique=True, nullable=False)
    razon_social = db.Column(db.String(200), nullable=False)
    nombre_comercial = db.Column(db.String(200))
    fecha_constitucion = db.Column(db.Date, nullable=False)
    tipo_empresa = db.Column(db.String(50), nullable=False)
    representante_legal = db.Column(db.String(100))
    direccion = db.Column(db.String(256))
    
    persona = db.relationship('Persona', backref=db.backref('persona_juridica', uselist=False))
    
    def to_dict(self):
        return {
            'ruc': self.ruc,
            'razon_social': self.razon_social,
            'nombre_comercial': self.nombre_comercial,
            'fecha_constitucion': self.fecha_constitucion.isoformat() if self.fecha_constitucion else None,
            'tipo_empresa': self.tipo_empresa,
            'representante_legal': self.representante_legal,
            'direccion': self.direccion
        }
