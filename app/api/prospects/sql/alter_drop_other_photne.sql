-- Migration: Remove other_photne column from prospects table
ALTER TABLE prospects DROP COLUMN IF EXISTS other_photne;