#!/usr/bin/env python3
"""
File: p2_06_extract_foldseek_human_hits.py
Description:
    Step 1: Traverse all FoldSeek result subfolders.
    Step 2: Parse .m8 files and extract hits annotated as "Homo sapiens".
    Step 3: Save a summary CSV of all human hits.
    Step 4: Save a list of proteins with no human hits.

Usage:
    python scripts/phase2/p2_06_extract_foldseek_human_hits.py \
        --input-root results/phase2/foldseek_results \
        --output-csv results/phase2/foldseek_human_hits_summary.csv \
        --no-hits-file results/phase2/no_human_hits.txt

Notes:
    - Input: FoldSeek outputs in .m8 format (tab-separated).
    - Output: summary CSV + text file of proteins without human hits.
"""

import os
import csv
import argparse

# === Step 1: Parse arguments ===
parser = argparse.ArgumentParser(description="Extract Homo sapiens hits from FoldSeek results.")
parser.add_argument("--input-root", type=str, default="results/phase2/foldseek_results",
                    help="Root directory containing FoldSeek result subfolders (default: results/phase2/foldseek_results)")
parser.add_argument("--output-csv", type=str, default="results/phase2/foldseek_human_hits_summary.csv",
                    help="Output CSV file for all human hits (default: results/phase2/foldseek_human_hits_summary.csv)")
parser.add_argument("--no-hits-file", type=str, default="results/phase2/no_human_hits.txt",
                    help="Output text file listing proteins with no human hits (default: results/phase2/no_human_hits.txt)")
args = parser.parse_args()

input_root = args.input_root
output_csv = args.output_csv
no_hits_file = args.no_hits_file

# === Step 2: Initialize data containers ===
summary_rows = [("query_protein", "database", "hit_id", "taxonomy", "evalue", "raw_line")]
no_hit_proteins = []

# === Step 3: Traverse result subfolders ===
for folder in sorted(os.listdir(input_root)):
    folder_path = os.path.join(input_root, folder)
    if not os.path.isdir(folder_path):
        continue

    found_human_hit = False  # flag per protein

    # Step 3.1: Iterate over .m8 files in this folder
    for fname in os.listdir(folder_path):
        if not fname.endswith(".m8") or "_report" in fname:
            continue

        dbname = fname.replace(".m8", "").replace("alis_", "")
        m8_path = os.path.join(folder_path, fname)

        # Step 3.2: Read lines and filter Homo sapiens hits
        with open(m8_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "Homo sapiens" in line:
                    parts = line.strip().split("\t")
                    hit_id = parts[1] if len(parts) > 1 else "N/A"
                    evalue = parts[10] if len(parts) > 10 else "N/A"
                    summary_rows.append((folder, dbname, hit_id, "Homo sapiens", evalue, line.strip()))
                    found_human_hit = True

    # Step 3.3: Record proteins with no human hits
    if not found_human_hit:
        no_hit_proteins.append(folder)

# === Step 4: Write outputs ===
# Save human hits summary
os.makedirs(os.path.dirname(output_csv), exist_ok=True)
with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(summary_rows)

# Save proteins with no human hits
with open(no_hits_file, "w") as f:
    for name in no_hit_proteins:
        f.write(name + "\n")

# === Step 5: Print stats ===
print(f"[DONE] Extracted {len(summary_rows)-1} Homo sapiens hits.")
print(f"[INFO] {len(no_hit_proteins)} proteins had no human hits.")
