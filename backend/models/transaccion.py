"""Modelo Transacción - Registro de movimientos"""

from extensions import db
from datetime import datetime
import uuid


class Transaccion(db.Model):
    """Transacción bancaria"""
    __tablename__ = 'transacciones'
    
    id_transaccion = db.Column(db.Integer, primary_key=True)
    id_cuenta_origen = db.Column(db.Integer, db.ForeignKey('cuenta.id_cuenta'))
    id_cuenta_destino = db.Column(db.Integer, db.ForeignKey('cuenta.id_cuenta'))
    id_tarjeta = db.Column(db.Integer, db.ForeignKey('tarjeta.id_tarjeta'))
    id_cajero = db.Column(db.Integer, db.ForeignKey('cajero.id_cajero'))
    tipo_transaccion = db.Column(db.String(50), nullable=False)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.String(256))
    estado = db.Column(db.String(20), default='COMPLETADA')
    referencia = db.Column(db.String(50))
    
    # Tipos de transacción
    TIPO_DEPOSITO = 'DEPOSITO'
    TIPO_RETIRO = 'RETIRO'
    TIPO_TRANSFERENCIA = 'TRANSFERENCIA'
    TIPO_PAGO_SERVICIO = 'PAGO_SERVICIO'
    TIPO_CONSUMO = 'CONSUMO'
    
    @staticmethod
    def generar_referencia():
        return f'TRX{datetime.now().strftime("%Y%m%d%H%M%S")}{str(uuid.uuid4())[:6].upper()}'
    
    def to_dict(self):
        return {
            'id': self.id_transaccion,
            'tipo': self.tipo_transaccion,
            'monto': float(self.monto),
            'fecha_hora': self.fecha_hora.isoformat() if self.fecha_hora else None,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'referencia': self.referencia,
            'id_cuenta_origen': self.id_cuenta_origen,
            'id_cuenta_destino': self.id_cuenta_destino,
            'id_tarjeta': self.id_tarjeta,
            'id_cajero': self.id_cajero
        }


class RetiroSinTarjeta(db.Model):
    """Retiro sin tarjeta - Código temporal"""
    __tablename__ = 'retiro_sin_tarjeta'
    
    id_retiro = db.Column(db.Integer, primary_key=True)
    id_cuenta = db.Column(db.Integer, db.ForeignKey('cuenta.id_cuenta'), nullable=False)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_expiracion = db.Column(db.DateTime, nullable=False)
    fecha_uso = db.Column(db.DateTime)
    estado = db.Column(db.String(20), default='PENDIENTE')
    id_cajero_uso = db.Column(db.Integer, db.ForeignKey('cajero.id_cajero'))
    
    cuenta = db.relationship('Cuenta', backref='retiros_sin_tarjeta')
    
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_USADO = 'USADO'
    ESTADO_EXPIRADO = 'EXPIRADO'
    ESTADO_CANCELADO = 'CANCELADO'
    
    @staticmethod
    def generar_codigo():
        """Genera código de 6 dígitos"""
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    def to_dict(self):
        return {
            'id': self.id_retiro,
            'codigo': self.codigo,
            'monto': float(self.monto),
            'fecha_generacion': self.fecha_generacion.isoformat() if self.fecha_generacion else None,
            'fecha_expiracion': self.fecha_expiracion.isoformat() if self.fecha_expiracion else None,
            'estado': self.estado,
            'id_cuenta': self.id_cuenta
        }
