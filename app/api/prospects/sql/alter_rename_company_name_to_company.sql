-- Migration: Rename company_name column to company in prospects table
ALTER TABLE prospects RENAME COLUMN company_name TO company;