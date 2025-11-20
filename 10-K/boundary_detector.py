import os
import json
from tqdm import tqdm

HEADER_DIR = "/Users/linxiaotian/Desktop/WRDS/10-K/header_predictions"
PARSED_DIR = "/Users/linxiaotian/Desktop/WRDS/10-K/parsed_lines"
OUTPUT_DIR = "/Users/linxiaotian/Desktop/WRDS/10-K/section_boundaries"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MIN_SPAN = 1000
VALID_ITEMS = ["1","1A","1B","2","3","4","5","6","7","7A",
               "8","9","9A","9B","10","11","12","13","14","15","16"]

def get_doc_length(parsed_file):
    """Return total document length using last end_offset."""
    last_line = None
    with open(parsed_file, "r", encoding="utf-8") as f:
        for line in f:
            last_line = json.loads(line)
    return last_line["end_offset"] if last_line else 0


def compute_spans(headers, doc_len):
    """Add span info for every header (end = next different item start)."""
    for i, h in enumerate(headers):
        next_start = None
        for j in range(i + 1, len(headers)):
            if headers[j]["item_num"] != h["item_num"]:
                next_start = headers[j]["start_offset"]
                break
        h["end_offset"] = next_start if next_start else doc_len
        h["span"] = h["end_offset"] - h["start_offset"]
    return headers


def choose_best(candidates):
    """Choose best candidate (from last → first) using MIN_SPAN logic."""
    candidates = sorted(candidates, key=lambda x: x["start_offset"])
    chosen = None
    for h in reversed(candidates):
        if h["span"] >= MIN_SPAN:
            chosen = h
            break
    if not chosen:
        chosen = candidates[-1]
    return chosen


def make_boundaries(header_file, parsed_file):
    """Main logic for generating ordered 1→16 boundaries."""
    headers = [json.loads(l) for l in open(header_file, encoding="utf-8")]
    headers = sorted(headers, key=lambda x: x["start_offset"])
    doc_len = get_doc_length(parsed_file)
    headers = compute_spans(headers, doc_len)

    # Group by item_num
    grouped = {}
    for h in headers:
        grouped.setdefault(h["item_num"], []).append(h)

    chosen_headers = []
    for item in VALID_ITEMS:
        if item in grouped:
            chosen = choose_best(grouped[item])
            chosen_headers.append(chosen)

    # Force 1→16 order
    results = []
    for i, item in enumerate(VALID_ITEMS):
        cur = next((h for h in chosen_headers if h["item_num"] == item), None)
        if not cur:
            continue
        # Find next existing chosen item
        later = next((h for h in chosen_headers[i+1:] if h["start_offset"] > cur["start_offset"]), None)
        end = later["start_offset"] if later else doc_len
        results.append({
            "canonical_key": cur["canonical_key"],
            "raw_header_text": cur["raw_header_text"],
            "item_num": cur["item_num"],
            "start": cur["start_offset"],
            "end": end,
            "span": end - cur["start_offset"],
            "doc_id": cur["doc_id"]
        })
    return results


def process_all():
    """Process all 10-K files."""
    for f in tqdm(os.listdir(HEADER_DIR)):
        if not f.endswith("_headers.jsonl"):
            continue
        doc_id = f.replace("_headers.jsonl", "")
        header_path = os.path.join(HEADER_DIR, f)
        parsed_path = os.path.join(PARSED_DIR, f.replace("_headers", ""))
        if not os.path.exists(parsed_path):
            continue
        boundaries = make_boundaries(header_path, parsed_path)
        out_path = os.path.join(OUTPUT_DIR, f"{doc_id}_boundaries.json")
        json.dump(boundaries, open(out_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"✅ Boundary detection (v9 - sequential 1→16, fallback min_span) complete. Results saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    process_all()
