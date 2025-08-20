#!/usr/bin/env python3
"""
File: p2_07_filter_drugbank_hits.py
Description:
    Step 1: Parse FoldSeek summary and extract unique UniProt IDs from AlphaFold hit IDs.
    Step 2: Query UniProt API for DrugBank cross-references.
    Step 3: Map DrugBank annotations back to original records.
    Step 4: Save filtered results to CSV.

Usage:
    python scripts/phase2/p2_07_filter_drugbank_hits.py \
        --input-csv results/phase2/foldseek_human_hits_summary.csv \
        --output-csv results/phase2/uniprot_with_drugbank.csv

Notes:
    - Input: FoldSeek summary CSV containing AlphaFold hit IDs.
    - Output: Filtered CSV with UniProt + DrugBank mappings.
    - evalue is kept as string from FoldSeek output; numerical filtering is handled separately (see p2_09_filter_by_evalue.py).
"""

import csv
import requests
import time
import argparse

# === Step 1: Parse arguments ===
parser = argparse.ArgumentParser(description="Filter FoldSeek hits with DrugBank annotations via UniProt API.")
parser.add_argument("--input-csv", type=str, default="results/phase2/foldseek_human_hits_summary.csv",
                    help="Input CSV file from FoldSeek results (default: results/phase2/foldseek_human_hits_summary.csv)")
parser.add_argument("--output-csv", type=str, default="results/phase2/uniprot_with_drugbank.csv",
                    help="Output CSV file with DrugBank-annotated hits (default: results/phase2/uniprot_with_drugbank.csv)")
args = parser.parse_args()

input_csv = args.input_csv
output_csv = args.output_csv

# === Step 2: Parse input CSV and collect UniProt IDs ===
records = []
uniprot_set = set()

with open(input_csv, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        hit_id = row["hit_id"]
        # Example format: AF-<UniProtID>-F1-model_v4
        if hit_id.startswith("AF-") and "-F" in hit_id:
            accession = hit_id.split("-F")[0].replace("AF-", "")
            uniprot_set.add(accession)
            records.append({
                "query_protein": row["query_protein"],
                "hit_id": hit_id,
                "uniprot": accession,
                "database": row["database"],
                "evalue": row["evalue"]
            })

print(f"[INFO] Total unique UniProt IDs to query: {len(uniprot_set)}")

# === Step 3: Query UniProt API for DrugBank cross-references ===
def get_drugbank_entries(uniprot_id):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            print(f"[WARN] HTTP {r.status_code} for {uniprot_id}")
            return []
        data = r.json()
        db_refs = data.get("uniProtKBCrossReferences", [])
        return [ref["id"] for ref in db_refs if ref.get("database") == "DrugBank"]
    except Exception as e:
        print(f"[ERROR] {uniprot_id}: {e}")
        return []

uniprot_drug_map = {}
for uni in sorted(uniprot_set):
    drugs = get_drugbank_entries(uni)
    if drugs:
        uniprot_drug_map[uni] = drugs
    time.sleep(0.2)  # avoid hitting API too fast

# === Step 4: Match DrugBank annotations back to original records ===
drugbank_hits = []
for entry in records:
    uni = entry["uniprot"]
    if uni in uniprot_drug_map:
        entry["drugbank_ids"] = ";".join(uniprot_drug_map[uni])
        drugbank_hits.append(entry)

# === Step 5: Write filtered records to CSV ===
fieldnames = ["query_protein", "hit_id", "uniprot", "database", "evalue", "drugbank_ids"]
with open(output_csv, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(drugbank_hits)

print(f"[DONE] Found {len(drugbank_hits)} hits with DrugBank entries.")
print(f"[OUTPUT] Results saved to {output_csv}")
