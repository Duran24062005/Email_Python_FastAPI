# PRD: 026 - Alembic y alineacion de esquema `users` + `emails`

**Fecha:** 2026-04-13

## 1. Resumen

Se incorpora Alembic como mecanismo oficial de migracion del esquema PostgreSQL y se corrige la desalineacion entre el modelo SQLAlchemy y `database.sql`.

El proyecto ya operaba con modelos `User` y `Email` relacionados, pero el bootstrap SQL todavia representaba solo `emails`. A partir de este cambio:

- el esquema deja de crearse automaticamente al iniciar FastAPI;
- la evolucion del esquema pasa a gestionarse con `alembic upgrade head`;
- `database.sql` se mantiene como bootstrap completo para entornos nuevos;
- la migracion inicial preserva datos existentes mediante backfill a un usuario legado tecnico.

## 2. Problema

Antes del cambio existian tres riesgos operativos:

1. La API intentaba crear el esquema al arrancar con `Base.metadata.create_all()`, mezclando inicio de aplicacion con administracion de base de datos.
2. `database.sql` no incluia la tabla `users`, ni enums de usuario, ni la relacion `emails.user_id -> users.id`, aunque el codigo ya dependia de ello.
3. No existia una via versionada y repetible para evolucionar el esquema entre entornos.

## 3. Objetivo

Introducir un flujo de migraciones explicito y trazable que:

- represente fielmente los modelos actuales;
- preserve datos historicos existentes;
- elimine la creacion implicita de tablas en startup;
- deje documentado el uso operativo correcto dentro del repositorio.

## 4. Solucion

### Alembic como fuente de verdad evolutiva

- Se agrega configuracion base de Alembic al repositorio.
- La metadata de migracion usa la `Base` compartida de SQLAlchemy.
- La revision inicial crea o alinea:
  - enums `userStatus`, `userRole`, `emailstatus`;
  - tabla `users`;
  - tabla `emails`;
  - indices y triggers de `updated_at`;
  - FK `emails.user_id -> users.id`.

### Preservacion de datos existentes

Si existen registros historicos en `emails` sin `user_id`, la migracion:

- crea un usuario tecnico legado estable;
- reasigna esos correos a dicho usuario;
- despues aplica `NOT NULL` y la FK.

Esto evita perdida de informacion y permite endurecer la integridad referencial.

### Cambio operativo

- La app deja de ejecutar `create_all()` al arrancar.
- El esquema debe actualizarse con Alembic antes de levantar la API.
- `database.sql` se conserva como snapshot completo para entornos nuevos en Docker.

## 5. Impacto

### Infraestructura y desarrollo

- Nuevo paso operativo: `alembic upgrade head`.
- Docker sigue pudiendo inicializar una base vacia con `database.sql`.
- La app ya no modifica el esquema en runtime.

### Datos y contratos

- Sin cambios en contratos HTTP.
- Cambio persistente en contrato de base de datos:
  - `emails.user_id` pasa a ser obligatorio;
  - `users` se vuelve parte formal del esquema bootstrap;
  - enums de usuario y email quedan persistidos en PostgreSQL.

## 6. Riesgos y consideraciones

1. Mantener `database.sql` completo junto con Alembic implica doble fuente operativa.
2. Si el snapshot SQL y las migraciones divergen, los entornos nuevos y existentes podrian quedar en estados distintos.
3. El usuario legado tecnico no debe usarse como cuenta funcional del sistema; solo existe para preservar historicos.

## 7. Criterios de aceptacion

1. `alembic upgrade head` funciona sobre una base vacia.
2. `alembic upgrade head` funciona sobre una base antigua con solo `emails`.
3. La API arranca sin `create_all()` ni creacion automatica de tablas.
4. `database.sql` crea `users`, `emails`, enums, FK, indices y triggers alineados al modelo.
5. La documentacion deja claro como usar Alembic y cual es su rol en este proyecto.
