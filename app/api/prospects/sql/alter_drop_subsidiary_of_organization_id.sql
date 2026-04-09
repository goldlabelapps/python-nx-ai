-- Migration: Remove subsidiary_of_organization_id column from prospects table
ALTER TABLE prospects DROP COLUMN IF EXISTS subsidiary_of_organization_id;