-- ============================================================
-- Run this ONCE in Supabase SQL Editor before using Medicine Info.
-- Go to: Supabase Dashboard → SQL Editor → paste this → Run
-- ============================================================

-- 1. Enable pgvector (already enabled if health_knowledge works)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the medicine_knowledge table (separate from health_knowledge)
CREATE TABLE IF NOT EXISTS medicine_knowledge (
    id         BIGSERIAL PRIMARY KEY,
    content    TEXT        NOT NULL,
    embedding  VECTOR(1024),
    title      TEXT,
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create similarity search function
CREATE OR REPLACE FUNCTION search_medicine_knowledge(
    query_embedding VECTOR(1024),
    match_threshold FLOAT DEFAULT 0.45,
    match_count     INT   DEFAULT 5
)
RETURNS TABLE (
    id         BIGINT,
    content    TEXT,
    title      TEXT,
    source_url TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        mk.id,
        mk.content,
        mk.title,
        mk.source_url,
        1 - (mk.embedding <=> query_embedding) AS similarity
    FROM medicine_knowledge mk
    WHERE 1 - (mk.embedding <=> query_embedding) > match_threshold
    ORDER BY mk.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;