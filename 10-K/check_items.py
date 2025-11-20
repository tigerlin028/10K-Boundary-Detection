import os
import json
import re

PARSED_DIR = "/Users/linxiaotian/Desktop/WRDS/10-K/parsed_lines"

# Regex to detect typical 10-K section headers
ITEM_PATTERN = re.compile(r"\bITEM\s+(\d+[A-Z]?)\b", re.IGNORECASE)

def check_parsed_files(parsed_dir=PARSED_DIR):
    files = [f for f in os.listdir(parsed_dir) if f.endswith(".jsonl")]
    print(f"Scanning {len(files)} parsed files...\n")

    summary = []
    for f in sorted(files):
        file_path = os.path.join(parsed_dir, f)
        found_items = set()

        with open(file_path, "r", encoding="utf-8") as infile:
            for line in infile:
                entry = json.loads(line)
                text = entry.get("text", "")
                match = ITEM_PATTERN.search(text)
                if match:
                    found_items.add(match.group(1).upper())

        if found_items:
            summary.append((f, sorted(found_items)))
        else:
            summary.append((f, []))

    # Print summary
    for filename, items in summary:
        if items:
            print(f"✅ {filename}: found items {', '.join(items)}")
        else:
            print(f"⚠️ {filename}: no 'Item' sections found")

if __name__ == "__main__":
    check_parsed_files()
