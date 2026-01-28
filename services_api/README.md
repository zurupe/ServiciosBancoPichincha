# API de Servicios - Banco Pichincha

Microservicio independiente para pago de servicios públicos, impuestos, matrículas y multas.

## Características

- ✅ API REST completa para pago de servicios
- ✅ Consulta de deudas (simulada)
- ✅ Procesamiento de pagos con comprobantes
- ✅ Historial de transacciones
- ✅ Independiente y reutilizable por otros proyectos

## Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
copy .env.example .env
# Editar .env con los datos de su PostgreSQL

# 4. Crear base de datos
# Ejecutar database/schema.sql en PostgreSQL

# 5. Ejecutar API
python app.py
```

## Endpoints

### Tipos de Servicio
- `GET /api/v1/tipos-servicio` - Lista categorías

### Proveedores
- `GET /api/v1/proveedores` - Lista proveedores
- `GET /api/v1/proveedores/categoria/{categoria}` - Por categoría

### Servicios
- `GET /api/v1/servicios` - Lista servicios
- `POST /api/v1/servicios/consultar` - Consulta deuda

### Pagos
- `GET /api/v1/pagos` - Historial
- `POST /api/v1/pagos` - Procesar pago

### Impuestos
- `POST /api/v1/impuestos/predial` - Pagar predial
- `POST /api/v1/impuestos/municipal` - Pagar patente

### Matrícula
- `POST /api/v1/matricula/vehicular` - Pagar matrícula
- `POST /api/v1/matricula/consultar` - Consultar

### Multas
- `POST /api/v1/multas/ant` - Pagar multa ANT
- `POST /api/v1/multas/cnt` - Pagar CNT
- `POST /api/v1/multas/claro` - Pagar Claro

### Servicios Públicos
- `POST /api/v1/servicios-publicos/luz` - Pagar luz
- `POST /api/v1/servicios-publicos/agua` - Pagar agua
- `POST /api/v1/servicios-publicos/telefono` - Pagar teléfono
- `POST /api/v1/servicios-publicos/internet` - Pagar internet

## Ejemplo de Uso

```bash
# Consultar tipos de servicio
curl http://localhost:5002/api/v1/tipos-servicio

# Pagar luz
curl -X POST http://localhost:5002/api/v1/servicios-publicos/luz \
  -H "Content-Type: application/json" \
  -d '{"numero_suministro": "123456", "monto": 45.50}'
```

## Puerto

Esta API corre en el **puerto 5002** por defecto.
