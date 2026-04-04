-- Migration: Add flag and hide columns to prospects table
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS flag BOOLEAN DEFAULT FALSE;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS hide BOOLEAN DEFAULT FALSE;
