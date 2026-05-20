-- CasaLuxe / Marketing AI Studio
-- PostgreSQL schema + example data

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =========================================================
-- CLEANUP
-- =========================================================

DROP TABLE IF EXISTS webhook_events CASCADE;
DROP TABLE IF EXISTS video_job_events CASCADE;
DROP TABLE IF EXISTS videos CASCADE;
DROP TABLE IF EXISTS video_jobs CASCADE;
DROP TABLE IF EXISTS script_versions CASCADE;
DROP TABLE IF EXISTS video_draft_reference_images CASCADE;
DROP TABLE IF EXISTS video_drafts CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS realtor_profiles CASCADE;
DROP TABLE IF EXISTS video_topics CASCADE;
DROP TABLE IF EXISTS auth_sessions CASCADE;
DROP TABLE IF EXISTS plans CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- =========================================================
-- USERS
-- =========================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    avatar_initials VARCHAR(8) NOT NULL,
    role TEXT NOT NULL DEFAULT 'realtor',
    status TEXT NOT NULL DEFAULT 'active',
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- AUTH SESSIONS (JWT REFRESH TOKENS)
-- =========================================================

CREATE TABLE auth_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash TEXT NOT NULL,
    device_name TEXT NULL,
    ip_address INET NULL,
    user_agent TEXT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- PLANS
-- =========================================================

CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    monthly_video_limit INTEGER NOT NULL,
    monthly_scene_limit INTEGER NOT NULL,
    price NUMERIC(10,2) NOT NULL DEFAULT 0,
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- SUBSCRIPTIONS
-- =========================================================

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES plans(id),
    billing_start DATE NOT NULL,
    billing_end DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    videos_used INTEGER NOT NULL DEFAULT 0,
    scenes_used INTEGER NOT NULL DEFAULT 0,
    videos_remaining INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- REALTOR PROFILES
-- =========================================================

CREATE TABLE realtor_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    brokerage_name TEXT NOT NULL,
    brand_name TEXT NOT NULL,
    logo_url TEXT NULL,
    avatar_asset_id TEXT NULL,
    voice_profile_id TEXT NULL,
    default_tone TEXT NOT NULL DEFAULT 'Professional',
    brand_settings_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- VIDEO TOPICS
-- =========================================================

CREATE TABLE video_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- VIDEO DRAFTS
-- =========================================================

CREATE TABLE video_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES video_topics(id),
    title TEXT NOT NULL,
    subject TEXT NULL,
    property_address TEXT NULL,
    description TEXT NULL,
    bullet_points_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    tone TEXT NOT NULL DEFAULT 'Professional',
    pacing TEXT NOT NULL DEFAULT 'Medium',
    status TEXT NOT NULL DEFAULT 'draft',
    current_step TEXT NOT NULL DEFAULT 'details',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- DRAFT REFERENCE IMAGES
-- =========================================================

CREATE TABLE video_draft_reference_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES video_drafts(id) ON DELETE CASCADE,
    storage_url TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'reference',
    sort_order INTEGER NOT NULL DEFAULT 0,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- SCRIPT VERSIONS
-- =========================================================

CREATE TABLE script_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES video_drafts(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    script_text TEXT NOT NULL,
    structured_script_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    estimated_read_time_seconds INTEGER NOT NULL DEFAULT 0,
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    approved_by_user_id UUID NULL REFERENCES users(id),
    approved_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- VIDEO JOBS
-- =========================================================

CREATE TABLE video_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES video_drafts(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'queued',
    job_type TEXT NOT NULL DEFAULT 'standard',
    idempotency_key TEXT NOT NULL UNIQUE,
    generation_job_id TEXT NULL,
    render_job_id TEXT NULL,
    progress_percent INTEGER NOT NULL DEFAULT 0,
    error_code TEXT NULL,
    error_message TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- VIDEO JOB EVENTS
-- =========================================================

CREATE TABLE video_job_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES video_jobs(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- VIDEOS
-- =========================================================

CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NULL UNIQUE REFERENCES video_jobs(id) ON DELETE CASCADE,
    draft_id UUID NULL UNIQUE REFERENCES video_drafts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    topic_id UUID NOT NULL REFERENCES video_topics(id),
    thumbnail_url TEXT NULL,
    final_video_url TEXT NULL,
    final_video_storage_key TEXT NULL,
    format TEXT NOT NULL DEFAULT 'mp4',
    duration_seconds INTEGER NOT NULL DEFAULT 0,
    scenes_count INTEGER NOT NULL DEFAULT 0,
    views_count INTEGER NOT NULL DEFAULT 0,
    downloads_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'published',
    published_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- WEBHOOK EVENTS
-- =========================================================

CREATE TABLE webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    external_event_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ NULL,
    status TEXT NOT NULL DEFAULT 'received'
);

-- =========================================================
-- INDEXES
-- =========================================================

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_video_drafts_user_id ON video_drafts(user_id);
CREATE INDEX idx_video_drafts_user_created_at ON video_drafts(user_id, created_at DESC);
CREATE INDEX idx_video_jobs_draft_id ON video_jobs(draft_id);
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_draft_id ON videos(draft_id);
