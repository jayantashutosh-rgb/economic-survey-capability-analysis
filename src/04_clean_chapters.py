"""
Clean extracted chapter text.

Reads:
  - data/interim/chapters/*.txt           (raw extracted chapters)

Writes:
  - data/processed/chapters/*.txt         (cleaned chapter text)
  - data/processed/cleaning_report.json   (per-chapter cleaning stats)

Cleaning rules applied:
  1. Drop pages flagged as "This page has been left blank"
  2. Remove repeated page-header lines (Economic Survey 2025-26, chapter titles)
  3. Drop lines that are clearly reversed/garbled text (chart labels)
  4. Drop standalone page-number footer lines
  5. Collapse excessive blank lines
Page markers (===== PDF PAGE N =====) are preserved for traceability.
"""

import re
import json
from pathlib import Path
from collections import Counter

INPUT_DIR = Path("data/interim/chapters")
OUTPUT_DIR = Path("data/processed/chapters")
REPORT_PATH = Path("data/processed/cleaning_report.json")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Common headers that appear on almost every page of the survey
KNOWN_HEADER_PATTERNS = [
    r"^Economic Survey 2025-26\s*$",
    r"^State of the Economy\s*$",
    r"^Fiscal Developments\s*$",
    r"^Monetary Management and Financial Intermediation\s*$",
    r"^External Sector\s*$",
    r"^Inflation\s*$",
    r"^Agriculture and Food Managmement\s*$",   # note: PDF has this typo
    r"^Agriculture and Food Management\s*$",
    r"^Services: From Stability to New Frontiers\s*$",
    r"^Industry's Next Leap: Structural Transformation and Global Integration\s*$",
    r"^Investment and Infrastructure: Strengthening Connectivity, Capacity and Competit.*$",
    r"^Environment and Climate Change\s*$",
    r"^Education and Health\s*$",
    r"^Employment and Skill Development\s*$",
    r"^Rural Development and Social Progress: From Participatiom to Partnership\s*$",   # typo in PDF
    r"^Evolution of the AI Ecosystem in India\s*$",
    r"^Urbanisation\s*$",
    r"^From Import Substitution to Strategic Resilience and Strategic Indispensability\s*$",
    r"^Building Strategic Resilience and Strategic Indispensability\s*$",
]
HEADER_RE = re.compile("|".join(KNOWN_HEADER_PATTERNS))

# Page marker we inserted during extraction
PAGE_MARKER_RE = re.compile(r"^=====\s*PDF PAGE\s+(\d+)\s*=====$")

# A line that is just a number (page-number footer)
PAGE_NUMBER_RE = re.compile(r"^\d{1,3}\s*$")

# Heuristic for reversed/garbled chart-label lines:
# - line is short (<= 25 chars)
# - mostly lowercase letters
# - ends in common reversed-word suffixes (rare letter patterns)
# Easier rule: line has no vowels at "expected" positions and contains rare letter combos.
# We use a practical heuristic: line is short + contains a reversed common word.
REVERSED_WORDS = {
    "htworg",      # growth
    "noitaflni",   # inflation
    "noitaived",   # deviation
    "etar",        # rate
    "yciloP",      # Policy
    "tnec",        # cent
    "rep",         # per
    "PDG",         # GDP
    "noitca",      # action
    "tnemyolpme",  # employment
    "tnemtsevni",  # investment
    "noitavoneR",  # Renovation
    "lairtsudni",  # industrial
    "secivres",    # services
    "noitcurtsnoc",# construction
    "noitalfni",   # inflation
    "tnemnrevog",  # government
}

def looks_reversed(line: str) -> bool:
    """Detect lines that are extracted reversed from rotated chart labels."""
    s = line.strip().lower()
    if not s or len(s) > 25:
        return False
    # If any known reversed token appears as a whole word, flag
    tokens = re.split(r"\s+", s)
    for t in tokens:
        if t in REVERSED_WORDS:
            return True
    return False


def clean_chapter_text(raw_text: str) -> tuple[str, dict]:
    """Apply cleaning rules to a single chapter's text. Returns cleaned text + stats."""
    stats = {
        "raw_lines": 0,
        "kept_lines": 0,
        "dropped_blank_pages": 0,
        "dropped_headers": 0,
        "dropped_page_numbers": 0,
        "dropped_reversed": 0,
        "raw_chars": len(raw_text),
    }

    # First, split into pages so we can drop whole "left blank" pages
    # Pages are separated by the PAGE_MARKER pattern.
    pages = []
    current_page_num = None
    current_lines = []

    for line in raw_text.splitlines():
        stats["raw_lines"] += 1
        m = PAGE_MARKER_RE.match(line.strip())
        if m:
            # Flush previous page if any
            if current_page_num is not None:
                pages.append((current_page_num, current_lines))
            current_page_num = int(m.group(1))
            current_lines = []
        else:
            current_lines.append(line)
    # Last page
    if current_page_num is not None:
        pages.append((current_page_num, current_lines))

    cleaned_chunks = []

    for page_num, lines in pages:
        page_text = "\n".join(lines)
        # Drop whole page if it's a blank marker
        if "this page has been left blank" in page_text.lower():
            stats["dropped_blank_pages"] += 1
            continue

        # Line-level cleaning within this page
        kept = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                kept.append("")   # keep blanks for now; collapse later
                continue
            if HEADER_RE.match(stripped):
                stats["dropped_headers"] += 1
                continue
            if PAGE_NUMBER_RE.match(stripped):
                stats["dropped_page_numbers"] += 1
                continue
            if looks_reversed(stripped):
                stats["dropped_reversed"] += 1
                continue
            kept.append(line)

        # Collapse multiple blank lines into a single blank line
        collapsed = []
        prev_blank = False
        for ln in kept:
            if ln.strip() == "":
                if not prev_blank:
                    collapsed.append("")
                prev_blank = True
            else:
                collapsed.append(ln)
                prev_blank = False

        if collapsed:
            cleaned_chunks.append(f"===== PDF PAGE {page_num} =====")
            cleaned_chunks.append("\n".join(collapsed))

    cleaned_text = "\n\n".join(cleaned_chunks).strip() + "\n"
    stats["kept_lines"] = cleaned_text.count("\n")
    stats["cleaned_chars"] = len(cleaned_text)
    return cleaned_text, stats


# Process each chapter file
report = {}
input_files = sorted(INPUT_DIR.glob("*.txt"))
print(f"Cleaning {len(input_files)} chapter files...\n", flush=True)

for fp in input_files:
    raw = fp.read_text(encoding="utf-8")
    cleaned, stats = clean_chapter_text(raw)

    out_path = OUTPUT_DIR / fp.name
    out_path.write_text(cleaned, encoding="utf-8")

    report[fp.name] = stats
    reduction = (1 - stats["cleaned_chars"] / stats["raw_chars"]) * 100 if stats["raw_chars"] else 0
    print(
        f"  {fp.name:<45}  "
        f"{stats['raw_chars']:>7} → {stats['cleaned_chars']:>7} chars  "
        f"({reduction:5.1f}% smaller)",
        flush=True,
    )

# Write report
REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"\nDone.", flush=True)
print(f"  Cleaned files: {OUTPUT_DIR}", flush=True)
print(f"  Report:        {REPORT_PATH}", flush=True)
