-- Migration: Add 'type' column to llm table
ALTER TABLE llm ADD COLUMN IF NOT EXISTS type TEXT DEFAULT 'default';
