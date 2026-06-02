-- =============================================================================
-- Framing comparison across all "human-development" chapters
-- =============================================================================
-- Question:
--   Finding 1 showed Chapter 11 (Education/Health) avoids Sen-vocabulary.
--   Is this pattern unique to Chapter 11, or does it hold across all chapters
--   that deal with human development (employment, rural welfare, urban life)?
--
-- Method:
--   Count two competing vocabulary clusters across four chapters:
--     - Ch 11: Education and Health
--     - Ch 12: Employment and Skill Development
--     - Ch 13: Rural Development and Social Progress
--     - Ch 15: Urbanisation
--
--   Side-by-side comparison shows whether the instrumental-vs-capability
--   asymmetry is systematic or chapter-specific.
-- =============================================================================

WITH target_pages AS (
    SELECT
        p.chapter_id,
        c.slug,
        p.word_count,
        LOWER(p.text) AS text_lower
    FROM pages p
    JOIN chapters c ON c.chapter_id = p.chapter_id
    WHERE p.chapter_id IN (11, 12, 13, 15)
),
hits AS (
    SELECT
        chapter_id,
        slug,
        SUM(word_count) AS total_words,

        -- Cluster A: Instrumental / Human Capital
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'human capital', '')))   / 13) AS h_human_capital,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'workforce', '')))       / 9)  AS h_workforce,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'productivity', '')))    / 12) AS h_productivity,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'skill', '')))           / 5)  AS h_skill,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'outcome', '')))         / 7)  AS h_outcome,

        -- Cluster B: Capability / Freedom / Wellbeing
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'capabilit', '')))       / 9)  AS h_capability,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'freedom', '')))         / 7)  AS h_freedom,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'agency', '')))          / 6)  AS h_agency,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'well-being', '')))      / 10) AS h_wellbeing_hyph,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'wellbeing', '')))       / 9)  AS h_wellbeing,
        SUM((LENGTH(text_lower) - LENGTH(REPLACE(text_lower, 'dignity', '')))         / 7)  AS h_dignity
    FROM target_pages
    GROUP BY chapter_id, slug
)

SELECT
    chapter_id,
    slug,
    total_words,
    -- Cluster A totals
    (h_human_capital + h_workforce + h_productivity + h_skill + h_outcome) AS cluster_a_hits,
    ROUND(1000.0 * (h_human_capital + h_workforce + h_productivity + h_skill + h_outcome) / total_words, 2) AS density_a,
    -- Cluster B totals
    (h_capability + h_freedom + h_agency + h_wellbeing_hyph + h_wellbeing + h_dignity) AS cluster_b_hits,
    ROUND(1000.0 * (h_capability + h_freedom + h_agency + h_wellbeing_hyph + h_wellbeing + h_dignity) / total_words, 2) AS density_b,
    -- Sen-core hits only (capability + freedom + dignity)
    (h_capability + h_freedom + h_dignity) AS sen_core_hits,
    ROUND(1000.0 * (h_capability + h_freedom + h_dignity) / total_words, 2) AS density_sen_core
FROM hits
ORDER BY chapter_id;