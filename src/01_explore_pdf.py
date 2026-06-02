import pdfplumber

PDF_PATH = "data/raw/economic_survey_2025_26.pdf"
OUTPUT_PATH = "data/interim/page_first_lines.txt"

with pdfplumber.open(PDF_PATH) as pdf:
    total = len(pdf.pages)
    print(f"Scanning {total} pages...", flush=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for i, page in enumerate(pdf.pages):
            if i % 50 == 0:
                print(f"  ... page {i+1}/{total}", flush=True)

            text = page.extract_text()
            if text is None:
                snippet = "(no text)"
            else:
                # Take first 80 characters, replace newlines with spaces
                snippet = text[:80].replace("\n", " ").strip()

            f.write(f"Page {i+1:>4}: {snippet}\n")

print(f"\nDone. Output saved to: {OUTPUT_PATH}", flush=True)
