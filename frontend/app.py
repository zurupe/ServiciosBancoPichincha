"""
Frontend - Banco Pichincha
Interfaz web para banca en línea
Puerto: 5000
"""

from flask import Flask, render_template, redirect, url_for, flash, session, request
import requests
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)


def api_request(method, endpoint, data=None, api='backend'):
    """Realiza peticiones a las APIs"""
    base_url = Config.BACKEND_URL if api == 'backend' else Config.SERVICES_API_URL
    url = f"{base_url}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=10)
        
        return response.json()
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'No se pudo conectar con el servidor'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ============== RUTAS PÚBLICAS ==============

@app.route('/')
def index():
    """Página principal"""
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuario"""
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        result = api_request('POST', '/api/auth/login', {
            'usuario': usuario,
            'password': password
        })
        
        if result.get('success'):
            session['usuario'] = result['data']['usuario']
            flash('Bienvenido', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result.get('error', 'Error de login'), 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('index'))


# ============== RUTAS PROTEGIDAS ==============

@app.route('/dashboard')
def dashboard():
    """Panel principal del usuario"""
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    usuario = session['usuario']
    
    # Obtener cuentas del usuario
    cuentas = api_request('GET', f'/api/cuentas?persona={usuario["id"]}')
    
    return render_template('dashboard.html', 
        usuario=usuario,
        cuentas=cuentas.get('data', [])
    )


@app.route('/cuentas')
def cuentas():
    """Gestión de cuentas"""
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    usuario = session['usuario']
    result = api_request('GET', f'/api/cuentas?persona={usuario["id"]}')
    
    return render_template('cuentas.html',
        usuario=usuario,
        cuentas=result.get('data', [])
    )


@app.route('/cuenta/<int:id>')
def detalle_cuenta(id):
    """Detalle de una cuenta"""
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    cuenta = api_request('GET', f'/api/cuentas/{id}?tarjetas=true')
    transacciones = api_request('GET', f'/api/transacciones?cuenta={id}&limite=20')
    
    return render_template('cuenta_detalle.html',
        usuario=session['usuario'],
        cuenta=cuenta.get('data'),
        transacciones=transacciones.get('data', [])
    )


@app.route('/transferir', methods=['GET', 'POST'])
def transferir():
    """Realizar transferencia"""
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    usuario = session['usuario']
    cuentas = api_request('GET', f'/api/cuentas?persona={usuario["id"]}')
    
    if request.method == 'POST':
        result = api_request('POST', '/api/transacciones/transferir', {
            'cuenta_origen': int(request.form['cuenta_origen']),
            'cuenta_destino': int(request.form['cuenta_destino']),
            'monto': float(request.form['monto']),
            'descripcion': request.form.get('descripcion', '')
        })
        
        if result.get('success'):
            flash('Transferencia realizada exitosamente', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result.get('error', 'Error en transferencia'), 'danger')
    
    return render_template('transferir.html',
        usuario=usuario,
        cuentas=cuentas.get('data', [])
    )


# ============== PAGO DE SERVICIOS ==============

@app.route('/servicios')
def servicios():
    """Menú de pago de servicios"""
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    tipos = api_request('GET', '/api/v1/tipos-servicio', api='services')
    
    return render_template('servicios.html',
        usuario=session['usuario'],
        tipos=tipos.get('data', [])
    )


@app.route('/servicios/<categoria>')
def servicios_categoria(categoria):
    """Servicios por categoría"""
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    proveedores = api_request('GET', f'/api/v1/proveedores/categoria/{categoria}', api='services')
    cuentas = api_request('GET', f'/api/cuentas?persona={session["usuario"]["id"]}')
    
    return render_template('servicios_categoria.html',
        usuario=session['usuario'],
        categoria=categoria,
        proveedores=proveedores.get('data', []),
        cuentas=cuentas.get('data', [])
    )


@app.route('/pagar-servicio', methods=['POST'])
def pagar_servicio():
    """Procesa pago de servicio"""
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    result = api_request('POST', '/api/v1/pagos', {
        'codigo_servicio': request.form['codigo_servicio'],
        'referencia': request.form['referencia'],
        'monto': float(request.form['monto']),
        'id_cuenta': int(request.form['id_cuenta'])
    }, api='services')
    
    if result.get('success'):
        flash(f'Pago realizado. Comprobante: {result["data"]["comprobante"]}', 'success')
    else:
        flash(result.get('error', 'Error en el pago'), 'danger')
    
    return redirect(url_for('servicios'))


# ============== RETIROS ==============

@app.route('/retiro-sin-tarjeta', methods=['GET', 'POST'])
def retiro_sin_tarjeta():
    """Generar código de retiro sin tarjeta"""
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    usuario = session['usuario']
    cuentas = api_request('GET', f'/api/cuentas?persona={usuario["id"]}')
    
    if request.method == 'POST':
        result = api_request('POST', '/api/retiros/sin-tarjeta/generar', {
            'id_cuenta': int(request.form['id_cuenta']),
            'monto': float(request.form['monto'])
        })
        
        if result.get('success'):
            return render_template('retiro_codigo.html',
                usuario=usuario,
                codigo=result['data']
            )
        else:
            flash(result.get('error', 'Error'), 'danger')
    
    return render_template('retiro_sin_tarjeta.html',
        usuario=usuario,
        cuentas=cuentas.get('data', [])
    )


# ============== ERRORES ==============

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', codigo=404, mensaje='Página no encontrada'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', codigo=500, mensaje='Error del servidor'), 500


if __name__ == '__main__':
    print("=" * 60)
    print("  Frontend Banco Pichincha")
    print("  Puerto: 5000")
    print("  http://localhost:5000/")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
