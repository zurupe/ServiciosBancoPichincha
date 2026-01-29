"""
Modelo PagoServicio - Registro de pagos realizados
"""

from extensions import db
from datetime import datetime
import uuid


class PagoServicio(db.Model):
    """Registro de pagos de servicios realizados"""
    __tablename__ = 'pago_servicio'
    
    id_pago = db.Column(db.Integer, primary_key=True)
    id_servicio = db.Column(db.Integer, db.ForeignKey('servicio.id_servicio'), nullable=False)
    id_cuenta = db.Column(db.Integer)  # FK a cuenta bancaria (opcional para API externa)
    id_transaccion = db.Column(db.Integer)  # FK a transacción bancaria
    referencia_cliente = db.Column(db.String(50), nullable=False)
    monto_base = db.Column(db.Numeric(12, 2), nullable=False)
    comision = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    monto_total = db.Column(db.Numeric(12, 2), nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    estado = db.Column(db.String(20), default='COMPLETADO', nullable=False)
    comprobante = db.Column(db.String(50), nullable=False)
    detalle = db.Column(db.String(256))
    
    # Estados posibles
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_PROCESANDO = 'PROCESANDO'
    ESTADO_COMPLETADO = 'COMPLETADO'
    ESTADO_FALLIDO = 'FALLIDO'
    ESTADO_REVERSADO = 'REVERSADO'
    
    @staticmethod
    def generar_comprobante():
        """Genera un número de comprobante único"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f'BP{timestamp}{unique_id}'
    
    def to_dict(self, include_servicio=False):
        """Serializar a diccionario"""
        data = {
            'id': self.id_pago,
            'referencia_cliente': self.referencia_cliente,
            'monto_base': float(self.monto_base),
            'comision': float(self.comision),
            'monto_total': float(self.monto_total),
            'fecha_pago': self.fecha_pago.isoformat() if self.fecha_pago else None,
            'estado': self.estado,
            'comprobante': self.comprobante,
            'detalle': self.detalle,
            'id_servicio': self.id_servicio,
            'id_cuenta': self.id_cuenta,
            'id_transaccion': self.id_transaccion
        }
        
        if include_servicio and self.servicio:
            data['servicio'] = {
                'codigo': self.servicio.codigo,
                'nombre': self.servicio.nombre
            }
            if self.servicio.proveedor:
                data['proveedor'] = {
                    'codigo': self.servicio.proveedor.codigo,
                    'nombre': self.servicio.proveedor.nombre
                }
                if self.servicio.proveedor.tipo:
                    data['tipo_servicio'] = {
                        'codigo': self.servicio.proveedor.tipo.codigo,
                        'nombre': self.servicio.proveedor.tipo.nombre
                    }
        
        return data
    
    def __repr__(self):
        return f'<PagoServicio {self.comprobante}>'
