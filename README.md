# Banco Pichincha - Sistema Bancario Integrado

Sistema bancario completo con arquitectura de microservicios.

## Arquitectura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│   PostgreSQL    │
│   Puerto 5000   │     │   Puerto 5001   │     │                 │
└────────┬────────┘     └─────────────────┘     └─────────────────┘
         │
         │              ┌─────────────────┐
         └─────────────▶│  API Servicios  │
                        │   Puerto 5002   │
                        └─────────────────┘
```

## Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- pip (gestor de paquetes Python)

## Instalación Rápida

### 1. Crear Base de Datos

```sql
-- En PostgreSQL
CREATE DATABASE banco_pichincha;
\c banco_pichincha
\i database/schema.sql
```

### 2. Instalar Dependencias

```bash
# API de Servicios
cd services_api
pip install -r requirements.txt

# Backend
cd ../backend
pip install -r requirements.txt

# Frontend
cd ../frontend
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

Copiar los archivos `.env.example` a `.env` en cada servicio:

```bash
copy services_api\.env.example services_api\.env
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env
```

Editar cada `.env` con las credenciales de PostgreSQL.

### 4. Iniciar Todo

**Opción A - Script automático (Windows):**
```batch
iniciar.bat
```

**Opción B - Manual (3 terminales):**

```bash
# Terminal 1 - API Servicios
cd services_api
python app.py

# Terminal 2 - Backend
cd backend
python app.py

# Terminal 3 - Frontend
cd frontend
python app.py
```

### 5. Acceder al Sistema

- **Frontend:** http://localhost:5000
- **Backend API:** http://localhost:5001
- **Services API:** http://localhost:5002

## Estructura del Proyecto

```
ProyectoIntegradorGr5/
├── database/
│   └── schema.sql          # DDL PostgreSQL
├── services_api/           # API Servicios (5002)
│   ├── app.py
│   ├── models/
│   └── routes/
├── backend/                # Backend Principal (5001)
│   ├── app.py
│   ├── models/
│   └── routes/
├── frontend/               # Interfaz Web (5000)
│   ├── app.py
│   └── templates/
└── iniciar.bat            # Script de inicio
```

## Funcionalidades

### Backend (5001)
- CRUD de Personas (Natural/Jurídica)
- Gestión de Cuentas (Ahorros/Corriente)
- Tarjetas (Débito/Crédito)
- Transferencias
- Retiros con/sin tarjeta

### API Servicios (5002)
- Pago de Impuestos
- Matrícula Vehicular
- Multas (ANT, CNT, Claro)
- Servicios Públicos (Luz, Agua, Teléfono)

### Frontend (5000)
- Dashboard con resumen de cuentas
- Transferencias entre cuentas
- Pago de servicios
- Generación de códigos para retiro sin tarjeta

## Datos de Prueba

Para generar datos de prueba en la API de Servicios:

```bash
cd services_api
python seed_data.py
```
