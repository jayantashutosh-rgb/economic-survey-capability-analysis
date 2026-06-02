"""
Find every occurrence of Sen's core vocabulary (capability, freedom, dignity)
in chapters 12, 13, and 15 — and print surrounding context.

Output goes to: outputs/sen_core_contexts_social_chapters.txt

The four pages-of-target are:
  Ch 12 — Employment and Skill Development
  Ch 13 — Rural Development and Social Progress
  Ch 15 — Urbanisation

(Chapter 11 returned zero hits for these terms, so it is excluded.)
"""

import re
import sqlite3
from pathlib import Path

DB_PATH = Path("db/survey.db")
OUTPUT_PATH = Path("outputs/sen_core_contexts_social_chapters.txt")
CONTEXT_CHARS = 150
TARGET_CHAPTERS = (12, 13, 15)

# Three Sen-core word patterns, matched as whole words, case-insensitive
PATTERNS = {
    "capability":  re.compile(r"\bcapabilit(?:y|ies)\b", re.IGNORECASE),
    "freedom":     re.compile(r"\bfreedom\b",            re.IGNORECASE),
    "dignity":     re.compile(r"\bdignity\b",            re.IGNORECASE),
}


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    placeholders = ",".join("?" for _ in TARGET_CHAPTERS)
    cur.execute(
        f"""
        SELECT pdf_page, chapter_id, text
        FROM pages
        WHERE chapter_id IN ({placeholders})
        ORDER BY chapter_id, pdf_page;
        """,
        TARGET_CHAPTERS,
    )
    rows = cur.fetchall()
    conn.close()

    matches = []
    for pdf_page, chapter_id, text in rows:
        if not text:
            continue
        for label, pattern in PATTERNS.items():
            for m in pattern.finditer(text):
                start = max(0, m.start() - CONTEXT_CHARS)
                end = min(len(text), m.end() + CONTEXT_CHARS)
                snippet = text[start:end].replace("\n", " ").strip()
                matches.append({
                    "pdf_page": pdf_page,
                    "chapter_id": chapter_id,
                    "term": label,
                    "word": m.group(0),
                    "snippet": snippet,
                })

    # Group by chapter for readable output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("Sen-core vocabulary in chapters 12, 13, 15\n")
        f.write(f"Total occurrences: {len(matches)}\n")
        f.write("=" * 80 + "\n\n")

        for ch in TARGET_CHAPTERS:
            chap_matches = [m for m in matches if m["chapter_id"] == ch]
            f.write(f"--- Chapter {ch} ({len(chap_matches)} occurrences) ---\n\n")
            for i, m in enumerate(chap_matches, 1):
                f.write(f"[{i:>2}] Page {m['pdf_page']}  — \"{m['word']}\" ({m['term']})\n")
                f.write(f"     ...{m['snippet']}...\n\n")
            f.write("\n")

    print(f"Found {len(matches)} occurrences.")
    print(f"Output: {OUTPUT_PATH}")
    # Print per-chapter counts to console
    for ch in TARGET_CHAPTERS:
        count = sum(1 for m in matches if m["chapter_id"] == ch)
        print(f"  Chapter {ch}: {count}")


if __name__ == "__main__":
    main()