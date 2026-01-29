"""
Script para generar datos adicionales (Cajeros, Empresas, VIPs)
"""
from app import create_app
from extensions import db
from models.cajero import Cajero
from models.persona import Persona, PersonaJuridica, PersonaNatural
from models.cuenta import Cuenta, CuentaCorriente
from models.tarjeta import Tarjeta, TarjetaCredito
from models.transaccion import Transaccion, RetiroSinTarjeta
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash
import random

def generar_datos_extra():
    # 1. Cajeros Automáticos
    cajeros_data = [
        {"nombre": "ATM CCI Norte", "ciudad": "Quito", "direccion": "Av. Amazonas y ONU", "lat": -0.1632, "lon": -78.4851, "saldo": 25000},
        {"nombre": "ATM Centro Histórico", "ciudad": "Quito", "direccion": "Plaza Grande", "lat": -0.2205, "lon": -78.5123, "saldo": 15000},
        {"nombre": "ATM Mall del Sol", "ciudad": "Guayaquil", "direccion": "Av. Constitución", "lat": -2.1534, "lon": -79.8921, "saldo": 40000},
        {"nombre": "ATM Parque Calderón", "ciudad": "Cuenca", "direccion": "Bolívar y Benigno Malo", "lat": -2.8974, "lon": -79.0045, "saldo": 20000},
    ]
    
    for c in cajeros_data:
        cajero = Cajero(
            nombre=c['nombre'], ciudad=c['ciudad'], provincia="Pichincha" if c['ciudad']=="Quito" else "Guayas" if c['ciudad']=="Guayaquil" else "Azuay",
            direccion=c['direccion'], latitud=c['lat'], longitud=c['lon'], saldo=c['saldo']
        )
        db.session.add(cajero)
    print("✓ Cajeros creados")

    # 2. Empresas (Persona Jurídica)
    empresas_data = [
        {"ruc": "1790012345001", "razon": "SUPERMERCADOS LA FAVORITA C.A.", "nombre": "Supermaxi", "tipo": "S.A.", "dir": "Av. Eloy Alfaro, Quito"},
        {"ruc": "0992345678001", "razon": "CORPORACION EL ROSADO S.A.", "nombre": "Mi Comisariato", "tipo": "S.A.", "dir": "9 de Octubre, Guayaquil"},
        {"ruc": "1791234567001", "razon": "TECNOLOGIA Y SISTEMAS S.A.S", "nombre": "TecnoSyS", "tipo": "S.A.S", "dir": "Av. 6 de Diciembre, Quito"}
    ]
    
    empresas_ids = []
    
    for num, e in enumerate(empresas_data):
        # Persona Base
        pb = Persona(
            celular=f"099000000{num}",
            correo=f"contacto{num}@empresa.com",
            patrimonio=500000,
            password_hash=generate_password_hash("admin123")
        )
        db.session.add(pb)
        db.session.flush()
        
        # Persona Jurídica
        pj = PersonaJuridica(
            id=pb.id,
            ruc=e['ruc'],
            razon_social=e['razon'],
            nombre_comercial=e['nombre'],
            fecha_constitucion=date(1990, 1, 1),
            tipo_empresa=e['tipo'],
            representante_legal="Gerente General",
            direccion=e['dir']
        )
        db.session.add(pj)
        empresas_ids.append(pb.id)
        
        # Cuenta Corriente Corporativa
        cuenta_base = Cuenta(
            id_persona=pb.id,
            numero_cuenta=f"2100{num}89900",
            tipo_cuenta='CORRIENTE',
            saldo_actual=random.uniform(50000, 200000)
        )
        db.session.add(cuenta_base)
        db.session.flush()
        
        cc = CuentaCorriente(
            id_cuenta=cuenta_base.id_cuenta,
            sobregiro_autorizado=50000,
            limite_cheques=100
        )
        db.session.add(cc)
        
    print("✓ Empresas y Cuentas Corporativas creadas")

    # 3. Tarjetas de Crédito Premium (Asignar a primeros usuarios naturales)
    personas_naturales = PersonaNatural.query.limit(2).all()
    if personas_naturales:
        tarjetas_data = [
            {"tipo": "Visa Infinite", "cupo": 15000, "pin": "9999"},
            {"tipo": "Mastercard Black", "cupo": 20000, "pin": "8888"}
        ]
        
        for i, pn in enumerate(personas_naturales):
            # Necesitamos una cuenta del usuario para asociar la tarjeta (aunque sea crédito, se linkea a cuenta principal en este modelo simplificado)
            cuenta = Cuenta.query.filter_by(id_persona=pn.id).first()
            if not cuenta: continue
            
            td = tarjetas_data[i % len(tarjetas_data)]
            t_base = Tarjeta(
                id_cuenta=cuenta.id_cuenta,
                numero_tarjeta=Tarjeta.generar_numero_tarjeta(),
                nombre_titular=f"{pn.nombre} {pn.apellido}",
                fecha_expiracion=date.today().replace(year=date.today().year + 4),
                tipo_tarjeta='CREDITO',
                cvv_hash=Tarjeta.generar_cvv()
            )
            t_base.set_pin(td['pin'])
            db.session.add(t_base)
            db.session.flush()
            
            tc = TarjetaCredito(
                id_tarjeta=t_base.id_tarjeta,
                cupo_total=td['cupo'],
                cupo_disponible=td['cupo'],
                fecha_corte=15,
                fecha_pago=30
            )
            db.session.add(tc)
            
    print("✓ Tarjetas Premium creadas")

    # 4. Transacciones Simuladas
    if empresas_ids and personas_naturales:
        cuenta_empresa = Cuenta.query.filter_by(id_persona=empresas_ids[0]).first()
        cuenta_persona = Cuenta.query.filter_by(id_persona=personas_naturales[0].id).first()
        
        if cuenta_empresa and cuenta_persona:
            t1 = Transaccion(
                id_cuenta_origen=cuenta_empresa.id_cuenta,
                id_cuenta_destino=cuenta_persona.id_cuenta,
                tipo_transaccion='TRANSFERENCIA',
                monto=1200.50,
                descripcion='Pago Nómina Enero',
                estado='COMPLETADA',
                referencia='NOM-001'
            )
            db.session.add(t1)
            
            t2 = Transaccion(
                id_cuenta_origen=None,
                id_cuenta_destino=cuenta_empresa.id_cuenta, # Deposito
                tipo_transaccion='DEPOSITO',
                monto=5000.00,
                descripcion='Depósito Ventas Día',
                estado='COMPLETADA',
                referencia='DEP-999'
            )
            db.session.add(t2)
            
    print("✓ Transacciones simuladas")
            
    db.session.commit()
    print("Datos extra generados exitosamente.")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        generar_datos_extra()
