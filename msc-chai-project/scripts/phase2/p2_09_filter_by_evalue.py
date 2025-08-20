#!/usr/bin/env python3
"""
File: p2_09_filter_by_evalue.py
Description:
    Step 1: Load protein–drug mapping results (with e-values).
    Step 2: Convert e-value column to numeric.
    Step 3: Filter rows with e-value < cutoff.
    Step 4: Save filtered results.

Usage:
    python scripts/phase2/p2_09_filter_by_evalue.py \
        --input results/phase2/uniprot_with_drugbank.csv \
        --output results/phase2/uniprot_with_drugbank_filtered.csv \
        --cutoff 0.05
"""

import pandas as pd
import argparse

# === Step 1: Parse arguments ===
parser = argparse.ArgumentParser(description="Filter protein–drug mappings by e-value threshold.")
parser.add_argument("--input", type=str, default="results/phase2/uniprot_with_drugbank.csv",
                    help="Input CSV file (default: results/phase2/uniprot_with_drugbank.csv)")
parser.add_argument("--output", type=str, default="results/phase2/uniprot_with_drugbank_filtered.csv",
                    help="Output CSV file (default: results/phase2/uniprot_with_drugbank_filtered.csv)")
parser.add_argument("--cutoff", type=float, default=0.05,
                    help="E-value cutoff for filtering (default: 0.05)")
args = parser.parse_args()

input_file = args.input
output_file = args.output
cutoff = args.cutoff

# === Step 2: Load CSV and convert evalue column ===
df = pd.read_csv(input_file)
df["evalue"] = pd.to_numeric(df["evalue"], errors="coerce")

# === Step 3: Apply filter ===
filtered_df = df[df["evalue"] < cutoff]

# === Step 4: Save results ===
filtered_df.to_csv(output_file, index=False)

# === Step 5: Print summary ===
print(f"[INFO] Loaded {len(df)} records from {input_file}")
print(f"[INFO] Filtered {len(filtered_df)} records with e-value < {cutoff}")
print(f"[DONE] Output written to {output_file}")
