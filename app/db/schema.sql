-- AudioRAG canonical schema.
-- The searchable table name is chunks. Do not introduce a second chunk table.
-- search_vector is derived only from content_redacted.
-- content keeps the original transcript for internal debugging and is not indexed.

CREATE TABLE IF NOT EXISTS audio_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'processing',
    stage TEXT NOT NULL DEFAULT 'normalizing',
    progress JSONB NOT NULL DEFAULT '{}'::jsonb,
    timings JSONB NOT NULL DEFAULT '{}'::jsonb,
    error TEXT,
    duration_seconds DOUBLE PRECISION,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    speaker_map JSONB NOT NULL DEFAULT '{}'::jsonb,
    vector_index TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT audio_files_filename_not_empty CHECK (length(btrim(filename)) > 0),
    CONSTRAINT audio_files_status_check CHECK (status IN ('processing', 'ready', 'failed')),
    CONSTRAINT audio_files_duration_check CHECK (
        duration_seconds IS NULL OR duration_seconds >= 0
    )
);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES audio_files (id) ON DELETE CASCADE,
    speaker TEXT NOT NULL,
    start_ts DOUBLE PRECISION NOT NULL,
    end_ts DOUBLE PRECISION NOT NULL,
    content TEXT NOT NULL,
    content_redacted TEXT NOT NULL,
    embedding vector(384),
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', content_redacted)
    ) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chunks_speaker_not_empty CHECK (length(btrim(speaker)) > 0),
    CONSTRAINT chunks_content_not_empty CHECK (length(btrim(content)) > 0),
    CONSTRAINT chunks_redacted_not_empty CHECK (length(btrim(content_redacted)) > 0),
    CONSTRAINT chunks_time_order_check CHECK (end_ts >= start_ts AND start_ts >= 0)
);

CREATE INDEX IF NOT EXISTS audio_files_status_idx ON audio_files (status);
CREATE INDEX IF NOT EXISTS chunks_file_id_idx ON chunks (file_id);
CREATE INDEX IF NOT EXISTS chunks_speaker_idx ON chunks (speaker);
CREATE INDEX IF NOT EXISTS chunks_search_vector_idx ON chunks USING gin (search_vector);

COMMENT ON TABLE chunks IS
    'Speaker-aware retrieval units. Lexical search and embeddings use content_redacted only.';
COMMENT ON COLUMN chunks.content IS
    'Original transcript text. Not indexed, not embedded, and not returned by the search API.';
COMMENT ON COLUMN chunks.content_redacted IS
    'PII-redacted text. Source for search_vector, embeddings, snippets, and LLM evidence.';
COMMENT ON COLUMN chunks.search_vector IS
    'English full-text vector generated from content_redacted.';
