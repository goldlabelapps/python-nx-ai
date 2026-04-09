-- Migration: Rename sub_departments column to department in prospects table
ALTER TABLE prospects RENAME COLUMN sub_departments TO department;