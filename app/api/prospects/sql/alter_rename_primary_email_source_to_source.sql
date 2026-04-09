-- Migration: Rename primary_email_source column to source in prospects table
ALTER TABLE prospects RENAME COLUMN primary_email_source TO source;