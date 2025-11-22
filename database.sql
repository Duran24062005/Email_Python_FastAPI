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
CREATE TYPE email_status AS ENUM ('pending', 'sent', 'failed');

-- Crear tabla de emails
CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    recipient VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    body TEXT,
    html_body TEXT,
    status email_status DEFAULT 'pending' NOT NULL,
    error_message TEXT,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Crear índices para mejorar rendimiento
CREATE INDEX idx_emails_recipient ON emails(recipient);
CREATE INDEX idx_emails_status ON emails(status);
CREATE INDEX idx_emails_created_at ON emails(created_at DESC);

-- Crear función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Crear trigger para actualizar updated_at
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