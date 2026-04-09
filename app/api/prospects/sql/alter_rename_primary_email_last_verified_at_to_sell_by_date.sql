-- Migration: Rename primary_email_last_verified_at column to sell_by_date in prospects table
ALTER TABLE prospects RENAME COLUMN primary_email_last_verified_at TO sell_by_date;