import os
import re
import json
from tqdm import tqdm

PARSED_DIR = "/Users/linxiaotian/Desktop/WRDS/10-K/parsed_lines"
OUTPUT_DIR = "/Users/linxiaotian/Desktop/WRDS/10-K/header_predictions"
os.makedirs(OUTPUT_DIR, exist_ok=True)

VALID_ITEMS = ["1","1A","1B","2","3","4","5","6","7","7A",
               "8","9","9A","9B","10","11","12","13","14","15","16"]

CANONICAL_MAP = {k: f"item_{k.lower()}" for k in VALID_ITEMS}

HEADER_PATTERN = re.compile(r"^ITEM\s+(\d+[A-Z]?)\.?\s*(.*)$", re.IGNORECASE)


def detect_headers(file_path):
    """
    Detect and record *all* possible 10-K headers, preserving multiple occurrences.
    Later boundary detector can fallback if the last one is too short.
    """
    headers = []
    lines = []

    # --- Load parsed lines ---
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            lines.append(json.loads(line))

    # --- Step 1: raw pattern matching ---
    i = 0
    while i < len(lines):
        text = lines[i]["text"].strip()
        start = lines[i]["start_offset"]
        match = HEADER_PATTERN.match(text)
        if match:
            item_num = match.group(1).upper()
            title = match.group(2).strip()

            # Merge split title line
            if not title and i + 1 < len(lines):
                nxt = lines[i + 1]["text"].strip()
                if len(nxt.split()) < 15:
                    title = nxt
                    i += 1

            if item_num not in VALID_ITEMS:
                i += 1
                continue

            canonical_key = CANONICAL_MAP[item_num]
            full_header = f"Item {item_num}. {title}".strip()

            headers.append({
                "raw_header_text": full_header,
                "canonical_key": canonical_key,
                "item_num": item_num,
                "start_offset": start,
                "confidence": 0.9 if text.isupper() else 0.8
            })
        i += 1

    if not headers:
        return []

    # --- Step 2: sort chronologically ---
    headers = sorted(headers, key=lambda x: x["start_offset"])

    # --- Step 3: group by item_num and keep ALL (no pruning yet) ---
    # We'll keep them all, so the boundary detector can decide later which occurrence to use.
    grouped = {}
    for h in headers:
        grouped.setdefault(h["item_num"], []).append(h)

    # --- Step 4: flatten preserving item order ---
    ordered = []
    for item in VALID_ITEMS:
        if item in grouped:
            ordered.extend(grouped[item])

    return ordered


def process_all_files(parsed_dir=PARSED_DIR, output_dir=OUTPUT_DIR):
    files = [f for f in os.listdir(parsed_dir) if f.endswith(".jsonl")]
    for f in tqdm(files):
        file_path = os.path.join(parsed_dir, f)
        detected = detect_headers(file_path)
        doc_id = f.replace(".jsonl", "")
        out_path = os.path.join(output_dir, f"{doc_id}_headers.jsonl")

        with open(out_path, "w", encoding="utf-8") as out_f:
            for h in detected:
                h["doc_id"] = doc_id
                out_f.write(json.dumps(h, ensure_ascii=False) + "\n")

    print(f"✅ Header detection (v4 - with fallback candidates) complete. Results saved to {output_dir}")


if __name__ == "__main__":
    process_all_files()
