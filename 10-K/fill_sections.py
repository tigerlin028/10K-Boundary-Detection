import os
import json
from tqdm import tqdm

# ---------- Directory paths ----------
BOUNDARY_DIR = "/Users/linxiaotian/Desktop/WRDS/10-K/section_boundaries"
PARSED_DIR = "/Users/linxiaotian/Desktop/WRDS/10-K/parsed_lines"
OUTPUT_DIR = "/Users/linxiaotian/Desktop/WRDS/10-K/section_filled"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_parsed_lines(parsed_file):
    """
    Load the parsed JSONL file into a list of tuples (start_offset, text).
    Each line corresponds to one text segment in the original 10-K document.
    """
    lines = []
    with open(parsed_file, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            lines.append((entry["start_offset"], entry["text"]))
    return lines


def extract_text(lines, start, end):
    """
    Extract text segments whose start_offset falls between [start, end).
    Join all those text lines into a single continuous paragraph.
    """
    selected = [t for (off, t) in lines if start <= off < end]
    # Clean excessive whitespace for readability
    text = " ".join(selected).replace("\n", " ").strip()
    return text


def fill_content(boundary_file, parsed_file):
    """
    For each detected section boundary, extract its corresponding text
    from the parsed lines and add it as the 'content' field.
    """
    lines = load_parsed_lines(parsed_file)
    boundaries = json.load(open(boundary_file, encoding="utf-8"))

    for b in boundaries:
        b["content"] = extract_text(lines, b["start"], b["end"])
    return boundaries


def process_all():
    """
    Iterate through all boundary files and fill in text content
    for each 10-K section. The filled results are saved as JSON files.
    """
    for fname in tqdm(os.listdir(BOUNDARY_DIR)):
        if not fname.endswith("_boundaries.json"):
            continue

        doc_id = fname.replace("_boundaries.json", "")
        boundary_path = os.path.join(BOUNDARY_DIR, fname)
        parsed_path = os.path.join(PARSED_DIR, f"{doc_id}.jsonl")

        if not os.path.exists(parsed_path):
            print(f"⚠️ Skipping {doc_id} - parsed file missing.")
            continue

        filled = fill_content(boundary_path, parsed_path)
        out_path = os.path.join(OUTPUT_DIR, f"{doc_id}_sections.json")

        json.dump(filled, open(out_path, "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)

    print(f"✅ Section text successfully filled into {OUTPUT_DIR}")


if __name__ == "__main__":
    process_all()
