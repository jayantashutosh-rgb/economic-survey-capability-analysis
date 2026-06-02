# Findings — Capability Language in the Economic Survey 2025-26

This file records analytical findings as they emerge. Each finding lists
the question, the method, the result, and how to reproduce it from the
project files.

---

## Finding 1 — Chapter 11 (Education & Health) avoids Sen-vocabulary entirely

**Question:** Does the chapter on Education and Health, the natural ground
for Sen's capability framework, use Sen's vocabulary?

**Method:** SQL query counting hits for two vocabulary clusters within
Chapter 11 only.

**Result:**
- Cluster A — Instrumental / Human Capital (`skill`, `outcome`, `productivity`,
  `human capital`, `workforce`): 91 hits, density 4.73 per 1,000 words.
- Cluster B — Capability / Freedom / Wellbeing (`capabilit*`, `freedom`,
  `agency`, `well-being`, `dignity`): 22 hits, density 1.14 per 1,000 words.
- Zero occurrences of `capabilit*`, `freedom`, `dignity` in 19,250 words.
- Ratio 4.13 : 1 in favour of instrumental vocabulary.

**Reproduce:** `python src\run_sql.py sql\analysis\03_chapter11_framing_comparison.sql`

---

## Finding 2 — Chapter 16 uses "capability" 66 times, none in Sen's sense

**Question:** Where the Survey does use "capability" frequently (Chapter 16),
in what sense does it use the word?

**Method:** Python script extracts all occurrences of `capability` /
`capabilities` in Chapter 16 with 150-character context windows. Each
occurrence was manually classified into one of four categories:
- A: State capability (Mazzucato sense)
- B: Industrial / productive capability
- C: Human capability (Sen sense)
- D: Ambiguous

**Result (66 total occurrences):**
- A — State capability: 23
- B — Industrial / productive: 41
- C — Human capability (Sen): 0
- D — Ambiguous: 2

**Reproduce:** `python src\06_capability_context_ch16.py`
Output file: `outputs\ch16_capability_contexts.txt`

---

## Combined observation

Where the Survey is conceptually closest to Sen's framework (Chapter 11),
his core vocabulary is absent. Where the Survey uses "capability" most
heavily (Chapter 16), it does so in the state-capacity sense (Mazzucato)
or in the industrial / export sense, not in Sen's sense of substantive
human freedoms.

The Survey adopts Mazzucato's vocabulary openly (the phrase "entrepreneurial
state" appears as a section heading on page 644). It does not adopt Sen's
vocabulary, even in the chapter where it would most naturally apply.
---

## Finding 3 — The pattern holds across all human-development chapters

**Question:** Is the absence of Sen-vocabulary unique to Chapter 11, or does
it hold across all chapters dealing with human development?

**Method:** A side-by-side SQL query measures the two vocabulary clusters
(instrumental and capability) across four human-development chapters:
Ch 11 (Education/Health), Ch 12 (Employment/Skill), Ch 13 (Rural Development),
Ch 15 (Urbanisation). Combined word count: 65,673.

**Result — densities per 1,000 words:**

| Chapter | Cluster A (instrumental) | Cluster B (capability) | Sen-core only |
|---------|--------------------------|------------------------|---------------|
| 11 — Education/Health   | 4.73  | 1.14 | 0.00 |
| 12 — Employment/Skill   | 17.09 | 1.32 | 0.38 |
| 13 — Rural Development  | 3.83  | 1.28 | 0.38 |
| 15 — Urbanisation       | 3.09  | 0.27 | 0.07 |

Cluster A includes: `human capital`, `workforce`, `productivity`, `skill*`, `outcome*`.
Cluster B includes: `capabilit*`, `freedom`, `agency`, `wellbeing`, `well-being`, `dignity`.
Sen-core is the strict subset: `capabilit*`, `freedom`, `dignity`.

Note: Cluster A density in Ch 12 (17.09) is inflated by the chapter's
own subject — "skill" appears 40+ times because the chapter is titled
"Employment and Skill Development." This is acknowledged but does not
weaken the overall pattern: in every chapter, instrumental vocabulary
dominates by a wide margin.

**Reproduce:** `python src\run_sql.py sql\analysis\04_framing_comparison_social_chapters.sql`

---

## Finding 4 — The few Sen-core hits across these chapters are rhetorical, not framework

**Question:** Cluster B in Ch 12, 13, 15 contains 12 occurrences of
Sen-core words (capability/freedom/dignity). Are they used in Sen's sense?

**Method:** Python script extracts each occurrence with a 150-character
context window. Manual classification into four categories
(A=state, B=industrial, C=Sen-human, D=ambiguous).

**Result (12 occurrences classified):**
- A — State/institutional capability:   3
- B — Industrial/productive capability: 4
- C — Sen-sense human capability:       4
- D — Ambiguous/inverted:               1

All four C-classified entries are uses of the word **dignity**.
None use `capability` or `freedom` in Sen's sense.

The four "Sen-adjacent" dignity invocations:
- Ch 13 p.564 — "fairness, dignity, and equal rights" (boilerplate phrase justifying inclusive development)
- Ch 13 p.592 — same boilerplate phrase (Viksit Bharat context)
- Ch 13 p.596 — "safety and dignity of sanitation workers" (scheme justification — NAMASTE)
- Ch 15 p.676 — "cities that offer dignity... will retain and attract them" (instrumental — citizens framed as mobile labour)

In none of these four cases is dignity used as a structural concept
in Sen's sense — as an irreducible element of substantive freedom.
All four are either rhetorical openers, scheme justifications, or
instrumental claims about workforce retention.

**Reproduce:** `python src\07_sen_core_context_social_chapters.py`
Output file: `outputs\sen_core_contexts_social_chapters.txt`

---

## Combined empirical position after Findings 1–4

Across 89,681 words spanning the five chapters most relevant to human
development (Ch 11, 12, 13, 15) and to the State's role in development
(Ch 16):

- `capability` / `capabilities` is used in Sen's sense: **0 times**.
- `freedom` is used in Sen's sense: **0 times**.
- `dignity` appears in Sen-adjacent uses: **4 times**, all rhetorical.
- The dominant vocabulary in every chapter is instrumental
  (skill, outcome, productivity, human capital, workforce) or
  state-capacity-oriented (institutional, regulatory, strategic).

The Survey adopts Mazzucato's vocabulary openly (the phrase
"entrepreneurial state" appears as a section heading on page 644 and
"state capability" is used dozens of times in Chapter 16). It does not
adopt Sen's vocabulary, even in domains where Sen's framework is most
directly applicable.

This is the central empirical finding of the project so far.
---

## Finding 5 — Citizen framing: input vs end (document-wide)

**Question:** Does the Survey refer to citizens primarily as inputs to growth
(worker, beneficiary, consumer, taxpayer, human capital) or as ends in
themselves (citizen, individual, person)?

**Method:** SQL queries across all 17 chapters, counting two noun groups.
A first version included `household` and `family` in the END group;
a stricter version restricted END to clearly moral/agentive nouns
(`citizen`, `individual`, `person`).

**Result — strict version, key chapters:**

| Chapter | density_input | density_end | input_to_end_ratio |
|---------|---------------|-------------|--------------------|
| 11 — Education/Health   | 2.13 | 1.04 | 2.05 |
| 12 — Employment/Skill   | 16.87 | 2.80 | 6.02 |
| 13 — Rural Development  | 3.15 | 3.45 | 0.91 |
| 15 — Urbanisation       | 1.88 | 2.62 | 0.72 |
| 16.1 — Strategic Resilience-1 | 0.82 | 0.59 | 1.40 |
| 16.2 — Strategic Resilience-2 | 1.23 | 3.42 | 0.36 |

Most chapters are input-dominant (ratio > 1). Four chapters are end-dominant:
Rural Development (0.91), Urbanisation (0.72), Environment (0.57),
and Strategic Resilience-2 (0.36).

The result is mixed at the vocabulary-count level: the Survey is not
uniformly input-dominant. Two chapters in particular — Strategic
Resilience-2 and Rural Development — show stronger end-framing than
expected.

**Caveat acknowledged:** including or excluding `household` / `family`
changes results substantially. The strict version (presented above)
is reported as the more defensible test of Sen-style citizen-as-end
framing.

**Reproduce:**
- Original: `python src\run_sql.py sql\analysis\05_citizen_framing_by_chapter.sql`
- Strict:   `python src\run_sql.py sql\analysis\06_citizen_framing_strict.sql`

---

## Finding 6 — Chapter 16.2: where citizens appear most, they are framed as duty-bearers, not agents

**Question:** Strategic Resilience-2 (Ch 16.2) shows the strongest end-framing
in the strict citizen-framing query (ratio 0.36). Is this evidence that
the Survey treats citizens in Sen's sense in that chapter, or is the framing
oriented differently?

**Method:** Python script extracts every occurrence of `citizen(s)`,
`individual(s)`, and `person(s)` in Chapter 16.2 with a 180-character
context window. Each occurrence was manually classified into:
- S — Sen-adjacent (citizen as bearer of rights / agency / expectations)
- D — Duty-oriented (citizen as norm-internaliser / compliance subject)
- P — Partnership / co-production with state
- N — Neutral / structural reference

**Result (44 occurrences):**

| Term | Total | S — Sen-adjacent | D — Duty | P — Partnership | N — Neutral |
|------|-------|------------------|----------|------------------|-------------|
| citizen(s) | 31 | 13 | 11 | 2 | 5 |
| individual(s) | 13 | 0 | 4 | 0 | 9 |
| **Combined** | **44** | **13 (30%)** | **15 (34%)** | **2 (5%)** | **14 (32%)** |

The word `individual` — central to Sen's vocabulary — is used 13 times
and not once in Sen's sense.

Even the 13 entries classified as Sen-adjacent are largely transactional:
they refer to citizens as service recipients ("citizen-centric service")
or as the subjects of obligations the State must meet, rather than as
agents of substantive freedom. Genuine Sen-adjacent uses (citizen as
rights-bearer) cluster around RTI and accountability passages on pages
711–713 and amount to roughly 5–6 of the 13 entries.

The Survey's most sustained theoretical statement on citizens occupies
pages 727–731 under the heading *"Citizens, norms, and the social
foundations of capability"*. The framing in that section is consistently
disciplinary:
- *"citizens internalise compliance"*
- *"citizens accepting delayed gratification"*
- *"responsible citizens rather than short-term beneficiaries"*
- *"citizens... treat learning as a habit, respect physical and technical work"*

This is the conceptual inverse of Sen's framework. In Sen, the State's
role is to expand citizens' capabilities. Here, the citizen's role is
to develop habits and norms that reduce the State's enforcement burden
and enable State capacity.

**Reproduce:** `python src\08_citizen_end_context_ch16_2.py`
Output file: `outputs\ch16_2_citizen_contexts.txt`

---

## Updated empirical position after Findings 1–6

The Survey speaks of citizens often. But the framing is consistently
either instrumental (citizen as worker, consumer, beneficiary, input to
growth) or disciplinary (citizen as norm-internaliser, duty-bearer,
co-producer of State capacity). Neither framing matches Sen's
substantive-freedom framework, in which citizens are the bearers of
capabilities and the State exists to expand those capabilities.

The single most explicit theoretical claim about state-citizen relations
in the document — the "social foundations of capability" section in
Chapter 16.2 — inverts Sen's framework directly: citizens must change
to enable the State, rather than the State to enable citizens.

Combined with Findings 1–4 (Sen-vocabulary absent in human-development
chapters; Mazzucato vocabulary openly adopted), this establishes the
project's central empirical claim:

> The Economic Survey 2025-26 selectively adopts Mazzucato's vocabulary
> and conceptual structure for state-led development while leaving
> Sen's capability framework unused, even in domains where it would
> most naturally apply. Where the document discusses citizens at
> length, it does so within a disciplinary or instrumental register,
> not within Sen's register of substantive freedom.