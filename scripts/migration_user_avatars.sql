-- =========================================================
-- Migration: user_avatars table for avatar generation feature
-- Apply on existing databases that already ran scripts/database.sql
-- =========================================================

BEGIN;

CREATE TABLE IF NOT EXISTS user_avatars (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending',
    additional_instructions TEXT NULL,
    reference_image_urls JSONB NOT NULL DEFAULT '[]'::jsonb,
    avatar_url TEXT NULL,
    external_job_id TEXT NULL,
    error_message TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_avatars_external_job_id
    ON user_avatars(external_job_id);

COMMIT;
