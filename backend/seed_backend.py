"""
Script para generar datos de prueba del Backend
Genera Personas, Cuentas y Tarjetas
"""

from app import create_app
from extensions import db
from models.persona import Persona, PersonaNatural
from models.cuenta import Cuenta, CuentaAhorros, CuentaCorriente
from models.tarjeta import Tarjeta, TarjetaDebito
from datetime import date
from werkzeug.security import generate_password_hash
import random

def generar_datos_backend():
    print("Generando datos del Backend...")
    
    # 1. Crear Personas
    nombres = ["JUAN", "MARIA", "CARLOS", "ANA", "LUIS", "ELENA", "PEDRO", "SOFIA", "DIEGO", "LAURA"]
    apellidos = ["PEREZ", "GARCIA", "LOPEZ", "TORRES", "RUIZ", "DIAZ", "MERA", "FLORES", "ROJAS", "VEGA"]
    
    personas = []
    for i in range(10):
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        cedula = f"17{str(random.randint(10000000, 99999999))}"
        correo = f"{nombre.lower()}.{apellido.lower()}{i}@example.com"
        celular = f"09{str(random.randint(10000000, 99999999))}"
        
        # 1. Crear Persona base
        persona_base = Persona(
            celular=celular,
            correo=correo,
            patrimonio=0,
            password_hash=generate_password_hash("1234")
        )
        db.session.add(persona_base)
        db.session.flush() # Obtener ID
        
        # 2. Crear Persona Natural vinculada
        persona_natural = PersonaNatural(
            id=persona_base.id,
            cedula=cedula,
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=date(1980 + i, 1, 1),
            genero='M' if i % 2 == 0 else 'F',
            estado_civil='SOLTERO',
            direccion='Av. Siempre Viva 123',
            nacionalidad='Ecuatoriana'
        )
        db.session.add(persona_natural)
        personas.append(persona_natural)
    
    db.session.flush()
    print(f"✓ {len(personas)} Personas creadas (Pass: 1234)")
    
    # 2. Crear Cuentas
    cuentas = []
    for pn in personas:
        # 1. Crear Cuenta base (Ahorros)
        cuenta_base_ah = Cuenta(
            id_persona=pn.id,
            numero_cuenta=Cuenta.generar_numero_cuenta(),
            tipo_cuenta='AHORROS',
            saldo_actual=random.uniform(100, 5000)
        )
        db.session.add(cuenta_base_ah)
        db.session.flush()
        
        # 2. Crear detalle Ahorros
        cuenta_ahorros = CuentaAhorros(
            id_cuenta=cuenta_base_ah.id_cuenta,
            tasa_interes=1.5
        )
        db.session.add(cuenta_ahorros)
        cuentas.append(cuenta_base_ah)
        
        # 30% tiene Corriente
        if random.random() > 0.7:
            # 1. Crear Cuenta base (Corriente)
            cuenta_base_cc = Cuenta(
                id_persona=pn.id,
                numero_cuenta=Cuenta.generar_numero_cuenta(),
                tipo_cuenta='CORRIENTE',
                saldo_actual=random.uniform(500, 10000)
            )
            db.session.add(cuenta_base_cc)
            db.session.flush()
            
            # 2. Crear detalle Corriente
            cuenta_cc = CuentaCorriente(
                id_cuenta=cuenta_base_cc.id_cuenta,
                cupo_sobregiro=1000,
                limite_cheques=50
            )
            db.session.add(cuenta_cc)
            cuentas.append(cuenta_base_cc)
            
    db.session.flush()
    print(f"✓ {len(cuentas)} Cuentas creadas")
    
    # 3. Crear Tarjetas
    tarjetas = []
    for cuenta in cuentas:
        # Obtener nombre del propietario (buscar persona_natural asociada)
        # Nota: En este script sabemos que el propietario es pn (PersonaNatural)
        # pero la relación en modelo es cuenta.propietario -> Persona
        # Accedemos a la persona natural a través de la relación inversa o consulta directa
        try:
             # Recargar relación
            persona_nat = PersonaNatural.query.get(cuenta.id_persona)
            nombre_titular = f"{persona_nat.nombre} {persona_nat.apellido}"
        except:
            nombre_titular = "CLIENTE BANCO"

        cvv = Tarjeta.generar_cvv()
        tarjeta = Tarjeta(
            id_cuenta=cuenta.id_cuenta,
            numero_tarjeta=Tarjeta.generar_numero_tarjeta(),
            nombre_titular=nombre_titular,
            fecha_expiracion=date.today().replace(year=date.today().year + 5),
            tipo_tarjeta='DEBITO',
            cvv_hash=cvv
        )
        tarjeta.set_pin("1234")
        db.session.add(tarjeta)
        db.session.flush()
        
        debito = TarjetaDebito(
            id_tarjeta=tarjeta.id_tarjeta,
            limite_diario_retiro=500,
            limite_diario_compra=2000
        )
        db.session.add(debito)
        tarjetas.append(tarjeta)

    db.session.commit()
    print(f"✓ {len(tarjetas)} Tarjetas creadas (PIN: 1234)")
    print("Datos del backend generados exitosamente.")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        generar_datos_backend()
