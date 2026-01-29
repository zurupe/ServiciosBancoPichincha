"""
Modelo ProveedorServicio - Proveedores de servicios (ANT, CNT, SRI, etc.)
"""

from extensions import db


class ProveedorServicio(db.Model):
    """Proveedores: SRI, ANT, CNT, Claro, Empresa Eléctrica, etc."""
    __tablename__ = 'proveedor_servicio'
    
    id_proveedor = db.Column(db.Integer, primary_key=True)
    id_tipo = db.Column(db.Integer, db.ForeignKey('tipo_servicio.id_tipo'), nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(256))
    logo_url = db.Column(db.String(256))
    activo = db.Column(db.Boolean, default=True, nullable=False)
    requiere_referencia = db.Column(db.Boolean, default=True, nullable=False)
    formato_referencia = db.Column(db.String(100))
    
    # Relación con servicios
    servicios = db.relationship('Servicio', backref='proveedor', lazy='dynamic')
    
    def to_dict(self, include_tipo=False, include_servicios=False):
        """Serializar a diccionario"""
        data = {
            'id': self.id_proveedor,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'logo_url': self.logo_url,
            'activo': self.activo,
            'requiere_referencia': self.requiere_referencia,
            'formato_referencia': self.formato_referencia,
            'id_tipo': self.id_tipo
        }
        
        if include_tipo and self.tipo:
            data['tipo'] = {
                'codigo': self.tipo.codigo,
                'nombre': self.tipo.nombre
            }
        
        if include_servicios:
            data['servicios'] = [s.to_dict() for s in self.servicios.filter_by(activo=True)]
            data['cantidad_servicios'] = len(data['servicios'])
        
        return data
    
    def __repr__(self):
        return f'<ProveedorServicio {self.codigo}>'
