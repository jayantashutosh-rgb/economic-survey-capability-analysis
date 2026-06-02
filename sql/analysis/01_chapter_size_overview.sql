-- =============================================================================
-- Chapter-level size overview
-- =============================================================================
-- Question: How much text content does each chapter contain?
--
-- Why this matters:
-- Word/page count gives a baseline sense of chapter weight in the document.
-- A chapter that is twice as long has twice the "speaking time" in the
-- Survey's narrative — this is itself an editorial signal of importance.
-- =============================================================================

SELECT
    c.chapter_id,
    c.slug,
    c.page_count,
    SUM(p.word_count)  AS total_words,
    SUM(p.char_count)  AS total_chars,
    ROUND(AVG(p.word_count), 0) AS avg_words_per_page
FROM chapters c
JOIN pages p ON p.chapter_id = c.chapter_id
GROUP BY c.chapter_id, c.slug, c.page_count
ORDER BY total_words DESC;