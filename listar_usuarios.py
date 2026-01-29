import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host='192.168.100.12',
        port='5432',
        database='banco_pichincha',
        user='casaos',
        password='casaos',
        connect_timeout=5
    )
    cur = conn.cursor()
    
    # Debug info
    print("\n--- conteos ---")
    cur.execute("SELECT count(*) FROM persona")
    print(f"Total personas: {cur.fetchone()[0]}")
    cur.execute("SELECT count(*) FROM persona_natural")
    print(f"Total naturales: {cur.fetchone()[0]}")
    
    cur.execute("""
        SELECT pn.nombre, pn.apellido, pn.cedula, p.correo 
        FROM persona p
        JOIN persona_natural pn ON p.id = pn.id
        ORDER BY p.id
    """)
    
    print(f"\n{'NOMBRE':<15} {'APELLIDO':<15} {'CEDULA':<15} {'CORREO':<30}")
    print("-" * 80)
    
    for row in cur.fetchall():
        print(f"{row[0]:<15} {row[1]:<15} {row[2]:<15} {row[3]:<30}")
        
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
