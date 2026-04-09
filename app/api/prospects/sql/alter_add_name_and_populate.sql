-- Migration: Add name column and populate with first_name + ' ' + last_name
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS name TEXT;
UPDATE prospects SET name = CONCAT_WS(' ', first_name, last_name);
