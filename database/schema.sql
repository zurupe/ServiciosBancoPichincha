/*==============================================================*/
/* DBMS name:      PostgreSQL 9.x                               */
/* Sistema Bancario Banco Pichincha - DDL Corregido             */
/* Incluye módulo de Servicios para pagos                       */
/*==============================================================*/

-- Eliminar tablas existentes en orden correcto (dependencias)
DROP TABLE IF EXISTS PAGO_SERVICIO CASCADE;
DROP TABLE IF EXISTS SERVICIO CASCADE;
DROP TABLE IF EXISTS PROVEEDOR_SERVICIO CASCADE;
DROP TABLE IF EXISTS TIPO_SERVICIO CASCADE;
DROP TABLE IF EXISTS RETIRO_SIN_TARJETA CASCADE;
DROP TABLE IF EXISTS TRANSACCIONES CASCADE;
DROP TABLE IF EXISTS TARJETA_DEBITO CASCADE;
DROP TABLE IF EXISTS TARJETA_CREDITO CASCADE;
DROP TABLE IF EXISTS TARJETA CASCADE;
DROP TABLE IF EXISTS CUENTA_CORRIENTE CASCADE;
DROP TABLE IF EXISTS CUENTA_AHORROS CASCADE;
DROP TABLE IF EXISTS CUENTA CASCADE;
DROP TABLE IF EXISTS PERSONA_JURIDICA CASCADE;
DROP TABLE IF EXISTS PERSONA_NATURAL CASCADE;
DROP TABLE IF EXISTS PERSONA CASCADE;
DROP TABLE IF EXISTS CAJERO CASCADE;

/*==============================================================*/
/* Table: CAJERO                                                */
/*==============================================================*/
CREATE TABLE CAJERO (
   ID_CAJERO            SERIAL               NOT NULL,
   LATITUD              DECIMAL(10,6)        NOT NULL,
   LONGITUD             DECIMAL(10,6)        NOT NULL,
   ACTIVO               BOOLEAN              NOT NULL DEFAULT TRUE,
   SALDO                DECIMAL(12,2)        NOT NULL DEFAULT 0,
   DEPOSITOS            BOOLEAN              NOT NULL DEFAULT TRUE,
   NOMBRE               VARCHAR(100)         NOT NULL,
   CIUDAD               VARCHAR(64)          NOT NULL,
   PROVINCIA            VARCHAR(64)          NOT NULL,
   DIRECCION            VARCHAR(256)         NOT NULL,
   HORA_APERTURA        TIME                 NOT NULL DEFAULT '06:00',
   HORA_CIERRE          TIME                 NOT NULL DEFAULT '22:00',
   DIAS_OPERACION       VARCHAR(20)          NOT NULL DEFAULT 'L-D',
   CONSTRAINT PK_CAJERO PRIMARY KEY (ID_CAJERO)
);

/*==============================================================*/
/* Table: PERSONA                                               */
/*==============================================================*/
CREATE TABLE PERSONA (
   ID                   SERIAL               NOT NULL,
   CELULAR              VARCHAR(20)          NOT NULL,
   CORREO               VARCHAR(100)         NOT NULL,
   PATRIMONIO           NUMERIC(15,2)        NOT NULL DEFAULT 0,
   PASSWORD_HASH        VARCHAR(256)         NULL,
   FECHA_REGISTRO       TIMESTAMP            NOT NULL DEFAULT CURRENT_TIMESTAMP,
   ACTIVO               BOOLEAN              NOT NULL DEFAULT TRUE,
   CONSTRAINT PK_PERSONA PRIMARY KEY (ID)
);

/*==============================================================*/
/* Table: PERSONA_NATURAL                                       */
/*==============================================================*/
CREATE TABLE PERSONA_NATURAL (
   ID                   INTEGER              NOT NULL,
   CEDULA               VARCHAR(20)          NOT NULL UNIQUE,
   NOMBRE               VARCHAR(50)          NOT NULL,
   APELLIDO             VARCHAR(50)          NOT NULL,
   FECHA_NACIMIENTO     DATE                 NOT NULL,
   GENERO               VARCHAR(20)          NULL,
   ESTADO_CIVIL         VARCHAR(20)          NULL,
   OCUPACION            VARCHAR(50)          NULL,
   NACIONALIDAD         VARCHAR(50)          NOT NULL DEFAULT 'Ecuatoriana',
   DIRECCION            VARCHAR(256)         NULL,
   CONSTRAINT PK_PERSONA_NATURAL PRIMARY KEY (ID),
   CONSTRAINT FK_PN_PERSONA FOREIGN KEY (ID) REFERENCES PERSONA(ID) ON DELETE CASCADE
);

/*==============================================================*/
/* Table: PERSONA_JURIDICA                                      */
/*==============================================================*/
CREATE TABLE PERSONA_JURIDICA (
   ID                   INTEGER              NOT NULL,
   RUC                  VARCHAR(13)          NOT NULL UNIQUE,
   RAZON_SOCIAL         VARCHAR(200)         NOT NULL,
   NOMBRE_COMERCIAL     VARCHAR(200)         NULL,
   FECHA_CONSTITUCION   DATE                 NOT NULL,
   TIPO_EMPRESA         VARCHAR(50)          NOT NULL,
   REPRESENTANTE_LEGAL  VARCHAR(100)         NULL,
   DIRECCION            VARCHAR(256)         NULL,
   CONSTRAINT PK_PERSONA_JURIDICA PRIMARY KEY (ID),
   CONSTRAINT FK_PJ_PERSONA FOREIGN KEY (ID) REFERENCES PERSONA(ID) ON DELETE CASCADE
);

/*==============================================================*/
/* Table: CUENTA                                                */
/*==============================================================*/
CREATE TABLE CUENTA (
   ID_CUENTA            SERIAL               NOT NULL,
   ID_PERSONA           INTEGER              NOT NULL,
   NUMERO_CUENTA        VARCHAR(20)          NOT NULL UNIQUE,
   TIPO_CUENTA          VARCHAR(50)          NOT NULL,
   ESTADO               VARCHAR(20)          NOT NULL DEFAULT 'ACTIVA',
   FECHA_CREACION       TIMESTAMP            NOT NULL DEFAULT CURRENT_TIMESTAMP,
   FECHA_ACTUALIZACION  TIMESTAMP            NOT NULL DEFAULT CURRENT_TIMESTAMP,
   SALDO_ACTUAL         DECIMAL(18,2)        NOT NULL DEFAULT 0,
   COMISION_MENSUAL     DECIMAL(10,2)        NOT NULL DEFAULT 0,
   LIMITE_DIARIO        DECIMAL(12,2)        NOT NULL DEFAULT 5000,
   CONSTRAINT PK_CUENTA PRIMARY KEY (ID_CUENTA),
   CONSTRAINT FK_CUENTA_PERSONA FOREIGN KEY (ID_PERSONA) REFERENCES PERSONA(ID) ON DELETE RESTRICT
);

/*==============================================================*/
/* Table: CUENTA_AHORROS                                        */
/*==============================================================*/
CREATE TABLE CUENTA_AHORROS (
   ID_CUENTA            INTEGER              NOT NULL,
   TIPO_AHORRO          VARCHAR(50)          NOT NULL DEFAULT 'BASICA',
   TASA_INTERES         DECIMAL(5,4)         NOT NULL DEFAULT 0.0100,
   MINIMO_MANTENER      DECIMAL(12,2)        NOT NULL DEFAULT 0,
   COMISION_MANTENIMIENTO DECIMAL(10,2)      NOT NULL DEFAULT 0,
   CONSTRAINT PK_CUENTA_AHORROS PRIMARY KEY (ID_CUENTA),
   CONSTRAINT FK_CA_CUENTA FOREIGN KEY (ID_CUENTA) REFERENCES CUENTA(ID_CUENTA) ON DELETE CASCADE
);

/*==============================================================*/
/* Table: CUENTA_CORRIENTE                                      */
/*==============================================================*/
CREATE TABLE CUENTA_CORRIENTE (
   ID_CUENTA            INTEGER              NOT NULL,
   SOBREGIRO_AUTORIZADO DECIMAL(12,2)        NOT NULL DEFAULT 0,
   LIMITE_CHEQUES       INTEGER              NOT NULL DEFAULT 50,
   COSTO_CHEQUERA       DECIMAL(10,2)        NOT NULL DEFAULT 15.00,
   CONSTRAINT PK_CUENTA_CORRIENTE PRIMARY KEY (ID_CUENTA),
   CONSTRAINT FK_CC_CUENTA FOREIGN KEY (ID_CUENTA) REFERENCES CUENTA(ID_CUENTA) ON DELETE CASCADE
);

/*==============================================================*/
/* Table: TARJETA                                               */
/*==============================================================*/
CREATE TABLE TARJETA (
   ID_TARJETA           SERIAL               NOT NULL,
   ID_CUENTA            INTEGER              NOT NULL,
   NUMERO_TARJETA       VARCHAR(16)          NOT NULL UNIQUE,
   NOMBRE_TITULAR       VARCHAR(100)         NOT NULL,
   FECHA_EMISION        DATE                 NOT NULL DEFAULT CURRENT_DATE,
   FECHA_EXPIRACION     DATE                 NOT NULL,
   ESTADO               VARCHAR(20)          NOT NULL DEFAULT 'ACTIVA',
   TIPO_TARJETA         VARCHAR(20)          NOT NULL,
   PIN_HASH             VARCHAR(256)         NOT NULL,
   CVV_HASH             VARCHAR(256)         NOT NULL,
   PAIS_EMISION         VARCHAR(50)          NOT NULL DEFAULT 'Ecuador',
   CONSTRAINT PK_TARJETA PRIMARY KEY (ID_TARJETA),
   CONSTRAINT FK_TARJETA_CUENTA FOREIGN KEY (ID_CUENTA) REFERENCES CUENTA(ID_CUENTA) ON DELETE RESTRICT
);

/*==============================================================*/
/* Table: TARJETA_DEBITO                                        */
/*==============================================================*/
CREATE TABLE TARJETA_DEBITO (
   ID_TARJETA           INTEGER              NOT NULL,
   LIMITE_DIARIO_RETIRO DECIMAL(10,2)        NOT NULL DEFAULT 500,
   LIMITE_DIARIO_COMPRA DECIMAL(10,2)        NOT NULL DEFAULT 2000,
   CONSTRAINT PK_TARJETA_DEBITO PRIMARY KEY (ID_TARJETA),
   CONSTRAINT FK_TD_TARJETA FOREIGN KEY (ID_TARJETA) REFERENCES TARJETA(ID_TARJETA) ON DELETE CASCADE
);

/*==============================================================*/
/* Table: TARJETA_CREDITO                                       */
/*==============================================================*/
CREATE TABLE TARJETA_CREDITO (
   ID_TARJETA           INTEGER              NOT NULL,
   CUPO_TOTAL           DECIMAL(12,2)        NOT NULL,
   CUPO_DISPONIBLE      DECIMAL(12,2)        NOT NULL,
   FECHA_CORTE          INTEGER              NOT NULL DEFAULT 15,
   FECHA_PAGO           INTEGER              NOT NULL DEFAULT 25,
   TASA_INTERES         DECIMAL(5,4)         NOT NULL DEFAULT 0.1650,
   SALDO_ACTUAL         DECIMAL(12,2)        NOT NULL DEFAULT 0,
   CONSTRAINT PK_TARJETA_CREDITO PRIMARY KEY (ID_TARJETA),
   CONSTRAINT FK_TC_TARJETA FOREIGN KEY (ID_TARJETA) REFERENCES TARJETA(ID_TARJETA) ON DELETE CASCADE
);

/*==============================================================*/
/* Table: TRANSACCIONES                                         */
/*==============================================================*/
CREATE TABLE TRANSACCIONES (
   ID_TRANSACCION       SERIAL               NOT NULL,
   ID_CUENTA_ORIGEN     INTEGER              NULL,
   ID_CUENTA_DESTINO    INTEGER              NULL,
   ID_TARJETA           INTEGER              NULL,
   ID_CAJERO            INTEGER              NULL,
   TIPO_TRANSACCION     VARCHAR(50)          NOT NULL,
   MONTO                DECIMAL(12,2)        NOT NULL,
   FECHA_HORA           TIMESTAMP            NOT NULL DEFAULT CURRENT_TIMESTAMP,
   DESCRIPCION          VARCHAR(256)         NULL,
   ESTADO               VARCHAR(20)          NOT NULL DEFAULT 'COMPLETADA',
   REFERENCIA           VARCHAR(50)          NULL,
   CONSTRAINT PK_TRANSACCIONES PRIMARY KEY (ID_TRANSACCION),
   CONSTRAINT FK_TRANS_CUENTA_O FOREIGN KEY (ID_CUENTA_ORIGEN) REFERENCES CUENTA(ID_CUENTA),
   CONSTRAINT FK_TRANS_CUENTA_D FOREIGN KEY (ID_CUENTA_DESTINO) REFERENCES CUENTA(ID_CUENTA),
   CONSTRAINT FK_TRANS_TARJETA FOREIGN KEY (ID_TARJETA) REFERENCES TARJETA(ID_TARJETA),
   CONSTRAINT FK_TRANS_CAJERO FOREIGN KEY (ID_CAJERO) REFERENCES CAJERO(ID_CAJERO)
);

/*==============================================================*/
/* Table: RETIRO_SIN_TARJETA                                    */
/*==============================================================*/
CREATE TABLE RETIRO_SIN_TARJETA (
   ID_RETIRO            SERIAL               NOT NULL,
   ID_CUENTA            INTEGER              NOT NULL,
   CODIGO               VARCHAR(10)          NOT NULL UNIQUE,
   MONTO                DECIMAL(10,2)        NOT NULL,
   FECHA_GENERACION     TIMESTAMP            NOT NULL DEFAULT CURRENT_TIMESTAMP,
   FECHA_EXPIRACION     TIMESTAMP            NOT NULL,
   FECHA_USO            TIMESTAMP            NULL,
   ESTADO               VARCHAR(20)          NOT NULL DEFAULT 'PENDIENTE',
   ID_CAJERO_USO        INTEGER              NULL,
   CONSTRAINT PK_RETIRO_SIN_TARJETA PRIMARY KEY (ID_RETIRO),
   CONSTRAINT FK_RST_CUENTA FOREIGN KEY (ID_CUENTA) REFERENCES CUENTA(ID_CUENTA),
   CONSTRAINT FK_RST_CAJERO FOREIGN KEY (ID_CAJERO_USO) REFERENCES CAJERO(ID_CAJERO)
);

/*==============================================================*/
/* MODULO DE SERVICIOS - Para pagos de impuestos, matrículas,   */
/* multas y servicios públicos                                  */
/*==============================================================*/

/*==============================================================*/
/* Table: TIPO_SERVICIO                                         */
/*==============================================================*/
CREATE TABLE TIPO_SERVICIO (
   ID_TIPO              SERIAL               NOT NULL,
   CODIGO               VARCHAR(20)          NOT NULL UNIQUE,
   NOMBRE               VARCHAR(100)         NOT NULL,
   DESCRIPCION          VARCHAR(256)         NULL,
   ICONO                VARCHAR(50)          NULL,
   ACTIVO               BOOLEAN              NOT NULL DEFAULT TRUE,
   ORDEN                INTEGER              NOT NULL DEFAULT 0,
   CONSTRAINT PK_TIPO_SERVICIO PRIMARY KEY (ID_TIPO)
);

/*==============================================================*/
/* Table: PROVEEDOR_SERVICIO                                    */
/*==============================================================*/
CREATE TABLE PROVEEDOR_SERVICIO (
   ID_PROVEEDOR         SERIAL               NOT NULL,
   ID_TIPO              INTEGER              NOT NULL,
   CODIGO               VARCHAR(20)          NOT NULL UNIQUE,
   NOMBRE               VARCHAR(100)         NOT NULL,
   DESCRIPCION          VARCHAR(256)         NULL,
   LOGO_URL             VARCHAR(256)         NULL,
   ACTIVO               BOOLEAN              NOT NULL DEFAULT TRUE,
   REQUIERE_REFERENCIA  BOOLEAN              NOT NULL DEFAULT TRUE,
   FORMATO_REFERENCIA   VARCHAR(100)         NULL,
   CONSTRAINT PK_PROVEEDOR_SERVICIO PRIMARY KEY (ID_PROVEEDOR),
   CONSTRAINT FK_PROV_TIPO FOREIGN KEY (ID_TIPO) REFERENCES TIPO_SERVICIO(ID_TIPO)
);

/*==============================================================*/
/* Table: SERVICIO                                              */
/*==============================================================*/
CREATE TABLE SERVICIO (
   ID_SERVICIO          SERIAL               NOT NULL,
   ID_PROVEEDOR         INTEGER              NOT NULL,
   CODIGO               VARCHAR(50)          NOT NULL UNIQUE,
   NOMBRE               VARCHAR(100)         NOT NULL,
   DESCRIPCION          VARCHAR(256)         NULL,
   MONTO_FIJO           DECIMAL(10,2)        NULL,
   PERMITE_MONTO_VARIABLE BOOLEAN            NOT NULL DEFAULT TRUE,
   MONTO_MINIMO         DECIMAL(10,2)        NULL,
   MONTO_MAXIMO         DECIMAL(10,2)        NULL,
   COMISION             DECIMAL(10,2)        NOT NULL DEFAULT 0,
   ACTIVO               BOOLEAN              NOT NULL DEFAULT TRUE,
   CONSTRAINT PK_SERVICIO PRIMARY KEY (ID_SERVICIO),
   CONSTRAINT FK_SERV_PROV FOREIGN KEY (ID_PROVEEDOR) REFERENCES PROVEEDOR_SERVICIO(ID_PROVEEDOR)
);

/*==============================================================*/
/* Table: PAGO_SERVICIO                                         */
/*==============================================================*/
CREATE TABLE PAGO_SERVICIO (
   ID_PAGO              SERIAL               NOT NULL,
   ID_SERVICIO          INTEGER              NOT NULL,
   ID_CUENTA            INTEGER              NULL,
   ID_TRANSACCION       INTEGER              NULL,
   REFERENCIA_CLIENTE   VARCHAR(50)          NOT NULL,
   MONTO_BASE           DECIMAL(12,2)        NOT NULL,
   COMISION             DECIMAL(10,2)        NOT NULL DEFAULT 0,
   MONTO_TOTAL          DECIMAL(12,2)        NOT NULL,
   FECHA_PAGO           TIMESTAMP            NOT NULL DEFAULT CURRENT_TIMESTAMP,
   ESTADO               VARCHAR(20)          NOT NULL DEFAULT 'COMPLETADO',
   COMPROBANTE          VARCHAR(50)          NOT NULL,
   DETALLE              VARCHAR(256)         NULL,
   CONSTRAINT PK_PAGO_SERVICIO PRIMARY KEY (ID_PAGO),
   CONSTRAINT FK_PAGO_SERVICIO FOREIGN KEY (ID_SERVICIO) REFERENCES SERVICIO(ID_SERVICIO),
   CONSTRAINT FK_PAGO_CUENTA FOREIGN KEY (ID_CUENTA) REFERENCES CUENTA(ID_CUENTA),
   CONSTRAINT FK_PAGO_TRANS FOREIGN KEY (ID_TRANSACCION) REFERENCES TRANSACCIONES(ID_TRANSACCION)
);

/*==============================================================*/
/* Índices para mejorar rendimiento                             */
/*==============================================================*/
CREATE INDEX IDX_PERSONA_CORREO ON PERSONA(CORREO);
CREATE INDEX IDX_CUENTA_PERSONA ON CUENTA(ID_PERSONA);
CREATE INDEX IDX_CUENTA_NUMERO ON CUENTA(NUMERO_CUENTA);
CREATE INDEX IDX_TARJETA_CUENTA ON TARJETA(ID_CUENTA);
CREATE INDEX IDX_TARJETA_NUMERO ON TARJETA(NUMERO_TARJETA);
CREATE INDEX IDX_TRANS_FECHA ON TRANSACCIONES(FECHA_HORA);
CREATE INDEX IDX_TRANS_CUENTA_O ON TRANSACCIONES(ID_CUENTA_ORIGEN);
CREATE INDEX IDX_PAGO_FECHA ON PAGO_SERVICIO(FECHA_PAGO);
CREATE INDEX IDX_PAGO_REFERENCIA ON PAGO_SERVICIO(REFERENCIA_CLIENTE);
CREATE INDEX IDX_PROVEEDOR_TIPO ON PROVEEDOR_SERVICIO(ID_TIPO);

/*==============================================================*/
/* Datos iniciales para el módulo de servicios                  */
/*==============================================================*/

-- Tipos de servicio
INSERT INTO TIPO_SERVICIO (CODIGO, NOMBRE, DESCRIPCION, ICONO, ORDEN) VALUES
('IMPUESTOS', 'Impuestos', 'Pago de impuestos prediales y municipales', 'fa-building', 1),
('MATRICULA', 'Matrícula Vehicular', 'Pago de matrícula y tasas vehiculares', 'fa-car', 2),
('MULTAS', 'Multas y Citaciones', 'Pago de multas de tránsito y citaciones', 'fa-file-invoice', 3),
('SERVICIOS', 'Servicios Públicos', 'Pago de agua, luz, teléfono y más', 'fa-bolt', 4);

-- Proveedores de servicio
INSERT INTO PROVEEDOR_SERVICIO (ID_TIPO, CODIGO, NOMBRE, DESCRIPCION, REQUIERE_REFERENCIA, FORMATO_REFERENCIA) VALUES
-- Impuestos
(1, 'SRI', 'Servicio de Rentas Internas', 'Pago de impuestos al SRI', TRUE, 'RUC o Cédula'),
(1, 'GAD_QUITO', 'Municipio de Quito', 'Impuestos municipales y prediales Quito', TRUE, 'Número de predio'),
(1, 'GAD_GUAYAQUIL', 'Municipio de Guayaquil', 'Impuestos municipales y prediales Guayaquil', TRUE, 'Número de predio'),
(1, 'GAD_CUENCA', 'Municipio de Cuenca', 'Impuestos municipales y prediales Cuenca', TRUE, 'Número de predio'),
-- Matrícula
(2, 'ANT_MATRICULA', 'ANT - Matrícula', 'Agencia Nacional de Tránsito - Matriculación', TRUE, 'Placa del vehículo'),
(2, 'SRI_VEHICULAR', 'SRI - Impuesto Vehicular', 'Impuesto a la propiedad de vehículos', TRUE, 'Placa del vehículo'),
-- Multas
(3, 'ANT_MULTAS', 'ANT - Multas', 'Multas de tránsito ANT', TRUE, 'Cédula o Placa'),
(3, 'AMT_QUITO', 'AMT Quito', 'Agencia Metropolitana de Tránsito Quito', TRUE, 'Número de citación'),
(3, 'CNT', 'CNT', 'Corporación Nacional de Telecomunicaciones', TRUE, 'Número de teléfono'),
(3, 'CLARO', 'Claro', 'Claro Ecuador', TRUE, 'Número de línea'),
(3, 'MOVISTAR', 'Movistar', 'Movistar Ecuador', TRUE, 'Número de línea'),
-- Servicios públicos
(4, 'EEQ', 'Empresa Eléctrica Quito', 'Servicio de energía eléctrica Quito', TRUE, 'Número de suministro'),
(4, 'CNEL', 'CNEL', 'Corporación Nacional de Electricidad', TRUE, 'Número de cuenta'),
(4, 'EMAAP', 'EMAAP-Q', 'Agua potable Quito', TRUE, 'Número de cuenta'),
(4, 'INTERAGUA', 'Interagua', 'Agua potable Guayaquil', TRUE, 'Número de cuenta'),
(4, 'ETAPA', 'ETAPA', 'Agua y telecomunicaciones Cuenca', TRUE, 'Número de cuenta'),
(4, 'CNT_FIJO', 'CNT - Telefonía Fija', 'Servicio de telefonía fija CNT', TRUE, 'Número de teléfono'),
(4, 'CNT_INTERNET', 'CNT - Internet', 'Servicio de internet CNT', TRUE, 'Número de cuenta');

-- Servicios específicos
INSERT INTO SERVICIO (ID_PROVEEDOR, CODIGO, NOMBRE, DESCRIPCION, MONTO_FIJO, PERMITE_MONTO_VARIABLE, COMISION) VALUES
-- SRI
(1, 'SRI_IVA', 'Pago IVA', 'Pago mensual de IVA', NULL, TRUE, 0),
(1, 'SRI_RENTA', 'Impuesto a la Renta', 'Pago de impuesto a la renta', NULL, TRUE, 0),
-- Municipios
(2, 'QUITO_PREDIAL', 'Impuesto Predial Quito', 'Pago de impuesto predial urbano', NULL, TRUE, 0.50),
(2, 'QUITO_PATENTE', 'Patente Municipal Quito', 'Pago de patente municipal', NULL, TRUE, 0.50),
(3, 'GYE_PREDIAL', 'Impuesto Predial Guayaquil', 'Pago de impuesto predial', NULL, TRUE, 0.50),
(4, 'CUENCA_PREDIAL', 'Impuesto Predial Cuenca', 'Pago de impuesto predial', NULL, TRUE, 0.50),
-- Matrícula
(5, 'MATRICULA_VEHICULAR', 'Matrícula Vehicular', 'Pago de matrícula anual', NULL, TRUE, 1.00),
(6, 'IMP_VEHICULAR', 'Impuesto Vehicular', 'Impuesto sobre propiedad vehicular', NULL, TRUE, 0),
-- Multas
(7, 'ANT_MULTA_TRANSITO', 'Multa de Tránsito ANT', 'Pago de multas de tránsito', NULL, TRUE, 0.50),
(8, 'AMT_CITACION', 'Citación AMT', 'Pago de citaciones AMT Quito', NULL, TRUE, 0.50),
(9, 'CNT_FACTURA', 'Factura CNT', 'Pago de factura CNT', NULL, TRUE, 0),
(10, 'CLARO_FACTURA', 'Factura Claro', 'Pago de factura Claro', NULL, TRUE, 0),
(11, 'MOVISTAR_FACTURA', 'Factura Movistar', 'Pago de factura Movistar', NULL, TRUE, 0),
-- Servicios públicos
(12, 'EEQ_LUZ', 'Luz Eléctrica EEQ', 'Pago de planilla de luz EEQ', NULL, TRUE, 0),
(13, 'CNEL_LUZ', 'Luz Eléctrica CNEL', 'Pago de planilla de luz CNEL', NULL, TRUE, 0),
(14, 'EMAAP_AGUA', 'Agua Potable EMAAP', 'Pago de planilla de agua Quito', NULL, TRUE, 0),
(15, 'INTERAGUA_AGUA', 'Agua Potable Interagua', 'Pago de planilla de agua Guayaquil', NULL, TRUE, 0),
(16, 'ETAPA_AGUA', 'Agua Potable ETAPA', 'Pago de planilla de agua Cuenca', NULL, TRUE, 0),
(17, 'CNT_TELEFONO', 'Telefonía Fija CNT', 'Pago de servicio telefónico fijo', NULL, TRUE, 0),
(18, 'CNT_NET', 'Internet CNT', 'Pago de servicio de internet', NULL, TRUE, 0);

-- Mensaje de confirmación
DO $$
BEGIN
   RAISE NOTICE 'Base de datos Banco Pichincha creada exitosamente';
   RAISE NOTICE 'Tablas creadas: 17';
   RAISE NOTICE 'Tipos de servicio: 4';
   RAISE NOTICE 'Proveedores: 18';
   RAISE NOTICE 'Servicios: 21';
END $$;
