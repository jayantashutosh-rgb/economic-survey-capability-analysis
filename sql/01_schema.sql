-- =============================================================================
-- Economic Survey 2025-26 — Capability Analysis Project
-- Schema definition for SQLite database
-- =============================================================================
-- This schema stores the chapter structure and page-level text of the
-- Economic Survey 2025-26 (Government of India, January 2026).
-- All data is sourced from the uploaded PDF only.
-- =============================================================================


-- Drop existing tables if rerunning (safe for development; remove in prod)
DROP TABLE IF EXISTS pages;
DROP TABLE IF EXISTS chapters;


-- -----------------------------------------------------------------------------
-- Table: chapters
-- One row per chapter in the Economic Survey.
-- Chapter 16 has two parts; stored as 16.1 and 16.2 (REAL type allows decimals).
-- -----------------------------------------------------------------------------
CREATE TABLE chapters (
    chapter_id     REAL    PRIMARY KEY,        -- 1, 2, ..., 15, 16.1, 16.2
    slug           TEXT    NOT NULL UNIQUE,    -- e.g. 'state_of_economy'
    title          TEXT    NOT NULL,           -- full chapter title
    start_page     INTEGER NOT NULL,           -- first PDF page of chapter
    end_page       INTEGER NOT NULL,           -- last PDF page of chapter
    page_count     INTEGER NOT NULL,           -- end_page - start_page + 1
    CHECK (start_page <= end_page),
    CHECK (page_count > 0)
);


-- -----------------------------------------------------------------------------
-- Table: pages
-- One row per PDF page within the body of the document.
-- Front matter (pages 1-51) and back matter (page 739-740 if not in a chapter)
-- are not stored.
-- -----------------------------------------------------------------------------
CREATE TABLE pages (
    page_id         INTEGER PRIMARY KEY AUTOINCREMENT, -- surrogate key
    pdf_page        INTEGER NOT NULL UNIQUE,           -- physical PDF page number
    chapter_id      REAL    NOT NULL,                  -- FK to chapters
    text            TEXT,                              -- cleaned page text
    char_count      INTEGER NOT NULL DEFAULT 0,
    word_count      INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id)
);


-- -----------------------------------------------------------------------------
-- Indexes for query performance
-- -----------------------------------------------------------------------------
-- Most analytical queries will filter by chapter or join chapters <-> pages
CREATE INDEX idx_pages_chapter_id ON pages(chapter_id);

-- Page lookups by PDF page number (e.g. tracing a finding back to source)
CREATE INDEX idx_pages_pdf_page ON pages(pdf_page);
