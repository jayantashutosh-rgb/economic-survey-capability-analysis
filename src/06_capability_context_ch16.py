"""
Find every occurrence of 'capability' / 'capabilities' in Chapter 16
(both Part I and Part II) and print the surrounding text context.

Output goes to: outputs/ch16_capability_contexts.txt

The point is to read each occurrence in context and classify whether
the survey means:
  - state capability      (Mazzucato sense)
  - industrial capability (productive / technological)
  - human capability      (Sen sense)
  - other
"""

import re
import sqlite3
from pathlib import Path

DB_PATH = Path("db/survey.db")
OUTPUT_PATH = Path("outputs/ch16_capability_contexts.txt")
CONTEXT_CHARS = 150   # characters on each side of the match

# Match 'capability' or 'capabilities' as whole words, case-insensitive
PATTERN = re.compile(r"\bcapabilit(?:y|ies)\b", re.IGNORECASE)


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Pull all pages from chapters 16.1 and 16.2
    cur.execute("""
        SELECT pdf_page, chapter_id, text
        FROM pages
        WHERE chapter_id IN (16.1, 16.2)
        ORDER BY pdf_page;
    """)
    rows = cur.fetchall()
    conn.close()

    matches = []
    for pdf_page, chapter_id, text in rows:
        if not text:
            continue
        for m in PATTERN.finditer(text):
            start = max(0, m.start() - CONTEXT_CHARS)
            end = min(len(text), m.end() + CONTEXT_CHARS)
            snippet = text[start:end].replace("\n", " ").strip()
            matches.append({
                "pdf_page": pdf_page,
                "chapter_id": chapter_id,
                "word": m.group(0),
                "snippet": snippet,
            })

    # Write output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(f"Chapter 16 — occurrences of 'capability/capabilities'\n")
        f.write(f"Total occurrences: {len(matches)}\n")
        f.write("=" * 80 + "\n\n")
        for i, m in enumerate(matches, 1):
            f.write(f"[{i:>3}] Page {m['pdf_page']}  (Chapter {m['chapter_id']})  — \"{m['word']}\"\n")
            f.write(f"     ...{m['snippet']}...\n\n")

    print(f"Found {len(matches)} occurrences.")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()