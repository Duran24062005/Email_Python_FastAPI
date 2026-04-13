-- ============================================================
-- Bootstrap completo para entornos nuevos
-- PostgreSQL
--
-- Importante:
-- - Este archivo sirve como snapshot inicial del esquema.
-- - La evolucion incremental del esquema debe gestionarse con Alembic.
-- - Despues de inicializar un entorno nuevo conviene ejecutar:
--   alembic upgrade head
-- ============================================================

-- Nota:
-- En Docker este script se ejecuta dentro de la base configurada por `POSTGRES_DB`.
-- Si lo ejecutas manualmente, conectate primero a `email_db`:
--   psql -U postgres -d email_db -f database.sql

-- ============================================================
-- ENUMS
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userStatus') THEN
        CREATE TYPE "userStatus" AS ENUM ('pending', 'active', 'deleted', 'blocked');
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userRole') THEN
        CREATE TYPE "userRole" AS ENUM ('admin', 'general');
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'emailstatus') THEN
        CREATE TYPE emailstatus AS ENUM ('pending', 'sent', 'failed');
    END IF;
END$$;

-- ============================================================
-- FUNCION COMPARTIDA PARA updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- TABLA users
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id             SERIAL PRIMARY KEY,
    name           VARCHAR(255) NOT NULL,
    email          VARCHAR(255) NOT NULL UNIQUE,
    hash_password  VARCHAR(255) NOT NULL,
    email_key      VARCHAR(255),
    status         "userStatus" NOT NULL DEFAULT 'active',
    role           "userRole"   NOT NULL DEFAULT 'general',
    last_login     TIMESTAMP,
    email_verify   BOOLEAN,
    created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_users_name      ON users(name);
CREATE INDEX IF NOT EXISTS ix_users_email     ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_email_key ON users(email_key);

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- TABLA emails
-- ============================================================

CREATE TABLE IF NOT EXISTS emails (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER      NOT NULL REFERENCES users(id),
    recipient      VARCHAR(255) NOT NULL,
    subject        VARCHAR(500) NOT NULL,
    body           TEXT,
    html_body      TEXT,
    status         emailstatus  NOT NULL DEFAULT 'pending',
    error_message  TEXT,
    sent_at        TIMESTAMP,
    created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_emails_user_id    ON emails(user_id);
CREATE INDEX IF NOT EXISTS idx_emails_recipient  ON emails(recipient);
CREATE INDEX IF NOT EXISTS idx_emails_status     ON emails(status);
CREATE INDEX IF NOT EXISTS idx_emails_created_at ON emails(created_at);

DROP TRIGGER IF EXISTS update_emails_updated_at ON emails;
CREATE TRIGGER update_emails_updated_at
    BEFORE UPDATE ON emails
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- DATOS DE EJEMPLO
-- ============================================================

INSERT INTO users (
    id,
    name,
    email,
    hash_password,
    status,
    role,
    email_verify,
    created_at,
    updated_at
)
VALUES
    (1, 'Administrador Demo', 'admin@example.com', 'demo-hash-admin', 'active', 'admin', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (2, 'Usuario Demo', 'user@example.com', 'demo-hash-user', 'active', 'general', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (3, 'Legacy Migration User', 'legacy-migration@local.invalid', 'alembic-managed-no-login', 'active', 'admin', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (email) DO NOTHING;

SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 1), true);

INSERT INTO emails (
    user_id,
    recipient,
    subject,
    body,
    status,
    sent_at,
    created_at,
    updated_at
)
VALUES
    (1, 'ejemplo1@test.com', 'Email de prueba 1', 'Este es un email de prueba', 'sent', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (2, 'ejemplo2@test.com', 'Email de prueba 2', 'Otro email de prueba', 'sent', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (3, 'ejemplo3@test.com', 'Email migrado legado', 'Este email representa un historico legado', 'pending', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- ============================================================
-- VERIFICACIONES MANUALES
-- ============================================================

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

\d users
\d emails

SELECT id, email, role, status FROM users ORDER BY id;
SELECT id, user_id, recipient, status FROM emails ORDER BY id;
