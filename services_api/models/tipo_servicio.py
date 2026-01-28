"""
Modelo TipoServicio - Categorías de servicios
"""

from app import db


class TipoServicio(db.Model):
    """Categorías de servicios: IMPUESTOS, MATRICULA, MULTAS, SERVICIOS"""
    __tablename__ = 'tipo_servicio'
    
    id_tipo = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(256))
    icono = db.Column(db.String(50))
    activo = db.Column(db.Boolean, default=True, nullable=False)
    orden = db.Column(db.Integer, default=0, nullable=False)
    
    # Relación con proveedores
    proveedores = db.relationship('ProveedorServicio', backref='tipo', lazy='dynamic')
    
    def to_dict(self):
        """Serializar a diccionario"""
        return {
            'id': self.id_tipo,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'icono': self.icono,
            'activo': self.activo,
            'orden': self.orden,
            'cantidad_proveedores': self.proveedores.count()
        }
    
    def __repr__(self):
        return f'<TipoServicio {self.codigo}>'
