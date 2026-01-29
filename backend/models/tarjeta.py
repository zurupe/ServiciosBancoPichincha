"""Modelo Tarjeta - Tarjetas de débito y crédito"""

from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import random
import string


class Tarjeta(db.Model):
    """Tarjeta bancaria base"""
    __tablename__ = 'tarjeta'
    
    id_tarjeta = db.Column(db.Integer, primary_key=True)
    id_cuenta = db.Column(db.Integer, db.ForeignKey('cuenta.id_cuenta'), nullable=False)
    numero_tarjeta = db.Column(db.String(16), unique=True, nullable=False)
    nombre_titular = db.Column(db.String(100), nullable=False)
    fecha_emision = db.Column(db.Date, default=date.today)
    fecha_expiracion = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), default='ACTIVA')
    tipo_tarjeta = db.Column(db.String(20), nullable=False)
    pin_hash = db.Column(db.String(256), nullable=False)
    cvv_hash = db.Column(db.String(256), nullable=False)
    pais_emision = db.Column(db.String(50), default='Ecuador')
    
    @staticmethod
    def generar_numero_tarjeta():
        """Genera número de tarjeta de 16 dígitos"""
        prefix = '4551'  # Visa Banco Pichincha
        numero = ''.join(random.choices(string.digits, k=12))
        return f'{prefix}{numero}'
    
    @staticmethod
    def generar_cvv():
        return ''.join(random.choices(string.digits, k=3))
    
    def set_pin(self, pin):
        self.pin_hash = generate_password_hash(str(pin))
    
    def check_pin(self, pin):
        return check_password_hash(self.pin_hash, str(pin))
    
    def to_dict(self, ocultar_numero=True):
        numero = self.numero_tarjeta
        if ocultar_numero and numero:
            numero = f'**** **** **** {numero[-4:]}'
        
        return {
            'id': self.id_tarjeta,
            'numero_tarjeta': numero,
            'nombre_titular': self.nombre_titular,
            'fecha_expiracion': self.fecha_expiracion.strftime('%m/%y') if self.fecha_expiracion else None,
            'estado': self.estado,
            'tipo_tarjeta': self.tipo_tarjeta,
            'id_cuenta': self.id_cuenta
        }


class TarjetaDebito(db.Model):
    """Tarjeta de Débito"""
    __tablename__ = 'tarjeta_debito'
    
    id_tarjeta = db.Column(db.Integer, db.ForeignKey('tarjeta.id_tarjeta'), primary_key=True)
    limite_diario_retiro = db.Column(db.Numeric(10, 2), default=500)
    limite_diario_compra = db.Column(db.Numeric(10, 2), default=2000)
    
    tarjeta = db.relationship('Tarjeta', backref=db.backref('debito', uselist=False))


class TarjetaCredito(db.Model):
    """Tarjeta de Crédito"""
    __tablename__ = 'tarjeta_credito'
    
    id_tarjeta = db.Column(db.Integer, db.ForeignKey('tarjeta.id_tarjeta'), primary_key=True)
    cupo_total = db.Column(db.Numeric(12, 2), nullable=False)
    cupo_disponible = db.Column(db.Numeric(12, 2), nullable=False)
    fecha_corte = db.Column(db.Integer, default=15)
    fecha_pago = db.Column(db.Integer, default=25)
    tasa_interes = db.Column(db.Numeric(5, 4), default=0.1650)
    saldo_actual = db.Column(db.Numeric(12, 2), default=0)
    
    tarjeta = db.relationship('Tarjeta', backref=db.backref('credito', uselist=False))
