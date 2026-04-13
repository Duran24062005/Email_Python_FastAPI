# Alembic en este proyecto

## Que es Alembic

Alembic es la herramienta oficial de migraciones para SQLAlchemy. Permite versionar cambios de esquema en la base de datos de forma explicita, repetible y trazable.

En vez de depender de `create_all()` o de editar manualmente la base en cada entorno, Alembic guarda revisiones con pasos `upgrade` y `downgrade` para evolucionar el esquema con control.

## Por que se usa aqui

Este proyecto ya tenia modelos `users` y `emails` relacionados, pero el bootstrap SQL y el arranque de la aplicacion no estaban alineados.

Alembic se agrega para resolver eso de manera operativa:

- separar migraciones del arranque de FastAPI;
- evolucionar el esquema sin cambios manuales ad hoc;
- preservar datos existentes cuando el modelo cambie;
- dejar una historia versionada de cambios de base de datos.

## Flujo recomendado en este repositorio

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar migraciones antes de iniciar la API

```bash
alembic upgrade head
```

### 3. Iniciar la aplicacion

```bash
uvicorn app.main:app --reload --port 8001
```

La API ya no crea tablas automaticamente al arrancar. Si el esquema no esta migrado, la aplicacion podra conectarse a PostgreSQL, pero fallara cuando intente usar tablas inexistentes.

## Comandos basicos

### Aplicar todas las migraciones pendientes

```bash
alembic upgrade head
```

### Volver una revision atras

```bash
alembic downgrade -1
```

### Ver la revision actual aplicada

```bash
alembic current
```

### Ver el historial de revisiones

```bash
alembic history
```

### Crear una nueva revision

```bash
alembic revision -m "descripcion_corta"
```

Si el cambio es simple y los modelos ya estan actualizados, tambien puedes evaluar:

```bash
alembic revision --autogenerate -m "descripcion_corta"
```

Antes de usar `--autogenerate`, revisa manualmente el resultado. En este proyecto hay enums, triggers y SQL defensivo para compatibilidad con esquemas existentes, por lo que una revision autogenerada no debe asumirse correcta sin inspeccion.

## Relacion entre Alembic y `database.sql`

En este repositorio existen dos piezas relacionadas, pero con roles distintos:

- `alembic/`: fuente de verdad para la evolucion incremental del esquema.
- `database.sql`: snapshot completo para bootstrap de entornos nuevos, especialmente en Docker.

### Cuando usar Alembic

Usa Alembic cuando:

- cambias modelos SQLAlchemy;
- agregas o modificas tablas, columnas, enums, indices o constraints;
- necesitas llevar una base existente desde un estado anterior a uno nuevo;
- necesitas trazabilidad historica del esquema.

### Cuando tocar `database.sql`

Actualiza `database.sql` cuando el cambio de esquema deba reflejarse tambien en el bootstrap inicial de una base nueva.

En este proyecto, si agregas una nueva tabla o cambias relaciones base, debes hacer dos cosas:

1. crear la migracion en Alembic;
2. sincronizar `database.sql` para que nuevos entornos arranquen con el mismo shape base.

## Caso de uso concreto de este proyecto

La primera migracion de Alembic cubre el caso real que motivaba este cambio:

- la aplicacion ya esperaba `users`;
- `emails` ya dependia de `users.id`;
- el SQL bootstrap solo creaba `emails`;
- habia riesgo de tener registros historicos sin propietario.

La migracion inicial:

- crea enums `userStatus`, `userRole` y `emailstatus`;
- crea o alinea `users`;
- crea o alinea `emails`;
- agrega `emails.user_id`;
- crea la FK hacia `users`;
- crea un usuario tecnico legado y le asigna correos antiguos sin `user_id`.

Ese usuario legado existe para preservar historicos y endurecer la integridad referencial. No debe usarse como un actor funcional del producto.

## Uso con Docker

Si usas Docker Compose, el flujo recomendado es:

```bash
docker compose up -d postgres
docker compose run --rm email-api alembic upgrade head
docker compose up email-api
```

Si destruyes el volumen de PostgreSQL y vuelves a crear desde cero, `database.sql` dejara el esquema base listo. Aun asi, conviene ejecutar `alembic upgrade head` para asegurar que el contenedor queda exactamente en la revision actual.

## Reglas practicas para futuras migraciones

- no vuelvas a introducir `create_all()` en el startup de FastAPI;
- no dependas de cambios manuales en la base para entornos compartidos;
- revisa cada migracion antes de aplicarla en produccion;
- si cambias enums, relaciones o backfills, documenta el impacto en `prds/` o `docs/` cuando tenga efecto duradero;
- mantén sincronizados Alembic y `database.sql` mientras ambos sigan conviviendo.
