-- Migration: Rename person_linkinkedin_url column to linkedin in prospects table
ALTER TABLE prospects RENAME COLUMN person_linkinkedin_url TO linkedin;