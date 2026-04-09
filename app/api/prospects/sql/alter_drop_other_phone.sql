-- Migration: Remove other_phone column from prospects table
ALTER TABLE prospects DROP COLUMN IF EXISTS other_phone;