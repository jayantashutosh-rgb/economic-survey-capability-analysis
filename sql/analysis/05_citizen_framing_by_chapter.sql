-- =============================================================================
-- Citizen framing: input vs end
-- =============================================================================
-- Question:
--   In Sen's framework, the citizen is the END of development; in Mazzucato's
--   and in human-capital theory, the citizen is an INPUT to growth.
--   Does the Survey refer to citizens primarily as inputs (worker, beneficiary,
--   consumer, taxpayer, human capital) or as ends (citizen, individual, person)?
--
-- Method:
--   For each chapter, count hits for two word groups:
--     Group 1 — Citizen as INPUT (instrumental nouns)
--     Group 2 — Citizen as END (constitutive nouns)
--   Express as density per 1,000 words for cross-chapter comparison.
--
-- Caveat:
--   Word counting cannot resolve context. Words like "people" and "household"
--   are neutral and can appear in either framing. We restrict each group
--   to nouns whose default register is reasonably clear.
-- =============================================================================

WITH chapter_text AS (
    SELECT
        c.chapter_id,
        c.slug,
        SUM(p.word_count) AS total_words,
        LOWER(GROUP_CONCAT(p.text, ' ')) AS combined_text
    FROM chapters c
    JOIN pages p ON p.chapter_id = c.chapter_id
    GROUP BY c.chapter_id, c.slug
),
hits AS (
    SELECT
        chapter_id,
        slug,
        total_words,

        -- Group 1: Citizen as INPUT
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'worker', '')))         / 6  AS h_worker,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'workforce', '')))      / 9  AS h_workforce,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'labour', '')))         / 6  AS h_labour,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'human capital', '')))  / 13 AS h_human_capital,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'human resource', ''))) / 14 AS h_human_resource,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'beneficiar', '')))     / 10 AS h_beneficiary,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'consumer', '')))       / 8  AS h_consumer,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'taxpayer', '')))       / 8  AS h_taxpayer,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'manpower', '')))       / 8  AS h_manpower,

        -- Group 2: Citizen as END
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'citizen', '')))        / 7  AS h_citizen,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'individual', '')))     / 10 AS h_individual,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'household', '')))      / 9  AS h_household,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'family', '')))         / 6  AS h_family,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'families', '')))       / 8  AS h_families
    FROM chapter_text
)

SELECT
    chapter_id,
    slug,
    total_words,

    -- Group 1 (input) total + density
    (h_worker + h_workforce + h_labour + h_human_capital + h_human_resource
     + h_beneficiary + h_consumer + h_taxpayer + h_manpower)                                     AS input_hits,
    ROUND(1000.0 * (h_worker + h_workforce + h_labour + h_human_capital + h_human_resource
     + h_beneficiary + h_consumer + h_taxpayer + h_manpower) / total_words, 2)                   AS density_input,

    -- Group 2 (end) total + density
    (h_citizen + h_individual + h_household + h_family + h_families)                              AS end_hits,
    ROUND(1000.0 * (h_citizen + h_individual + h_household + h_family + h_families)
        / total_words, 2)                                                                         AS density_end,

    -- Ratio (input / end)
    CASE
        WHEN (h_citizen + h_individual + h_household + h_family + h_families) = 0 THEN NULL
        ELSE ROUND(
            1.0 * (h_worker + h_workforce + h_labour + h_human_capital + h_human_resource
                 + h_beneficiary + h_consumer + h_taxpayer + h_manpower)
            / (h_citizen + h_individual + h_household + h_family + h_families), 2)
    END                                                                                           AS input_to_end_ratio
FROM hits
ORDER BY chapter_id;