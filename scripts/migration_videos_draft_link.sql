-- =========================================================
-- Migration: link videos to drafts directly + allow nullable job_id
-- Apply on existing databases that already ran scripts/database.sql
-- =========================================================

BEGIN;

ALTER TABLE videos
    ALTER COLUMN job_id DROP NOT NULL;

ALTER TABLE videos
    ADD COLUMN IF NOT EXISTS draft_id UUID NULL
        REFERENCES video_drafts(id) ON DELETE CASCADE;

ALTER TABLE videos
    ADD CONSTRAINT videos_draft_id_unique UNIQUE (draft_id);

CREATE INDEX IF NOT EXISTS idx_videos_draft_id ON videos(draft_id);
CREATE INDEX IF NOT EXISTS idx_video_drafts_user_created_at
    ON video_drafts(user_id, created_at DESC);

-- Backfill existing draft statuses to the new vocabulary
UPDATE video_drafts SET status = 'drafted' WHERE status = 'draft';

COMMIT;
