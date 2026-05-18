-- Ask a Delegate: vector store for WCA regulations + guidelines.
-- Run this once in the Supabase SQL Editor.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS regulation_chunks (
    id            BIGSERIAL PRIMARY KEY,
    regulation_id TEXT        NOT NULL,
    article_num   TEXT        NOT NULL,
    article_title TEXT,
    section_path  TEXT,
    content       TEXT        NOT NULL,
    kind          TEXT        NOT NULL CHECK (kind IN ('regulation', 'guideline')),
    url           TEXT        NOT NULL,
    embedding     VECTOR(1024) NOT NULL,
    updated_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (regulation_id, kind)
);

CREATE INDEX IF NOT EXISTS regulation_chunks_embedding_idx
    ON regulation_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 50);

-- Similarity-search RPC the Flask app calls.
CREATE OR REPLACE FUNCTION match_regulations(
    query_embedding VECTOR(1024),
    match_count     INT DEFAULT 6
)
RETURNS TABLE (
    regulation_id TEXT,
    article_title TEXT,
    section_path  TEXT,
    content       TEXT,
    kind          TEXT,
    url           TEXT,
    similarity    FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT regulation_id, article_title, section_path, content, kind, url,
           1 - (embedding <=> query_embedding) AS similarity
    FROM regulation_chunks
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Regulations are public reference material, so allow anon read access.
ALTER TABLE regulation_chunks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "regulation_chunks_anon_read"
    ON regulation_chunks
    FOR SELECT
    TO anon, authenticated
    USING (true);
