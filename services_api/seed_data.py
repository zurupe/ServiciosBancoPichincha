"""
Script para generar datos de prueba
Genera 30+ registros de pagos de servicios
"""

from app import create_app, db
from models.tipo_servicio import TipoServicio
from models.proveedor import ProveedorServicio
from models.servicio import Servicio
from models.pago import PagoServicio
from decimal import Decimal
import random
from datetime import datetime, timedelta


def generar_pagos_prueba(cantidad=35):
    """Genera pagos de prueba para todos los tipos de servicios"""
    
    # Referencias de ejemplo
    referencias = {
        'impuestos': ['P-' + str(i).zfill(6) for i in range(1001, 1012)] + 
                     ['RUC' + str(random.randint(1000000000, 9999999999)) for _ in range(5)],
        'matricula': ['PBM-' + str(random.randint(1000, 9999)) for _ in range(10)] +
                     ['ABC-' + str(random.randint(100, 999)) for _ in range(5)],
        'multas': [str(random.randint(1000000000, 1999999999)) for _ in range(10)] +
                  ['099' + str(random.randint(1000000, 9999999)) for _ in range(10)],
        'servicios': [str(random.randint(100000, 999999)) for _ in range(15)]
    }
    
    detalles = {
        'IMPUESTOS': 'Pago de impuestos',
        'MATRICULA': 'Pago matrícula/impuesto vehicular',
        'MULTAS': 'Pago de multa/factura',
        'SERVICIOS': 'Pago de servicio público'
    }
    
    pagos_creados = 0
    servicios = Servicio.query.filter_by(activo=True).all()
    
    if not servicios:
        print("No hay servicios en la base de datos. Ejecute primero el schema.sql")
        return 0
    
    for i in range(cantidad):
        servicio = random.choice(servicios)
        tipo_codigo = servicio.proveedor.tipo.codigo if servicio.proveedor and servicio.proveedor.tipo else 'SERVICIOS'
        
        # Seleccionar referencia según tipo
        if tipo_codigo == 'IMPUESTOS':
            referencia = random.choice(referencias['impuestos'])
        elif tipo_codigo == 'MATRICULA':
            referencia = random.choice(referencias['matricula'])
        elif tipo_codigo == 'MULTAS':
            referencia = random.choice(referencias['multas'])
        else:
            referencia = random.choice(referencias['servicios'])
        
        # Generar monto aleatorio
        monto_base = Decimal(str(round(random.uniform(15.00, 250.00), 2)))
        comision = servicio.comision or Decimal('0')
        monto_total = monto_base + comision
        
        # Fecha de pago en los últimos 90 días
        dias_atras = random.randint(0, 90)
        fecha_pago = datetime.now() - timedelta(days=dias_atras)
        
        pago = PagoServicio(
            id_servicio=servicio.id_servicio,
            id_cuenta=random.randint(1, 30) if random.random() > 0.3 else None,
            referencia_cliente=referencia,
            monto_base=monto_base,
            comision=comision,
            monto_total=monto_total,
            fecha_pago=fecha_pago,
            estado=PagoServicio.ESTADO_COMPLETADO,
            comprobante=PagoServicio.generar_comprobante(),
            detalle=f'{detalles.get(tipo_codigo, "Pago")} - {servicio.nombre}'
        )
        
        db.session.add(pago)
        pagos_creados += 1
    
    db.session.commit()
    return pagos_creados


def mostrar_estadisticas():
    """Muestra estadísticas de la base de datos"""
    print("\n" + "=" * 60)
    print("  ESTADÍSTICAS DE LA BASE DE DATOS")
    print("=" * 60)
    
    print(f"\n  Tipos de servicio: {TipoServicio.query.count()}")
    for tipo in TipoServicio.query.all():
        print(f"    - {tipo.nombre} ({tipo.codigo})")
    
    print(f"\n  Proveedores: {ProveedorServicio.query.count()}")
    
    print(f"\n  Servicios: {Servicio.query.count()}")
    
    print(f"\n  Pagos registrados: {PagoServicio.query.count()}")
    
    # Resumen de pagos por tipo
    print("\n  Resumen de pagos por tipo:")
    for tipo in TipoServicio.query.all():
        total = db.session.query(db.func.sum(PagoServicio.monto_total)).join(
            Servicio, PagoServicio.id_servicio == Servicio.id_servicio
        ).join(
            ProveedorServicio, Servicio.id_proveedor == ProveedorServicio.id_proveedor
        ).filter(
            ProveedorServicio.id_tipo == tipo.id_tipo
        ).scalar() or 0
        
        count = db.session.query(PagoServicio).join(
            Servicio, PagoServicio.id_servicio == Servicio.id_servicio
        ).join(
            ProveedorServicio, Servicio.id_proveedor == ProveedorServicio.id_proveedor
        ).filter(
            ProveedorServicio.id_tipo == tipo.id_tipo
        ).count()
        
        print(f"    - {tipo.nombre}: {count} pagos, ${total:,.2f} total")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 60)
        print("  GENERADOR DE DATOS DE PRUEBA - API Servicios")
        print("=" * 60)
        
        # Verificar si ya hay datos
        pagos_existentes = PagoServicio.query.count()
        
        if pagos_existentes > 0:
            print(f"\n  Ya existen {pagos_existentes} pagos en la base de datos.")
            respuesta = input("  ¿Desea agregar más datos de prueba? (s/n): ")
            if respuesta.lower() != 's':
                mostrar_estadisticas()
                exit()
        
        print("\n  Generando datos de prueba...")
        cantidad = generar_pagos_prueba(35)
        print(f"  ✓ Se crearon {cantidad} pagos de prueba")
        
        mostrar_estadisticas()
