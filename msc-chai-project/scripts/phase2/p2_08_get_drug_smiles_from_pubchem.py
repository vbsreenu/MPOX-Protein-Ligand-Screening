#!/usr/bin/env python3
"""
File: p2_08_get_drug_smiles_from_pubchem.py
Description:
    Step 1: Read DrugBank IDs from filtered UniProt hits.
    Step 2: Query PubChem API to map DrugBank IDs → CIDs → SMILES.
    Step 3: Save unique SMILES and DrugBank mappings.
    Step 4: Log failures for manual checking.

Usage:
    python scripts/phase2/p2_08_get_drug_smiles_from_pubchem.py \
        --input-csv results/phase2/uniprot_with_drugbank.csv \
        --output-smiles results/phase2/unique_smiles.smi \
        --output-drugs results/phase2/unique_drugs.csv \
        --fail-log results/phase2/smiles_failures.txt
"""

import csv
import requests
import time
import argparse

# === Step 1: Parse arguments ===
parser = argparse.ArgumentParser(description="Retrieve SMILES from PubChem using DrugBank IDs.")
parser.add_argument("--input-csv", type=str, default="results/phase2/uniprot_with_drugbank.csv",
                    help="Input CSV file containing DrugBank IDs (default: results/phase2/uniprot_with_drugbank.csv)")
parser.add_argument("--output-smiles", type=str, default="results/phase2/unique_smiles.smi",
                    help="Output SMILES file (default: results/phase2/unique_smiles.smi)")
parser.add_argument("--output-drugs", type=str, default="results/phase2/unique_drugs.csv",
                    help="Output CSV with DrugBank_ID,SMILES (default: results/phase2/unique_drugs.csv)")
parser.add_argument("--fail-log", type=str, default="results/phase2/smiles_failures.txt",
                    help="Log file for failed DrugBank IDs (default: results/phase2/smiles_failures.txt)")
args = parser.parse_args()

input_csv = args.input_csv
output_smiles = args.output_smiles
output_drugs = args.output_drugs
fail_log = args.fail_log

# === Step 2: Collect unique DrugBank IDs from input ===
unique_drugs = set()
with open(input_csv, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        for dbid in row["drugbank_ids"].split(";"):
            dbid = dbid.strip()
            if dbid:
                unique_drugs.add(dbid)

print(f"[INFO] Total unique DrugBank IDs to query: {len(unique_drugs)}")

# === Step 3: Define API query functions ===
def get_cid_from_drugbank_id(dbid):
    """Retrieve PubChem CID for a given DrugBank ID."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{dbid}/cids/JSON"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        cids = data.get("IdentifierList", {}).get("CID", [])
        return cids[0] if cids else None
    except Exception as e:
        print(f"[WARN] Failed to get CID for {dbid}: {e}")
        return None

def get_smiles_from_cid(cid):
    """Retrieve isomeric SMILES string from PubChem given a CID."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IsomericSMILES/JSON"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        return data["PropertyTable"]["Properties"][0]["IsomericSMILES"]
    except Exception as e:
        print(f"[WARN] Failed to get SMILES for CID {cid}: {e}")
        return None

# === Step 4: Query PubChem for each DrugBank ID ===
drug_to_smiles = {}
failures = []

for i, dbid in enumerate(sorted(unique_drugs)):
    print(f"[QUERY] ({i+1}/{len(unique_drugs)}) {dbid}")
    cid = get_cid_from_drugbank_id(dbid)
    if cid:
        smiles = get_smiles_from_cid(cid)
        if smiles:
            drug_to_smiles[dbid] = smiles
        else:
            failures.append(dbid)
    else:
        failures.append(dbid)
    time.sleep(0.2)  # polite delay to avoid rate limiting

# === Step 5: Save results ===
with open(output_smiles, "w") as smi_out, open(output_drugs, "w", newline="") as csv_out:
    writer = csv.writer(csv_out)
    writer.writerow(["DrugBank_ID", "SMILES"])
    for dbid, smiles in drug_to_smiles.items():
        smi_out.write(f"{smiles} {dbid}\n")
        writer.writerow([dbid, smiles])

# === Step 6: Save failed IDs ===
with open(fail_log, "w") as f:
    for dbid in failures:
        f.write(dbid + "\n")

print(f"[DONE] Retrieved SMILES for {len(drug_to_smiles)} drugs.")
print(f"[WARN] {len(failures)} drugs failed. Logged to {fail_log}")
