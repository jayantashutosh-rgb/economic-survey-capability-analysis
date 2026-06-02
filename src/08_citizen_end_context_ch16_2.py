"""
Find every occurrence of citizen-as-end vocabulary
(citizen/individual/person) in Chapter 16.2 and print the surrounding
context. Manual classification will determine whether the framing is:
  - genuinely Sen-adjacent (citizens as bearers of capabilities/rights/agency)
  - or rhetorical / state-oriented (citizens as duty-bearers / instruments
    of state purpose)

Output: outputs/ch16_2_citizen_contexts.txt
"""

import re
import sqlite3
from pathlib import Path

DB_PATH = Path("db/survey.db")
OUTPUT_PATH = Path("outputs/ch16_2_citizen_contexts.txt")
CONTEXT_CHARS = 180
TARGET_CHAPTER = 16.2

PATTERNS = {
    "citizen":    re.compile(r"\bcitizen(?:s)?\b",    re.IGNORECASE),
    "individual": re.compile(r"\bindividual(?:s)?\b", re.IGNORECASE),
    "person":     re.compile(r"\bperson(?:s)?\b",     re.IGNORECASE),
}


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT pdf_page, text FROM pages WHERE chapter_id = ? ORDER BY pdf_page;",
        (TARGET_CHAPTER,),
    )
    rows = cur.fetchall()
    conn.close()

    matches = []
    for pdf_page, text in rows:
        if not text:
            continue
        for label, pattern in PATTERNS.items():
            for m in pattern.finditer(text):
                start = max(0, m.start() - CONTEXT_CHARS)
                end = min(len(text), m.end() + CONTEXT_CHARS)
                snippet = text[start:end].replace("\n", " ").strip()
                matches.append({
                    "pdf_page": pdf_page,
                    "term": label,
                    "word": m.group(0),
                    "snippet": snippet,
                })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(f"Chapter 16.2 — citizen / individual / person occurrences\n")
        f.write(f"Total occurrences: {len(matches)}\n")
        f.write("=" * 80 + "\n\n")

        # Group by term
        for term in PATTERNS:
            term_matches = [m for m in matches if m["term"] == term]
            f.write(f"--- {term} ({len(term_matches)} occurrences) ---\n\n")
            for i, m in enumerate(term_matches, 1):
                f.write(f"[{i:>2}] Page {m['pdf_page']}  — \"{m['word']}\"\n")
                f.write(f"     ...{m['snippet']}...\n\n")
            f.write("\n")

    print(f"Found {len(matches)} occurrences.")
    print(f"Output: {OUTPUT_PATH}")
    for term in PATTERNS:
        count = sum(1 for m in matches if m["term"] == term)
        print(f"  {term}: {count}")


if __name__ == "__main__":
    main()