-- =============================================================================
-- Keyword density by chapter
-- =============================================================================
-- Question:
--   Which language clusters dominate each chapter, after normalising for
--   chapter size?
--
-- Method:
--   For five language clusters (growth, capability, state, welfare, market),
--   count keyword hits per chapter, then express them as hits per 1,000 words.
--   Density beats raw counts because chapter lengths vary 4x in this document.
--
-- Note on matching:
--   LIKE in SQLite is case-insensitive for ASCII by default. Patterns are
--   chosen so that key plural / inflected forms are also captured
--   (e.g. 'capabilit%' matches both 'capability' and 'capabilities').
-- =============================================================================

WITH keyword_hits AS (
    SELECT
        c.chapter_id,
        c.slug,
        SUM(p.word_count) AS total_words,

        -- Growth / output language
        SUM(
            (LENGTH(LOWER(p.text)) - LENGTH(REPLACE(LOWER(p.text), 'growth', ''))) / 6
        ) AS hits_growth,

        -- Capability / freedom language (Sen / Nussbaum vocabulary)
        SUM(
            (LENGTH(LOWER(p.text)) - LENGTH(REPLACE(LOWER(p.text), 'capabilit', ''))) / 9
        ) AS hits_capability,

        -- State / Mazzucato language
        SUM(
            (LENGTH(LOWER(p.text)) - LENGTH(REPLACE(LOWER(p.text), 'state capacity', ''))) / 14
            + (LENGTH(LOWER(p.text)) - LENGTH(REPLACE(LOWER(p.text), 'entrepreneurial', ''))) / 15
        ) AS hits_state,

        -- Welfare language
        SUM(
            (LENGTH(LOWER(p.text)) - LENGTH(REPLACE(LOWER(p.text), 'welfare', ''))) / 7
            + (LENGTH(LOWER(p.text)) - LENGTH(REPLACE(LOWER(p.text), 'poverty', ''))) / 7
        ) AS hits_welfare,

        -- Market language
        SUM(
            (LENGTH(LOWER(p.text)) - LENGTH(REPLACE(LOWER(p.text), 'market', ''))) / 6
        ) AS hits_market

    FROM chapters c
    JOIN pages p ON p.chapter_id = c.chapter_id
    GROUP BY c.chapter_id, c.slug
)

SELECT
    chapter_id,
    slug,
    total_words,
    hits_growth,
    hits_capability,
    hits_state,
    hits_welfare,
    hits_market,
    -- Density per 1,000 words (rounded to 1 decimal)
    ROUND(1000.0 * hits_growth     / total_words, 1) AS density_growth,
    ROUND(1000.0 * hits_capability / total_words, 1) AS density_capability,
    ROUND(1000.0 * hits_state      / total_words, 1) AS density_state,
    ROUND(1000.0 * hits_welfare    / total_words, 1) AS density_welfare,
    ROUND(1000.0 * hits_market     / total_words, 1) AS density_market
FROM keyword_hits
ORDER BY chapter_id;