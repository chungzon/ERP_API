-- Migration: Add ParentCategoryID column to ProductCategory table
-- Purpose: Enable parent-child relationships between category layers
-- Layer 1 (大類別): ParentCategoryID = NULL
-- Layer 2 (中類別): ParentCategoryID = Layer 1 CategoryID
-- Layer 3 (小類別): ParentCategoryID = Layer 2 CategoryID

ALTER TABLE ProductCategory
ADD ParentCategoryID nvarchar(20) NULL;
