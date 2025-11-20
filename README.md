# 🧩 10-K Item Boundary Detection Pipeline

This repository implements a full Python pipeline for parsing, detecting, and segmenting SEC 10-K filings into structured sections (Item 1–16).

---

## ⚙️ Modules Overview

| File | Description |
|:--|:--|
| `parser.py` | Converts raw HTML/SGML 10-K filings to JSONL (`parsed_lines/`). Each line includes text and character offsets. |
| `head.detector.py` | Detects all candidate “Item X.” headers and saves multiple occurrences per item. |
| `boundary_detector.py` | Selects the best header for each item using a fallback rule: the last valid occurrence whose span ≥ 1000 characters; otherwise backtracks. Output is strictly ordered Item 1 → 16. |
| `fill_sections.py` | Fills section text between `start` and `end` offsets into structured JSON (`sections/`). |
| `check_items.py` | Validates section consistency (no missing items, no negative spans, monotonic order). |
| `download.py` | Handles SEC 10-K file downloads and pre-processing. |
| `Outliers.md` | Documents anomalies, false detections, or edge-case filings that require manual inspection. |

---

## 🧠 Logic Summary

### 1. Header Detection
- Regex pattern: `^ITEM\s+(\d+[A-Z]?)\.?\s*(.*)$`
- Merges split lines (e.g., “Item 3.” + “Legal Proceedings”).
- Keeps *all* detected headers for fallback.

### 2. Boundary Computation
- Groups headers by item number.
- Computes span = next item start – current start.
- Traverses candidates backward (last → first):
  - If `span ≥ 1000` → keep it.
  - Else → fallback to previous.
- Always outputs Item 1 → Item 16 in correct order.

### 3. Section Filling
- Extracts raw text from parsed JSONL between `start` and `end`.
- Produces structured JSON files (`*_sections.json`).

### 4. Validation
- Ensures:
  - All spans > 0  
  - Sequential start order  
  - Missing or short sections logged for review  

---

## 🚀 Usage

```bash
# Parse raw HTML filings
python parser.py

# Detect all possible headers
python head.detector.py

# Compute final boundaries (v9)
python boundary_detector.py

# Fill each section with text
python fill_sections.py

# Validate and log anomalies
python check_items.py
