"""
Build chapters.json — the ground-truth map of chapter page boundaries.

This is a one-time script. It produces data/interim/chapters.json
which downstream extraction and analysis scripts will read.

Page boundaries were identified manually from data/interim/page_first_lines.txt
by scanning for the 'CHAPTE R' pattern in the PDF.
"""

import json
from pathlib import Path

OUTPUT_PATH = Path("data/interim/chapters.json")

# Each entry: chapter id, short slug, full title, start page (PDF physical page)
# end_page is computed below as (next_chapter_start - 1)
chapters_raw = [
    (1,    "state_of_economy",       "State of the Economy: Pushing the Growth Frontier",                                 52),
    (2,    "fiscal_developments",    "Fiscal Developments: Anchoring Stability Through Credible Consolidation",           88),
    (3,    "monetary_management",    "Monetary Management and Financial Intermediation: Refining the Regulatory Touch",   130),
    (4,    "external_sector",        "External Sector: Playing the Long Game",                                            196),
    (5,    "inflation",              "Inflation: Tamed and Anchored",                                                     254),
    (6,    "agriculture",            "Agriculture and Food Management: Raising Productivity, Securing Income",            276),
    (7,    "services",               "Services: From Stability to New Frontiers",                                         310),
    (8,    "industry",               "Industry's Next Leap: Structural Transformation and Global Integration",            344),
    (9,    "investment_infra",       "Investment and Infrastructure: Strengthening Connectivity, Capacity, Competitiveness", 390),
    (10,   "environment_climate",    "Environment and Climate Change: Building a Resilient, Competitive India",           428),
    (11,   "education_health",       "Education and Health: What Works and What's Next",                                  470),
    (12,   "employment_skill",       "Employment and Skill Development: Getting Skilling Right",                          518),
    (13,   "rural_development",      "Rural Development and Social Progress: From Participation to Partnership",          564),
    (14,   "ai_ecosystem",           "Evolution of the AI Ecosystem in India: The Way Forward",                           600),
    (15,   "urbanisation",           "Urbanisation: Making India's Cities Work for Its Citizens",                         638),
    (16.1, "strategic_resilience_1", "From Import Substitution to Strategic Resilience and Strategic Indispensability",   678),
    (16.2, "strategic_resilience_2", "Building Strategic Resilience: The Role of State, Private Sector and Citizens",     704),
]

# Total PDF pages (we confirmed earlier)
LAST_PDF_PAGE = 740

# Build the structured list with end_page derived from next chapter's start_page
chapters = []
for idx, (cid, slug, title, start) in enumerate(chapters_raw):
    # next chapter's start page (or LAST_PDF_PAGE if this is the last chapter)
    if idx + 1 < len(chapters_raw):
        next_start = chapters_raw[idx + 1][3]
        end = next_start - 1
    else:
        end = LAST_PDF_PAGE

    chapters.append({
        "chapter_id": cid,
        "slug": slug,
        "title": title,
        "start_page": start,
        "end_page": end,
        "page_count": end - start + 1
    })

# Make sure output directory exists
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Write JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(chapters, f, indent=2, ensure_ascii=False)

# Print a summary
print(f"Wrote {len(chapters)} chapters to {OUTPUT_PATH}\n")
print(f"{'Ch':>5} {'Slug':<25} {'Pages':>10} {'Count':>6}")
print("-" * 55)
for c in chapters:
    print(f"{str(c['chapter_id']):>5} {c['slug']:<25} {c['start_page']:>4}–{c['end_page']:<4} {c['page_count']:>6}")
    