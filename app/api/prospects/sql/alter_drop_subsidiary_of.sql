-- Migration: Remove subsidiary_of column from prospects table
ALTER TABLE prospects DROP COLUMN IF EXISTS subsidiary_of;