-- Script para crear la base de datos y tabla de emails
-- PostgreSQL

-- Crear la base de datos (ejecutar como superusuario)
CREATE DATABASE email_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;

-- Conectarse a la base de datos
\c email_db

-- Crear enum para estados de email
-- ============================================================
-- Script de inicialización para Docker
-- Se ejecuta automáticamente al crear el contenedor de postgres
-- ============================================================

-- Crear enum (nombre debe coincidir con el modelo SQLAlchemy: 'emailstatus')
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'emailstatus') THEN
        CREATE TYPE emailstatus AS ENUM ('pending', 'sent', 'failed');
    END IF;
END$$;

-- Crear tabla de emails
CREATE TABLE IF NOT EXISTS emails (
    id          SERIAL PRIMARY KEY,
    recipient   VARCHAR(255) NOT NULL,
    subject     VARCHAR(500) NOT NULL,
    body        TEXT,
    html_body   TEXT,
    status      emailstatus  NOT NULL DEFAULT 'pending',
    error_message TEXT,
    sent_at     TIMESTAMP,
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_emails_recipient  ON emails(recipient);
CREATE INDEX IF NOT EXISTS idx_emails_status     ON emails(status);
CREATE INDEX IF NOT EXISTS idx_emails_created_at ON emails(created_at DESC);

-- Trigger para updated_at automático
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_emails_updated_at ON emails;
CREATE TRIGGER update_emails_updated_at
    BEFORE UPDATE ON emails
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insertar datos de ejemplo (opcional)
INSERT INTO emails (recipient, subject, body, status, sent_at) VALUES
    ('ejemplo1@test.com', 'Email de prueba 1', 'Este es un email de prueba', 'sent', CURRENT_TIMESTAMP),
    ('ejemplo2@test.com', 'Email de prueba 2', 'Otro email de prueba', 'sent', CURRENT_TIMESTAMP),
    ('ejemplo3@test.com', 'Email pendiente', 'Este email está pendiente', 'pending', NULL);

-- Verificar que todo se creó correctamente
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Ver estructura de la tabla
\d emails

-- Ver datos insertados
SELECT * FROM emails;