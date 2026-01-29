"""Modelo Cuenta - Cuentas bancarias"""

from app import db
from datetime import datetime
import random
import string


class Cuenta(db.Model):
    """Cuenta bancaria"""
    __tablename__ = 'cuenta'
    
    id_cuenta = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id'), nullable=False)
    numero_cuenta = db.Column(db.String(20), unique=True, nullable=False)
    tipo_cuenta = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(20), default='ACTIVA')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    saldo_actual = db.Column(db.Numeric(18, 2), default=0)
    comision_mensual = db.Column(db.Numeric(10, 2), default=0)
    limite_diario = db.Column(db.Numeric(12, 2), default=5000)
    
    # Relaciones
    tarjetas = db.relationship('Tarjeta', backref='cuenta', lazy='dynamic')
    transacciones_origen = db.relationship('Transaccion', 
        foreign_keys='Transaccion.id_cuenta_origen', backref='cuenta_origen', lazy='dynamic')
    transacciones_destino = db.relationship('Transaccion',
        foreign_keys='Transaccion.id_cuenta_destino', backref='cuenta_destino', lazy='dynamic')
    
    @staticmethod
    def generar_numero_cuenta():
        """Genera número de cuenta único"""
        prefix = '22'  # Código Banco Pichincha
        numero = ''.join(random.choices(string.digits, k=8))
        return f'{prefix}{numero}'
    
    def to_dict(self, include_tarjetas=False):
        data = {
            'id': self.id_cuenta,
            'numero_cuenta': self.numero_cuenta,
            'tipo_cuenta': self.tipo_cuenta,
            'estado': self.estado,
            'saldo_actual': float(self.saldo_actual) if self.saldo_actual else 0,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'limite_diario': float(self.limite_diario) if self.limite_diario else 5000,
            'id_persona': self.id_persona
        }
        
        if include_tarjetas:
            data['tarjetas'] = [t.to_dict() for t in self.tarjetas]
        
        return data


class CuentaAhorros(db.Model):
    """Cuenta de Ahorros"""
    __tablename__ = 'cuenta_ahorros'
    
    id_cuenta = db.Column(db.Integer, db.ForeignKey('cuenta.id_cuenta'), primary_key=True)
    tipo_ahorro = db.Column(db.String(50), default='BASICA')
    tasa_interes = db.Column(db.Numeric(5, 4), default=0.0100)
    minimo_mantener = db.Column(db.Numeric(12, 2), default=0)
    comision_mantenimiento = db.Column(db.Numeric(10, 2), default=0)
    
    cuenta = db.relationship('Cuenta', backref=db.backref('ahorros', uselist=False))


class CuentaCorriente(db.Model):
    """Cuenta Corriente"""
    __tablename__ = 'cuenta_corriente'
    
    id_cuenta = db.Column(db.Integer, db.ForeignKey('cuenta.id_cuenta'), primary_key=True)
    sobregiro_autorizado = db.Column(db.Numeric(12, 2), default=0)
    limite_cheques = db.Column(db.Integer, default=50)
    costo_chequera = db.Column(db.Numeric(10, 2), default=15.00)
    
    cuenta = db.relationship('Cuenta', backref=db.backref('corriente', uselist=False))
