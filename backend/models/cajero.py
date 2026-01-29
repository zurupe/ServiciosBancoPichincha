"""Modelo Cajero - Cajeros automáticos"""

from extensions import db
from datetime import time


class Cajero(db.Model):
    """Cajero automático"""
    __tablename__ = 'cajero'
    
    id_cajero = db.Column(db.Integer, primary_key=True)
    latitud = db.Column(db.Numeric(10, 6), nullable=False)
    longitud = db.Column(db.Numeric(10, 6), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    saldo = db.Column(db.Numeric(12, 2), default=0)
    depositos = db.Column(db.Boolean, default=True)
    nombre = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(64), nullable=False)
    provincia = db.Column(db.String(64), nullable=False)
    direccion = db.Column(db.String(256), nullable=False)
    hora_apertura = db.Column(db.Time, default=time(6, 0))
    hora_cierre = db.Column(db.Time, default=time(22, 0))
    dias_operacion = db.Column(db.String(20), default='L-D')
    
    def to_dict(self):
        return {
            'id': self.id_cajero,
            'nombre': self.nombre,
            'ubicacion': {
                'latitud': float(self.latitud) if self.latitud else None,
                'longitud': float(self.longitud) if self.longitud else None,
                'ciudad': self.ciudad,
                'provincia': self.provincia,
                'direccion': self.direccion
            },
            'activo': self.activo,
            'saldo_disponible': float(self.saldo) if self.saldo else 0,
            'permite_depositos': self.depositos,
            'horario': {
                'apertura': self.hora_apertura.strftime('%H:%M') if self.hora_apertura else None,
                'cierre': self.hora_cierre.strftime('%H:%M') if self.hora_cierre else None,
                'dias': self.dias_operacion
            }
        }
