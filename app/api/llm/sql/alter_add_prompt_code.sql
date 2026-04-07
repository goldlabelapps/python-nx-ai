-- Migration: Add prompt_code column to llm table
ALTER TABLE llm ADD COLUMN IF NOT EXISTS prompt_code TEXT;