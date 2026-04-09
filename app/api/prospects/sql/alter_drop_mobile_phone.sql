-- Migration: Remove mobile_phone column from prospects table
ALTER TABLE prospects DROP COLUMN IF EXISTS mobile_phone;