#!/usr/bin/env python3
"""
File: p2_10_count_summary.py
Description:
    Step 1: Load filtered protein–drug mapping file.
    Step 2: Count unique query proteins.
    Step 3: Count unique DrugBank compounds.
    Step 4: Count unique protein–drug pairs.
    Step 5: Print summary to console.

Usage:
    python scripts/phase2/p2_10_count_summary.py \
        --input results/phase2/uniprot_with_drugbank_filtered.csv
"""

import pandas as pd
import csv
import argparse

# === Step 1: Parse arguments ===
parser = argparse.ArgumentParser(description="Summarize Mpox protein–drug mapping statistics.")
parser.add_argument("--input", type=str, default="results/phase2/uniprot_with_drugbank_filtered.csv",
                    help="Input CSV file (default: results/phase2/uniprot_with_drugbank_filtered.csv)")
args = parser.parse_args()

input_path = args.input

# === Step 2: Load CSV ===
df = pd.read_csv(input_path)

# === Step 3: Count unique proteins ===
unique_proteins = df["query_protein"].nunique()

# === Step 4: Count unique DrugBank IDs ===
drug_set = set()
for drugs in df["drugbank_ids"]:
    for d in str(drugs).split(";"):
        if d.strip():
            drug_set.add(d.strip())

# === Step 5: Count unique (protein, drug) pairs ===
unique_pairs = set()
with open(input_path, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        query_protein = row["query_protein"].strip()
        drugbank_ids = row["drugbank_ids"].strip()
        if not drugbank_ids:
            continue
        for drug_id in drugbank_ids.split(";"):
            if drug_id.strip():
                unique_pairs.add((query_protein, drug_id.strip()))

# === Step 6: Print results ===
print(f"[INFO] Number of unique Mpox proteins: {unique_proteins}")
print(f"[INFO] Number of unique DrugBank compounds: {len(drug_set)}")
print(f"[INFO] Number of unique Mpox–Drug combinations: {len(unique_pairs)}")
