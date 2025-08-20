#!/usr/bin/env python3
"""
File: p2_12_prepare_mpxv_analysis_dir.py
Description:
    Step 1: Traverse Phase 2 prediction outputs.
    Step 2: Collect protein-drug complex results into a unified analysis folder.
    Step 3: Copy model CIF and score NPZ files under standardized naming.

Usage:
    python scripts/phase2/p2_12_prepare_mpxv_analysis_dir.py \
        --src-dir data/phase2 \
        --dst-dir results/phase2/analysis

Notes:
    - Input structure: <src>/<protein>/<drug_id>/output_<protein>+<drug_id>_chai/
    - Output structure: <dst>/<protein>_<drug_id>/output_<protein>_<drug_id>_noTemplate/
    - Copies only pred.model_idx_*.cif and scores.model_idx_*.npz files.
"""

import os
import shutil
import re
import argparse


# === Step 1: Parse arguments ===
parser = argparse.ArgumentParser(description="Prepare Phase 2 analysis directory.")
parser.add_argument("--src-dir", type=str, default="data/phase2",
                    help="Source base directory with protein folders (default: data/phase2)")
parser.add_argument("--dst-dir", type=str, default="results/phase2/analysis",
                    help="Destination base directory for organized outputs (default: results/phase2/analysis)")
args = parser.parse_args()

src_base_dir = args.src_dir
dst_base_dir = args.dst_dir
os.makedirs(dst_base_dir, exist_ok=True)

# Regex for UniProt-like protein IDs (e.g., A0A7H0DNB6)
protein_pattern = re.compile(r"^[A-Z0-9]+$")

# Counters
total_proteins = 0
total_combinations = 0
skipped_no_drug = 0


# === Step 2: Traverse protein directories ===
for protein in os.listdir(src_base_dir):
    protein_path = os.path.join(src_base_dir, protein)

    # Step 2.1: Skip non-directories or invalid protein names
    if not os.path.isdir(protein_path):
        continue
    if not protein_pattern.match(protein):
        continue

    total_proteins += 1
    has_drug = False

    # Step 2.2: Traverse drug directories under each protein
    for drugbank_id in os.listdir(protein_path):
        drug_path = os.path.join(protein_path, drugbank_id)
        if not os.path.isdir(drug_path):
            continue

        # Step 2.3: Locate Chai output directory
        output_dir_name = f"output_{protein}+{drugbank_id}_chai"
        output_dir_path = os.path.join(drug_path, output_dir_name)
        if not os.path.isdir(output_dir_path):
            continue

        has_drug = True
        total_combinations += 1

        # Step 2.4: Define standardized destination path
        complex_id = f"{protein}_{drugbank_id}"
        dst_output_dir = os.path.join(
            dst_base_dir,
            complex_id,
            f"output_{complex_id}_noTemplate"
        )
        os.makedirs(dst_output_dir, exist_ok=True)

        # === Step 3: Copy files (CIF + NPZ) ===
        for filename in os.listdir(output_dir_path):
            if (filename.startswith("pred.model_idx_") and filename.endswith(".cif")) \
               or (filename.startswith("scores.model_idx_") and filename.endswith(".npz")):
                shutil.copy2(
                    os.path.join(output_dir_path, filename),
                    os.path.join(dst_output_dir, filename)
                )

        print(f"[INFO] Copied: {complex_id}")

    if not has_drug:
        skipped_no_drug += 1


# === Step 4: Print summary ===
print(f"\n[DONE] All valid complexes copied to {dst_base_dir}")
print(f"[STATS] Total proteins scanned     : {total_proteins}")
print(f"[STATS] Proteins skipped (no drug) : {skipped_no_drug}")
print(f"[STATS] Protein-drug combinations  : {total_combinations}")
