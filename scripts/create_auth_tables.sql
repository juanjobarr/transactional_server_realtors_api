-- =============================================================================
-- Auth tables for the Transactional Service
-- Run this in Supabase SQL Editor if the tables don't exist yet
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- users
CREATE TABLE IF NOT EXISTS users (
    id               UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name        VARCHAR(255) NOT NULL,
    email            VARCHAR(255) UNIQUE NOT NULL,
    password_hash    VARCHAR(255) NOT NULL,
    avatar_initials  VARCHAR(10),
    role             VARCHAR(50)  NOT NULL DEFAULT 'realtor',
    status           VARCHAR(50)  NOT NULL DEFAULT 'active',
    is_email_verified BOOLEAN     NOT NULL DEFAULT FALSE,
    last_login_at    TIMESTAMPTZ,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

-- auth_sessions
CREATE TABLE IF NOT EXISTS auth_sessions (
    id                  UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID         NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    refresh_token_hash  VARCHAR(255) NOT NULL UNIQUE,
    device_name         VARCHAR(255),
    ip_address          VARCHAR(50),
    user_agent          VARCHAR(500),
    expires_at          TIMESTAMPTZ  NOT NULL,
    revoked_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id            ON auth_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_refresh_token_hash ON auth_sessions (refresh_token_hash);
