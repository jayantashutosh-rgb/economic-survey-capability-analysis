# Methodology

This document records the analytical methods used in the project, the
choices made at each step, and the reasoning behind those choices.
The aim is to make every finding in `findings.md` reproducible and to
let a reviewer judge for themselves whether the evidence supports the
conclusions.

---

## 1. Source and scope

**Source document:** Economic Survey 2025-26, Government of India,
published January 2026. Single PDF, 740 pages, downloaded from the
official Ministry of Finance portal.

**Scope:**
- Only the body chapters are analysed (pages 52 to 740).
- Front matter (preface, acknowledgements, abbreviations, lists of
  tables/charts/boxes) is excluded.
- Chapter 16 has two parts (Part I and Part II); they are stored
  separately as chapter_id 16.1 and 16.2.

No other external data source is used. All claims come from the
uploaded PDF.

---

## 2. Data preparation pipeline

The project follows a standard extract-clean-load pipeline.

### 2.1 Extraction

Tool: `pdfplumber` (chosen over `pypdf` and `PyMuPDF` because it is
layout-aware and handles multi-column government PDFs better).

Each chapter is extracted into a single text file with page markers
of the form `===== PDF PAGE N =====`. The markers preserve the link
back to the source page, which matters for two reasons: (a) every
analytical claim can be traced to a specific page; (b) the database
uses these markers to split chapter files into per-page rows.

### 2.2 Cleaning (light)

Two cleaning approaches were considered: aggressive (strip tables,
charts, footers, footnotes) and targeted (remove only clear noise).
The targeted approach was chosen because:

- The project measures language patterns. Stripping tables can remove
  legitimate text that includes keywords of interest.
- Aggressive cleaning is irreversible; mistakes cannot be undone
  without re-extracting.
- The database stores text at page-level granularity, so noise can
  also be filtered at query time.

What the cleaning step removes:

- Pages containing the phrase "this page has been left blank"
- Repeating page-header lines (chapter title, "Economic Survey 2025-26")
- Standalone page-number footers
- Recognisable reversed-text fragments from rotated chart labels
- Excessive blank lines

What it preserves:

- All body prose
- Footnotes and citations
- Tables (text form)
- All paragraph numbering (1.1, 1.2, etc.)

Average size reduction across chapters: 1–4 percent.

### 2.3 Database

Schema: two tables, `chapters` and `pages`, linked by `chapter_id`.
The schema is defined in `sql/01_schema.sql`.

Granularity choice: **page-level**. One row per PDF page (676 rows
total after cleaning, from a raw count of 689). Page-level was chosen
over chapter-level or paragraph-level because:

- Chapter-level loses all locational information.
- Paragraph-level requires reliable paragraph detection, which is
  noisy in this PDF (numbering is inconsistent across boxes and
  tables).
- Page-level matches the project's analytical needs (chapter-aggregated
  queries plus the ability to trace any hit back to a single page).

The build script (`src/05_build_database.py`) is idempotent: it drops
existing tables, applies the schema, and reloads from cleaned files.
A reproducibility check was performed by deleting and rebuilding the
database — counts remained identical (17 chapters, 676 pages,
252,587 words).

---

## 3. Vocabulary cluster selection

Five vocabulary clusters were defined for the document-wide density
query (`sql/analysis/02_keyword_density_by_chapter.sql`):

| Cluster | Terms | Rationale |
|---------|-------|-----------|
| Growth / output | `growth` | The Survey's most frequent keyword; baseline for comparison. |
| Capability | `capabilit*` | Sen and Nussbaum's core term. The presence or absence of this word in human-development chapters is itself the central question. |
| State (Mazzucato) | `state capacity`, `entrepreneurial` | Mazzucato's signature vocabulary. The phrase "entrepreneurial state" appears in the Survey's own section heading (page 644). |
| Welfare | `welfare`, `poverty` | Tests whether welfare-language is treated as a distinct register from capability-language. |
| Market | `market` | Counter-cluster to capture market-oriented framing. |

For the Chapter 11 head-to-head test
(`sql/analysis/03_chapter11_framing_comparison.sql`) and the
cross-chapter version
(`sql/analysis/04_framing_comparison_social_chapters.sql`), two
narrower clusters were used:

**Cluster A — Instrumental / Human Capital:** `human capital`,
`workforce`, `productivity`, `skill`, `outcome`.

These are the standard vocabulary of human-capital theory (Schultz,
Becker). They frame people as inputs to growth.

**Cluster B — Capability / Freedom / Wellbeing:** `capabilit*`,
`freedom`, `agency`, `well-being` (with and without hyphen), `dignity`.

These are the standard vocabulary of the capability approach (Sen,
Nussbaum). They frame people as bearers of substantive freedom.

**Sen-core subset:** `capabilit*`, `freedom`, `dignity` — the three
words that Sen and Nussbaum use as load-bearing terms. Used as the
strictest test.

### 3.1 Why these specific words?

The choices are biased toward terms whose technical-academic register
is unambiguous. `freedom` and `capability` are signature Sen terms
that an economist citing Sen would use; `human capital` and `workforce`
are signature instrumental terms that a Becker-Schultz analysis would
use. Less unambiguous terms (`people`, `household`, `family`) were
either dropped from the strict version or held back from the cluster
entirely.

### 3.2 What was not included

- `agency` is included in Cluster B (broad) but excluded from Sen-core
  because it has overlapping non-Sen uses ("agency problem" in
  principal-agent theory).
- `human capabilities` (the plural) is captured by `capabilit*`.
- `freedoms` is captured by `freedom`.
- `well-being` and `wellbeing` are both included because the Survey
  uses both spellings.

---

## 4. Counting method

Two counting methods are used in the project:

### 4.1 SQL substring count
This is permissive — it counts every substring occurrence, including
inside larger words. For example, `capabilit` matches `capability`,
`capabilities`, and would also match `incapability` if such a word
appeared.

Used in: all `sql/analysis/*.sql` files.

### 4.2 Python regex with word boundaries

```python
re.compile(r"\bcapabilit(?:y|ies)\b", re.IGNORECASE)
```

This is strict — only matches `capability` or `capabilities` as
whole words.

Used in: context-extraction scripts (`src/06_*.py`, `src/07_*.py`,
`src/08_*.py`).

### 4.3 When the two disagree

For Chapter 16, the SQL substring count returned 66 hits for
`capabilit`. The Python regex returned the same 66.

For Chapter 13's Sen-core query, SQL returned 5 hits. Python returned 4.
The discrepancy is acknowledged in `findings.md` and the Python count
is used as the canonical figure, since whole-word matching is the
research-grade standard.

---

## 5. Manual classification

Two findings (Finding 2 and Finding 6) involved manual classification
of context windows. The protocol was:

1. A Python script extracted every occurrence of the target word(s)
   in the target chapter, with a 150- or 180-character context window
   on each side.
2. The full set of occurrences was written to a single output file
   in `outputs/`.
3. Each occurrence was read in context and assigned to one of four
   categories.

### 5.1 Categories for "capability" in Chapter 16 (Finding 2)

- **A — State capability** (Mazzucato): institutional, regulatory,
  bureaucratic capacity. Examples: "institutional capability",
  "the State... toward capability".
- **B — Industrial / productive**: manufacturing, export,
  technological, productive. Examples: "manufacturing capability",
  "export capability".
- **C — Human capability (Sen)**: capability of a person to do or
  be something. Example phrasing that would qualify:
  "citizens' capabilities", "expansion of people's capabilities".
- **D — Ambiguous**: cannot be assigned to A, B, or C without
  stretching.

### 5.2 Categories for citizen-end words in Chapter 16.2 (Finding 6)

- **S — Sen-adjacent**: citizen as rights-bearer, agent, or holder
  of expectations on the State.
- **D — Duty-oriented**: citizen as norm-internaliser, compliance
  subject, duty-bearer.
- **P — Partnership**: citizen as co-producer with the State.
- **N — Neutral / structural**: descriptive use with no normative
  framing (footnotes, chart captions, generic phrases).

### 5.3 Subjectivity

Manual classification involves judgement. To mitigate this:

- Each entry includes the exact context window in the source output
  file. A reviewer can re-classify and check.
- The classification key is explicit (above), not implicit.
- Ambiguous cases are recorded as ambiguous (Category D / N) rather
  than being forced into a stronger category.
- A second-pass spot-check was performed on entries 15, 35, 48, 56,
  65 in the Chapter 16 set.

The classification files are committed:
- `outputs/ch16_capability_contexts.txt` (66 entries)
- `outputs/sen_core_contexts_social_chapters.txt` (12 entries)
- `outputs/ch16_2_citizen_contexts.txt` (44 entries)

---

## 6. The citizen-framing query — strict version

A first version of the citizen-framing query
(`sql/analysis/05_citizen_framing_by_chapter.sql`) included
`household` and `family` in the END group. Inspecting the data showed
that these nouns are dominantly used as statistical units in this
document ("rural households", "farm households"), not as moral
subjects.

A stricter version (`sql/analysis/06_citizen_framing_strict.sql`)
restricts END to `citizen`, `individual`, `person`. The strict version
is the one cited in Finding 5.

Both queries are retained in the repository so that the effect of the
choice is visible.

---

## 7. Limitations

The following limitations should be acknowledged when using these
findings:

1. **Absence of word is not absence of concept.** The Survey may
   implement parts of Sen's framework without using Sen's vocabulary.
   The project's claims are about vocabulary and framing, not about
   underlying policy substance.

2. **No comparison baseline.** The project does not compare the
   2025-26 Survey to earlier Surveys, nor to other policy documents.
   It is possible (but untested here) that the absence of Sen-vocabulary
   is a long-standing feature of this document series.

3. **Chart text noise.** A small amount of reversed text from rotated
   chart labels survives the cleaning step. It does not affect keyword
   counts for the terms used in this project (the reversed fragments
   are short, non-English-shaped strings).

4. **Manual classification is single-coder.** Inter-rater reliability
   was not measured. Categories are exposed (Section 5) so a second
   coder can re-rate.

5. **Page-level granularity, not paragraph-level.** Some occurrences
   span a page break; the context-extraction script handles this by
   working on full chapter text rather than per-page text.

6. **Substring counts in SQL are slightly permissive** by design.
   Where exact whole-word counts matter, the Python regex versions
   are the canonical figures.

---

## 8. Reproducibility

The full pipeline is reproducible end-to-end:
Dependencies are pinned in `requirements.txt`. The cleaned text files
are committed under `data/processed/chapters/`. The raw PDF is not
committed (it is hosted externally).