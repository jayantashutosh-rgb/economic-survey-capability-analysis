"""
Build and populate the SQLite database.

Reads:
  - sql/01_schema.sql                     (schema definition)
  - data/interim/chapters.json            (chapter metadata)
  - data/processed/chapters/*.txt         (cleaned chapter text)

Writes:
  - db/survey.db                          (SQLite database file)

The database holds two tables: chapters (17 rows) and pages (689 rows).
"""

import json
import re
import sqlite3
from pathlib import Path

SCHEMA_PATH = Path("sql/01_schema.sql")
CHAPTERS_JSON = Path("data/interim/chapters.json")
CLEANED_DIR = Path("data/processed/chapters")
DB_PATH = Path("db/survey.db")

# Regex to split cleaned chapter files by our page marker
PAGE_MARKER_RE = re.compile(r"^=====\s*PDF PAGE\s+(\d+)\s*=====\s*$", re.MULTILINE)


def split_chapter_into_pages(text: str) -> list[tuple[int, str]]:
    """Split a cleaned chapter file into (pdf_page, page_text) tuples."""
    # Find all marker positions
    matches = list(PAGE_MARKER_RE.finditer(text))
    pages = []
    for i, m in enumerate(matches):
        pdf_page = int(m.group(1))
        # Text starts right after this marker
        start = m.end()
        # Text ends at next marker (or end of file)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        page_text = text[start:end].strip()
        pages.append((pdf_page, page_text))
    return pages


def count_words(text: str) -> int:
    """Simple whitespace-based word count. Good enough for analytics."""
    if not text:
        return 0
    return len(text.split())


def main():
    # Ensure db directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing DB to ensure a clean rebuild
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Removed existing database: {DB_PATH}")

    # Open connection
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # 1. Apply schema
    print(f"\nApplying schema from {SCHEMA_PATH}...")
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    cur.executescript(schema_sql)
    conn.commit()
    print("  Schema applied.")

    # 2. Load chapters from JSON
    print(f"\nLoading chapters from {CHAPTERS_JSON}...")
    chapters = json.loads(CHAPTERS_JSON.read_text(encoding="utf-8"))

    cur.executemany(
        """
        INSERT INTO chapters (chapter_id, slug, title, start_page, end_page, page_count)
        VALUES (:chapter_id, :slug, :title, :start_page, :end_page, :page_count);
        """,
        chapters,
    )
    conn.commit()
    print(f"  Inserted {len(chapters)} chapters.")

    # 3. Load pages from cleaned chapter files
    print(f"\nLoading pages from {CLEANED_DIR}...")
    total_pages_inserted = 0

    for ch in chapters:
        ch_id = ch["chapter_id"]
        slug = ch["slug"]

        # Reconstruct expected filename — same logic as 03_extract_chapters.py
        ch_id_str = str(ch_id).replace(".", "_")
        if "_" in ch_id_str:
            main_part, sub = ch_id_str.split("_")
            filename = f"{main_part.zfill(2)}_{sub}_{slug}.txt"
        else:
            filename = f"{ch_id_str.zfill(2)}_{slug}.txt"

        fp = CLEANED_DIR / filename
        if not fp.exists():
            print(f"  WARNING: missing file {fp}")
            continue

        text = fp.read_text(encoding="utf-8")
        pages = split_chapter_into_pages(text)

        rows = [
            (pdf_page, ch_id, page_text, len(page_text), count_words(page_text))
            for pdf_page, page_text in pages
        ]

        cur.executemany(
            """
            INSERT INTO pages (pdf_page, chapter_id, text, char_count, word_count)
            VALUES (?, ?, ?, ?, ?);
            """,
            rows,
        )
        total_pages_inserted += len(rows)
        print(f"  Chapter {ch_id:<6} ({slug:<25}) → {len(rows):>3} pages")

    conn.commit()
    print(f"\n  Inserted {total_pages_inserted} pages total.")

# 3.5 Sync chapters.page_count with actual stored pages
    # (blank divider pages were dropped during cleaning, so the raw range
    #  page_count from chapters.json overstates the actual content pages)
    print("\nSyncing chapters.page_count with actual stored pages...")
    cur.execute("""
        UPDATE chapters
        SET page_count = (
            SELECT COUNT(*) FROM pages
            WHERE pages.chapter_id = chapters.chapter_id
        );
    """)
    conn.commit()
    print("  page_count synced.")

    # 4. Quick sanity checks
    print("\nSanity checks:")
    cur.execute("SELECT COUNT(*) FROM chapters;")
    print(f"  chapters table: {cur.fetchone()[0]} rows")

    cur.execute("SELECT COUNT(*) FROM pages;")
    print(f"  pages table:    {cur.fetchone()[0]} rows")

    cur.execute("SELECT SUM(char_count), SUM(word_count) FROM pages;")
    total_chars, total_words = cur.fetchone()
    print(f"  total chars:    {total_chars:,}")
    print(f"  total words:    {total_words:,}")

    conn.close()
    print(f"\nDatabase built: {DB_PATH}")


if __name__ == "__main__":
    main()
