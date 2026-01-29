"""
Modelo Servicio - Servicios específicos que se pueden pagar
"""

from extensions import db


class Servicio(db.Model):
    """Servicios específicos: Pago de luz, agua, impuesto predial, etc."""
    __tablename__ = 'servicio'
    
    id_servicio = db.Column(db.Integer, primary_key=True)
    id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedor_servicio.id_proveedor'), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(256))
    monto_fijo = db.Column(db.Numeric(10, 2))
    permite_monto_variable = db.Column(db.Boolean, default=True, nullable=False)
    monto_minimo = db.Column(db.Numeric(10, 2))
    monto_maximo = db.Column(db.Numeric(10, 2))
    comision = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relación con pagos
    pagos = db.relationship('PagoServicio', backref='servicio', lazy='dynamic')
    
    def to_dict(self, include_proveedor=False):
        """Serializar a diccionario"""
        data = {
            'id': self.id_servicio,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'monto_fijo': float(self.monto_fijo) if self.monto_fijo else None,
            'permite_monto_variable': self.permite_monto_variable,
            'monto_minimo': float(self.monto_minimo) if self.monto_minimo else None,
            'monto_maximo': float(self.monto_maximo) if self.monto_maximo else None,
            'comision': float(self.comision) if self.comision else 0,
            'activo': self.activo,
            'id_proveedor': self.id_proveedor
        }
        
        if include_proveedor and self.proveedor:
            data['proveedor'] = {
                'codigo': self.proveedor.codigo,
                'nombre': self.proveedor.nombre,
                'requiere_referencia': self.proveedor.requiere_referencia,
                'formato_referencia': self.proveedor.formato_referencia
            }
            if self.proveedor.tipo:
                data['tipo'] = {
                    'codigo': self.proveedor.tipo.codigo,
                    'nombre': self.proveedor.tipo.nombre
                }
        
        return data
    
    def calcular_total(self, monto_base):
        """Calcular monto total incluyendo comisión"""
        return float(monto_base) + float(self.comision or 0)
    
    def __repr__(self):
        return f'<Servicio {self.codigo}>'
