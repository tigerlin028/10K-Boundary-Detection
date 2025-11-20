import os
import re
import json
import html
import unicodedata
from bs4 import BeautifulSoup
from tqdm import tqdm

# === Path settings ===
BASE_DIR = "/Users/linxiaotian/Desktop/WRDS/10-K/sec-edgar-filings"
OUTPUT_DIR = "/Users/linxiaotian/Desktop/WRDS/10-K/parsed_lines"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_main_10k_section(raw_html: str) -> str:
    """
    Locate and extract the <TYPE>10-K section (the main filing body)
    from the raw SEC SGML file.
    """
    lower = raw_html.lower()

    # Find the start of the main 10-K document
    start_type = lower.find("<type>10-k")
    if start_type == -1:
        # Fallback: return whole file
        return raw_html

    trimmed = raw_html[start_type:]

    # Try to capture <TEXT> ... </TEXT> only
    text_start = trimmed.lower().find("<text>")
    text_end = trimmed.lower().find("</text>")
    if text_start != -1 and text_end != -1 and text_end > text_start:
        trimmed = trimmed[text_start:text_end]

    return trimmed


def parse_html_to_lines(file_path: str):
    """Parse a 10-K HTML (or TXT) file into clean text lines with offsets."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_html = f.read()

    # --- Step 1: Extract only the <TYPE>10-K section ---
    raw_html = extract_main_10k_section(raw_html)

    # --- Step 2: Decode HTML entities & normalize Unicode ---
    text = html.unescape(raw_html)
    text = unicodedata.normalize("NFKC", text)

    # --- Step 3: Parse with BeautifulSoup ---
    soup = BeautifulSoup(text, "lxml")

    # Remove only scripts and styles (they contain no visible text)
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Unwrap tables and anchors (keep text but remove tag shells)
    for tag in soup.find_all(["a", "table"]):
        tag.unwrap()

    # --- Step 4: Extract visible text ---
    clean_text = soup.get_text(separator="\n")

    # --- Step 5: Normalize whitespace ---
    clean_text = re.sub(r"\n+", "\n", clean_text)
    clean_text = re.sub(r"[ \t]+", " ", clean_text)

    # --- Step 6: Split into lines & compute offsets ---
    lines = clean_text.split("\n")
    result = []
    offset = 0

    for line in lines:
        line = line.strip()
        if not line:
            offset += 1
            continue

        # Skip repeated page markers like "Page 3 of 125"
        if re.search(r"Page\s+\d+\s+of\s+\d+", line, re.IGNORECASE):
            offset += len(line) + 1
            continue

        start = offset
        end = start + len(line)
        result.append({
            "text": line,
            "start_offset": start,
            "end_offset": end
        })
        offset = end + 1

    return result


def process_all_files(base_dir=BASE_DIR, output_dir=OUTPUT_DIR):
    """Traverse all filings (.html/.htm/.txt) and parse them into JSONL."""
    html_files = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith((".html", ".htm", ".txt")):
                html_files.append(os.path.join(root, f))

    print(f"Found {len(html_files)} files to parse.")

    for file_path in tqdm(html_files):
        try:
            # Derive doc_id (e.g., AAPL_0000320193-21-000010)
            parts = file_path.split(os.sep)
            ticker = parts[-4] if len(parts) >= 4 else "UNKNOWN"
            accession = parts[-2]
            doc_id = f"{ticker}_{accession}"

            parsed = parse_html_to_lines(file_path)
            output_file = os.path.join(output_dir, f"{doc_id}.jsonl")

            with open(output_file, "w", encoding="utf-8") as out_f:
                for line in parsed:
                    out_f.write(json.dumps(line, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"⚠️ Failed to parse {file_path}: {e}")

    print(f"✅ Parsing complete. Output saved to {output_dir}")


if __name__ == "__main__":
    process_all_files()
