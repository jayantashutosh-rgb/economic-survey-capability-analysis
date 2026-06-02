"""
Extract per-chapter text from the Economic Survey PDF.

Reads:
  - data/raw/economic_survey_2025_26.pdf
  - data/interim/chapters.json  (chapter page boundaries)

Writes:
  - data/interim/chapters/<NN>_<slug>.txt   (one file per chapter)
  - data/interim/pages_metadata.json        (page-level metadata)

Each chapter file contains plain text with page markers,
preserving traceability back to the source PDF page numbers.
"""

import json
from pathlib import Path
import pdfplumber

PDF_PATH = Path("data/raw/economic_survey_2025_26.pdf")
CHAPTERS_JSON = Path("data/interim/chapters.json")
OUTPUT_DIR = Path("data/interim/chapters")
METADATA_PATH = Path("data/interim/pages_metadata.json")

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load chapter map
with open(CHAPTERS_JSON, "r", encoding="utf-8") as f:
    chapters = json.load(f)

# Collect page-level metadata while extracting
pages_metadata = []

print(f"Extracting {len(chapters)} chapters from {PDF_PATH}\n", flush=True)

with pdfplumber.open(PDF_PATH) as pdf:
    for ch in chapters:
        ch_id = ch["chapter_id"]
        slug = ch["slug"]
        start = ch["start_page"]
        end = ch["end_page"]

        # Build filename — handle 16.1 / 16.2 cleanly
        ch_id_str = str(ch_id).replace(".", "_")
        # Pad chapter id for ordering: 01, 02, ..., 16_1, 16_2
        if "_" in ch_id_str:
            main, sub = ch_id_str.split("_")
            filename = f"{main.zfill(2)}_{sub}_{slug}.txt"
        else:
            filename = f"{ch_id_str.zfill(2)}_{slug}.txt"

        out_path = OUTPUT_DIR / filename

        print(f"  Chapter {ch_id}: pages {start}-{end}  →  {filename}", flush=True)

        # Extract each page in this chapter
        chapter_parts = []
        for pdf_page_num in range(start, end + 1):
            page = pdf.pages[pdf_page_num - 1]   # pdfplumber is 0-indexed
            text = page.extract_text()

            if text is None:
                text = ""

            char_count = len(text)
            is_blank = "this page has been left blank" in text.lower()

            # Add to page metadata
            pages_metadata.append({
                "pdf_page": pdf_page_num,
                "chapter_id": ch_id,
                "chapter_slug": slug,
                "char_count": char_count,
                "is_blank_marker": is_blank,
            })

            # Append text with a marker so we can trace each page later
            chapter_parts.append(f"\n\n===== PDF PAGE {pdf_page_num} =====\n\n{text}")

        # Write chapter file
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("".join(chapter_parts))

# Write metadata
with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(pages_metadata, f, indent=2, ensure_ascii=False)

print(f"\nDone.", flush=True)
print(f"  Chapter files: {OUTPUT_DIR}", flush=True)
print(f"  Page metadata: {METADATA_PATH}  ({len(pages_metadata)} pages)", flush=True)