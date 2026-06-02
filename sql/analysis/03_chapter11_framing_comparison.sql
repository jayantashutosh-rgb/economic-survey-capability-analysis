-- =============================================================================
-- Chapter 11 (Education & Health) — Framing comparison
-- =============================================================================
-- Hypothesis:
--   Chapter 11 covers exactly the domain (health, education) where Sen's
--   capability framework is most relevant. Yet the keyword density query
--   (02_keyword_density_by_chapter.sql) showed density_capability = 0.0
--   for this chapter.
--
--   If the chapter avoids Sen's vocabulary, what vocabulary does it use
--   instead? We hypothesise that it uses instrumental / human-capital
--   language, framing citizens as inputs to growth rather than as bearers
--   of substantive freedoms.
--
-- Method:
--   Count two competing vocabulary clusters within Chapter 11 only.
--   Compare hit counts and densities.
-- =============================================================================

WITH ch11 AS (
    SELECT
        p.page_id,
        p.pdf_page,
        p.word_count,
        LOWER(p.text) AS text_lower
    FROM pages p
    WHERE p.chapter_id = 11
),
hits AS (
    SELECT
        SUM(word_count) AS total_words,

        -- Cluster A: Instrumental / Human Capital language
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'human capital', '')))   / 13) AS hits_human_capital,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'workforce', '')))       / 9)  AS hits_workforce,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'productivity', '')))    / 12) AS hits_productivity,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'skill', '')))           / 5)  AS hits_skill,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'outcome', '')))         / 7)  AS hits_outcome,

        -- Cluster B: Capability / Wellbeing / Freedom language
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'capabilit', '')))       / 9)  AS hits_capability,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'freedom', '')))         / 7)  AS hits_freedom,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'agency', '')))          / 6)  AS hits_agency,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'well-being', '')))      / 10) AS hits_wellbeing_hyph,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'wellbeing', '')))       / 9)  AS hits_wellbeing,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'dignity', '')))         / 7)  AS hits_dignity
    FROM ch11
)

SELECT 'CLUSTER A — Instrumental / Human Capital'                                AS label, total_words,
       hits_human_capital + hits_workforce + hits_productivity + hits_skill + hits_outcome
                                                                                  AS total_hits,
       ROUND(1000.0 * (hits_human_capital + hits_workforce + hits_productivity + hits_skill + hits_outcome) / total_words, 2)
                                                                                  AS density_per_1000
FROM hits

UNION ALL

SELECT 'CLUSTER B — Capability / Freedom / Wellbeing'                            AS label, total_words,
       hits_capability + hits_freedom + hits_agency + hits_wellbeing_hyph + hits_wellbeing + hits_dignity
                                                                                  AS total_hits,
       ROUND(1000.0 * (hits_capability + hits_freedom + hits_agency + hits_wellbeing_hyph + hits_wellbeing + hits_dignity) / total_words, 2)
                                                                                  AS density_per_1000
FROM hits

UNION ALL

-- Also break down Cluster A internally
SELECT '  └─ human capital'   AS label, total_words, hits_human_capital, ROUND(1000.0 * hits_human_capital / total_words, 2) FROM hits
UNION ALL
SELECT '  └─ workforce'        AS label, total_words, hits_workforce,     ROUND(1000.0 * hits_workforce     / total_words, 2) FROM hits
UNION ALL
SELECT '  └─ productivity'     AS label, total_words, hits_productivity,  ROUND(1000.0 * hits_productivity  / total_words, 2) FROM hits
UNION ALL
SELECT '  └─ skill*'           AS label, total_words, hits_skill,         ROUND(1000.0 * hits_skill         / total_words, 2) FROM hits
UNION ALL
SELECT '  └─ outcome*'         AS label, total_words, hits_outcome,       ROUND(1000.0 * hits_outcome       / total_words, 2) FROM hits
UNION ALL

-- And Cluster B internally
SELECT '  └─ capabilit*'       AS label, total_words, hits_capability,    ROUND(1000.0 * hits_capability    / total_words, 2) FROM hits
UNION ALL
SELECT '  └─ freedom'          AS label, total_words, hits_freedom,       ROUND(1000.0 * hits_freedom       / total_words, 2) FROM hits
UNION ALL
SELECT '  └─ agency'           AS label, total_words, hits_agency,        ROUND(1000.0 * hits_agency        / total_words, 2) FROM hits
UNION ALL
SELECT '  └─ well-being'       AS label, total_words, hits_wellbeing_hyph,ROUND(1000.0 * hits_wellbeing_hyph/ total_words, 2) FROM hits
UNION ALL
SELECT '  └─ wellbeing'        AS label, total_words, hits_wellbeing,     ROUND(1000.0 * hits_wellbeing     / total_words, 2) FROM hits
UNION ALL
SELECT '  └─ dignity'          AS label, total_words, hits_dignity,       ROUND(1000.0 * hits_dignity       / total_words, 2) FROM hits;