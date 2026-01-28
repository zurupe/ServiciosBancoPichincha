/*==============================================================*/
/* DBMS name:      PostgreSQL 9.x                               */
/* Created on:     28/1/2026 17:21:03                           */
/*==============================================================*/


drop index CAJERO_PK;

drop table CAJERO;

drop index RELATIONSHIP_1_FK;

drop index CUENTA_PK;

drop table CUENTA;

drop index INHERITANCE_4_FK;

drop index CUENTA_AHORROS_PK;

drop table CUENTA_AHORROS;

drop index INHERITANCE_3_FK;

drop index CUENTA_CORRIENTE_PK;

drop table CUENTA_CORRIENTE;

drop index PERSONA_PK;

drop table PERSONA;

drop index INHERITANCE_2_FK;

drop index PERSONA_JURIDICA_PK;

drop table PERSONA_JURIDICA;

drop index INHERITANCE_1_FK;

drop index PERSONA_NATURAL_PK;

drop table PERSONA_NATURAL;

drop index RELATIONSHIP_2_FK;

drop index TARJETA_PK;

drop table TARJETA;

drop index TARJETA_CREDITO_PK;

drop table TARJETA_CREDITO;

drop index TARJETA_DEBITO_PK;

drop table TARJETA_DEBITO;

drop index RELATIONSHIP_4_FK;

drop index RELATIONSHIP_3_FK;

drop table TRANSACCIONES;

/*==============================================================*/
/* Table: CAJERO                                                */
/*==============================================================*/
create table CAJERO (
   ID_CAJERO            INT4                 not null,
   LATITUD              DECIMAL(8,2)         not null,
   LONGITUD             DECIMAL(8,2)         not null,
   ACTIVO               BOOL                 not null,
   SALDO                DECIMAL(8,2)         not null,
   DEPOSITOS            BOOL                 not null,
   NOMBRE               VARCHAR(20)          not null,
   CIUDAD               VARCHAR(32)          not null,
   PROVINCIA            VARCHAR(32)          not null,
   DIRECCION            VARCHAR(128)         not null,
   HORA_APERTURA        TIME                 not null,
   HORA_CIERRE          TIME                 not null,
   DIAS                 CHAR(1)              not null,
   constraint PK_CAJERO primary key (ID_CAJERO)
);

/*==============================================================*/
/* Index: CAJERO_PK                                             */
/*==============================================================*/
create unique index CAJERO_PK on CAJERO (
ID_CAJERO
);

/*==============================================================*/
/* Table: CUENTA                                                */
/*==============================================================*/
create table CUENTA (
   ID_CUENTA            INT4                 not null,
   ID                   INT4                 null,
   N_CUENTA             INT4                 not null,
   TIPO_CUENTA          VARCHAR(128)         not null,
   ESTADO               VARCHAR(64)          not null,
   FECHA_CREACION       DATE                 not null,
   FECHA_ACTUALIZACION  DATE                 not null,
   FECHA_CIERRE         DATE                 not null,
   SALDO_ACTUAL         DECIMAL(18,2)        not null,
   COMISION_MENSUAL     DECIMAL(18,2)        not null,
   LIMITE_OPERACIONES_DIARIAS INT4                 not null,
   constraint PK_CUENTA primary key (ID_CUENTA)
);

/*==============================================================*/
/* Index: CUENTA_PK                                             */
/*==============================================================*/
create unique index CUENTA_PK on CUENTA (
ID_CUENTA
);

/*==============================================================*/
/* Index: RELATIONSHIP_1_FK                                     */
/*==============================================================*/
create  index RELATIONSHIP_1_FK on CUENTA (
ID
);

/*==============================================================*/
/* Table: CUENTA_AHORROS                                        */
/*==============================================================*/
create table CUENTA_AHORROS (
   ID_CUENTA            INT4                 not null,
   ID_TIPO_CUENTA       INT4                 not null,
   ID                   INT4                 null,
   N_CUENTA             INT4                 not null,
   TIPO_CUENTA          VARCHAR(128)         not null,
   ESTADO               VARCHAR(64)          not null,
   FECHA_CREACION       DATE                 not null,
   FECHA_ACTUALIZACION  DATE                 not null,
   FECHA_CIERRE         DATE                 not null,
   SALDO_ACTUAL         DECIMAL(18,2)        not null,
   COMISION_MENSUAL     DECIMAL(18,2)        not null,
   LIMITE_OPERACIONES_DIARIAS INT4                 not null,
   TIPO_CUENTA_AHORROS  VARCHAR(200)         not null,
   TAZA_INTERES         DECIMAL(18,2)        not null,
   MINIMO_PARA_MANTENER DECIMAL(18,2)        not null,
   COMISION_MANTENIMIENTO DECIMAL(18,2)        not null,
   FECHA_APERTURA       DATE                 not null,
   constraint PK_CUENTA_AHORROS primary key (ID_CUENTA, ID_TIPO_CUENTA)
);

/*==============================================================*/
/* Index: CUENTA_AHORROS_PK                                     */
/*==============================================================*/
create unique index CUENTA_AHORROS_PK on CUENTA_AHORROS (
ID_CUENTA,
ID_TIPO_CUENTA
);

/*==============================================================*/
/* Index: INHERITANCE_4_FK                                      */
/*==============================================================*/
create  index INHERITANCE_4_FK on CUENTA_AHORROS (
ID_CUENTA
);

/*==============================================================*/
/* Table: CUENTA_CORRIENTE                                      */
/*==============================================================*/
create table CUENTA_CORRIENTE (
   ID_CUENTA            INT4                 not null,
   CUENTA_CREDITO       INT4                 not null,
   ID                   INT4                 null,
   N_CUENTA             INT4                 not null,
   TIPO_CUENTA          VARCHAR(128)         not null,
   ESTADO               VARCHAR(64)          not null,
   FECHA_CREACION       DATE                 not null,
   FECHA_ACTUALIZACION  DATE                 not null,
   FECHA_CIERRE         DATE                 not null,
   SALDO_ACTUAL         DECIMAL(18,2)        not null,
   CUE_COMISION_MENSUAL DECIMAL(18,2)        not null,
   LIMITE_OPERACIONES_DIARIAS INT4                 not null,
   FECHA_VENCIMIENTO    DATE                 not null,
   LIMITE_OPERACIONAL_DIARIO INT4                 not null,
   REGLAS_REGISTRADAS   VARCHAR(200)         not null,
   COMISION_MENSUAL     DECIMAL(18,2)        not null,
   constraint PK_CUENTA_CORRIENTE primary key (ID_CUENTA, CUENTA_CREDITO)
);

/*==============================================================*/
/* Index: CUENTA_CORRIENTE_PK                                   */
/*==============================================================*/
create unique index CUENTA_CORRIENTE_PK on CUENTA_CORRIENTE (
ID_CUENTA,
CUENTA_CREDITO
);

/*==============================================================*/
/* Index: INHERITANCE_3_FK                                      */
/*==============================================================*/
create  index INHERITANCE_3_FK on CUENTA_CORRIENTE (
ID_CUENTA
);

/*==============================================================*/
/* Table: PERSONA                                               */
/*==============================================================*/
create table PERSONA (
   ID                   INT4                 not null,
   CELULAR              VARCHAR(20)          not null,
   CORREO               CHAR(20)             not null,
   PATRIMONIO           FLOAT15              not null,
   constraint PK_PERSONA primary key (ID)
);

/*==============================================================*/
/* Index: PERSONA_PK                                            */
/*==============================================================*/
create unique index PERSONA_PK on PERSONA (
ID
);

/*==============================================================*/
/* Table: PERSONA_JURIDICA                                      */
/*==============================================================*/
create table PERSONA_JURIDICA (
   ID                   INT4                 not null,
   RUC                  CHAR(13)             not null,
   CELULAR              VARCHAR(20)          not null,
   CORREO               CHAR(20)             not null,
   PATRIMONIO           FLOAT15              not null,
   RAZON_SOCIAL         VARCHAR(100)         not null,
   NOMBRE_COMERCIAL     VARCHAR(100)         not null,
   FECHA_CONSTITUCION   DATE                 not null,
   TIPO_EMPRESA         VARCHAR(50)          not null,
   constraint PK_PERSONA_JURIDICA primary key (ID, RUC)
);

/*==============================================================*/
/* Index: PERSONA_JURIDICA_PK                                   */
/*==============================================================*/
create unique index PERSONA_JURIDICA_PK on PERSONA_JURIDICA (
ID,
RUC
);

/*==============================================================*/
/* Index: INHERITANCE_2_FK                                      */
/*==============================================================*/
create  index INHERITANCE_2_FK on PERSONA_JURIDICA (
ID
);

/*==============================================================*/
/* Table: PERSONA_NATURAL                                       */
/*==============================================================*/
create table PERSONA_NATURAL (
   ID                   INT4                 not null,
   CEDULA               VARCHAR(20)          not null,
   CELULAR              VARCHAR(20)          not null,
   CORREO               CHAR(20)             not null,
   PATRIMONIO           FLOAT15              not null,
   NOMBRE               VARCHAR(20)          not null,
   APELLIDO             VARCHAR(20)          not null,
   FECHA_NACIMIENTO     DATE                 not null,
   GENERO               VARCHAR(10)          not null,
   ESTADO_CIVIL         VARCHAR(20)          not null,
   OCUPACION            VARCHAR(20)          not null,
   NACIONALIDAD         VARCHAR(20)          not null,
   constraint PK_PERSONA_NATURAL primary key (ID, CEDULA)
);

/*==============================================================*/
/* Index: PERSONA_NATURAL_PK                                    */
/*==============================================================*/
create unique index PERSONA_NATURAL_PK on PERSONA_NATURAL (
ID,
CEDULA
);

/*==============================================================*/
/* Index: INHERITANCE_1_FK                                      */
/*==============================================================*/
create  index INHERITANCE_1_FK on PERSONA_NATURAL (
ID
);

/*==============================================================*/
/* Table: TARJETA                                               */
/*==============================================================*/
create table TARJETA (
   ID_TARJETA           VARCHAR(16)          not null,
   ID_CUENTA            INT4                 null,
   NUMERO_TARJETA       VARCHAR(16)          not null,
   NOMBRE_TITULAR       VARCHAR(100)         not null,
   FECHA_EMISION        DATE                 not null,
   FECHA_EXPIRACION     DATE                 not null,
   ESTADO_TARJETA       VARCHAR(20)          not null,
   TIPO_TARJETA         VARCHAR(10)          not null,
   PIN_HASH             VARCHAR(256)         not null,
   PAIS_EMISION         VARCHAR(50)          not null,
   constraint PK_TARJETA primary key (ID_TARJETA)
);

/*==============================================================*/
/* Index: TARJETA_PK                                            */
/*==============================================================*/
create unique index TARJETA_PK on TARJETA (
ID_TARJETA
);

/*==============================================================*/
/* Index: RELATIONSHIP_2_FK                                     */
/*==============================================================*/
create  index RELATIONSHIP_2_FK on TARJETA (
ID_CUENTA
);

/*==============================================================*/
/* Table: TARJETA_CREDITO                                       */
/*==============================================================*/
create table TARJETA_CREDITO (
   ID_TARJETA           VARCHAR(16)          not null,
   ID_CUENTA            INT4                 null,
   NUMERO_TARJETA       VARCHAR(16)          not null,
   NOMBRE_TITULAR       VARCHAR(100)         not null,
   FECHA_EMISION        DATE                 not null,
   FECHA_EXPIRACION     DATE                 not null,
   ESTADO_TARJETA       VARCHAR(20)          not null,
   TIPO_TARJETA         VARCHAR(10)          not null,
   PIN_HASH             VARCHAR(256)         not null,
   PAIS_EMISION         VARCHAR(50)          not null,
   CUPO_TOTAL_APROBADO  DECIMAL(12,2)        not null,
   CUPO_DISPONIBLE      DECIMAL(12,2)        not null,
   FECHA_CORTE          DATE                 not null,
   FECHA_PAGO           DATE                 not null,
   TASA_INTERES         DECIMAL(5,2)         not null,
   constraint PK_TARJETA_CREDITO primary key (ID_TARJETA)
);

/*==============================================================*/
/* Index: TARJETA_CREDITO_PK                                    */
/*==============================================================*/
create unique index TARJETA_CREDITO_PK on TARJETA_CREDITO (
ID_TARJETA
);

/*==============================================================*/
/* Table: TARJETA_DEBITO                                        */
/*==============================================================*/
create table TARJETA_DEBITO (
   ID_TARJETA           VARCHAR(16)          not null,
   ID_CUENTA            INT4                 null,
   NUMERO_TARJETA       VARCHAR(16)          not null,
   NOMBRE_TITULAR       VARCHAR(100)         not null,
   FECHA_EMISION        DATE                 not null,
   FECHA_EXPIRACION     DATE                 not null,
   ESTADO_TARJETA       VARCHAR(20)          not null,
   TIPO_TARJETA         VARCHAR(10)          not null,
   PIN_HASH             VARCHAR(256)         not null,
   PAIS_EMISION         VARCHAR(50)          not null,
   NUMERO_CUENTA_ASOCIADA VARCHAR(20)          not null,
   TIPO_CUENTA          VARCHAR(128)         not null,
   SALDO_DISPONIBLE     DECIMAL(12,2)        not null,
   LIMITE_DIARIO_RETIRO DECIMAL(10,2)        not null,
   constraint PK_TARJETA_DEBITO primary key (ID_TARJETA)
);

/*==============================================================*/
/* Index: TARJETA_DEBITO_PK                                     */
/*==============================================================*/
create unique index TARJETA_DEBITO_PK on TARJETA_DEBITO (
ID_TARJETA
);

/*==============================================================*/
/* Table: TRANSACCIONES                                         */
/*==============================================================*/
create table TRANSACCIONES (
   ID_TARJETA           VARCHAR(16)          null,
   ID_CAJERO            INT4                 null
);

/*==============================================================*/
/* Index: RELATIONSHIP_3_FK                                     */
/*==============================================================*/
create  index RELATIONSHIP_3_FK on TRANSACCIONES (
ID_CAJERO
);

/*==============================================================*/
/* Index: RELATIONSHIP_4_FK                                     */
/*==============================================================*/
create  index RELATIONSHIP_4_FK on TRANSACCIONES (
ID_TARJETA
);

alter table CUENTA
   add constraint FK_CUENTA_RELATIONS_PERSONA foreign key (ID)
      references PERSONA (ID)
      on delete restrict on update restrict;

alter table CUENTA_AHORROS
   add constraint FK_CUENTA_A_INHERITAN_CUENTA foreign key (ID_CUENTA)
      references CUENTA (ID_CUENTA)
      on delete restrict on update restrict;

alter table CUENTA_CORRIENTE
   add constraint FK_CUENTA_C_INHERITAN_CUENTA foreign key (ID_CUENTA)
      references CUENTA (ID_CUENTA)
      on delete restrict on update restrict;

alter table PERSONA_JURIDICA
   add constraint FK_PERSONA__INHERITAN_PERSONA foreign key (ID)
      references PERSONA (ID)
      on delete restrict on update restrict;

alter table PERSONA_NATURAL
   add constraint FK_PERSONA__INHERITAN_PERSONA foreign key (ID)
      references PERSONA (ID)
      on delete restrict on update restrict;

alter table TARJETA
   add constraint FK_TARJETA_RELATIONS_CUENTA foreign key (ID_CUENTA)
      references CUENTA (ID_CUENTA)
      on delete restrict on update restrict;

alter table TARJETA_CREDITO
   add constraint FK_TARJETA__INHERITAN_TARJETA foreign key (ID_TARJETA)
      references TARJETA (ID_TARJETA)
      on delete restrict on update restrict;

alter table TARJETA_DEBITO
   add constraint FK_TARJETA__INHERITAN_TARJETA foreign key (ID_TARJETA)
      references TARJETA (ID_TARJETA)
      on delete restrict on update restrict;

alter table TRANSACCIONES
   add constraint FK_TRANSACC_RELATIONS_CAJERO foreign key (ID_CAJERO)
      references CAJERO (ID_CAJERO)
      on delete restrict on update restrict;

alter table TRANSACCIONES
   add constraint FK_TRANSACC_RELATIONS_TARJETA foreign key (ID_TARJETA)
      references TARJETA (ID_TARJETA)
      on delete restrict on update restrict;

