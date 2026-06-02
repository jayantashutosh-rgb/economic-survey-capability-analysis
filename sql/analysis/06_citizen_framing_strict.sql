-- =============================================================================
-- Citizen framing — strict version
-- =============================================================================
-- Question:
--   Does the input-dominant framing of citizens hold up under a stricter
--   definition of "citizen as end"?
--
-- Motivation:
--   The first version (05_citizen_framing_by_chapter.sql) included
--   `household` and `family` in Group 2. These are commonly statistical
--   units (e.g. "rural households", "farm households") rather than
--   moral subjects in Sen's sense. Including them inflated the end-side
--   count in several chapters, particularly Rural Development.
--
-- Stricter definition:
--   Group 2 retains only nouns that unambiguously denote moral/agentive
--   subjects in development literature: citizen, individual, person.
--
-- Group 1 (INPUT) is unchanged.
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

        -- Group 1: Citizen as INPUT (unchanged from prior query)
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'worker', '')))         / 6  AS h_worker,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'workforce', '')))      / 9  AS h_workforce,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'labour', '')))         / 6  AS h_labour,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'human capital', '')))  / 13 AS h_human_capital,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'human resource', ''))) / 14 AS h_human_resource,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'beneficiar', '')))     / 10 AS h_beneficiary,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'consumer', '')))       / 8  AS h_consumer,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'taxpayer', '')))       / 8  AS h_taxpayer,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'manpower', '')))       / 8  AS h_manpower,

        -- Group 2: Citizen as END (strict — moral/agentive nouns only)
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'citizen', '')))        / 7  AS h_citizen,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'individual', '')))     / 10 AS h_individual,
        (LENGTH(combined_text) - LENGTH(REPLACE(combined_text, 'person', '')))         / 6  AS h_person
    FROM chapter_text
)

SELECT
    chapter_id,
    slug,
    total_words,

    -- INPUT totals
    (h_worker + h_workforce + h_labour + h_human_capital + h_human_resource
     + h_beneficiary + h_consumer + h_taxpayer + h_manpower)                                      AS input_hits,
    ROUND(1000.0 * (h_worker + h_workforce + h_labour + h_human_capital + h_human_resource
     + h_beneficiary + h_consumer + h_taxpayer + h_manpower) / total_words, 2)                    AS density_input,

    -- END totals (strict)
    (h_citizen + h_individual + h_person)                                                          AS end_hits,
    ROUND(1000.0 * (h_citizen + h_individual + h_person) / total_words, 2)                         AS density_end,

    -- Ratio (input / end)
    CASE
        WHEN (h_citizen + h_individual + h_person) = 0 THEN NULL
        ELSE ROUND(
            1.0 * (h_worker + h_workforce + h_labour + h_human_capital + h_human_resource
                 + h_beneficiary + h_consumer + h_taxpayer + h_manpower)
            / (h_citizen + h_individual + h_person), 2)
    END                                                                                            AS input_to_end_ratio
FROM hits
ORDER BY chapter_id;